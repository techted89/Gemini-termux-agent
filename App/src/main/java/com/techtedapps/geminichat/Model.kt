package com.techtedapps.geminichat

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
