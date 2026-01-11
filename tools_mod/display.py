from google.genai import types as genai_types
from utils.display import display_image

def display_image_task(path):
    return display_image(path)

def tool_definitions():
    return [
        genai_types.Tool(
            function_declarations=[
                genai_types.FunctionDeclaration(
                    name="display_image",
                    description="Display an image.",
                    parameters=genai_types.Schema(
                        type=genai_types.Type.OBJECT,
                        properties={"path": genai_types.Schema(type=genai_types.Type.STRING)},
                        required=["path"],
                    ),
                )
            ]
        )
    ]
