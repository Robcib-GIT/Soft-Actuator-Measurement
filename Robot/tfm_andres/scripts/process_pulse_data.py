#!/usr/bin/env python3

import rospy
from std_msgs.msg import Int32, Int32MultiArray, Float32MultiArray
from tfm_andres.msg import CardiacData
import numpy as np
from scipy.signal import butter, lfilter, find_peaks
from typing import List

# Publicadores
ppg_pub = rospy.Publisher('/ppg_data', Float32MultiArray, queue_size=10) 
cardiac_pub = rospy.Publisher('/cardiac_data', CardiacData, queue_size=10) 

# Constantes y variables generales TODO: Ajustar
MAX_SISTOLICO = 580 # Dedo: 550 | Brazo: 580
BARRERA_SIS_DIA = 525  # Dedo: 515 | Brazo: 525
MIN_DIASTOLICO = 480

INTERVAL = 40
MIN_SAMPLES_PER_BEAT = 7 #Para poder detectar hasta pulsos de 200ppm
MAX_SAMPLES_PER_BEAT = 60  #(60*1000) / (INTERVAL*25) #Para poder detectar hasta pulsos de 25ppm
SHIPPING_SAMPLES = 5      # Envio cada 200ms
MIN_SAMPLES_TO_ANALYZE = 15*5     # 3secs de muestras suficientes para analizar
MAX_SAMPLES_TO_ANALYZE = 1500     # 1min de datos es más que suficiente


# Otros
processing = False
pulse_segment = []
filtered_signal = []
processed_samples = 0
systolics_time = [[], []]
diastolics_time = [[], []]

"""
==============================================================================
1: DEFINICIÓN DE FUNCIONES
==============================================================================
"""

# _______________1.1 Filtro de paso bajo (Butterworth)_______________
def init_low_pass_filter(_cutoff, _fs, order=4):
    nyquist = 0.5 * _fs
    normal_cutoff = _cutoff / nyquist
    _b, _a = butter(order, normal_cutoff, btype='low', analog=False)
    return _b, _a

def apply_low_pass_filter(data, _b, _a, _zi=None):
    if _zi is None:
        _zi = [0 for _ in range(max(len(_a), len(_b))-1)]
    yf, zf = lfilter(_b, _a, data, zi=_zi)
    return yf, zf

fs = 1000 / INTERVAL  # Frecuencia de muestreo (Hz)
cutoff = 3  # Frecuencia de corte (Hz) (entre 2 y 5 va bien)
b, a = init_low_pass_filter(cutoff, fs)
zi = None


# _______________1.x Publicar datos_______________
def publish_ppg_data(_segment):
    msg = Float32MultiArray()
    msg.layout.data_offset = INTERVAL

    # Limitar los valores dentro de un rango y normalizarlos para que estén entre 0 y 1
    adapted_segment = []
    MIN_VAL = MIN_DIASTOLICO-3
    MAX_VAL = MAX_SISTOLICO+3

    adapted_segment = [
        (max(MIN_VAL, min(value, MAX_VAL)) - MIN_VAL) / (MAX_VAL - MIN_VAL)
        for value in _segment
    ]

    # Añadir indicador de final de señal
    if  not processing:
        adapted_segment.append(-1)
    
    msg.data = adapted_segment

    # Enviar mensaje
    ppg_pub.publish(msg)


def get_cardiac_data(_systolics_time_list):
    # Convertir a numpy para mayor agilidad
    _systolics_time = np.array(_systolics_time_list[1])

    # Obtener propiedades del pulso
    if len(_systolics_time) > 1:
        _ibi = np.diff(_systolics_time)  # Intervalo entre pulsos

        # Tomar ultimos 5 pulsos para el ibi
        if len(_ibi)>5:
            temp_ibi = _ibi[-5:]
        else:
            temp_ibi = _ibi

        mean_ibi = np.mean(temp_ibi)
        _frequency = 1000 / mean_ibi
        _pulse = _frequency * 60

        # Tomar ultimos 20 pulsos para el ibi
        if len(_ibi)>20:
            temp_ibi = _ibi[-20:]
        else:
            temp_ibi = _ibi

        if len(temp_ibi)>2:
            _sdnn = np.std(temp_ibi, ddof=1)  # Desviación estándar
        else:
            _sdnn = -1 

        if len(temp_ibi)>1:
            _rmssd = np.sqrt(np.mean(np.diff(temp_ibi)**2))  # Raíz cuadrada de la media de las diferencias al cuadrado 
        else:
            _rmssd = -1 
        
        # Enviar informacion

        cardiac_data_msg = CardiacData()
        cardiac_data_msg.ppm = int(_pulse)
        cardiac_data_msg.ibi = mean_ibi
        cardiac_data_msg.frequency = _frequency
        cardiac_data_msg.sdnn = _sdnn
        cardiac_data_msg.rmssd = _rmssd
        
        # Publicar el mensaje CardiacData
        cardiac_pub.publish(cardiac_data_msg)

