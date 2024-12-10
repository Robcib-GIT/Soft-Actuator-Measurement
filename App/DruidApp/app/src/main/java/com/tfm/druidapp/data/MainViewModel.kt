package com.tfm.druidapp.data

import androidx.compose.runtime.MutableState
import androidx.compose.runtime.State
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import java.net.URI

class MainViewModel : ViewModel() {
    ////////////////// UTILES /////////////////////////////
    //TOAST
    private val _toastMessage = MutableStateFlow<String?>(null)
    val toastMessage: StateFlow<String?> = _toastMessage
    fun showToast(message: String) {
        _toastMessage.value = message
    }
    fun clearToast() {
        _toastMessage.value = null
    }

    //Proceso de carga
    private val _loadingState = MutableStateFlow(false)
    val loadingState: StateFlow<Boolean> get() = _loadingState
    fun updateLoadingState(updating: Boolean){
        _loadingState.value = updating
    }


    ////////////////// ROSBRIDGE /////////////////////////////
    private val _connectionState = mutableStateOf(false)
    val connectionState: State<Boolean> get() = _connectionState
    fun updateConnectionState(connected: Boolean){
        _connectionState.value = connected
    }

    private val _wsUri: MutableState<String> = mutableStateOf("ws://192.168.1.67:9090")
    val wsUri: State<String> get() = _wsUri
    fun updateWsUri(uri: String){
        _wsUri.value = uri
    }

    lateinit var wsClient: RosWebSocketClient
    init {
        connectWebSocket()
    }

    fun connectWebSocket() {
        // Crear una nueva instancia de WebSocketClient y conectarse
        wsClient = RosWebSocketClient(URI(_wsUri.value), this)
        wsClient.connect()
    }
    fun disconnectWebSocket() {
        wsClient.disconnect()
        clearAmplitudes()
        updateTemperature(null)
    }

    fun waitForConnection(){
        _loadingState.value = true
        //Iniciar la verificación de la conexión
        viewModelScope.launch {
            delay(10000)
            _loadingState.value = false
            if (!_connectionState.value) {
                showToast("No se pudo conectar")
            }
        }
    }

    override fun onCleared() {
        super.onCleared()
        disconnectWebSocket() // Cerrar la conexión al destruir el ViewModel
    }




    ////////////////// RELACIONADO CON MEDIC DATA /////////////////////////////
    //Glasgow
    private val _glasgowScore: MutableState<Int> = mutableStateOf(0)
    val glasgowScore: State<Int> = _glasgowScore
    fun updateGlasgowScore(score: Int){
        _glasgowScore.value = score
    }

    /*
    TODO tal vez tengo que poner las clases como posible null
      porque si el mensaje no se parsea bien se liaria creo
     */
    //Pulso
    private val _ppgData: MutableStateFlow<PpgData> = MutableStateFlow(PpgData())
    val ppgData: StateFlow<PpgData> = _ppgData

    fun updatePpgData(data: PpgData){
        _ppgData.value = data
    }

    private val _pulseAmplitudeList: MutableStateFlow<List<Float>> = MutableStateFlow(listOf(0f))
    val pulseAmplitudeList: StateFlow<List<Float>> = _pulseAmplitudeList

    val maxPulseRegisters = 30 //TODO ajustar si eso para que sea configurable

    fun addPulseAmplitude(amplitude: Float) {
        _pulseAmplitudeList.value = _pulseAmplitudeList.value
            .toMutableList() // Convierte la lista inmutable a mutable
            .apply {
                if (size >= maxPulseRegisters) {
                    removeAt(size - 1) // Elimina el primer elemento si se supera el límite
                }
                add(0, amplitude) // Agrega el nuevo valor
            }
    }
    fun clearAmplitudes() { //TODO si la conexion se pierde eliminar la lista
        _pulseAmplitudeList.value = listOf(0f)
    }

    //Presion
    private val _pressureData: MutableState<BloodPressureData> = mutableStateOf(BloodPressureData()) //TODO cambiar a la ventana de conexión
    val pressureData: State<BloodPressureData> = _pressureData
    fun updateBloodPressureData(data: BloodPressureData){
        _pressureData.value = data
    }

    //Temperatura
    private val _temperature: MutableStateFlow<Float?> = MutableStateFlow(null)
    val temperature: StateFlow<Float?> = _temperature

    fun updateTemperature(newTemperature: Float?) {
        _temperature.value = newTemperature
    }



    //TODO borrar
    private val _sensor1Data: MutableStateFlow<Double?> = MutableStateFlow(null)
    val sensor1Data: StateFlow<Double?> = _sensor1Data
    fun updateSensor1Data(data: Double?){
        _sensor1Data.value = data
    }

    private val _sensor2Data: MutableStateFlow<Double?> = MutableStateFlow(null)
    val sensor2Data: StateFlow<Double?> = _sensor2Data
    fun updateSensor2Data(data: Double?){
        _sensor2Data.value = data
    }

    private val _sensor3Data: MutableStateFlow<Double?> = MutableStateFlow(null)
    val sensor3Data: StateFlow<Double?> = _sensor3Data
    fun updateSensor3Data(data: Double?){
        _sensor3Data.value = data
    }


}