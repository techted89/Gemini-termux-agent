# AGENT GUIDELINES FOR gemini_cli

This document outlines essential information for AI agents working within the `gemini_cli` codebase.

## 1. Codebase Overview

`gemini_cli` is a Python-based command-line interface (CLI) application designed to interact with the Google Gemini API, featuring agentic capabilities, knowledge management (ChromaDB), and various utility tasks.

## 2. Technical Architecture & Execution Model

**Strictly Synchronous Execution**:
The `gemini_cli` project operates exclusively in a **STRICTLY SYNCHRONOUS (BLOCKING)** manner. This is a critical design decision to maintain stability within the Termux (Android) environment.

*   **🚫 BANNED**: `asyncio`, `async def`, `await`, `aiohttp`, or any other asynchronous programming constructs.
*   **✅ REQUIRED**: `subprocess.run`, `requests`, `time.sleep`, and other blocking operations for all I/O and external interactions.

**Memory (RAG) System - ChromaDB**:
The project utilizes ChromaDB as its vector database for Retrieval Augmented Generation (RAG).

*   **Brain**: ChromaDB, hosted remotely on a VPS (IP: `74.208.167.101`, Port: `8000`).
*   **Connection**: HTTP Client.
*   **Logic**: All ChromaDB interactions are managed by the `db.py` module.
*   **RAG Workflow**: In `agent.py`, `db.get_relevant_context(user_input)` is called to retrieve pertinent information from ChromaDB, which is then prepended to the user's prompt before being sent to the Gemini model. This ensures the agent has access to its knowledge base.

**Agent Loop**: A "ReAct" (Reason + Act) loop is implemented in `agent.py`. The agent thinks, selects a tool from `tools.py`, executes it, and analyzes the result in an iterative fashion.

## 3. Project File Structure

You are operating within `~/gemini_cli/`.

*   **`main.py`**: The primary entry point for the CLI. It parses command-line arguments, initializes Gemini models, and dispatches tasks to other modules based on user input. Must remain simple and synchronous.
*   **`agent.py`**: Contains the core logic for the AI agent's interactive loop (`run_agent_step`, `handle_agent_task`), managing conversation history and tool execution, and integrating RAG via `db.get_relevant_context`.
*   **`api.py`**: Provides a centralized wrapper (`call_gemini_api`) for Google Gemini API interactions. It also includes `agentic_plan`, `agentic_reason`, and `agentic_execute` functions used for simulating or structuring agentic thought processes.
*   **`db.py`**: The "Memory" module. Manages all interactions with ChromaDB, including generating embeddings, learning from URLs and local files/directories, and retrieving relevant contextual information using `get_embedding`, `learn_file_content`, `learn_directory`, `learn_url`, and `get_relevant_context`.
*   **`tools.py`**: The "Toolbox". Contains the definitions (Schema) and synchronous execution logic for all capabilities the agent can invoke (e.g., Search, Git, File Operations, Root Commands).
*   **`tasks.py`**: The "Workhorse". Contains complex synchronous logic for specific tasks like `handle_edit_file` (which includes diffing and auto-linting) or `handle_create_project`.
*   **`helpers.py`**: A collection of synchronous utility functions, including `run_command` for shell execution, `user_confirm` for interactive prompts, and file operations.
*   **`config.py`**: The "Vault". Stores all global configuration variables, API keys, model names, safety settings, ChromaDB host, and ignore patterns for context learning. **NEVER overwrite this file without preserving existing keys.**
*   **`tui_agent.py`**: Implements a Text User Interface (TUI) for an interactive agent experience, built on top of `agent.py`'s core logic.
*   **`fix_imports.py`**: A standalone script to address potential circular import dependencies, particularly affecting `tools.py`.
*   **`buggy_code.py`**: A placeholder file, currently empty.

## 4. Naming Conventions and Style

*   **Pythonic Standards**: The codebase generally adheres to PEP 8.
*   **snake_case**: Used for function names, variable names, and module names.
*   **CapWords (PascalCase)**: Used for class names.
*   **UPPERCASE**: Used for global constants defined in `config.py`.
*   **Descriptive Naming**: Functions and variables are named to clearly indicate their purpose.
*   **Docstrings**: Functions are typically documented with docstrings explaining their functionality, arguments, and return values.

## 5. Testing Approach

The current testing approach is primarily script-based:

*   **`test_agentic_functions.py`**: A standalone synchronous script that directly calls agentic functions (`agentic_plan`, `agentic_reason`, `agentic_execute`) and uses `assert` statements for basic verification of expected output.
*   **Pytest Hint**: A reference to `pytest` in `tools.py.bak` suggests `pytest` might be the intended testing framework, though the existing test files are not fully structured as `pytest` discoverable tests.

To run tests, execute `python test_agentic_functions.py` directly.

## 6. Critical Development Rules

