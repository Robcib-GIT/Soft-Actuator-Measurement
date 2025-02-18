#!/usr/bin/env python3

import rospy
from std_msgs.msg import Int32, Float32, String, Int32MultiArray, MultiArrayLayout
from dataclasses import dataclass
import random
import os

# Pruebas, TODO: borrar
pulse_dummy = []
pulse_dummy_index = 0

# Declaración de sensores
@dataclass
class Sensor:
    publisher: rospy.Publisher
    interval: float = 100.0  # Intervalo entre muestras [ms]
    publishing: bool = False
    last_publish_time: float = 0.0 # Tiempo anterior de publlicacion

sensors = {
    "Temperature" : Sensor(
        publisher= rospy.Publisher("/temperature_data", Int32, queue_size=10),
        interval= 1000
    ),
    "Actuator_Pressure" : Sensor(
        publisher= rospy.Publisher("/actuator_pressure_data", Float32, queue_size=10),
        interval=500
    ),
    "Cuff_Pressure" : Sensor(
        publisher= rospy.Publisher("/cuff_pressure_data", Float32, queue_size=10),
        interval=500
    ),
    "Pulse" : Sensor(
        publisher= rospy.Publisher("/pulse_data", Int32, queue_size=10),
        interval=40
    ),
}
    



def publish_sensor_data():
    rospy.loginfo("Nodo de lectura de sensores iniciado correctamente.")
    
    while not rospy.is_shutdown():
        current_time = rospy.Time.now().to_sec()

        for key, value in sensors.items():
            if(value.publishing and (current_time-value.last_publish_time) >= value.interval/1000.0):
                value.last_publish_time = current_time

                value.publisher.publish(read_sensor(key))
                #rospy.loginfo(f"Valor: {random_value}")


# Función para activar o desactivar la lectura de los sensores
def sensor_control_callback(msg: String):
    sensor_name = msg.data

    if sensor_name in sensors:
        sensors[sensor_name].publishing = not sensors[sensor_name].publishing

        if(sensors[sensor_name].publishing):
            rospy.loginfo(f"Lecturas de {sensor_name} activadas")
        else:
            rospy.loginfo(f"Lecturas de {sensor_name} desactivadas")

            # Indicar final de transmisión con un -1
            sensors[sensor_name].publisher.publish(-1)

    elif sensor_name.lower() == "all":
        for sensor in sensors.values():
            sensor.publishing = True
        rospy.loginfo("Todas las lecturas activadas")

    elif sensor_name.lower() == "none":
        for sensor in sensors.values():
            sensor.publishing = False

            # Indicar final de transmisión con un -1
            sensor.publisher.publish(-1)
        rospy.loginfo("Todas las lecturas desactivadas")
    
cuff_pressure_temp = 0     #TODO borrar
actuator_pressure_temp = 0     #TODO borrar
# Leer sensor TODO: Modificar 
def read_sensor(sensor: str):
    global pulse_dummy_index #TODO borrar
    global cuff_pressure_temp #TODO borrar
    global actuator_pressure_temp #TODO borrar

    if sensor in sensors.keys():
        if sensor == "Temperature":
            return random.randint(0, 1023)
        elif sensor == "Cuff_Pressure":
            cuff_pressure_temp += 5
            return cuff_pressure_temp
        elif sensor == "Actuator_Pressure":
            actuator_pressure_temp += 5
            return actuator_pressure_temp
        elif sensor == "Pulse":
            if pulse_dummy_index < len(pulse_dummy):
                pulse_value = pulse_dummy[pulse_dummy_index]
                pulse_dummy_index += 1  # Avanzamos al siguiente valor
                return pulse_value
            else:
                return -1

    else:
        return -2   # No afecta


        

if __name__ == '__main__':
    # Inicializa el nodo
    rospy.init_node('read_sensors', anonymous=True)

    # Subscriber para controlar las lecturas de los sensores
    rospy.Subscriber("/sensor_command", String, sensor_control_callback)

    #Leer dummy TODO: borrar
    try:
        file_path = "/home/andres/catkin_ws/src/tfm_andres/resources/SalidaPulsoSujeto1_derecho.txt"
        rospy.loginfo(file_path)
        with open(file_path, "r") as file:
            # Cargamos todo el contenido del archivo y lo convertimos a una lista de enteros
            pulse_dummy = [int(line.strip()) for line in file.readlines()]
    except FileNotFoundError:
        rospy.logwarn("El archivo no se encuentra.")

    try:
        publish_sensor_data()
    except rospy.ROSInterruptException:
        pass