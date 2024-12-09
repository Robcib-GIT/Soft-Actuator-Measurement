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
        topicsMap.forEach{topic,topicInfo->
            subscribeToTopic(topic = topic)
            topicInfo.subscribedTo = true
        }
        viewModel.showToast("Conexión exitosa")
    }

    override fun onMessage(message: String?) {
        safelyExecute{
            val parsedMsg = parseRosMessage(message)

            when(parsedMsg.topic){
                "/sensor1_data" -> viewModel.updateSensor1Data(parsedMsg.msg.data as? Double)
                "/sensor2_data" -> viewModel.updateSensor2Data(parsedMsg.msg.data as? Double)
                "/sensor3_data" -> viewModel.updateSensor3Data(parsedMsg.msg.data as? Double)
                else -> {}
            }
        }
    }

    override fun onClose(code: Int, reason: String?, remote: Boolean) {
        Log.d("RosWebSocketClient", "Disconnected")
        reason?.let {
            if(it.indexOf("failed") == -1){ //sino solapa el toast del error de conexion
                viewModel.showToast("Conexión cerrada")
                viewModel.updateConnectionState(false)
            }
        }

    }
    fun disconnect() {
        if (isOpen) {
            topicsMap.forEach{topic,topicInfo->
                if (!topicInfo.subscribedTo){
                    unsubscribeFromTopic(topic = topic)
                    topicInfo.subscribedTo = false
                }

            }
        }
        close()
    }

    override fun onError(ex: Exception?) {
        ex?.let { Log.e("RosWebSocketClient", "Error: ${it.message}") }
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
            jsonMessage.put("op", "subscribe")  //TODO usar clase
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
            jsonMessage.put("op", "unsubscribe") //TODO usar clase
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