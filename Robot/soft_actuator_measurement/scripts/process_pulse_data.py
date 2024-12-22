#!/usr/bin/env python3


"""
==============================================================================
0: CONFIGURACIÓN INICIAL
==============================================================================
"""

import rospy
from std_msgs.msg import Int32MultiArray, Float32MultiArray
from soft_actuator_measurement.msg import CardiacData
import numpy as np
import queue
from scipy.signal import butter, lfilter, find_peaks

# Publicadores
pub1 = rospy.Publisher('ppg_data', Float32MultiArray, queue_size=10) 
pub2 = rospy.Publisher('cardiac_data', CardiacData, queue_size=10) 

# Cola para almacenar mensajes
message_queue = queue.Queue()

# Constantes y variables generales TODO: Ajustar
MAX_SISTOLICO = 550  # Dedo: 550 | Brazo: 580
BARRERA_SIS_DIA = 515  # Dedo: 515 | Brazo: 525
MIN_DIASTOLICO = 480
MIN_MUESTRAS_ENTRE_PULSOS = (60 / 100) * (1000 / 40)

MUESTRAS_ENVIO = 5
SEGMENTOS_ANALISIS = 15

dt = 40 # Intervalo de tiempo entre muestras TODO: arreglar actualizacion


"""
==============================================================================
1: DEFINICIÓN DE FUNCIONES
==============================================================================
"""

# _______________1.1 PROCESAMIENTO DE DATOS_______________
# Descripción: Se recopilan los datos almacenados en la cola y se envian después de ser
#   procesados al publicador correspondiente.

def process_data():
    while not rospy.is_shutdown():

        # 1.1.1: Variables generales
        processed_samples = 0
        finish_processing = False # TODO: Arreglar

        # 1.1.2: Variables para el filtro
        fs = 1000 / dt  # Frecuencia de muestreo (Hz)
        cutoff = 3  # Frecuencia de corte (Hz) (entre 2 y 5 va bien)
        b, a = init_low_pass_filter(cutoff, fs)
        zi = None

        # 1.1.3: Variables para picos
        temp_peaks_time = [np.array([]), np.array([])]

        while not rospy.is_shutdown() and not finish_processing:
            filtered_signal = []

            # 1.1.4: Extraer fragmentos de la cola y enviar el fragmento filtrado
            for i in range(SEGMENTOS_ANALISIS):
                segment = message_queue.get()

                if -1 in segment:
                    clipped_segment = []

                    for value in segment:
                        if value == -1:
                            break
                        clipped_segment.append(value)
                    
                    segment = clipped_segment
                    finish_processing = True
                    break
                
                if len(segment)>0:
                    filtered_segment, zi = apply_low_pass_filter(segment, b, a, zi)
                    filtered_signal.extend(filtered_segment)
                
                if not finish_processing:
                    publish_segment(filtered_segment)
                else:
                    publish_segment(filtered_segment.append(-1))  # Para indicar el fin de la transmision

            # 1.1.5: Extraer información de la señal

            # Utilizar np.array para mayor velocidad
            filtered_signal = np.array(filtered_signal)
            sample_items = len(filtered_signal)

            if sample_items > 0:

                # Añadir tiempo a la señal
                time = np.arange(processed_samples, processed_samples + sample_items) * dt

                # Unir sobrante anterior para no pasar picos por alto
                filtered_signal_temp = np.concatenate((temp_peaks_time[0], filtered_signal))
                time_temp = np.concatenate((temp_peaks_time[1], time))

                # Localizar puntos de interés
                systolic_indexes, _ = find_peaks(
                    filtered_signal_temp,
                    height=(BARRERA_SIS_DIA, MAX_SISTOLICO),
                    distance=MIN_MUESTRAS_ENTRE_PULSOS)
                diastolic_indexes, _ = find_peaks(
                    filtered_signal_temp,
                    height=(MIN_DIASTOLICO, BARRERA_SIS_DIA),
                    distance=MIN_MUESTRAS_ENTRE_PULSOS)

                systolics_time = [[], []]
                diastolics_time = [[], []]

                if len(systolic_indexes) > 0:
                    for index in systolic_indexes:
                        systolics_time[0].append(filtered_signal_temp[index])
                        systolics_time[1].append(time_temp[index])

                if len(diastolic_indexes) > 0:
                    for index in diastolic_indexes:
                        diastolics_time[0].append(filtered_signal_temp[index])
                        diastolics_time[1].append(time_temp[index])

                # Almacenal sobrante por si hay picos
                if len(filtered_signal) > 2:
                    clip_index = len(filtered_signal) - 2

                    if len(systolic_indexes) > 0:
                        if systolic_indexes[-1] > clip_index:
                            clip_index = None
                    elif len(diastolic_indexes) > 0:
                        if diastolic_indexes[-1] > clip_index:
                            clip_index = None

                    if clip_index is None:
                        temp_peaks_time = [np.array([]), np.array([])]
                    else:
                        temp_peaks_time[0] = filtered_signal[-2:]
                        temp_peaks_time[1] = time[-2:]

                processed_samples += sample_items     

                # Obtener datos médicos  
                get_medic_data(systolics_time) 

        rospy.loginfo("Terminado de procesar")


