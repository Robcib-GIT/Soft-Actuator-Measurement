import math
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, find_peaks, peak_prominences
from tkinter import Tk, filedialog

PROMINENCE_MIN = 1.5
PROMINENCE_MAX = 5
HEIGHT_MAX = 0
HEIGHT_MIN = -25


def seleccionar_csv():
    root = Tk()
    root.withdraw()
    directorio_inicial = os.path.dirname(os.path.abspath(__file__))
    filepath = filedialog.askopenfilename(
        initialdir=directorio_inicial,
        title="Selecciona el archivo CSV",
        filetypes=[("CSV files", "*.csv")]
    )
    return filepath


def load_csv_data(filepath):
    df = pd.read_csv(filepath)
    time_data = df.iloc[:, 0].values
    pressure_data = df.iloc[:, 1].values
    return time_data, pressure_data


def calcular_derivada(_time, _pressure):
    derivative = np.gradient(_pressure, _time)
    return derivative


def filtro_paso_bajo(data, _fs, _fc, order=4):
    nyquist = 0.5 * _fs
    normal_fc = _fc / nyquist
    b, a = butter(order, normal_fc, btype='low', analog=False)
    filtered_data = filtfilt(b, a, data)
    return filtered_data


""" Devuelve los indices de los picos de la señal proporcionada que cumplen 
con ciertos margenes de altura y prominencia"""


def filtrado_morfologico(signal, height_max, height_min, prominence_max, prominence_min, start_index):
    # Encontrar picos usando altura y prominencia minima
    signal_peaks_indexes, _ = find_peaks(
        signal,
        height=(height_min, height_max),
        prominence=prominence_min,  # Por defecto calcula con la base mas alta
        distance=1
    )

    # Filtrar picos por prominencia maxima, es decir, utilizando el minimo de las 2 bases

    prominences, left_bases, right_bases = peak_prominences(signal, signal_peaks_indexes)
    min_bases = np.minimum(signal[left_bases], signal[right_bases])
    min_prominences = signal[signal_peaks_indexes] - min_bases

    # Filtrar los picos cuya prominencia mínima sea mayor que cierto valor
    filtered_signal_peaks_indexes = []
    for i in range(len(min_prominences)):
        # Si la prominencia es mayor que el umbral y el pico esta en la parte de desinflado pasa el filtro
        if min_prominences[i] > prominence_max and signal_peaks_indexes[i] > start_index:
            filtered_signal_peaks_indexes.append(signal_peaks_indexes[i])

    return filtered_signal_peaks_indexes


""" Devuelve la lista de los indices correspondientes a los picos que cumplen con cierto espaciado entre si que podria
ser interpretado como un pulso"""


def filtrado_por_distanciamiento(peaks_indexes):
    distances = np.diff(peaks_indexes)
    min_distance = math.floor(60 / 230 * fs)  # Muestras correspondientes a 230ppm
    max_distance = math.ceil(60 / 40 * fs)  # Muestras correspondientes a 40ppm
    variance = math.ceil(60E-3 * fs)  # Maxima diferencia entre pulsos de 60ms=60E-3*fs muestras

    # Crear histograma
    bins = np.arange(min_distance, max_distance + 1, variance)
    hist, bin_edges = np.histogram(distances, bins=bins)
    # print("Histograma:", hist)
    # print("Límites de los bins:", bin_edges)

    # Mostrar histograma
    plt.hist(distances, bins=bins, edgecolor='black')
    plt.xticks(bin_edges)  # Mostrar los bordes en el eje x
    plt.xlabel('Distancia')
    plt.ylabel('Frecuencia')
    plt.title('Histograma de muestras entre picos')
    plt.grid(True)
    plt.show()

    # Encontrar punto de evaluacion: distancia valida mas frecuente
    # FIXME: cuando cae en medio no detecta algunos, tal vez calcular aqui la variacion añadida
    threshold_index = np.argmax(hist)
    if 0 < threshold_index < len(hist) - 1:
        if hist[threshold_index - 1] >= hist[threshold_index + 1]:
            threshold_distance = bin_edges[threshold_index]
        else:
            threshold_distance = bin_edges[threshold_index + 1]
    elif threshold_index == 0:
        threshold_distance = bin_edges[1]
    else:
        threshold_distance = bin_edges[threshold_index]

    # Separar los picos en segmentos que cumplan con las restricciones de distancia
    grouped_peaks = []
    cut_index = 0
    for i, distance in enumerate(distances):
        current_variance = abs(threshold_distance - distance)
        if current_variance > variance:
            grouped_peaks.append(peaks_indexes[cut_index:i + 1])
            cut_index = i + 1
            # print(f"Corte entre puntos {i}-{i+1}")    TODO: borrar

    grouped_peaks.append(peaks_indexes[cut_index:])
    print(grouped_peaks)

    # Devolver el grupo mas amplio
    return max(grouped_peaks, key=len)


