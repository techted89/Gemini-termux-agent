import chromadb
import config

try:
    print(f"Connecting to ChromaDB at {config.CHROMA_HOST}:{config.CHROMA_PORT}...")
    client = chromadb.HttpClient(host=config.CHROMA_HOST, port=config.CHROMA_PORT)
    print("Connection to ChromaDB successful.")

    print("Existing collections:", client.list_collections())

    try:
        print("Deleting 'knowledge' collection...")
        client.delete_collection(name="knowledge")
        print("'knowledge' collection deleted.")
    except Exception as e:
        print(f"Could not delete 'knowledge' collection (it might not exist): {e}")

    try:
        print("Deleting 'history' collection...")
        client.delete_collection(name="history")
        print("'history' collection deleted.")
    except Exception as e:
        print(f"Could not delete 'history' collection (it might not exist): {e}")

    print("Collections after deletion:", client.list_collections())
    print("Script finished.")

except Exception as e:
    print(f"An error occurred during the process: {e}")
