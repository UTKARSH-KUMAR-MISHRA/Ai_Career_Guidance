import os
import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
from config import VECTOR_DB_DIR, DATA_DIR

def ingest_chroma():
    # Cache folder inside data directory to avoid permission/download issues
    cache_folder = os.path.join(DATA_DIR, ".cache")
    os.makedirs(cache_folder, exist_ok=True)
    
    print("Loading SentenceTransformer model ('all-MiniLM-L6-v2')...")
    model = SentenceTransformer("all-MiniLM-L6-v2", cache_folder=cache_folder)
    
    print(f"Connecting to Chroma PersistentClient at {VECTOR_DB_DIR}...")
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
            print(f"CSV file not found: {csv_path}. Skipping.")
            continue
            
        print(f"Ingesting {task['csv']} into collection '{task['collection']}'...")
        try:
            df = pd.read_csv(csv_path)
            
            # Delete old collection if exists
            try:
                client.delete_collection(name=task["collection"])
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
                metadatas.append({"source": task["csv"]})
                
            # Batch uploads of size 100
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i:i+batch_size]
                batch_ids = ids[i:i+batch_size]
                batch_metas = metadatas[i:i+batch_size]
                
                # Generate embeddings
                batch_embeddings = model.encode(batch_docs).tolist()
                
                collection.add(
                    embeddings=batch_embeddings,
                    documents=batch_docs,
                    ids=batch_ids,
                    metadatas=batch_metas
                )
                
            print(f"Successfully loaded {len(documents)} documents into '{task['collection']}' collection.")
        except Exception as e:
            print(f"Error loading {task['csv']}: {e}")
            
    print("Vector database ingestion complete!")

if __name__ == "__main__":
    ingest_chroma()
