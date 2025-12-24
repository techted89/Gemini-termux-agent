import google.generativeai as genai
from googleapiclient.discovery import build
import config


def google_search(query):
    """A tool that can search the web."""
    print(f'Tool: Running google_search(query="{query}")')
    if (
        not config.GOOGLE_API_KEY
        or config.GOOGLE_API_KEY == "YOUR_GOOGLE_SEARCH_API_KEY"
    ):
        return "Error: GOOGLE_API_KEY is not set in config.py."
    try:
        service = build("customsearch", "v1", developerKey=config.GOOGLE_API_KEY)
        res = service.cse().list(q=query, cx=config.CUSTOM_SEARCH_CX, num=3).execute()
        snippets = [
            f"Title: {item['title']}\nSnippet: {item['snippet']}\nSource: {item['link']}"
            for item in res.get("items", [])
        ]
        if not snippets:
            return "No search results found."
        return "\n---\n".join(snippets)
    except Exception as e:
        return f"Error during search: {e}"


tool_definitions = {
    "google_search": genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name="google_search",
                description="Search web",
                parameters={
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
            )
        ]
    ),
}
