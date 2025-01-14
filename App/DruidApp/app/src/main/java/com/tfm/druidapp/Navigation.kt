package com.tfm.druidapp

import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.padding
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import com.tfm.druidapp.data.MainViewModel
import com.tfm.druidapp.views.ActuationView
import com.tfm.druidapp.views.MonitoringView
import com.tfm.druidapp.views.RobotView
import com.tfm.druidapp.data.Screen
import com.tfm.druidapp.views.GlasgowView
import com.tfm.druidapp.views.PPGView

@Composable
fun Navigation(navController: NavHostController, viewModel: MainViewModel, pd: PaddingValues){

    NavHost(
        navController = navController,// as NavHostController,
        startDestination = Screen.Actuation.route,
        modifier = Modifier.padding(pd)
    ) {
        composable(Screen.Monitoring.route) {
            MonitoringView(viewModel, navController)
        }

        composable(Screen.Actuation.route) {
            ActuationView(viewModel, navController)
        }

        composable(Screen.Robot.route) {
            RobotView(viewModel)
        }

        composable(Screen.PPG.route) {
            PPGView(viewModel)
        }

        composable(Screen.Glasgow.route) {
            GlasgowView(viewModel)
        }


    }
}