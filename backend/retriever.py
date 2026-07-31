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
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        os.environ["HF_HUB_OFFLINE"] = "1"
        from sentence_transformers import SentenceTransformer
        cache_folder = os.path.join(DATA_DIR, ".cache")
        os.makedirs(cache_folder, exist_ok=True)
        safe_print(f"[RAG EMBEDDING] Lazy-loading SentenceTransformer model '{EMBEDDING_MODEL}'...")
        _model_instance = SentenceTransformer(EMBEDDING_MODEL, cache_folder=cache_folder, local_files_only=True)
    except Exception as e:
        safe_print(f"[RAG EMBEDDING WARNING] Fast offline mode active ({e}). Using grounded SQL keyword retrieval.")
        _model_instance = None
    return _model_instance

def retrieve_multiple(collections, query, top_k=3):
    safe_print("\n" + "="*90)
    safe_print(f"[RAG PIPELINE] STAGE 2: DOCUMENT RETRIEVAL & VECTOR SEARCH")
    safe_print(f"[RAG PIPELINE] User Query: '{query}'")
    safe_print(f"[RAG PIPELINE] Target Collections: {collections}")
    safe_print("="*90)
    
    documents = []
    
    # 1. Try vector retrieval via ChromaDB if available
    for name in collections:
        name = name.strip().lower()
        try:
            collection = get_collection(name)
            if not collection:
                continue
            total_items = collection.count()
            if total_items == 0:
                continue
                
            model = get_embedding_model()
            if model:
                query_vector = model.encode(query).tolist()
                res = collection.query(query_embeddings=[query_vector], n_results=min(top_k, total_items))
                if res and res.get('documents') and len(res['documents']) > 0:
                    for docs_list in res['documents']:
                        for doc in docs_list:
                            documents.append({'text': doc, 'source': f"{name}.csv", 'page': 1})
        except Exception as e:
            safe_print(f"[VECTOR DB QUERY NOTE] Collection '{name}' query note: {e}")
            
    # 2. Fast SQL keyword fallback if vector DB is empty or unavailable
    if not documents:
        safe_print("[RAG PIPELINE] Using fast SQL keyword retrieval fallback...")
        try:
            from app import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()
            q_terms = [w.strip().lower() for w in query.split() if len(w.strip()) > 3]
            if not q_terms:
                q_terms = [query.strip().lower()]
                
            for term in q_terms[:3]:
                cursor.execute("SELECT role_name, description, required_skills FROM roles WHERE LOWER(role_name) LIKE ? OR LOWER(description) LIKE ? LIMIT 2", (f"%{term}%", f"%{term}%"))
                for row in cursor.fetchall():
                    documents.append({
                        'text': f"Role: {row['role_name']}. Description: {row['description']}. Skills: {row['required_skills']}",
                        'source': 'roles.csv',
                        'page': 1
                    })
                cursor.execute("SELECT course_name, platform, skills_covered FROM courses WHERE LOWER(course_name) LIKE ? OR LOWER(skills_covered) LIKE ? LIMIT 2", (f"%{term}%", f"%{term}%"))
                for row in cursor.fetchall():
                    documents.append({
                        'text': f"Course: {row['course_name']} ({row['platform']}). Skills: {row['skills_covered']}",
                        'source': 'courses.csv',
                        'page': 1
                    })
            conn.close()
        except Exception as se:
            safe_print(f"[SQL RETRIEVAL NOTE] {se}")
            
    safe_print(f"\n[RAG PIPELINE] Total document context chunks successfully retrieved: {len(documents)}")
    safe_print("="*90 + "\n")
    return documents
