package com.tfm.druidapp.views.customElements

import android.content.res.Configuration
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemColors
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.tooling.preview.Preview
import com.tfm.druidapp.data.Screen
import com.tfm.druidapp.data.screensWithNav
import com.tfm.druidapp.ui.theme.DruidAppTheme

@Composable
fun BottomNavigationBar(currentRoute: String, onItemSelected: (Screen) -> Unit){
    NavigationBar(
        containerColor = MaterialTheme.colorScheme.primary
    ) {
        screensWithNav.forEach { item->
            NavigationBarItem(
                selected = currentRoute==item.route,
                onClick = { onItemSelected(item) },
                icon = { Icon(painter = painterResource(id = item.icon), contentDescription = item.title) },
                label = {Text(text = item.title)},
                colors = NavigationBarItemColors(
                    selectedIndicatorColor = Color.Transparent,
                    selectedIconColor = MaterialTheme.colorScheme.onPrimary,
                    selectedTextColor = MaterialTheme.colorScheme.onPrimary,
                    unselectedIconColor = MaterialTheme.colorScheme.onPrimaryContainer,
                    unselectedTextColor = MaterialTheme.colorScheme.onPrimaryContainer,
                    disabledIconColor = MaterialTheme.colorScheme.onPrimaryContainer,
                    disabledTextColor = MaterialTheme.colorScheme.onPrimaryContainer
                )
            )
        }
    }
}

@Preview(showBackground = true, uiMode = Configuration.UI_MODE_NIGHT_YES)
@Composable
fun BottomNavigationBarPreview(){
    DruidAppTheme {
        BottomNavigationBar(currentRoute = Screen.Monitoring.route) { }
    }
}