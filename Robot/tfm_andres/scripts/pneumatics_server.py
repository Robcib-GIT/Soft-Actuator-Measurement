#!/usr/bin/env python3

import rospy
import actionlib
from std_msgs.msg import Bool, Float32, String
from tfm_andres.msg import PneumaticsAction, PneumaticsFeedback, PneumaticsResult

actuator_pressure_goal = 200.0 #TODO cambiar
cuff_pressure_goal = 300.0  #TODO cambiar

class PneumaticsServer:
    def __init__(self):
        rospy.init_node('pneumatics_server')

        # Suscripción a la presión actual
        self.actuator_pressure = 0.0
        self.cuff_pressure = 0.0
        rospy.Subscriber('/actuator_pressure_data', Float32, self.actuator_pressure_callback)
        rospy.Subscriber('/cuff_pressure_data', Float32, self.cuff_pressure_callback)

        # Servidor de acción
        self.server = actionlib.SimpleActionServer('pneumatics', PneumaticsAction, self.execute, False)
        self.server.start()
        self.paused = False #TODO implementar
        rospy.loginfo("Pneumatics Server is running...")

    def actuator_pressure_callback(self, msg):
        self.actuator_pressure = msg.data

    def cuff_pressure_callback(self, msg):
        self.cuff_pressure = msg.data

    def execute(self, goal):
        rospy.loginfo(f"Received target pressure: {goal.target_pressure}")
        rospy.loginfo(f"Ejecutando secuencia: {goal.tasks}")

        feedback = PneumaticsFeedback()
        rate = rospy.Rate(2)  # 2 Hz TODO cambiar

        # Ejecutar la secuencia de válvulas
        for task in goal.tasks:
            if self.server.is_preempt_requested():
                rospy.logwarn("Acción pneumática interrumpida.")
                self.server.set_preempted()
                return
            
            progress = 0
            self.setValves(task)
            rospy.sleep(2)

            while progress<1:
                progress = self.calculateProgress(task)

                # Enviar feedback
                feedback.current_progress = progress
                feedback.current_task = task
                self.server.publish_feedback(feedback)

                rate.sleep()  # TODO cambiar por espera hasta nuevo mensaje igual

        # Enviar resultado
        result = PneumaticsResult(success=True)
        self.server.set_succeeded(result)
        rospy.loginfo("Pneumatics sequence completed successfully.")

    def setValves(task: String): #TODO completar
        if task == "home":
            print("Going to home position")
            #TODO
        elif task == "close actuator":
            print("Closing actuator")
            #TODO
        elif task == "Pump cuff":
            print("Pumping Up cuff")
            #TODO
        else: #IDLE
            pass
    
    def calculateProgress(task: String): #TODO completar + returns
        if task == "home":
            print("Going to home position")
            #TODO
        elif task == "close actuator":
            print("Closing actuator")
            #TODO
        elif task == "Pump cuff":
            print("Pumping Up cuff")
            #TODO
        else: #IDLE
            pass

    def switchOnPump(): #TODO añadir variable global y en set valves meter esta funcion cuando toque solo para cambiar
        print("Swintching on pump")
        #TODO

    def switchOffPump():
        print("Swintching off pump")
        #TODO
        

if __name__ == '__main__':
    try:
        ValveSequenceServer()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
