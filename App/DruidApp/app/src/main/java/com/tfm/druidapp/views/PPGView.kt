package com.tfm.druidapp.views

import android.content.res.Configuration
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.material3.HorizontalDivider
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
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.tfm.druidapp.R
import com.tfm.druidapp.data.ActuatorStates
import com.tfm.druidapp.data.DataStoreManager
import com.tfm.druidapp.data.MainViewModel
import com.tfm.druidapp.data.MedicUtilities
import com.tfm.druidapp.data.MsgTypes
import com.tfm.druidapp.views.customElements.BPMInfo
import com.tfm.druidapp.ui.theme.DruidAppTheme
import com.tfm.druidapp.views.customElements.FrequencyInfo
import com.tfm.druidapp.views.customElements.IBIInfo
import com.tfm.druidapp.views.customElements.PPG
import com.tfm.druidapp.views.customElements.RMSSDInfo
import com.tfm.druidapp.views.customElements.RotatingIcon
import com.tfm.druidapp.views.customElements.SDNNInfo

private const val col1Width = 150
private const val col2Width = 100

@Composable
fun PPGView(viewModel: MainViewModel){
    val cardiacData by viewModel.cardiacData.collectAsState()
    val enabled = (viewModel.actuatorState.value == ActuatorStates.Connected)
    val ranges by viewModel.normalMedicRanges

    Column(
        modifier = Modifier
            .padding(16.dp)
            .fillMaxSize(),
        verticalArrangement = Arrangement.spacedBy(6.dp)
    ) {
        PPG(viewModel = viewModel)

        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(top = 5.dp)
        ) {
            /*
            TODO relacionar con viewModel y cambiar color a rojo si está mal
             */
            Column( //Contenedor para todos los datos
                modifier= Modifier.fillMaxWidth(),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Text(
                    text = "Frecuencia cardíaca",
                    style = MaterialTheme.typography.titleMedium
                )
                Column( //frec. card.
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(start = 50.dp)
                ) {
                    val ppmColor = MedicUtilities.setColor(
                        value = cardiacData.ppm,
                        range = ranges.ppm,
                        enabled = enabled,
                        colors = MedicUtilities.MedicDataColors(
                            onCorrect = MaterialTheme.colorScheme.onPrimary,
                            onIncorrect = Color.Red,
                            onIdle = MaterialTheme.colorScheme.onPrimaryContainer
                        )
                    )
                    DataRow(
                        title = "PPM",
                        value = cardiacData.ppm.toFloat(),
                        valueUnits = "",
                        color = ppmColor
                    ) {
                        viewModel.setComposableContent { BPMInfo() }
                        viewModel.updateBottomSheetVisibility(true)
                    }
                    DataRow(
                        title = "IBI",
                        value = cardiacData.ibi,
                        valueUnits = " ms",
                        color = ppmColor
                    ) {
                        viewModel.setComposableContent { IBIInfo() }
                        viewModel.updateBottomSheetVisibility(true)
                    }
                    DataRow(
                        title = "Frecuencia",
                        value = cardiacData.frequency,
                        valueUnits = " Hz",
                        color = ppmColor
                    ) {
                        viewModel.setComposableContent { FrequencyInfo() }
                        viewModel.updateBottomSheetVisibility(true)
                    }

                }

                HorizontalDivider(
                    color = MaterialTheme.colorScheme.onPrimaryContainer
                )

                Text(
                    text = "Variabilidad de la FC",
                    style = MaterialTheme.typography.titleMedium
                )
                Column( //Datos variabilidad frec. card.
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(start = 50.dp)
                ) {

                    DataRow(
                        title = "SDNN",
                        value = cardiacData.sdnn,
                        valueUnits = " ms",
                        color = MedicUtilities.setColor(
                            value = cardiacData.sdnn,
                            range = ranges.sdnn,
                            enabled = enabled,
                            colors = MedicUtilities.MedicDataColors(
                                onCorrect = MaterialTheme.colorScheme.onPrimary,
                                onIncorrect = Color.Red,
                                onIdle = MaterialTheme.colorScheme.onPrimaryContainer
                            )
                        )
                    ) {
                        viewModel.setComposableContent { SDNNInfo() }
                        viewModel.updateBottomSheetVisibility(true)
                    }
                    DataRow(
                        title = "RMSDD",
                        value = cardiacData.rmsdd,
                        valueUnits = " ms",
                        color = MedicUtilities.setColor(
                            value = cardiacData.rmsdd,
                            range = ranges.rmsdd,
                            enabled = enabled,
                            colors = MedicUtilities.MedicDataColors(
                                onCorrect = MaterialTheme.colorScheme.onPrimary,
                                onIncorrect = Color.Red,
                                onIdle = MaterialTheme.colorScheme.onPrimaryContainer
                            )
                        )
                    ) {
                        viewModel.setComposableContent { RMSSDInfo() }
                        viewModel.updateBottomSheetVisibility(true)
                    }
                }
            }
        }
    }
}

@Composable
fun DataRow(title: String, value: Float, valueUnits: String, color: Color, onInfoClick: ()->Unit){
    Row(
        verticalAlignment = Alignment.Bottom
    ) {
        Text(text = title,
            style = MaterialTheme.typography.bodyMedium,
            modifier = Modifier.width(col1Width.dp)
        )
        Text(
            text = if (value == -1f) {
                    "-- $valueUnits"
                } else if (value % 1 == 0f) {
                    String.format("%.0f", value) + valueUnits
                } else {
                    String.format("%.1f", value) + valueUnits
                },
            style = MaterialTheme.typography.bodyMedium,
            color = color,
            modifier = Modifier.width(col2Width.dp)
        )
        RotatingIcon(R.drawable.baseline_info_outline_24){
            onInfoClick()
        }
    }
}

@Preview(showBackground = true, uiMode = Configuration.UI_MODE_NIGHT_YES)
@Composable
fun PPGViewPreview(){
    DruidAppTheme{
        Surface(
            modifier = Modifier.fillMaxSize(),
            color = MaterialTheme.colorScheme.background
        ) {
            val dataStoreManager = DataStoreManager(LocalContext.current)
            val vm = MainViewModel(dataStoreManager)
            vm.updateCardiacData(data = MsgTypes.CardiacMsg(
                ppm = 60,
                ibi = 824.14f,
                frequency = 1f,
                sdnn = 60f,
                rmsdd = 2f
            ))
            vm.updateActuatorState(state = ActuatorStates.Connected)
            PPGView(vm)
        }
    }
}


