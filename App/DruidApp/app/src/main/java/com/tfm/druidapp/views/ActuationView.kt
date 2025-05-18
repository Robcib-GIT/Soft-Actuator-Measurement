package com.tfm.druidapp.views

import android.content.res.Configuration
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonColors
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import androidx.navigation.compose.rememberNavController
import com.tfm.druidapp.R
import com.tfm.druidapp.data.ActuatorStates
import com.tfm.druidapp.data.ActuatorUtilities
import com.tfm.druidapp.data.DataStoreManager
import com.tfm.druidapp.data.MainViewModel
import com.tfm.druidapp.ui.theme.DruidAppTheme
import com.tfm.druidapp.views.customElements.ActionProcessButton

@Composable
fun ActuationView(viewModel: MainViewModel, navController: NavHostController) {
    val state by viewModel.actuatorState
    val openActuatorState by viewModel.openActuatorState.collectAsState()
    val closeActuatorState by viewModel.closeActuatorState.collectAsState()
    val measureBPState by viewModel.measureBPState.collectAsState()
    val actuatorUtilities = ActuatorUtilities(viewModel)

    Column(
        modifier = Modifier
            .padding(16.dp)
            .fillMaxSize(),
        verticalArrangement = Arrangement.spacedBy(6.dp),
        horizontalAlignment = Alignment.CenterHorizontally
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
            onClick = {actuatorUtilities.closeActuator()}
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
            onClick = {actuatorUtilities.openActuator()}
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
            expanded = state==ActuatorStates.MeasuringBP,
            onClick = {actuatorUtilities.measureBP()}
        )

        Spacer(modifier = Modifier.weight(1f))

        StopButton(
            state = state,
            onClick = {
                when(state){
                    ActuatorStates.Opening->{
                        actuatorUtilities.cancelOpenActuator()
                    }
                    ActuatorStates.Closing->{
                        actuatorUtilities.cancelCloseActuator()
                    }
                    ActuatorStates.MeasuringBP->{
                        actuatorUtilities.cancelMeasureBP()
                    }
                    else->{}
                }
            }
        )


    }
}

@Composable
fun StopButton(
    state: ActuatorStates,
    onClick: ()->Unit = {}
){
    val stopButtonBackgroundColor: Color
    val stopButtonContentColor: Color

    if(state in listOf(
            ActuatorStates.Closing,
            ActuatorStates.Opening,
            ActuatorStates.MeasuringBP
        )){
        stopButtonBackgroundColor = Color.Red
        stopButtonContentColor = MaterialTheme.colorScheme.onPrimary
    }else{
        stopButtonBackgroundColor = Color(0xFF411D1D)
        stopButtonContentColor = MaterialTheme.colorScheme.onPrimaryContainer
    }

    Button(
        shape = CircleShape,
        contentPadding = PaddingValues(6.dp),
        colors = ButtonColors(
            containerColor = stopButtonBackgroundColor,
            disabledContainerColor = stopButtonBackgroundColor,
            contentColor = stopButtonContentColor,
            disabledContentColor = stopButtonContentColor
        ),
        modifier = Modifier
            .padding(bottom = 20.dp)
            .size(120.dp),
        onClick = { onClick() }
    ) {
        Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = "STOP",
                style = TextStyle(
                    fontWeight = FontWeight.ExtraBold,
                    fontSize = 40.sp
                )
            )
        }
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
            val dataStoreManager = DataStoreManager(LocalContext.current)
            val vm = MainViewModel(dataStoreManager)
            val navController = rememberNavController()
            ActuationView(vm, navController)
        }
    }
}