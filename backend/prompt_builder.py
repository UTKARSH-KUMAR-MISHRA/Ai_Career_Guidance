def build_prompt(question, documents, profile):
    """
    Build a prompt for the LLM using the retrieved documents
    and personalize it using the student's profile.
    """
    if documents:
        context_parts = []
        for doc in documents:
            context_parts.append(f"Source: {doc['source']}\nContent: {doc['text']}")
        context = "\n\n".join(context_parts)
    else:
        context = "No direct database context found."

    prompt = f"""Student Profile:
Name: {profile.get("name", "Student")}
Branch: {profile.get("branch", "Engineering")}
Year: {profile.get("year", "N/A")}
Skills: {profile.get("known_skills", "N/A")}
Interests: {profile.get("interests", "N/A")}
Career Goal: {profile.get("career_goal", "N/A")}

Retrieved Context from Local Database:
=========================
{context}
=========================

User Question: {question}

Formatting Instructions (Mandatory):
1. If the user asks about a roadmap, career path, learning steps, or workflow, you MUST construct a visual flowchart using Mermaid.js syntax inside a code block at the end of your answer:
   ```mermaid
   graph TD
       A["Start"] --> B["Step 1"]
       B --> C["Step 2"]
       subgraph "Phase 1"
           B
       end
   ```
   Ensure all node labels inside square brackets are wrapped in double quotes. For subgraphs, always use the syntax `subgraph "Title"` with quotes and no separate ID to avoid parser errors.
2. Ground your answers strictly on the retrieved context. Personalize suggestions for the student.
3. Keep the response clean and cohesive. Do not repeat sections.
"""
    return prompt
