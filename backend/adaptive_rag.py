import os
import requests
from router import route_query
from retriever import retrieve_multiple, safe_print
from prompt_builder import build_prompt
from sarvam_client import SarvamClient

def get_wiki_summary(query):
    safe_print("\n" + "="*90)
    safe_print(f"[RAG PIPELINE] WEB SEARCH FALLBACK CHECK (WIKIPEDIA)")
    safe_print(f"[RAG WEB SEARCH] Parsing query for technical terms: '{query}'")
    safe_print("="*90)
    
    keywords = [
        "kubeflow", "mlflow", "bayesian optimization", "xgboost", "random forest", 
        "mops", "mlops", "transformer", "bert", "gpt", "cnn", "lstm", "rnn", 
        "climate anomaly", "weather forecasting", "neural network", "deep learning",
        "grid search", "random search", "feature store"
    ]
    query_lower = query.lower()
    matched_term = None
    for kw in keywords:
        if kw in query_lower:
            matched_term = kw
            break
            
    if not matched_term:
        words = [w.strip("?,.!") for w in query.split() if w.strip("?,.!")]
        for w in words:
            if len(w) > 4 and w[0].isupper() and w.lower() not in ["hello", "please", "would", "could", "should", "career", "guidance"]:
                matched_term = w.lower()
                break
                
    if not matched_term:
         stop_words = {"what", "where", "which", "about", "route", "career", "course", "roadmap", "project"}
         words = [w.strip("?,.!-").lower() for w in query.split() if w.strip("?,.!-").lower() not in stop_words]
         if words:
             matched_term = max(words, key=len)
             
    if matched_term:
        target = matched_term.title().replace(" ", "_")
        safe_print(f"[RAG WEB SEARCH] Matched technical term: '{matched_term}' -> Target Page: '{target}'")
        try:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{target}"
            headers = {"User-Agent": "Mozilla/5.0"}
            safe_print(f"[RAG WEB SEARCH] Requesting URL: {url}")
            response = requests.get(url, headers=headers, timeout=0.5)
            if response.status_code == 200:
                data = response.json()
                extract = data.get("extract", "")
                if extract:
                    safe_print(f"[RAG WEB SEARCH] Wikipedia fetch successful! Snippet length: {len(extract)} chars.")
                    safe_print(f"  Snippet: {extract[:120]}...")
                    safe_print("="*90 + "\n")
                    return {
                        "text": f"External Web Search Summary for {matched_term.upper()}: {extract}",
                        "source": f"web_search_{matched_term}.json",
                        "page": 1
                    }
            safe_print(f"[RAG WEB SEARCH] Wikipedia page summary not found for target '{target}'. Status: {response.status_code}")
        except Exception as e:
            safe_print(f"[RAG WEB SEARCH] Search fallback failed for target '{target}': {e}")
    else:
        safe_print("[RAG WEB SEARCH] No extra technical keyword trigger matched.")
    safe_print("="*90 + "\n")
    return None

