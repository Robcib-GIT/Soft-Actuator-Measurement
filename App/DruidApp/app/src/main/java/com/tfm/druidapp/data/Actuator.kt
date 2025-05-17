package com.tfm.druidapp.data

data class ActuationState(
    val name: String,
    val progress: Float = 0f
)

class ActuatorUtilities(val viewModel: MainViewModel) {

    fun closeActuator(){
        viewModel.wsClient.publishToTopic(
            RosMsg(
                operation = MsgOp.PUBLISH,
                topic = "/close_actuator/goal",
                msg = MsgTypes.ActionGoal(goal = emptyMap<String, Float>())
            )
        )
    }

    fun cancelCloseActuator(){
        // Enviar mensaje para cancelar la accion
        val msg = RosMsg(
            operation = MsgOp.PUBLISH,
            topic = "/close_actuator/cancel",
            msg = MsgTypes.ActionCancel()
        )
        viewModel.wsClient.publishToTopic(msg)
    }

    fun openActuator(){
        viewModel.wsClient.publishToTopic(
            RosMsg(
                operation = MsgOp.PUBLISH,
                topic = "/open_actuator/goal",
                msg = MsgTypes.ActionGoal(goal = emptyMap<String, Float>())
            )
        )
    }

    fun cancelOpenActuator(){
        // Enviar mensaje para cancelar la accion
        val msg = RosMsg(
            operation = MsgOp.PUBLISH,
            topic = "/open_actuator/cancel",
            msg = MsgTypes.ActionCancel()
        )
        viewModel.wsClient.publishToTopic(msg)
    }

    fun measureBP(){
        viewModel.wsClient.publishToTopic(
            RosMsg(
                operation = MsgOp.PUBLISH,
                topic = "/blood_pressure/goal",
                msg = MsgTypes.ActionGoal(goal = emptyMap<String, Float>())
            )
        )
    }

    fun cancelMeasureBP(){
        // Enviar mensaje para cancelar la accion
        val msg = RosMsg(
            operation = MsgOp.PUBLISH,
            topic = "/blood_pressure/cancel",
            msg = MsgTypes.ActionCancel()
        )
        viewModel.wsClient.publishToTopic(msg)
    }
}