package com.tfm.druidapp.views

import android.content.res.Configuration
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.compose.rememberNavController
import com.tfm.druidapp.data.MainViewModel
import com.tfm.druidapp.ui.theme.DruidAppTheme
import com.tfm.druidapp.views.customElements.ProcessIndicatorsState
import com.tfm.druidapp.views.customElements.ProcessProgressIndicator

@Composable
fun ActuationView(viewModel: MainViewModel){
    val expanded by viewModel.processIndicatorsExpanded
    val state by viewModel.vitalsMonitoring

    val processes = mapOf<String, Float>( //TODO: relacionar con viewmodel
        "Proceso1" to 1f,
        "Proceso2" to 1f,
        "Proceso3" to 0.5f,
        "Proceso4" to 1f,
        "Proceso5" to 0f,
    )

    Column(
        modifier = Modifier
            .padding(16.dp)
            .fillMaxSize(),
        //verticalArrangement = Arrangement.spacedBy(6.dp)
    ) {
        ProcessProgressIndicator(
            expanded = expanded,
            state = state,
            processMap = processes,
            onRun = {
                viewModel.updateProcessIndicatorsState(true)
                viewModel.updateVitalsMonitoring(ProcessIndicatorsState.Active)
                //TODO: enviar comando para empezar
            },
            onPause = {
                if (state == ProcessIndicatorsState.Paused){
                    viewModel.updateVitalsMonitoring(ProcessIndicatorsState.Active)
                    //TODO: reactivar
                }else{
                    viewModel.updateVitalsMonitoring(ProcessIndicatorsState.Paused)
                    //TODO: pausar
                }

            },
            onStop = {
                viewModel.updateProcessIndicatorsState(false)
                viewModel.updateVitalsMonitoring(ProcessIndicatorsState.Inactive)
                //TODO: enviar comando para terminar
            }
        )
    }
}


@Preview(showBackground = true, uiMode = Configuration.UI_MODE_NIGHT_YES)
@Composable
fun ActuationViewPreview(){
    DruidAppTheme{
        Surface(
            modifier = Modifier.fillMaxSize(),
            color = MaterialTheme.colorScheme.background
        ) {
            val vm: MainViewModel = viewModel()
            ActuationView(vm)
        }
    }
}