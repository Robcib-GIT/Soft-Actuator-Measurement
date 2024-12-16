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
                    val msg = parsedMsg.msg as? MsgTypes.DoubleMsg
                    val sensor1 = msg?.data?.div(10.23) //TODO cambiar esto para prueba

                    if(sensor1 != null && sensor1 != -1.0){
                        viewModel.updateSensor1Data(sensor1)
                        viewModel.updateTemperature(sensor1.toFloat())
                    }else{
                        viewModel.updateTemperature(null)
                        viewModel.updateSensor3Data(null)
                    }

                }
                "/sensor2_data" -> {}
                "/sensor3_data" -> {
                    val msg = parsedMsg.msg as? MsgTypes.IntArrayMsg
                    val processedList = mutableListOf<Float>()
                    msg?.data?.forEach{item->
                        if(item==-1) processedList.add(item.toFloat())
                        else processedList.add(item.toFloat()/1023)
                    }
                    if (msg != null) {
                        msg.layout.data_offset?.let { viewModel.updatePulseSampleRate(it.toLong()) }
                    }
                    viewModel.sendToChannel(processedList)
                    if (_firstPulseList){
                        viewModel.startProcessingPulseChannel()
                        _firstPulseList = false
                    }
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
                val jsonMessage = createJsonMessage(rosMsg, viewModel.topicsMap)
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