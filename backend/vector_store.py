import os
from config import VECTOR_DB_DIR

_chroma_client = None

def get_chroma_client():
    global _chroma_client
    if _chroma_client is not None:
        return _chroma_client
    try:
        import chromadb
        _chroma_client = chromadb.PersistentClient(path=VECTOR_DB_DIR)
    except Exception as e:
        print(f"[RAG PIPELINE WARNING] ChromaDB client init note: {e}")
        _chroma_client = None
    return _chroma_client

def get_collection(name):
    print(f"\n[RAG PIPELINE] Connecting to ChromaDB collection: '{name}'")
    client = get_chroma_client()
    if not client:
        return None
    collection = client.get_or_create_collection(name=name)
    print(f"[RAG PIPELINE] Successfully connected. Collection '{name}' contains {collection.count()} document chunks.")
    return collection
