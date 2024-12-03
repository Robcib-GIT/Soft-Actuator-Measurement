package com.tfm.druidapp.data

import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlin.random.Random

open class MQTT(open val viewModel: MainViewModel) {
    /*TODO añadir verdadera funcionalidad MQTT*/


    /*Dummy MQTT*/
    class Simulation(override val viewModel: MainViewModel):MQTT(viewModel){

        // Lista de valores predefinidos de amplitud (simulando una onda)
        private val amplitudeValues = listOf(0f, 0.5f, 1f, 0.5f, 0f, -0.5f, -1f, -0.5f, 0f)

        // Frecuencia de simulación (milisegundos entre valores)
        private val intervalMillis: Long = 50 // 10 Hz = 100 ms

        // Método para iniciar la simulación
        fun startSimulation() {
            viewModel.viewModelScope.launch {
                for (i in 1..6) {
                    for (amplitude in amplitudeValues) {
                        viewModel.addPulseAmplitude(amplitude)
                        viewModel.updateTemperature(Random.nextFloat() * (45f - 34f) + 34f)
                        delay(intervalMillis)
                    }
                }
            }
        }

    }
}