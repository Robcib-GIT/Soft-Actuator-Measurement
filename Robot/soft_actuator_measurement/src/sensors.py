#!/usr/bin/env python3

import rospy
from std_msgs.msg import String, Float32
import serial
import json

# Variables globales para almacenar los datos de los sensores
sensor1_data = None
sensor2_data = None
sensor3_data = None

previous_sensor1_data = None
previous_sensor2_data = None
previous_sensor3_data = None

# Publicadores
pub1 = rospy.Publisher('sensor1_data', Float32, queue_size=10)
pub2 = rospy.Publisher('sensor2_data', Float32, queue_size=10)
pub3 = rospy.Publisher('sensor3_data', Float32, queue_size=10)

# Funcion para manejar publicaciones
def publish_if_not_none(sensor_data, previous_data, publisher):
    if sensor_data is not None:
        publisher.publish(sensor_data)
        return sensor_data  
    elif previous_data is not None:
        publisher.publish(float(-1))
        return None  
    return previous_data  

# Función para enviar el comando al Arduino
def send_command_to_arduino(command):
    arduino.write(command.encode()) 

# Callback para recibir el comando desde un topic y enviarlo a Arduino
def command_callback(msg):
    rospy.loginfo(f"Comando recibido: {msg.data}")
    send_command_to_arduino(msg.data)

# Función para leer los datos de Arduino y publicar los resultados
def read_data_from_arduino():
    global previous_sensor1_data, previous_sensor2_data, previous_sensor3_data
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
                previous_sensor1_data = publish_if_not_none(sensor1_data, previous_sensor1_data, pub1)
                previous_sensor2_data = publish_if_not_none(sensor2_data, previous_sensor2_data, pub2)
                previous_sensor3_data = publish_if_not_none(sensor3_data, previous_sensor3_data, pub3)
                #rospy.loginfo(f"Sensor 1: {sensor1_data}, Sensor 2: {sensor2_data}, Sensor 3: {sensor3_data}")

            except json.JSONDecodeError:
                rospy.logwarn("No se pudo decodificar el JSON recibido de Arduino.")

# Función principal
def main():
    rospy.init_node('sensors', anonymous=True)

    # Configuración de la conexión serie
    try:
        global arduino
        arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)  # Cambia '/dev/ttyACM0' según corresponda a tu puerto serie
        rospy.loginfo("Conexión serie establecida correctamente.")
    except serial.SerialException as e:
        rospy.logerr(f"Error al intentar conectar con el puerto serie: {e}")
        rospy.signal_shutdown("Error de conexión serie, cerrando el nodo.")

    # Suscribirse al topic donde se envían los comandos
    rospy.Subscriber('command_topic', String, command_callback)

    # Ejecutar la lectura de datos en segundo plano
    rospy.Timer(rospy.Duration(1), lambda event: read_data_from_arduino())  # Lee datos del Arduino cada 1 segundo

    rospy.spin()

if __name__ == '__main__':
    main()
