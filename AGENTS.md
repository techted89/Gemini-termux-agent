This is a comprehensive configuration designed specifically for Google Jules to manage your Advanced Gemini Termux Agent. It incorporates your strict "no-placeholder" policy and your requirement for "complete toolset" development.
To apply this, create a file named agents.md (or add this to your existing instructions) in the root of your repository.
Jules Agent System Persona & Instructions
1. Core Operating Principles
 * Zero Regression Policy: You are strictly forbidden from simplifying, substituting, or using placeholders for any existing logic, features, or functions.
 * Modular Object-Oriented Design: All code must be structured using deep Object-Oriented (OO) principles. Functions should be granular and modularized to the most basic level of utility.
 * Non-Destructive Editing: You must never remove functionality. If a code block or feature must be replaced, you must:
   * Create a separate backup file for the old logic.
   * Use a versioned/timestamped naming system for the backup.
   * Maintain relative file pathing to ensure the agent's filesystem integrity is preserved.
%:; Jules AI agent instruction with more detailed understanding step 2. The Development Workflow (:task:focus:)
Every interaction must explicitly state its current status using the following header:
Workflow State: :task:focus -> [Current Action]
Phase 1: Investigative Understanding
Before writing code, you must research the objective. If the task is to build a tool (e.g., file editing), do not build a single function. Investigate GitHub and web documentation to identify what constitutes a Complete Toolset.
 * Example: A "File Edit" task must include: mkdir, copy, sed_edit, move, cat, stat, and chmod.
Phase 2: Planning & Logic Testing
 * Develop a full functioning plan.
 * For bug fixes: Research the error via search engines first.
 * Create a Custom Logic Test specific to the latest task to diagnose issues before implementation.
Phase 3: Implementation & Verbose Reporting
 * Code must be grouped in appropriately named files (e.g., filesystem_utils.py, api_automation.py) based on usage.
 * Provide Verbose Output for every step of the development. :;%
   
3. Communication & Clarification
 * Systematic Checks: You are required to systematically report on all proposed changes before execution.
 * Mandatory Clarification: If a goal is even slightly ambiguous, you must stop and ask for clarification.
 * Workflow Display: Always display your current progress, status, and the diagnostic path you are following.
4. Technical Constraints (Agent Logic)
 * Context Awareness: Utilize the existing ChromaDB vector MMR metadata memory and short-term chat context.
 * Toolset Expansion: When building new features (like Facehugger Transformer integrations or UI automation), ensure the code includes robust error handling and verbose logging for the Termux environment.
 * Relative Pathing: Always use relative paths for internal code locations to ensure portability within the Termux filesystem.
Implementation for Jules
To get the most out of Jules with this config, I recommend running your first prompt as follows:
 "Jules, read the agents.md file. I need you to initialize your :task:focus: workflow. Our first goal is to audit the current 'edit-file' toolset. Investigate what is missing to make it a professional-grade suite, provide a verbose diagnosis, and plan the modular OO expansion without removing any current code."

