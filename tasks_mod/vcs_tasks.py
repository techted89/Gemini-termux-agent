from helpers import run_command, user_confirm
from api import call_gemini_api

def handle_git_commit(model, prompt):
    diff = run_command("git diff --staged", shell=True, check_output=True)
    if not diff:
        return "No changes staged."
    res = call_gemini_api(model, [f"User: {prompt}. Diff: {diff}. Write commit msg."])
    msg = res.text.strip()
    print(f"\nCommit Msg: {msg}")
    if user_confirm("Commit?"):
        run_command(f'git commit -m "{msg}"', shell=True)
        return "Committed."
    return "Cancelled."

def handle_gh_issue(model, repo, prompt):
    res = call_gemini_api(model, [f"User: {prompt}. Write GitHub issue title/body."])
    print(f"\nIssue:\n{res.text}")
    if user_confirm(f"Post to {repo}?"):
        run_command(
            f"gh issue create -R {repo} -t 'AI Issue' -b '{res.text}'", shell=True
        )
        return "Created."
    return "Cancelled."
