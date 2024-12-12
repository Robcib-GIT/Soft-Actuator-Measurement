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
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.wrapContentHeight
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Divider
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
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import androidx.navigation.compose.rememberNavController
import com.tfm.druidapp.data.MainViewModel
import com.tfm.druidapp.data.Screen
import com.tfm.druidapp.ui.theme.DruidAppTheme
import com.tfm.druidapp.views.customElements.GlasgowGauge
import com.tfm.druidapp.views.customElements.PPG
import com.tfm.druidapp.views.customElements.ThermometerIcon

@Composable
fun MonitoringView(viewModel: MainViewModel, navController: NavHostController){
    val temperature by viewModel.temperature.collectAsState()
    val pressureData by viewModel.pressureData

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

            PressureItem(title = "SYS", value = pressureData.sys)

            VerticalDivider(
                modifier = Modifier.height(100.dp),
                color = MaterialTheme.colorScheme.onPrimaryContainer
            )


            PressureItem(title = "DIA", value = pressureData.dia)
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
                TemperatureDisplay(temperature = temperature)
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

        //TODO borrar prueba
        val sensor1Data by viewModel.sensor1Data.collectAsState()
        val sensor2Data by viewModel.sensor2Data.collectAsState()
        val sensor3Data by viewModel.sensor3Data.collectAsState()
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceAround
        ) {
            Text(text = "S1: " + (sensor1Data?.let { String.format("%.2f", it) } ?: "--"))
            Text(text = "S2: " + (sensor2Data?.let { String.format("%.2f", it) } ?: "--"))
            Text(text = "S3: " + (sensor3Data?.let { String.format("%.2f", it) } ?: "--"))
        }

    }
}

@Composable
fun PressureItem(title: String, value: Int?){ //TODO comprobar que sea int
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
            text = value?.toString() ?: "--",
            style = MaterialTheme.typography.labelLarge,
            textAlign = TextAlign.End,
            modifier = Modifier.fillMaxWidth()
        ) //TODO relacionar con viewModel
    }
}

@Composable
fun TemperatureDisplay(temperature: Float?){

    Box(modifier = Modifier.fillMaxSize()){
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .align(Alignment.Center),
            verticalAlignment = Alignment.Top,
            horizontalArrangement = Arrangement.Center
        ) {
            Text(
                text = temperature?.let{String.format("%.1f", temperature)} ?: "--",
                style = MaterialTheme.typography.labelLarge,
                textAlign = TextAlign.Center
            )
            Text(
                text = "º",
                style = MaterialTheme.typography.titleLarge,
                textAlign = TextAlign.Center

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
            val vm: MainViewModel = viewModel()
            val navController = rememberNavController()
            MonitoringView(vm, navController)
        }
    }
}