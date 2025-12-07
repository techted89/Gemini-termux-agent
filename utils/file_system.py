from pathlib import Path


def save_to_file(filename, content):
    """Saves content to a file."""
    try:
        p = Path(filename)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
        return f"\nSuccessfully saved content to: {filename}"
    except Exception as e:
        return f"Error saving file: {e}"
