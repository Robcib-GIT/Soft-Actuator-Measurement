package com.tfm.druidapp.views.customElements

import android.content.res.Configuration
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.wrapContentHeight
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.tfm.druidapp.R
import com.tfm.druidapp.data.ActuatorStates
import com.tfm.druidapp.data.MainViewModel
import com.tfm.druidapp.data.MedicUtilities
import com.tfm.druidapp.ui.theme.DruidAppTheme


@Composable
fun PPG(viewModel: MainViewModel, modifier: Modifier = Modifier) {
    val enabled by viewModel.monitoringPT
    val pulseAmplitudeList by viewModel.pulseAmplitudeList.collectAsState()
    val cardiacData by viewModel.cardiacData.collectAsState()
    val measuresInScreen = viewModel.maxPulseRegisters
    // Modifier base con características predeterminadas
    val baseModifier = Modifier
        .clip(RoundedCornerShape(10.dp))
        .background(MaterialTheme.colorScheme.primary)
        .height(180.dp)


    // Combina el Modifier base con el del usuario
    val combinedModifier = baseModifier.then(modifier)  //igual al reves pero cuadra
    Box(
        modifier = combinedModifier // El padding será gestionado externamente
    ) {
        Box(modifier = Modifier.padding(vertical = 16.dp)) {

            Canvas(modifier = Modifier.fillMaxSize()) {
                val width = size.width
                val height = size.height

                // Escalar las amplitudes para que se ajusten al tamaño del Canvas
                val scaleX = width / (measuresInScreen - 1).coerceAtLeast(1)
                val scaleY = height

                // Crear un Path para dibujar la onda
                val path = Path().apply {
                    // Mover al primer punto de la lista
                    moveTo(width, height - pulseAmplitudeList[0] * scaleY)

                    // Dibujar la onda conectando los puntos
                    for (i in 1 until pulseAmplitudeList.size) {
                        val x = width - (i * scaleX)
                        val y = (height - pulseAmplitudeList[i] * scaleY).coerceIn(0f, height)
                        lineTo(x, y)
                    }
                }

                drawLine(
                    color = Color(0xB0504F4F),
                    start = Offset(0f, height / 2),
                    end = Offset(width, height / 2),
                    strokeWidth = 2f
                )

                // Dibujar el path en el Canvas
                if (enabled){ //TODO comprobar que funcione bien
                    drawPath(path, color = Color.Green, style = Stroke(width = 4f))
                }

            }
            Row (
                modifier = Modifier
                    .fillMaxWidth()
                    .wrapContentHeight()
                    .padding(end = 32.dp),
                horizontalArrangement = Arrangement.End,
                verticalAlignment = Alignment.CenterVertically
            ){
                val textColor = MedicUtilities.setColor(
                    value = cardiacData.ppm,
                    range = viewModel.normalMedicRanges.value.ppm,
                    enabled = enabled,
                    colors = MedicUtilities.MedicDataColors(
                        onCorrect = MaterialTheme.colorScheme.onPrimary,
                        onIncorrect = Color.Red,
                        onIdle = MaterialTheme.colorScheme.onPrimaryContainer
                    )
                )
                Text(
                    text = cardiacData.ppm.takeIf { it != -1 }?.toString() ?: "--",
                    color = textColor,
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "PPM",
                    color = textColor,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Medium,
                    modifier=Modifier.align(Alignment.Bottom)
                )

                Icon(
                    painter = painterResource(id = R.drawable.icono_corazon),
                    contentDescription = "Pulscaciones",
                    tint = Color.Red
                )
            }
        }
    }
}

@Preview(showBackground = true, uiMode = Configuration.UI_MODE_NIGHT_YES)
@Composable
fun PPGPreview(){
    DruidAppTheme{
        val amplitudeValues = mutableListOf(0.5f, 10f, 5f, -0.5f, -0.5f, -1f, -0.5f, 0f, 0.2f, -0.5f, -1f, -0.5f, 0f, 0.2f)
        val viewModel: MainViewModel = viewModel()
        Column(modifier = Modifier
            .fillMaxHeight(1f)
            .background(MaterialTheme.colorScheme.background)
        ) {
            PPG(viewModel)

        }
    }


}