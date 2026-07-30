"""
RAG Distance & Retrieval Check Tool (backend/rag_check.py)
Tests distance thresholds and document chunk matches against ChromaDB collections.
"""

import sys
from retriever import retrieve_multiple, safe_print

def check_rag_retrieval(query="What does an AI Engineer do?", distance_threshold=0.9):
    safe_print("\n" + "="*80)
    safe_print(f"[RAG CHECK] Querying ChromaDB with distance threshold {distance_threshold}")
    safe_print(f"[RAG CHECK] Query: '{query}'")
    safe_print("="*80)
    
    results = retrieve_multiple(["career", "courses", "projects", "interview", "pdf"], query, top_k=5)
    
    safe_print(f"\n=== RETRIEVAL RESULTS ({len(results)} chunks returned) ===\n")
    for i, res in enumerate(results, 1):
        dist = res.get("distance", 0.0)
        source = res.get("source", "unknown")
        snippet = res.get("content", "")[:200]
        status = "PASSED" if dist <= distance_threshold else "WARNING (Above threshold)"
        safe_print(f"Chunk {i}:")
        safe_print(f"  Source:    {source}")
        safe_print(f"  Distance:  {dist:.4f}  [{status}]")
        safe_print(f"  Preview:   {snippet}...\n")

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What does an AI Engineer do?"
    check_rag_retrieval(q)
