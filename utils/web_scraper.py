import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def scrape_text(url: str) -> str:
    """
    Scrapes the text content from a given URL.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        return soup.get_text()
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"


def extract_links(html_content: str, base_url: str) -> list[str]:
    """
    Extracts all absolute links from HTML content.
    """
    links = set()
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            # Join with base URL to handle relative links
            absolute_url = urljoin(base_url, href)

            # Basic validation: must have scheme and netloc
            parsed = urlparse(absolute_url)
            if parsed.scheme in ["http", "https"] and parsed.netloc:
                links.add(absolute_url)
    except Exception:
        pass
    return list(links)
