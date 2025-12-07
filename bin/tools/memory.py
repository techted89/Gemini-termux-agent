import google.generativeai as genai
import tempfile
from pypdf import PdfReader
from utils.database import learn_directory, learn_file_content
from utils.commands import run_command


def learn_pdf_task(filepath):
    """
    Loads a PDF, splits it into chunks, and learns the content of each chunk.
    """
    print(f'Tool: Running learn_pdf_task(filepath="{filepath}")')
    try:
        reader = PdfReader(filepath)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                # Simple chunking by page
                learn_file_content(
                    filepath,
                    content=text,
                    metadata={"source": filepath, "page_number": i + 1},
                )
        return f"Successfully learned content from {len(reader.pages)} pages of {filepath}."
    except Exception as e:
        return f"Error learning PDF {filepath}: {e}"


def learn_repo_task(repo_url):
    """Wrapper for learn_repo to be called by the agent."""
    print(f'Tool: Running learn_repo_task(repo_url="{repo_url}")')
    if not (repo_url.startswith("http") and repo_url.endswith(".git")):
        return "Error: Agent passed an invalid .git URL"
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"Cloning {repo_url} into {temp_dir}...")
            run_command(f"git clone --depth 1 {repo_url} {temp_dir}", shell=True)
            print("Clone complete. Learning from directory...")
            learn_directory(temp_dir)
            return "Learning complete. Temporary directory auto-cleaned."
    except Exception as e:
        return f"Error during repo learning: {e}"


tool_definitions = {
    "learn_from_url_or_repo": genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name="learn_from_url_or_repo",
                description="Learn",
                parameters={
                    "type": "object",
                    "properties": {"url": {"type": "string"}},
                    "required": ["url"],
                },
            )
        ]
    ),
    "learn_pdf_task": genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name="learn_pdf_task",
                description="Learn from a PDF document.",
                parameters={
                    "type": "object",
                    "properties": {"filepath": {"type": "string"}},
                    "required": ["filepath"],
                },
            )
        ]
    ),
}
