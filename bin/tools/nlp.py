import google.generativeai as genai
import requests
from config import HF_API_TOKEN


def huggingface_sentence_similarity(source_sentence, sentences_to_compare):
    """
    Calculates sentence similarity using the Hugging Face Inference API.

    This tool is useful for understanding the semantic relationship between sentences,
    which can be used for tasks like finding the most relevant piece of text.

    Args:
        source_sentence (str): The main sentence to compare against.
        sentences_to_compare (list[str]): A list of sentences to compare with the source.

    Returns:
        list[float]: A list of similarity scores, each corresponding to a sentence
                     in the `sentences_to_compare` list. Returns an error message on failure.
    """
    print(
        f"Tool: Running huggingface_sentence_similarity(source='{source_sentence}', sentences_to_compare={len(sentences_to_compare)})"
    )

    if not HF_API_TOKEN or HF_API_TOKEN == "YOUR_HUGGINGFACE_API_TOKEN":
        return "Error: HF_API_TOKEN is not set in config.py. Please get a token from hf.co/settings/tokens."

    api_url = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

    payload = {
        "inputs": {
            "source_sentence": source_sentence,
            "sentences": sentences_to_compare,
        }
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            scores = response.json()
            return f"Similarity scores: {scores}"
        else:
            return (
                f"Error from Hugging Face API: {response.status_code} - {response.text}"
            )
    except requests.exceptions.RequestException as e:
        return f"Error making request to Hugging Face API: {e}"


tool_definitions = {
    "huggingface_sentence_similarity": genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name="huggingface_sentence_similarity",
                description="Calculates sentence similarity using the Hugging Face Inference API.",
                parameters={
                    "type": "object",
                    "properties": {
                        "source_sentence": {"type": "string"},
                        "sentences_to_compare": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["source_sentence", "sentences_to_compare"],
                },
            )
        ]
    ),
}
