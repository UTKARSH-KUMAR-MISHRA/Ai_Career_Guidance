import os
import pdfplumber
import chromadb
from sentence_transformers import SentenceTransformer
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import VECTOR_DB_DIR, DATA_DIR
from retriever import safe_print

def ingest_pdfs():
    safe_print("\n" + "="*90)
    safe_print("[PDF INGESTION PIPELINE] STARTING PDF PARSING, CHUNKING & EMBEDDING")
    safe_print("="*90)
    
    cache_folder = os.path.join(DATA_DIR, ".cache")
    os.makedirs(cache_folder, exist_ok=True)
    
    model_name = "all-MiniLM-L6-v2"
    safe_print(f"[EMBEDDING MODEL] Loading SentenceTransformer model '{model_name}' (cache: {cache_folder})...")
    model = SentenceTransformer(model_name, cache_folder=cache_folder)
    safe_print(f"[EMBEDDING MODEL] Loaded successfully! Target vector dimension: 384")
    
    safe_print(f"[VECTOR DB] Connecting to Chroma PersistentClient at: '{VECTOR_DB_DIR}'")
    client = chromadb.PersistentClient(path=VECTOR_DB_DIR)
    
    pdf_dir = os.path.join(DATA_DIR, "uploaded_pdf")
    if not os.path.exists(pdf_dir):
        pdf_dir = os.path.join(DATA_DIR, "uploaded_pdfs")
    if not os.path.exists(pdf_dir):
        safe_print(f"[PDF INGESTION ERROR] PDF directory not found: {pdf_dir}")
        return
        
    safe_print(f"[PDF INGESTION] Scanning PDF directory: '{pdf_dir}'")
    
    try:
        client.delete_collection(name="pdf")
        safe_print("[VECTOR DB] Reset/deleted existing 'pdf' collection for fresh indexing.")
    except Exception:
        pass
    collection = client.create_collection(name="pdf")
    
    documents = []
    ids = []
    metadatas = []
    
    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith(".pdf")]
    safe_print(f"[PDF CHUNKING] Found {len(pdf_files)} PDF files to ingest.")
    
    total_chars_all = 0
    
    for filename in pdf_files:
        pdf_path = os.path.join(pdf_dir, filename)
        file_size_bytes = os.path.getsize(pdf_path)
        safe_print(f"\n[DOCUMENT CHUNKING] Processing PDF: '{filename}' (File Size: {file_size_bytes} bytes)")
        try:
            with pdfplumber.open(pdf_path) as pdf:
                page_count = len(pdf.pages)
                safe_print(f"  - Total Pages in PDF: {page_count}")
                for page_idx, page in enumerate(pdf.pages):
                    page_num = page_idx + 1
                    
                    text = page.extract_text(layout=True) or ""
                    tables_str = ""
                    tables = page.extract_tables()
                    table_count = len(tables) if tables else 0
                    
                    if tables:
                        for t_idx, table in enumerate(tables):
                            tables_str += f"\n\n[Table {t_idx+1}]\n"
                            for row in table:
                                cleaned_row = [str(cell).replace("\n", " ").strip() if cell is not None else "" for cell in row]
                                tables_str += "| " + " | ".join(cleaned_row) + " |\n"
                    
                    combined_text = f"Document: {filename}\nPage: {page_num}\n\nContent:\n{text}\n{tables_str}"
                    chunk_size = len(combined_text)
                    total_chars_all += chunk_size
                    
                    safe_print(f"  - Chunk [Page {page_num}] Text Chars: {len(text)} | Tables Extracted: {table_count} | Combined Chunk Size: {chunk_size} chars")
                    
                    documents.append(combined_text)
                    ids.append(f"pdf_{filename}_p{page_num}")
                    metadatas.append({
                        "source": filename,
                        "page": page_num,
                        "type": "pdf",
                        "char_count": chunk_size
                    })
        except Exception as e:
            safe_print(f"  - Error processing PDF '{filename}': {e}")
            
    if documents:
        sizes = [len(d) for d in documents]
        safe_print(f"\n[PDF CHUNKING SUMMARY]")
        safe_print(f"  - Total PDF Chunks Created: {len(documents)}")
        safe_print(f"  - Total PDF Text Characters: {total_chars_all}")
        safe_print(f"  - Smallest Chunk Size: {min(sizes)} chars")
        safe_print(f"  - Largest Chunk Size: {max(sizes)} chars")
        safe_print(f"  - Average Chunk Size: {sum(sizes) // len(sizes)} chars")
        
        safe_print(f"\n[EMBEDDING GENERATION] Converting {len(documents)} PDF chunks into vectors using '{model_name}'...")
        batch_size = 50
        total_batches = (len(documents) + batch_size - 1) // batch_size
        
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            batch_metas = metadatas[i:i+batch_size]
            
            batch_embeddings = model.encode(batch_docs).tolist()
            batch_num = (i // batch_size) + 1
            safe_print(f"  - Generated Batch [{batch_num}/{total_batches}] ({len(batch_docs)} chunks) -> Vector Dimension: {len(batch_embeddings[0])}")
            
            collection.add(
                embeddings=batch_embeddings,
                documents=batch_docs,
                ids=batch_ids,
                metadatas=batch_metas
            )
            safe_print(f"  - Stored Batch [{batch_num}/{total_batches}] into ChromaDB collection 'pdf'")
            
        safe_print(f"\n[VECTOR STORAGE] PDF ingestion into ChromaDB complete! Total items in 'pdf' collection: {collection.count()}")
        safe_print("="*90 + "\n")
    else:
        safe_print("[PDF INGESTION] No PDF documents were found to ingest.")

if __name__ == "__main__":
    ingest_pdfs()
