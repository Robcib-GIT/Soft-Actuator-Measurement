package com.tfm.druidapp.views.customElements

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp

@Composable
fun ThermometerIcon(temperature: Float) {
    val thermometerWidth = 4.dp // Ancho del termómetro
    val thermometerHeight = 24.dp // Altura total del termómetro
    val circleRadius = 10.dp // Altura total del termómetro
    val canvasWidth = circleRadius+2.dp

    // Convierte los valores dp a píxeles
    val widthPx = with(LocalDensity.current) { thermometerWidth.toPx() }
    val heightPx = with(LocalDensity.current) { thermometerHeight.toPx() }
    val circleRadiusPx = with(LocalDensity.current) { circleRadius.toPx() }
    val canvasWidthPx = with(LocalDensity.current) { canvasWidth.toPx() }



    val level = when {
        temperature > 40 -> 1f
        temperature < 32 -> 0.4f
        else -> {
            val range = (temperature - 32) / 8
            0.4f + range * (1f - 0.4f)
        }
    }

    var thermometerColor = when {
        temperature > 37.7f -> Color.Red
        temperature < 35 -> Color.Blue
        else -> Color.White
    }


    Canvas(
        modifier = Modifier
            .padding(2.dp)
            .size(canvasWidth, thermometerHeight)

    ) {
        val levelHeight = (level.coerceIn(0f, 1f)) * heightPx // Asegura que el nivel esté entre 0 y la altura máxima
        drawRoundRect(
            color = thermometerColor, // Color del nivel del termómetro
            size = Size(widthPx, levelHeight),
            topLeft = Offset((canvasWidthPx-widthPx)/2, heightPx - levelHeight), // Ajusta la posición para que suba de abajo hacia arriba
            cornerRadius = CornerRadius(8f)
        )
        drawRoundRect(
            color = Color.White,
            size = Size(widthPx, heightPx),
            topLeft = Offset((canvasWidthPx-widthPx)/2, 0f),
            cornerRadius = CornerRadius(8f),
            style = Stroke(width = 3f) // Borde del termómetro
        )


        drawCircle(
            color = thermometerColor, // Color de la base del termómetro
            radius = circleRadiusPx/2, // Radio del círculo
            center = Offset((canvasWidthPx)/2, heightPx-circleRadiusPx/2) // Posición en la parte inferior
        )


        drawArc(
            color = Color.White,           // Color del arco
            size = Size(circleRadiusPx, circleRadiusPx), // Tamaño igual al diámetro del círculo
            startAngle = -73f,             // Comienza en el eje X positivo
            sweepAngle = 360f-35,            // Dibuja un cuarto de círculo (90 grados)
            useCenter = false,           // No dibuja una línea al centro del círculo
            style = Stroke(width = 3f),  // Ancho del borde del arco igual al del círculo
            topLeft = Offset((canvasWidthPx)/2 - circleRadiusPx / 2, heightPx - circleRadiusPx) // Posición similar al círculo
        )






    }
}

@Preview
@Composable
fun ThermometerIconPreview(){
    ThermometerIcon(0.5f)
}