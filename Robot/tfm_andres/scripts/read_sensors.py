#!/usr/bin/env python3

import rospy
from std_msgs.msg import Int32, Float32, String, Int32MultiArray, MultiArrayLayout
from dataclasses import dataclass
import ADS1x15
import math

# Declaración de sensores
BUS_I2C_ADS115 = 1
ADS_1 = ADS1x15.ADS1115(BUS_I2C_ADS115, 0x49)  # Para pulso y temperatura
ADS_1.setGain(ADS_1.PGA_0_512V)

ADS_2 = ADS1x15.ADS1115(BUS_I2C_ADS115, 0x48)  # Para presiones
ADS_2.setGain(ADS_2.PGA_0_512V)

# Constantes generales para sensores
VCC = 5.0

# Constantes para la temperatura
R_AUX = 10000.0  # Resistencia en serie (ohmios)
R0 = 10000.0  # Resistencia del NTC a T0 (ohmios)
BETA = 3950.0  # Constante beta del NTC (K)
T0 = 25.0 + 273.15  # Temperatura nominal en Kelvin (25°C)


@dataclass
class Sensor:
    publisher: rospy.Publisher
    interval: float = 100.0  # Intervalo entre muestras [ms]
    publishing: bool = False
    last_publish_time: float = 0.0  # Tiempo anterior de publicación [s]


sensors = {
    "temperature": Sensor(
        publisher=rospy.Publisher("/temperature_data", Float32, queue_size=10),
        interval=500  # 2Hz
    ),
    "actuator_pressure": Sensor(
        publisher=rospy.Publisher("/actuator_pressure_data", Float32, queue_size=10),
        interval=10  # 100Hz
    ),
    "cuff_pressure": Sensor(
        publisher=rospy.Publisher("/cuff_pressure_data", Float32, queue_size=10),
        interval=10  # 100Hz
    ),
    "pulse": Sensor(
        publisher=rospy.Publisher("/pulse_data", Int32, queue_size=10),
        interval=40  # 25Hz
    ),
}


def publish_sensor_data():
    rospy.loginfo("Nodo de lectura de sensores iniciado correctamente.")

    while not rospy.is_shutdown():
        current_time = rospy.Time.now().to_sec()

        for sensor_name, sensor in sensors.items():
            if sensor.publishing and (current_time - sensor.last_publish_time) >= sensor.interval / 1000.0:
                sensor.last_publish_time = current_time
                sensor.publisher.publish(read_sensor(sensor_name))
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


def get_temperature() -> float:
    voltage = ADS_1.toVoltage(ADS_1.readADC(0))

    if voltage == 0:
        return 25.0  # Evitar división por cero o log(0)

    r_ntc = R_AUX * (VCC / voltage - 1)
    temperature_k = 1.0 / ((math.log(r_ntc / R0) / BETA) + (1.0 / T0))
    return temperature_k - 273.15  # Convertir de Kelvin a Celsius


def get_pressure(sensor: str):
    if sensor == "actuator":  # Actuator
        offset = -21
        pressure_ref = 200.0
        value_ref = 2870

        # ADS_2.requestADC_Differential_0_1()  # TODO: ver si con esto soluciona
        # pressure_raw = ADS_2.getValue()
        pressure_raw = ADS_2.readADC_Differential_0_1()
    else:  # Cuff
        offset = 11
        pressure_ref = 200.0
        value_ref = 2960
        # ADS_2.requestADC_Differential_2_3()
        # pressure_raw = ADS_2.getValue()
        pressure_raw = ADS_2.readADC_Differential_2_3()

    pressure = (pressure_raw - offset) * pressure_ref / (value_ref - offset)
    return float(pressure)


# Leer sensor TODO: Modificar 
def read_sensor(sensor: str):
    if sensor in sensors.keys():
        if sensor == "temperature":
            return get_temperature()

        elif sensor == "pulse":
            return ADS_1.readADC(1)

        elif sensor == "actuator_pressure":
            return get_pressure(sensor='actuator')

        elif sensor == "cuff_pressure":
            return get_pressure(sensor='cuff')

    else:
        return -2  # No afecta


if __name__ == '__main__':
    # Inicializa el nodo
    rospy.init_node('read_sensors', anonymous=True)

    # Subscriber para controlar las lecturas de los sensores
    rospy.Subscriber("/sensor_command", String, sensor_control_callback)

    try:
        publish_sensor_data()
    except rospy.ROSInterruptException:
        pass
