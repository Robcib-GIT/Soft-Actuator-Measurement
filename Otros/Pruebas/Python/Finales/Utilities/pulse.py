import math
from typing import List
import numpy as np
from scipy.signal import butter, lfilter, find_peaks
import matplotlib.pyplot as plt


class Pulse:
    MAX_SYSTOLIC = 25000         # Dedo: 550 | Brazo: 580 | Cuello: 25000
    BARRIER_SYS_DIA = 15000      # Dedo: 515 | Brazo: 525  | Cuello: 15000
    MIN_DIASTOLIC = 10000        # Dedo: ? | Brazo: ?  | Cuello: 10000

    def __init__(self, fs: float):  # Añadir un publicador como entrada para enviar segmentos
        self.fs = fs
        self.interval = 1 / fs
        self.__min_samples_per_beat = math.ceil(60 / 200 * fs)  # Para pulsos de hasta 200ppm
        self.__max_samples_per_beat = math.ceil(60 / 25 * fs)  # Para pulsos de hasta 25ppm
        self.__min_samples_to_analice = math.ceil(3 * fs)  # 3s de muestras suficientes para analizar el pulso
        self.__max_samples_to_analice = math.ceil(60 * fs)  # 60s de muestras suficientes para analizar el pulso

        self.__processed_samples = 0
        self.shipping_samples = math.ceil(200E-3 * fs)  # Envio cada 200ms
        self.filtered_signal = []
        self.signal = []  # TODO: ver si borrar
        self.time = []  # TODO: manejar
        self.__systolics_time = [[], []]
        self.__diastolics_time = [[], []]

        # Variables para el filtro
        self.__zi: np.ndarray | None = None
        self.__b, self.__a = self.__init_low_pass_filter(fc=5, order=4)

    def __init_low_pass_filter(self, fc, order=4):
        nyquist = 0.5 * self.fs
        normal_cutoff = fc / nyquist
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a

    def apply_low_pass_filter(self, data: List[int]):
        if not data:
            return []

        else:
            if self.__zi is None:
                self.__zi = [0 for _ in range(max(len(self.__a), len(self.__b)) - 1)]
            filtered_data, self.__zi = lfilter(self.__b, self.__a, data, zi=self.__zi)

            # TODO: mover esta parte cuando añada publicador
            # Actualizar señales
            self.filtered_signal.extend(filtered_data)
            self.__processed_samples += len(data)
            self.signal.extend(data)

            # Eliminar sobrante del principio
            if len(self.filtered_signal) > self.__max_samples_to_analice:
                self.filtered_signal = self.filtered_signal[self.shipping_samples:]
                self.signal = self.signal[self.shipping_samples:]

            return filtered_data

    def __get_cardiac_data(self):  # TODO: retocar
        # Obtener propiedades del pulso
        if len(self.__systolics_time[1]) > 2:
            ibi = np.diff(self.__systolics_time[1])  # Intervalo entre pulsos

            # Tomar últimos 5 pulsos del ibi para datos más cambiantes
            relevant_pulses = 5
            ibi_slice = ibi[-min(len(ibi), relevant_pulses):]
            mean_ibi: float = np.mean(ibi_slice)
            frequency: float = 1000 / mean_ibi
            ppm = int(frequency * 60)

            # Tomar últimos 20 pulsos para parámetros menos cambiantes
            relevant_pulses = 20
            ibi_slice = ibi[-min(len(ibi), relevant_pulses):]

            if len(ibi_slice) > 2:
                sdnn: float = np.std(ibi_slice, ddof=1)  # Desviación estándar
            else:
                sdnn = -1

            if len(ibi_slice) > 1:
                rmssd: float = np.sqrt(
                    np.mean(np.diff(ibi_slice) ** 2))  # Raíz cuadrada de la media de las diferencias al cuadrado
            else:
                rmssd = -1

            return ppm, mean_ibi, frequency, sdnn, rmssd

        else:
            return (-1,) * 5

    def analice_pulse_signal(self):
        samples = len(self.filtered_signal)

        if samples >= self.__min_samples_to_analice:
            # Añadir tiempo a la señal TODO: intentar no reasignarlo tanto igual
            self.time = np.arange(self.__processed_samples - samples, self.__processed_samples) * self.interval

            # Localizar puntos de interés en los ultimos puntos
            systolic_indexes, _ = find_peaks(
                self.filtered_signal,
                height=(self.BARRIER_SYS_DIA, self.MAX_SYSTOLIC),
                distance=self.__min_samples_per_beat)
            diastolic_indexes, _ = find_peaks(
                self.filtered_signal,
                height=(self.MIN_DIASTOLIC, self.BARRIER_SYS_DIA),
                distance=self.__min_samples_per_beat)

            # Añadir nuevos puntos de interés
            if len(systolic_indexes) > 0:
                for index in systolic_indexes:  # FIXME: ver como solucionar lo del recorte
                    # Si el pico no está se guarda
                    if self.time[index] not in self.__systolics_time[1]:
                        self.__systolics_time[0].append(self.filtered_signal[index])
                        self.__systolics_time[1].append(self.time[index])

            if len(diastolic_indexes) > 0:
                for index in diastolic_indexes:
                    # Si el pico no está se guarda
                    if self.time[index] not in self.__systolics_time[1]:
                        self.__diastolics_time[0].append(self.filtered_signal[index])
                        self.__diastolics_time[1].append(self.time[index])

            # Obtener datos médicos
            return self.__get_cardiac_data()
        else:
            return (-1,) * 5

    def plot_results(self):
        plt.plot(self.time, self.signal, color='r', linewidth=1, label='Pulso original')
        plt.plot(self.time, self.filtered_signal, color='g', linewidth=2, label='Pulso filtrado')
        plt.scatter(self.__systolics_time[1], self.__systolics_time[0], color='blue', label="Picos sistólicos")
        plt.scatter(self.__diastolics_time[1], self.__diastolics_time[0], color='orange', label="Picos diastólicos")
        plt.xlabel('Time (s)')
        plt.ylabel('Pulso (mV)')
        plt.title('Pulso vs Tiempo')
        plt.grid()
        plt.legend()
        plt.tight_layout()
        plt.show()

    def restart(self):
        self.__processed_samples = 0
        self.filtered_signal = []
        self.signal = []
        self.time = []
        self.__systolics_time = [[], []]
        self.__diastolics_time = [[], []]
        self.__zi = None
