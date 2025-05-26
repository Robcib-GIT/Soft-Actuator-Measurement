import math
from typing import List

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import firwin, filtfilt, find_peaks

PLOT_THROUGH = False


class BloodPressure:
    __MIN_PEAK_H = -100
    __PROMINENCE = 4    # Prominencia mínima para considerar un pico  5
    __MAX_IBI_VARIANCE = 90E-3  # Máximo tiempo que pueden diferir los intervalos entre pulsos entre si  80
    __SYS_RATIO = 0.88  # @0.83: 6.29  inicialmente 0.8
    __DIA_RATIO = 0.42  # @0.41: 8.38  inicialmente 0.5

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
        self.map: int | None = None
        self.ppm: int | None = None

        # Aplica un filtro paso banda

    def __fir_filter(self, low_cut: float = 0.5, high_cut: float = 4.0):
        # Define los parámetros del filtro
        nyq = 0.5 * self.fs  # frecuencia de Nyquist
        num_taps = 20  # número de coeficientes del FIR (ajustable)

        # Diseña el filtro FIR
        fir_coeffs = firwin(num_taps, [low_cut / nyq, high_cut / nyq], pass_zero=False)

        # Aplica el filtro a la señal de presión
        self.__filtered_pressures = filtfilt(fir_coeffs, [1.0], self.pressures)

    def __get_amplitudes(self, peaks: List[int]):
        amplitudes = []

        for i, peak in enumerate(peaks):
            # Buscar mínimo a la izquierda (se suele descartar el primero)
            left_min = np.min(self.__d_pressures[peaks[i - 1]:peak]) if i > 0 else self.__d_pressures[peak]

            # Buscar mínimo a la derecha
            if i < len(peaks) - 1:  # and peak < len(self.pressures)-1:
                right_min = np.min(self.__d_pressures[peak:peaks[i + 1]])
            else:
                right_min = np.min(self.__d_pressures[peak:])

            # Diferencias de altura
            amp_left = self.__d_pressures[peak] - left_min
            amp_right = self.__d_pressures[peak] - right_min

            # Tomar la mayor de las dos
            amplitudes.append(min(amp_left, amp_right))  # FIXME: he cambiado min por max

        return amplitudes

    @staticmethod
    def __find_1d_peak_widths(signal):
        peaks, _ = find_peaks(signal)
        widths = []
        for i, peak in enumerate(peaks):
            left = 0
            right = len(signal) - 1
            if i > 0:
                temp = signal[peak]
                for j in range(peak, peaks[i - 1], -1):
                    left = j
                    if signal[j] <= temp:
                        temp = signal[j]
                    else:
                        left = j + 1
                        break

            if i < len(peaks) - 1:
                temp = signal[peak]
                for j in range(peak, peaks[i + 1] + 1):
                    right = j
                    if signal[j] <= temp:
                        temp = signal[j]
                    else:
                        right = j - 1
                        break

            widths.append(right - left)
        return peaks, widths

    """
    Según parece Omron y demas tienen ciertos coeficientes fijos y los usan para obtener sys y dia sabiendo map
    """

    def __morphological_filter(self) -> List[int]:
        # Sacar los picos de la primera zona (desinflado y d_pressures>0)
        wlen = 2 * math.ceil(60 / 40 * self.fs)  # Ventana para la prominencia el doble del max intervalo entre pulsos
        idx_peaks, properties = find_peaks(self.__d_pressures, height=self.__MIN_PEAK_H, prominence=self.__PROMINENCE,
                                           wlen=wlen)
        self.__all_idx_peaks = idx_peaks  # Para plotear luego sin más

        # Recortar parte de desinflado
        idx_deflate = np.argmax(self.pressures)

        for i, val in enumerate(idx_peaks):
            if val > idx_deflate:
                idx_peaks = idx_peaks[i:]
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

        if PLOT_THROUGH:
            self.plot_histogram(distances, bins)

        # Determinar el rango de interés cogiendo los max_bins bins consecutivos que contienen la mayor cantidad de picos
        idx_bins_range = (None, None)
        max_peaks_count = 0
        current_start = None
        current_peaks_count = 0
        max_bins = 5  # FIXME: antes 3 pero parece mejorar alguna (Jaime_v1)

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
        # Además si 2 consecutivos suman una distancia equivalente a un pulso también los considera para omitir ruido
        groups, i_ini = [], 0
        i = 0
        while i < len(distances):
            d = distances[i]
            if not (search_distance_range[0] <= d <= search_distance_range[1]):
                if i < len(distances) - 1 and (
                        search_distance_range[0] <= d + distances[i + 1] <= search_distance_range[1]):
                    i += 2
                    continue

                groups.append(peaks[i_ini:i + 1])
                i_ini = i + 1
            i += 1
        groups.append(peaks[i_ini:])

        return max(groups, key=len) if groups else []

    # Calcular velocidad media
    def calculate_velocity(self, pressures: List[float], sample_time=0.5):
        samples = max(2, math.ceil(sample_time * self.fs))  # al menos 2 muestras
        if len(pressures) < samples:
            return 0.0

        delta_pressures = np.diff(pressures[-samples:])
        velocity = float(np.mean(delta_pressures)) * self.fs

        return velocity

    @staticmethod
    def __polinomial_fitting(signal, deg=3):
        x = np.arange(len(signal))
        coeffs = np.polyfit(x, signal, deg=deg)
        poly = np.poly1d(coeffs)
        return poly(x)

    def __get_map(self, idx_peaks: List[int]):
        peak_amplitudes = self.__get_amplitudes(peaks=idx_peaks)

        smoothed_peak_amplitudes = self.__polinomial_fitting(peak_amplitudes)
        # Obtener el punto maximo en la version suavizada y a partir de ese indice coger el
        # maximo mas cercano en la original
        idx_max_smoothed = np.argmax(smoothed_peak_amplitudes)
        idx_map = idx_max_smoothed - 1 + np.argmax([peak_amplitudes[idx_max_smoothed - 1:idx_max_smoothed + 2]])

        # amplitude_peak_idxs, amplitude_peak_widths = self.__find_1d_peak_widths(peak_amplitudes)

        # idx_map = amplitude_peak_idxs[np.argmax(amplitude_peak_widths)]

        # Se selecciona el map como el pico de amplitudes más ancho
        # idx_amplitude_peaks, properties = find_peaks(peak_amplitudes, width=0)
        # Se obtiene map como el pico más ancho
        # idx_map = idx_amplitude_peaks[np.argmax(properties['widths'])]

        # Se selecciona el map como el pico de amplitudes más alto con ancho superior a 2
        # idx_amplitude_peaks, properties = find_peaks(peak_amplitudes, width=1, height=0)
        # # Se obtiene map como el pico más ancho que 2 muestras y más alto
        # idx_map = idx_amplitude_peaks[np.argmax(properties['peak_heights'])]

        # Obtener map real
        idx_map_peak = idx_peaks[idx_map]  # Indice en el que se encuentra
        self.map = self.pressures[idx_map_peak]

        if PLOT_THROUGH:
            print(f"MAP: {self.map:.2f}mmHg en latido [{idx_map}]")
            print(f"Amplitudes: {[f'{a:.2f}' for a in peak_amplitudes]}")

            plt.plot(range(len(peak_amplitudes)), peak_amplitudes, label='Amplitudes original')
            plt.scatter(idx_map, peak_amplitudes[idx_map], color='red', s=30)
            plt.plot(range(len(peak_amplitudes)), smoothed_peak_amplitudes, label='Amplitudes suavizada')
            plt.scatter(idx_max_smoothed, smoothed_peak_amplitudes[idx_max_smoothed], color='red', s=30)
            plt.legend()
            plt.show()

        return peak_amplitudes, idx_map

    def __get_sys_dia(self, idx_peaks: List[int], peak_amplitudes: List[int], idx_map: int):
        # ---------------OBTENER SYS--------------------
        idx_first_pulse = None

        # Tomar sys como MAP
        #idx_first_pulse = idx_map

        # Tomar sys como primer pulso mas cercano a MAP que no supere el umbral ni su siguiente
        for i in range(idx_map, -1, -1):
            if peak_amplitudes[i] >= peak_amplitudes[idx_map] * self.__SYS_RATIO:
                idx_first_pulse = i
            else:
                if i > 0 and peak_amplitudes[i - 1] >= peak_amplitudes[idx_map] * self.__SYS_RATIO:  # el FIXME
                    continue
                break

        # Tomar sys como último pulso más cercano a MAP que no supere el umbral
        # for i in range(idx_map, -1, -1):
        #     if peak_amplitudes[i] >= peak_amplitudes[idx_map] * self.__SYS_RATIO:
        #         idx_first_pulse = i

        if idx_first_pulse is None:
            raise ValueError(f"Presión sistólica no detectada")

        # idx_first_pulse += 1  # TODO: por la cara pero ver si funciona
        idx_sys = idx_peaks[idx_first_pulse]
        sys = int(self.pressures[idx_sys])

        # ---------------OBTENER SYS--------------------
        idx_last_pulse = None

        # Obtener dia como el primer pico después de map que no supere el umbral ni su siguiente (DIA_RATIO = 0.41)
        for i in range(idx_map, len(peak_amplitudes)):
            if peak_amplitudes[i] >= peak_amplitudes[idx_map] * self.__DIA_RATIO:
                idx_last_pulse = i
            else:
                if i < len(peak_amplitudes) - 1 and peak_amplitudes[i + 1] >= peak_amplitudes[idx_map] * self.__DIA_RATIO:
                    continue
                break

        # Tomar dia como último pulso más cercano a MAP que no supere el umbral (DIA_RATIO = 0.5)
        # for i in range(idx_map, len(peak_amplitudes)):
        #     if peak_amplitudes[i] >= peak_amplitudes[idx_map] * self.__DIA_RATIO:
        #         idx_last_pulse = i
        #
        if idx_last_pulse is None:
            raise ValueError(f"Presión diastólica no detectada")

        # if idx_last_pulse < len(peak_amplitudes)-1:
        #     idx_last_pulse += 1 # TODO: por la cara pero ver si funciona
        idx_dia = idx_peaks[idx_last_pulse]
        dia = int(self.pressures[idx_dia])

        # Rangos extremos 240>sys>70 & 140>dia>40
        if not (240 > sys > 70) or not (140 > dia > 40):
            raise ValueError(f"Presiones fuera de rangos factibles. (SYS: {sys}, DIA: {dia})")

        self.sys = sys
        self.dia = dia

        self.__idx_peaks = idx_peaks[idx_first_pulse:idx_last_pulse + 1]

        return self.__idx_peaks

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

            self.plot_tests(idx_peaks)

            # Volver a filtrar por distanciamiento para quitar falsos picos
            idx_peaks = self.__distance_based_filter(idx_peaks)
            if len(idx_peaks) < 2:
                raise ValueError("No se han encontrado picos en el análisis por distanciamiento.")

            self.plot_tests(idx_peaks)

            # Obtener MAP
            peak_amplitudes, idx_map = self.__get_map(idx_peaks=idx_peaks)

            # Obtener SYS y DIA
            idx_peaks = self.__get_sys_dia(idx_peaks=idx_peaks, peak_amplitudes=peak_amplitudes, idx_map=idx_map)

            # Obtener ppm
            ppm = int(60 * self.fs / np.mean(np.diff(idx_peaks)))
            self.ppm = ppm

            return self.sys, self.dia, self.ppm

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

    def plot_tests(self, idx_peaks: List[int]):
        if PLOT_THROUGH:
            peaks_time = [self.time[i] for i in idx_peaks]
            peaks_pressure = [self.pressures[i] for i in idx_peaks]
            peaks_d_pressure = [self.__d_pressures[i] for i in idx_peaks]

            plt.figure(figsize=(12, 6))

            # Gráfico de presión original con anotaciones de presión sistólica y diastólica
            plt.subplot(2, 1, 1)
            plt.plot(self.time, self.pressures, label='Original pressure')
            plt.plot(self.time, self.__filtered_pressures, label='FIR filtered pressure')
            plt.scatter(peaks_time, peaks_pressure, color='green', label="Pulse peaks", s=26)
            plt.xlabel('Time (s)')
            plt.ylabel('Pressure (mmHg)')
            plt.title('Pressure vs Time')
            plt.grid()
            plt.legend()

            # Gráfico de derivada de presión con picos detectados
            plt.subplot(2, 1, 2)
            plt.plot(self.time, self.__d_pressures, label='Pressure derivative')
            plt.scatter(peaks_time, peaks_d_pressure, color='green', label='Filtered peaks')
            plt.xlabel('Time (s)')
            plt.ylabel('dPressure/dt (mmHg/s)')
            plt.title('Pressure derivative')
            plt.grid()
            plt.legend()

            plt.tight_layout()
            plt.show()
