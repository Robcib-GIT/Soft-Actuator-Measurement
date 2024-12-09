package com.tfm.druidapp

import android.content.res.Configuration
import android.widget.Toast
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.wrapContentWidth
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.DrawerValue
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalDrawerSheet
import androidx.compose.material3.ModalNavigationDrawer
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.rememberDrawerState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.tfm.druidapp.data.MainViewModel
import com.tfm.druidapp.ui.theme.DruidAppTheme
import com.tfm.druidapp.data.Screen
import com.tfm.druidapp.data.allScreens
import com.tfm.druidapp.views.customElements.BottomNavigationBar
import com.tfm.druidapp.views.customElements.TopBar
import com.tfm.druidapp.data.screensInDrawer
import com.tfm.druidapp.data.screensWithNav
import kotlinx.coroutines.launch

@Composable
fun App(viewModel: MainViewModel = viewModel()){
    val toastMessage by viewModel.toastMessage.collectAsState()
    val context = LocalContext.current

    // Muestra el Toast cuando el mensaje esté presente
    LaunchedEffect(toastMessage) {
        toastMessage?.let {
            Toast.makeText(context, it, Toast.LENGTH_SHORT).show()
            viewModel.clearToast()  // Limpia el mensaje después de mostrarlo
        }
    }

    val navController = rememberNavController()
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route ?: Screen.Monitoring.route
    val scope = rememberCoroutineScope()
    val drawerState = rememberDrawerState(initialValue = DrawerValue.Closed)

    val title = allScreens.firstOrNull { it.route == currentRoute }?.title ?: ""
    val isLoading by viewModel.loadingState.collectAsState()

    ModalNavigationDrawer(
        drawerState = drawerState,
        drawerContent = {
            ModalDrawerSheet(
                modifier = Modifier
                    .wrapContentWidth() //Ajusta el ancho dinámicamente al contenido
                    .fillMaxHeight(), // Ocupa todo el alto
                drawerContainerColor = MaterialTheme.colorScheme.primary
            ){
                //Text(text = "Holi") TODO añadir algun titulo
                LazyColumn(
                    modifier = Modifier.fillMaxWidth(0.7f),//wrapContentWidth(),
                    horizontalAlignment = Alignment.Start
                ){
                    items(screensInDrawer){ item->
                        DrawerItem(
                            selected = (currentRoute == item.route),
                            item = item
                        ){
                            //TODO navegar a la ventana que toque y cambiar a archivo separado
                        }


                    }
                }
            }
        }
    ){
        Scaffold(
        topBar = {
            TopBar(
                title = title,
                viewModel.connectionState.value,
                loading = isLoading,
                onNavigationClicked = {
                    if(screensWithNav.any{it.route == currentRoute} || screensInDrawer.any{it.route == currentRoute}){
                        scope.launch { drawerState.open() }
                    }else{
                        navController.popBackStack()
                    }
                },
                switchOffFunction = {viewModel.disconnectWebSocket()},
                switchOnFunction = {
                    viewModel.connectWebSocket()
                    viewModel.waitForConnection()
                }
            )
        },
        bottomBar = {
            if(screensWithNav.any{it.route == currentRoute}){
                BottomNavigationBar(currentRoute){ destinationScreen->
                    if (currentRoute != destinationScreen.route) { // Navegar solo si es diferente
                        navController.navigate(destinationScreen.route)
                    }
                }
            }else{
                null
            }

        }
        ) {paddingValues->
            Navigation(navController = navController ,viewModel = viewModel, pd = paddingValues)
        }
    }

}




@Composable
fun DrawerItem(
    selected: Boolean,
    item: Screen,
    onDrawerItemClicked: ()->Unit
){
    Row(
        modifier = Modifier
            .fillMaxWidth()//.wrapContentWidth()
            .clickable { onDrawerItemClicked() }
            .background(if(selected) Color(0xFF3B3D3D) else MaterialTheme.colorScheme.primary)
            .padding(vertical = 10.dp)
    ) {
        Icon(
            painter = painterResource(id = item.icon),
            contentDescription = item.title,
            modifier = Modifier.padding(start= 20.dp,end = 8.dp),
            tint = MaterialTheme.colorScheme.onPrimary

        )
        Text(
            text = item.title,
            style = MaterialTheme.typography.titleMedium,
            color = MaterialTheme.colorScheme.onPrimary
        )

    }

}

@Preview(showBackground = true, uiMode = Configuration.UI_MODE_NIGHT_YES)
@Composable
fun AppPreview(){
    DruidAppTheme {
        App()
    }
}