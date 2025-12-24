from utils.commands import run_command, user_confirm
from api import call_gemini_api
import os
import config

def handle_git_commit(model, prompt=None):
    diff = run_command("git diff --cached", check_output=True)
    if not diff:
        return "No changes staged for commit. Use 'git add' to stage your changes."

    commit_prompt = (
        f"Based on the following git diff, generate a concise and descriptive commit message. "
        f"The message should follow conventional commit standards.\n\n"
        f"DIFF:\n---\n{diff}\n---\n"
    )

    if prompt:
        commit_prompt += f"USER HINT: {prompt}\n\n"

    commit_prompt += "COMMIT MESSAGE:"

    commit_message = call_gemini_api(
        model, [{"role": "user", "parts": [commit_prompt]}]
    ).text.strip()

    print(
        f"--- SUGGESTED COMMIT MESSAGE ---\n{commit_message}\n------------------------------"
    )

    if user_confirm("Use this commit message?"):
        # The commit message might have multiple lines, so we need to handle it carefully
        # We can save it to a temp file and use git commit -F <file>
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
            tmp.write(commit_message)
            tmp_path = tmp.name

        try:
            run_command(f"git commit -F {tmp_path}")
            return "Commit successful."
        finally:
            os.unlink(tmp_path)

    return "Commit cancelled."


def handle_gh_issue(model, repo, prompt):
    # This is a placeholder for a more complex GitHub integration
    # For now, it will just generate a comment based on the prompt
    comment_prompt = (
        f"Generate a GitHub issue comment for '{repo}' based on the prompt: '{prompt}'"
    )
    comment = call_gemini_api(model, [{"role": "user", "parts": [comment_prompt]}]).text

    print(f"--- GENERATED COMMENT ---\n{comment}\n-------------------------")
    if user_confirm("Post this comment?"):
        # Here you would add the actual GitHub API call
        return "Comment posted (simulation)."
    return "Comment discarded."
