package com.tfm.druidapp.data

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.intPreferencesKey
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.map


const val APP_DATASTORE = "app_data"
val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = APP_DATASTORE)

class DataStoreManager(val context: Context) {
    companion object{
        val AGE = intPreferencesKey("age")
        val GENDER = stringPreferencesKey("gender")
        val WS_URI = stringPreferencesKey("ws_uri")
    }

    suspend fun saveToDataStore(settingsData: SettingsData){
        context.dataStore.edit{
            it[AGE] = settingsData.age
            it[GENDER] = settingsData.gender
            it[WS_URI] = settingsData.wsUri
        }
    }

    fun getFromDataStore() = context.dataStore.data.map {
        SettingsData(
            age = it[AGE] ?: 30,
            gender = it[GENDER] ?: "Male",
            wsUri = it[WS_URI] ?: "ws://192.168.1.67:9090"
        )
    }

    suspend fun clearDataStore() = context.dataStore.edit {
        it.clear()
    }
}