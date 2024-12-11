package com.tfm.druidapp.views

import android.content.res.Configuration
import androidx.activity.compose.BackHandler
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Clear
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
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
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import androidx.navigation.compose.rememberNavController
import com.tfm.druidapp.data.MainViewModel
import com.tfm.druidapp.ui.theme.DruidAppTheme

@Composable
fun RobotView(viewModel: MainViewModel, navController: NavHostController){
    val wsUriEdited by viewModel.wsUriEdited
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
        UriEditor(
            wsUriEdited = wsUriEdited,
            isUriEditable = isUriEditable,
            onUriChange = { viewModel.updateWsUriEdited(it) },
            onEditStart = {
                isUriEditable = true
                focusRequester.requestFocus()
            },
            onAccept = {
                viewModel.updateWsUri(wsUriEdited)
                isUriEditable = false
            },
            onCancel = {
                viewModel.updateWsUriEdited(viewModel.wsUri.value)
                isUriEditable = false
            },
            focusRequester = focusRequester
        )

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
            readOnly = !isUriEditable,
            singleLine = true,
            label = { Text(text = "URI") },
            colors = OutlinedTextFieldDefaults.colors(
                disabledTrailingIconColor = MaterialTheme.colorScheme.onPrimary,
                disabledLabelColor = MaterialTheme.colorScheme.onPrimary
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



@Preview(showBackground = true, uiMode = Configuration.UI_MODE_NIGHT_YES)
@Composable
fun RobotViewPreview(){
    DruidAppTheme{
        Surface(
            modifier = Modifier.fillMaxSize(),
            color = MaterialTheme.colorScheme.background
        ) {
            val vm: MainViewModel = viewModel()
            val navController = rememberNavController()
            RobotView(vm, navController)
        }
    }
}