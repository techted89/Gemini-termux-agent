import os
import sys
import shutil
import tempfile
import requests
import shlex
import google.generativeai as genai
from googleapiclient.discovery import build
from pypdf import PdfReader
import config
from helpers import run_command, user_confirm
from db import learn_directory, learn_file_content, learn_url

def google_search(query):
    """A tool that can search the web."""
    print(f"Tool: Running google_search(query=\"{query}\")")
    if not config.GOOGLE_API_KEY or config.GOOGLE_API_KEY == "YOUR_GOOGLE_SEARCH_API_KEY":
        return "Error: GOOGLE_API_KEY is not set in config.py."
    try:
        service = build("customsearch", "v1", developerKey=config.GOOGLE_API_KEY)
        res = service.cse().list(q=query, cx=config.CUSTOM_SEARCH_CX, num=3).execute()
        snippets = [f"Title: {item['title']}\nSnippet: {item['snippet']}\nSource: {item['link']}"
                    for item in res.get('items', [])]
        if not snippets: return "No search results found."
        return "\n---\n".join(snippets)
    except Exception as e:
        return f"Error during search: {e}"

def learn_pdf_task(filepath):
    """
    Loads a PDF, splits it into chunks, and learns the content of each chunk.
    """
    print(f"Tool: Running learn_pdf_task(filepath=\"{filepath}\")")
    try:
        reader = PdfReader(filepath)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                # Simple chunking by page
                learn_file_content(filepath, content=text, metadata={"source": filepath, "page_number": i + 1})
        return f"Successfully learned content from {len(reader.pages)} pages of {filepath}."
    except Exception as e:
        return f"Error learning PDF {filepath}: {e}"

def learn_repo_task(repo_url):
    """Wrapper for learn_repo to be called by the agent."""
    print(f"Tool: Running learn_repo_task(repo_url=\"{repo_url}\")")
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

def execute_puppeteer_script(url, action="screenshot", output_file="screenshot.png"):
    """
    Executes a Puppeteer script to automate a Chromium browser on Termux.
    Currently supports 'screenshot' and 'get_html' actions.
    """
    print(f"Tool: Running execute_puppeteer_script(url=\"{url}\", action=\"{action}\")")
    if user_confirm(f"Execute Puppeteer script for URL: {url} with action: {action}?"):
        script_content = f'''
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
'''
        # Create a temporary JavaScript file
        temp_js_path = os.path.join(tempfile.gettempdir(), "puppeteer_script.js")
        with open(temp_js_path, "w") as f:
            f.write(script_content)

        try:
            result = run_command(f"node {shlex.quote(temp_js_path)}", shell=True, check_output=True)
            return result
        except Exception as e:
            return f"Error executing Puppeteer script: {e}"
        finally:
            if os.path.exists(temp_js_path):
                os.remove(temp_js_path)
    return "Denied."

def huggingface_sentence_similarity(source_sentence, sentences_to_compare):
    """
    Calculates sentence similarity using the Hugging Face Inference API.

    This tool is useful for understanding the semantic relationship between sentences,
    which can be used for tasks like finding the most relevant piece of text.

    Args:
        source_sentence (str): The main sentence to compare against.
        sentences_to_compare (list[str]): A list of sentences to compare with the source.

    Returns:
        list[float]: A list of similarity scores, each corresponding to a sentence
                     in the `sentences_to_compare` list. Returns an error message on failure.
    """
    print(f"Tool: Running huggingface_sentence_similarity(source='{source_sentence}', sentences_to_compare={len(sentences_to_compare)})")

    if not config.HF_API_TOKEN or config.HF_API_TOKEN == "YOUR_HUGGINGFACE_API_TOKEN":
        return "Error: HF_API_TOKEN is not set in config.py. Please get a token from hf.co/settings/tokens."

    api_url = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
    headers = {"Authorization": f"Bearer {config.HF_API_TOKEN}"}

    payload = {
        "inputs": {
            "source_sentence": source_sentence,
            "sentences": sentences_to_compare
        }
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            scores = response.json()
            return f"Similarity scores: {scores}"
        else:
            return f"Error from Hugging Face API: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Error making request to Hugging Face API: {e}"

def web_interact_task(url, method="GET", data=None, headers=None):
    """Interacts with a URL using HTTP methods."""
    try:
        if method.upper() == "GET":
            res = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            res = requests.post(url, json=data, headers=headers)
        else:
            return f"Unsupported method: {method}"
        return f"Status: {res.status_code}\nContent: {res.text[:1000]}..."
    except Exception as e:
        return f"Error: {e}"

def scrape_search_engine_task(query, engine="google"):
    """Scrapes a search engine (simulated/fragile)."""
    # Just forward to google_search if engine is google, or generic scrape
    if engine == "google":
        return google_search(query)
    return f"Scraping {engine} for '{query}' is not fully implemented."

definitions = {
    "web_interact": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="web_interact", description="Interact with a URL (GET/POST).", parameters={"type": "object", "properties": {"url": {"type": "string"}, "method": {"type": "string"}, "data": {"type": "object"}, "headers": {"type": "object"}}, "required": ["url"]})]),
    "scrape_search_engine": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="scrape_search_engine", description="Scrape search engine results.", parameters={"type": "object", "properties": {"query": {"type": "string"}, "engine": {"type": "string"}}, "required": ["query"]})]),
    "google_search": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="google_search", description="Search web", parameters={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]})]),
    "learn_from_url_or_repo": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="learn_from_url_or_repo", description="Learn", parameters={"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]})]),
    "learn_pdf_task": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="learn_pdf_task", description="Learn from a PDF document.", parameters={"type": "object", "properties": {"filepath": {"type": "string"}}, "required": ["filepath"]})]),
    "execute_puppeteer_script": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="execute_puppeteer_script", description="Executes a Puppeteer script for browser automation (screenshot, get_html).", parameters={"type": "object", "properties": {"url": {"type": "string"}, "action": {"type": "string"}, "output_file": {"type": "string"}}, "required": ["url"]})]),
    "huggingface_sentence_similarity": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="huggingface_sentence_similarity", description="Calculates sentence similarity using the Hugging Face Inference API.", parameters={"type": "object", "properties": {"source_sentence": {"type": "string"}, "sentences_to_compare": {"type": "array", "items": {"type": "string"}}}, "required": ["source_sentence", "sentences_to_compare"]})]),
}
