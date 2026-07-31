import os
import sys

os.environ["HF_HUB_OFFLINE"] = "0"
from config import EMBEDDING_MODEL, DATA_DIR
from vector_store import get_collection

def safe_print(*args, **kwargs):
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

_model_instance = None

def get_embedding_model():
    global _model_instance
    if _model_instance is not None:
        return _model_instance
    try:
        from sentence_transformers import SentenceTransformer
        cache_folder = os.path.join(DATA_DIR, ".cache")
        os.makedirs(cache_folder, exist_ok=True)
        safe_print(f"[RAG EMBEDDING] Lazy-loading SentenceTransformer model '{EMBEDDING_MODEL}'...")
        _model_instance = SentenceTransformer(EMBEDDING_MODEL, cache_folder=cache_folder)
    except Exception as e:
        safe_print(f"[RAG EMBEDDING WARNING] Custom cache load note ({e}). Retrying default load...")
        try:
            from sentence_transformers import SentenceTransformer
            _model_instance = SentenceTransformer(EMBEDDING_MODEL)
        except Exception as err2:
            safe_print(f"[RAG EMBEDDING ERROR] Critical: Failed to load SentenceTransformer: {err2}")
            _model_instance = None
    return _model_instance

def retrieve_multiple(collections, query, top_k=3):
    safe_print("\n" + "="*90)
    safe_print(f"[RAG PIPELINE] STAGE 2: DOCUMENT RETRIEVAL & VECTOR SEARCH")
    safe_print(f"[RAG PIPELINE] User Query: '{query}'")
    safe_print(f"[RAG PIPELINE] Target Collections: {collections}")
    safe_print("="*90)
    
    model = get_embedding_model()
    if not model:
        safe_print("[RAG EMBEDDING ERROR] SentenceTransformer model is unavailable.")
        return []
        
    safe_print(f"[RAG EMBEDDING] Generating vector embedding for query using model '{EMBEDDING_MODEL}'...")
    query_vector = model.encode(query)
    embedding = query_vector.tolist()
    vector_dim = len(embedding)
    safe_print(f"[RAG EMBEDDING] Query embedding generation complete.")
    safe_print(f"  - Vector dimension: {vector_dim}")
    safe_print(f"  - Vector L2 norm: {float(sum(x**2 for x in embedding)**0.5):.4f}")
    safe_print(f"  - Sample vector values: {[round(x, 4) for x in embedding[:5]]}")
    
    documents = []
    
    for name in collections:
        name = name.strip().lower()
        try:
            collection = get_collection(name)
            if not collection:
                safe_print(f"[VECTOR DB QUERY] Warning: Collection '{name}' unavailable.")
                continue
            total_items = collection.count()
            safe_print(f"\n[VECTOR DB QUERY] Querying collection '{name}' (total chunks in collection: {total_items}, top_k: {top_k})")
            
            if total_items == 0:
                safe_print(f"[VECTOR DB QUERY] Warning: Collection '{name}' is currently empty!")
                continue

            results = collection.query(
                query_embeddings=[embedding],
                n_results=top_k
            )
            
            if results["documents"] and len(results["documents"][0]) > 0:
                docs = results["documents"][0]
                metas = results["metadatas"][0] if "metadatas" in results and results["metadatas"] else None
                distances = results["distances"][0] if "distances" in results and results["distances"] else None
                
                safe_print(f"[VECTOR DB RETRIEVAL] Retrieved {len(docs)} matching chunks from collection '{name}':")
                for i in range(len(docs)):
                    doc_text = docs[i]
                    source = metas[i].get("source", f"{name}.csv") if metas and metas[i] else f"{name}.csv"
                    page_info = f" (Page {metas[i]['page']})" if metas and metas[i] and "page" in metas[i] else ""
                    dist_info = f" [Distance: {distances[i]:.4f}]" if distances else ""
                    char_count = len(doc_text)
                    
                    safe_print(f"  -------------------------------------------------------------------------")
                    safe_print(f"  - Chunk [{i+1}] Source: {source}{page_info}{dist_info} | Size: {char_count} chars")
                    safe_print(f"    Snippet: {doc_text[:200]}...")
                    safe_print(f"  -------------------------------------------------------------------------")
                    
                    documents.append({
                        "text": doc_text,
                        "source": f"{source}{page_info}" if page_info else source,
                        "collection": name,
                        "distance": distances[i] if distances else 0.0,
                        "char_count": char_count
                    })
            else:
                safe_print(f"[VECTOR DB RETRIEVAL] No matching context chunks found in collection '{name}'.")
        except Exception as e:
            safe_print(f"[VECTOR DB ERROR] Error searching collection '{name}': {e}")
            
    safe_print(f"\n[RAG PIPELINE] Total document context chunks successfully retrieved: {len(documents)}")
    safe_print("="*90 + "\n")
    return documents
