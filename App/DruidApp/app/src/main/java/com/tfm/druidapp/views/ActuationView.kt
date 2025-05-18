package com.tfm.druidapp.views

import android.content.res.Configuration
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import androidx.navigation.compose.rememberNavController
import com.tfm.druidapp.R
import com.tfm.druidapp.data.ActuationState
import com.tfm.druidapp.data.ActuatorStates
import com.tfm.druidapp.data.ActuatorUtilities
import com.tfm.druidapp.data.MainViewModel
import com.tfm.druidapp.ui.theme.DruidAppTheme
import com.tfm.druidapp.views.customElements.ActionProcessButton

@Composable
fun ActuationView(viewModel: MainViewModel, navController: NavHostController) {
    val connected by viewModel.connectionState
    val state by viewModel.actuatorState
    val openActuatorState by viewModel.openActuatorState.collectAsState()
    val closeActuatorState by viewModel.closeActuatorState.collectAsState()
    val measureBPState by viewModel.measureBPState.collectAsState()
    val actuatorUtilities = ActuatorUtilities(viewModel)

    Column(
        modifier = Modifier
            .padding(16.dp)
            .fillMaxSize(),
        verticalArrangement = Arrangement.spacedBy(6.dp)
    ) {
        Text(text = "hola")

    }
}

@Composable
fun ActuationContent(){
    val state = ActuatorStates.MeasuringBP
    val openActuatorState = ActuationState(name = "Abrir actuador", progress = 0f)
    val closeActuatorState = ActuationState(name = "Cerrar actuador", progress = 0f)
    val measureBPState = listOf(
        ActuationState("Desinflado", progress = 1f),
        ActuationState("Inflado", progress = 0.5f),
        ActuationState("Procesamiento", progress = 0.1f)
    )

    Column(
        modifier = Modifier
            .padding(16.dp)
            .fillMaxSize(),
        verticalArrangement = Arrangement.spacedBy(6.dp)
    ) {
        ActionProcessButton(
            process = closeActuatorState,
            painterId = R.drawable.rounded_lock_24,
            enabled = state !in listOf(
                ActuatorStates.Opening,
                ActuatorStates.Closing,
                ActuatorStates.MeasuringBP,
                ActuatorStates.Disconnected
                ),
            focus = state in listOf(
                ActuatorStates.Connected,
                ActuatorStates.Closing,
                ActuatorStates.Open
            ),
            onClick = {}
        )

        ActionProcessButton(
            process = openActuatorState,
            painterId = R.drawable.rounded_lock_open_right_24,
            enabled = state !in listOf(
                ActuatorStates.Opening,
                ActuatorStates.Closing,
                ActuatorStates.MeasuringBP,
                ActuatorStates.Disconnected
            ),
            focus = state in listOf(
                ActuatorStates.Connected,
                ActuatorStates.Opening,
                ActuatorStates.Closed
            ),
            onClick = {}
        )

        ActionProcessButton(
            title = "Medir presión arterial",
            processes = measureBPState,
            painterId = R.drawable.rounded_blood_pressure_24,
            enabled = state in listOf(
                ActuatorStates.Closed
            ),
            focus = state in listOf(
                ActuatorStates.MeasuringBP,
                ActuatorStates.Closed
            ),
            expanded = if (state==ActuatorStates.MeasuringBP) true else false,
            onClick = {}
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
            ActuationContent()
        }
    }
}