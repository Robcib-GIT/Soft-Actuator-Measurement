#!/usr/bin/env python3

import rospy
import actionlib
from std_msgs.msg import Bool, Float32, String
from tfm_andres.msg import PneumaticsAction, PneumaticsFeedback, PneumaticsResult
from dataclasses import dataclass
from typing import Optional

actuator_pressure_goal = 200.0 #TODO cambiar
cuff_pressure_goal = 300.0  #TODO cambiar

@dataclass
class PressureGoal:
    valve: int
    pressure: float

@dataclass
class PneumaticState:
    name: str
    pump_on: bool
    valve1_angle: Optional[int]
    valve2_angle: Optional[int]
    goal: Optional[PressureGoal]



class PneumaticsServer:
    STATES = [ #TODO igual añadir algun tipo de funcion ns con callable
        PneumaticState(name="Home", pump_on=False, valve1_angle=90, valve2_angle=90, goal=None),
        PneumaticState(name="Close actuator", pump_on=True, valve1_angle=90, valve2_angle=None, goal=PressureGoal(valve=2, pressure=actuator_pressure_goal)),
        PneumaticState(name="Inflate cuff", pump_on=True, valve1_angle=0, valve2_angle=180, goal=PressureGoal(valve=1, pressure=cuff_pressure_goal)),
        PneumaticState(name="Deflate cuff", pump_on=False, valve1_angle=90, valve2_angle=None, goal=None),
        PneumaticState(name="Open actuator", pump_on=False, valve1_angle=180, valve2_angle=180, goal=None),
        PneumaticState(name="IDLE", pump_on=False, valve1_angle=None, valve2_angle=None, goal=None)
    ]

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
        for state in range(goal.first_state, goal.last_state + 1):
            if self.server.is_preempt_requested():
                rospy.logwarn("Acción pneumática interrumpida.")
                self.server.set_preempted()
                return
            
            progress = 0
            self.setValves(state)

            #TODO añadir algo para start pressure

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

    def setValves(self, state: int): #TODO completar
        self.turnValve(valve=1, angle=PneumaticsServer.STATES[state].valve1_angle)
        self.turnValve(valve=2, angle=PneumaticsServer.STATES[state].valve2_angle)
    
    def calculateProgress(self, state_id: int, start_pressure: float): #TODO completar + returns
        progress = 0
        try:
            state = PneumaticsServer.STATES[state_id]
            if state.goal is None:
                rospy.sleep(3) #TODO configurar
                progress = 1
            else:
                if state.goal.valve == 1: 
                    progress = abs(self.cuff_pressure - start_pressure)/abs(state.goal.pressure - start_pressure)
                else:
                    progress = abs(self.actuator_pressure - start_pressure)/abs(state.goal.pressure - start_pressure)
            
            return progress #TODO completar esto porque naroa no me deja acabar
            
        except IndexError:
            print("Índice fuera de rango")

    def switchOnPump(): #TODO añadir variable global y en set valves meter esta funcion cuando toque solo para cambiar
        print("Swintching on pump")
        #TODO

    def switchOffPump():
        print("Swintching off pump")
        #TODO
    
    def turnValve(valve: int, angle: int):
        print(f"Turning valve {valve} to position {angle}...")
        #TODO

        

if __name__ == '__main__':
    try:
        PneumaticsServer()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