def ask(question, profile, history=None):
    safe_print("\n" + "#"*100)
    safe_print(f"[RAG PIPELINE] STARTING ADAPTIVE RAG ASK INVOCATION")
    safe_print(f"[RAG PIPELINE] Input Query: '{question}'")
    safe_print(f"[RAG PIPELINE] Profile: Name={profile.get('name')}, Branch={profile.get('branch')}, Goal={profile.get('career_goal')}")
    safe_print(f"[RAG PIPELINE] History Turns: {len(history) if history else 0}")
    safe_print("#"*100)
    
    # 1. Routing
    routing = route_query(question)
    collections = routing.get("collections", ["career"])
    
    # 2. Retrieval
    docs = retrieve_multiple(collections, question)
    
    # 3. Wikipedia Technical Augmentation Fallback
    wiki_doc = get_wiki_summary(question)
    if wiki_doc:
        safe_print(f"[RAG PIPELINE] Augmenting context with Wikipedia document: {wiki_doc['source']}")
        docs.append(wiki_doc)
            
    # 4. Empty context check
    if not docs:
        safe_print("[RAG PIPELINE] No local database or web search matches found. Yielding system fallback context.")
        docs.append({
            "text": "Fallback Guidance Guidelines: Provide professional career advice matching their profile. Guide them to focus on step-by-step software, machine learning, and cloud infrastructure basics.",
            "source": "system_guidance_fallback.json",
            "page": 1
        })
        
    # 5. Assembling Prompt
    prompt = build_prompt(question, docs, profile)
    
    # 6. Structuring conversation history & system instruction
    safe_print("\n" + "="*90)
    safe_print("[RAG PIPELINE] PREPARING CONVERSATION LOGS & SYSTEM INSTRUCTION")
    system_instruction = (
        "You are a professional AI Career Mentor and an elite Machine Learning & Data Science Expert. "
        "Format your output nicely in Markdown. Ground your answers strictly on the retrieved context, "
        "and seamlessly incorporate advanced technical concepts when relevant.\n\n"
        "Formatting Guidelines:\n"
        "1. If the user asks about a roadmap, career steps, learning path, or workflow hierarchy, you MUST construct "
        "a visual flowchart using Mermaid.js syntax inside a code block:\n"
        "```mermaid\n"
        "graph TD\n"
        "    A[\"Start\"] --> B[\"Step 1\"]\n"
        "    B --> C[\"Step 2\"]\n"
        "```\n"
        "2. Keep response structured and clean."
    )
    
    messages = [
        {
            "role": "system",
            "content": system_instruction
        }
    ]
    
    if history:
        safe_print(f"[RAG PIPELINE] Appending {len(history)} conversation history turns:")
        for turn in history:
            role = "user" if turn["role"] == "user" else "assistant"
            safe_print(f"  - [{role.upper()}] Snippet: {turn['content'][:80]}...")
            messages.append({
                "role": role,
                "content": turn["content"]
            })
            
    messages.append({
        "role": "user",
        "content": prompt
    })
    
    safe_print("\n" + "="*90)
    safe_print("[RAG PIPELINE] STAGE 5: FULL AUGMENTED PROMPT SENT TO MODEL")
    safe_print("="*90)
    safe_print(prompt)
    safe_print("="*90)
    
    # 7. Model Inference Call
    safe_print("\n" + "="*90)
    safe_print("[RAG PIPELINE] STAGE 6: EXECUTING LLM INFERENCE VIA SARVAM CLIENT")
    safe_print("="*90)
    client = SarvamClient()
    answer = client.chat(messages)
    safe_print(f"[RAG PIPELINE] Model API execution successful. Returned response size: {len(answer) if answer else 0} characters.")
    
    # 8. Programmatic source resolution
    sources = []
    seen_sources = set()
    for d in docs:
        src_name = d.get("source", "unknown")
        if src_name not in seen_sources:
            seen_sources.add(src_name)
            sources.append({
                "title": src_name.replace(".csv", "").replace("_", " ").title(),
                "source": src_name,
                "snippet": d.get("text", "")[:150] + "..."
            })
            
    safe_print("\n" + "#"*100)
    safe_print(f"[RAG PIPELINE] ADAPTIVE RAG ASK INVOCATION COMPLETED SUCCESSFULLY")
    safe_print("#"*100 + "\n")
    return answer, sources

if __name__ == "__main__":
    sample_profile = {
        "name": "Utkarsh Mishra",
        "branch": "Computer Science",
        "year": 3,
        "known_skills": "Python, Machine Learning, Data Structures",
        "interests": "AI, Cloud Computing, MLOps",
        "career_goal": "AI Engineer"
    }
    sample_query = "What is the complete roadmap and key skills required to become a successful AI Engineer?"
    ans, src = ask(sample_query, sample_profile)
