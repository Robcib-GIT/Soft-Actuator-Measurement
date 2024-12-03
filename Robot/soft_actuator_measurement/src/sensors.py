#!/usr/bin/env python3

import rospy
from sensor_msgs.msg import Temperature, Range, Imu

def publicar_sensor_1(event):
    """Publica datos del Sensor 1."""
    msg = Temperature()
    msg.header.stamp = rospy.Time.now()
    msg.temperature = 25.0
    msg.variance = 0.1
    rospy.loginfo(f"Sensor 1: {msg.temperature}°C")
    pub1.publish(msg)

def publicar_sensor_2(event):
    """Publica datos del Sensor 2."""
    msg = Range()
    msg.header.stamp = rospy.Time.now()
    msg.radiation_type = Range.ULTRASOUND
    msg.range = 1.5
    rospy.loginfo(f"Sensor 2: {msg.range} m")
    pub2.publish(msg)

def publicar_sensor_3(event):
    """Publica datos del Sensor 3."""
    msg = Imu()
    msg.header.stamp = rospy.Time.now()
    msg.angular_velocity.x = 0.01
    msg.angular_velocity.y = 0.02
    msg.angular_velocity.z = 0.03
    rospy.loginfo(f"Sensor 3: Publicando IMU")
    pub3.publish(msg)

if __name__ == "__main__":
    rospy.init_node("sensors", anonymous=True)

    # Crear publicadores
    pub1 = rospy.Publisher("sensor_1_temperature", Temperature, queue_size=10)
    pub2 = rospy.Publisher("sensor_2_range", Range, queue_size=10)
    pub3 = rospy.Publisher("sensor_3_imu", Imu, queue_size=10)

    # Timers para diferentes frecuencias
    rospy.Timer(rospy.Duration(0.1), publicar_sensor_1)  # Frecuencia 10 Hz
    rospy.Timer(rospy.Duration(1.0), publicar_sensor_2)  # Frecuencia 1 Hz
    rospy.Timer(rospy.Duration(5.0), publicar_sensor_3)  # Frecuencia 0.2 Hz

    rospy.loginfo("Nodo 'sensores' inicializado")
    rospy.spin()
