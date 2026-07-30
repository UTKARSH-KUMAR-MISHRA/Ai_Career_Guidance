import os
import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import VECTOR_DB_DIR, DATA_DIR, EMBEDDING_MODEL
from retriever import safe_print

def ingest_chroma():
    safe_print("\n" + "="*90)
    safe_print("[CHROMA INGESTION PIPELINE] DATASET PARSING & VECTOR INDEXING")
    safe_print("="*90)
    
    cache_folder = os.path.join(DATA_DIR, ".cache")
    os.makedirs(cache_folder, exist_ok=True)
    
    model_name = EMBEDDING_MODEL
    safe_print(f"[EMBEDDING MODEL] Loading SentenceTransformer model '{model_name}' (cache: {cache_folder})...")
    model = SentenceTransformer(model_name, cache_folder=cache_folder)
    vector_dim = getattr(model, "get_embedding_dimension", None) or getattr(model, "get_sentence_embedding_dimension", None)
    vector_dim_val = vector_dim() if vector_dim else 384
    safe_print(f"[EMBEDDING MODEL] Loaded successfully! Vector dimension: {vector_dim_val}")
    
    safe_print(f"[VECTOR DB] Connecting to Chroma PersistentClient at: '{VECTOR_DB_DIR}'")
    client = chromadb.PersistentClient(path=VECTOR_DB_DIR)
    
    tasks = [
        {
            "csv": "roles.csv",
            "collection": "career",
            "format": lambda r: f"Career Role: {r['role_name']}. Description: {r['description']}. Difficulty: {r['difficulty_level']}. Salary: {r['salary_range']}. Future Scope: {r['future_scope']}."
        },
        {
            "csv": "courses.csv",
            "collection": "courses",
            "format": lambda r: f"Online Course: {r['course_name']} on {r['platform']} by {r['provider']}. Difficulty: {r['difficulty']}. Duration: {r['duration_hours']} hours. Rating: {r['rating']}."
        },
        {
            "csv": "projects.csv",
            "collection": "projects",
            "format": lambda r: f"Practical Project: {r['project_name']} in domain {r['project_domain']}. Difficulty: {r['difficulty']}. Estimated time: {r['estimated_duration']}. Description: {r['description']}. Required skills: {r['required_skills']}."
        },
        {
            "csv": "interview_questions.csv",
            "collection": "interview",
            "format": lambda r: f"Interview Question Type: {r['question_type']} for Role ID: {r['role_id']}. Question: {r['question']}. Expected Answer: {r['expected_answer']}."
        },
        {
            "csv": "certifications.csv",
            "collection": "education",
            "format": lambda r: f"Professional Certification: {r['certificate_name']} by {r['provider']}. Difficulty: {r['difficulty']}. Fee: {r['exam_fee']}. Industry Recognition: {r['recognized_by_industry']}."
        }
    ]
    
    csv_dir = os.path.join("data", "temp_cleaned")
    if not os.path.exists(csv_dir) and os.path.exists(os.path.join("..", "data", "temp_cleaned")):
        csv_dir = os.path.join("..", csv_dir)
        
    for task in tasks:
        csv_path = os.path.join(csv_dir, task["csv"])
        if not os.path.exists(csv_path):
            safe_print(f"[CSV WARNING] CSV file not found: {csv_path}. Skipping collection '{task['collection']}'.")
            continue
            
        safe_print(f"\n[DATASET CHUNKING] Reading CSV: '{task['csv']}' -> Target Collection: '{task['collection']}'")
        try:
            df = pd.read_csv(csv_path)
            row_count = len(df)
            safe_print(f"  - Read {row_count} rows from '{task['csv']}'")
            
            try:
                client.delete_collection(name=task["collection"])
                safe_print(f"  - Reset existing ChromaDB collection '{task['collection']}'.")
            except Exception:
                pass
            collection = client.create_collection(name=task["collection"])
            
            documents = []
            ids = []
            metadatas = []
            
            for idx, row in df.iterrows():
                doc_text = task["format"](row)
                documents.append(doc_text)
                ids.append(f"doc_{task['collection']}_{idx}")
                metadatas.append({"source": task["csv"], "char_count": len(doc_text)})
                
            chunk_sizes = [len(d) for d in documents]
            safe_print(f"  - Chunk Size Stats for '{task['collection']}': Min={min(chunk_sizes)} chars, Max={max(chunk_sizes)} chars, Avg={sum(chunk_sizes)//len(chunk_sizes)} chars")
            
            batch_size = 100
            total_batches = (len(documents) + batch_size - 1) // batch_size
            safe_print(f"  - Generating embeddings in {total_batches} batches using '{model_name}'...")
            
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i:i+batch_size]
                batch_ids = ids[i:i+batch_size]
                batch_metas = metadatas[i:i+batch_size]
                
                batch_embeddings = model.encode(batch_docs).tolist()
                batch_num = (i // batch_size) + 1
                
                collection.add(
                    embeddings=batch_embeddings,
                    documents=batch_docs,
                    ids=batch_ids,
                    metadatas=batch_metas
                )
                safe_print(f"    * Batch [{batch_num}/{total_batches}] stored {len(batch_docs)} vectors (Vector dim: {len(batch_embeddings[0])})")
                
            safe_print(f"[VECTOR STORAGE] Collection '{task['collection']}' successfully created & loaded with {collection.count()} vectors.")
        except Exception as e:
            safe_print(f"[INGESTION ERROR] Error loading '{task['csv']}': {e}")
            
    safe_print("\n[CHROMA INGESTION PIPELINE] Vector database ingestion complete!")
    safe_print("="*90 + "\n")

if __name__ == "__main__":
    ingest_chroma()
