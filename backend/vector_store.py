import chromadb
from config import VECTOR_DB_DIR

client = chromadb.PersistentClient(path=VECTOR_DB_DIR)

def get_collection(name):
    print(f"\n[RAG PIPELINE] Connecting to ChromaDB collection: '{name}'")
    print(f"[RAG PIPELINE] Persistent DB path configured: '{VECTOR_DB_DIR}'")
    collection = client.get_or_create_collection(name=name)
    print(f"[RAG PIPELINE] Successfully connected. Collection '{name}' contains {collection.count()} document chunks.")
    return collection
