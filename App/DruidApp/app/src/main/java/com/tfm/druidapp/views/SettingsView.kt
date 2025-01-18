package com.tfm.druidapp.views

import android.content.res.Configuration
import androidx.activity.compose.BackHandler
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.wrapContentWidth
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowDropDown
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Clear
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material3.Button
import androidx.compose.material3.Checkbox
import androidx.compose.material3.CheckboxDefaults
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.RadioButton
import androidx.compose.material3.RadioButtonDefaults
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.tfm.druidapp.data.DataStoreManager
import com.tfm.druidapp.data.MainViewModel
import com.tfm.druidapp.data.SettingsData
import com.tfm.druidapp.data.TopicInfo
import com.tfm.druidapp.ui.theme.DruidAppTheme

@Composable
fun SettingsView(viewModel: MainViewModel){
    val settingsData by viewModel.settingsData.collectAsState()
    val wsUriEdited by viewModel.wsUriEdited.collectAsState()
    var isUriEditable by remember { mutableStateOf(false) }
    val focusRequester = remember { FocusRequester() }

    BackHandler(enabled = isUriEditable) {
        viewModel.updateWsUriEdited(viewModel.wsUri.value)
        isUriEditable = false
        //navController.popBackStack()
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(6.dp)
    ) {
        Text(
            text = "Ajustes del robot",
            style = MaterialTheme.typography.titleMedium)
        UriEditor(
            wsUriEdited = wsUriEdited,
            isUriEditable = isUriEditable,
            onUriChange = { viewModel.updateWsUriEdited(it) },
            onEditStart = {
                isUriEditable = true
                focusRequester.requestFocus()
            },
            onAccept = {
                //viewModel.updateWsUri(wsUriEdited)
                viewModel.saveSettings(settingsData.copy(wsUri = wsUriEdited))
                //viewModel.connectWebSocket()
                isUriEditable = false
            },
            onCancel = {
                viewModel.updateWsUriEdited(viewModel.wsUri.value)
                isUriEditable = false
            },
            focusRequester = focusRequester
        )

        TopicSelector(
            topicsMap = viewModel.topicsMap,
            connected = viewModel.connectionState.value,
            onChecked = {topic->
                viewModel.wsClient.subscribeToTopic(topic = topic)
            },
            onUnchecked = {topic->
                viewModel.wsClient.unsubscribeFromTopic(topic = topic)
            }
        )

        Spacer(modifier = Modifier.height(20.dp))
        Text(
            text = "Información del paciente",
            style = MaterialTheme.typography.titleMedium)
        VictimInfoEditor(
            settingsData = settingsData,
            onAccept = {
                viewModel.saveSettings(it)
            }
        )

    }

}


