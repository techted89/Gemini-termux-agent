import os
import re
import json
import PIL.Image
import io
import datetime
import config
from helpers import run_command, user_confirm, save_to_file, display_image_termux
from api import call_gemini_api

def handle_image_generation(model, prompt):
    res = call_gemini_api(model, [prompt])
    if res.parts:
        img_data = next((p for p in res.parts if p.inline_data), None).inline_data.data
        path = os.path.join(
            config.IMAGE_OUTPUT_DIR, f"gen_{datetime.datetime.now().timestamp()}.png"
        )
        os.makedirs(config.IMAGE_OUTPUT_DIR, exist_ok=True)
        PIL.Image.open(io.BytesIO(img_data)).save(path)
        display_image_termux(path)
        return f"Saved to {path}"
    return "No image."

def handle_edit_file(model, filepath, prompt, save_as=None, conversation_history=None):
    try:
        with open(os.path.expanduser(filepath), "r") as f:
            content = f.read()
    except Exception as e:
        return f"Error: {e}"

    prompt_txt = f"Edit this file: {prompt}\nFile:\n{content}"
    hist = (conversation_history or []) + [{"role": "user", "parts": [prompt_txt]}]
    res = call_gemini_api(model, hist)

    new_content = res.text.strip()
    if user_confirm(f"Overwrite {filepath}?"):
        save_to_file(os.path.expanduser(save_as or filepath), new_content)
        return "File saved."
    return "Cancelled."

def handle_create_project(model, prompt, conversation_history=None):
    prompt_txt = f"Create project files: {prompt}. Wrap in --- START: name --- ... --- END: name ---"
    hist = (conversation_history or []) + [{"role": "user", "parts": [prompt_txt]}]
    res = call_gemini_api(model, hist)
    files = re.findall(
        r"--- START: (.*?) ---\n(.*?)\n--- END: \1 ---", res.text, re.DOTALL
    )
    if not files:
        return "No files parsed."
    if user_confirm(f"Create {len(files)} files?"):
        for name, content in files:
            save_to_file(name.strip(), content.strip())
        return "Created."
    return "Cancelled."

def handle_install(model, prompt):
    res = call_gemini_api(
        model, [f"Suggest install cmd for: {prompt}. Return JSON with manager/package."]
    )
    try:
        j = json.loads(re.search(r"\{.*\}", res.text, re.DOTALL).group(0))
        cmd = f"{j['manager']} install {j['package']}"
        if user_confirm(f"Run {cmd}?"):
            run_command(cmd, shell=True)
            return "Installed."
    except Exception:
        pass
    return "Failed."
