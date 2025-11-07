#!/bin/bash

# --- File Creation Script for Gemini Chat App ---

# Define the base paths
BASE_DIR="app/src/main"
JAVA_DIR="$BASE_DIR/java/com/example/geminichat"
UI_DIR="$JAVA_DIR/ui"
GRADLE_DIR="App"

echo "Creating directory structure: $GRADLE_DIR and $JAVA_DIR..."
# Create all necessary nested directories in one command
mkdir -p $GRADLE_DIR
mkdir -p $UI_DIR

echo "Writing App/build.gradle.kts..."
cat << 'EOF_GRADLE' > $GRADLE_DIR/build.gradle.kts
plugins {
    alias(libs.plugins.androidApplication)
    alias(libs.plugins.kotlinAndroid)
}

android {
    namespace = "com.example.geminichat"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.geminichat"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables {
            useSupportLibrary = true
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }
    kotlinOptions {
        jvmTarget = "1.8"
    }
    buildFeatures {
        compose = true
    }
    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.1"
    }
    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}

dependencies {
    # AndroidX & Compose
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.activity.compose)
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.ui)
    implementation(libs.androidx.ui.graphics)
    implementation(libs.androidx.ui.tooling.preview)
    implementation(libs.androidx.material3)

    # Gemini SDK (Assuming version 1.26.0 as of late 2025)
    # NOTE: You must include your GEMINI_API_KEY in a local.properties file or Gradle property.
    implementation("com.google.genai:google-genai:1.26.0")

    # ViewModel utilities
    implementation(libs.androidx.lifecycle.viewmodel.compose)
}
EOF_GRADLE

echo "Writing app/src/main/AndroidManifest.xml..."
cat << 'EOF_MANIFEST' > $BASE_DIR/AndroidManifest.xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <!-- REQUIRED PERMISSION: Allows the app to open network sockets for API communication -->
    <uses-permission android:name="android.permission.INTERNET" />

    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.GeminiChat">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:theme="@style/Theme.GeminiChat">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

</manifest>
EOF_MANIFEST

echo "Writing Model.kt (with permissive safety settings)..."
cat << 'EOF_MODEL' > $JAVA_DIR/Model.kt
package com.example.geminichat

import com.google.genai.client.GenerativeModel
import com.google.genai.common.HarmBlockThreshold
import com.google.genai.common.HarmCategory
import com.google.genai.common.SafetySetting

/**
 * Singleton object to configure and provide the GenerativeModel instance.
 *
 * This configuration applies highly permissive safety settings as requested (BLOCK_NONE for all categories).
 */
object Model {
    # Placeholder for your API Key. It should be securely provided, e.g., via BuildConfig.
    private const val API_KEY = "YOUR_GEMINI_API_KEY"

    # Configuration to ensure "no restrictions" by setting all major harm categories to BLOCK_NONE.
    private val permissiveSafetySettings = listOf(
        # Set all core harm categories to BLOCK_NONE to disable filtering at the API level.
        SafetySetting(HarmCategory.HARASSMENT, HarmBlockThreshold.BLOCK_NONE),
        SafetySetting(HarmCategory.HATE_SPEECH, HarmBlockThreshold.BLOCK_NONE),
        SafetySetting(HarmCategory.SEXUALLY_EXPLICIT, HarmBlockThreshold.BLOCK_NONE),
        SafetySetting(HarmCategory.DANGEROUS_CONTENT, HarmBlockThreshold.BLOCK_NONE),
    )

    /**
     * Initializes the GenerativeModel with the 'gemini-2.5-flash' model
     * and the permissive safety settings.
     */
    val generativeModel: GenerativeModel = GenerativeModel(
        modelName = "gemini-2.5-flash",
        apiKey = API_KEY, # Replace with your actual API key access method (e.g., BuildConfig)
        config = com.google.genai.client.GenerateContentConfig(
            safetySettings = permissiveSafetySettings
        )
    )
}
EOF_MODEL

echo "Writing ChatState.kt..."
cat << 'EOF_STATE' > $JAVA_DIR/ChatState.kt
package com.example.geminichat

/**
 * Represents a single message in the chat.
 * @param text The content of the message.
 * @param isUser True if the message was sent by the user, false for the model/system.
 */
data class Message(
    val text: String,
    val isUser: Boolean,
)

/**
 * Represents the entire state of the chat UI.
 * This is used by the ViewModel to expose data to the Composable screen.
 *
 * @param messages The list of all messages in the conversation.
 * @param isLoading True if waiting for a response from the model.
 * @param input The current text in the user input field.
 */
