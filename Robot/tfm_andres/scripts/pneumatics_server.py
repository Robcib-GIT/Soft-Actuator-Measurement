# !/usr/bin/env python3
import rospy
import actionlib
from std_msgs.msg import Bool, Float32, String
from tfm_andres.msg import PneumaticsAction, PneumaticsFeedback, PneumaticsResult, BloodPressureData
from tfm_andres.blood_pressure import BloodPressure
import board
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
import threading

# --- Constantes y variables presión arterial --- TODO: refinar y recolocar
PRESSURE_FS = 40  # Hz
bp = BloodPressure(PRESSURE_FS)

# --- Constantes y variables servos --- TODO: refinar rangos servo y ángulos
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
    # TODO: añadir el resto de constantes
    # TODO: en los timeouts añadir desinflado de emergencia + función
    # TODO: controlar los rospy.is_shutdown restantes
    # TODO: añadir activación y desactivación de los sensores de presión
    # TODO: usar on_shutdown para apagar y puentear todo
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
        self.sensor_command_pub = rospy.Publisher('/sensor_command', String, queue_size=10)
        self.bp_pub = rospy.Publisher('/blood_pressure_data', BloodPressureData, queue_size=10)

        # Servidores de acción
        self.server_blood_pressure = actionlib.SimpleActionServer('blood_pressure', PneumaticsAction,
                                                                  self.execute_blood_pressure, False)
        self.server_blood_pressure.start()
        rospy.loginfo("Servidor de acción 'close_cuff' iniciado")

        self.server_close_actuator = actionlib.SimpleActionServer('close_actuator', PneumaticsAction,
                                                                  self.execute_close_actuator, False)
        self.server_close_actuator.start()
        rospy.loginfo("Servidor de acción 'close_actuator' iniciado")

        self.server_open_actuator = actionlib.SimpleActionServer('open_actuator', PneumaticsAction,
                                                                 self.execute_open_actuator, False)
        self.server_open_actuator.start()
        rospy.loginfo("Servidor de acción 'open_actuator' iniciado")

    @staticmethod
    def check_timeout(start_time: float, max_duration: float, server, result,
                      name: str):
        """
        Comprueba si se ha superado el tiempo máximo permitido y aborta la acción si es necesario.
        :param start_time: Tiempo de inicio (en segundos).
        :param max_duration: Duración máxima permitida antes de abortar (en segundos).
        :param server: Instancia de SimpleActionServer asociada a la acción.
        :param result: Objeto de tipo Result de la acción.
        :param name: Nombre del proceso.
        :return: True si se aborta por timeout, False si no se ha superado el tiempo límite.
        """
        elapsed_time = rospy.get_time() - start_time
        if elapsed_time > max_duration:
            cancel_msg = f"{name}: Cancelado por timeout"
            rospy.logerr(cancel_msg)
            result.success = False
            server.set_aborted(result, text=cancel_msg)
            return True

        return False

    @staticmethod
    def wait_new_value(event, check_interval: float = 1.0):
        """
            Espera de forma bloqueante (con timeout) a que se active un evento que indica la llegada de un nuevo valor.
            :param event: Instancia de threading. Event que se activa cuando se recibe un nuevo dato.
            :param check_interval: Tiempo máximo (en segundos) a esperar antes de continuar.
            :return: True si llegó un nuevo valor, False si se agotó el tiempo de espera sin recibir nada.
        """
        if event.wait(timeout=check_interval):
            event.clear()
            return True
        else:
            rospy.logwarn(f"No han llegado lecturas nuevas en {check_interval:.1}s")
            return False

    def publish_blood_pressure(self, sys: int, dia: int):
        msg = BloodPressureData()
        msg.sys = sys
        msg.dia = dia
        self.bp_pub.publish(msg)

    def toggle_sensor(self, sensor: str):  # TODO: meterlo donde toque
        msg = String()
        msg.data = sensor
        self.sensor_command_pub.publish(msg)

    def actuator_pressure_callback(self, msg):
        self.actuator_pressure = msg.data
        self.new_actuator_pressure_event.set()

    def cuff_pressure_callback(self, msg):
        self.cuff_pressure = msg.data
        self.new_cuff_pressure_event.set()

    def get_process_status(self, name: str, start_time: float, server, result, new_value_event, timeout: float = 15.0,
                           value_check_interval: float = 0.5) -> str:
        """
        Comprueba si hay cancelación, timeout o falta de nuevas lecturas de datos.

        :param name: Nombre del proceso.
        :param start_time: Tiempo en segundos desde el inicio del proceso.
        :param server: Servidor de acción que contiene al proceso.
        :param result: Objeto de resultado que será actualizado en caso de cancelación o error.
        :param new_value_event: Evento que indica la llegada de una nueva lectura.
        :param timeout: Tiempo máximo de espera antes de abortar el proceso. Por defecto, 15.0 segundos.
        :param value_check_interval: Intervalo entre verificaciones del evento. Por defecto, 0.5 segundos.

        :return: Estado del proceso. Puede ser:
                 - 'cancelled': si se solicitó una cancelación.
                 - 'timeout': si se superó el tiempo de espera.
                 - 'no_new_value': si no llegó una nueva lectura en el intervalo especificado.
                 - 'ok': si transcurrió correctamente.
        """

        if server.is_preempt_requested():
            rospy.loginfo(f"{name}: cancelado por el cliente")
            server.set_preempted()
            return 'cancelled'

        if self.check_timeout(start_time=start_time, max_duration=timeout, server=server, result=result, name=name):
            return 'timeout'

        if not self.wait_new_value(new_value_event, check_interval=value_check_interval):
            return 'no_new_value'

        return 'ok'

    def abort_actuator(self):
        # TODO: desactivar relé
        rospy.loginfo("Bomba neumática desactivada")
        cuff_servo.angle = CUFF_BRIDGE_ANGLE
        actuator_servo.angle = ACTUATOR_DEFLATE_ANGLE
        self.toggle_sensor("actuator_pressure")

    def abort_bp(self):
        # TODO: desactivar relé
        rospy.loginfo("Bomba neumática desactivada")
        cuff_servo.angle = CUFF_DEFLATE_ANGLE
        actuator_servo.angle = ACTUATOR_BRIDGE_ANGLE
        self.toggle_sensor("cuff_pressure")

    def execute_close_actuator(self, goal):  # TODO: añadir open
        rospy.loginfo("Iniciado cierre del actuador")
        feedback = PneumaticsFeedback()
        result = PneumaticsResult()

        # Activar sensor de presión
        self.toggle_sensor("actuator_pressure")

        # Colocar válvulas
        cuff_servo.angle = CUFF_BRIDGE_ANGLE
        actuator_servo.angle = ACTUATOR_INFLATE_ANGLE
        rospy.sleep(1)
        # TODO: activar relé
        rospy.loginfo("Bomba neumática activada")

        start_time = rospy.get_time()
        while not rospy.is_shutdown():
            status = self.get_process_status(
                name="Cierre del actuador",
                start_time=start_time,
                server=self.server_close_actuator,
                result=result,
                new_value_event=self.new_actuator_pressure_event,
                timeout=15.0,
                value_check_interval=0.5
            )

            if status in ['cancelled', 'timeout']:
                self.abort_actuator()
                return
            if status == 'no_new_value':
                continue

            if self.actuator_pressure >= self.ACTUATOR_GOAL_PRESSURE:
                # Desactivar sensor de presión
                self.toggle_sensor("actuator_pressure")
                break

            # Calcular y enviar progreso
            feedback.progress = max(0.0, min(self.ACTUATOR_GOAL_PRESSURE,
                                             self.actuator_pressure)) / self.ACTUATOR_GOAL_PRESSURE
            self.server_close_actuator.publish_feedback(feedback)

        # Cortar suministro de aire
        # TODO: desactivar relé
        rospy.loginfo("Bomba neumática desactivada")

        if not rospy.is_shutdown():
            actuator_servo.angle = ACTUATOR_BRIDGE_ANGLE
            cuff_servo.angle = CUFF_BRIDGE_ANGLE

            # Notificar de finalización exitosa
            result.success = True
            rospy.loginfo("Actuador cerrado con éxito")
            self.server_close_actuator.set_succeeded(result)

    def execute_open_actuator(self, goal):  # TODO: añadir open
        rospy.loginfo("Iniciado apertura del actuador")
        feedback = PneumaticsFeedback()
        result = PneumaticsResult()

        # Activar sensor de presión
        self.toggle_sensor("actuator_pressure")

        # Colocar válvulas
        cuff_servo.angle = CUFF_BRIDGE_ANGLE
        actuator_servo.angle = ACTUATOR_DEFLATE_ANGLE

        start_time = rospy.get_time()
        while not rospy.is_shutdown():
            status = self.get_process_status(
                name="Apertura del actuador",
                start_time=start_time,
                server=self.server_open_actuator,
                result=result,
                new_value_event=self.new_actuator_pressure_event,
                timeout=6.0,
                value_check_interval=0.5
            )

            if status in ['cancelled', 'timeout']:
                self.abort_actuator()
                return
            if status == 'no_new_value':
                continue

            if self.actuator_pressure <= 5:
                # Desactivar sensor de presión
                self.toggle_sensor("actuator_pressure")
                break

            # Calcular y enviar progreso
            feedback.progress = 1.0 - max(0.0, min(self.ACTUATOR_GOAL_PRESSURE,
                                                   self.actuator_pressure)) / self.ACTUATOR_GOAL_PRESSURE
            self.server_close_actuator.publish_feedback(feedback)

        if not rospy.is_shutdown():
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
        pressures = []

        # 1- Desinflar por completo el manguito (progress: 0.0-1.0)
        # Activar sensor de presión
        self.toggle_sensor("cuff_pressure")

        rospy.loginfo("Fase 1: Comenzado vaciado completo del manguito")
        actuator_servo.angle = ACTUATOR_BRIDGE_ANGLE
        cuff_servo.angle = CUFF_FULL_DEFLATE_ANGLE

        start_time = rospy.get_time()
        while not rospy.is_shutdown():
            status = self.get_process_status(
                name="Desinflado completo del manguito",
                start_time=start_time,
                server=self.server_blood_pressure,
                result=result,
                new_value_event=self.new_cuff_pressure_event,
                timeout=10.0,
                value_check_interval=0.5
            )

            if status in ['cancelled', 'timeout']:
                self.abort_bp()
                return
            if status == 'no_new_value':
                continue

            if self.cuff_pressure <= 5.0:
                feedback.progress = 1.0
                break

            # Calcular progreso
            feedback.progress = 1.0 - (
                    max(0.0, min(self.cuff_pressure, self.CUFF_GOAL_PRESSURE)) / self.CUFF_GOAL_PRESSURE)
            self.server_blood_pressure.publish_feedback(feedback)

        # 2- Inflar por completo el manguito (progress: 1.0-2.0)
        if not rospy.is_shutdown():
            rospy.loginfo("Fase 2: Comenzado inflado completo del manguito")
            cuff_servo.angle = CUFF_INFLATE_ANGLE
            rospy.sleep(0.5)
            # TODO: activar relé
            rospy.loginfo("Bomba neumática activada")

        start_time = rospy.get_time()
        while not rospy.is_shutdown():
            status = self.get_process_status(
                name="Inflado del manguito",
                start_time=start_time,
                server=self.server_blood_pressure,
                result=result,
                new_value_event=self.new_cuff_pressure_event,
                timeout=10.0,
                value_check_interval=0.5
            )

            if status in ['cancelled', 'timeout']:
                self.abort_bp()
                return
            if status == 'no_new_value':
                continue

            if self.cuff_pressure >= self.CUFF_GOAL_PRESSURE:
                feedback.progress = 2.0
                # TODO: desactivar relé
                rospy.loginfo("Bomba neumática desactivada")
                break

            pressures.append(self.cuff_pressure)
            # Calcular progreso
            feedback.progress = 1.0 + (
                    max(0.0, min(self.cuff_pressure, self.CUFF_GOAL_PRESSURE)) / self.CUFF_GOAL_PRESSURE)
            self.server_blood_pressure.publish_feedback(feedback)

        # 3- Desinflado controlado del manguito (progress: 2.0-3.0)
        if not rospy.is_shutdown():
            rospy.loginfo("Fase 3: Comenzado desinflado controlado del manguito")
            cuff_servo.angle = CUFF_DEFLATE_ANGLE

        start_time = rospy.get_time()
        samples_prev_opening = 0
        while not rospy.is_shutdown():
            status = self.get_process_status(
                name="Desinflado controlado del manguito",
                start_time=start_time,
                server=self.server_blood_pressure,
                result=result,
                new_value_event=self.new_cuff_pressure_event,
                timeout=60.0,
                value_check_interval=0.5
            )

            if status in ['cancelled', 'timeout']:
                self.abort_bp()
                return
            if status == 'no_new_value':
                continue

            if self.cuff_pressure <= 15.0:
                feedback.progress = 3.0
                # Desactivar sensor de presión
                self.toggle_sensor("cuff_pressure")
                # Dejar salir el resto del aire al terminar
                cuff_servo.angle = CUFF_FULL_DEFLATE_ANGLE
                break

            pressures.append(self.cuff_pressure)
            samples_prev_opening += 1
            p_velocity = bp.calculate_velocity(pressures=pressures, sample_time=0.1)  # FIXME: actualizar función
            # Calcular progreso
            feedback.progress = 3.0 - (
                    max(0.0, min(self.cuff_pressure, self.CUFF_GOAL_PRESSURE)) / self.CUFF_GOAL_PRESSURE)
            self.server_blood_pressure.publish_feedback(feedback)

            if p_velocity > -2 and samples_prev_opening >= int(4 / bp.sample_interval):  # FIXME: igual poner con tiempo
                cuff_servo.angle -= 1
                samples_prev_opening = 0

        # 4- Cálculo de la presión arterial
        if not rospy.is_shutdown():
            rospy.loginfo("Fase 4: Cálculo de la presión arterial")

            try:
                sys, dia = bp.get_blood_pressure(pressures)
                # bp.plot_results()
                # Notificar de finalización exitosa
                self.publish_blood_pressure(sys=sys, dia=dia)
                result.success = True
                self.server_blood_pressure.set_succeeded(result)
            except Exception:
                rospy.logerr("Ocurrió un error al procesar los datos.")
                self.publish_blood_pressure(sys=-1, dia=-1)
                result.success = False
                self.server_blood_pressure.set_succeeded(result)


if __name__ == '__main__':
    try:
        PneumaticsServer()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
