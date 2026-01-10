AGENTS.MD: Advanced Gemini Termux Agent Configuration
Core Operating Principles
* Zero Regression Policy: You are strictly forbidden from simplifying, substituting, or using placeholders for any existing logic, features, or functions.
* Modular Object-Oriented Design: All code must be structured using deep Object-Oriented (OO) principles. Functions must be granular and modularized to the most basic level of utility.
* Non-Destructive Editing: You must never remove functionality. If a code block or feature must be replaced, you must:
  * Create a separate backup file for the old logic.
  * Use a versioned/timestamped naming system for the backup.
  * Maintain relative file pathing to ensure the agent's filesystem integrity is preserved.
The Development Workflow (:task:focus:)
Every interaction must explicitly state its current status using the header: Workflow State: :task:focus -> [Current Action].
Phase 1: Investigative Understanding
Before writing code, you must research the objective. If the task is to build a tool (e.g., file editing), do not build a single function. Investigate GitHub and web documentation to identify what constitutes a Complete Toolset.
* Example: A "File Edit" toolset must include: mkdir, copy, sed_edit, move, cat, stat, and chmod.
Phase 2: Planning & Logic Testing
* Develop a full functioning plan.
* For bug fixes: Research the error via search engines or GitHub issues first.
* Create a Custom Logic Test specific to the latest task to diagnose issues before implementation. Provide verbose output of the course of action and diagnosis.
Phase 3: Implementation & Verbose Reporting
* Code must be modularized and grouped in appropriately named files (e.g., filesystem_utils.py, api_automation.py) based on usage.
* If removing functionality is required for a specific task, you must provide a Verbose Statement justifying the removal and move the old code to a separate file with a relative path reference.
Communication & Clarification
* Systematic Checks: Systematically report on all possible updates or changes based on the development workflow.
* Mandatory Clarification: You are required to ask questions and clarify the goal before execution.
* Workflow Display: Always display verbose status, current progress, and the diagnostic path you are following.
Technical Constraints (Agent Logic)
* Context Awareness: Utilize the existing ChromaDB vector MMR metadata memory and short-term chat context (15-20 turns).
* Toolset Expansion: For features like Facehugger Transformer integrations or UI automation, ensure robust error handling and verbose logging for the Termux environment.
* Relative Pathing: Always use relative paths for internal code locations to ensure portability within the Termux filesystem.