data class ChatState(
    val messages: List<Message> = emptyList(),
    val isLoading: Boolean = false,
    val input: String = ""
)
EOF_STATE

echo "Writing ChatViewModel.kt..."
cat << 'EOF_VIEWMODEL' > $JAVA_DIR/ChatViewModel.kt
package com.example.geminichat

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.google.genai.client.GenerativeModel
import com.google.genai.common.Content
import com.google.genai.common.Role
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

/**
 * ViewModel to handle chat logic, state, and API calls.
 */
class ChatViewModel(
    private val model: GenerativeModel = Model.generativeModel
) : ViewModel() {

    private val _uiState = MutableStateFlow(ChatState())
    val uiState: StateFlow<ChatState> = _uiState

    // Tracks the current conversation history for context
    private val chatHistory = mutableListOf<Content>()

    /**
     * Updates the user's input text as they type.
     */
    fun updateInput(newInput: String) {
        _uiState.update { it.copy(input = newInput) }
    }

    /**
     * Sends the current user message to the Gemini API and streams the response.
     */
    fun sendMessage() {
        val userMessage = _uiState.value.input.trim()
        if (userMessage.isEmpty()) return

        // 1. Prepare UI for sending message
        _uiState.update {
            it.copy(
                messages = it.messages + Message(userMessage, isUser = true),
                input = "", // Clear the input field
                isLoading = true
            )
        }

        // 2. Add user content to history
        val userContent = Content(role = Role.USER, parts = listOf(com.google.genai.common.Part.text(userMessage)))
        chatHistory.add(userContent)

        // 3. Start streaming the API response
        viewModelScope.launch {
            try {
                // Add an initial empty message for the model's response
                val initialBotMessage = Message(text = "", isUser = false)
                _uiState.update { it.copy(messages = it.messages + initialBotMessage) }

                // Get a reference to the message that will be streamed into
                val currentMessageIndex = _uiState.value.messages.lastIndex

                val stream = model.generateContentStream(chatHistory)
                val fullResponse = StringBuilder()

                stream.collect { chunk ->
                    // Append the chunk text to the message
                    val latestText = chunk.text
                    fullResponse.append(latestText)

                    // Update the last message in the list with the accumulated text
                    _uiState.update { currentState ->
                        val updatedMessages = currentState.messages.toMutableList()
                        updatedMessages[currentMessageIndex] = updatedMessages[currentMessageIndex].copy(text = fullResponse.toString())
                        currentState.copy(messages = updatedMessages)
                    }
                }

                // 4. Update chat history with the model's final response
                val modelContent = Content(role = Role.MODEL, parts = listOf(com.google.genai.common.Part.text(fullResponse.toString())))
                chatHistory.add(modelContent)

            } catch (e: Exception) {
                // Handle any API or network errors
                _uiState.update { currentState ->
                    val errorMsg = "Error: Could not connect to Gemini API. Check your API key and network connection. (${e.message})"
                    val updatedMessages = currentState.messages.toMutableList()
                    // Replace or append the error message
                    if (updatedMessages.isNotEmpty() && !updatedMessages.last().isUser) {
                        updatedMessages[updatedMessages.lastIndex] = updatedMessages.last().copy(text = errorMsg)
                    } else {
                        updatedMessages.add(Message(errorMsg, isUser = false))
                    }
                    currentState.copy(messages = updatedMessages)
                }
                e.printStackTrace()
            } finally {
                _uiState.update { it.copy(isLoading = false) }
            }
        }
    }
}
EOF_VIEWMODEL

echo "Writing ChatScreen.kt (Jetpack Compose UI)..."
cat << 'EOF_SCREEN' > $UI_DIR/ChatScreen.kt
package com.example.geminichat.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.wrapContentWidth
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Send
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.geminichat.ChatState
import com.example.geminichat.ChatViewModel
import com.example.geminichat.Message
import com.example.geminichat.ui.theme.GeminiChatTheme

/**
 * Main composable function for the Chat UI.
 */
@Composable
fun ChatScreen(viewModel: ChatViewModel = viewModel()) {
    # Collect the UI state as a Compose State
    val state by viewModel.uiState.collectAsState()
    val listState = rememberLazyListState()

    # Scroll to the latest message whenever the message list updates
    LaunchedEffect(state.messages.size) {
        if (state.messages.isNotEmpty()) {
            listState.animateScrollToItem(state.messages.lastIndex)
        }
    }

    Surface(
        modifier = Modifier.fillMaxSize(),
        color = MaterialTheme.colorScheme.background
    ) {
        Column(modifier = Modifier.fillMaxSize()) {
            # 1. Message List
            LazyColumn(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth()
                    .padding(horizontal = 8.dp),
                state = listState,
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                item { Spacer(modifier = Modifier.height(8.dp)) } # Top padding
                items(state.messages) { message ->
                    MessageBubble(message)
                }
                item {
                    if (state.isLoading && state.messages.lastOrNull()?.isUser == true) {
                        LoadingIndicator()
                    }
                    Spacer(modifier = Modifier.height(8.dp)) # Bottom padding
                }
            }

            # 2. Input Bar
            InputBar(
                input = state.input,
                onInputChange = viewModel::updateInput,
                onSend = viewModel::sendMessage,
                isLoading = state.isLoading
            )
        }
    }
}

