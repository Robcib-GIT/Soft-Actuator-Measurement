package com.tfm.druidapp.data

import android.content.res.Configuration
import androidx.compose.foundation.background
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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.tfm.druidapp.ui.theme.DruidAppTheme

@Composable
fun bpmInfo(){
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
            bpmInfo()
        }
    }
}