@Composable
fun TopicSelector(
    topicsMap: Map<String,TopicInfo>,
    connected: Boolean,
    onChecked: (String)->Unit,
    onUnchecked: (String)->Unit
){
    var expanded by remember { mutableStateOf(false) }

    Box(
        modifier = Modifier
            .fillMaxWidth()
    ) {
        // Botón con texto fijo
        Button(
            onClick = { expanded = true },
            shape = RoundedCornerShape(6.dp),
            contentPadding = PaddingValues(horizontal = 16.dp)
        ) {
            Text(
                text = "Topics subscritos",
                style = MaterialTheme.typography.bodyLarge
            )
            Spacer(modifier = Modifier.width(8.dp))
            Icon(imageVector = Icons.Default.ArrowDropDown, contentDescription = "Subscribed Topics")
        }

        // Menú desplegable con casillas de verificación
        DropdownMenu(
            expanded = expanded,
            onDismissRequest = { expanded = false },
            modifier = Modifier.wrapContentWidth()
        ) {
            topicsMap.forEach { (topic, topicInfo) ->
                DropdownMenuItem(
                    text = {
                        Row(
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Checkbox(
                                checked = topicInfo.subscribedTo.value,
                                onCheckedChange = null,
                                colors = CheckboxDefaults.colors(
                                    checkmarkColor = Color.Green
                                )
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(
                                text = topic,
                                style = MaterialTheme.typography.bodyLarge
                            )
                        }
                    },
                    enabled = connected,
                    onClick = {
                        topicInfo.subscribedTo.value = !topicInfo.subscribedTo.value
                        if (topicInfo.subscribedTo.value){
                            onChecked(topic)
                        }else{
                            onUnchecked(topic)
                        }
                    }
                )
            }
        }
    }
}

@Composable
fun UriEditor(
    wsUriEdited: String,
    isUriEditable: Boolean,
    onUriChange: (String) -> Unit,
    onEditStart: () -> Unit,
    onAccept: () -> Unit,
    onCancel: () -> Unit,
    focusRequester: FocusRequester
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically
    ) {
        OutlinedTextField(
            value = wsUriEdited,
            onValueChange = onUriChange,
            modifier = Modifier
                .focusRequester(focusRequester)
                .width(250.dp),
            enabled = isUriEditable,
            //readOnly = !isUriEditable,
            singleLine = true,
            label = { Text(text = "URI") },
            colors = OutlinedTextFieldDefaults.colors(
                disabledTrailingIconColor = MaterialTheme.colorScheme.onPrimary,
                disabledLabelColor = MaterialTheme.colorScheme.onPrimary,
                cursorColor = Color.White
            ),
            trailingIcon = {
                if (!isUriEditable) {
                    IconButton(onClick = onEditStart) {
                        Icon(
                            imageVector = Icons.Default.Edit,
                            contentDescription = "Edit"
                        )
                    }
                }
            }
        )
        if (isUriEditable) {
            Row(
                modifier = Modifier.padding(horizontal = 6.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                Box(
                    modifier = Modifier
                        .clip(CircleShape)
                        .clickable(onClick = onAccept)
                        .background(Color.Green)
                        .size(28.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.Check,
                        contentDescription = "Accept",
                        modifier = Modifier.align(Alignment.Center)
                    )
                }
                Box(
                    modifier = Modifier
                        .clip(CircleShape)
                        .clickable(onClick = onCancel)
                        .background(Color.Red)
                        .size(28.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.Clear,
                        contentDescription = "Cancel",
                        modifier = Modifier.align(Alignment.Center)
                    )
                }
            }
        }
    }
}

@Composable
fun VictimInfoEditor(
    settingsData: SettingsData,
    onAccept: (SettingsData)->Unit
){
    var expanded by remember { mutableStateOf(false) }
    var editedAge by remember { mutableStateOf(settingsData.age.toString()) }
    var editedGender by remember { mutableStateOf(settingsData.gender) }

    Box(
        modifier = Modifier
            .fillMaxWidth()
    ) {
        // Botón con texto fijo
        Button(
            onClick = { expanded = true },
            shape = RoundedCornerShape(6.dp),
            contentPadding = PaddingValues(horizontal = 16.dp)
        ) {
            Text(
                text = "Edad: ${settingsData.age}    |    Sexo: ${settingsData.gender}",
                style = MaterialTheme.typography.bodyLarge
            )
            Spacer(modifier = Modifier.width(12.dp))
            Icon(imageVector = Icons.Default.Edit, contentDescription = null)
        }

        DropdownMenu(
            expanded = expanded,
            onDismissRequest = {
                expanded = false
                editedAge = settingsData.age.toString()},
            modifier = Modifier.width(300.dp)
        ) {
            VictimInfoItem(
                text = "Edad",
                value = editedAge,
                type = 1,
                onValueChange = {editedAge = it}
            )
            VictimInfoItem(
                text = "Sexo",
                value = editedGender,
                type = 2,
                onValueChange = {editedGender = it}
            )
            Row(
                modifier = Modifier
                    .fillMaxWidth(),
                horizontalArrangement = Arrangement.Center
            ) {
                Button(
                    onClick = {
                        expanded = false
                        onAccept(settingsData.copy(age = editedAge.toInt(), gender = editedGender))
                    }
                ) {
                    Text(text = "Aceptar", style = MaterialTheme.typography.bodyLarge)
                }
            }

        }
    }
}


@Composable
fun VictimInfoItem(text: String, value: String, type: Int, onValueChange: (String)->Unit){
    DropdownMenuItem(
        text = {
            Row(
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(text = text, style = MaterialTheme.typography.bodyLarge)
                if(type==1){
                    Spacer(modifier = Modifier.width(10.dp))
                    TextField(
                        value = value,
                        onValueChange = { onValueChange(it)},
                        textStyle = MaterialTheme.typography.bodyMedium,
                        singleLine = true,
                        maxLines = 1,
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                        modifier = Modifier.width(60.dp)
                    )
                }else{
                    Row(
                        verticalAlignment = Alignment.CenterVertically
                    ){
                        Spacer(modifier = Modifier.width(10.dp))
                        RadioButton(
                            selected = (value == "Hombre"),
                            onClick = {onValueChange("Hombre")},
                            //modifier = Modifier.padding(end=8.dp),
                            colors = RadioButtonDefaults.colors(
                                selectedColor = Color.Green,
                                unselectedColor = MaterialTheme.colorScheme.onPrimary
                            )
                        )
                        Text(
                            text = "Hombre",
                            style = MaterialTheme.typography.bodyMedium)


                        Spacer(modifier = Modifier.width(10.dp))

                        RadioButton(
                            selected = (value == "Mujer"),
                            onClick = {onValueChange("Mujer")},
                            modifier = Modifier.padding(end=8.dp),
                            colors = RadioButtonDefaults.colors(
                                selectedColor = Color.Green,
                                unselectedColor = MaterialTheme.colorScheme.onPrimary
                            )
                        )
                        Text(
                            text = "Mujer",
                            style = MaterialTheme.typography.bodyMedium)
                    }
                }
            }
        },
        onClick = {}
    )
}
@Preview(showBackground = true, uiMode = Configuration.UI_MODE_NIGHT_YES)
@Composable
fun RobotViewPreview(){
    DruidAppTheme{
        Surface(
            modifier = Modifier.fillMaxSize(),
            color = MaterialTheme.colorScheme.background
        ) {
            val dataStoreManager = DataStoreManager(LocalContext.current)
            val vm = MainViewModel(dataStoreManager)
            SettingsView(vm)
            //VictimInfoEditor(settingsData = SettingsData(), onAccept ={} )
        }
    }
}