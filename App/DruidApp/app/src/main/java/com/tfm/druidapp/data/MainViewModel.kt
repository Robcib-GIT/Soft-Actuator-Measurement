package com.tfm.druidapp.data

import androidx.compose.runtime.MutableState
import androidx.compose.runtime.State
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.ViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

class MainViewModel : ViewModel() {
    //MQTT
    private val _connected: MutableState<Boolean> = mutableStateOf(false) //TODO cambiar a la ventana de conexión
    val connected: State<Boolean> = _connected
    fun setConnectionState(connected: Boolean){
        _connected.value = connected
    }

    //Glasgow
    private val _glasgowScore: MutableState<Int> = mutableStateOf(0)
    val glasgowScore: State<Int> = _glasgowScore
    fun setGlasgowScore(score: Int){
        _glasgowScore.value = score
    }

    //Pulso
    private val _pulsations: MutableStateFlow<Int> = MutableStateFlow(0)
    val pulsations: StateFlow<Int> = _pulsations

    fun setPulsations(pulsations: Int){
        _pulsations.value = pulsations
    }


    private val _pulseAmplitudeList: MutableStateFlow<List<Float>> = MutableStateFlow(listOf(0f))
    val pulseAmplitudeList: StateFlow<List<Float>> = _pulseAmplitudeList

    val maxPulseRegisters = 30 //TODO ajustar si eso

    fun addPulseAmplitude(amplitude: Float) {
        _pulseAmplitudeList.value = _pulseAmplitudeList.value
            .toMutableList() // Convierte la lista inmutable a mutable
            .apply {
                if (size >= maxPulseRegisters) {
                    removeAt(0) // Elimina el primer elemento si se supera el límite
                }
                add(amplitude) // Agrega el nuevo valor
            }
    }
    fun clearAmplitudes() { //TODO si la conexion se pierde eliminar la lista
        _pulseAmplitudeList.value = listOf(0f)
    }

    //Presion
    private val _pressureSYS: MutableState<Int> = mutableStateOf(0) //TODO cambiar a la ventana de conexión
    val pressureSYS: State<Int> = _pressureSYS
    fun setPressureSYS(pressure: Int){
        _pressureSYS.value = pressure
    }

    private val _pressureDIA: MutableState<Int> = mutableStateOf(0) //TODO cambiar a la ventana de conexión
    val pressureDIA: State<Int> = _pressureDIA
    fun setPressureDIA(pressure: Int){
        _pressureDIA.value = pressure
    }

    //Temperatura
    private val _temperature: MutableStateFlow<Float> = MutableStateFlow(0f)
    val temperature: StateFlow<Float> = _temperature

    fun updateTemperature(newTemperature: Float) {
        _temperature.value = newTemperature
    }






}