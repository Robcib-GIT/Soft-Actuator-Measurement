import math
from typing import List

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, filtfilt, find_peaks, peak_prominences


class BloodPressure:
    __PROMINENCE_MIN = 3.5  # Prominencia mínima para considerar un pico
    __PROMINENCE_MAX = 60  # Prominencia máxima para considerar un pico
    __HEIGHT_MAX = 30  # Altura máxima permitida para los picos
    __HEIGHT_MIN = -35  # Altura mínima permitida para los picos
    __FC = 4  # Frecuencia de corte del filtro paso bajo para la derivada de la señal
    __MAX_IBI_VARIANCE = 80E-3  # Máximo tiempo que pueden diferir los intervalos entre pulsos entre si

    def __init__(self, fs: float):
        self.fs = fs
        self.sample_interval = 1 / fs
        self.pressures: np.ndarray | None = None  # TODO: comprobar que en ros no me de problema
        self.time: np.ndarray | None = None
        self.d_pressures: np.ndarray | None = None
        self.d_pressures_filtered: np.ndarray | None = None
        self.__idx_peaks: List[int] | None = None

    # Calcula la derivada de la señal de presión con respecto al tiempo
    def __compute_derivative(self):
        if self.pressures is not None:
            self.d_pressures = np.gradient(self.pressures, self.time)
            # TODO: controlar que el tiempo este vacio o sea muy corto
        else:
            raise ValueError("No hay registros de presiones")

    # Aplica un filtro paso bajo Butterworth
    def __lowpass_filter(self, order: int = 4) -> np.ndarray:
        nyquist = 0.5 * self.fs
        normal_fc = self.__FC / nyquist
        b, a = butter(order, normal_fc, btype='low')
        return filtfilt(b, a, self.d_pressures)

    # Filtrado morfológico de picos: solo se aceptan picos entre ciertos valores de altura y prominencia situados en la zona de desinflado
    # Devuelve los índices en los que se encuentran los picos
    def __morphological_filter(self, signal: np.ndarray, idx_start: int) -> List[
        int]:  # TODO: no sirve la prominencia cambiarlo
        idx_peaks, _ = find_peaks(signal, height=(self.__HEIGHT_MIN, self.__HEIGHT_MAX))
        idx_mins, _ = find_peaks(-signal, height=(-self.__HEIGHT_MAX, -self.__HEIGHT_MIN))

        filtered_peaks = []
        for i, idx_peak in enumerate(idx_peaks):
            left_local_prominence = right_local_prominence = self.__PROMINENCE_MIN

            # Buscar prominencia local a la izquierda
            if i > 0:
                posibles = [x for x in idx_mins if idx_peaks[i - 1] < x < idx_peak]
                if posibles:
                    left_minimum = min(signal[x] for x in posibles)
                    left_local_prominence = signal[idx_peak] - left_minimum
                else:
                    # En teoría nunca llega aquí por lo de que entre picos siempre hay minimo
                    continue
            else:
                # El primero siempre cumple por la izda
                left_local_prominence = self.__PROMINENCE_MIN

            # Buscar prominencia local a la derecha
            if i < len(idx_peaks) - 1:
                posibles = [x for x in idx_mins if idx_peak < x < idx_peaks[i + 1]]
                if posibles:
                    right_minimum = min(signal[x] for x in posibles)
                    right_local_prominence = signal[idx_peak] - right_minimum
                else:
                    # En teoría nunca llega aquí por lo de que entre picos siempre hay minimo
                    continue
            else:
                # El último siempre cumple por la derecha
                right_local_prominence = self.__PROMINENCE_MIN

            if all(self.__PROMINENCE_MIN <= p <= self.__PROMINENCE_MAX for p in
                   (left_local_prominence, right_local_prominence)) and idx_peak > idx_start:
                filtered_peaks.append(idx_peak)

        return filtered_peaks

    # Filtrado basado en distanciamiento entre picos: se buscan secuencias de picos regulares
    # y compatibles con la frecuencia cardíaca
    def __distance_based_filter(self, peaks: List[int]) -> List[int]:  # TODO: mirar si pillar ambos lados en vez de uno
        distances = np.diff(peaks)
        min_d = math.floor(60 / 230 * self.fs)  # Muestras correspondientes a 230ppm
        max_d = math.ceil(60 / 40 * self.fs)  # Muestras correspondientes a 40ppm
        var = math.ceil(
            self.__MAX_IBI_VARIANCE * self.fs)  # Maxima diferencia entre pulsos de 60ms=60E-3*fs muestras  # FIXME: he cambiado a 80 mirar histograma

        # Obtener histograma y obtener la distancia objetivo como la más frecuente
        bins = np.arange(min_d, max_d + 1, var)
        hist, bin_edges = np.histogram(distances, bins=bins)

        self.plot_histogram(distances, bins)

        # Determinar el rango de interés
        idx_bins_range = (None, None)
        max_peaks_count = 0
        current_start = None
        current_peaks_count = 0
        max_bins = 3

        for i, freq in enumerate(hist):
            if freq > 0:
                if current_start is None:
                    current_start = i

                if (i - current_start) == max_bins:
                    current_peaks_count += (freq - hist[current_start])
                    current_start += 1
                else:
                    current_peaks_count += freq

                if current_peaks_count > max_peaks_count:
                    max_peaks_count = current_peaks_count
                    idx_bins_range = (current_start, i)

            else:
                current_start = None
                current_peaks_count = 0

        if None in idx_bins_range:
            raise ValueError("Rango de distancias aplicable no encontrado")

        search_distance_range = (bin_edges[idx_bins_range[0]], bin_edges[idx_bins_range[1] + 1])

        # Agrupa los picos en grupos cuyos elementos mantienen relación de distancia
        groups, i_ini = [], 0
        for i, d in enumerate(distances):
            if not (search_distance_range[0] <= d <= search_distance_range[1]):
                groups.append(peaks[i_ini:i + 1])
                i_ini = i + 1
        groups.append(peaks[i_ini:])
        return max(groups, key=len) if groups else []

    # Genera gráficas para visualizar la señal original, derivada, picos detectados y puntos SYS/DIA
    def plot_results(self):
        peaks_time = [self.time[i] for i in self.__idx_peaks]
        peaks_d_pressure = [self.d_pressures_filtered[i] for i in self.__idx_peaks]

        idx_sys, idx_dia = self.__idx_peaks[0], self.__idx_peaks[-1]
        sys, dia = int(self.pressures[idx_sys]), int(self.pressures[idx_dia])

        plt.figure(figsize=(12, 6))

        # Gráfico de presión original con anotaciones de presión sistólica y diastólica
        plt.subplot(2, 1, 1)
        plt.plot(self.time, self.pressures, label='Original pressure')
        plt.scatter(self.time[idx_sys], self.pressures[idx_sys], color='blue', label=f"SYS: {sys} mmHg")
        plt.axvline(x=self.time[idx_sys], color='r', linestyle='--')
        plt.scatter(self.time[idx_dia], self.pressures[idx_dia], color='green', label=f"DIA: {dia} mmHg")
        plt.axvline(x=self.time[idx_dia], color='r', linestyle='--')
        plt.xlabel('Time (s)')
        plt.ylabel('Pressure (mmHg)')
        plt.title('Pressure vs Time')
        plt.grid()
        plt.legend()

        # Gráfico de derivada de presión con picos detectados
        plt.subplot(2, 1, 2)
        plt.plot(self.time, self.d_pressures, label='Raw derivative', alpha=0.6)
        plt.plot(self.time, self.d_pressures_filtered, label=f'Filtered derivative ({self.__FC} Hz)', linewidth=2)
        plt.scatter(peaks_time, peaks_d_pressure, color='red', label='Detected peaks')
        plt.axvline(x=self.time[idx_sys], color='r', linestyle='--')
        plt.axvline(x=self.time[idx_dia], color='r', linestyle='--')
        plt.xlabel('Time (s)')
        plt.ylabel('dPressure/dt (mmHg/s)')
        plt.title('Pressure derivative')
        plt.grid()
        plt.legend()

        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_histogram(distances, bins):
        plt.hist(distances, bins=bins, edgecolor='black')
        plt.xlabel("IBI")
        plt.ylabel("Frecuencia")
        plt.title("Histograma de IBI")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_pruebas(self, idx_peaks):  # TODO: borrar!!!!
        peaks_time = [self.time[i] for i in idx_peaks]
        peaks_d_pressure = [self.d_pressures_filtered[i] for i in idx_peaks]
        idx_sys = idx_peaks[0]
        idx_dia = idx_peaks[-1]

        sys, dia = int(self.pressures[idx_sys]), int(self.pressures[idx_dia])

        plt.figure(figsize=(12, 6))

        # Gráfico de presión original con anotaciones de presión sistólica y diastólica
        plt.subplot(2, 1, 1)
        plt.plot(self.time, self.pressures, label='Original pressure')
        plt.scatter(self.time[idx_sys], self.pressures[idx_sys], color='blue', label=f"SYS: {sys} mmHg")
        plt.axvline(x=self.time[idx_sys], color='r', linestyle='--')
        plt.scatter(self.time[idx_dia], self.pressures[idx_dia], color='green', label=f"DIA: {dia} mmHg")
        plt.axvline(x=self.time[idx_dia], color='r', linestyle='--')
        plt.xlabel('Time (s)')
        plt.ylabel('Pressure (mmHg)')
        plt.title('Pressure vs Time')
        plt.grid()
        plt.legend()

        plt.subplot(2, 1, 2)

        plt.plot(self.time, self.d_pressures, label='Raw derivative', alpha=0.6)
        plt.plot(self.time, self.d_pressures_filtered, label=f'Filtered derivative ({self.__FC} Hz)', linewidth=2)
        plt.scatter(peaks_time, peaks_d_pressure, color='red', label='Detected morph peaks')
        plt.xlabel('Time (s)')
        plt.ylabel('d_Pressure (mmHg/s)')
        plt.title('d_Pressure vs Time')
        plt.grid()
        plt.legend()

        print(f"Resultados de filtro morfológico: SYS: {sys}  |  DIA: {dia}")

        plt.show()

    # Calcular velocidad media
    def calculate_velocity(self, pressures: List[float], sample_time=0.5):  # TODO: hacer que sea la media de todas
        samples = max(2, math.ceil(sample_time * self.fs))  # al menos 2 muestras
        if len(pressures) < samples:
            return 0.0

        delta_pressures = pressures[-1] - pressures[-samples]
        velocity = delta_pressures / samples * self.fs
        return velocity

    # Función principal para calcular la presión arterial
    def get_blood_pressure(self, pressures: List[float]):
        self.time = np.arange(0, len(pressures)) * self.sample_interval
        self.pressures = pressures

        try:
            self.__compute_derivative()
            self.d_pressures_filtered = self.__lowpass_filter()

            idx_deflating_point = int(np.argmax(pressures))  # Índice del punto de desinflado
            idx_morph_peaks = self.__morphological_filter(signal=self.d_pressures_filtered,
                                                          idx_start=idx_deflating_point)
            if len(idx_morph_peaks) < 2:
                raise ValueError("No se han encontrado picos en el análisis morfológico.")

            self.plot_pruebas(idx_morph_peaks)  # TODO: Activar para las pruebas

            idx_distance_peaks = self.__distance_based_filter(idx_morph_peaks)
            if len(idx_distance_peaks) < 2:
                raise ValueError("No se han encontrado picos en el análisis por distanciamiento.")

            self.__idx_peaks = idx_distance_peaks
            idx_sys, idx_dia = idx_distance_peaks[0], idx_distance_peaks[-1]

            # Rangos extremos 240>sys>70 & 140>dia>40
            sys, dia = int(pressures[idx_sys]), int(pressures[idx_dia])
            if not (240 > sys > 70) or not (140 > dia > 40):
                raise ValueError("Cálculo erróneo, presiones fuera de rangos factibles.")
            print(f"SYS: {sys} mmHg  |  DIA: {dia} mmHg")
            return sys, dia

        except ValueError as e:
            print(f"ValueError: {e}")
