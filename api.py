def call_gemini_api(model, conversation_history, tools=None):
    """
    A simple, centralized wrapper for generate_content to handle errors gracefully.
    """
    print("🧠 Gemini is thinking...")
    try:
        if tools:
            response = model.generate_content(conversation_history, tools=tools)
        else:
            response = model.generate_content(conversation_history)

        # Check for empty or invalid responses
        if not response or not response.parts:
            # This is a fallback, which should ideally be handled by a retry mechanism.
            return None

        return response
    except Exception as e:
        print(f"🔥 An error occurred during the API call: {e}")
        # Re-raising the exception allows the calling function to handle it,
        # for example, by attempting a retry.
        raise


def agentic_reason_and_act(model, conversation_history, tools):
    """
    The core of the agentic loop: reasons about the next action and executes it.

    1.  **Call Gemini API**: To decide the next step (either a tool call or a direct response).
    2.  **Parse Response**: Extract any function calls or textual content.
    3.  **Return Action**: Return the action to be executed by the agent loop.
    """
    response = call_gemini_api(model, conversation_history, tools=tools)

    if response is None:
        # If the API call fails, we return a text response to the user.
        return "The model did not return a response. Please try again.", None

    function_call = None
    text_content = ""

    # Check for function calls or text in the response parts
    for part in response.parts:
        if part.function_call:
            function_call = part.function_call
        if part.text:
            text_content += part.text

    # The "thought" is the textual explanation of the action being taken
    thought = text_content if text_content else "No thought was provided."

    # Prioritize function call over text response
    if function_call:
        return thought, function_call

    # If no function call, return the text content as the final response
    return thought, None
