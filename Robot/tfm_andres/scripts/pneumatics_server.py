# !/usr/bin/env python3
import rospy
import actionlib
from std_msgs.msg import Bool, Float32, String
from tfm_andres.msg import PneumaticsAction, PneumaticsFeedback, PneumaticsResult
from tfm_andres.blood_pressure import BloodPressure
import board
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
import time

# --- Constantes y variables presión arterial --- TODO: refinar y recolocar
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


class PneumaticsServer:
    def __init__(self):
        rospy.init_node('pneumatics_server')
        # Publicadores y subscriptores
        self.actuator_pressure: float = 0.0
        self.cuff_pressure: float = 0.0
        self.actuator_goal_pressure = 600.0
        self.actuator_sub = rospy.Subscriber('/actuator_pressure_data', Float32, self.actuator_pressure_callback)
        self.cuff_sub = rospy.Subscriber('/cuff_pressure_data', Float32, self.cuff_pressure_callback)

        # Servidores de acción
        self.server_blood_pressure = actionlib.SimpleActionServer('blood_pressure', PneumaticsAction, self.execute_blood_pressure, False)
        self.server_blood_pressure.start()
        rospy.loginfo("Servidor de acción 'close_cuff' iniciado")

        self.server_close_actuator = actionlib.SimpleActionServer('close_cuff', PneumaticsAction, self.execute_close_actuator, False)
        self.server_close_actuator.start()
        rospy.loginfo("Servidor de acción 'close_actuator' iniciado")

    def actuator_pressure_callback(self, msg):
        self.actuator_pressure = msg.data

    def cuff_pressure_callback(self, msg):
        self.cuff_pressure = msg.data

    def execute_close_actuator(self, goal):  # TODO: añadir open
        feedback = PneumaticsFeedback()
        result = PneumaticsResult()

        # Colocar válvulas
        cuff_servo.angle = CUFF_BRIDGE_ANGLE
        actuator_servo.angle = ACTUATOR_INFLATE_ANGLE
        time.sleep(1)
        # TODO: activar relé
        rospy.loginfo("Bomba neumática activada")

        start_time = rospy.get_time()
        while self.actuator_pressure <= self.actuator_goal_pressure and not rospy.is_shutdown():
            if self.server_close_actuator.is_preempt_requested():
                rospy.loginfo("Cierre del actuador cancelado")
                self.server_close_actuator.set_preempted()
                return

            # Si se supera cierto límite de tiempo de espera, se aborta
            elapsed_time = rospy.get_time() - start_time
            if elapsed_time > 15.0:  # TODO: ajustar tiempo
                error_str = "Cierre del actuador abortado: tiempo de ejecución excedido"
                rospy.logerr(error_str)
                result.success = False
                self.server.set_aborted(result, text=error_str)
                rospy.loginfo("Cierre del actuador cancelado")

            # Calcular y enviar progreso
            feedback.progress = max(0.0, min(self.actuator_goal_pressure,
                                             self.actuator_pressure)) / self.actuator_goal_pressure
            self.server_close_actuator.publish_feedback(feedback)

        # Cortar suministro de aire
        # TODO: desactivar relé
        rospy.loginfo("Bomba neumática desactivada")
        actuator_servo.angle = ACTUATOR_BRIDGE_ANGLE
        cuff_servo.angle = CUFF_BRIDGE_ANGLE

        # Notificar de finalización exitosa
        result.success = True
        rospy.loginfo("Actuador cerrado con éxito")
        self.server_close_actuator.set_succeeded(result)

    def execute_blood_pressure(self, goal):
        feedback = PneumaticsFeedback()
        result = PneumaticsResult()

        # Colocar válvulas
        cuff_servo.angle = CUFF_BRIDGE_ANGLE
        actuator_servo.angle = ACTUATOR_INFLATE_ANGLE
        time.sleep(1)
        # TODO: activar relé
        rospy.loginfo("Bomba neumática activada")




if __name__ == '__main__':
    try:
        PneumaticsServer()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
