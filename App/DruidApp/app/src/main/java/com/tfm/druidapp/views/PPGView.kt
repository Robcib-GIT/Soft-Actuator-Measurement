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
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.tfm.druidapp.R
import com.tfm.druidapp.data.MainViewModel
import com.tfm.druidapp.views.customElements.bpmInfo
import com.tfm.druidapp.ui.theme.DruidAppTheme
import com.tfm.druidapp.views.customElements.PPG
import com.tfm.druidapp.views.customElements.RotatingIcon

private const val col1Width = 150
private const val col2Width = 100

@Composable
fun PPGView(viewModel: MainViewModel){
    val cardiacData by viewModel.cardiacData.collectAsState()

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

                    DataRow(
                        title = "PPM", value = cardiacData.ppm.toFloat(), valueUnits = ""
                    ) {
                        viewModel.setComposableContent { bpmInfo() }
                        viewModel.updateBottomSheetVisibility(true)
                    }
                    DataRow(
                        title = "IBI", value = cardiacData.ibi, valueUnits = " ms"
                    ) {
                        //TODO
                    }
                    DataRow(
                        title = "Frecuencia", value = cardiacData.frequency, valueUnits = " Hz"
                    ) {
                        //TODO
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
                        title = "SDNN", value = cardiacData.sdnn, valueUnits = " ms"
                    ) {
                        //TODO
                    }
                    DataRow(
                        title = "RMSDD", value = cardiacData.rmsdd, valueUnits = " ms"
                    ) {
                        //TODO
                    }
                }

                HorizontalDivider(
                    color = MaterialTheme.colorScheme.onPrimaryContainer
                )

                Text(
                    text = "Análisis morfológico de la onda",
                    style = MaterialTheme.typography.titleMedium
                )

                Column( //Forma onda PPG
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(start = 50.dp)
                ) {

                    DataRow(title = "Amplitud", value = 0f, valueUnits = "") {
                        //TODO
                    }
                    DataRow(title = "Rise Time", value = 0f, valueUnits = " ms") {
                        //TODO
                    }

                }
            }
        }
    }
}

@Composable
fun DataRow(title: String, value: Float, valueUnits: String, onInfoClick: ()->Unit){
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
            val vm: MainViewModel = viewModel()
            PPGView(vm)
        }
    }
}