@Composable
fun MessageBubble(message: Message) {
    val bubbleColor = if (message.isUser) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.surfaceVariant
    val textColor = if (message.isUser) MaterialTheme.colorScheme.onPrimary else MaterialTheme.colorScheme.onSurfaceVariant
    val alignment = if (message.isUser) Alignment.CenterEnd else Alignment.CenterStart

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(
                start = if (message.isUser) 64.dp else 8.dp,
                end = if (message.isUser) 8.dp else 64.dp
            ),
        horizontalArrangement = if (message.isUser) Arrangement.End else Arrangement.Start
    ) {
        Box(
            modifier = Modifier
                .wrapContentWidth(align = alignment.horizontal)
                .background(
                    color = bubbleColor,
                    shape = RoundedCornerShape(12.dp)
                )
                .padding(12.dp)
        ) {
            Column {
                Text(
                    text = if (message.isUser) "You" else "Gemini",
                    style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold),
                    color = if (message.isUser) MaterialTheme.colorScheme.onPrimary.copy(alpha = 0.8f) else MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.8f)
                )
                Text(
                    text = message.text,
                    color = textColor,
                    style = MaterialTheme.typography.bodyLarge,
                    modifier = Modifier.padding(top = 4.dp)
                )
            }
        }
    }
}

@Composable
fun InputBar(
    input: String,
    onInputChange: (String) -> Unit,
    onSend: () -> Unit,
    isLoading: Boolean
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(MaterialTheme.colorScheme.surface)
            .padding(8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        OutlinedTextField(
            value = input,
            onValueChange = onInputChange,
            label = { Text("Ask Gemini...") },
            modifier = Modifier.weight(1f),
            shape = RoundedCornerShape(28.dp),
            singleLine = true,
            enabled = !isLoading # Disable input while loading
        )
        IconButton(
            onClick = onSend,
            enabled = input.isNotBlank() && !isLoading,
            modifier = Modifier
                .padding(start = 8.dp)
                .background(
                    color = if (input.isNotBlank() && !isLoading) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.surfaceVariant,
                    shape = RoundedCornerShape(50)
                )
                .size(56.dp)
        ) {
            Icon(
                imageVector = Icons.Filled.Send,
                contentDescription = "Send Message",
                tint = if (input.isNotBlank() && !isLoading) MaterialTheme.colorScheme.onPrimary else Color.Gray
            )
        }
    }
}

@Composable
fun LoadingIndicator() {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp),
        horizontalArrangement = Arrangement.Start
    ) {
        CircularProgressIndicator(
            modifier = Modifier.size(24.dp),
            color = MaterialTheme.colorScheme.primary
        )
        Text(
            text = "Gemini is thinking...",
            modifier = Modifier.padding(start = 8.dp),
            style = MaterialTheme.typography.bodyMedium,
            color = Color.Gray
        )
    }
}

@Preview(showBackground = true)
@Composable
fun PreviewChatScreen() {
    GeminiChatTheme {
        Column(Modifier.fillMaxSize()) {
            MessageBubble(Message("Hello! What can I help you with today?", false))
            MessageBubble(Message("Can you tell me a story about a space pirate?", true))
            MessageBubble(Message("The notorious Captain Vira, with a glint of starlight in her eyes...", false))
        }
    }
}
EOF_SCREEN

echo "Writing MainActivity.kt..."
cat << 'EOF_MAIN' > $JAVA_DIR/MainActivity.kt
package com.example.geminichat

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import com.example.geminichat.ui.ChatScreen
import com.example.geminichat.ui.theme.GeminiChatTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            GeminiChatTheme {
                // A surface container using the 'background' color from the theme
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    ChatScreen()
                }
            }
        }
    }
}
EOF_MAIN

echo "---"
echo "✅ Script complete. All files created under the ./app directory structure."
echo "REMINDER: Before running, open 'app/src/main/java/com/example/geminichat/Model.kt' and replace 'YOUR_GEMINI_API_KEY' with your actual API key."

