import os


MODEL_NAME = "gemini-2.5-flash"
IMAGE_OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "gemini_generated_images")
API_KEY = "AIzaSyA5cQDPLh-L35vdPYBe4DR0JMPP_B4L80I"

GOOGLE_API_KEY = "AIzaSyA5cQDPLh-L35vdPYBe4DR0JMPP_B4L80I"
CUSTOM_SEARCH_CX = "a7c8270384f8f4595"
CHROMA_HOST = "74.208.167.101"
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
VPS_USER = "root"
VPS_IP = "74.208.167.101"
VPS_SSH_KEY_PATH = os.path.join(os.path.expanduser("~"), ".ssh", "vps.pub")
VPS_SSH_COMMAND_TEMPLATE = "ssh -i {key_path} {user}@{ip} '{cmd}'"
