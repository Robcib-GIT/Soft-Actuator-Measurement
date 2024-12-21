#!/usr/bin/env python3

import rospy
from std_msgs.msg import String, Int32, Int32MultiArray, MultiArrayLayout
import serial
import json


# Publicadores
pub1 = rospy.Publisher('sensor1_data', Int32, queue_size=10) #Temperatura
pub2 = rospy.Publisher('sensor2_data', Int32MultiArray, queue_size=10) #
pub3 = rospy.Publisher('sensor3_data', Int32MultiArray, queue_size=10) #Pulso

# Funcion para manejar publicaciones
def publish_if_available(key, data, publisher):
    if key in data:
        sensorData = data[key]
        if isinstance(sensorData, dict): 
            periodo = sensorData["offset"]
            msg = Int32MultiArray()
            msg.data = sensorData["data"]
            msg.layout.data_offset = periodo
            #msg.layout = MultiArrayLayout()
            publisher.publish(msg)
        else:
            publisher.publish(sensorData)

# Función para enviar el comando al Arduino
def send_command_to_arduino(command):
    arduino.write(command.encode()) 

# Callback para recibir el comando desde un topic y enviarlo a Arduino
def command_callback(msg):
    rospy.loginfo(f"Comando recibido: {msg.data}")
    send_command_to_arduino(msg.data)

# Función para leer los datos de Arduino y publicar los resultados
def read_data_from_arduino():
    while arduino.in_waiting > 0:
        line = arduino.readline().decode('utf-8').strip()  # Leer la línea de datos del Arduino
        if line:
            try:
                # Parsear el JSON recibido de Arduino
                data = json.loads(line)

                # Publicar los datos de los sensores
                publish_if_available("sensor1", data, pub1)
                publish_if_available("sensor2", data, pub2)
                publish_if_available("sensor3", data, pub3)

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
    rospy.Timer(rospy.Duration(0.1), lambda event: read_data_from_arduino())  # Lee datos del Arduino cada 1 segundo

    rospy.spin()

if __name__ == '__main__':
    main()
