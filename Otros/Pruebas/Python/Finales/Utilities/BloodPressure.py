import math
from typing import List

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, filtfilt, find_peaks, peak_prominences


class BloodPressure:
    PROMINENCE_MIN = 1.5    # Prominencia mínima para considerar un pico
    PROMINENCE_MAX = 5      # Prominencia máxima para considerar un pico
    HEIGHT_MAX = 2          # Altura máxima permitida para los picos
    HEIGHT_MIN = -40        # Altura mínima permitida para los picos
    FC = 2                  # Frecuencia de corte del filtro paso bajo para la derivada de la señal

    def __init__(self, fs: float):
        self.fs = fs
        self.sample_interval = 1 / fs
        self.time: np.ndarray | None = None  # TODO: comprobar que en ros no me de problema

    # Calcula la derivada de la señal de presión con respecto al tiempo
    def __compute_derivative(self, pressures: np.ndarray) -> np.ndarray:
        # TODO: controlar que el tiempo este vacio o sea muy corto
        return np.gradient(pressures, self.time)

    # Aplica un filtro paso bajo Butterworth
    def __lowpass_filter(self, data: np.ndarray, order: int = 4) -> np.ndarray:
        nyquist = 0.5 * self.fs
        normal_fc = self.FC / nyquist
        b, a = butter(order, normal_fc, btype='low')
        return filtfilt(b, a, data)

    # Filtrado morfológico de picos: solo se aceptan picos entre ciertos valores de altura y prominencia situados en la zona de desinflado
    # Devuelve los índices en los que se encuentran los picos
    def __morphological_filter(self, signal: np.ndarray, idx_start: int) -> List[int]:
        idx_peaks, _ = find_peaks(signal, height=(self.HEIGHT_MIN, self.HEIGHT_MAX), prominence=self.PROMINENCE_MIN)
        prominences, left_bases, right_bases = peak_prominences(signal, idx_peaks)
        min_prominences = signal[idx_peaks] - np.minimum(signal[left_bases], signal[right_bases])
        return [n for i, n in enumerate(idx_peaks) if min_prominences[i] > self.PROMINENCE_MAX and n > idx_start]

    # Filtrado basado en distanciamiento entre picos: se buscan secuencias de picos regulares
    # y compatibles con la frecuencia cardíaca
    def __distance_based_filter(self, peaks: List[int]) -> List[int]:
        distances = np.diff(peaks)
        min_d = math.floor(60 / 230 * self.fs)  # Muestras correspondientes a 230ppm
        max_d = math.ceil(60 / 40 * self.fs)  # Muestras correspondientes a 40ppm
        var = math.ceil(60E-3 * self.fs)  # Maxima diferencia entre pulsos de 60ms=60E-3*fs muestras

        # Obtener histograma y obtener la distancia objetivo como la más frecuente
        bins = np.arange(min_d, max_d + 1, var)
        hist, bin_edges = np.histogram(distances, bins=bins)
        idx_threshold = np.argmax(hist)

        # Segun donde caiga el siguiente mas común se mueve la distancia objetivo hacia un lado u otro del limite
        # TODO: a veces si hay pirámide tal vez error. Arreglar si eso calculando aquí nueva varianza
        if 0 < idx_threshold < len(hist) - 1:
            threshold = bin_edges[
                idx_threshold if hist[idx_threshold - 1] >= hist[idx_threshold + 1] else idx_threshold + 1]
        else:
            threshold = bin_edges[min(idx_threshold + 1, len(bin_edges) - 1)]

        # Agrupa los picos en grupos cuyos elementos mantienen relación de distancia
        groups, i_ini = [], 0
        for i, d in enumerate(distances):
            if abs(threshold - d) > var:
                groups.append(peaks[i_ini:i + 1])
                i_ini = i + 1
        groups.append(peaks[i_ini:])
        return max(groups, key=len) if groups else []

    # Genera gráficas para visualizar la señal original, derivada, picos detectados y puntos SYS/DIA
    def plot_results(self, pressures: np.ndarray, d_pressures: np.ndarray, d_pressures_filtered: np.ndarray,
                     peak_idx: List[int], sys_idx: int, dia_idx: int, sys: int, dia: int):
        peaks_time = [self.time[i] for i in peak_idx]
        peaks_d_pressure = [d_pressures_filtered[i] for i in peak_idx]

        plt.figure(figsize=(12, 6))

        # Gráfico de presión original con anotaciones de presión sistólica y diastólica
        plt.subplot(2, 1, 1)
        plt.plot(self.time, pressures, label='Original pressure')
        plt.scatter(self.time[sys_idx], pressures[sys_idx], color='blue', label=f"SYS: {sys} mmHg")
        plt.scatter(self.time[dia_idx], pressures[dia_idx], color='green', label=f"DIA: {dia} mmHg")
        # TODO: añadir lineas verticales
        plt.xlabel('Time (s)')
        plt.ylabel('Pressure (mmHg)')
        plt.title('Pressure vs Time')
        plt.grid()
        plt.legend()

        # Gráfico de derivada de presión con picos detectados
        plt.subplot(2, 1, 2)
        plt.plot(self.time, d_pressures, label='Raw derivative', alpha=0.6)
        plt.plot(self.time, d_pressures_filtered, label=f'Filtered derivative ({self.FC} Hz)', linewidth=2)
        plt.scatter(peaks_time, peaks_d_pressure, color='red', label='Detected peaks')
        # TODO: añadir lineas verticales
        plt.xlabel('Time (s)')
        plt.ylabel('dPressure/dt (mmHg/s)')
        plt.title('Pressure derivative')
        plt.grid()
        plt.legend()

        plt.tight_layout()
        plt.show()

    # Calcular velocidad media
    def calculate_velocity(self, pressures: np.ndarray, sample_time=0.5):
        samples = max(2, math.ceil(sample_time * self.fs))  # al menos 2 muestras
        if len(pressures) < samples:
            return 0.0

        delta_pressures = pressures[-1] - pressures[-samples]
        velocity = delta_pressures / samples * self.fs
        return velocity

    # Función principal para calcular la presión arterial
    def get_blood_pressure(self, pressures: np.ndarray):
        self.time = np.arange(0, len(pressures)) * self.sample_interval
        d_pressures = self.__compute_derivative(pressures)
        d_pressures_filtered = self.__lowpass_filter(d_pressures)

        idx_deflating_point = int(np.argmax(pressures))  # Índice del punto de desinflado
        idx_morph_peaks = self.__morphological_filter(signal=d_pressures_filtered, idx_start=idx_deflating_point)
        if len(idx_morph_peaks) < 2:
            raise ValueError("No se han encontrado picos en el análisis morfológico.")
        else:
            idx_distance_peaks = self.__distance_based_filter(idx_morph_peaks)
            if len(idx_distance_peaks) < 2:
                raise ValueError("No se han encontrado picos en el análisis por distanciamiento.")
            else:
                idx_sys, idx_dia = idx_distance_peaks[0], idx_distance_peaks[-1]
                sys, dia = int(pressures[idx_sys]), int(pressures[idx_dia])
                print(f"SYS: {sys} mmHg  |  DIA: {dia} mmHg")
                return sys, dia, idx_sys, idx_dia
