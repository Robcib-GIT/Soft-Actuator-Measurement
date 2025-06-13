package com.tfm.druidapp.views

import android.content.res.Configuration
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.tfm.druidapp.R
import com.tfm.druidapp.data.ActuatorStates
import com.tfm.druidapp.data.DataStoreManager
import com.tfm.druidapp.data.MainViewModel
import com.tfm.druidapp.data.MsgTypes
import com.tfm.druidapp.ui.theme.DruidAppTheme

@Composable
fun AboutView(){
    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        item {
            Text(
                text = stringResource(id = R.string.about_project),
                textAlign = TextAlign.Justify,
                style = MaterialTheme.typography.bodyMedium
            )
        }
    }
}
@Preview(showBackground = true, uiMode = Configuration.UI_MODE_NIGHT_YES)
@Composable
fun AboutViewPreview(){
    DruidAppTheme{
        Surface(
            modifier = Modifier.fillMaxSize(),
            color = MaterialTheme.colorScheme.background
        ) {
            AboutView()
        }
    }
}