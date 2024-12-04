#!/usr/bin/env python3

import rospy
from std_msgs.msg import String
import serial
import json

# Configuración de la conexión serie
arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)  # Cambia '/dev/ttyACM0' según corresponda a tu puerto serie

# Variables globales para almacenar los datos de los sensores
sensor1_data = None
sensor2_data = None
sensor3_data = None

# Publicadores
pub1 = rospy.Publisher('sensor1_data', String, queue_size=10)
pub2 = rospy.Publisher('sensor2_data', String, queue_size=10)
pub3 = rospy.Publisher('sensor3_data', String, queue_size=10)

# Función para enviar el comando al Arduino
def send_command_to_arduino(command):
    arduino.write(command.encode())  # Enviar comando por serie

# Callback para recibir el comando desde un topic y enviarlo a Arduino
def command_callback(msg):
    send_command_to_arduino(msg.data)

# Función para leer los datos de Arduino y publicar los resultados
def read_data_from_arduino():
    while arduino.in_waiting > 0:
        line = arduino.readline().decode('utf-8').strip()  # Leer la línea de datos del Arduino
        if line:
            try:
                # Parsear el JSON recibido de Arduino
                data = json.loads(line)
                # Asignar los valores de los sensores a las variables globales
                global sensor1_data, sensor2_data, sensor3_data
                sensor1_data = data.get("sensor1", None)
                sensor2_data = data.get("sensor2", None)
                sensor3_data = data.get("sensor3", None)

                # Publicar los datos de los sensores
                pub1.publish(str(sensor1_data) if sensor1_data is not None else "null")
                pub2.publish(str(sensor2_data) if sensor2_data is not None else "null")
                pub3.publish(str(sensor3_data) if sensor3_data is not None else "null")

            except json.JSONDecodeError:
                rospy.logwarn("No se pudo decodificar el JSON recibido de Arduino.")

# Función principal
def main():
    rospy.init_node('sensors', anonymous=True)

    # Suscribirse al topic donde se envían los comandos
    rospy.Subscriber('command_topic', String, command_callback)

    # Ejecutar la lectura de datos en segundo plano
    rospy.Timer(rospy.Duration(1), lambda event: read_data_from_arduino())  # Lee datos del Arduino cada 1 segundo

    rospy.spin()

if __name__ == '__main__':
    main()
