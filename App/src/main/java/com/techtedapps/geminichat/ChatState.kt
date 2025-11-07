package com.techtedapps.geminichat

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
