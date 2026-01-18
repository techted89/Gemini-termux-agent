import google.genai as genai
from googleapiclient.discovery import build
import config
from utils.web_scraper import scrape_text


def google_search(
    query: str,
    api_key: str = config.GOOGLE_API_KEY,
    cx: str = config.CUSTOM_SEARCH_CX,
    num: int = 5,
) -> str:
    """
    Perform a Google Custom Search and return the top results formatted for display.
    
    If the API key or Custom Search CX is missing or left as the placeholder values, the function returns an error string indicating the missing configuration.
    
    Parameters:
        query (str): The search query.
        api_key (str): Google API key (defaults to config.GOOGLE_API_KEY).
        cx (str): Custom Search Engine ID (defaults to config.CUSTOM_SEARCH_CX).
        num (int): Number of results to retrieve.
    
    Returns:
        str: Concatenated result entries where each entry includes `Title`, `URL`, and `Snippet` on separate lines, or an error string if configuration is missing.
    """
    if not api_key or api_key == "YOUR_GOOGLE_SEARCH_API_KEY":
        return "Error: GOOGLE_API_KEY is not configured."
    if not cx or cx == "YOUR_CUSTOM_SEARCH_CX":
        return "Error: CUSTOM_SEARCH_CX is not configured."
    service = build("customsearch", "v1", developerKey=api_key)
    res = (
        service.cse()
        .list(
            q=query,
            cx=cx,
            num=num,
        )
        .execute()
    )
    items = res.get("items", [])
    return "\n".join(
        [
            f"Title: {item['title']}\nURL: {item['link']}\nSnippet: {item['snippet']}\n"
            for item in items
        ]
    )


def tool_definitions():
    """
    Provide Tool metadata that declares the available tool functions for the AI interface.
    
    Each returned Tool contains FunctionDeclaration entries for:
    - `google_search`: performs a Google search and requires the `query` parameter.
    - `scrape_text`: scrapes text from a URL and requires the `url` parameter.
    
    Returns:
        list: A list of `genai.types.Tool` objects describing the available tool functions.
    """
    return [
        genai.types.Tool(
            function_declarations=[
                genai.types.FunctionDeclaration(
                    name="google_search",
                    description="Performs a Google search.",
                    parameters={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The search query."}
                        },
                        "required": ["query"],
                    },
                ),
                genai.types.FunctionDeclaration(
                    name="scrape_text",
                    description="Scrapes the text content from a given URL.",
                    parameters={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL to scrape.",
                            }
                        },
                        "required": ["url"],
                    },
                ),
            ]
        )
    ]

library = {
    "google_search": google_search,
    "scrape_text": scrape_text,
}
}
