import os
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

DATA_DIR = "data"
VECTOR_STORE = "vector_store/index.faiss"
MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)

def ingest_documents():
    docs = []
    for fname in os.listdir(DATA_DIR):
        with open(os.path.join(DATA_DIR, fname), "r", encoding="utf-8") as f:
            docs.append(f.read())
    embeddings = model.encode(docs)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings, dtype=np.float32))
    faiss.write_index(index, VECTOR_STORE)
    with open("vector_store/docs.txt", "w", encoding="utf-8") as f:
        for doc in docs:
            f.write(doc.replace("\n", " ") + "\n---\n")
    print("Ingestion complete.")

if __name__ == "__main__":
    ingest_documents()
