import google.genai as genai
try:
    import uiautomator2 as u2
except ImportError:
    u2 = None
from utils.commands import user_confirm


def open_app(package_name: str) -> str:
    """Opens an app using uiautomator2."""
    if u2 is None:
        return "uiautomator2 is not installed. Please install it with 'pip install uiautomator2'"
    try:
        d = u2.connect()
        d.app_start(package_name)
        return f"App {package_name} started."
    except Exception as e:
        return f"Error opening app with uiautomator2: {e}"


def android_ui_find_and_tap_text(text: str, timeout: int = 10) -> str:
    """Finds and taps on a UI element with the given text."""
    if u2 is None:
        return "uiautomator2 is not installed. Please install it with 'pip install uiautomator2'"
    try:
        d = u2.connect()
        d(text=text).click(timeout=timeout)
        return f"Tapped on text: {text}"
    except Exception as e:
        return f"Error finding and tapping text: {e}"


def android_ui_long_press_text(text: str, duration: int = 1) -> str:
    """Finds and long presses on a UI element with the given text."""
    if u2 is None:
        return "uiautomator2 is not installed. Please install it with 'pip install uiautomator2'"
    try:
        d = u2.connect()
        d(text=text).long_click(duration=duration)
        return f"Long pressed on text: {text}"
    except Exception as e:
        return f"Error long pressing text: {e}"

def extract_text_from_screen():
    """
    Dumps the UI hierarchy and extracts all text elements.
    """
    if u2 is None:
        return "uiautomator2 is not installed. Please install it with 'pip install uiautomator2'"
    try:
        d = u2.connect()
        xml_dump = d.dump_hierarchy()

        # A simple regex to find text attributes in the XML dump.
        # This is a basic implementation and might not cover all cases.
        import re
        text_elements = re.findall(r'text="([^"]*)"', xml_dump)

        return "\n".join(text_elements)
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
                    "properties": {
                        "package_name": {
                            "type": "string",
                            "description": "The package name of the app to open.",
                        }
                    },
                },
            )
        ]
    ),
    "android_ui_find_and_tap_text": genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name="android_ui_find_and_tap_text",
                description="Finds and taps on a UI element with the given text.",
                parameters={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The text to find and tap.",
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "The timeout in seconds to wait for the element.",
                        },
                    },
                },
            )
        ]
    ),
    "android_ui_long_press_text": genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name="android_ui_long_press_text",
                description="Finds and long presses on a UI element with the given text.",
                parameters={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The text to find and long press.",
                        },
                        "duration": {
                            "type": "integer",
                            "description": "The duration of the long press in seconds.",
                        },
                    },
                },
            )
        ]
    ),
    "extract_text_from_screen": genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name="extract_text_from_screen",
                description="Extracts all text elements from the current screen.",
                parameters={"type": "object", "properties": {}},
            )
        ]
    ),
}
