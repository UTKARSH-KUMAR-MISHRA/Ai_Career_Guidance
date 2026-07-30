"""
Unified RAG Engine (backend/rag.py)
Built with BGE-M3 (BAAI/bge-m3) Embeddings, ChromaDB Vector Store, and Live Terminal Citation Visibility.
"""

import os
import sys
import json
import re
import chromadb
from sentence_transformers import SentenceTransformer

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import VECTOR_DB_DIR, DATA_DIR, EMBEDDING_MODEL
from retriever import retrieve_multiple, safe_print
from prompt_builder import build_prompt
from sarvam_client import SarvamClient

def extract_chart_data(answer: str) -> dict:
    pattern1 = r'([\w\s]+?)\s+[█░]+\s+(\d+)%'
    matches = re.findall(pattern1, answer)
    if matches:
        labels = [m[0].strip() for m in matches]
        data = [int(m[1]) for m in matches]
        return {"labels": labels, "data": data, "type": "bar"}
    pattern2 = r'([\w\s]+?):\s*(\d+)%'
    matches = re.findall(pattern2, answer)
    if matches:
        labels = [m[0].strip() for m in matches]
        data = [int(m[1]) for m in matches]
        return {"labels": labels, "data": data, "type": "bar"}
    return None

def detect_hallucination(answer: str, context: str) -> bool:
    if not re.search(r'\[\d+\]|\[\w+\.csv\]|\[web_search', answer):
        return True
    external_phrases = [
        "according to my knowledge", "i think", "i believe",
        "as per my training", "from my understanding", "in general"
    ]
    for phrase in external_phrases:
        if phrase in answer.lower():
            return True
    return False

from retriever import model as shared_model

class RAGPipeline:
    def __init__(self):
        safe_print("\n" + "="*90)
        safe_print(f"[RAG INITIALIZATION] Setting up BGE RAG Core Engine ({EMBEDDING_MODEL} + ChromaDB)")
        safe_print("="*90)
        
        self.model = shared_model
        if self.model:
            dim_fn = getattr(self.model, "get_embedding_dimension", None) or getattr(self.model, "get_sentence_embedding_dimension", None)
            self.vector_dim = dim_fn() if dim_fn else 384
        else:
            self.vector_dim = 384
        safe_print(f"[RAG EMBEDDING] BGE Model Ready! Dimension: {self.vector_dim}")
        
        safe_print(f"[VECTOR DB] Connecting to Chroma PersistentClient at: '{VECTOR_DB_DIR}'")
        self.client = chromadb.PersistentClient(path=VECTOR_DB_DIR)
        
    def classify_intent(self, question: str) -> list:
        keywords = {
            "career": ["role", "engineer", "developer", "scientist", "analyst", "manager", "job", "career", "salary"],
            "courses": ["course", "learn", "coursera", "nptel", "youtube", "certification", "rating", "platform"],
            "projects": ["project", "capstone", "build", "practical", "code", "portfolio"],
            "interview": ["interview", "question", "technical", "hr", "behavioral", "prep", "answer"],
            "education": ["degree", "btech", "mtech", "diploma", "cert"],
            "pdf": ["pdf", "document", "report", "policy"]
        }
        q_lower = question.lower()
        matched = []
        for collection, words in keywords.items():
            if any(word in q_lower for word in words):
                matched.append(collection)
                
        if not matched:
            matched = ["career", "courses", "projects", "interview", "pdf"]
        return matched

    def ask(self, question: str, student_profile: dict = None, conversation_history: list = None, language: str = "en") -> dict:
        safe_print("\n" + "█"*90)
        safe_print(f"[UI INPUT RECEIVED] Query: '{question}' | Language: {language}")
        safe_print("█"*90)
        
        # 1. Query Classification & Target Collections
        collections = self.classify_intent(question)
        safe_print(f"\n[RAG STEP 1: QUERY INTENT & CLASSIFICATION]")
        safe_print(f"  - Target ChromaDB Collections: {collections}")
        
        # 2. Vector Encoding & Retrieval using BGE-M3
        retrieved_chunks = retrieve_multiple(collections, question, top_k=4)
        
        safe_print(f"\n[RAG STEP 2: RETRIEVED GROUNDED CONTEXT CHUNKS & CITATIONS]")
        citations_list = []
        
        for idx, chunk in enumerate(retrieved_chunks, 1):
            source_name = chunk.get("source", "unknown")
            text = chunk.get("content", "").strip()
            dist = chunk.get("distance", 0.0)
            
            citation_item = {
                "id": idx,
                "source": source_name,
                "distance": round(dist, 4),
                "snippet": text[:180] + "..."
            }
            citations_list.append(citation_item)
            
            safe_print(f"  📌 CITATION [{idx}]: Source='{source_name}' | Distance={dist:.4f}")
            safe_print(f"     Preview: {text[:150]}...")
            
        safe_print("="*90)
        safe_print(f"[TERMINAL VISIBILITY] Total Visible Citations Formatted: {len(citations_list)}")
        safe_print("="*90)
        
        # 3. Prompt Assembly
        prompt_str = build_prompt(
            question,
            retrieved_chunks,
            student_profile or {}
        )
        
        # 4. LLM Generation & Citation Output
        safe_print(f"\n[RAG STEP 3: LLM INFERENCE VIA SARVAM API]")
        s_client = SarvamClient()
        
        try:
            llm_response = s_client.call_chat_completions(
                messages=[
                    {"role": "system", "content": "You are an AI Career Guidance Mentor. Ground your answers strictly on the context and cite sources like [1], [roles.csv]."},
                    {"role": "user", "content": prompt_str}
                ]
            )
        except Exception as e:
            safe_print(f"[RAG WARNING] LLM call note: {e}. Executing fallback response...")
            llm_response = s_client._local_grounded_fallback([{"role": "user", "content": prompt_str}])
            
        safe_print("\n" + "="*90)
        safe_print("[RAG STEP 4: FINAL GENERATED ANSWER WITH CITATIONS DISPLAYED IN TERMINAL]")
        safe_print("="*90)
        safe_print(llm_response)
        safe_print("="*90 + "\n")
        
        chart_data = extract_chart_data(llm_response)
        is_hallucinated = detect_hallucination(llm_response, prompt_str)
        
        return {
            "answer": llm_response,
            "sources": citations_list,
            "citations": citations_list,
            "context_chunks_count": len(retrieved_chunks),
            "chart_data": chart_data,
            "hallucination_detected": is_hallucinated
        }

if __name__ == "__main__":
    pipeline = RAGPipeline()
    res = pipeline.ask("What is the complete roadmap and key skills required to become a Machine Learning Engineer?")