# Seleccionar archivo y cargar datos
csv_rute = seleccionar_csv()
time, pressure = load_csv_data(csv_rute)

# Obtener derivada
d_pressure = calcular_derivada(time, pressure)

# Aplicar filtro de paso bajo a la derivada
fs = 1 / np.mean(np.diff(time))  # Hz
fc = 2  # Hz
filtered_d_pressure = filtro_paso_bajo(data=d_pressure, _fs=fs, _fc=fc)

# Obtener zona de desinflado
max_pressure = np.max(pressure)
max_pressure_index = np.argmax(pressure)

# Encontrar picos significativos
d_pressure_peaks_indexes = filtrado_morfologico(signal=filtered_d_pressure, height_max=HEIGHT_MAX, height_min=HEIGHT_MIN,
                                                prominence_max=PROMINENCE_MAX, prominence_min=PROMINENCE_MIN,
                                                start_index=max_pressure_index)

print(f"Indices picos (1er filtrado): {d_pressure_peaks_indexes}")  # TODO: borrar

# Volver a filtrar por distanciamiento
d_pressure_peaks_indexes = filtrado_por_distanciamiento(d_pressure_peaks_indexes)
print(f"Indices picos (2ndo filtrado): {d_pressure_peaks_indexes}")  # TODO: borrar

# Obtener puntos
# TODO: ver si puedo usar picos vPresion directamente
d_pressure_peaks = [filtered_d_pressure[i] for i in d_pressure_peaks_indexes]
d_pressure_peaks_time = [time[i] for i in d_pressure_peaks_indexes]

# Calcular presiones sys y dia
indice_sys = d_pressure_peaks_indexes[0]
sys = int(pressure[indice_sys])
indice_dia = d_pressure_peaks_indexes[-1]
dia = int(pressure[indice_dia])
print(f"Sys: {sys}mmHg  |  Dia: {dia}mmHg")

# Paso 6: Graficar
plt.figure(figsize=(12, 6))

plt.subplot(2, 1, 1)
plt.plot(time, pressure, label='Presión original')
plt.scatter(time[indice_sys], pressure[indice_sys], color='blue', marker='o', label=f"SYS: {sys}mmHg")
plt.scatter(time[indice_dia], pressure[indice_dia], color='green', marker='o', label=f"DIA: {dia}mmHg")
plt.xlabel('Tiempo (s)')
plt.ylabel('Presión (mmHg)')
plt.title('Presión vs Tiempo')
plt.grid()
plt.legend()

plt.subplot(2, 1, 2)
plt.plot(time, d_pressure, label='Derivada sin filtrar', alpha=0.6)
plt.plot(time, filtered_d_pressure, label=f'Derivada filtrada ({fc} Hz)', linewidth=2)
plt.scatter(d_pressure_peaks_time, d_pressure_peaks, color='red', marker='o', label='Picos detectados')
plt.xlabel('Tiempo (s)')
plt.ylabel('dPresión/dt (mmHg/s)')
plt.title('Primera derivada de la presión')
plt.grid()
plt.legend()

plt.tight_layout()
plt.show()
