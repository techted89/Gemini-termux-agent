# Gemini CLI Agent for Ubuntu Linux

This document provides instructions for setting up and running the `gemini_cli` application on an Ubuntu Linux environment.

## 1. Codebase Overview

`gemini_cli` is a Python-based command-line interface (CLI) application designed to interact with the Google Gemini API. It features agentic capabilities, knowledge management with ChromaDB, and various utility tasks.

## 2. Technical Architecture

**Synchronous Execution**: The project operates in a strictly synchronous (blocking) manner to ensure stable and predictable behavior.

**RAG System**: The application uses a Retrieval Augmented Generation (RAG) system with ChromaDB as the vector database. All ChromaDB interactions are managed by the `db.py` module.

## 3. Installation

Follow these steps to set up the `gemini_cli` agent on your Ubuntu system.

**Prerequisites**:
* Ubuntu Linux
* Python 3.10 or higher
* `git`

**Step 1: Clone the Repository**
```bash
git clone <repository_url>
cd gemini_cli
```

**Step 2: Install System Dependencies**
Run the `install_dependencies.sh` script to install `pip` and other required system-level packages.
```bash
bash install_dependencies.sh
```

**Step 3: Install Python Packages**
```bash
pip install -r requirements.txt
```
This will install all the required Python packages.

**Step 4: Configure API Keys**
You need to configure your API keys in the `config.py` file.

1.  Open `config.py` in a text editor.
2.  Set the values for the following variables:
    *   `API_KEY`: Your Google API key.
    *   `GOOGLE_API_KEY`: Same as `API_KEY`.
    *   `CUSTOM_SEARCH_CX`: Your Google Custom Search Engine ID.
    *   `CHROMA_HOST`: The IP address of your ChromaDB instance.

## 4. Usage

To run the agent, execute the `main.py` script from the command line:

```bash
python main.py <command> [options]
```

For example, to start the agent in interactive mode, you might use a command like:
```bash
python main.py agent --prompt "Hello, how can you help me today?"
```
Refer to the application's help message for a full list of commands and options.
```bash
python main.py --help
```

## 5. Project File Structure

*   **`main.py`**: The primary entry point for the CLI.
*   **`agent.py`**: Contains the core logic for the AI agent's interactive loop.
*   **`api.py`**: A wrapper for Google Gemini API interactions.
*   **`db.py`**: Manages all interactions with ChromaDB.
*   **`tools_mod/`**: Contains the definitions and logic for all tools the agent can use.
*   **`tasks_mod/`**: Contains logic for complex, multi-step tasks.
*   **`utils/`**: A collection of utility functions.
*   **`config.py`**: Stores all global configuration variables and API keys.
*   **`tui_agent.py`**: Implements the Text User Interface (TUI) for an interactive agent experience.
