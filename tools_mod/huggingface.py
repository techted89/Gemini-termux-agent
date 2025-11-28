import google.generativeai as genai

try:
    from transformers import pipeline
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False

def hf_local_inference_task(model_name, pipeline_task, input_text):
    if not HF_AVAILABLE:
        return "Error: 'transformers' library not installed. Please install it (e.g., `pip install transformers torch`)."

    try:
        # Initialize pipeline (this might download the model if not cached)
        print(f"Loading local model '{model_name}' for task '{pipeline_task}'...")
        pipe = pipeline(pipeline_task, model=model_name)
        result = pipe(input_text)
        return str(result)
    except Exception as e:
        return f"Error running local inference: {e}"

definitions = {
    "hf_local_inference": genai.types.Tool(function_declarations=[
        genai.types.FunctionDeclaration(
            name="hf_local_inference",
            description="Run a Hugging Face model locally using transformers pipeline.",
            parameters={
                "type": "object",
                "properties": {
                    "model_name": {"type": "string", "description": "The model ID (e.g., 'gpt2', 'distilbert-base-uncased')."},
                    "pipeline_task": {"type": "string", "description": "The task (e.g., 'text-generation', 'sentiment-analysis')."},
                    "input_text": {"type": "string", "description": "The input text for the model."}
                },
                "required": ["model_name", "pipeline_task", "input_text"]
            }
        )
    ])
}
