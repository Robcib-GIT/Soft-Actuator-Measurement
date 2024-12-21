#!/usr/bin/env python3

import rospy
from std_msgs.msg import Int32MultiArray, Float32MultiArray
from soft_actuator_measurement.msg import CardiacData
import numpy as np

# Publicadores
pub1 = rospy.Publisher('ppg_data', Float32MultiArray, queue_size=10) 
pub2 = rospy.Publisher('cardiac_data', CardiacData, queue_size=10) 

def callback(data):
    segment = np.array(data.data)
    
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

if __name__ == '__main__':
    rospy.init_node('process_pulse_data', anonymous=True)
    rospy.Subscriber('/sensor2_data', Int32MultiArray, callback)
    rospy.spin()