# _______________1.X Filtro de paso bajo (Butterworth)_______________

# 1.x.x: Iniciar filtro de paso bajo
def init_low_pass_filter(_cutoff, _fs, order=4):
    nyquist = 0.5 * _fs
    normal_cutoff = _cutoff / nyquist
    _b, _a = butter(order, normal_cutoff, btype='low', analog=False)
    return _b, _a

# 1.x.x: Aplicar filtro de paso bajo
def apply_low_pass_filter(data, _b, _a, _zi=None):
    if _zi is None:
        _zi = [0 for _ in range(max(len(_a), len(_b))-1)]
    yf, zf = lfilter(_b, _a, data, zi=_zi)
    return yf, zf


def publish_segment(_segment):
    msg = Float32MultiArray()
    msg.data = _segment
    msg.layout.data_offset = dt
    pub1.publish(msg)


# _______________1.X Obtener y enviar informacion medica_______________
def get_medic_data(_systolics_time_list):

    # Convertir a numpy para mayor agilidad
    _systolics_times = np.array(_systolics_time_list[1])

    # Obtener propiedades del pulso
    if len(_systolics_times) > 1:
        _ibi = np.diff(_systolics_times)  # Intervalo entre pulsos
        mean_ibi = np.mean(_ibi)
        _frequency = 1000 / mean_ibi
        _pulse = _frequency * 60
        _sdnn = np.std(_ibi/1000)  # Desviación estándar
        _rmssd = np.sqrt(np.mean(np.diff(_ibi/1000)**2))  # Raíz cuadrada de la media de las diferencias al cuadrado

        # Enviar informacion

        cardiac_data_msg = CardiacData()
        cardiac_data_msg.ppm = int(_pulse)
        cardiac_data_msg.ibi = mean_ibi
        cardiac_data_msg.frequency = _frequency
        cardiac_data_msg.sdnn = _sdnn
        cardiac_data_msg.rmssd = _rmssd
        
        # Publicar el mensaje CardiacData
        pub2.publish(cardiac_data_msg)
    


# _______________1.X Callback para el subscriber_______________
def callback(msg):
    # Establecer sample time
    global dt
    if dt is None:
        dt = msg.layout.data_offset
    
    # Añadir fragmento a la colaa
    message_queue.put(msg.data)


"""
==============================================================================
2: Función principal
==============================================================================
"""
if __name__ == '__main__':
    rospy.init_node('process_pulse_data', anonymous=True)
    rospy.Subscriber('/sensor2_data', Int32MultiArray, callback)
    process_data()
    