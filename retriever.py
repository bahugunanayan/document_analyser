import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

VECTOR_STORE = "vector_store/index.faiss"
DOCS_FILE = "vector_store/docs.txt"
MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)

def retrieve_documents(query, k=3):
    index = faiss.read_index(VECTOR_STORE)
    with open(DOCS_FILE, "r", encoding="utf-8") as f:
        docs = [d.strip() for d in f.read().split("---") if d.strip()]
    query_emb = model.encode([query])
    D, I = index.search(np.array(query_emb, dtype=np.float32), k)
    return [docs[i] for i in I[0] if i < len(docs)]
