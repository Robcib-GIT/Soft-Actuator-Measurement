package com.tfm.druidapp.data

import com.google.gson.Gson
import com.google.gson.JsonObject

/*
Para añadir un nuevo mensaje al que se deba susbcribir RosWebSocketClient
añadir su informacion a topicsMap, donde la clave es el topico del mensaje
y su contenido un data object que contiene si se está actualmente subscrito a
este y la data class a la que pertenece. Esta última solo hace falta añadirla
si se trata de una clase personalizada.
 */
val topicsMap: Map<String, TopicInfo> = mapOf( //TODO poner los que haga falta
    "/sensor1_data" to TopicInfo(),
    "/sensor2_data" to TopicInfo(),
    "/sensor3_data" to TopicInfo(),
    "/temperature_data" to TopicInfo(),
    "/ppg_data" to TopicInfo(PpgData::class.java),
    "/pressure_data" to TopicInfo(BloodPressureData::class.java),
)
data object MsgOp {
    val PUBLISH = "publish"
    val SUBSCRIBE = "subscribe"
    val UNSUBSCRIBE = "unsubscribe"
}

data class MsgData(
    val data: Any?
)

data class RosMsg(
    val operation: String,
    val topic: String,
    val msg: MsgData,
    val type: String? = null
)

data class TopicInfo(
    val clazz: Class<*>? = null,
    var subscribedTo: Boolean = false
)

object RosMsgUtilities {
    fun createJsonMessage(rosMsg: RosMsg): String {
        val gson = Gson()

        val jsonObject = JsonObject().apply {
            addProperty("op", rosMsg.operation)
            addProperty("topic", rosMsg.topic)

            val msgJson = JsonObject().apply {
                if (rosMsg.msg.data != null) {
                    val dataJson = gson.toJsonTree(rosMsg.msg.data)
                    add("data", dataJson)
                }
            }
            add("msg", msgJson)

            rosMsg.type?.let { addProperty("type", it) }
        }

        return gson.toJson(jsonObject)
    }

    fun parseRosMessage(jsonMessage: String?): RosMsg {
        val gson = Gson()

        val jsonObject = gson.fromJson(jsonMessage, JsonObject::class.java)

        val operation = jsonObject.get("op")?.asString ?: ""
        val topic = jsonObject.get("topic")?.asString ?: ""
        val msgJson = jsonObject.getAsJsonObject("msg")
        val type = jsonObject.get("type")?.asString

        val msg: MsgData = if (topicsMap[topic]?.clazz != null){
            val msgData = msgJson.getAsJsonObject("data")

            val data = gson.fromJson(msgData, topicsMap[topic]?.clazz)

            MsgData(data)
        }else{
            gson.fromJson(msgJson, MsgData::class.java)
        }

        return RosMsg(operation = operation, topic = topic, msg = msg, type = type)
    }
}