import os
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, find_peaks, peak_prominences
import csv
from tkinter import Tk, filedialog
from typing import Tuple, List
import ADS1x15
import time
import board
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
import busio

# --- Variables globales presion arterial --- TODO: refinar cuando complete el actuador
PROMINENCE_MIN = 1.5  # Prominencia mínima para considerar un pico
PROMINENCE_MAX = 5    # Prominencia máxima para considerar un pico
HEIGHT_MAX = 2        # Altura máxima permitida para los picos
HEIGHT_MIN = -40      # Altura mínima permitida para los picos
FC = 2                # Frecuencia de corte del filtro paso bajo para la derivada de la señal
INTERVAL = 0.025      # Segundos entre muestras
pressures = []         # Vector para guardar todas las presiones

ADS = ADS1x15.ADS1115(1, 0x48)
ADS.setGain(ADS.PGA_0_512V)


# --- Variables globales servos --- TODO: refinar rangos servo y angulos
IFLATE_ANGLE = 90
DEFLATE_ANGLE = 26
IDLE_ANGLE = 180
BUS_I2C = 0

if BUS_I2C == 1:                                # BUS1 (SCL: 5  |  SDA: 3)
    i2c = board.I2C() # o busio.I2C(board.SCL, board.SDA)
else:                                           # BUS0 (SCL: 28 | SDA: 27)
    i2c = busio.I2C(board.SCL_1, board.SDA_1)

pca = PCA9685(i2c)
pca.frequency = 50
cuffServo = servo.Servo(pca.channels[15], min_pulse=650, max_pulse=2650)


# --- Declaracion de funciones presion arterial ---
def getPressure(offset=27.0, pressureRef=200.0, valueRef=2960.0):
    pressure_raw = ADS.readADC_Differential_0_1()
    pressure = (pressure_raw - offset) * pressureRef / valueRef
    time.sleep(INTERVAL)  # TODO: quitar
    return float(pressure)

# Calcula la derivada de la señal de presión con respecto al tiempo
def compute_derivative(t: np.ndarray, p: np.ndarray) -> np.ndarray:
    return np.gradient(p, t)


# Aplica un filtro paso bajo Butterworth
def lowpass_filter(data: np.ndarray, _fs: float, _fc: float, order: int = 4) -> np.ndarray:
    nyquist = 0.5 * _fs
    normal_fc = _fc / nyquist
    b, a = butter(order, normal_fc, btype='low')
    return filtfilt(b, a, data)


# Filtrado morfológico de picos: solo se aceptan picos entre ciertos valores de altura y prominencia
# Devuelve los índices en los que se encuentran los picos
def morphological_filter(signal: np.ndarray, h_max: float, h_min: float, p_max: float, p_min: float, i_start: int) -> List[int]:
    peaks, _ = find_peaks(signal, height=(h_min, h_max), prominence=p_min, distance=1)
    prominences, left_bases, right_bases = peak_prominences(signal, peaks)
    min_prom = signal[peaks] - np.minimum(signal[left_bases], signal[right_bases])
    return [p for i, p in enumerate(peaks) if min_prom[i] > p_max and p > i_start]


# Filtrado basado en distanciamiento entre picos: se buscan secuencias de picos regulares
# y compatibles con la frecuencia cardíaca
def distance_based_filter(peaks: List[int], _fs: float) -> List[int]:
    distances = np.diff(peaks)
    min_d = math.floor(60 / 230 * _fs)  # Muestras correspondientes a 230ppm
    max_d = math.ceil(60 / 40 * _fs)    # Muestras correspondientes a 40ppm
    var = math.ceil(60E-3 * _fs)        # Maxima diferencia entre pulsos de 60ms=60E-3*fs muestras
    bins = np.arange(min_d, max_d + 1, var)

    # Obtener histograma y obtener la distancia objetivo como la más frecuente
    hist, bin_edges = np.histogram(distances, bins=bins)
    threshold_idx = np.argmax(hist)

    # Segun donde caiga el siguiente mas comun se mueve la distancia objetivo hacia un lado u otro del limite
    # TODO: a veces si hay pirámide tal vez error. Arreglar si eso calculando aquí nueva varianza
    if 0 < threshold_idx < len(hist) - 1:
        threshold = bin_edges[threshold_idx if hist[threshold_idx - 1] >= hist[threshold_idx + 1] else threshold_idx + 1]
    else:
        threshold = bin_edges[min(threshold_idx + 1, len(bin_edges) - 1)]

    # Agrupa los picos en grupos cuyos elementos mantienen relación de distancia
    groups, i_ini = [], 0
    for i, d in enumerate(distances):
        if abs(threshold - d) > var:
            groups.append(peaks[i_ini:i + 1])
            i_ini = i + 1
    groups.append(peaks[i_ini:])
    return max(groups, key=len) if groups else []


