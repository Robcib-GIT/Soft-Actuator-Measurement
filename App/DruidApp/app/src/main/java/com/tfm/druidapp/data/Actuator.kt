package com.tfm.druidapp.data

enum class ActuatorStates {
    Closing,
    Closed,
    Opening,
    Open,
    MeasuringBP,
    Connected,
    Disconnected
}
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
                msg = MsgTypes.ActionGoalMsg(goal = emptyMap<String, Float>())
            )
        )
        viewModel.updateActuatorState(state = ActuatorStates.Closing)
    }

    fun cancelCloseActuator(){
        // Enviar mensaje para cancelar la accion
        val msg = RosMsg(
            operation = MsgOp.PUBLISH,
            topic = "/close_actuator/cancel",
            msg = MsgTypes.ActionCancelMsg()
        )
        viewModel.wsClient.publishToTopic(msg)

        viewModel.updateActuatorState(state = ActuatorStates.Open)
    }

    fun openActuator(){
        viewModel.wsClient.publishToTopic(
            RosMsg(
                operation = MsgOp.PUBLISH,
                topic = "/open_actuator/goal",
                msg = MsgTypes.ActionGoalMsg(goal = emptyMap<String, Float>())
            )
        )

        viewModel.updateActuatorState(state = ActuatorStates.Opening)
    }

    fun cancelOpenActuator(){
        // Enviar mensaje para cancelar la accion
        val msg = RosMsg(
            operation = MsgOp.PUBLISH,
            topic = "/open_actuator/cancel",
            msg = MsgTypes.ActionCancelMsg()
        )
        viewModel.wsClient.publishToTopic(msg)

        viewModel.updateActuatorState(state = ActuatorStates.Closed)  //TODO: tal vez un prev state pero ñe
    }

    fun measureBP(){
        viewModel.wsClient.publishToTopic(
            RosMsg(
                operation = MsgOp.PUBLISH,
                topic = "/blood_pressure/goal",
                msg = MsgTypes.ActionGoalMsg(goal = emptyMap<String, Float>())
            )
        )

        viewModel.updateActuatorState(state = ActuatorStates.MeasuringBP)
    }

    fun cancelMeasureBP(){
        // Enviar mensaje para cancelar la accion
        val msg = RosMsg(
            operation = MsgOp.PUBLISH,
            topic = "/blood_pressure/cancel",
            msg = MsgTypes.ActionCancelMsg()
        )
        viewModel.wsClient.publishToTopic(msg)

        viewModel.updateActuatorState(state = ActuatorStates.Closed)
    }
}