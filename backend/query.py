"""
ChromaDB Vector Store Query Utility (backend/query.py)
"""
import sys
import os
from retriever import retrieve_multiple, safe_print

def query_vector_store(query_text, collections=None, top_k=3):
    if collections is None:
        collections = ["career", "courses", "projects", "interview", "pdf"]
        
    safe_print("\n" + "="*90)
    safe_print(f"[CHROMADB QUERY CLI] Executing Search Query: '{query_text}'")
    safe_print(f"[CHROMADB QUERY CLI] Target Collections: {collections}")
    safe_print("="*90)
    
    results = retrieve_multiple(collections, query_text, top_k=top_k)
    return results

if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_query = " ".join(sys.argv[1:])
    else:
        user_query = "What is the complete roadmap and key skills required to become a Machine Learning Engineer?"
        
    results = query_vector_store(user_query)
    safe_print(f"\n[CHROMADB QUERY COMPLETE] Found {len(results)} matching chunks across collections.")
