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
import threading

# --- Constantes y variables presión arterial --- TODO: refinar y recolocar
pressure_fs = 40  # Hz
bp = BloodPressure(pressure_fs)

# --- Constantes y variables servos --- TODO: refinar rangos servo y angulos
CUFF_INFLATE_ANGLE = 90
CUFF_DEFLATE_ANGLE = 27
CUFF_FULL_DEFLATE_ANGLE = 0
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
    # TODO: aádir el resto de constantes
    ACTUATOR_GOAL_PRESSURE = 600.0
    CUFF_GOAL_PRESSURE = 190.0

    def __init__(self):
        rospy.init_node('pneumatics_server')

        # Variables para presiones
        self.actuator_pressure: float = 0.0
        self.new_actuator_pressure_event = threading.Event()
        self.cuff_pressure: float = 0.0
        self.new_cuff_pressure_event = threading.Event()

        # Publicadores y subscriptores
        self.actuator_sub = rospy.Subscriber('/actuator_pressure_data', Float32, self.actuator_pressure_callback)
        self.cuff_sub = rospy.Subscriber('/cuff_pressure_data', Float32, self.cuff_pressure_callback)

        # Servidores de acción
        self.server_blood_pressure = actionlib.SimpleActionServer('blood_pressure', PneumaticsAction,
                                                                  self.execute_blood_pressure, False)
        self.server_blood_pressure.start()
        rospy.loginfo("Servidor de acción 'close_cuff' iniciado")

        self.server_close_actuator = actionlib.SimpleActionServer('close_cuff', PneumaticsAction,
                                                                  self.execute_close_actuator, False)
        self.server_close_actuator.start()
        rospy.loginfo("Servidor de acción 'close_actuator' iniciado")

    @staticmethod
    def check_timeout(start_time: float, max_duration: float, server, result,
                      cancel_msg="Acción cancelada por timeout"):
        """
        Comprueba si se ha superado el tiempo máximo permitido y aborta la acción si es necesario.

        :param start_time: Tiempo de inicio (en segundos).
        :param max_duration: Duración máxima permitida antes de abortar (en segundos).
        :param server: Instancia de SimpleActionServer asociada a la acción.
        :param result: Objeto de tipo Result de la acción.
        :param cancel_msg: Mensaje de error personalizado que se muestra si se aborta la acción.
        :return: True si se aborta por timeout, False si no se ha superado el tiempo límite.
        """
        elapsed_time = rospy.get_time() - start_time
        if elapsed_time > max_duration:
            rospy.logerr(cancel_msg)
            result.success = False
            server.set_aborted(result, text=cancel_msg)
            return True

        return False

    @staticmethod
    def wait_new_value(event, check_interval: float = 1.0):
        """
            Espera de forma bloqueante (con timeout) a que se active un evento que indica la llegada de un nuevo valor.

            :param event: Instancia de threading.Event que se activa cuando se recibe un nuevo dato.
            :param check_interval: Tiempo máximo (en segundos) a esperar antes de continuar.
            :return: True si llegó un nuevo valor, False si se agotó el tiempo de espera sin recibir nada.
        """
        if event.wait(timeout=check_interval):
            event.clear()
            return True
        else:
            rospy.logwarn(f"No han llegado lecturas nuevas en {check_interval:.1}s")
            return False

    def actuator_pressure_callback(self, msg):
        self.actuator_pressure = msg.data
        self.new_actuator_pressure_event.set()

    def cuff_pressure_callback(self, msg):
        self.cuff_pressure = msg.data
        self.new_cuff_pressure_event.set()

    def execute_close_actuator(self, goal):  # TODO: añadir open
        rospy.loginfo("Iniciado cierre del actuador")
        feedback = PneumaticsFeedback()
        result = PneumaticsResult()

        # Colocar válvulas
        cuff_servo.angle = CUFF_BRIDGE_ANGLE
        actuator_servo.angle = ACTUATOR_INFLATE_ANGLE
        rospy.sleep(1)
        # TODO: activar relé
        rospy.loginfo("Bomba neumática activada")

        start_time = rospy.get_time()
        while self.actuator_pressure <= self.ACTUATOR_GOAL_PRESSURE and not rospy.is_shutdown():
            if self.server_close_actuator.is_preempt_requested():
                rospy.loginfo("Cierre del actuador cancelado")
                self.server_close_actuator.set_preempted()
                return

            # Si se supera cierto límite de tiempo de espera, se aborta
            if self.check_timeout(start_time=start_time, max_duration=15.0, server=self.server_close_actuator,
                                  result=result, cancel_msg="Cierre del actuador abortado por timeout"):
                return

            # Para mayor eficacia se espera a que se active el evento que indica la llegada de una nueva lectura
            if not self.wait_new_value(self.new_actuator_pressure_event, check_interval=0.5):
                if rospy.is_shutdown():
                    return
                continue

            # Calcular y enviar progreso
            feedback.progress = max(0.0, min(self.ACTUATOR_GOAL_PRESSURE,
                                             self.actuator_pressure)) / self.ACTUATOR_GOAL_PRESSURE
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
        rospy.loginfo("Iniciada medición de la presión arterial")
        feedback = PneumaticsFeedback()
        result = PneumaticsResult()

        # 1- Desinflar por completo el manguito (progress: 0.0-1.0)
        rospy.loginfo("Fase 1: Comenzado vaciado completo del manguito")
        actuator_servo.angle = ACTUATOR_BRIDGE_ANGLE
        cuff_servo.angle = CUFF_FULL_DEFLATE_ANGLE

        start_time = rospy.get_time()
        while self.cuff_pressure >= 5.0 and not rospy.is_shutdown():
            # Si se supera cierto límite de tiempo de espera, se aborta
            if self.check_timeout(start_time=start_time, max_duration=10.0, server=self.server_blood_pressure,
                                  result=result, cancel_msg="Desinflado del manguito abortado por timeout"):
                return

            # Para mayor eficacia se espera a que se active el evento que indica la llegada de una nueva lectura
            if not self.wait_new_value(self.new_cuff_pressure_event, check_interval=0.5):
                if rospy.is_shutdown():
                    return
                continue

            # Calcular progreso
            feedback.progress = 1.0 - (
                        max(0.0, min(self.cuff_pressure, self.CUFF_GOAL_PRESSURE)) / self.CUFF_GOAL_PRESSURE)
            self.server_blood_pressure.publish_feedback(feedback)

        # 2- Inflar por completo el manguito (progress: 0.0-1.0)
        rospy.loginfo("Fase 2: Comenzado inflado completo del manguito")
        cuff_servo.angle = CUFF_INFLATE_ANGLE
        rospy.sleep(0.5)
        # TODO: activar relé
        rospy.loginfo("Bomba neumática activada")

        start_time = rospy.get_time()
        while not rospy.is_shutdown():




if __name__ == '__main__':
    try:
        PneumaticsServer()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
