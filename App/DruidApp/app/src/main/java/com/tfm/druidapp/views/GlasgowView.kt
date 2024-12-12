package com.tfm.druidapp.views

import android.content.res.Configuration
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Divider
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.RadioButton
import androidx.compose.material3.RadioButtonDefaults
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.tfm.druidapp.data.GlasgowData
import com.tfm.druidapp.data.MainViewModel
import com.tfm.druidapp.ui.theme.DruidAppTheme
import com.tfm.druidapp.views.customElements.GlasgowGauge


@Composable
fun GlasgowView(viewModel: MainViewModel){
    val selectedOptions by viewModel.selectedGlasgowList
    val score = viewModel.glasgowScore.value

    LazyColumn(
        modifier = Modifier
            .padding(16.dp)
            .fillMaxSize(),
        verticalArrangement = Arrangement.spacedBy(6.dp)
    ){
        item{
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier
                    .clip(RoundedCornerShape(10.dp))
                    .background(MaterialTheme.colorScheme.primary)
                    .fillMaxWidth()
                    .height(120.dp)
                    .padding(6.dp)
            ) {
                GlasgowGauge(
                    score,
                    modifier = Modifier
                        .fillMaxWidth(0.5f)
                        .padding(top = 8.dp)
                )
                Column(
                    modifier = Modifier
                        .fillMaxSize(),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center
                ) {
                    Text(
                        text = if (score<3 || score>15){
                            ""
                        }else{
                            score.toString()
                        },
                        style = MaterialTheme.typography.labelLarge
                    )
                    Text(
                        text = when (score) {
                            in 3..8 -> "Grave"
                            in 9..12 -> "Moderado"
                            in 13..15 -> "Leve"
                            else -> ""
                        },
                        style = MaterialTheme.typography.titleMedium,
                    )
                }
            }
        }

        item {
            Text(
                text = "Apertura ocular",
                style = MaterialTheme.typography.titleMedium,
                modifier = Modifier.padding(top = 6.dp)
            )
        }
        item {
            RadioButtonList(GlasgowData.EyeOpening, selectedOptions[0]){index->
                viewModel.updateGlasgowScore(group = 0, selected = index)
            }
            HorizontalDivider(
                modifier = Modifier.padding(vertical = 6.dp),
                color = MaterialTheme.colorScheme.onPrimaryContainer
            )
        }
        item {
            Text(
                text = "Respuesta verbal",
                style = MaterialTheme.typography.titleMedium
            )
        }
        item {
            RadioButtonList(GlasgowData.VerbalResponse, selectedOptions[1]){index->
                viewModel.updateGlasgowScore(group = 1, selected = index)
            }
            HorizontalDivider(
                modifier = Modifier.padding(vertical = 6.dp),
                color = MaterialTheme.colorScheme.onPrimaryContainer
            )
        }

        item {
            Text(
                text = "Respuesta motora",
                style = MaterialTheme.typography.titleMedium
            )
        }
        item {
            RadioButtonList(GlasgowData.MotorResponse, selectedOptions[2]){index->
                viewModel.updateGlasgowScore(group = 2, selected = index)
            }
            HorizontalDivider(
                modifier = Modifier.padding(vertical = 6.dp),
                color = MaterialTheme.colorScheme.onPrimaryContainer
            )
        }


    }



}

@Composable
fun RadioButtonList(options: GlasgowData, selectedIndex: Int?, onSelected: (Int?)->Unit){

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(start = 16.dp)
    ){
        options.options.forEachIndexed{index, glasgowOption ->
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 4.dp)
                    .selectable(
                        selected = (index == selectedIndex),
                        onClick = {
                            if (index == selectedIndex) {
                                onSelected(null) // Emitir evento de deselección
                            } else {
                                onSelected(index) // Emitir evento normal
                            }
                        },
                        role = Role.RadioButton
                    ),
                verticalAlignment = androidx.compose.ui.Alignment.Top
            ) {
                RadioButton(
                    selected = (index == selectedIndex),
                    onClick = null, // Se gestiona el click desde `Row`,
                    modifier = Modifier.padding(end=8.dp),
                    colors = RadioButtonDefaults.colors(
                        selectedColor = Color.Green,
                        unselectedColor = MaterialTheme.colorScheme.onPrimary
                    )
                )
                Text(
                    text = glasgowOption.text,
                    style = MaterialTheme.typography.bodyMedium)
            }
        }
    }
}

@Preview(showBackground = true, uiMode = Configuration.UI_MODE_NIGHT_YES)
@Composable
fun GlasgowViewPreview(){
    DruidAppTheme{
        Surface(
            modifier = Modifier.fillMaxSize(),
            color = MaterialTheme.colorScheme.background
        ) {
            val vm: MainViewModel = viewModel()
            GlasgowView(vm)
        }
    }
}