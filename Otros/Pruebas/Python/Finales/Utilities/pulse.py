import math
from typing import List
import numpy as np
from scipy.signal import butter, lfilter, find_peaks


class BloodPressure:
    MAX_SISTOLICO = 580         # Dedo: 550 | Brazo: 580
    BARRERA_SIS_DIA = 525       # Dedo: 515 | Brazo: 525
    MIN_DIASTOLICO = 480

    def __init__(self, fs: float):  # Añadir un publicador como entrada para enviar segmentos
        self.fs = fs
        self.interval = 1/fs
        self.__min_samples_per_beat = math.ceil(60/200*fs)      # Para pulsos de hasta 200ppm
        self.__max_samples_per_beat = math.ceil(60/25*fs)       # Para pulsos de hasta 25ppm
        self.__min_samples_to_analice = math.ceil(3*fs)         # 3s de muestras suficientes para analizar el pulso
        self.__max_samples_to_analice = math.ceil(60 * fs)      # 60s de muestras suficientes para analizar el pulso

        self.__processing = False
        self.__processed_samples = 0
        self.shipping_samples = math.ceil(200E-3*fs)              # Envio cada 200ms
        self.filtered_signal = []
        self.time = []   # TODO: manejar
        self.systolics_time = [[], []]
        self.diastolics_time = [[], []]

        # Variables para el filtro
        self.__zi: np.ndarray | None = None
        self.__b, self.__a = self.init_low_pass_filter(fc=3, order=4)

    def init_low_pass_filter(self, fc, order=4):
        nyquist = 0.5 * self.fs
        normal_cutoff = fc / nyquist
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a

    def apply_low_pass_filter(self, data: List[int]):
        if not data:
            raise ValueError("Segmento vacío.")

        if self.__zi is None:
            self.__zi = [0 for _ in range(max(len(self.__a), len(self.__b)) - 1)]
        filtered_data, self.__zi = lfilter(self.__b, self.__a, data, zi=self.__zi)

        # TODO: mover esta parte cuando añada publicador
        # Actualizar señales
        self.filtered_signal.extend(filtered_data)
        self.processed_samples += len(data)

        # Eliminar sobrante
        if len(self.filtered_signal) > self.__max_samples_to_analice:
            self.filtered_signal = self.filtered_signal[self.shipping_samples:]

        return filtered_data

    def get_cardiac_data(_systolics_time_list):  #TODO: retocar
        # Convertir a numpy para mayor agilidad
        _systolics_time = np.array(_systolics_time_list[1])

        # Obtener propiedades del pulso
        if len(_systolics_time) > 1:
            _ibi = np.diff(_systolics_time)  # Intervalo entre pulsos

            # Tomar ultimos 5 pulsos para el ibi
            if len(_ibi) > 5:
                temp_ibi = _ibi[-5:]
            else:
                temp_ibi = _ibi

            mean_ibi = np.mean(temp_ibi)
            _frequency = 1000 / mean_ibi
            _pulse = _frequency * 60

            # Tomar ultimos 20 pulsos para el ibi
            if len(_ibi) > 20:
                temp_ibi = _ibi[-20:]
            else:
                temp_ibi = _ibi

            if len(temp_ibi) > 2:
                _sdnn = np.std(temp_ibi, ddof=1)  # Desviación estándar
            else:
                _sdnn = -1

            if len(temp_ibi) > 1:
                _rmssd = np.sqrt(
                    np.mean(np.diff(temp_ibi) ** 2))  # Raíz cuadrada de la media de las diferencias al cuadrado
            else:
                _rmssd = -1

                # Enviar informacion

            return int(_pulse), mean_ibi, _frequency, _sdnn, _rmssd


    def analice_pulse_signal(self):
        filtered_signal = np.array(self.filtered_signal)
        samples = len(filtered_signal)

        if samples >= self.__min_samples_to_analice:
            # Añadir tiempo a la señal TODO: intentar no reasignarlo tanto igual
            self.time = np.arange(self.__processed_samples - samples, self.__processed_samples) * self.interval

            # Localizar puntos de interés en los ultimos puntos
            systolic_indexes, _ = find_peaks(
                self.filtered_signal,
                height=(self.BARRERA_SIS_DIA, self.MAX_SISTOLICO),
                distance=self.__min_samples_per_beat)
            diastolic_indexes, _ = find_peaks(
                self.filtered_signal,
                height=(self.MIN_DIASTOLICO, self.BARRERA_SIS_DIA),
                distance=self.__min_samples_per_beat)

            # Añadir nuevos puntos de interés
            if len(systolic_indexes) > 0:
                for index in systolic_indexes:
                    # Si el pico no está se guarda
                    if self.time[index] not in self.systolics_time[1]:
                        self.systolics_time[0].append(self.filtered_signal[index])
                        self.systolics_time[1].append(self.time[index])

            if len(diastolic_indexes) > 0:
                for index in diastolic_indexes:
                    # Si el pico no está se guarda
                    if self.time[index] not in self.systolics_time[1]:
                        self.diastolics_time[0].append(self.filtered_signal[index])
                        self.diastolics_time[1].append(self.time[index])

            # Obtener datos médicos
            self.get_cardiac_data(self.systolics_time)


            # TODO: def get_cardiac_data(_systolics_time_list):

    # TODO: funcion para reiniio
