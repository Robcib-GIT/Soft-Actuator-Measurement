package com.tfm.druidapp.data

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

data class Stamp(
    val secs: Int = 0,
    val nsecs: Int = 0
)

sealed class MsgTypes(){ //Añadir aqui más si hace falta
    data class IntMsg(
        val data: Int
    ):MsgTypes()
    data class DoubleMsg(
        val data: Double
    ):MsgTypes()
    data class FloatMsg(
        val data: Float
    ):MsgTypes()
    data class StringMsg(
        val data: String
    ):MsgTypes()
    data class BoolMsg(
        val data: Boolean
    ):MsgTypes()
    data class IntArrayMsg(
        val layout: MsgLayout = MsgLayout(),
        val data: List<Int> = emptyList()
    ):MsgTypes()
    data class DoubleArrayMsg(
        val layout: MsgLayout,
        val data: List<Double> = emptyList()
    ):MsgTypes()

    data class FloatArrayMsg(
        val layout: MsgLayout,
        val data: List<Float> = emptyList()
    ):MsgTypes()

    //Personales
    data class BloodPressureMsg(
        val sys: Int = -1,
        val dia: Int = -1,
        val ppm: Int = -1
    ):MsgTypes()
    /*
    int32 ppm
    float32 ibi
    float32 frequency
    float32 sdnn
    float32 rmssd
    */
    data class CardiacMsg(  //TODO modificar y añadir tipos de datos
        val ppm: Int = -1,
        val ibi: Float = -1f,
        val frequency: Float = -1f,
        val sdnn: Float = -1f,
        val rmsdd: Float = -1f,
        //val amplitude: Float = -1f,
        //val riseTime: Float = -1f,
    ):MsgTypes()

    data class PneumaticFeedbackMsg(  //TODO
        val header: Any,
        val status: Any,
        val feedback: FloatMsg
    ):MsgTypes()

    data class ActionGoal(  //TODO
        val goal: Any
    ):MsgTypes()

    data class  ActionCancel(
        val stamp: Stamp = Stamp(),
        val id: String = ""
    ):MsgTypes()
}

object RosMsgUtilities {
    fun createJsonMessage(rosMsg: RosMsg): String {
        //TODO añadir posibilidad de enviar arrays (no voy a usar de momento)
        val gson = Gson()

        val jsonObject = JsonObject().apply {
            addProperty("op", rosMsg.operation)
            addProperty("topic", rosMsg.topic)

            val msgJson = gson.toJsonTree(rosMsg.msg)
            //Log.d("Pruebas","JsonCreado: $msgJson")
            add("msg", msgJson)

            rosMsg.type?.let { addProperty("type", it) } //TODO: quitar
        }

        return gson.toJson(jsonObject)
    }

    fun parseRosMessage(jsonMessage: String?, topicsMap: Map<String, TopicInfo>): RosMsg {
        val gson = Gson()

        val jsonObject = gson.fromJson(jsonMessage, JsonObject::class.java)

        val operation = jsonObject.get("op")?.asString ?: ""
        val topic = jsonObject.get("topic")?.asString ?: ""
        val msgJson = jsonObject.getAsJsonObject("msg")
        val type = jsonObject.get("type")?.asString //TODO: quitar porque no lo envia

        val msg = gson.fromJson(msgJson, topicsMap[topic]?.clazz)

        return RosMsg(operation = operation, topic = topic, msg = msg, type = type)
    }
}