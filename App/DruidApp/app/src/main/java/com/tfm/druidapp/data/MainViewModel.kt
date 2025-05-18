package com.tfm.druidapp.data

import android.util.Log
import androidx.compose.runtime.Composable
import androidx.compose.runtime.MutableState
import androidx.compose.runtime.State
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.tfm.druidapp.data.MedicUtilities.calculateNormalRanges
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.launchIn
import kotlinx.coroutines.flow.onEach
import kotlinx.coroutines.launch
import java.net.URI

class MainViewModel(private val dataStoreManager: DataStoreManager) : ViewModel() {

    ////////////////// DataStore /////////////////////////////
    private val _settingsData = MutableStateFlow(SettingsData())
    val settingsData: StateFlow<SettingsData> get() = _settingsData
    fun saveSettings(settingsData: SettingsData) {
        viewModelScope.launch {
            dataStoreManager.saveToDataStore(settingsData)
        }
    }
    fun clearSettings() {
        viewModelScope.launch {
            dataStoreManager.clearDataStore()
        }
    }

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

    //BottomSheet
    private val _showBottomSheet = mutableStateOf(false)
    val showBottomSheet: State<Boolean> get() = _showBottomSheet
    fun updateBottomSheetVisibility(show: Boolean){
        _showBottomSheet.value = show
    }
    private val _bottomSheetContent = mutableStateOf<(@Composable () -> Unit)?>(null)
    val bottomSheetContent: State<(@Composable () -> Unit)?> get() = _bottomSheetContent
    fun setComposableContent(content: @Composable () -> Unit) {
        _bottomSheetContent.value = content
    }

    ////////////////// ROSBRIDGE /////////////////////////////
    private val _connectionState = mutableStateOf(false)
    val connectionState: State<Boolean> get() = _connectionState
    fun updateConnectionState(connected: Boolean){
        _connectionState.value = connected
    }

    private val _wsUri = MutableStateFlow("")//: MutableState<String> = mutableStateOf("")//192.168.2.181//192.168.1.67//"ws://192.168.1.67:9090"
    val wsUri: StateFlow<String> get() = _wsUri
    fun updateWsUri(uri: String){
        _wsUri.value = uri
        //connectWebSocket()
    }

    lateinit var wsClient: RosWebSocketClient
    init {

        dataStoreManager.getFromDataStore()
            .onEach {
                if (it.wsUri !=  _wsUri.value){
                    _wsUri.value = it.wsUri
                    _wsUriEdited.value = it.wsUri
                    connectWebSocket()
                }
                if (it.age !=  _settingsData.value.age || it.gender !=  _settingsData.value.gender){
                    updateNormalMedicRanges()
                }
                _settingsData.value = it
            }
            .launchIn(viewModelScope)

    }

