import chromadb
import sys
import google.generativeai as genai
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from config import PROJECT_CONTEXT_IGNORE, CHROMA_HOST

try:
    if not CHROMA_HOST:
        print("Error: CHROMA_HOST not set")
        sys.exit(1)
    client = chromadb.HttpClient(host=CHROMA_HOST, port=8000)
    knowledge_collection = client.get_or_create_collection(name="knowledge")
    conversation_history_collection = client.get_or_create_collection(
        name="conversation_history"
    )
except Exception as e:
    print(f"DB Connection Failed: {e}")
    # Consider sys.exit(1) here if DB connection is critical for the whole script


def get_embedding(text, task_type="RETRIEVAL_DOCUMENT"):
    if not text.strip():
        return None
    try:
        res = genai.embed_content(
            model="models/text-embedding-004", content=text[:10000], task_type=task_type
        )
        return res["embedding"]
    except Exception as e: # Changed bare except to Exception
        print(f"Error getting embedding: {e}") # Added specific error logging
        return None


def learn_file_content(filepath):
    try:
        p = Path(filepath)
        if not p.is_file():
            return
        content = p.read_text(encoding="utf-8", errors="ignore")
        if len(content) > 15000 or not content.strip():
            return
        emb = get_embedding(content)
        if emb:
            knowledge_collection.upsert(
                embeddings=[emb],
                documents=[content],
                metadatas=[{"source": str(p.resolve())}],
                ids=[str(p.resolve())],
            )
            print(".", end="", flush=True)
    except Exception: # Changed bare except to Exception
        pass


def learn_directory(directory_path):
    print(f"Learning: {directory_path}", end="", flush=True)
    for p in Path(directory_path).rglob("*"):
        if any(x in p.parts for x in PROJECT_CONTEXT_IGNORE):
            continue
        if p.is_file() and p.suffix in [".py", ".js", ".txt", ".md"]:
            learn_file_content(p)
    print("\nDone.") # Fixed the syntax error here


def learn_url(url):
    try:
        print(f"Learning URL: {url}")
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        text = BeautifulSoup(res.text, "html.parser").get_text(
            separator=" ", strip=True
        )[:15000]
        emb = get_embedding(text)
        if emb:
            knowledge_collection.upsert(
                embeddings=[emb],
                documents=[text],
                metadatas=[{"source": url, "type": "url"}],
                ids=[url],
            )
            print(f"Learned URL: {url}") # Added confirmation print
    except Exception as e:
        print(f"Error learning URL {url}: {e}") # Enhanced error message


def get_relevant_context(prompt, n_results=5):
    try:
        emb = get_embedding(prompt, task_type="RETRIEVAL_QUERY")
        if not emb:
            return ""
        res = knowledge_collection.query(query_embeddings=[emb], n_results=n_results)
        if not res["documents"] or not res["documents"][0]:
            return ""
        ctx = "--- RELEVANT CONTEXT ---\n"
        for i, doc in enumerate(res["documents"][0]):
            source = res['metadatas'][0][i].get('source', 'Unknown') # Safely get source
            ctx += f"Source: {source}\nContent: {doc[:500]}...\n\n"
        return ctx
    except Exception as e: # Changed bare except to Exception
        print(f"Error retrieving context: {e}") # Added specific error logging
        return ""


def delete_knowledge(ids=None, where=None):
    """
    Deletes entries from the knowledge collection.
    Args:
        ids (list, optional): List of document IDs to delete.
        where (dict, optional): A ChromaDB filter dictionary to specify documents by metadata.
                                E.g., {"source": "some_path.py"}.
    Returns:
        bool: True if deletion was attempted, False if no IDs or filters were provided or an error occurred.
    """
    if not ids and not where:
        print("Warning: No IDs or 'where' clause provided for knowledge deletion.")
        return False
    try:
        knowledge_collection.delete(ids=ids, where=where)
        print(f"Knowledge deleted. IDs: {ids if ids else 'N/A'}, Where: {where if where else 'N/A'}")
        return True
    except Exception as e:
        print(f"Error deleting knowledge: {e}")
        return False


