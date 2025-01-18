package com.tfm.druidapp.data

import android.content.res.Configuration
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.wrapContentHeight
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.tfm.druidapp.ui.theme.DruidAppTheme
import com.tfm.druidapp.views.PPGView

////////////////////// MEDIC INFO //////////////////////
data class NormalRange<T : Number>(
    val min: T,
    val max: T
)
data class NormalMedicRanges(
    val ppm: NormalRange<Int>? = null,
    val ibi: NormalRange<Float>? = null,
    val frequency: NormalRange<Float>? = null,
    val sdnn: NormalRange<Float>? = null,
    val rmsdd: NormalRange<Float>? = null,
    val amplitude: NormalRange<Float>? = null,
    val riseTime: NormalRange<Float>? = null,
    val sys: NormalRange<Int>? = null,
    val dia: NormalRange<Int>? = null,
    val temperature: NormalRange<Float>? = null
)
////////////////////// GLASGOW //////////////////////
data class GlasgowTestItem(
    val text: String,
    val score: Int
)

sealed class GlasgowData(val options: List<GlasgowTestItem>){
    data object EyeOpening:GlasgowData(
        listOf(
            GlasgowTestItem("Espontánea",4),
            GlasgowTestItem("A la orden",3),
            GlasgowTestItem("Ante estímulo doloroso",2),
            GlasgowTestItem("Ausencia de apertura ocular",1)
        )
    )
    data object VerbalResponse:GlasgowData(
        listOf(
            GlasgowTestItem("Orientado correctamente",5),
            GlasgowTestItem("Paciente confuso",4),
            GlasgowTestItem("Lenguaje inapropiado",3),
            GlasgowTestItem("Lenguaje incomprensible",2),
            GlasgowTestItem("Carencia de actividad verbal",1)
        )
    )
    data object MotorResponse:GlasgowData(
        listOf(
            GlasgowTestItem("Obedece órdenes correctamente",6),
            GlasgowTestItem("Localiza estímulos dolorosos",5),
            GlasgowTestItem("Responde al estímulo doloroso pero no localiza",4),
            GlasgowTestItem("Respuesta con flexión anormal de los miembros",3),
            GlasgowTestItem("Respuesta con extensión anormal de los miembros",2),
            GlasgowTestItem("Ausencia de respuesta motora",1)
        )
    )
}