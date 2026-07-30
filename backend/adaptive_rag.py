import os
import requests
from router import route_query
from retriever import retrieve_multiple, safe_print
from prompt_builder import build_prompt
from sarvam_client import SarvamClient

def get_wiki_summary(query):
    print("\n" + "="*80)
    print(f"[RAG PIPELINE] WEB SEARCH FALLBACK (WIKIPEDIA)")
    print(f"[RAG PIPELINE] Parsing query for technical terms: '{query}'")
    print("="*80)
    
    # Clean query to get core terms
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
        print(f"[RAG PIPELINE] Matched keyword term: '{matched_term}' -> Wikipedia Target Page: '{target}'")
        try:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{target}"
            headers = {"User-Agent": "Mozilla/5.0"}
            print(f"[RAG PIPELINE] Sending API request to: {url}")
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                extract = data.get("extract", "")
                if extract:
                    print(f"[RAG PIPELINE] Wikipedia fetch successful! Snippet length: {len(extract)} chars.")
                    print(f"  Snippet: {extract[:120]}...")
                    print("="*80 + "\n")
                    return {
                        "text": f"External Web Search Summary for {matched_term.upper()}: {extract}",
                        "source": f"web_search_{matched_term}.json",
                        "page": 1
                    }
            print(f"[RAG PIPELINE] Wikipedia page summary not found for target '{target}'. Status code: {response.status_code}")
        except Exception as e:
            print(f"[RAG PIPELINE] Wikipedia search fallback failed for target '{target}': {e}")
    else:
        print("[RAG PIPELINE] No matching technical keyword found for Wikipedia search fallback.")
    print("="*80 + "\n")
    return None

def ask(question, profile, history=None):
    safe_print("\n" + "#"*100)
    safe_print(f"[RAG PIPELINE] STARTING ADAPTIVE RAG ASK INVOCATION")
    safe_print(f"[RAG PIPELINE] Input query: '{question}'")
    safe_print(f"[RAG PIPELINE] Student profile details: {profile}")
    safe_print(f"[RAG PIPELINE] Conversation history turns: {len(history) if history else 0}")
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
    safe_print("\n" + "="*80)
    safe_print("[RAG PIPELINE] STAGE 3: PROMPT ASSEMBLY")
    prompt = build_prompt(question, docs, profile)
    safe_print(f"[RAG PIPELINE] Assembled prompt text length: {len(prompt)} characters.")
    safe_print("="*80)
    
    # 6. Structuring conversation history
    safe_print("\n" + "="*80)
    safe_print("[RAG PIPELINE] STAGE 4: PREPARING CONVERSATION LOGS FOR MODEL")
    system_instruction = (
        "You are a professional AI Career Mentor and an elite Machine Learning & Data Science Expert. "
        "Format your output nicely in Markdown. Ground your answers strictly on the retrieved context, "
        "and seamlessly incorporate advanced technical concepts on ML/DL pipelines, hyperparameter tuning, "
        "spatial-temporal climate models, network architectures, and MLOps when relevant.\n\n"
        "Formatting Guidelines:\n"
        "1. If the user asks about a roadmap, career steps, learning path, or workflow hierarchy, you MUST construct "
        "a visual flowchart using Mermaid.js syntax inside a code block. Always wrap node labels in double quotes. "
        "For subgraphs, always use the syntax `subgraph \"Title\"` with quotes and no separate ID to avoid parser errors:\n"
        "```mermaid\n"
        "graph TD\n"
        "    A[\"Start\"] --> B[\"Step 1\"]\n"
        "    B --> C[\"Step 2\"]\n"
        "    subgraph \"Phase 1\"\n"
        "        B\n"
        "    end\n"
        "```\n"
        "2. When presenting multi-column structures (such as challenges vs recommendations, comparisons, or side-by-side layouts), "
        "wrap them in raw HTML flex columns (do NOT wrap in markdown code blocks):\n"
        "<div style=\"display: flex; gap: 12px; margin: 12px 0;\">\n"
        "  <div style=\"flex: 1; border: 1px solid #ECEDF3; padding: 10px; border-radius: 8px; background: #F9FAFB;\">\n"
        "    <strong>Column 1</strong>\n"
        "    <p>Content...</p>\n"
        "  </div>\n"
        "  <div style=\"flex: 1; border: 1px solid #ECEDF3; padding: 10px; border-radius: 8px; background: #F9FAFB;\">\n"
        "    <strong>Column 2</strong>\n"
        "    <p>Content...</p>\n"
        "  </div>\n"
        "</div>\n"
        "3. When presenting statistics or metrics, render them visually as styled progress bar blocks using raw inline HTML (do NOT wrap in markdown code blocks):\n"
        "<div style=\"margin: 8px 0; font-size: 11.5px; font-family: sans-serif;\">\n"
        "  <strong>Metric Name</strong> (percentage%)\n"
        "  <div style=\"background: #E5E7EB; border-radius: 4px; height: 8px; width: 100%; margin-top: 4px;\">\n"
        "    <div style=\"background: #4F46E5; height: 8px; border-radius: 4px; width: percentage%;\"></div>\n"
        "  </div>\n"
        "</div>\n"
        "4. Use Markdown tables for quantitative data comparisons.\n"
        "5. Cleanly cite the sources and page numbers when quoting from PDF documents.\n"
        "6. DO NOT repeat yourself. Keep the response clean, well-formatted, and cohesive."
    )
    
    messages = [
        {
            "role": "system",
            "content": system_instruction
        }
    ]
    
    if history:
        safe_print(f"[RAG PIPELINE] Appending {len(history)} recent conversation history turns to chat history payload:")
        for turn in history:
            role = "user" if turn["role"] == "user" else "assistant"
            safe_print(f"  - [{role.upper()}] Snippet: {turn['content'][:80]}...")
            messages.append({
                "role": role,
                "content": turn["content"]
            })
            
    # Append the newly engineered user query
    messages.append({
        "role": "user",
        "content": prompt
    })
    safe_print("="*80)
    
    # 7. Model Inference Call
    safe_print("\n" + "="*80)
    safe_print("[RAG PIPELINE] STAGE 5: LLM INFERENCE (SARVAM API)")
    client = SarvamClient()
    safe_print(f"[RAG PIPELINE] Invoking API with model endpoint...")
    answer = client.chat(messages)
    safe_print(f"[RAG PIPELINE] Model API execution successful. Returned response size: {len(answer) if answer else 0} characters.")
    safe_print("="*80)
    
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
