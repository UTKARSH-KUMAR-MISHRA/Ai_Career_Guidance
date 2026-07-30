import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")
VECTOR_DB_DIR = os.path.join(DATA_DIR, "vector_db")

EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # SentenceTransformer automatically downloads this model

COLLECTIONS = {
    "career": "career",
    "education": "education",
    "projects": "projects",
    "courses": "courses",
    "interview": "interview",
    "student": "student"
}
