import math
from typing import List

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import firwin, filtfilt, find_peaks


class BloodPressure:
    __DIA_H = 1.5       # Altura de la derivada de la presion para considerar DIA
    __PROMINENCE = 2.5  # Prominencia mínima para considerar un pico
    __FC = 4  # Frecuencia de corte del filtro paso bajo para la derivada de la señal
    __MAX_IBI_VARIANCE = 80E-3  # Máximo tiempo que pueden diferir los intervalos entre pulsos entre si

    def __init__(self, fs: float):
        self.fs = fs
        self.sample_interval = 1 / fs
        self.pressures: np.ndarray | None = None
        self.__filtered_pressures: np.ndarray | None = None
        self.time: np.ndarray | None = None
        self.__d_pressures: np.ndarray | None = None
        self.__idx_peaks: List[int] | None = None
        self.__all_idx_peaks: List[int] | None = None
        self.sys: int | None = None
        self.dia: int | None = None
        self.ppm: int | None = None

        # Aplica un filtro paso bajo Butterworth
    def __fir_filter(self, low_cut: float = 0.5, high_cut: float = 4.0):
        # Define los parámetros del filtro
        nyq = 0.5 * self.fs  # frecuencia de Nyquist
        num_taps = 20  # número de coeficientes del FIR (ajustable)

        # Diseña el filtro FIR
        fir_coeffs = firwin(num_taps, [low_cut / nyq, high_cut / nyq], pass_zero=False)

        # Aplica el filtro a la señal de presión
        self.__filtered_pressures = filtfilt(fir_coeffs, [1.0], self.pressures)

    """
    Según parece viendo las graficas, el tensiómetro digital toma como sys el aquel pico de presión cuya derivada es >=0
    y como día el ultimo pico cuya derivada alcanza un minimo de altura tras pasar el MAP
    """
    def __morphological_filter(self) -> List[int]:
        # Sacar los picos de la primera zona (desinflado y d_pressures>0)
        idx_peaks, properties = find_peaks(self.__d_pressures, height=0, prominence=self.__PROMINENCE)
        heights = properties["peak_heights"]
        self.__all_idx_peaks = idx_peaks  # Para plotear luego sin más

        # Recortar parte de desinflado
        idx_deflate = np.argmax(self.pressures)

        for i, val in enumerate(idx_peaks):
            if val > idx_deflate:
                # TODO: tal vez un raise
                idx_peaks = idx_peaks[i:]
                heights = heights[i:]
                break

        # Obtener MAP
        idx_map = idx_peaks[np.argmax(heights)]
        # pressure_map = pressures[idx_map]

        # Encontrar el ultimo pico del DIA
        for i, val in enumerate(idx_peaks):
            if val > idx_map:
                if heights[i] < self.__DIA_H:  # TODO: añadir que si el siguiente es mas alto que el anterior parta
                    idx_peaks = idx_peaks[:i]
                    # print(f"Ultimo dia: h->{heights[i - 1]}")
                    break

        return idx_peaks

    # Filtrado basado en distanciamiento entre picos: se buscan secuencias de picos regulares
    # y compatibles con la frecuencia cardíaca
    def __distance_based_filter(self, peaks: List[int]) -> List[int]:
        distances = np.diff(peaks)
        min_d = math.floor(60 / 230 * self.fs)  # Muestras correspondientes a 230ppm
        max_d = math.ceil(60 / 40 * self.fs)  # Muestras correspondientes a 40ppm
        var = math.ceil(
            self.__MAX_IBI_VARIANCE * self.fs)  # Maxima diferencia entre pulsos de 60ms=60E-3*fs muestras

        # Obtener histograma y obtener la distancia objetivo como la más frecuente
        bins = np.arange(min_d, max_d + 1, var)
        hist, bin_edges = np.histogram(distances, bins=bins)

        # self.plot_histogram(distances, bins)  # TODO: descomentar solo para pruebas

        # Determinar el rango de interés cogiendo los 3 bins consecutivos que contienen la mayor cantidad de picos
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

        # Obtener ppm
        self.ppm = int(60*self.fs/np.mean(search_distance_range))

        # Agrupa los picos en grupos cuyos elementos mantienen relación de distancia
        groups, i_ini = [], 0
        for i, d in enumerate(distances):
            if not (search_distance_range[0] <= d <= search_distance_range[1]):
                groups.append(peaks[i_ini:i + 1])
                i_ini = i + 1
        groups.append(peaks[i_ini:])

        return max(groups, key=len) if groups else []

    # Calcular velocidad media
    def calculate_velocity(self, pressures: List[float], sample_time=0.5):  # TODO: hacer que sea la media de todas
        samples = max(2, math.ceil(sample_time * self.fs))  # al menos 2 muestras
        if len(pressures) < samples:
            return 0.0
        
        delta_pressures = np.diff(pressures[-samples:])
        velocity = float(np.mean(delta_pressures))*self.fs

        return velocity

    # Función principal para calcular la presión arterial
    def get_blood_pressure(self, pressures: List[float]):
        self.time = np.arange(0, len(pressures)) * self.sample_interval
        self.pressures = pressures

        try:
            # Filtrar presiones
            self.__fir_filter()

            # Localizar picos mediante la derivada
            self.__d_pressures = np.gradient(self.__filtered_pressures, self.time)

            # Aplicar filtro morfológico para obtener los índices de los picos válidos
            idx_peaks = self.__morphological_filter()
            if len(idx_peaks) < 2:
                raise ValueError("No se han encontrado picos en el análisis morfológico.")

            # Volver a filtrar por distanciamiento para quitar falsos picos
            idx_peaks = self.__distance_based_filter(idx_peaks)
            if len(idx_peaks) < 2:
                raise ValueError("No se han encontrado picos en el análisis por distanciamiento.")

            # Obtener sys y dia
            self.__idx_peaks = idx_peaks
            idx_sys, idx_dia = idx_peaks[0], idx_peaks[-1]

            # Rangos extremos 240>sys>70 & 140>dia>40
            sys, dia = int(pressures[idx_sys]), int(pressures[idx_dia])
            if not (240 > sys > 70) or not (140 > dia > 40):
                raise ValueError(f"Presiones fuera de rangos factibles. (SYS: {sys}, DIA: {dia})")

            self.sys = sys
            self.dia = dia
            return sys, dia, self.ppm

        except ValueError:
            return None, None, None

    def plot_results(self):
        try:
            peaks_time = [self.time[i] for i in self.__idx_peaks]
            peaks_pressure = [self.pressures[i] for i in self.__idx_peaks]
            peaks_d_pressure = [self.__d_pressures[i] for i in self.__idx_peaks]

            all_peaks_time = [self.time[i] for i in self.__all_idx_peaks]
            all_peaks_d_pressure = [self.__d_pressures[i] for i in self.__all_idx_peaks]

            idx_sys, idx_dia = self.__idx_peaks[0], self.__idx_peaks[-1]
            sys, dia = int(self.pressures[idx_sys]), int(self.pressures[idx_dia])

            plt.figure(figsize=(12, 6))

            # Gráfico de presión original con anotaciones de presión sistólica y diastólica
            plt.subplot(2, 1, 1)
            plt.plot(self.time, self.pressures, label='Original pressure')
            plt.plot(self.time, self.__filtered_pressures, label='FIR filtered pressure')
            plt.scatter(peaks_time, peaks_pressure, color='green', label="Pulse peaks", s=26)
            plt.scatter(self.time[idx_sys], self.pressures[idx_sys], color='red', label=f"SYS: {sys} mmHg")
            plt.axvline(x=self.time[idx_sys], color='r', linestyle='--')
            plt.scatter(self.time[idx_dia], self.pressures[idx_dia], color='red', label=f"DIA: {dia} mmHg")
            plt.axvline(x=self.time[idx_dia], color='r', linestyle='--')
            plt.xlabel('Time (s)')
            plt.ylabel('Pressure (mmHg)')
            plt.title('Pressure vs Time')
            plt.grid()
            plt.legend()

            # Gráfico de derivada de presión con picos detectados
            plt.subplot(2, 1, 2)
            plt.plot(self.time, self.__d_pressures, label='Pressure derivative')
            plt.scatter(all_peaks_time, all_peaks_d_pressure, color='red', label="All peaks", s=26)
            plt.scatter(peaks_time, peaks_d_pressure, color='green', label='Filtered peaks')
            plt.axvline(x=self.time[idx_sys], color='r', linestyle='--')
            plt.axvline(x=self.time[idx_dia], color='r', linestyle='--')
            plt.xlabel('Time (s)')
            plt.ylabel('dPressure/dt (mmHg/s)')
            plt.title('Pressure derivative')
            plt.grid()
            plt.legend()

            plt.tight_layout()
            plt.show()

        except Exception:
            plt.figure(figsize=(12, 6))

            # Gráfico de presión original con anotaciones de presión sistólica y diastólica
            plt.subplot(2, 1, 1)
            plt.plot(self.time, self.pressures, label='Original pressure')
            plt.plot(self.time, self.__filtered_pressures, label='FIR filtered pressure')
            plt.xlabel('Time (s)')
            plt.ylabel('Pressure (mmHg)')
            plt.title('Pressure vs Time')
            plt.grid()
            plt.legend()

            # Gráfico de derivada de presión con picos detectados
            plt.subplot(2, 1, 2)
            plt.plot(self.time, self.__d_pressures, label='Pressure derivative')
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
