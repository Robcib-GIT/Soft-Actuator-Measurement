package com.tfm.druidapp.views.customElements

import android.content.res.Configuration
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.tween
import androidx.compose.animation.expandVertically
import androidx.compose.animation.shrinkVertically
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.tfm.druidapp.R
import com.tfm.druidapp.data.ActuationState
import com.tfm.druidapp.ui.theme.DruidAppTheme

/**
 * El ActionProcessButton es una derivación del [Button] de Material3 que sirve tanto para ejecutar
 * código al pulsarse como para representar el progreso de una acción mediante un [LinearProgressIndicator].
 *
 * @param process Nombre del proceso.
 * @param painterId [painterResource] para el icono.
 * @param enabled Controla el estado de activación del botón. Si está activado el botón pierde
 * completamente su funcionalidad y se desactiva. Útil para seguridad.
 * @param focus Sirve para controlar la visibilidad del boton aunque [enabled] sea true. Sirve para
 * casos en los que en teoria el botón no debería de tener que pulsarse a menos que haya habido un
 * fallo y que no suponga un riesgo ejecutar [onClick] en ese momento.
 * @param onClick Función que será llamada cuando se pulse el botón.
 * */
@Composable
fun ActionProcessButton(
    process: ActuationState,
    painterId: Int,
    enabled: Boolean = true,
    focus: Boolean = true,
    onClick: () -> Unit = {}
){
    val backgroundColor: Color
    val textColor: Color
    val progressIndicatorColor: Color

    if (enabled && focus) {
        backgroundColor = Color.DarkGray
        textColor = MaterialTheme.colorScheme.onPrimary
        progressIndicatorColor = Color.Green
    } else {
        backgroundColor = MaterialTheme.colorScheme.onPrimaryContainer
        textColor = MaterialTheme.colorScheme.onPrimaryContainer
        progressIndicatorColor = Color(0xFF305A16)
    }

    Button(
        onClick = onClick,
        enabled = enabled,
        shape = RoundedCornerShape(
            topStart = 10.dp,
            topEnd = 10.dp,
            bottomStart = 10.dp,
            bottomEnd = 10.dp
        ),
        colors = ButtonDefaults.buttonColors(
            containerColor = backgroundColor,
            disabledContainerColor = MaterialTheme.colorScheme.onPrimaryContainer
        ),
        contentPadding = PaddingValues(
            vertical = 6.dp,
            horizontal = 16.dp
        )
    ){
        Row(
            modifier = Modifier
                .fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.Absolute.SpaceBetween

        ) {
            Column(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                Text(
                    text = process.name,
                    style = MaterialTheme.typography.titleMedium,
                    color = textColor
                )
                LinearProgressIndicator(
                    progress = { process.progress },
                    color = progressIndicatorColor,
                    trackColor = MaterialTheme.colorScheme.onPrimaryContainer,
                    gapSize = 0.dp,
                    drawStopIndicator = {},
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(end = 10.dp)
                )
            }

            Icon(
                painter = painterResource(id = painterId),
                contentDescription = null,
                tint = textColor,
                modifier = Modifier
                    .size(50.dp)
            )
        }
    }
}

/**
 * El ActionProcessButton es una derivación del [Button] de Material3 que sirve tanto para ejecutar
 * código al pulsarse como para representar el progreso de una acción mediante un [LinearProgressIndicator].
 *
 * @param title Nombre del proceso.
 * @param processes Lista de subprocesos.
 * @param painterId [painterResource] para el icono.
 * @param expanded Expande la vista del progreso de los subprocesos
 * @param enabled Controla el estado de activación del botón. Si está activado el botón pierde
 * completamente su funcionalidad y se desactiva. Útil para seguridad.
 * @param focus Sirve para controlar la visibilidad del boton aunque [enabled] sea true. Sirve para
 * casos en los que en teoria el botón no debería de tener que pulsarse a menos que haya habido un
 * fallo y que no suponga un riesgo ejecutar [onClick] en ese momento.
 * @param onClick Función que será llamada cuando se pulse el botón.
 * */
