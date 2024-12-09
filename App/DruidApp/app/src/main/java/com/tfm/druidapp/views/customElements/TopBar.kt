package com.tfm.druidapp.views.customElements

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Menu
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.colorResource
import androidx.compose.ui.unit.dp
import com.tfm.druidapp.R
import com.tfm.druidapp.data.screensWithNav

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TopBar(
    title: String,
    robotConnected: Boolean,
    loading: Boolean,
    onNavigationClicked: ()->Unit,
    switchOffFunction: ()->Unit,
    switchOnFunction: ()->Unit
){
    TopAppBar(
        title = {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.Center
            ) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.headlineLarge,
                    color = MaterialTheme.colorScheme.onPrimary
                )
            }
        },
        colors = TopAppBarDefaults.topAppBarColors(
            containerColor = MaterialTheme.colorScheme.primary
        ),
        navigationIcon = {
            IconButton(
                onClick = {
                    onNavigationClicked()
                },
                modifier = Modifier.padding(start = 8.dp)
            ) {
                if(screensWithNav.any {it.title == title}){
                    Icon(
                        imageVector = Icons.Default.Menu,
                        contentDescription = "Open drawer",
                        modifier = Modifier.size(30.dp)
                    )
                }else{
                    Icon(
                        imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                        contentDescription = "Go Back",
                        modifier = Modifier.size(30.dp)
                    )
                }
            }

        },
        actions = {
            Row(
                modifier = Modifier
                    .padding(end = 6.dp)
                    .size(24.dp),
                horizontalArrangement = Arrangement.Center,
                verticalAlignment = Alignment.CenterVertically
            ) {
                if(loading){
                    CircularProgressIndicator(
                        color = MaterialTheme.colorScheme.onPrimary,
                        modifier = Modifier.size(20.dp)
                    )
                }else{
                    IconButton(
                        onClick = {
                            if (robotConnected){
                                //TODO abrir advertencia
                                switchOffFunction()
                            }else{
                                switchOnFunction()
                            }
                        }
                    ){
                        Box(
                            modifier = Modifier
                                .size(15.dp) // Tamaño del círculo
                                .clip(CircleShape) // Forma circular
                                .background(
                                    if (robotConnected) colorResource(id = R.color.GreenBulb)
                                    else colorResource(id = R.color.RedBulb)
                                )
                        )
                    }
                }
            }



        }

    )
}