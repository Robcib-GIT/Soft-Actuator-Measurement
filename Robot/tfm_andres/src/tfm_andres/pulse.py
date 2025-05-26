import math
from typing import List
import numpy as np
from scipy.signal import butter, lfilter, find_peaks
import matplotlib.pyplot as plt


class Pulse:

    MAX_HEIGHT = 18000
    MIN_HEIGHT = 10000

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

        # Variables para el filtro
        self.__zi: np.ndarray | None = None
        self.__b, self.__a = self.__init_low_pass_filter(fc=3.5, order=4)

    def __init_low_pass_filter(self, fc, order=4):
        nyquist = 0.5 * self.fs
        normal_cutoff = fc / nyquist
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a

    def apply_low_pass_filter(self, data: List[int]):
        if not data:
            return np.array([])

        else:
            if self.__zi is None:
                self.__zi = [0 for _ in range(max(len(self.__a), len(self.__b)) - 1)]

            coerced_data = [min(max(x, self.MIN_HEIGHT), self.MAX_HEIGHT) for x in data]
            filtered_data, self.__zi = lfilter(self.__b, self.__a, coerced_data, zi=self.__zi)

            # TODO: mover esta parte cuando añada publicador
            # Actualizar señales
            self.filtered_signal.extend(filtered_data)
            self.__processed_samples += len(coerced_data)
            self.signal.extend(coerced_data)

            # Eliminar sobrante del principio
            if len(self.filtered_signal) > self.__max_samples_to_analice:
                self.filtered_signal = self.filtered_signal[self.shipping_samples:]
                self.signal = self.signal[self.shipping_samples:]

            return filtered_data  # TODO: toque

    def __get_cardiac_data(self):  # TODO: retocar
        # Obtener propiedades del pulso
        if len(self.__systolics_time[1]) > 2:
            ibi = np.diff(self.__systolics_time[1])  # Intervalo entre pulsos

            # Tomar últimos 5 pulsos del ibi para datos más cambiantes
            relevant_pulses = 5
            ibi_slice = ibi[-min(len(ibi), relevant_pulses):]
            mean_ibi: float = np.mean(ibi_slice)
            frequency: float = 1/mean_ibi
            ppm = int(frequency * 60)

            # Tomar últimos 20 pulsos para parámetros menos cambiantes
            relevant_pulses = 15
            ibi_slice = ibi[-min(len(ibi), relevant_pulses):]

            if len(ibi_slice) > 2:
                sdnn: float = np.std(ibi_slice, ddof=1)  # Desviación estándar
            else:
                sdnn = -1.0

            if len(ibi_slice) > 1:
                rmssd: float = np.sqrt(
                    np.mean(np.diff(ibi_slice) ** 2))  # Raíz cuadrada de la media de las diferencias al cuadrado
            else:
                rmssd = -1.0

            return ppm, mean_ibi, frequency, sdnn, rmssd

        else:
            return -1, -1.0, -1.0, -1.0, -1.0

    def get_beat_idxs(self):

        # Obtener todos los picos entre 2 alturas y distanciados al menos cierta cantidad de muestras
        # systolic_indexes, _ = find_peaks(
        #     self.filtered_signal,
        #     height=(self.MIN_DIASTOLIC, self.MAX_SYSTOLIC),
        #     distance=self.__min_samples_per_beat)

        # Obtener picos cuya prominencia este entre un 40% por debajo y un 60% por encima de la media
        # de los ultimos 20 secs
        # TODO: ver si el 20 ese lo meto como constante que lo uso en otro lao tambn
        idx_beats, properties = find_peaks(
            self.filtered_signal,
            height=0,
            prominence=0,
            distance=self.__min_samples_per_beat
        )

        n_samples = 20 * self.fs
        # Obtener la posición de partida para la busqueda, si no hay mustras suficientes coge el inicio
        mask = idx_beats >= (len(self.filtered_signal)-n_samples)
        idx_start_search = np.argmax(mask)

        # Obtener rango de prominencias a partir de los picos de esa zona
        mean_prominence = np.mean(properties['prominences'][idx_start_search:])
        prominence_range = (mean_prominence * (1 - 0.4), mean_prominence * (1 + 0.6))

        idx_filtered_prominences = np.where((properties['prominences'] > prominence_range[0])
                                            & (properties['prominences'] < prominence_range[1]))[0]

        idx_beats_filtered = idx_beats[idx_filtered_prominences]

        return idx_beats_filtered

    def analice_pulse_signal(self):
        samples = len(self.filtered_signal)

        if samples >= self.__min_samples_to_analice:
            # Añadir tiempo a la señal TODO: intentar no reasignarlo tanto igual
            self.time = np.arange(self.__processed_samples - samples, self.__processed_samples) * self.interval

            # Localizar puntos de interés en los ultimos puntos
            systolic_indexes = self.get_beat_idxs()

            filtered_signal = np.array(self.filtered_signal)

            # Ahora puedes indexar sin problema
            self.__systolics_time = [
                filtered_signal[systolic_indexes],
                self.time[systolic_indexes]
            ]

            # TODO: meter ppm, ibi etc en self y devolver el anterior si no hay mas picos o ns
            return self.__get_cardiac_data()
        else:
            return -1, -1.0, -1.0, -1.0, -1.0

    def plot_results(self):
        plt.plot(self.time, self.signal, color='r', linewidth=1, label='Pulso original')
        plt.plot(self.time, self.filtered_signal, color='g', linewidth=2, label='Pulso filtrado')
        plt.scatter(self.__systolics_time[1], self.__systolics_time[0], color='blue', label="Picos sistólicos")
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
        self.__zi = None
