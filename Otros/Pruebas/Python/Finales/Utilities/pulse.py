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
        self.time = []

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

    def analice_pulse_signal(self):
        print("kk") #TODO: terminar

    # TODO: def get_cardiac_data(_systolics_time_list):

    # TODO: funcion para reiniio
