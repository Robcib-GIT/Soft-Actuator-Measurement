#!/usr/bin/env python3
"""
import rospy
import actionlib
from std_msgs.msg import Bool, Float32, String
from tfm_andres.msg import PneumaticsAction, PneumaticsFeedback, PneumaticsResult
from dataclasses import dataclass
from typing import Optional
"""

# !/usr/bin/env python3
import rospy
import actionlib
from std_msgs.msg import Bool, Float32, String
from tfm_andres.msg import ActuatorAction, ActuatorFeedback, ActuatorResult


class ActuatorServer:
    # TODO: añadir cancelación
    def __init__(self):
        rospy.init_node('actuator_server')
        # Publicadores y subscriptores
        self.actuator_pressure = 0.0
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

        # Acción simulada con duración de 10 pasos
        total_steps = 10
        for i in range(total_steps):
            if self.server.is_preempt_requested():
                rospy.loginfo("Acción preemptada")
                self.server.set_preempted()
                return

            feedback.progress = float(i + 1) / total_steps
            self.server.publish_feedback(feedback)
            rospy.loginfo(f"Progreso: {feedback.progress * 100:.0f}%")
            time.sleep(0.5)  # Simula trabajo

        result.success = True
        rospy.loginfo("Acción completada con éxito")
        self.server.set_succeeded(result)


if __name__ == '__main__':
    try:
        ActuatorServer()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
