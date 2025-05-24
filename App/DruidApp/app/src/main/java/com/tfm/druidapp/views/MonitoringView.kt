package com.tfm.druidapp.views

import android.content.res.Configuration
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.wrapContentHeight
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.VerticalDivider
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.navigation.NavHostController
import androidx.navigation.compose.rememberNavController
import com.tfm.druidapp.data.ActuatorStates
import com.tfm.druidapp.data.DataStoreManager
import com.tfm.druidapp.data.MainViewModel
import com.tfm.druidapp.data.MedicUtilities
import com.tfm.druidapp.data.MedicUtilities.setColor
import com.tfm.druidapp.data.Screen
import com.tfm.druidapp.ui.theme.DruidAppTheme
import com.tfm.druidapp.views.customElements.GlasgowGauge
import com.tfm.druidapp.views.customElements.PPG
import com.tfm.druidapp.views.customElements.ThermometerIcon

@Composable
fun MonitoringView(viewModel: MainViewModel, navController: NavHostController){
    val temperature by viewModel.temperature.collectAsState()
    val pressureData by viewModel.pressureData
    val enabled = (viewModel.actuatorState.value == ActuatorStates.Closed)
    val normalRanges by viewModel.normalMedicRanges
    val bpEnabled = (viewModel.actuatorState.value == ActuatorStates.Closed)
    val PTEnabled by viewModel.monitoringPT

    Column(
        modifier = Modifier
            .padding(16.dp)
            .fillMaxSize(),
        verticalArrangement = Arrangement.spacedBy(6.dp)
        ) {
        PPG(
            viewModel= viewModel,
            modifier = Modifier.clickable {
                navController.navigate(Screen.PPG.route)
            }
        )
        Row( //Presion arterial
            modifier = Modifier
                .clip(RoundedCornerShape(10.dp))
                .background(MaterialTheme.colorScheme.primary)
                .fillMaxWidth()
                .wrapContentHeight()
                .padding(vertical = 16.dp, horizontal = 16.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceAround
        ) {

            PressureItem(
                title = "SYS",
                value = if (bpEnabled) pressureData.sys else null,
                color = setColor(
                    value = pressureData.sys,
                    range = normalRanges.sys,
                    enabled = bpEnabled,
                    colors = MedicUtilities.MedicDataColors(
                        onCorrect = MaterialTheme.colorScheme.onPrimary,
                        onIncorrect = Color.Red,
                        onIdle = MaterialTheme.colorScheme.onPrimaryContainer
                    )
                )
            )


            VerticalDivider(
                modifier = Modifier.height(100.dp),
                color = MaterialTheme.colorScheme.onPrimaryContainer
            )


            PressureItem(
                title = "DIA",
                value = if (bpEnabled) pressureData.dia else null,
                color = setColor(
                    value = pressureData.dia,
                    range = normalRanges.dia,
                    enabled = bpEnabled,
                    colors = MedicUtilities.MedicDataColors(
                        onCorrect = MaterialTheme.colorScheme.onPrimary,
                        onIncorrect = Color.Red,
                        onIdle = MaterialTheme.colorScheme.onPrimaryContainer
                    )
                )
            )
        }

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .height(126.dp),
            horizontalArrangement = Arrangement.spacedBy(6.dp)
        ) {

            Box(modifier = Modifier
                .width(126.dp)
                .fillMaxHeight()
                .clip(RoundedCornerShape(10.dp))
                .background(MaterialTheme.colorScheme.primary)
            ){
                TemperatureDisplay(
                    temperature = if (PTEnabled) temperature else null,
                    color = setColor(
                        value = temperature,
                        range = normalRanges.temperature,
                        enabled = PTEnabled,
                        colors = MedicUtilities.MedicDataColors(
                            onCorrect = MaterialTheme.colorScheme.onPrimary,
                            onIncorrect = Color.Red,
                            onIdle = MaterialTheme.colorScheme.onPrimaryContainer
                        )
                    )
                )
            }
            Box(modifier = Modifier
                .fillMaxSize()
                .clip(RoundedCornerShape(10.dp))
                .background(MaterialTheme.colorScheme.primary)
                .clickable { navController.navigate(Screen.Glasgow.route) }
            ){
                GlasgowDisplay(score = viewModel.glasgowScore.value)
            }
        }
    }
}

@Composable
fun PressureItem(title: String, value: Int?, color: Color){ //TODO comprobar que sea int
    Row(
        modifier = Modifier.width(130.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically

    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleLarge
            )
            Text(
                text = "mmHg",
                style = MaterialTheme.typography.titleSmall
            )
        }
        Text(
            text = value?.takeIf { it != -1 }?.toString() ?: "--",
            style = MaterialTheme.typography.labelLarge,
            textAlign = TextAlign.End,
            modifier = Modifier.fillMaxWidth(),
            color = color
        )
    }
}

@Composable
fun TemperatureDisplay(temperature: Float?, color: Color){

    Box(modifier = Modifier.fillMaxSize()){
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .align(Alignment.Center),
            verticalAlignment = Alignment.Top,
            horizontalArrangement = Arrangement.Center
        ) {
            Text(
                text = temperature?.takeIf { it != -1f }?.let { String.format("%.1f", it) } ?: "--",
                style = MaterialTheme.typography.labelLarge,
                textAlign = TextAlign.Center,
                color = color
            )
            Text(
                text = "º",
                style = MaterialTheme.typography.titleLarge,
                textAlign = TextAlign.Center,
                color = color
            )
        }
        Box(modifier = Modifier.padding(vertical = 6.dp, horizontal = 4.dp)){
            ThermometerIcon(temperature ?: 0f)
        }

    }
}

@Composable
fun GlasgowDisplay(score: Int){
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(vertical = 4.dp, horizontal = 8.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.SpaceBetween
        ) {
        Text(
            text = "Escala de Glasgow",
            style = MaterialTheme.typography.titleMedium
        )
        Row(
            verticalAlignment = Alignment.CenterVertically
        ) {
            GlasgowGauge(
                score,
                modifier = Modifier
                    .width(100.dp)
                    .padding(top = 22.dp)
            )
            Column(
                modifier = Modifier
                    .fillMaxSize(),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                Text(
                    text = if (score<3 || score>15){
                                ""
                           }else{
                                score.toString()
                           },
                    style = MaterialTheme.typography.labelLarge
                    )
                Text(
                    text = when (score) {
                        in 3..8 -> "Grave"
                        in 9..12 -> "Moderado"
                        in 13..15 -> "Leve"
                        else -> ""
                    },
                    style = MaterialTheme.typography.bodyMedium,
                    )
            }
        }

    }
}



@Preview(showBackground = true, uiMode = Configuration.UI_MODE_NIGHT_YES)
@Composable
fun MonitoringViewPreview(){
    DruidAppTheme{
        Surface(
            modifier = Modifier.fillMaxSize(),
            color = MaterialTheme.colorScheme.background
        ) {
            val dataStoreManager = DataStoreManager(LocalContext.current)
            val vm = MainViewModel(dataStoreManager)
            val navController = rememberNavController()
            MonitoringView(vm, navController)
        }
    }
}