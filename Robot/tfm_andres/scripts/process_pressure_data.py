#!/usr/bin/env python3

import rospy
from std_msgs.msg import Int32
from tfm_andres.msg import BloodPressureData
import numpy as np
from scipy.signal import butter, lfilter, find_peaks

# Publicadores
bp_pub = rospy.Publisher("/blood_pressure_data", BloodPressureData, queue_size=10)

# Constantes
INTERVAL = 40
SCALE = 5                   #TODO: ajustar
SYSTOLIC_PROMINENCE =20     #TODO: ajustar
DIASTOLIC_PROMINENCE = 25   #TODO: ajustar

# Otros
pressure_data = []
receiving = False
tare_value = 0


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
cutoff = 3  # Frecuencia de corte (Hz) (entre 2 y 5 va bien) TODO ajustar
b, a = init_low_pass_filter(cutoff, fs)
# zi = None

# _______________1.x _______________
def pressure_callback(msg: Int32):
    global receiving
    global pressure_data
    global tare_value

    value = msg.data

    if value == -1:
        if receiving: process_data()    #si es el final de la transmision se procesa la info
        receiving = False
        pressure_data = []
    else:
        if not receiving: 
            receiving = True
            tare_value = value  # Asignar presion inicial
        pressure_data.append(value)

# _______________1.x _______________
def publish_pressure_data(sys: int, dia: int):
    msg = BloodPressureData()
    msg.sys = sys
    msg.dia = dia

    bp_pub.publish(msg)


# _______________1.x _______________
def value_to_pressure(value: int):
    pressure = (value - tare_value)*SCALE
    return int(pressure)

def process_data():
    np_pressure_data = np.array(pressure_data)

    if len(np_pressure_data)>0:
        filtered_pressure_data, _ = apply_low_pass_filter(np_pressure_data, b, a)

        # lo que importa analizar es la porcion de desinflado
        max_index = np.argmax(filtered_pressure_data)
        deflating_pressure = filtered_pressure_data[max_index:]

        # encontrar comienzo de flujo
        sys_indexes, _ = find_peaks(deflating_pressure, prominence=SYSTOLIC_PROMINENCE)
        if len(sys_indexes)>0:
            sys_value = deflating_pressure[sys_indexes[0]]
        else:
            sys_value = -1

        # Encontrar punto intermedio de mayor pico
        peaks_index_phase_1 = [
            deflating_pressure[sys_indexes],
            sys_indexes 
        ]
        # Obtengoo el indice en el que se encuentra ese pico y recorto
        phase_1_end_index = peaks_index_phase_1[1][np.argmax(peaks_index_phase_1[0])]
        deflating_pressure = deflating_pressure[phase_1_end_index:]

        # encontrar punto en el que la sangre fluye libremente
        dia_indexes, _ = find_peaks(deflating_pressure, prominence=SYSTOLIC_PROMINENCE)

        # el ultimo pico sera el critico para la diastolica
        if len(dia_indexes)>0:
            dia_value = deflating_pressure[dia_indexes[-1]]
        else:
            dia_value = -1

        # Convertir valores a presion
        if sys_value == -1:
            sys_pressure = -1
        else:
            sys_pressure = value_to_pressure(sys_value)
        
        if dia_value == -1:
            dia_pressure = -1
        else:
            dia_pressure = value_to_pressure(dia_value)

        
        # Enviar resultados
        publish_pressure_data(sys=sys_pressure, dia=dia_pressure)


if __name__ == '__main__':
    # Inicializa el nodo
    rospy.init_node('process_pressure_data', anonymous=True)

    # Subscriber para controlar las lecturas de los sensores
    rospy.Subscriber("/pressure_data", Int32, pressure_callback)

    rospy.spin()