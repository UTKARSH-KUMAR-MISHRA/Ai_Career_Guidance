import os
os.environ["HF_HUB_OFFLINE"] = "1"
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL, DATA_DIR
from vector_store import get_collection

# Cache folder inside data directory to avoid directory/permission errors
cache_folder = os.path.join(DATA_DIR, ".cache")
os.makedirs(cache_folder, exist_ok=True)
model = SentenceTransformer(EMBEDDING_MODEL, cache_folder=cache_folder)

import sys

def safe_print(*args, **kwargs):
    # Safe console printer for Windows to avoid UnicodeEncodeErrors
    sep = kwargs.get('sep', ' ')
    end = kwargs.get('end', '\n')
    text = sep.join(str(arg) for arg in args)
    try:
        sys.stdout.write(text + end)
        sys.stdout.flush()
    except UnicodeEncodeError:
        enc = sys.stdout.encoding or 'utf-8'
        sys.stdout.write(text.encode(enc, errors='replace').decode(enc) + end)
        sys.stdout.flush()

def retrieve_multiple(collections, query, top_k=3):
    safe_print("\n" + "="*80)
    safe_print(f"[RAG PIPELINE] STAGE 2: DOCUMENT RETRIEVAL")
    safe_print(f"[RAG PIPELINE] Target collections: {collections}")
    safe_print(f"[RAG PIPELINE] Query string: '{query}'")
    safe_print("="*80)
    
    safe_print(f"[RAG PIPELINE] Generating query embedding with SentenceTransformer model: '{EMBEDDING_MODEL}'")
    embedding = model.encode(query).tolist()
    safe_print(f"[RAG PIPELINE] Embedding encoding finished. Vector dimension: {len(embedding)}")
    
    documents = []
    
    for name in collections:
        name = name.strip().lower()
        try:
            collection = get_collection(name)
            safe_print(f"[RAG PIPELINE] Querying collection '{name}' (total chunks in store: {collection.count()})")
            results = collection.query(
                query_embeddings=[embedding],
                n_results=top_k
            )
            
            if results["documents"] and len(results["documents"][0]) > 0:
                docs = results["documents"][0]
                metas = results["metadatas"][0] if "metadatas" in results and results["metadatas"] else None
                distances = results["distances"][0] if "distances" in results and results["distances"] else None
                
                safe_print(f"[RAG PIPELINE] Retrieved {len(docs)} matching chunks from '{name}':")
                for i in range(len(docs)):
                    source = metas[i].get("source", name + ".csv") if metas and metas[i] else name + ".csv"
                    page_info = f" (Page {metas[i]['page']})" if metas and metas[i] and "page" in metas[i] else ""
                    dist_info = f" [Distance: {distances[i]:.4f}]" if distances else ""
                    
                    safe_print(f"  - Chunk [{i+1}] Source: {source}{page_info}{dist_info}")
                    safe_print(f"    Snippet: {docs[i][:120]}...")
                    
                    documents.append({
                        "text": docs[i],
                        "source": f"{source}{page_info}" if page_info else source,
                        "collection": name
                    })
            else:
                safe_print(f"[RAG PIPELINE] No document matches found in collection '{name}'.")
        except Exception as e:
            safe_print(f"[RAG PIPELINE] Error searching collection '{name}': {e}")
            
    safe_print(f"\n[RAG PIPELINE] Total document chunks successfully retrieved: {len(documents)}")
    safe_print("="*80 + "\n")
    return documents
