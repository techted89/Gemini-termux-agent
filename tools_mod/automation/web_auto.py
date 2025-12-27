import google.genai as genai
try:
    import uiautomator2 as u2
except ImportError:
    u2 = None
from utils.commands import user_confirm, run_command
import requests
from bs4 import BeautifulSoup


def web_navigate(url: str) -> str:
    """Navigates to a URL in the Chrome browser."""
    if u2 is None:
        return "uiautomator2 is not installed. Please install it with 'pip install uiautomator2'"
    try:
        d = u2.connect()
        # Use adb to start the browser with the given URL
        run_command(f"am start -a android.intent.action.VIEW -d {url} com.android.chrome", shell=True)
        return f"Navigated to {url}."
    except Exception as e:
        return f"Error navigating to URL: {e}"


def web_screenshot(output_file: str = "screenshot.png") -> str:
    """Takes a screenshot of the current view."""
    if u2 is None:
        return "uiautomator2 is not installed. Please install it with 'pip install uiautomator2'"
    try:
        d = u2.connect()
        d.screenshot(output_file)
        return f"Screenshot saved to {output_file}."
    except Exception as e:
        return f"Error taking screenshot: {e}"


def web_get_html(output_file: str = "web_content.html") -> str:
    """Gets the HTML content of the current web page."""
    if u2 is None:
        return "uiautomator2 is not installed. Please install it with 'pip install uiautomator2'"
    try:
        d = u2.connect()
        # Find the URL bar and get the URL
        url_bar = d(resourceId="com.android.chrome:id/url_bar")
        if not url_bar.exists:
            return "Error: Could not find the Chrome URL bar."
        url = url_bar.get_text()

        # Fetch the HTML content
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        with open(output_file, "w") as f:
            f.write(soup.prettify())
        return f"Web content saved to {output_file}."
    except Exception as e:
        return f"Error getting web content: {e}"


tool_definitions = {
    "web_navigate": genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name="web_navigate",
                description="Navigates to a URL in the Chrome browser.",
                parameters={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The URL to navigate to.",
                        }
                    },
                },
            )
        ]
    ),
    "web_screenshot": genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name="web_screenshot",
                description="Takes a screenshot of the current view.",
                parameters={
                    "type": "object",
                    "properties": {
                        "output_file": {
                            "type": "string",
                            "description": "The file to save the screenshot to.",
                        }
                    },
                },
            )
        ]
    ),
    "web_get_html": genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name="web_get_html",
                description="Gets the HTML content of the current web page.",
                parameters={
                    "type": "object",
                    "properties": {
                        "output_file": {
                            "type": "string",
                            "description": "The file to save the web content to.",
                        }
                    },
                },
            )
        ]
    ),
}
