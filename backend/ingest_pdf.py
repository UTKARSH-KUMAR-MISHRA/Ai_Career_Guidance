import os
import pdfplumber
import chromadb
from sentence_transformers import SentenceTransformer

# Re-use config values
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import VECTOR_DB_DIR, DATA_DIR

def ingest_pdfs():
    cache_folder = os.path.join(DATA_DIR, ".cache")
    os.makedirs(cache_folder, exist_ok=True)
    
    print("Loading SentenceTransformer model ('all-MiniLM-L6-v2')...")
    model = SentenceTransformer("all-MiniLM-L6-v2", cache_folder=cache_folder)
    
    print(f"Connecting to Chroma PersistentClient at {VECTOR_DB_DIR}...")
    client = chromadb.PersistentClient(path=VECTOR_DB_DIR)
    
    pdf_dir = os.path.join(DATA_DIR, "uploaded_pdf")
    if not os.path.exists(pdf_dir):
        pdf_dir = os.path.join(DATA_DIR, "uploaded_pdfs")
    if not os.path.exists(pdf_dir):
        print(f"PDF directory not found: {pdf_dir}")
        return
        
    print(f"Found PDF directory: {pdf_dir}")
    
    try:
        client.delete_collection(name="pdf")
        print("Deleted existing 'pdf' collection.")
    except Exception:
        pass
    collection = client.create_collection(name="pdf")
    
    documents = []
    ids = []
    metadatas = []
    
    for filename in os.listdir(pdf_dir):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(pdf_dir, filename)
            print(f"Processing PDF (layout-aware): {filename}...")
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for page_idx, page in enumerate(pdf.pages):
                        page_num = page_idx + 1
                        
                        # Use layout-aware extraction to preserve columns and tabular grids
                        text = page.extract_text(layout=True) or ""
                        
                        # Extract tables with pdfplumber
                        tables_str = ""
                        tables = page.extract_tables()
                        if tables:
                            for t_idx, table in enumerate(tables):
                                tables_str += f"\n\n[Table {t_idx+1}]\n"
                                for row in table:
                                    cleaned_row = [str(cell).replace("\n", " ").strip() if cell is not None else "" for cell in row]
                                    tables_str += "| " + " | ".join(cleaned_row) + " |\n"
                        
                        combined_text = f"Document: {filename}\nPage: {page_num}\n\nContent:\n{text}\n{tables_str}"
                        
                        documents.append(combined_text)
                        ids.append(f"pdf_{filename}_p{page_num}")
                        metadatas.append({
                            "source": filename,
                            "page": page_num,
                            "type": "pdf"
                        })
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                
    if documents:
        print(f"Generating embeddings for {len(documents)} PDF pages...")
        batch_size = 50
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            batch_metas = metadatas[i:i+batch_size]
            batch_embeddings = model.encode(batch_docs).tolist()
            
            collection.add(
                embeddings=batch_embeddings,
                documents=batch_docs,
                ids=batch_ids,
                metadatas=batch_metas
            )
        print("PDF ingestion into ChromaDB complete!")
    else:
        print("No PDF documents found to ingest.")

if __name__ == "__main__":
    ingest_pdfs()
