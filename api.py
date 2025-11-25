import re

def call_gemini_api(model, conversation_history, tools=None):
    """A simple, centralized wrapper for generate_content to handle errors."""
    if model is None:
        # Simulate a response for agentic functions when model is None
        last_user_message = (
            conversation_history[-1]["parts"][0]["text"]
            if conversation_history and conversation_history[-1]["parts"]
            else "No user message."
        )
        return type(
            "Response",
            (object,),
            {
                "text": f"[SIMULATED RESPONSE for: {last_user_message}]",
                "prompt_feedback": type(
                    "PromptFeedback", (object,), {"safety_ratings": []}
                ),
            },
        )()

    print("\nGemini thinking...")
    try:
        # Note: model is expected to be None and conversation_history a simple list of messages
        # for these specific agentic functions as per the current simulated setup.

        # This part assumes model.generate_content would eventually be called
        # with a valid model instance and a proper conversation_history.
        # For the current simulation, if model is None, this call will fail.
        # The prompt indicates this needs refinement if functions become integrated with actual model calls.
        # Temporarily, we will assume this part might need to be adjusted or that
        # `model` will be provided by an outer scope in a real scenario.
        # Given the prompt, the primary change is how `conversation_history` is constructed.

        # For the purpose of just satisfying the signature, we'll keep the structure
        # but acknowledge 'model' will be None.
        # In a real scenario, if `model` is None, `model.generate_content` would raise an AttributeError.
        # The prompt asks to pass `None` for `model`, indicating the actual API call
        # with a real model object is not expected to happen in the current simulated context
        # when these specific agentic functions call `call_gemini_api`.
        # For the purpose of *this* instruction, we're not changing `call_gemini_api` itself,
        # but how its arguments are prepared.

        # If `model` is truly None here, the subsequent line will fail.
        # This implementation assumes that `model` will * eventually * be provided or
        # that `call_gemini_api` will be mocked or adjusted later.
        # For now, we will keep the original `call_gemini_api` logic and let the
        # AttributeError occur if `model` is truly None as per the prompt's instruction.
        if tools:
            return model.generate_content(conversation_history, tools=tools)
        else:
            return model.generate_content(conversation_history)
    except Exception as e:
        print(f"\nAn error occurred during API call: {e}")
        # This is the 'Blob' error fix. We now raise the error
        # to be handled by the agent loop, which will then retry.
        raise e


def agentic_plan(prompt, model=None, tools=None):
    """
    Formulates a detailed plan based on a prompt, explicitly outlining steps
    including potential tool usage like google_search for information gathering.
    The plan is returned as a structured string describing the sequence of actions.
    """
    print("\nAgentic planning...")
    plan_steps = []

    # Check if google_search is among the *declared* tools to include in the plan
    google_search_declared = False
    if tools:
        # Handle both dictionaries and lists of tools
        tool_iterator = tools.values() if isinstance(tools, dict) else tools
        for tool_spec in tool_iterator:
            if (
                hasattr(tool_spec, "function_declarations")
                and tool_spec.function_declarations
            ):
                for func_decl in tool_spec.function_declarations:
                    if func_decl.name == "google_search":
                        google_search_declared = True
                        break
            if google_search_declared:
                break

    plan_steps.append(f"1. Understand the goal: '{prompt}'.")

    if google_search_declared:
        search_query = f"information related to '{prompt}'"
        plan_steps.append(
            f"2. Gather initial information using google_search with query: '{search_query}'."
        )
        plan_steps.append(
            "3. Analyze search results to refine understanding and identify key areas."
        )
    else:
        plan_steps.append(
            "2. Proceed with internal knowledge, as google_search is not available."
        )

    plan_steps.append(
        "4. Develop a detailed strategy based on gathered information/internal knowledge."
    )
    plan_steps.append("5. Break down the strategy into actionable sub-tasks.")
    plan_steps.append(
        "6. Outline potential execution steps and necessary tools for each sub-task."
    )

    plan_output = "Agentic Plan:\n" + "\n".join(plan_steps)

    return plan_output


def agentic_reason(plan, model=None, tools=None):
    """
    Simulates the agent's reasoning process by taking a plan and elaborating on it,
    breaking it down into smaller steps, identifying necessary resources, or suggesting
    specific tool invocations.
    """
    print("\nAgentic reasoning...")

    reasoning_prompt_text = (
        f"Given the plan: '{plan}', "
        "elaborate on it by breaking it down into more granular, actionable steps. "
        "For each step, identify specific tools (e.g., google_search, read_file, execute_shell_command) "
        "that would be most suitable for execution. "
        "Also, consider any potential challenges or assumptions related to each step."
    )

    reasoning_conversation = [
        {"role": "user", "parts": [{"text": reasoning_prompt_text}]}
    ]

    response = call_gemini_api(model, reasoning_conversation, tools=tools)

    if response and hasattr(response, "text"):
        return response.text
    else:
        return "No detailed reasoning could be generated."


def agentic_execute(action, model=None, tools=None):
    """
    Simulates the execution of a specific action, detailing the likely outcome,
    especially if the action involves known tools like google_search or shell commands.
    """
    print("\nAgentic execution...")

    execution_description_parts = [
        f"The agent is executing the following action: '{action}'.",
        "Simulated outcome:",
    ]

    action_lower = action.lower()

    if (
        "google search" in action_lower
        or "search for" in action_lower
        or "look up" in action_lower
    ):
        search_query = action_lower.replace("google search for ", "").strip("'")
        execution_description_parts.append(
            f"  - Initiated a Google search for: '{search_query}'. "
            "Expected results would include relevant web pages and documentation."
        )
    elif "read file" in action_lower or "read content of" in action_lower:
        filepath = (
            action_lower.replace("read file", "").replace("read content of", "").strip().strip("'")
        )
        execution_description_parts.append(
            f"  - Attempted to read file: '{filepath if filepath else 'specified file'}'. "
            "Content would be loaded into context for analysis."
        )
    elif "execute shell command" in action_lower or "run command" in action_lower:
        command = (
            action_lower.replace("execute shell command", "")
            .replace("run command", "")
            .strip()
        )
        execution_description_parts.append(
            f"  - Executed shell command: '{command if command else 'specified command'}'. "
            "Output would vary based on the command and system state."
        )
    elif "create file" in action_lower or "make file" in action_lower:
        filename = (
            action_lower.replace("create file", "").replace("make file", "").strip()
        )
        execution_description_parts.append(
            f"  - Created file: '{filename if filename else 'new file'}'. "
            "File would be empty or contain initial content as specified."
        )
    elif "edit file" in action_lower:
        filepath = action_lower.replace("edit file", "").strip()
        execution_description_parts.append(
            f"  - Opened file for editing: '{filepath if filepath else 'specified file'}'. "
            "Changes would be applied based on the edit prompt."
        )
    else:
        execution_description_parts.append(
            f"  - Performed general action '{action}'. "
            "The outcome is a direct result of this specific action."
        )

    execution_prompt_text = "\n".join(execution_description_parts)

    execution_conversation = [
        {"role": "user", "parts": [{"text": execution_prompt_text}]}
    ]

    response = call_gemini_api(model, execution_conversation, tools=tools)

    if response and hasattr(response, "text"):
        return response.text
    else:
        return "No execution outcome could be generated for this action."
