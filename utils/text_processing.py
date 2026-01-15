import re


def extract_code_block(text: str) -> str:
    """
    Extracts the content of the first markdown code block in the text.

    Args:
        text (str): The input text containing markdown code blocks.

    Returns:
        str: The content of the code block. If no code block is found,
             returns the original text.
    """
    # Regex to capture content inside triple backticks
    # ```(?:[\w\+\-\.]+)?\s* -> Matches ``` followed by optional language
    # identifier and whitespace
    # (.*?) -> Captures the content (non-greedy)
    # ``` -> Matches closing ```
    # re.DOTALL ensures . matches newlines
    pattern = r"```(?:[\w\+\-\.]+)?\s*(.*?)```"
    match = re.search(pattern, text, re.DOTALL)

    if match:
        return match.group(1).strip()

    # If no match found via regex, check if the text *is* just a code block
    # but maybe malformed or just the content itself (fallback logic)
    # For now, we return the original text if no block is found,
    # as the user might have provided raw code without blocks.
    return text
