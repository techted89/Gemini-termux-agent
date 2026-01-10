from google.genai import types

def agentic_reason_and_act(model_wrapper, history, tools=None):
    response = model_wrapper.generate_content(history, tools=tools)
    if not response.candidates: return "No response from model.", None
    
    content = response.candidates[0].content
    thought = ""
    function_call = None

    for part in content.parts:
        if part.text: thought += part.text
        if hasattr(part, 'function_call') and part.function_call:
            function_call = part.function_call
    return thought, function_call

def call_gemini_api(model_wrapper, history):
    return model_wrapper.generate_content(history)