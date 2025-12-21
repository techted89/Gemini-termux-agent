import google.generativeai as genai
from utils.database import (
    search_and_delete_knowledge,
    search_and_delete_history,
    get_available_metadata_sources,
)

tool_definitions = {
    "search_and_delete_knowledge": genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name="search_and_delete_knowledge",
                description="Search/Del Knowledge",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "source": {"type": "string"},
                        "ids": {"type": "array", "items": {"type": "string"}},
                        "confirm": {"type": "boolean"},
                    },
                    "required": [],
                },
            )
        ]
    ),
    "search_and_delete_history": genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name="search_and_delete_history",
                description="Search/Del History",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "role": {"type": "string"},
                        "ids": {"type": "array", "items": {"type": "string"}},
                        "confirm": {"type": "boolean"},
                    },
                    "required": [],
                },
            )
        ]
    ),
    "get_available_metadata_sources": genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name="get_available_metadata_sources",
                description="Get available metadata sources for filtering.",
                parameters={"type": "object", "properties": {}},
            )
        ]
    ),
}
