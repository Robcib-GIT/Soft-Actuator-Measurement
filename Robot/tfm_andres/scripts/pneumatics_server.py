# !/usr/bin/env python3
import rospy
import actionlib
from std_msgs.msg import Bool, Float32, String
from tfm_andres.msg import ActuatorAction, ActuatorFeedback, ActuatorResult
from tfm_andres.blood_pressure import BloodPressure
import board
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
import time

# --- Constantes y variables presión arterial --- TODO: refinar
pressure_fs = 40  # Hz
bp = BloodPressure(pressure_fs)

DEFLATE_THRESHOLD_PRESSURE = 190  # mmHg

# --- Constantes y variables servos --- TODO: refinar rangos servo y angulos
CUFF_INFLATE_ANGLE = 90
CUFF_DEFLATE_ANGLE = 27
CUFF_BRIDGE_ANGLE = 180

ACTUATOR_INFLATE_ANGLE = 90
ACTUATOR_DEFLATE_ANGLE = 27
ACTUATOR_BRIDGE_ANGLE = 180

"""
 I2C BUS 0 (SCL: 28 | SDA: 27)
 I2C BUS 1 (SCL: 5  |  SDA: 3)
"""
BUS_I2C_PCA965 = 0
if BUS_I2C_PCA965 == 1:  #
    i2c = board.I2C()  # o busio.I2C(board.SCL, board.SDA)
else:
    i2c = busio.I2C(board.SCL_1, board.SDA_1)

pca = PCA9685(i2c)
pca.frequency = 50
cuff_servo = servo.Servo(pca.channels[15], min_pulse=650, max_pulse=2650)
actuator_servo = servo.Servo(pca.channels[14], min_pulse=650, max_pulse=2650)


class PneumaticsServer:   # TODO: cambiar para que también sirva para abrirlo
    # TODO: añadir cancelación
    # TODO: añadir cuff server
    def __init__(self):
        rospy.init_node('pneumatics_server')
        # Publicadores y subscriptores
        self.actuator_pressure: float = 0.0
        self.goal_pressure = 600.0
        self.actuator_sub = rospy.Subscriber('/cuff_pressure_data', Float32, self.actuator_pressure_callback)

        # Servidor de acción
        self.server = actionlib.SimpleActionServer('actuator', ActuatorAction, self.execute, False)
        self.server.start()
        rospy.loginfo("Servidor de acción 'actuator' iniciado")

    def actuator_pressure_callback(self, msg):
        self.actuator_pressure = msg.data

    def execute(self, goal):
        feedback = ActuatorFeedback()
        result = ActuatorResult()

        # Colocar válvulas
        cuff_servo.angle = CUFF_BRIDGE_ANGLE
        actuator_servo.angle = ACTUATOR_INFLATE_ANGLE
        time.sleep(1)
        # TODO: activar relé

        while self.actuator_pressure <= self.goal_pressure:
            if self.server.is_preempt_requested():
                rospy.loginfo("Cierre del actuador cancelado")
                self.server.set_preempted()
                return

            feedback.progress = max(0, min(self.goal_pressure, self.actuator_pressure))/self.goal_pressure
            self.server.publish_feedback(feedback)
            rospy.loginfo(f"Progreso: {feedback.progress * 100:.0f}%")

        result.success = True
        rospy.loginfo("Actuador cerrado con éxito")
        self.server.set_succeeded(result)


if __name__ == '__main__':
    try:
        PneumaticsServer()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
