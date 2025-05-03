#!/usr/bin/env python3

from typing import List

import rospy
from std_msgs.msg import Int32, Float32MultiArray
from tfm_andres.msg import CardiacData
from tfm_andres.pulse import Pulse

# Publicadores
ppg_pub = rospy.Publisher('/ppg_data', Float32MultiArray, queue_size=10)
cardiac_pub = rospy.Publisher('/cardiac_data', CardiacData, queue_size=10)

fs = 25  # 1/40ms
pulse = Pulse(fs=fs)
processing = False
pulse_segment = []


def publish_ppg_data(segment: List[int]):
    msg = Float32MultiArray()
    msg.layout.data_offset = pulse.interval

    # Limitar los valores dentro de un rango y normalizarlos para que estén entre 0 y 1
    min_val = pulse.MIN_DIASTOLIC - 3
    max_val = pulse.MAX_SYSTOLIC + 3
    adapted_segment = [
        (max(min_val, min(value, max_val)) - min_val) / (max_val - min_val)
        for value in segment
    ]

    # Añadir indicador de final de señal
    if not processing:
        adapted_segment.append(-1)

    msg.data = adapted_segment

    # Enviar mensaje
    ppg_pub.publish(msg)


def publish_cardiac_data(ppm: int, ibi: float, frequency: float, sdnn: float, rmssd: float):
    msg = CardiacData()
    msg.ppm = ppm
    msg.ibi = ibi
    msg.frequency = frequency,
    msg.sdnn = sdnn
    msg.rmssd = rmssd

    cardiac_pub.publish(msg)


def process_pulse_segment():
    # Filtrar el segmento a enviar
    filtered_segment = pulse.apply_low_pass_filter(pulse_segment)
    publish_ppg_data(filtered_segment)
    # Extraer y enviar info cardiaca
    ppm, ibi, frequency, sdnn, rmssd = pulse.analice_pulse_signal()
    publish_cardiac_data(ppm, ibi, frequency, sdnn, rmssd)


def pulse_data_callback(msg: Int32):
    global pulse_segment
    global processing

    value = msg.data

    if value == -1 and processing:
        processing = False
        process_pulse_segment()
        pulse.plot_results()
        pulse.restart()
        pulse_segment = []
        print("Fin del análisis cardiaco")

    elif value != -1:
        if not processing:
            print("Comienzo del análisis cardiaco")
            processing = True

        pulse_segment.append(value)

        if len(pulse_segment) >= pulse.shipping_samples:
            process_pulse_segment()
            pulse_segment = []


if __name__ == '__main__':
    # Inicializa el nodo
    rospy.init_node('process_pulse_data', anonymous=True)

    # Subscriber para controlar las lecturas de los sensores
    rospy.Subscriber("/pulse_data", Int32, pulse_data_callback)

    rospy.spin()
