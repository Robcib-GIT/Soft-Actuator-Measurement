package com.tfm.druidapp.data

import androidx.annotation.DrawableRes
import com.tfm.druidapp.R

sealed class Screen(val title: String, val route: String, @DrawableRes val icon: Int) {
    /*
    NavScreen: Ventanas normales con barra de navegación
     */
    data object Monitoring : Screen(
        title = "Monitorización",
        route = "monitorizacion",
        icon = R.drawable.baseline_monitor_heart_24
    )
    data object Actuation : Screen(
        title = "Actuación",
        route = "actuacion",
        icon = R.drawable.baseline_precision_manufacturing_24
    )
    data object Settings : Screen(
        title = "Ajustes",
        route = "settings",
        icon = R.drawable.baseline_settings_24
    )

    /*
    DrawerScreen: Ventanas a las que se accede desde el drawer
     */
    data object Project : Screen(
        title = "Proyecto",
        route = "proyecto",
        icon = R.drawable.baseline_info_24
    )
    data object Opcion1 : Screen(
        title = "Opcion1",
        route = "opcion1",
        icon = R.drawable.baseline_info_24
    )
    data object Opcion2 : Screen(
        title = "opcion2",
        route = "opcion2",
        icon = R.drawable.baseline_info_24
    )

    /*
    Monitoring: Ventanas que derivan de monitoring
     */
    data object PPG : Screen(
        title = "PPG",
        route = "ppg",
        icon = R.drawable.baseline_monitor_heart_24
    )
    data object Glasgow : Screen(
        title = "Escala de Glasgow",
        route = "glasgow",
        icon = R.drawable.baseline_monitor_heart_24
    )

}

val allScreens = listOf(
    Screen.Monitoring,
    Screen.Actuation,
    Screen.Settings,
    Screen.PPG,
    Screen.Glasgow,
    Screen.Project,
    Screen.Opcion1,
    Screen.Opcion2
)

val screensWithNav = listOf(
    Screen.Actuation,
    Screen.Monitoring,
    Screen.Settings
)
val screensInDrawer = listOf(
    Screen.Project,
    Screen.Opcion1,
    Screen.Opcion2
)

