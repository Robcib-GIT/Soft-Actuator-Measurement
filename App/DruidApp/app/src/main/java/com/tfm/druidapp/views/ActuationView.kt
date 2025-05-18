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
import com.tfm.druidapp.data.ActuatorUtilities
import com.tfm.druidapp.data.MainViewModel
import com.tfm.druidapp.data.MsgOp
import com.tfm.druidapp.data.MsgTypes
import com.tfm.druidapp.data.RosMsg
import com.tfm.druidapp.data.Screen
import com.tfm.druidapp.ui.theme.DruidAppTheme
import com.tfm.druidapp.views.customElements.MonitoringState

@Composable
fun ActuationView(viewModel: MainViewModel, navController: NavHostController) {
    val connected by viewModel.connectionState
    val state by viewModel.vitalsMonitoring
    val openActuatorState by viewModel.openActuatorState.collectAsState()
    val closeActuatorState by viewModel.closeActuatorState.collectAsState()
    val measureBPState by viewModel.measureBPState.collectAsState()
    val actuatorUtilities = ActuatorUtilities(viewModel)

    Column(
        modifier = Modifier
            .padding(16.dp)
            .fillMaxSize(),
        //verticalArrangement = Arrangement.spacedBy(6.dp)
    ) {
        /*ProcessProgressIndicator( //TODO:retocar para los cambios nuevos
            state = state,
            text = if (state == MonitoringState.Disabled || state == MonitoringState.Enabling || state == MonitoringState.EnPaused) {
                "Iniciar monitorización"
            } else {
                "Detener monitorización"
            },
            statesList = if (state == MonitoringState.Disabled || state == MonitoringState.Enabling || state == MonitoringState.EnPaused) {
                //Activacion
                actuatorStates.slice(actuatorUtilities.activationFirstState ..actuatorUtilities.activationLastState)
            } else {
                actuatorStates.slice(actuatorUtilities.deactivationFirstState ..actuatorUtilities.deactivationLastState)
            },
            onRun = {
                if (state == MonitoringState.Disabled) {
                    if (connected){
                        viewModel.updateVitalsMonitoring(MonitoringState.Enabling)

                        // Activar el actuador
                        actuatorUtilities.activateActuator()
                    }else{
                        viewModel.showToast("Robot no conectado")
                    }

                } else {
                    viewModel.updateVitalsMonitoring(MonitoringState.Disabling)

                    // Desactivar el actuador
                    actuatorUtilities.deactivateActuator()
                }
            },
            onPause = {
                if (state == MonitoringState.EnPaused) {
                    viewModel.updateVitalsMonitoring(MonitoringState.Enabling)
                    //TODO: seguir con enabling
                    actuatorUtilities.pauseActuator(pause = false)
                } else if(state == MonitoringState.DisPaused){
                    viewModel.updateVitalsMonitoring(MonitoringState.Disabling)
                    //TODO: seguir con disabling
                    actuatorUtilities.pauseActuator(pause = false)
                }else {
                    if (state == MonitoringState.Enabling){
                        viewModel.updateVitalsMonitoring(MonitoringState.EnPaused)
                    }else{
                        viewModel.updateVitalsMonitoring(MonitoringState.DisPaused)
                    }
                    //TODO: pausar
                    actuatorUtilities.pauseActuator(pause = true)
                }

            },
            onStop = { //TODO: manejar pause
                viewModel.resetActuatorStates()

                if (state == MonitoringState.Enabling || state == MonitoringState.EnPaused) {
                    viewModel.updateVitalsMonitoring(MonitoringState.Disabling)

                    // Cancelar la accion
                    actuatorUtilities.stopActuator()

                    // Desactivar el actuador
                    actuatorUtilities.deactivateActuator()

                } else {
                    viewModel.updateVitalsMonitoring(MonitoringState.Enabling)
                    //TODO: comprobar que funciona
                    // Cancelar la accion
                    actuatorUtilities.stopActuator()

                    // Activar el actuador
                    actuatorUtilities.activateActuator()
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
        )*/
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