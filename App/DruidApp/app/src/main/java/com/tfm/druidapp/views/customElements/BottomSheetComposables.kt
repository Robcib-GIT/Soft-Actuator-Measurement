package com.tfm.druidapp.views.customElements

import android.content.res.Configuration
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.wrapContentHeight
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.tfm.druidapp.ui.theme.DruidAppTheme

@Composable
fun BPMInfo(){
    val bpmMap: Map<String, String> = mapOf(
        "Bebés (hasta 1 mes)" to "70 - 190",
        "Bebés (1 a 11 meses)" to "80 - 160",
        "Niños (1 a 2 años)" to "80 - 130",
        "Niños (3 a 4 años)" to "80 - 120",
        "Niños (5 a 6 años)" to "75 - 115",
        "Niños (7 a 9 años)" to "70 - 110",
        "Niños (más de 10 años)\n&\nAdultos (general)" to "60 - 100",
        "Adultos (Atletas entrenados)" to "40 - 60"
    )


    Column(
        modifier = Modifier.fillMaxWidth(),
        horizontalAlignment = Alignment.CenterHorizontally
    ){
        tableRow(text1 = "GRUPO", text2 = "PPM EN REPOSO", weight1 = 1f, weight2 = 1.4f, tableTitle = true)
        bpmMap.forEach{(group,bpmRange)->
            HorizontalDivider(
                modifier = Modifier
                .fillMaxWidth(0.9f),
                color = MaterialTheme.colorScheme.onPrimaryContainer
            )
            tableRow(text1 = group, text2 = bpmRange, weight1 = 1f, weight2 = 1.4f)
        }
    }
}

@Composable
fun FrequencyInfo(){
    val frecMap: Map<String, String> = mapOf(
        "Bebés (hasta 1 mes)" to "1.16 - 3.16",
        "Bebés (1 a 11 meses)" to "1.33 - 2.66",
        "Niños (1 a 2 años)" to "1.33 - 2.16",
        "Niños (3 a 4 años)" to "1.33 - 2",
        "Niños (5 a 6 años)" to "1.25 - 1.91",
        "Niños (7 a 9 años)" to "1.16 - 1.83",
        "Niños (más de 10 años)\n&\nAdultos (general)" to "1 - 1.66",
        "Adultos (Atletas entrenados)" to "0.66 - 1"
    )


    Column(
        modifier = Modifier.fillMaxWidth(),
        horizontalAlignment = Alignment.CenterHorizontally
    ){
        tableRow(text1 = "GRUPO", text2 = "FREC EN REPOSO", weight1 = 1f, weight2 = 1.4f, tableTitle = true)
        frecMap.forEach{(group,bpmRange)->
            HorizontalDivider(
                modifier = Modifier
                    .fillMaxWidth(0.9f),
                color = MaterialTheme.colorScheme.onPrimaryContainer
            )
            tableRow(text1 = group, text2 = bpmRange, weight1 = 1f, weight2 = 1.4f)
        }
    }
}

@Composable
fun IBIInfo(){
    val ibiMap: Map<String, String> = mapOf(
        "Bebés (hasta 1 mes)" to "315 - 857",
        "Bebés (1 a 11 meses)" to "375 - 750",
        "Niños (1 a 2 años)" to "461 - 750",
        "Niños (3 a 4 años)" to "500 - 750",
        "Niños (5 a 6 años)" to "521 - 800",
        "Niños (7 a 9 años)" to "545 - 857",
        "Niños (más de 10 años)\n&\nAdultos (general)" to "600 - 1000",
        "Adultos (Atletas entrenados)" to "1000 - 1500"
    )


    Column(
        modifier = Modifier.fillMaxWidth(),
        horizontalAlignment = Alignment.CenterHorizontally
    ){
        tableRow(text1 = "GRUPO", text2 = "IBI EN REPOSO", weight1 = 1f, weight2 = 1.4f, tableTitle = true)
        ibiMap.forEach{(group,bpmRange)->
            HorizontalDivider(
                modifier = Modifier
                    .fillMaxWidth(0.9f),
                color = MaterialTheme.colorScheme.onPrimaryContainer
            )
            tableRow(text1 = group, text2 = bpmRange, weight1 = 1f, weight2 = 1.4f)
        }
    }
}

@Composable
fun SDNNInfo(){
    val sdnnMap: Map<String, String> = mapOf(
        "Adulto en reposo" to "50 - 100",
        "Adulto entrenado en reposo" to ">100",
        "Sueño profundo" to ">150",
        "Recien nacidos" to "<200"
    )


    Column(
        modifier = Modifier.fillMaxWidth(),
        horizontalAlignment = Alignment.CenterHorizontally
    ){
        tableRow(text1 = "GRUPO", text2 = "SDNN NORMAL", weight1 = 1f, weight2 = 1.4f, tableTitle = true)
        sdnnMap.forEach{(group,bpmRange)->
            HorizontalDivider(
                modifier = Modifier
                    .fillMaxWidth(0.9f),
                color = MaterialTheme.colorScheme.onPrimaryContainer
            )
            tableRow(text1 = group, text2 = bpmRange, weight1 = 1f, weight2 = 1.4f)
        }
    }
}

@Composable
fun RMSSDInfo(){
    val rmssdMap: Map<String, String> = mapOf(
        "Adulto en reposo" to "20 - 50",
        "Adulto entrenado en reposo" to ">60",
        "Sueño profundo" to ">80",
        "Recien nacidos" to "<100"
    )


    Column(
        modifier = Modifier.fillMaxWidth(),
        horizontalAlignment = Alignment.CenterHorizontally
    ){
        tableRow(text1 = "GRUPO", text2 = "SDNN NORMAL", weight1 = 1f, weight2 = 1.4f, tableTitle = true)
        rmssdMap.forEach{(group,bpmRange)->
            HorizontalDivider(
                modifier = Modifier
                    .fillMaxWidth(0.9f),
                color = MaterialTheme.colorScheme.onPrimaryContainer
            )
            tableRow(text1 = group, text2 = bpmRange, weight1 = 1f, weight2 = 1.4f)
        }
    }
}


@Composable
fun tableRow(text1: String, text2: String, weight1: Float,weight2: Float,  tableTitle: Boolean= false){
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
            modifier = Modifier
                .weight(weight1)
                .padding(vertical = 4.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(text = text1, style = style, textAlign = TextAlign.Center)
        }
        Column(
            modifier = Modifier
                .weight(weight2)
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
            RMSSDInfo()
        }
    }
}