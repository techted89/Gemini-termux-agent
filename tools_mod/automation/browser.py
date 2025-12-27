import os
import tempfile
import shlex
import google.genai as genai
from utils.commands import run_command, user_confirm


def execute_puppeteer_script(url, action="screenshot", output_file="screenshot.png"):
    """
    Executes a Puppeteer script to automate a Chromium browser on Termux.
    Currently supports 'screenshot' and 'get_html' actions.
    """
    print(f'Tool: Running execute_puppeteer_script(url="{url}", action="{action}")')

    # Check for node
    try:
        run_command("node -v", shell=True, check_output=True)
    except Exception:
        return "Error: Node.js is not installed. Please install it to use this tool."

    if user_confirm(f"Execute Puppeteer script for URL: {url} with action: {action}?"):
        script_content = f"""
try {{
    const puppeteer = require('puppeteer');

    (async () => {{
        const browser = await puppeteer.launch({{
            executablePath: '/data/data/com.termux/files/usr/bin/chromium',
            args: ['--no-sandbox']
        }});
        const page = await browser.newPage();
        await page.goto('{url}', {{waitUntil: 'networkidle2'}});

        if ("{action}" === "screenshot") {{
            await page.screenshot({{path: '{output_file}'}});
            console.log(`Screenshot saved to {output_file}`);
        }} else if ("{action}" === "get_html") {{
            const html = await page.content();
            console.log(html);
        }} else {{
            console.log(`Unknown action: {action}`);
        }}

        await browser.close();
    }})();
}} catch (error) {{
    if (error.code === 'MODULE_NOT_FOUND') {{
        console.error('Puppeteer is not installed. Please run "npm i puppeteer" to use this tool.');
    }} else {{
        console.error('An error occurred:', error);
    }}
    process.exit(1);
}}
"""
        # Create a temporary JavaScript file
        temp_js_path = os.path.join(tempfile.gettempdir(), "puppeteer_script.js")
        with open(temp_js_path, "w") as f:
            f.write(script_content)

        try:
            result = run_command(
                f"node {shlex.quote(temp_js_path)}", shell=True, check_output=True
            )
            return result
        except Exception as e:
            return f"Error executing Puppeteer script: {e}"
        finally:
            if os.path.exists(temp_js_path):
                os.remove(temp_js_path)
    return "Denied."


def execute_playwright_script(url, action="screenshot", output_file="screenshot.png"):
    """
    Executes a Playwright script to automate a Chromium browser on Termux.
    Currently supports 'screenshot' and 'get_html' actions.
    """
    print(f'Tool: Running execute_playwright_script(url="{url}", action="{action}")')

    # Check for node
    try:
        run_command("node -v", shell=True, check_output=True)
    except Exception:
        return "Error: Node.js is not installed. Please install it to use this tool."

    if user_confirm(f"Execute Playwright script for URL: {url} with action: {action}?"):
        script_content = f"""
try {{
    const {{ chromium }} = require('playwright');

    (async () => {{
        const browser = await chromium.launch({{
            executablePath: '/data/data/com.termux/files/usr/bin/chromium',
            args: ['--no-sandbox']
        }});
        const page = await browser.newPage();
        await page.goto('{url}', {{waitUntil: 'networkidle2'}});

        if ("{action}" === "screenshot") {{
            await page.screenshot({{path: '{output_file}'}});
            console.log(`Screenshot saved to {output_file}`);
        }} else if ("{action}" === "get_html") {{
            const html = await page.content();
            console.log(html);
        }} else {{
            console.log(`Unknown action: {action}`);
        }}

        await browser.close();
    }})();
}} catch (error) {{
    if (error.code === 'MODULE_NOT_FOUND') {{
        console.error('Playwright is not installed. Please run "npm i playwright" to use this tool.');
    }} else {{
        console.error('An error occurred:', error);
    }}
    process.exit(1);
}}
"""
        # Create a temporary JavaScript file
        temp_js_path = os.path.join(tempfile.gettempdir(), "playwright_script.js")
        with open(temp_js_path, "w") as f:
            f.write(script_content)

        try:
            result = run_command(
                f"node {shlex.quote(temp_js_path)}", shell=True, check_output=True
            )
            return result
        except Exception as e:
            return f"Error executing Playwright script: {e}"
        finally:
            if os.path.exists(temp_js_path):
                os.remove(temp_js_path)
    return "Denied."


tool_definitions = {
    "execute_puppeteer_script": genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name="execute_puppeteer_script",
                description="Executes a Puppeteer script for browser automation (screenshot, get_html).",
                parameters={
                    "type": "object",
                    "properties": {
                        "url": {"type": "string"},
                        "action": {"type": "string"},
                        "output_file": {"type": "string"},
                    },
                    "required": ["url"],
                },
            )
        ]
    ),
    "execute_playwright_script": genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name="execute_playwright_script",
                description="Executes a Playwright script for browser automation (screenshot, get_html).",
                parameters={
                    "type": "object",
                    "properties": {
                        "url": {"type": "string"},
                        "action": {"type": "string"},
                        "output_file": {"type": "string"},
                    },
                    "required": ["url"],
                },
            )
        ]
    ),
}
