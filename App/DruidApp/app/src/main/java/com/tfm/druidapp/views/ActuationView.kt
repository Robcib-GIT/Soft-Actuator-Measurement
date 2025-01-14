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
import com.tfm.druidapp.data.MainViewModel
import com.tfm.druidapp.ui.theme.DruidAppTheme
import com.tfm.druidapp.views.customElements.MonitoringState
import com.tfm.druidapp.views.customElements.ProcessProgressIndicator

@Composable
fun ActuationView(viewModel: MainViewModel) {
    val state by viewModel.vitalsMonitoring
    val activationProcessMap by viewModel.activationProcessMap.collectAsState()
    val deactivationProcessMap by viewModel.deactivationProcessMap.collectAsState()
    var prevState = MonitoringState.Enabling

    Column(
        modifier = Modifier
            .padding(16.dp)
            .fillMaxSize(),
        //verticalArrangement = Arrangement.spacedBy(6.dp)
    ) {
        ProcessProgressIndicator(
            state = state,
            text = if (state == MonitoringState.Disabled || state == MonitoringState.Enabling || state == MonitoringState.EnPaused) {
                "Iniciar monitorización"
            } else {
                "Detener monitorización"
            },
            processMap = if (state == MonitoringState.Disabled || state == MonitoringState.Enabling || state == MonitoringState.EnPaused) {
                activationProcessMap
            } else {
                deactivationProcessMap
            },
            onRun = {
                if (state == MonitoringState.Disabled) {
                    viewModel.updateVitalsMonitoring(MonitoringState.Enabling)
                    viewModel.simularProcesos()
                    //TODO: Enviar comando inicializacion
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
                if (state == MonitoringState.Enabling || state == MonitoringState.EnPaused) {
                    viewModel.resetActivationMap()
                    viewModel.updateVitalsMonitoring(MonitoringState.Disabling)
                    prevState = MonitoringState.Disabling
                    //TODO: comenzar disabling
                } else {
                    viewModel.resetDeactivationMap()
                    viewModel.updateVitalsMonitoring(MonitoringState.Enabling)
                    prevState = MonitoringState.Enabling
                    //TODO: comenzar enabling
                }
            },
            onEnd = {
                if (state == MonitoringState.Enabling) {
                    viewModel.updateVitalsMonitoring(MonitoringState.Enabled)
                    viewModel.resetActivationMap()
                    //TODO: comenzar disabling
                } else {
                    viewModel.updateVitalsMonitoring(MonitoringState.Disabled)
                    viewModel.resetDeactivationMap()
                    //TODO: comenzar enabling
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
            ActuationView(vm)
        }
    }
}