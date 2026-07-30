import json
from sarvam_client import SarvamClient
from retriever import safe_print

def route_query(question):
    safe_print("\n" + "="*90)
    safe_print(f"[RAG PIPELINE] STAGE 1: ROUTING QUERY TO VECTOR COLLECTIONS")
    safe_print(f"[RAG ROUTER] Input Query: '{question}'")
    safe_print("="*90)
    
    prompt = f"""
You are an AI Router for an Adaptive RAG system.

Available Collections:
1. career
2. education
3. projects
4. courses
5. interview
6. student
7. pdf (for industry reports, future of jobs, sector-specific data like Energy, FMCG, Healthcare, Infrastructure, Manufacturing, and hiring trends)

Return ONLY valid JSON in this format:

{{
    "intent": "career_guidance",
    "collections": ["career", "projects", "courses"]
}}

Rules:
- Return one intent.
- Return one or more collections.
- Do not explain.
- Do not add markdown wrappers.
- Return JSON only.
- Include "pdf" if the question asks about sector reports, future of jobs, hiring trends, or specific industries (FMCG, Energy, Manufacturing, Healthcare, Infrastructure).

Question:
{question}
"""
    try:
        safe_print("[RAG ROUTER] Invoking Router Classifier...")
        client = SarvamClient()
        response = client.chat([
            {
                "role": "user",
                "content": prompt
            }
        ])
        
        safe_print(f"[RAG ROUTER] Classifier Response:\n{response}")
        
        clean_response = response.strip()
        if clean_response.startswith("```json"):
            clean_response = clean_response[7:]
        if clean_response.endswith("```"):
            clean_response = clean_response[:-3]
        clean_response = clean_response.strip()
        
        result = json.loads(clean_response)
        safe_print(f"[RAG ROUTER] Route classification complete:")
        safe_print(f"  - Intent: '{result.get('intent', 'unknown')}'")
        safe_print(f"  - Selected Collections: {result.get('collections', [])}")
        safe_print("="*90 + "\n")
        return result
    except Exception as e:
        safe_print(f"[RAG ROUTER] Classifier note/fallback ({e}). Using default collections.")
        fallback = {
            "intent": "career_guidance",
            "collections": ["career", "courses", "projects", "interview", "education"]
        }
        safe_print(f"  - Intent (Fallback): '{fallback['intent']}'")
        safe_print(f"  - Selected Collections (Fallback): {fallback['collections']}")
        safe_print("="*90 + "\n")
        return fallback
