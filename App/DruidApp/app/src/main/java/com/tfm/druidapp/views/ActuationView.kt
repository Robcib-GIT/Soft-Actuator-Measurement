package com.tfm.druidapp.views

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.tfm.druidapp.data.MainViewModel

@Composable
fun ActuationView(viewModel: MainViewModel){
    val expanded by viewModel.processIndicatorsExpanded
    val state by viewModel.vitalsMonitoring

    Column(
        modifier = Modifier
            .padding(16.dp)
            .fillMaxSize(),
        verticalArrangement = Arrangement.spacedBy(6.dp)
    ) {

    }
}