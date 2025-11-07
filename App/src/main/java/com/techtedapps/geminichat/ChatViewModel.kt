package com.techtedapps.geminichat

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