    fun connectWebSocket() {
        //Log.d("Pruebas", "Conectando a ${_wsUri.value}")
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
    val topicsMap: Map<String, TopicInfo> = mapOf( //TODO poner los que haga falta y mover si eso
        "/sensor1_data" to TopicInfo(MsgTypes.FloatMsg::class.java),
        "/ppg_data" to TopicInfo(MsgTypes.FloatArrayMsg::class.java),
        "/cardiac_data" to TopicInfo(MsgTypes.CardiacMsg::class.java),
        "/open_actuator/feedback" to TopicInfo(MsgTypes.PneumaticFeedbackMsg::class.java),
        "/close_actuator/feedback" to TopicInfo(MsgTypes.PneumaticFeedbackMsg::class.java),
        "/blood_pressure/feedback" to TopicInfo(MsgTypes.PneumaticFeedbackMsg::class.java),
    )


    ////////////////// RELACIONADO CON MEDIC DATA /////////////////////////////
    fun resetMedicData(){ //TODO: añadir donde toque
        clearAmplitudes()
        updateTemperature(null)
        updateCardiacData(MsgTypes.CardiacMsg())
        updateBloodPressureData(MsgTypes.BloodPressureMsg())
    }

    private val _normalMedicRanges = mutableStateOf(NormalMedicRanges())
    val normalMedicRanges: State<NormalMedicRanges> get() = _normalMedicRanges
    private fun updateNormalMedicRanges(){
        _normalMedicRanges.value = calculateNormalRanges(age = settingsData.value.age, gender = settingsData.value.gender)
    }

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
    private val _pulseListChannel = Channel<List<Float>>(Channel.BUFFERED)
    private var _pulseSampleRate: Long = 100L
    fun updatePulseSampleRate(rate: Long){
        if(rate != _pulseSampleRate) _pulseSampleRate = rate
    }
    fun sendToChannel(list: List<Float>) {
        viewModelScope.launch(Dispatchers.IO) {
            _pulseListChannel.send(list)
        }
    }
    fun startProcessingPulseChannel() {
        viewModelScope.launch(Dispatchers.Default) {
            for (list in _pulseListChannel) {
                for (item in list){
                    if (item == -1f || !_connectionState.value){ //Evitar restos al apagar
                        clearAmplitudes()
                    }else{
                        addPulseAmplitude(item)
                        delay(_pulseSampleRate-4) //Un poco menos para compensar
                    }
                }

            }
        }
    }


    private val _cardiacData: MutableStateFlow<MsgTypes.CardiacMsg> = MutableStateFlow(MsgTypes.CardiacMsg())
    val cardiacData: StateFlow<MsgTypes.CardiacMsg> = _cardiacData

    fun updateCardiacData(data: MsgTypes.CardiacMsg){
        //TODO: Añadir cuenta de valores inconsistentes y si supera una cantidad sacar toast
        _cardiacData.value = data
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

        //Actualizar las pulsaciones sacadas del analisis de bp
        data.ppm.takeIf { it > -1 }?.let {ppm->
            updateCardiacData(_cardiacData.value.copy(ppm = ppm))
        }
    }

    //Temperatura
    private val _temperature: MutableStateFlow<Float?> = MutableStateFlow(null)
    val temperature: StateFlow<Float?> = _temperature

    fun updateTemperature(newTemperature: Float?) {
        _temperature.value = newTemperature
    }

    ////////////////// RELACIONADO CON ACTUADOR ///////////////////////////// TODO: comprobar lo del reset
    private val _actuatorState = mutableStateOf(ActuatorStates.Disconnected)
    val actuatorState: State<ActuatorStates> get() = _actuatorState
    fun updateActuatorState(state: ActuatorStates){
        _actuatorState.value = state
    }

    private val _openActuatorState = MutableStateFlow(
        ActuationState(name = "Abrir actuador")
    )
    val openActuatorState: StateFlow<ActuationState> = _openActuatorState
    fun updateOpenActuatorProgress(progress: Float){
        Log.d("ActuatorFeedback", "Open actuator: ${_openActuatorState.value.progress}") //TODO: comentar
        _openActuatorState.value = _openActuatorState.value.copy(progress = progress)
    }

    private val _closeActuatorState = MutableStateFlow(
        ActuationState(name = "Cerrar actuador")
    )
    val closeActuatorState: StateFlow<ActuationState> = _closeActuatorState
    fun updateCloseActuatorProgress(progress: Float){
        Log.d("ActuatorFeedback", "Close actuator: ${_closeActuatorState.value.progress}") //TODO: comentar
        _closeActuatorState.value = _closeActuatorState.value.copy(progress = progress)
    }

    private val _measureBPState = MutableStateFlow(listOf(
        ActuationState("Desinflado"),
        ActuationState("Inflado"),
        ActuationState("Procesamiento")
        )
    )
    val measureBPState: StateFlow<List<ActuationState>> = _measureBPState
    fun updateMeasureBPProgress(progress: Float){
        val statesProgress = FloatArray(3) { 0f }
        when (progress) {
            in 0f..1f -> {
                statesProgress[0] = progress
            }
            in 1f..2f -> {
                statesProgress[0] = 1f
                statesProgress[1] = progress - 1f
            }
            in 2f..3f -> {
                statesProgress[0] = 1f
                statesProgress[1] = 1f
                statesProgress[2] = progress - 2f
            }
        }

        _measureBPState.value = measureBPState.value.mapIndexed { index, state ->
            state.copy(progress=statesProgress[index])
        }

    }

    ////////////////// RELACIONADO CON UI /////////////////////////////
    //ActuationView




    /*
    fun simularProcesos() { //TODO: borrar
        viewModelScope.launch {
            if (actuatorState.value == ActuatorStates.Enabling) {
                // Lanza un proceso por cada elemento en el mapa
                actuatorStates.value.forEachIndexed{ index, state ->
                    var currentProgress = state.progress
                    while (currentProgress < 1f) {
                        delay(100)
                        currentProgress += 0.1f
                        updateActuatorStateProgress(index, currentProgress)
                    }
                    Log.d("Pruebas","Progreso $currentProgress")
                }
            }
        }
    }
    */

    //RobotView
    private val _wsUriEdited = MutableStateFlow("")//MutableState<String> = mutableStateOf("")//192.168.2.181//192.168.1.67//ws://192.168.1.67:9090
    val wsUriEdited: StateFlow<String> get() = _wsUriEdited
    fun updateWsUriEdited(uri: String){
        _wsUriEdited.value = uri
    }
}