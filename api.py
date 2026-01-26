from google.genai import types
import time
import google.genai as genai

def agentic_reason_and_act(model_wrapper, history, tools=None):
    # Unwrap the Model
    model = model_wrapper.get('model', model_wrapper) if isinstance(model_wrapper, dict) else model_wrapper
    
    retries = 3
    for attempt in range(retries):
        try:
            response = model.generate_content(history, tools=tools)
            if not response.candidates: return "No response from model.", None

            content = response.candidates[0].content
            thought = ""
            function_call = None

            for part in content.parts:
                if part.text: thought += part.text
                if hasattr(part, 'function_call') and part.function_call:
                    function_call = part.function_call
            return thought, function_call

        except Exception as e:
            # Check for 429 or RESOURCE_EXHAUSTED
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                if attempt < retries - 1:
                    time.sleep(10)
                    continue
            # Re-raise if not handled or retries exhausted
            raise e

def call_gemini_api(model_wrapper, history):
    # Wrapper for simple calls, applying similar logic if needed, but keeping it simple for now as requested.
    model = model_wrapper.get('model', model_wrapper) if isinstance(model_wrapper, dict) else model_wrapper
    return model.generate_content(history)
