import os
import sqlite3
import numpy as np
import json
import re

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
DB_PATH = os.path.join(DATA_DIR, "career_guidance.db")
CHUNKS_PATH = os.path.join(DATA_DIR, "chunks.json")
EMBEDDINGS_PATH = os.path.join(DATA_DIR, "embeddings.npy")
TFIDF_PATH = os.path.join(DATA_DIR, "tfidf_data.json")

class RAGAssistant:
    def __init__(self):
        self.model = None
        self.use_transformer = False
        self.chunks = []
        self.embeddings = None
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        
        # Try importing sentence_transformers
        try:
            from sentence_transformers import SentenceTransformer
            print("Loading SentenceTransformer model ('all-MiniLM-L6-v2')...")
            # Set a cache folder inside our workspace to avoid downloading into user's home folder directly or permission errors
            cache_folder = os.path.join(DATA_DIR, ".cache")
            os.makedirs(cache_folder, exist_ok=True)
            self.model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder=cache_folder)
            self.use_transformer = True
            print("SentenceTransformer loaded successfully!")
        except Exception as e:
            print(f"Warning: Failed to load SentenceTransformer: {e}. Falling back to TF-IDF vectorizer.")
            self.use_transformer = False
            try:
                from sklearn.feature_extraction.text import TfidfVectorizer
                self.tfidf_vectorizer = TfidfVectorizer(stop_words='english')
            except Exception as se_err:
                print(f"Critical: Could not load scikit-learn TfidfVectorizer: {se_err}")
                
        # Load index if exists
        self.load_index()

    def load_index(self):
        if os.path.exists(CHUNKS_PATH):
            try:
                with open(CHUNKS_PATH, 'r', encoding='utf-8') as f:
                    self.chunks = json.load(f)
                print(f"Loaded {len(self.chunks)} chunks from chunks.json")
            except Exception as e:
                print(f"Error loading chunks.json: {e}")
                
        if self.use_transformer and os.path.exists(EMBEDDINGS_PATH):
            try:
                self.embeddings = np.load(EMBEDDINGS_PATH)
                print(f"Loaded embeddings matrix of shape: {self.embeddings.shape}")
            except Exception as e:
                print(f"Error loading embeddings.npy: {e}")
        elif not self.use_transformer and os.path.exists(TFIDF_PATH):
            try:
                with open(TFIDF_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # Rebuild TFIDF vectorizer
                from sklearn.feature_extraction.text import TfidfVectorizer
                self.tfidf_vectorizer = TfidfVectorizer(stop_words='english')
                corpus = [c['text'] for c in self.chunks]
                if corpus:
                    self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(corpus)
                    print(f"TF-IDF Vectorizer rebuilt with corpus of size: {len(corpus)}")
            except Exception as e:
                print(f"Error loading TF-IDF data: {e}")

    def clean_markdown_block(self, text):
        # Remove markdown code ticks and clean spaces
        text = text.replace("```", "")
        text = re.sub(r'#+\s+', '', text)
        text = re.sub(r'\*+\s*', '', text)
        return text.strip()

    def build_index(self):
        print("Building search index...")
        self.chunks = []
        
        # 1. Parse docs/role_descriptions.md
        role_md_path = os.path.join(DOCS_DIR, "role_descriptions.md")
        if os.path.exists(role_md_path):
            print(f"Reading role descriptions: {role_md_path}")
            try:
                with open(role_md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Split content by markdown headers (### or ##)
                sections = re.split(r'\n(?=#{2,3}\s+)', content)
                for sec in sections:
                    sec_clean = sec.strip()
                    if not sec_clean:
                        continue
                    # Extract header
                    header_match = re.match(r'^#{2,3}\s+(.+)', sec_clean)
                    title = header_match.group(1).strip() if header_match else "General Info"
                    
                    self.chunks.append({
                        "text": self.clean_markdown_block(sec_clean),
                        "source": "Role Descriptions Guide",
                        "title": title,
                        "metadata": {"type": "role_description", "title": title}
                    })
                print(f"  Parsed {len(sections)} sections from role descriptions")
            except Exception as e:
                print(f"  Error parsing role descriptions: {e}")
                
        # 2. Parse docs/interview_tips.md
        interview_md_path = os.path.join(DOCS_DIR, "interview_tips.md")
        if os.path.exists(interview_md_path):
            print(f"Reading interview tips: {interview_md_path}")
            try:
                with open(interview_md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # We can partition by role sections first, then by Q&A pairs
                sections = re.split(r'\n(?=###\s+)', content)
                q_count = 0
                for sec in sections:
                    sec_clean = sec.strip()
                    if not sec_clean:
                        continue
                    header_match = re.match(r'^###\s+(.+)', sec_clean)
                    role_title = header_match.group(1).strip() if header_match else "General Interview Prep"
                    
                    # Split Q&A blocks
                    q_blocks = re.split(r'\n(?=\*\*Q\d+)', sec_clean)
                    for block in q_blocks:
                        block_clean = block.strip()
                        if not block_clean or block_clean.startswith("###"):
                            continue
                        self.chunks.append({
                            "text": self.clean_markdown_block(block_clean),
                            "source": f"Interview Preparation - {role_title}",
                            "title": f"Interview Prep for {role_title}",
                            "metadata": {"type": "interview_question", "role": role_title}
                        })
                        q_count += 1
                print(f"  Parsed {q_count} question blocks from interview tips")
            except Exception as e:
                print(f"  Error parsing interview tips: {e}")
                
        # 3. Read SQLite career_faq table
        if os.path.exists(DB_PATH):
            print(f"Reading FAQs from database: {DB_PATH}")
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("SELECT faq_id, category, question, answer, keywords FROM career_faq")
                rows = cursor.fetchall()
                for row in rows:
                    faq_id, category, question, answer, keywords = row
                    text = f"Category: {category}\nQuestion: {question}\nAnswer: {answer}\nKeywords: {keywords}"
                    self.chunks.append({
                        "text": text,
                        "source": f"Career FAQs - {category}",
                        "title": question,
                        "metadata": {"type": "faq", "category": category, "id": faq_id}
                    })
                conn.close()
                print(f"  Ingested {len(rows)} FAQ items from career_faq database table")
            except Exception as e:
                print(f"  Error ingesting database FAQs: {e}")
                
        if not self.chunks:
            print("No data chunks created. Aborting indexing.")
            return
            
        print(f"Total chunks to index: {len(self.chunks)}")
        
        # Save chunks to json
        with open(CHUNKS_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.chunks, f, indent=2)
            
        # Re-compute vector embeddings
        corpus = [c['text'] for c in self.chunks]
        if self.use_transformer and self.model:
            print("Computing embeddings using SentenceTransformer model...")
            try:
                self.embeddings = self.model.encode(corpus, show_progress_bar=True, batch_size=32)
                np.save(EMBEDDINGS_PATH, self.embeddings)
                print(f"Saved embeddings matrix of shape {self.embeddings.shape} to embeddings.npy")
            except Exception as e:
                print(f"Error computing/saving transformer embeddings: {e}. Reverting to TF-IDF.")
                self.use_transformer = False
                
        if not self.use_transformer:
            print("Building TF-IDF model...")
            try:
                from sklearn.feature_extraction.text import TfidfVectorizer
                self.tfidf_vectorizer = TfidfVectorizer(stop_words='english')
                self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(corpus)
                # Save status
                with open(TFIDF_PATH, 'w', encoding='utf-8') as f:
                    json.dump({"status": "built", "corpus_size": len(corpus)}, f)
                print("TF-IDF Index created and saved successfully!")
            except Exception as e:
                print(f"Critical error creating TF-IDF index: {e}")

    def retrieve(self, query, top_k=3):
        if not self.chunks:
            print("Search index is empty!")
            return []
            
        results = []
        
        if self.use_transformer and self.embeddings is not None and self.model:
            try:
                query_emb = self.model.encode([query])[0]
                # Cosine similarity
                norm_query = np.linalg.norm(query_emb)
                norm_embs = np.linalg.norm(self.embeddings, axis=1)
                dot_products = np.dot(self.embeddings, query_emb)
                similarities = dot_products / (norm_embs * norm_query + 1e-8)
                
                # Get top_k
                top_indices = np.argsort(similarities)[::-1][:top_k]
                for idx in top_indices:
                    score = float(similarities[idx])
                    chunk = self.chunks[idx].copy()
                    chunk["score"] = score
                    results.append(chunk)
            except Exception as e:
                print(f"Error in Transformer retrieval: {e}. Trying fallback.")
                
        # Fallback to TF-IDF if results are empty or transformer failed
        if not results and self.tfidf_vectorizer is not None and self.tfidf_matrix is not None:
            try:
                query_tfidf = self.tfidf_vectorizer.transform([query])
                from sklearn.metrics.pairwise import cosine_similarity
                similarities = cosine_similarity(self.tfidf_matrix, query_tfidf).flatten()
                top_indices = np.argsort(similarities)[::-1][:top_k]
                for idx in top_indices:
                    score = float(similarities[idx])
                    if score > 0:  # Only retrieve if there's some match
                        chunk = self.chunks[idx].copy()
                        chunk["score"] = score
                        results.append(chunk)
            except Exception as e:
                print(f"Error in TF-IDF retrieval: {e}")
                
        # Basic keyword match fallback if all vector search methods fail/return nothing
        if not results:
            query_words = set(query.lower().split())
            scores = []
            for chunk in self.chunks:
                text_words = set(chunk['text'].lower().split())
                overlap = len(query_words.intersection(text_words))
                if overlap > 0:
                    scores.append((overlap / len(query_words), chunk))
            scores.sort(key=lambda x: x[0], reverse=True)
            for score, chunk in scores[:top_k]:
                c = chunk.copy()
                c["score"] = score
                results.append(c)
                
        return results

if __name__ == "__main__":
    assistant = RAGAssistant()
    assistant.build_index()
    print("Testing search retrieval...")
    q = "What does a Software Engineer do at entry level?"
    results = assistant.retrieve(q, top_k=2)
    print(f"Query: '{q}'\nResults:")
    for r in results:
        print(f" - Source: {r['source']} (Score: {r['score']:.4f})\n   Snippet: {r['text'][:120]}...")
