package com.tfm.druidapp.data

import android.util.Log
import androidx.compose.runtime.MutableState
import androidx.compose.runtime.State
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.channels.Channel
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

    private val _wsUri: MutableState<String> = mutableStateOf("ws://192.168.1.67:9090")//192.168.2.181//192.168.1.67
    val wsUri: State<String> get() = _wsUri
    fun updateWsUri(uri: String){
        _wsUri.value = uri
        connectWebSocket()
    }

    lateinit var wsClient: RosWebSocketClient
    init {
        connectWebSocket()
    }

    fun connectWebSocket() {
        // Crear una nueva instancia de WebSocketClient y conectarse
        wsClient = RosWebSocketClient(URI(_wsUri.value), this)
        wsClient.connect()
        //waitForConnection()
        updateLoadingState(true)
    }
    fun disconnectWebSocket() {
        wsClient.disconnect()
        //TODO Resetear vatiables
        clearAmplitudes()
        updateTemperature(null)
    }

    override fun onCleared() {
        super.onCleared()
        disconnectWebSocket() // Cerrar la conexión al destruir el ViewModel
        _pulseListChannel.close() //TODO crear un nuevo canal cuando se reconecte
    }

    //Mensajes
    val topicsMap: Map<String, TopicInfo> = mapOf( //TODO poner los que haga falta
        "/sensor1_data" to TopicInfo(MsgTypes.DoubleMsg::class.java),
        "/ppg_data" to TopicInfo(MsgTypes.DoubleArrayMsg::class.java)
    )


    ////////////////// RELACIONADO CON MEDIC DATA /////////////////////////////
    //Glasgow
    private val _glasgowScore: MutableState<Int> = mutableStateOf(0)
    val glasgowScore: State<Int> = _glasgowScore

    private val _selectedGlasgowList: MutableState<List<Int?>> = mutableStateOf(listOf(null, null, null))
    val selectedGlasgowList: State<List<Int?>> = _selectedGlasgowList

    fun updateGlasgowScore(group: Int, selected: Int?) {
        _selectedGlasgowList.value = _selectedGlasgowList.value .toMutableList()
            .apply { this[group] = selected }
        _glasgowScore.value = _selectedGlasgowList.value.takeIf {selectedList-> selectedList.all { selected-> selected != null } }?.let {
            GlasgowData.EyeOpening.options[it[0]!!].score +
                    GlasgowData.VerbalResponse.options[it[1]!!].score +
                    GlasgowData.MotorResponse.options[it[2]!!].score
        } ?: 0

    }

    //Pulso
    private val _pulseListChannel = Channel<List<Double>>(Channel.BUFFERED)
    private var _pulseSampleRate: Long = 100L
    fun updatePulseSampleRate(rate: Long){
        if(rate != _pulseSampleRate) _pulseSampleRate = rate
    }
    fun sendToChannel(list: List<Double>) {
        viewModelScope.launch(Dispatchers.IO) {
            _pulseListChannel.send(list)
        }
    }
    fun startProcessingPulseChannel() {
        viewModelScope.launch(Dispatchers.Default) {
            for (list in _pulseListChannel) {
                for (item in list){
                    if (item == -1.0){
                        clearAmplitudes()
                    }else{
                        addPulseAmplitude(item.toFloat())
                        delay(_pulseSampleRate-4) //Un poco menos para compensar
                    }
                }

            }
        }
    }


    private val _ppgData: MutableStateFlow<MsgTypes.PpgMsg> = MutableStateFlow(MsgTypes.PpgMsg())
    val ppgData: StateFlow<MsgTypes.PpgMsg> = _ppgData

    fun updatePpgData(data: MsgTypes.PpgMsg){
        _ppgData.value = data
    }

    private val _pulseAmplitudeList: MutableStateFlow<List<Float>> = MutableStateFlow(listOf(0f))
    val pulseAmplitudeList: StateFlow<List<Float>> = _pulseAmplitudeList

    val maxPulseRegisters = 50 //TODO ajustar si eso para que sea configurable

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
    private val _pressureData: MutableState<MsgTypes.BloodPressureMsg> = mutableStateOf(MsgTypes.BloodPressureMsg()) //TODO cambiar a la ventana de conexión
    val pressureData: State<MsgTypes.BloodPressureMsg> = _pressureData
    fun updateBloodPressureData(data: MsgTypes.BloodPressureMsg){
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


    ////////////////// RELACIONADO CON UI /////////////////////////////
    //RobotView
    private val _wsUriEdited: MutableState<String> = mutableStateOf("ws://192.168.1.67:9090")//192.168.2.181//192.168.1.67
    val wsUriEdited: State<String> get() = _wsUriEdited
    fun updateWsUriEdited(uri: String){
        _wsUriEdited.value = uri
    }
}