package com.tfm.druidapp.views.customElements

import android.content.res.Configuration
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.tfm.druidapp.ui.theme.DruidAppTheme
import kotlin.math.cos
import kotlin.math.sin

@Composable
fun GlasgowGauge(score: Int, modifier: Modifier = Modifier){
    val coercedScore = (score-3).coerceIn(0, 12)

    val density = LocalDensity.current
    val strokeWidthDp = 15.dp
    val strokeWidthPx = with(density) { strokeWidthDp.toPx() }

    /*
    3-8: Grave
    9-12: Moderado
    13-15: Leve
     */
    val maxScore = 15
    val minScore = 3
    val angStep = 180f/(maxScore-minScore)
    val angSevere = angStep*(8-3)
    val angModerate = angStep*(12-9+1)
    val angMild = angStep*(15-13)

    val baseModifier = Modifier
        .background(MaterialTheme.colorScheme.primary) //TODO quitar
        //.height(180.dp)


    Box(modifier = modifier.then(baseModifier)
    ) {
        Canvas(
            modifier = Modifier
                .fillMaxSize()

        ) {
            val width = size.width
            val height = size.height
            val restrictedSize = minOf(width-strokeWidthPx,height*2-strokeWidthPx)

            drawArc(
                color = Color.Green,
                size = Size(restrictedSize, restrictedSize),
                topLeft = Offset(strokeWidthPx/2, strokeWidthPx/2),
                startAngle = 0f,
                sweepAngle = -180f,
                useCenter = false,
                style = Stroke(strokeWidthPx)
            )
            drawArc(
                color = Color.Red,
                size = Size(restrictedSize, restrictedSize),//Size(width-strokeWidthPx, width-strokeWidthPx),
                topLeft = Offset(strokeWidthPx/2, strokeWidthPx/2),
                startAngle = -180f,
                sweepAngle = angSevere,
                useCenter = false,
                style = Stroke(strokeWidthPx)
            )
            drawArc(
                color = Color.Yellow,
                size = Size(restrictedSize, restrictedSize),
                topLeft = Offset(strokeWidthPx/2, strokeWidthPx/2),
                startAngle = -180+angSevere,
                sweepAngle = angModerate,
                useCenter = false,
                style = Stroke(strokeWidthPx)
            )

            val arrowSize = 20f
            val start = Offset(width/2, width/2)
            val angleRadians = Math.toRadians((angStep*coercedScore).toDouble()).toFloat()
            val length = width/2-strokeWidthPx-arrowSize
            val end = Offset(
                start.x - (length * cos(angleRadians.toDouble()).toFloat()),
                start.y - (length * sin(angleRadians.toDouble()).toFloat())
            )
            drawLine(
                color = Color.White,                // Color de la línea
                start = start,                     // Punto de inicio
                end = end,                         // Punto final calculado
                strokeWidth = 5f,                  // Estilo de los extremos de la línea
            )
            drawCircle(
                color = Color.White,
                center = start,
                radius = 7f
            )


            val arrowPath = Path().apply {
                // Punta de la flecha (final de la línea)
                moveTo(end.x - arrowSize * cos(angleRadians),
                    end.y - arrowSize * sin(angleRadians)
                )

                // Flecha izquierda
                lineTo(
                    end.x + arrowSize * cos(angleRadians - Math.PI / 6).toFloat(),
                    end.y + arrowSize * sin(angleRadians - Math.PI / 6).toFloat()
                )

                // Flecha derecha
                lineTo(
                    end.x + arrowSize * cos(angleRadians + Math.PI / 6).toFloat(),
                    end.y + arrowSize * sin(angleRadians + Math.PI / 6).toFloat()
                )

                // Regresar al punto de la punta
                close()
            }

            // Dibuja el triángulo relleno
            drawPath(
                path = arrowPath,
                color = Color.White
            )


        }


    }
}

@Preview(showBackground = true, uiMode = Configuration.UI_MODE_NIGHT_YES)
@Composable
fun GlasgowGaugePreview(){
    DruidAppTheme{
        val score = 7
        Column(modifier = Modifier
            .fillMaxHeight(1f)
            .background(MaterialTheme.colorScheme.background)
        ) {
            GlasgowGauge(
                score,
                modifier = Modifier
                    .size(width = 450.dp, height = 280.dp)
            )

        }
    }


}