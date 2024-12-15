package com.tfm.druidapp.data

import android.util.Log
import androidx.lifecycle.viewModelScope
import com.tfm.druidapp.data.RosMsgUtilities.createJsonMessage
import com.tfm.druidapp.data.RosMsgUtilities.parseRosMessage
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.java_websocket.client.WebSocketClient
import org.java_websocket.handshake.ServerHandshake
import org.json.JSONObject
import java.lang.Exception
import java.net.URI

class RosWebSocketClient(uri: URI, private val viewModel: MainViewModel) : WebSocketClient(uri) {

    override fun onOpen(handshakedata: ServerHandshake?) {
        Log.d("RosWebSocketClient", "Connected to $uri")
        viewModel.updateConnectionState(true)
        viewModel.updateLoadingState(false)
        // Suscribirse a tópicos
        viewModel.topicsMap.forEach{ (topic, topicInfo) ->
            subscribeToTopic(topic = topic)
            topicInfo.subscribedTo.value = true
        }
        viewModel.showToast("Conexión exitosa")
    }

    private var _firstPulseList = true
    override fun onMessage(message: String?) {
        safelyExecute{
            val parsedMsg = parseRosMessage(message, viewModel.topicsMap)

            when(parsedMsg.topic){
                "/sensor1_data" -> {
                    var sensor1 = parsedMsg.msg.data as? Double

                    if(sensor1 != null && sensor1 != -1.0){
                        sensor1 = sensor1.times(50)
                        viewModel.updateSensor3Data(sensor1)
                        val floatValue = sensor1.toFloat()
                        viewModel.updateSensor1Data(sensor1)
                        viewModel.updateTemperature(floatValue)
                    }else{
                        viewModel.updateTemperature(null)
                        viewModel.updateSensor3Data(null)
                    }

                }
                "/sensor2_data" -> {}
                "/sensor3_data" -> {
                    //Como no he expecificado el tipo de numero recibido gson lo parsea como double
                    if(parsedMsg.msg.data is List<*> && parsedMsg.msg.data.all { it is Double }){
                        //Log.d("Pruebas", "Array recibido: ${parsedMsg.msg.data}")
                        //val doubleList= parsedMsg.msg.data as? List<Double>
                        val doubleList = mutableListOf<Double>()
                        for (item in parsedMsg.msg.data) {
                            if (item is Double) {
                                doubleList.add(item/1023) //TODO Cambiar segun la resolucion
                            }
                        }
                        viewModel.sendToChannel(doubleList)
                        if (_firstPulseList){
                            viewModel.startProcessingPulseChannel()
                            _firstPulseList = false
                        }
                        /*
                        TODO arreglar
                        val doubleList: List<Double> = parsedMsg.msg.data
                        viewModel.vectorChannel.send(doubleList)
                         */
                    }

                    /*
                     val sensor3 = parsedMsg.msg.data as? Double
                    if(sensor3 != null && sensor3 != -1.0){
                        viewModel.updateSensor3Data(sensor3)
                        val floatValue = sensor3.coerceIn(0.0,1.0).toFloat()
                        viewModel.addPulseAmplitude(floatValue)
                    }else{
                        viewModel.clearAmplitudes()
                        viewModel.updateSensor3Data(null)
                    }
                    */

                }
                else -> {}
            }
        }
    }

    override fun onClose(code: Int, reason: String?, remote: Boolean) {
        Log.d("RosWebSocketClient", "Disconnected")
        reason?.let {
            if(it.indexOf("failed") == -1 && it.indexOf("unreachable") == -1){
                viewModel.showToast("Conexión cerrada")
                viewModel.updateConnectionState(false)
            }
        }

    }
    fun disconnect() {
        if (isOpen) {
            viewModel.topicsMap.forEach{ (topic, topicInfo) ->
                if (topicInfo.subscribedTo.value){
                    unsubscribeFromTopic(topic = topic)
                    topicInfo.subscribedTo.value = false
                }

            }
        }
        close()
    }

    override fun onError(ex: Exception?) {
        ex?.let {
            Log.e("RosWebSocketClient", "Error: ${it.message}")
            if(viewModel.loadingState.value){
                viewModel.updateLoadingState(false)
                viewModel.showToast("No se pudo conectar")
            }

        }
    }

    fun publishToTopic(rosMsg: RosMsg) {
        safelyExecute {
            if (isOpen) {
                val jsonMessage = createJsonMessage(rosMsg)
                send(jsonMessage)
                //Log.d("RosWebSocketClient", "Published: $jsonMessage")
            } else {
                Log.e("RosWebSocketClient", "WebSocket is not open, cannot publish")
            }
        }
    }

    fun subscribeToTopic(topic: String) {
        if (isOpen) {
            val jsonMessage = JSONObject()
            jsonMessage.put("op", MsgOp.SUBSCRIBE)
            jsonMessage.put("topic", topic)

            send(jsonMessage.toString())
            Log.d("RosWebSocketClient", "Subscribed to $topic")
        } else {
            Log.e("RosWebSocketClient", "WebSocket is not open, cannot subscribe")
        }
    }

    fun unsubscribeFromTopic(topic: String) {
        if (isOpen) {
            val jsonMessage = JSONObject()
            jsonMessage.put("op", MsgOp.UNSUBSCRIBE)
            jsonMessage.put("topic", topic)

            send(jsonMessage.toString())
            Log.d("RosWebSocketClient", "Unsubscribed from $topic")
        } else {
            Log.e("RosWebSocketClient", "WebSocket is not open, cannot unsubscribe")
        }
    }

    private fun safelyExecute(task: ()-> Unit){
        viewModel.viewModelScope.launch {
            try {
                withContext(Dispatchers.IO) {
                    task()
                }
            } catch (e: Exception) {
                Log.e("RosWebSocketClient", "Error handling data: ${e.message}")
            }
        }
    }

}