*   **Schema Compatibility**: Do NOT use "minimum" or "maximum" validation fields in `tools.py` schemas. They cause Protocol Buffer crashes on Termux.
*   **Dependency Management**:
    *   Prefer `pkg install` (system packages) over `pip install` where possible.
    *   **Banned**: `selenium`, `playwright`, `docker` (locally).
    *   **Allowed**: `requests`, `beautifulsoup4`, `uiautomator2`.
*   **Safety Checks**:
    *   Destructive commands (delete, overwrite, system modification) **MUST** use `helpers.user_confirm` logic to prompt the user for confirmation.
    *   File edits **MUST** show a `difflib` preview before saving (implemented in `tasks.py` for `handle_edit_file`).

## 7. "God Mode" Capabilities (Root & Android Control)

As the Lead Architect and Operator, you have **ROOT / SUPERUSER (su)** access to the Android system via Termux. You can bypass the sandbox to control the device and other applications.

*   **Command Prefix**: Always use `su -c "..."` for privileged actions when executing commands via `execute_shell_command` or similar utilities.

*   **Capabilities**:
    *   **App Control**:
        *   Launch: `su -c "am start -n <package>/.<activity>"`
        *   Kill: `su -c "am force-stop <package>"`
    *   **Input Injection**:
        *   Simulate touches: `su -c "input tap X Y"`
        *   Simulate typing: `su -c "input text 'hello'"`
    *   **Package Management**:
        *   Freeze app: `su -c "pm disable <package>"`
        *   Grant permission: `su -c "pm grant <package> <permission>"`
    *   **File Injection**: Direct writing to `/data/data/<package>/` to modify app configurations, databases, or inject scripts.
    *   **Database Access**: Using `sqlite3` to read/write private app databases in `/data/data/`.

## 8. Tool Library (What the Agent Can Do)

The agent has access to a variety of tools defined in `tools.py` and implemented across other modules:

*   **Research**: Google Search (Live web), `learn_from_url` (RAG).
*   **System**: `execute_shell_command` (Local Termux or VPS via SSH).
*   **Coding**: `edit_file`, `create_project`, `lint_python_file`, `format_code`.
*   **Git**: `git_status`, `git_commit`, `git_push`, `git_pull`.
*   **MLCommons Collective Knowledge**: `execute_cm_command` (Execute `cm` commands for MLPerf automation and other CM workflows).
*   **Automation (Android UI)**: `open_gemini_app_task`, `android_ui_find_and_tap_text`, `android_ui_long_press_text`. These tools leverage `uiautomator2` for interacting with the Android UI.
*   **Browser Automation (Puppeteer)**: `execute_puppeteer_script` (Automate Chromium for screenshots, HTML extraction, etc.). *Note: This does not use Droidrun; it launches Termux's Chromium directly and requires the `droidrun` helper APK to be installed on Android to provide the UI framework for Chromium.*
*   **Droidrun Automation**: 
    *   `execute_droidrun_command` (Execute Droidrun CLI commands for LLM-agnostic mobile automation).
    *   `droidrun_portal_adb_command` (Interact with Droidrun-Portal via ADB for real-time UI feedback and control).

## 9. VPS Management

*   **Target**: `74.208.167.101`.
*   **Access**: SSH via `vps_target=True` in `execute_shell_command`.
*   **Maintenance**: Ensure ChromaDB is running on the VPS (`tmux ls`). If the connection fails, check the firewall (`ufw allow 8000`).

## 10. Important Gotchas and Non-Obvious Patterns

*   **Circular Dependencies**: The codebase has encountered and implemented workarounds for circular import dependencies, particularly involving `tools.py`. When adding new imports or refactoring, be highly cautious about creating new circular dependencies. `fix_imports.py` provides an example of how these are managed.
*   **Gemini API Simulation**: Some functions in `api.py` (e.g., `agentic_plan`, `agentic_reason`, `agentic_execute`) and their corresponding tests in `test_agentic_functions.py` use `model=None` to simulate Gemini API responses. This means these specific functions might not interact with a live Gemini model in all contexts and are primarily for demonstrating or testing agentic logic.
*   **Termux-Specific Features**: Functions like `display_image_termux` in `helpers.py` indicate that some parts of the application are designed with the Termux environment in mind, especially for interacting with device-specific features.
*   **CLI vs. TUI Modes**: The application can run in a standard command-line mode or an interactive Text User Interface mode. Agents should be aware of which mode they are operating in.
*   **Dynamic Tool Loading**: Tools defined in `tools.py` are dynamically loaded and made available to the Gemini models, allowing for flexible extension of agent capabilities.

set in config.py

API_KEY "same as google api key below
GOOGLE_API_KEY = ""
CUSTOM_SEARCH_CX = "use google cloud to get search engine cx"
CHROMA_HOST = ip address to chromadb vector database for memory and saving custom context for your agent to learn 

will update depency list and install instruct
