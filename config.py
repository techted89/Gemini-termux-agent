import os


MODEL_NAME = "gemini-2.5-flash"
IMAGE_OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "gemini_generated_images")

SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

PROJECT_CONTEXT_IGNORE = [
    ".git",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    ".env",
    "package-lock.json",
    "yarn.lock",
    "venv",
    ".idea",
    ".vscode",
]

# VPS SSH Configuration
