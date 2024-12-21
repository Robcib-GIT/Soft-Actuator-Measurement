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

dt = None  # Intervalo de tiempo entre muestras


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
        processed_fragments = 0
        finish_processing = False

        # 1.1.2: Variables para el filtro
        fs = 1000 / dt  # Frecuencia de muestreo (Hz)
        cutoff = 3  # Frecuencia de corte (Hz) (entre 2 y 5 va bien)
        b, a = init_low_pass_filter(cutoff, fs)
        zi = None

        # 1.1.3: Variables para picos
        temp_peaks_time = [np.array([]), np.array([])]

        while not finish_processing:
            filtered_signal = []

            for i in range(SEGMENTOS_ANALISIS):
                segment = message_queue.get()

                if -1 in segment:
                    clipped_segment = []

                    for value in segment:
                        if value == -1:
                            break
                        clipped_segment.append(value)
                    
                    segment = clipped_segment
                    fin_analisis = True
                    break
                
                # TODO: enviar -1 al final cuando se acaba y arreglar
                if len(segment)>0:
                    filtered_segment, zi = apply_low_pass_filter(segment, b, a, zi)
                    publish_segment(filtered_segment.append(-1))
                    filtered_signal.append(filtered_segment)

    segment = []
    
    # Por ejemplo, supongamos que realizas algunas operaciones con los elementos del array
    ppm = sum(segment)  # Operación ficticia
    ibi = float(segment[0])  # Otro valor ficticio basado en el primer elemento
    frecuencia = 60.0 / ibi if ibi > 0 else 0.0  # Ejemplo de frecuencia (inversa de IBI)
    sdnn = 10.0  # Un valor fijo de ejemplo para SDNN
    rmssd = 5.0  # Un valor fijo de ejemplo para RMSSD
    
    # Crear un mensaje CardiacData con los resultados procesados
    cardiac_data_msg = CardiacData()
    cardiac_data_msg.ppm = ppm
    cardiac_data_msg.ibi = ibi
    cardiac_data_msg.frecuencia = frecuencia
    cardiac_data_msg.sdnn = sdnn
    cardiac_data_msg.rmssd = rmssd
    
    # Publicar el mensaje CardiacData
    pub2.publish(cardiac_data_msg)


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
    msg = Int32MultiArray()
    msg.data = _segment
    msg.layout.data_offset = dt
    pub1.publish(msg)


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
    