# _______________1.x Procesamiento de datos_______________
def process_data(segment: List[int]):
    global zi
    global filtered_signal
    global processed_samples
    global systolics_time
    global diastolics_time

    #1.x.1 Aplicar filtro de paso bajo al segmento y enviarlo
    np_segment = np.array(segment)

    if len(np_segment)>0:
        filtered_segment, zi = apply_low_pass_filter(segment, b, a, zi)
        filtered_signal.extend(filtered_segment)
        processed_samples += len(np_segment)

        # Eliminar sobrante
        if len(filtered_signal) > MAX_SAMPLES_TO_ANALYZE:
            filtered_signal = filtered_signal[SHIPPING_SAMPLES:]

    
    publish_ppg_data(filtered_segment)

    #1.x.2 Extraer información de la señal extendida
    # Utilizar np.array para mayor velocidad
    np_filtered_signal = np.array(filtered_signal)
    samples = len(np_filtered_signal)

    if samples >= MIN_SAMPLES_TO_ANALYZE:
        # Añadir tiempo a la señal
        time = np.arange(processed_samples-samples, processed_samples) * INTERVAL

        # Localizar puntos de interés en los ultimos puntos
        systolic_indexes, _ = find_peaks(
            np_filtered_signal,
            height=(BARRERA_SIS_DIA, MAX_SISTOLICO),
            distance=MIN_SAMPLES_PER_BEAT)
        diastolic_indexes, _ = find_peaks(
            np_filtered_signal,
            height=(MIN_DIASTOLICO, BARRERA_SIS_DIA),
            distance=MIN_SAMPLES_PER_BEAT)
        
        # Añadir nuevos puntos de interes
        if len(systolic_indexes) > 0:
            for index in systolic_indexes:
                # Si el pico no está se guarda
                if time[index] not in systolics_time[1]:
                    systolics_time[0].append(np_filtered_signal[index])
                    systolics_time[1].append(time[index])


        if len(diastolic_indexes) > 0:
            for index in diastolic_indexes:
                # Si el pico no está se guarda
                if time[index] not in systolics_time[1]:
                    diastolics_time[0].append(np_filtered_signal[index])
                    diastolics_time[1].append(time[index])
        
        # Obtener datos médicos  
        get_cardiac_data(systolics_time) 

    
    

# _______________1.X Callback del subscriber_______________
def pulse_data_callback(msg: Int32):
    global pulse_segment
    global filtered_signal
    global processing
    global zi
    global processed_samples
    global systolics_time
    global diastolics_time

    value = msg.data

    if value == -1 and processing:
        rospy.loginfo("Fin del analisis cardiaco")
        processing = False
        process_data(pulse_segment)
        pulse_segment = []
        filtered_signal = []
        processed_samples = 0
        systolics_time = [[], []]
        diastolics_time = [[], []]
        zi = None
    elif value != -1:
        if not processing: 
            rospy.loginfo("Comienzo del analisis cardiaco")
            processing = True

        pulse_segment.append(value)
        
        if len(pulse_segment) >= SHIPPING_SAMPLES:
            process_data(pulse_segment)
            pulse_segment = []



if __name__ == '__main__':
    # Inicializa el nodo
    rospy.init_node('process_pulse_data', anonymous=True)

    # Subscriber para controlar las lecturas de los sensores
    rospy.Subscriber("/pulse_data", Int32, pulse_data_callback)

    rospy.spin()