def delete_conversation_history(ids=None, where=None):
    """
    Deletes entries from the conversation history collection.
    Args:
        ids (list, optional): List of document IDs to delete.
        where (dict, optional): A ChromaDB filter dictionary to specify documents by metadata.
                                E.g., {"role": "user"}.
    Returns:
        bool: True if deletion was attempted, False if no IDs or filters were provided or an error occurred.
    """
    if not ids and not where:
        print("Warning: No IDs or 'where' clause provided for conversation history deletion.")
        return False
    try:
        conversation_history_collection.delete(ids=ids, where=where)
        print(f"Conversation history deleted. IDs: {ids if ids else 'N/A'}, Where: {where if where else 'N/A'}")
        return True
    except Exception as e:
        print(f"Error deleting conversation history: {e}")
        return False



from api import call_gemini_api
from tools import tool_definitions, execute_tool


def run_agent_step(
    models, history, user_input=None, print_func=print, verbose_mode=False
):
    """
    Executes a single step of the agent's turn.
    Returns (done, result_text, metadata).
    - done: True if the agent has finished processing (either responded with text or error), False if it made a tool call and needs to process the result.
    - result_text: The text output to be displayed to the user.
    - metadata: (Currently None, but can be used for more complex state/data in the future).
    """
    if user_input:
        history.append({"role": "user", "parts": [user_input]})

    try:
        response = call_gemini_api(
            models["tools"], history, tools=list(tool_definitions.values())
        )

        function_call, text_content = None, ""
        if response.parts:
            for part in response.parts:
                if hasattr(part, "function_call") and part.function_call:
                    function_call = part.function_call
                text_val = getattr(part, "text", None)
                if text_val:
                    text_content += text_val

        if function_call:
            # Add model's thought/call to history
            history.append({"role": "model", "parts": response.parts})

            if text_content and verbose_mode:
                print_func(f"🤖 {text_content}")

            # Execute tool
            print_func(f"⚙️ Tool: {function_call.name}")
            # Note: The `execute_tool` function might need the `models` dictionary
            # if tools themselves require access to different model configurations.
            tool_result = execute_tool(function_call, models)  # SYNC CALL

            # Add result to history
            history.append(
                {
                    "role": "function",
                    "parts": [
                        {
                            "function_response": {
                                "name": function_call.name,
                                "response": {"result": str(tool_result)},
                            }
                        }
                    ],
                }
            )
            print_func(
                f"✅ Result: {str(tool_result)[:100]}..."
            )  # Truncate for display
            return False, None, None  # Not done, as it needs to process the tool result

        elif text_content:
            history.append({"role": "model", "parts": [text_content]})
            return True, text_content, None  # Done, responded with text

        return (
            True,
            "⚠️ Agent returned empty response.",
            None,
        )  # Done, but with an empty response

    except Exception as e:
        return True, f"🔥 Error: {e}", None  # Done, due to an error


def handle_agent_task(models, initial_prompt, initial_context):
    """
    Handles a full agent task in a CLI loop.
    This replaces the previous handle_agent_task and process_agent_turn functions.
    """
    print("🤖 Agent mode. Type 'exit' to quit.")

    # Initialize history with the system prompt
    sys_prompt = f"You are a Termux AI Agent. Goal: {initial_prompt}"
    hist = [*initial_context, {"role": "user", "parts": [sys_prompt]}]

    # Initial kick-off for the agent to start working on the goal
    done = False
    while not done:
        done, res, _ = run_agent_step(models, hist)
        if res:
            print(f"🤖 {res}")

    # Main loop for user interaction and continued agent processing
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit"]:
                break

            # Process user input
            done, res, _ = run_agent_step(models, hist, user_input=user_input)
            if res:
                print(f"🤖 {res}")

            # Continue agent processing until it's "done" (either responded or errored)
            while not done:
                done, res, _ = run_agent_step(models, hist)
                if res:
                    print(f"🤖 {res}")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"🔥 An error occurred during user interaction: {e}")
            break



