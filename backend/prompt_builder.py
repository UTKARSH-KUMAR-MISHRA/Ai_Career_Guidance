from retriever import safe_print

def build_prompt(question, documents, profile):
    """
    Build an augmented prompt for the LLM using retrieved document context
    personalized for the student's profile.
    """
    safe_print("\n" + "="*90)
    safe_print("[PROMPT BUILDER] STAGE 4: PROMPT ASSEMBLY & PERSONALIZATION")
    safe_print("="*90)
    
    if documents:
        context_parts = []
        safe_print(f"[PROMPT BUILDER] Combining {len(documents)} context chunks into context block:")
        for idx, doc in enumerate(documents, start=1):
            src = doc.get('source', 'Unknown Source')
            text = doc.get('text', '')
            safe_print(f"  - Context [{idx}] Source: {src} | Size: {len(text)} chars")
            context_parts.append(f"Source: {src}\nContent: {text}")
        context = "\n\n".join(context_parts)
    else:
        context = "No direct database context found."
        safe_print("[PROMPT BUILDER] Warning: Context block is empty (No retrieved docs).")

    safe_print(f"[PROMPT BUILDER] Total Context Character Length: {len(context)} chars")

    prompt = f"""Student Profile:
Name: {profile.get("name", "Student")}
Branch: {profile.get("branch", "Engineering")}
Year: {profile.get("year", "N/A")}
Known Skills: {profile.get("known_skills", "N/A")}
Interests: {profile.get("interests", "N/A")}
Target Career Goal: {profile.get("career_goal", "N/A")}

Retrieved Context Records from Database (ChromaDB Vector Store):
==========================================================================================
{context}
==========================================================================================

User Question: {question}

STRICT GROUNDING & RESPONSE RULES (MANDATORY):
1. DATABASE-ONLY GROUNDING: You MUST base your entire response strictly on the retrieved database records above. Do not invent or hallucinate outside information.
2. CITATIONS: Cite the exact source of every fact using brackets like [1], [2], [roles.csv], [courses.csv], [projects.csv], [interview_questions.csv].
3. NO CONTEXT HANDLING: If the retrieved database context is empty or does not directly mention the topic, clearly state: "No direct database context found for this query in the vector store." then summarize what database data is available for their branch/career goal.
4. MERMAID FLOWCHART: If asked for a roadmap, progression, or learning steps, end your response with a Mermaid flowchart in a code block:
   ```mermaid
   graph TD
       A["Phase 1: Foundations"] --> B["Phase 2: Core Skills"]
       B --> C["Phase 3: Industry Projects"]
   ```
   Wrap all node titles in double quotes.
5. Provide clear, professional, structured Markdown responses tailored to the student's profile.
"""
    safe_print(f"[PROMPT BUILDER] Final Assembled Augmented Prompt Size: {len(prompt)} chars")
    safe_print("="*90 + "\n")
    return prompt
