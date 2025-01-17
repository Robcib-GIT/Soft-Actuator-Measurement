package com.tfm.druidapp.data

data class SettingsData(
    val age: Int = 30,
    val gender: String = "Hombre",
    val wsUri: String = "ws://192.168.1.67:9090"
)