#!/usr/bin/env python3

import rospy
from std_msgs.msg import Int32, Float32, String, Int32MultiArray, MultiArrayLayout
from dataclasses import dataclass
import ADS1x15
import math

# Declaración de sensores
ADS_1 = ADS1x15.ADS1115(0, 0x48)  # Para pulso y temperatura
ADS_1.setGain(ADS_1.PGA_6_144V)

ADS_2 = ADS1x15.ADS1115(0, 0x49)  # Para presiones
ADS_2.setGain(ADS_2.PGA_0_512V)

# Constantes para sensores
VCC = 5.0  # Voltaje de alimentación (V)
# TEMPERATURA
R_AUX = 10000.0  # Resistencia en serie (ohmios)
R0 = 10000.0  # Resistencia del NTC a T0 (ohmios)
BETA = 3950.0  # Constante beta del NTC (K)
T0 = 25.0 + 273.15  # Temperatura nominal en Kelvin (25°C)


@dataclass
class Sensor:
    publisher: rospy.Publisher
    interval: float = 100.0  # Intervalo entre muestras [ms]
    publishing: bool = False
    last_publish_time: float = 0.0  # Tiempo anterior de publlicacion


sensors = {
    "temperature": Sensor(
        publisher=rospy.Publisher("/temperature_data", Float32, queue_size=10),
        interval=1000
    ),
    "actuator_pressure": Sensor(
        publisher=rospy.Publisher("/actuator_pressure_data", Float32, queue_size=10),
        interval=500
    ),
    "cuff_pressure": Sensor(
        publisher=rospy.Publisher("/cuff_pressure_data", Float32, queue_size=10),
        interval=500
    ),
    "pulse": Sensor(
        publisher=rospy.Publisher("/pulse_data", Int32, queue_size=10),
        interval=40
    ),
}


def publish_sensor_data():
    rospy.loginfo("Nodo de lectura de sensores iniciado correctamente.")

    while not rospy.is_shutdown():
        current_time = rospy.Time.now().to_sec()

        for key, value in sensors.items():
            if value.publishing and (current_time - value.last_publish_time) >= value.interval / 1000.0:
                value.last_publish_time = current_time

                value.publisher.publish(read_sensor(key))
                # rospy.loginfo(f"Valor: {random_value}")


# Función para activar o desactivar la lectura de los sensores
def sensor_control_callback(msg: String):
    sensor_name = msg.data

    if sensor_name in sensors:
        sensors[sensor_name].publishing = not sensors[sensor_name].publishing

        if sensors[sensor_name].publishing:
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


def get_temperature(voltage: float):
    if voltage == 0:
        return 25.0  # Evitar división por cero o log(0)

    R_NTC = R_AUX * (VCC / voltage - 1)
    temperaturaK = 1.0 / ((math.log(R_NTC / R0) / BETA) + (1.0 / T0))
    return temperaturaK - 273.15  # Convertir de Kelvin a Celsius


def get_pressure(value: int):  # TODO: posibilidad de pasar a kPa o mmHg
    # TODO: completar
    pressure = float(value)
    return pressure


# Leer sensor TODO: Modificar 
def read_sensor(sensor: str):
    if sensor in sensors.keys():
        if sensor == "Temperature":
            temperature_raw = ADS_1.readADC(0)
            temperature = ADS_1.toVoltage(temperature_raw)
            return temperature

        elif sensor == "Cuff_Pressure":
            pressure_raw = ADS_2.readADC_Differential_0_1()
            return get_pressure(pressure_raw)

        elif sensor == "Actuator_Pressure":
            pressure_raw = ADS_2.readADC_Differential_2_3()
            return get_pressure(pressure_raw)

        elif sensor == "Pulse":
            return ADS_1.readADC(1)

    else:
        return -2  # No afecta


if __name__ == '__main__':
    # Inicializa el nodo
    rospy.init_node('read_sensors', anonymous=True)

    # Subscriber para controlar las lecturas de los sensores
    rospy.Subscriber("/sensor_command", String, sensor_control_callback)

    # Leer dummy TODO: borrar
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
