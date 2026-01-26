import google.genai as genai
from googleapiclient.discovery import build
import requests
import os
import config
from utils.web_scraper import scrape_text


def google_search(
    query: str,
    api_key: str = config.GOOGLE_API_KEY,
    cx: str = config.CUSTOM_SEARCH_CX,
    num: int = 5,
) -> str:
    """
    Performs a Google search and returns the top results as a formatted string.
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

def download_file_task(url, filepath):
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        expanded_path = os.path.expanduser(filepath)
        with open(expanded_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return f"Downloaded {url} to {filepath}"
    except Exception as e:
        return f"Error downloading file: {e}"

def visit_page_task(url):
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error visiting page: {e}"

def tool_definitions():
    return [
        genai.types.Tool(
            function_declarations=[
                genai.types.FunctionDeclaration(
                    name="search_web", # Renamed/Aliased from google_search to match typical dispatcher expectations
                    description="Performs a Google search.",
                    parameters={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The search query."}
                        },
                        "required": ["query"],
                    },
                ),
                # Also keep google_search as alias? The prompt asked to rename OR add alias. Rename is cleaner.
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
                genai.types.FunctionDeclaration(
                    name="download_file",
                    description="Downloads a file from a URL to a local path.",
                    parameters={
                        "type": "object",
                        "properties": {
                            "url": {"type": "string"},
                            "filepath": {"type": "string"}
                        },
                        "required": ["url", "filepath"],
                    },
                ),
                genai.types.FunctionDeclaration(
                    name="visit_page",
                    description="Visits a webpage and returns the raw HTML content.",
                    parameters={
                        "type": "object",
                        "properties": {
                            "url": {"type": "string"}
                        },
                        "required": ["url"],
                    },
                ),
            ]
        )
    ]

library = {
    "search_web": google_search,
    "google_search": google_search, # Keep both in library for backward compat
    "scrape_text": scrape_text,
    "download_file": download_file_task,
    "visit_page": visit_page_task,
}
