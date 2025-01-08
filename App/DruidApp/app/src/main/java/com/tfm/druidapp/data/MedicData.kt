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
@Composable
fun bpmInfo(){
    Column(
        modifier = Modifier.fillMaxWidth(),
        horizontalAlignment = Alignment.CenterHorizontally
    ){
        tableRow(text1 = "GRUPO", text2 = "PPM EN REPOSO", weight1 = 1f, weight2 = 1.4f, tableTitle = true)
        tableRow(text1 = "Bebés (hasta 1 mes)", text2 = "70 - 190", weight1 = 1f, weight2 = 1.4f)
        tableRow(text1 = "Bebés (1 a 11 meses)", text2 = "80 - 160", weight1 = 1f, weight2 = 1.4f)
        tableRow(text1 = "Niños (1 a 2 años)", text2 = "80 - 130", weight1 = 1f, weight2 = 1.4f)
        tableRow(text1 = "Niños (3 a 4 años)", text2 = "80 - 120", weight1 = 1f, weight2 = 1.4f)
        tableRow(text1 = "Niños (5 a 6 años)", text2 = "75 - 115", weight1 = 1f, weight2 = 1.4f)
        tableRow(text1 = "Niños (7 a 9 años)", text2 = "70 - 110", weight1 = 1f, weight2 = 1.4f)
        tableRow(text1 = "Niños (más de 10 años)\n" +
                "&\n" +
                "Adultos (general)", text2 = "60 - 100", weight1 = 1f, weight2 = 1.4f)
        tableRow(text1 = "Adultos (Atletas entrenados)", text2 = "40 - 60", weight1 = 1f, weight2 = 1.4f)

    }
}

@Composable
fun tableRow(text1: String, text2: String, weight1: Float,weight2: Float, tableTitle: Boolean= false){
    Row(
        modifier = Modifier
            .fillMaxWidth(0.9f)
            .wrapContentHeight(),
        verticalAlignment = Alignment.CenterVertically

    ){
        val style = if(tableTitle){
            MaterialTheme.typography.titleMedium
        }else{
            MaterialTheme.typography.bodySmall
        }
        Column(
            modifier = Modifier.weight(weight1)
                .padding(vertical = 4.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(text = text1, style = style, textAlign = TextAlign.Center)
        }
        Column(
            modifier = Modifier.weight(weight2)
                .padding(vertical = 4.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(text = text2, style = style, textAlign = TextAlign.Center)
        }
    }

}

@Preview(showBackground = true, uiMode = Configuration.UI_MODE_NIGHT_YES)
@Composable
fun bpmInfoPreview(){
    DruidAppTheme{
        Surface(
            modifier = Modifier.fillMaxSize(),
            color = MaterialTheme.colorScheme.background
        ) {
            bpmInfo()
        }
    }
}
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