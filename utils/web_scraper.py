import requests
from bs4 import BeautifulSoup

def scrape_text(url: str) -> str:
    """
    Scrapes the text content from a given URL.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        soup = BeautifulSoup(response.content, "html.parser")
        return soup.get_text()
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"
