import google.generativeai as genai
import uiautomator2 as u2
from utils.commands import user_confirm


def open_app(package_name):
    """Opens an app using uiautomator2."""
    try:
        d = u2.connect()
        d.app_start(package_name, stop=True)
        return f"Successfully opened the app with package name: {package_name}"
    except Exception as e:
        return f"Error opening app with uiautomator2: {e}"


def tap_text(text, timeout=10):
    """Finds a UI element by text and taps it."""
    try:
        d = u2.connect()
        if d(text=text).wait(timeout=timeout * 1000):
            d(text=text).click()
            return f"Successfully tapped element with text: {text}"
        else:
            return (
                f"Error: Element with text '{text}' not found within {timeout} seconds."
            )
    except Exception as e:
        return f"Error finding and tapping element by text: {e}"


def long_press_text(text, duration=1.0, timeout=10):
    """Finds a UI element by text and performs a long press on it."""
    try:
        d = u2.connect()
        if d(text=text).wait(timeout=timeout * 1000):
            d(text=text).long_click(duration=duration)
            return f"Successfully long-pressed element with text: {text} for {duration} seconds"
        else:
            return (
                f"Error: Element with text '{text}' not found within {timeout} seconds."
            )
    except Exception as e:
        return f"Error long-pressing element by text: {e}"

def extract_text_from_screen():
    """Extracts all visible text from the screen."""
    try:
        d = u2.connect()
        xml = d.dump_hierarchy()
        # Parse XML to extract text attribute from all nodes
        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml)
        texts = []
        for elem in root.iter():
            text = elem.get('text')
            if text:
                texts.append(text)
        return "\n".join(texts)
    except Exception as e:
        return f"Error extracting text from screen: {e}"


tool_definitions = {
    "open_app": genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name="open_app",
                description="Opens an app using uiautomator2.",
                parameters={
                    "type": "object",
                    "properties": {"package_name": {"type": "string"}},
                    "required": ["package_name"],
                },
            )
        ]
    ),
    "tap_text": genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name="tap_text",
                description="Finds a UI element by text and taps it.",
                parameters={
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "timeout": {"type": "number", "format": "float"},
                    },
                    "required": ["text"],
                },
            )
        ]
    ),
    "long_press_text": genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name="long_press_text",
                description="Finds a UI element by text and performs a long press on it.",
                parameters={
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "duration": {"type": "number", "format": "float"},
                        "timeout": {"type": "number", "format": "float"},
                    },
                    "required": ["text"],
                },
            )
        ]
    ),
    "extract_text_from_screen": genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name="extract_text_from_screen",
                description="Extracts all visible text from the screen.",
                parameters={
                    "type": "object",
                    "properties": {},
                },
            )
        ]
    ),
}