@Composable
fun ActionProcessButton(
    title: String,
    processes: List<ActuationState>,
    painterId: Int,
    expanded: Boolean = false,
    enabled: Boolean = true,
    focus: Boolean = true,
    onClick: () -> Unit = {}
){

    val backgroundColor: Color
    val textColor: Color
    val progressIndicatorColor: Color

    if (enabled && focus) {
        backgroundColor = Color.DarkGray
        textColor = MaterialTheme.colorScheme.onPrimary
        progressIndicatorColor = Color.Green
    } else {
        backgroundColor = MaterialTheme.colorScheme.onPrimaryContainer
        textColor = MaterialTheme.colorScheme.onPrimaryContainer
        progressIndicatorColor = Color(0xFF305A16)
    }

    Button(
        onClick = onClick,
        enabled = enabled,
        shape = RoundedCornerShape(
            topStart = 10.dp,
            topEnd = 10.dp,
            bottomStart = 10.dp,
            bottomEnd = 10.dp
        ),
        colors = ButtonDefaults.buttonColors(
            containerColor = backgroundColor,
            disabledContainerColor = MaterialTheme.colorScheme.onPrimaryContainer
        ),
        contentPadding = PaddingValues(
            vertical = 6.dp,
            horizontal = 16.dp
        )
    ) {
        Column(
            modifier = Modifier
            //verticalArrangement = Arrangement.spacedBy(6.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleMedium,
                    color = textColor
                )

                Icon(
                    painter = painterResource(id = painterId),
                    contentDescription = null,
                    tint = textColor,
                    modifier = Modifier
                        .size(50.dp)
                )
            }

            AnimatedVisibility(
                visible = expanded,
                enter = expandVertically(
                    animationSpec = tween(durationMillis = 600) // más lento
                ),
                exit = shrinkVertically(
                    animationSpec = tween(durationMillis = 600)
                )
            ){
                HorizontalDivider(
                    thickness = 1.dp,
                    color = MaterialTheme.colorScheme.onPrimaryContainer
                )
                Column(
                    verticalArrangement = Arrangement.spacedBy(6.dp),
                    modifier = Modifier.padding(top = 6.dp)
                ) {
                    processes.forEach{process->
                        Row(
                            modifier = Modifier
                                .fillMaxWidth(),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(
                                text = process.name,
                                style = MaterialTheme.typography.titleSmall,
                                color = textColor
                            )
                            LinearProgressIndicator(
                                progress = { process.progress },
                                color = progressIndicatorColor,
                                trackColor = MaterialTheme.colorScheme.onPrimaryContainer,
                                gapSize = 0.dp,
                                drawStopIndicator = {}
                            )
                        }
                    }
                }
            }
        }
    }
}



//TODO: borrar
enum class MonitoringState {
    Enabled,
    Enabling,
    Disabled,
    Disabling,
    EnPaused,
    DisPaused
}

@Preview(showBackground = true, uiMode = Configuration.UI_MODE_NIGHT_YES)
@Composable
fun actionProcessButtonPreview() {
    DruidAppTheme {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .background(MaterialTheme.colorScheme.background)
                .padding(6.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp)
        ) {
            //Spacer(modifier = Modifier.height(16.dp))
            ActionProcessButton(
                process = ActuationState(
                    name = "Cerrar actuador",
                    progress = 1f
                ),
                painterId = R.drawable.rounded_lock_24,
                enabled = true,
                focus = false,
                onClick = {}
            )
            ActionProcessButton(
                process = ActuationState(
                    name = "Abrir actuador",
                    progress = 1f
                ),
                painterId = R.drawable.rounded_lock_open_right_24,
                enabled = false,
                onClick = {}
            )
            ActionProcessButton(
                process = ActuationState(
                    name = "Matar actuador",
                    progress = 0.8f
                ),
                painterId = R.drawable.rounded_lock_open_right_24,
                onClick = {}
            )

            val procesos = listOf(
                ActuationState("Desinflado", 1f),
                ActuationState("Inflado", 1f),
                ActuationState("Procesamiento", 0.68f)
            )
            ActionProcessButton(
                title = "Medir presión arterial",
                processes = procesos,
                painterId = R.drawable.rounded_blood_pressure_24,
                expanded = true,
                enabled = true,
                focus = false,
                onClick = {}
            )
        }
    }
}
