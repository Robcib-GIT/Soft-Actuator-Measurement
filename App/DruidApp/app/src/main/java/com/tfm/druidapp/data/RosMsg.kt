package com.tfm.druidapp.data

import android.util.Log
import androidx.compose.runtime.MutableState
import androidx.compose.runtime.mutableStateOf
import com.google.gson.Gson
import com.google.gson.JsonObject

/*
Para añadir un nuevo mensaje al que se deba susbcribir RosWebSocketClient
añadir su informacion a topicsMap, donde la clave es el topico del mensaje
y su contenido un data object que contiene si se está actualmente subscrito a
este y la data class a la que pertenece. Esta última solo hace falta añadirla
si se trata de una clase personalizada.
 */

data object MsgOp {
    val PUBLISH = "publish"
    val SUBSCRIBE = "subscribe"
    val UNSUBSCRIBE = "unsubscribe"
}

/*data class MsgData(
    val data: Any?,
    val layout: MsgLayout? = null
)*/
data class MsgLayout(
    val dim: List<MsgMultiArrayDimension> = emptyList(),
    val data_offset: Int? = null
)

data class MsgMultiArrayDimension(
    val label: String? = null,
    val size: Int? = null,
    val stride: Int? = null
)


data class RosMsg(
    val operation: String,
    val topic: String,
    val msg: Any,
    val type: String? = null
)

data class TopicInfo(
    val clazz: Class<*>,
    val subscribedTo: MutableState<Boolean> = mutableStateOf(false)
)

sealed class MsgTypes(){ //Añadir aqui más si hace falta
    data class IntMsg(
        val data: Int
    ):MsgTypes()
    data class DoubleMsg(
        val data: Double
    ):MsgTypes()
    data class StringMsg(
        val data: String
    ):MsgTypes()
    data class IntArrayMsg(
        val layout: MsgLayout = MsgLayout(),
        val data: List<Int> = emptyList()
    ):MsgTypes()
    data class DoubleArrayMsg(
        val layout: MsgLayout,
        val data: List<Double> = emptyList()
    ):MsgTypes()

    //Personales
    data class BloodPressureMsg(
        val sys: Int? = null,
        val dia: Int? = null
    ):MsgTypes()

    data class PpgMsg(  //TODO modificar tipos de datos
        val bpm: Int? = null,
        val sdnn: Int? = null,
        val rmsdd: Int? = null,
        val frequency: Double? = null,
        val amplitude: Double? = null,
        val riseTime: Double? = null
    ):MsgTypes()
}

object RosMsgUtilities {
    fun createJsonMessage(rosMsg: RosMsg, topicsMap: Map<String, TopicInfo>): String {
        //TODO añadir posibilidad de enviar arrays (no voy a usar de momento)
        val gson = Gson()

        val jsonObject = JsonObject().apply {
            addProperty("op", rosMsg.operation)
            addProperty("topic", rosMsg.topic)

            val msgJson = gson.toJsonTree(rosMsg.msg)
            Log.d("Pruebas","JsonCreado: $msgJson")
            add("msg", msgJson)

            rosMsg.type?.let { addProperty("type", it) }
        }

        return gson.toJson(jsonObject)
    }

    fun parseRosMessage(jsonMessage: String?, topicsMap: Map<String, TopicInfo>): RosMsg {
        val gson = Gson()

        val jsonObject = gson.fromJson(jsonMessage, JsonObject::class.java)

        val operation = jsonObject.get("op")?.asString ?: ""
        val topic = jsonObject.get("topic")?.asString ?: ""
        val msgJson = jsonObject.getAsJsonObject("msg")
        val type = jsonObject.get("type")?.asString

        val msg = gson.fromJson(msgJson, topicsMap[topic]?.clazz)

        return RosMsg(operation = operation, topic = topic, msg = msg, type = type)
    }
}