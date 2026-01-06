import os

# Gemini API Key
API_KEY = os.environ.get("GEMINI_API_KEY", "")

# ChromaDB Configuration
CHROMA_HOST = "localhost"
CHROMA_PORT = 8000

# Google Custom Search API Configuration
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
CUSTOM_SEARCH_CX = os.environ.get("CUSTOM_SEARCH_CX", "")

# Hugging Face API Token (for Inference API)
HF_API_TOKEN = os.environ.get("HF_API_TOKEN", "")

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
VPS_IP = "74.208.167.101"
VPS_USER = "user"
VPS_SSH_KEY_PATH = "~/.ssh/id_rsa"
