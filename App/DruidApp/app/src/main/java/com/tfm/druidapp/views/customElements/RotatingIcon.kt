package com.tfm.druidapp.views.customElements

import androidx.annotation.DrawableRes
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.res.painterResource


@Composable
fun RotatingIcon(@DrawableRes icon: Int, onClick: ()->Unit) {

    // Estado para controlar si el ícono ha sido presionado
    var isPressed by remember { mutableStateOf(false) }

    // Animación para la rotación sobre el eje Y (de 0 a 180 grados)
    val rotation by animateFloatAsState(
        targetValue = if (isPressed) 180f else 0f, // Gira 180 grados cuando es presionado
        animationSpec = tween(durationMillis = 500), label = "Girito" // Duración de la animación
    )

    // Icono con rotación
    Icon(
        painter = painterResource(id = icon),
        contentDescription = "Info",
        tint = MaterialTheme.colorScheme.primary,
        modifier = Modifier
            .graphicsLayer(
                rotationY = rotation // Rota sobre el eje Y
            )
            .clickable(
                interactionSource = remember { MutableInteractionSource() },
                indication = null // Desactiva el efecto ripple
            ) {
                // Cambia el estado al hacer clic
                isPressed = !isPressed
                onClick()
            }
    )
}