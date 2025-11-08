package com.techtedapps.geminichat.ui

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Slider
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

val availableModels = listOf(
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.0-flash"
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    onSave: (String, String, Float) -> Unit,
    apiKey: String,
    modelName: String,
    temperature: Float
) {
    val apiKeyState = remember { mutableStateOf(apiKey) }
    val modelNameState = remember { mutableStateOf(modelName) }
    val temperatureState = remember { mutableStateOf(temperature) }
    val expanded = remember { mutableStateOf(false) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        TextField(
            value = apiKeyState.value,
            onValueChange = { apiKeyState.value = it },
            label = { Text("API Key") }
        )
        Button(onClick = { expanded.value = !expanded.value }) {
            Text(modelNameState.value)
        }
        DropdownMenu(
            expanded = expanded.value,
            onDismissRequest = { expanded.value = false }
        ) {
            availableModels.forEach { model ->
                DropdownMenuItem(
                    text = { Text(model) },
                    onClick = {
                        modelNameState.value = model
                        expanded.value = false
                    }
                )
            }
        }
        Text("Temperature: ${temperatureState.value}")
        Slider(
            value = temperatureState.value,
            onValueChange = { temperatureState.value = it },
            valueRange = 0f..1f,
            steps = 10
        )
        Button(onClick = { onSave(apiKeyState.value, modelNameState.value, temperatureState.value) }) {
            Text("Save")
        }
    }
}
