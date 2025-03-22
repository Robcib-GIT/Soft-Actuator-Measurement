package com.tfm.druidapp.views.customElements

import android.content.res.Configuration
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.expandVertically
import androidx.compose.animation.shrinkVertically
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Done
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.tfm.druidapp.R
import com.tfm.druidapp.data.ActuationState
import com.tfm.druidapp.ui.theme.DruidAppTheme

enum class MonitoringState {
    Enabled,
    Enabling,
    Disabled,
    Disabling,
    EnPaused,
    DisPaused
}

@Composable
fun ProcessProgressIndicator(
    state: MonitoringState,
    text: String,
    statesList: List<ActuationState>, //TODO: cambiar con la actualizacion
    onRun: () -> Unit,
    onPause: () -> Unit,
    onStop: () -> Unit,
    onEnd: () -> Unit
) {
    val cornerRadius = 10.dp
    val expanded = state != MonitoringState.Enabled && state != MonitoringState.Disabled
    val shape = if (expanded) {
        RoundedCornerShape(
            topStart = cornerRadius,
            topEnd = cornerRadius,
            bottomStart = 0.dp,
            bottomEnd = 0.dp
        )
    } else {
        RoundedCornerShape(cornerRadius)
    }
    val completedStates = statesList.count { it.progress >= 1f }
    val numberOfStates = statesList.size

    LaunchedEffect(completedStates, numberOfStates) {
        if (completedStates == numberOfStates && numberOfStates > 0) {
            onEnd()
        }
    }

    Column(
        modifier = Modifier
            .clip(shape)
            .background(Color.DarkGray)
            .padding(horizontal = 16.dp)
            .fillMaxWidth()
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .height(50.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = text,
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onPrimary
            )

            if (!expanded) {
                processControlButton(painterId = if(state == MonitoringState.Disabled){
                    R.drawable.baseline_play_arrow_24
                }else{
                    R.drawable.baseline_stop_24
                }) {
                    //TODO
                    onRun()
                }
            } else {
                Text(
                    text = "${completedStates}/${numberOfStates}",
                    color = MaterialTheme.colorScheme.onPrimary
                )
            }
        }
    }
    AnimatedVisibility(
        visible = expanded,
        enter = expandVertically(
            expandFrom = Alignment.Top
        ),
        exit = shrinkVertically(
            shrinkTowards = Alignment.Top // Se contrae hacia arriba
        )
    ) {
        Column(
            modifier = Modifier
                .clip(
                    RoundedCornerShape(
                        topStart = 0.dp,
                        topEnd = 0.dp,
                        bottomStart = cornerRadius,
                        bottomEnd = cornerRadius
                    )
                )
                .background(Color.DarkGray)
                .padding(start = 16.dp, end = 16.dp, bottom = 6.dp)
                .fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            HorizontalDivider(
                thickness = 1.dp,
                color = MaterialTheme.colorScheme.onPrimaryContainer
            )

            statesList.forEach { state->
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(6.dp)
                ) {
                    Text(
                        text = state.name,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onPrimary,
                        softWrap = true,
                        modifier = Modifier.weight(1f)
                    )
                    LinearProgressIndicator(
                        progress = { state.progress },
                        color = Color.Green,
                        trackColor = MaterialTheme.colorScheme.onPrimaryContainer,
                        gapSize = 0.dp,
                        drawStopIndicator = {},
                        modifier = Modifier.weight(2f)
                    )
                    Icon(
                        imageVector = Icons.Default.Done,
                        contentDescription = null,
                        tint = if (state.progress >= 1f) {
                            Color.Green
                        } else {
                            Color.Transparent
                        }
                    )

                }
            }
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.Center,
                modifier = Modifier.fillMaxWidth()
            ) {
                processControlButton(
                    painterId = if (state == MonitoringState.Enabling || state == MonitoringState.Disabling) {
                        R.drawable.baseline_pause_24
                    } else {
                        R.drawable.baseline_play_arrow_24
                    }
                ) {
                    //TODO
                    onPause()
                }

                Spacer(modifier = Modifier.width(6.dp))
                processControlButton(R.drawable.baseline_stop_24) {
                    //TODO
                    onStop()
                }
            }

        }
    }
}

@Composable
fun processControlButton(painterId: Int, onClick: () -> Unit) {
    IconButton(
        modifier = Modifier.size(26.dp),
        onClick = {
            onClick()
        }
    ) {
        Icon(
            painter = painterResource(id = painterId),
            contentDescription = null,
            tint = Color.Black,
            modifier = Modifier
                .background(
                    color = MaterialTheme.colorScheme.onPrimary,
                    shape = CircleShape
                )
        )
    }
}

@Preview(showBackground = true, uiMode = Configuration.UI_MODE_NIGHT_YES)
@Composable
fun ProcessProgressIndicatorsPreview() {
    DruidAppTheme {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .background(MaterialTheme.colorScheme.background)
                .padding(6.dp)
        ) {
            Spacer(modifier = Modifier.height(16.dp))
            val states = listOf(
                ActuationState("Home"),
                ActuationState("Close actuator", 0.5f),
                ActuationState("Inflate cuff", 1f),
                ActuationState("Deflate cuff"),
                ActuationState("Open actuator"),
                ActuationState("IDLE") //TODO: igual quitar
            )
            ProcessProgressIndicator(
                state = MonitoringState.Enabling,
                text = "Iniciar mediciones",
                statesList = states,
                onRun = {},
                onPause = {},
                onStop = {},
                onEnd = {}
            )
        }
    }
}