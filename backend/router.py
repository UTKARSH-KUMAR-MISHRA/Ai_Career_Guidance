import json
from sarvam_client import SarvamClient
from retriever import safe_print

def route_query(question):
    safe_print("\n" + "="*90)
    safe_print(f"[RAG PIPELINE] STAGE 1: ROUTING QUERY TO VECTOR COLLECTIONS")
    safe_print(f"[RAG ROUTER] Input Query: '{question}'")
    safe_print("="*90)
    
    q_lower = question.lower()
    collections = []
    
    if any(w in q_lower for w in ["career", "role", "job", "salary", "roadmap", "path", "goal"]):
        collections.extend(["career", "courses", "projects"])
    if any(w in q_lower for w in ["course", "learn", "coursera", "nptel", "udemy", "class"]):
        collections.extend(["courses", "education"])
    if any(w in q_lower for w in ["project", "build", "code", "portfolio"]):
        collections.extend(["projects", "courses"])
    if any(w in q_lower for w in ["interview", "prep", "question", "hr", "technical"]):
        collections.extend(["interview", "career"])
    if any(w in q_lower for w in ["energy", "fmcg", "health", "infra", "manuf", "report", "trend"]):
        collections.extend(["pdf", "career"])
        
    if not collections:
        collections = ["career", "courses", "projects", "interview", "education"]
    else:
        # Deduplicate preserving order
        seen = set()
        collections = [x for x in collections if not (x in seen or seen.add(x))]
        
    safe_print(f"[RAG ROUTER] Instant Keyword Classifier -> Collections: {collections}")
    safe_print("="*90 + "\n")
    return {"intent": "career_guidance", "collections": collections}
