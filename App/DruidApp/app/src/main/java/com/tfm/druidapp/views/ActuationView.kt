package com.tfm.druidapp.views

import android.content.res.Configuration
import android.util.Log
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import androidx.navigation.compose.rememberNavController
import com.tfm.druidapp.data.MainViewModel
import com.tfm.druidapp.data.MsgOp
import com.tfm.druidapp.data.MsgTypes
import com.tfm.druidapp.data.PneumaticsGoal
import com.tfm.druidapp.data.RosMsg
import com.tfm.druidapp.data.Screen
import com.tfm.druidapp.ui.theme.DruidAppTheme
import com.tfm.druidapp.views.customElements.MonitoringState
import com.tfm.druidapp.views.customElements.ProcessProgressIndicator

@Composable
fun ActuationView(viewModel: MainViewModel, navController: NavHostController) {
    val state by viewModel.vitalsMonitoring
    val actuatorStates by viewModel.actuatorStates.collectAsState()
    val connected by viewModel.connectionState

    Column(
        modifier = Modifier
            .padding(16.dp)
            .fillMaxSize(),
        //verticalArrangement = Arrangement.spacedBy(6.dp)
    ) {
        ProcessProgressIndicator( //TODO:retocar para los cambios nuevos
            state = state,
            text = if (state == MonitoringState.Disabled || state == MonitoringState.Enabling || state == MonitoringState.EnPaused) {
                "Iniciar monitorización"
            } else {
                "Detener monitorización"
            },
            statesList = if (state == MonitoringState.Disabled || state == MonitoringState.Enabling || state == MonitoringState.EnPaused) {
                //Activacion
                actuatorStates.slice(1..3)
            } else {
                listOf(actuatorStates[4])
            },
            onRun = {
                if (state == MonitoringState.Disabled) {
                    if (true/*connected*/){ //TODO: comprobar y habilitar cuando no sean pruebas
                        viewModel.updateVitalsMonitoring(MonitoringState.Enabling)
                        // TODO: borrar
                        // viewModel.simularProcesos()
                        //TODO: Enviar comando inicializacion
                        viewModel.wsClient.publishToTopic(
                            RosMsg(
                                operation = MsgOp.PUBLISH,
                                topic = "/pneumatics/goal",
                                msg = MsgTypes.ActionGoal(PneumaticsGoal(first_state = 1, last_state = 3))
                            )
                        )
                    }else{
                        viewModel.showToast("Robot no conectado")
                    }

                } else {
                    viewModel.updateVitalsMonitoring(MonitoringState.Disabling)
                    //TODO: Enviar comando cancelacion
                }
            },
            onPause = {
                if (state == MonitoringState.EnPaused) {
                    viewModel.updateVitalsMonitoring(MonitoringState.Enabling)
                    //TODO: seguir con enabling
                } else if(state == MonitoringState.DisPaused){
                    viewModel.updateVitalsMonitoring(MonitoringState.Disabling)
                    //TODO: seguir con disabling
                }else {
                    if (state == MonitoringState.Enabling){
                        viewModel.updateVitalsMonitoring(MonitoringState.EnPaused)
                    }else{
                        viewModel.updateVitalsMonitoring(MonitoringState.DisPaused)
                    }
                    //TODO: pausar
                }

            },
            onStop = { //TODO: manejar pause
                viewModel.resetActuatorStates()

                if (state == MonitoringState.Enabling || state == MonitoringState.EnPaused) {
                    viewModel.updateVitalsMonitoring(MonitoringState.Disabling)
                    //TODO: comenzar disabling
                    val msg = RosMsg(
                        operation = MsgOp.PUBLISH,
                        topic = "/pneumatics/cancel",
                        msg = MsgTypes.ActionCancel()
                    )
                    viewModel.wsClient.publishToTopic(msg)
                } else {
                    viewModel.updateVitalsMonitoring(MonitoringState.Enabling)
                    //TODO: comenzar enabling
                }
            },
            onEnd = {
                if (state == MonitoringState.Enabling) {
                    navController.navigate(Screen.Monitoring.route)
                    viewModel.updateVitalsMonitoring(MonitoringState.Enabled)
                    viewModel.resetActuatorStates()
                    viewModel.showToast("Monitorización activada")
                } else {
                    viewModel.updateVitalsMonitoring(MonitoringState.Disabled)
                    viewModel.resetActuatorStates()
                    viewModel.showToast("Monitorización desactivada ")
                }
            }
        )
    }
}


@Preview(showBackground = true, uiMode = Configuration.UI_MODE_NIGHT_YES)
@Composable
fun ActuationViewPreview() {
    DruidAppTheme {
        Surface(
            modifier = Modifier.fillMaxSize(),
            color = MaterialTheme.colorScheme.background
        ) {
            val vm: MainViewModel = viewModel()
            val navController = rememberNavController()
            ActuationView(vm, navController)
        }
    }
}