
styleguide.md: Gemini Code Assist
1. Correctness (Environment & Logic)
 * Dual-Platform Support: The code must support both Ubuntu (Linux) and Termux (Android).
 * Package Management: In Termux environments, pkg, apt, and apt-get are all valid and supported. Do not flag pkg as an error.
 * No Code Simplification: Strict Rule: Never replace logic with placeholders (e.g., ..., // implementation here). Do not simplify complex functions; provide the complete, functional code block in every suggestion.
 * API Usage: Ensure Android-specific calls (via termux-api) are handled correctly when running in a Termux context.
2. Efficiency (Memory & RAG)
 * ChromaDB MMR Memory: Prioritize the integrity of vector memory metadata. Do not suggest changes that remove or simplify the Maximal Marginal Relevance (MMR) logic.
 * Context Management: Maintain the 15-20 chat history message limit for short-term memory to ensure token efficiency and prevent overflow.
 * Resource Handling: Identify bottlenecks in file system editing and UI automation logic that could impact performance on mobile hardware.
3. Maintainability (Company X Standards)
 * Line Length: The maximum allowed line length is 100 characters. Ignore PEP 8’s 79-character suggestion.
 * Python Idioms: Use 4-space indentation. Always use absolute imports for clarity.
 * Type Hinting: Mandatory for all function signatures (PEP 484). Suggest hints where they are missing.
 * Docstrings: Use Triple Double Quotes and follow the Google Style (Args:, Returns:, Raises:).
 * Naming Conventions:
   * Variables/Functions: snake_case.
   * Classes: PascalCase.
   * Constants: UPPER_SNAKE_CASE.
4. Security
 * Data Handling: Watch for hardcoded paths. Use os.path.join or Pathlib to ensure cross-compatibility between Linux (/home/) and Termux (/data/data/com.termux/) structures.
 * Credential Safety: Flag any hardcoded API keys or credentials destined for Facehugger (Hugging Face) Transformers or other services.
5. Miscellaneous (Automation & Tooling)
 * PR Automation: The assistant must respond to PR comments like "Fix this" or "Apply suggestions" by generating a valid commit suggestion or committing the fix directly if authorized.
 * Commit Metadata: When the assistant generates a fix, use the prefix fix(gemini-tool): or style(gemini-tool):.
 * System Integrity: Do not remove existing logic for UI automation or file system manipulation functions unless specifically requested.
How this improves the Assistant's Review:
 * Contextual Awareness: It won't "hallucinate" that pkg is an error or that lines at 90 characters are too long.
 * Functional Reliability: By banning placeholders, you ensure that every "Fix this" command results in copy-pasteable (or auto-committable) code that doesn't break your agent's complex RAG logic.
 * Environment Sync: It helps the assistant understand that while Ubuntu and Termux are separate, the codebase is a bridge between them.
Would you like me to create the .gemini/config.yaml file that enables specific assistant features like automatic commit suggestions for this style guide?