# Genera gráficas para visualizar la señal original, derivada, picos detectados y puntos SYS/DIA
def plot_results(t: np.ndarray, p: np.ndarray, dp: np.ndarray, dp_filt: np.ndarray,
                 peak_idx: List[int], sys_idx: int, dia_idx: int, sys: int, dia: int):
    peaks_t = [t[i] for i in peak_idx]
    peaks_v = [dp_filt[i] for i in peak_idx]

    plt.figure(figsize=(12, 6))

    # Gráfico de presión original con anotaciones de presión sistólica y diastólica
    plt.subplot(2, 1, 1)
    plt.plot(t, p, label='Original pressure')
    plt.scatter(t[sys_idx], p[sys_idx], color='blue', label=f"SYS: {sys} mmHg")
    plt.scatter(t[dia_idx], p[dia_idx], color='green', label=f"DIA: {dia} mmHg")
    plt.xlabel('Time (s)')
    plt.ylabel('Pressure (mmHg)')
    plt.title('Pressure vs Time')
    plt.grid()
    plt.legend()

    # Gráfico de derivada de presión con picos detectados
    plt.subplot(2, 1, 2)
    plt.plot(t, dp, label='Raw derivative', alpha=0.6)
    plt.plot(t, dp_filt, label=f'Filtered derivative ({FC} Hz)', linewidth=2)
    plt.scatter(peaks_t, peaks_v, color='red', label='Detected peaks')
    plt.xlabel('Time (s)')
    plt.ylabel('dPressure/dt (mmHg/s)')
    plt.title('Pressure derivative')
    plt.grid()
    plt.legend()

    plt.tight_layout()
    plt.show()


# Calcular velocidad media con 1 sec
def calculate_velocity(sample_time=1.0):
    samples = max(2, math.ceil(sample_time / INTERVAL))  # al menos 2 muestras
    if len(pressures) < samples:
        return 0.0

    # diferencia de presión entre cada paso
    delta_pressures = pressures[-1]-pressures[-samples]
    #print(f"Diferencia: {delta_pressures}")

    velocity = delta_pressures / (samples-1)/INTERVAL
    #print(f"Velocidad: {velocity}")
    return velocity


# --- Declaracion de funciones servos ---
def initialice_servo_pos():
    print("Moviendo servo a IDLE")
    cuffServo.angle = 0
    while(getPressure()>5.0):
        pass
    time.sleep(2)
    """ cuffServo.angle = IFLATE_ANGLE
    time.sleep(1)
    cuffServo.angle = DEFLATE_ANGLE
    time.sleep(1) """

# --- Bucle principal con PID ---
if __name__ == "__main__":
    print("Holi")
    initialice_servo_pos()
    angle = IFLATE_ANGLE
    cuffServo.angle = angle
    time.sleep(0.5)

    deflating = False
    prev_pressure = 0

    while True:
        pressure = getPressure()
        pressures.append(pressure)
        p_velocity = calculate_velocity()
        print(f"\rPresión: {pressure:.2f} mmHg  |   V_presion: {p_velocity:.2f} mmHg/s   |  Ángulo: {angle}         ", end="")

        if not deflating and pressure > 190:
            angle = DEFLATE_ANGLE
            cuffServo.angle = angle
            deflating = True
            prev_pressure = pressure
            

        elif deflating and pressure < 15:
            print("\nTerminado")
            angle = 0
            cuffServo.angle = angle
            break

        elif deflating: #TODO: ajustar y mejorar
            if p_velocity > -3 and (prev_pressure-pressure) > 50:
                angle -=2
                prev_pressure = pressure

            cuffServo.angle = angle
    
    #Calcular presiones
    pressures= np.array(pressures)
    time = np.arange(0, len(pressures)) * INTERVAL
    fs = 1 / np.mean(np.diff(time))  # Frecuencia de muestreo
    dp = compute_derivative(time, pressures)
    dp_filtered = lowpass_filter(dp, fs, FC)

    idx_max_pressure = np.argmax(pressures)  # Índice del pico máximo de presión
    morph_peaks = morphological_filter(dp_filtered, HEIGHT_MAX, HEIGHT_MIN, PROMINENCE_MAX, PROMINENCE_MIN, idx_max_pressure)
    filtered_peaks = distance_based_filter(morph_peaks, fs)

    if not filtered_peaks:
        print("⚠️ No valid peaks found after filtering.")
    else:
        idx_sys, idx_dia = filtered_peaks[0], filtered_peaks[-1]
        sys, dia = int(pressures[idx_sys]), int(pressures[idx_dia])
        print(f"✅ SYS: {sys} mmHg  |  DIA: {dia} mmHg")
        plot_results(time, pressures, dp, dp_filtered, filtered_peaks, idx_sys, idx_dia, sys, dia)

        # Crear ventana de diálogo para guardar el archivo CSV
        root = Tk()
        root.withdraw()  # Ocultar ventana principal
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])

        if file_path:
            # Guardar los datos en un archivo CSV
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Tiempo (segundos)', 'Presión (mmHg)'])
                for t, p in zip(time, pressures):
                    writer.writerow([t, p])
            print(f"Archivo guardado como {file_path}")
        else:
            print("No se guardó el archivo.")


        
