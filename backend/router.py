import json
from sarvam_client import SarvamClient

def route_query(question):
    print("\n" + "="*80)
    print(f"[RAG PIPELINE] STAGE 1: ROUTING QUERY")
    print(f"[RAG PIPELINE] Input query: '{question}'")
    print("="*80)
    
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
        print("[RAG PIPELINE] Invoking Sarvam VLM Router model...")
        client = SarvamClient()
        response = client.chat([
            {
                "role": "user",
                "content": prompt
            }
        ])
        
        print(f"[RAG PIPELINE] Raw router VLM response:\n{response}")
        
        # Parse JSON, cleaning markdown code blocks if the model outputs them
        clean_response = response.strip()
        if clean_response.startswith("```json"):
            clean_response = clean_response[7:]
        if clean_response.endswith("```"):
            clean_response = clean_response[:-3]
        clean_response = clean_response.strip()
        
        result = json.loads(clean_response)
        print(f"[RAG PIPELINE] Route successfully determined:")
        print(f"  - Intent: '{result.get('intent', 'unknown')}'")
        print(f"  - Target Collections: {result.get('collections', [])}")
        print("="*80 + "\n")
        return result
    except Exception as e:
        print(f"[RAG PIPELINE] WARNING: Router classification failed: {e}. Falling back to default collections.")
        fallback = {
            "intent": "career_guidance",
            "collections": ["career", "courses"]
        }
        print(f"  - Intent (Fallback): '{fallback['intent']}'")
        print(f"  - Target Collections (Fallback): {fallback['collections']}")
        print("="*80 + "\n")
        return fallback
