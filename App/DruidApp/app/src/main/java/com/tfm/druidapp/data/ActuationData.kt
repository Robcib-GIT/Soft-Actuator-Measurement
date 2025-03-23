package com.tfm.druidapp.data

data class ActuationState(
    val name: String,
    val progress: Float = 0f
)

class ActuatorUtilities(val viewModel: MainViewModel) {

    val activationFirstState = 1
    val activationLastState = 3
    val deactivationFirstState = 3
    val deactivationLastState = 4

    fun activateActuator(){
        // Enviar mensaje para activar el actuador
        viewModel.wsClient.publishToTopic(
            RosMsg(
                operation = MsgOp.PUBLISH,
                topic = "/pneumatics/goal",
                msg = MsgTypes.ActionGoal(PneumaticsGoal(first_state = activationFirstState, last_state = activationLastState))
            )
        )
    }
    fun deactivateActuator(){
        // Enviar mensaje para desactivar el actuador
        viewModel.wsClient.publishToTopic(
            RosMsg(
                operation = MsgOp.PUBLISH,
                topic = "/pneumatics/goal",
                msg = MsgTypes.ActionGoal(PneumaticsGoal(first_state = deactivationFirstState, last_state = deactivationLastState))
            )
        )
    }

    fun pauseActuator(){ //TODO: completar y añadir otra funcion para continuar si eso

    }

    fun stopActuator(){
        // Enviar mensaje para cancelar la accion
        val msg = RosMsg(
            operation = MsgOp.PUBLISH,
            topic = "/pneumatics/cancel",
            msg = MsgTypes.ActionCancel()
        )
        viewModel.wsClient.publishToTopic(msg)
    }


}