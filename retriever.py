import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# Must match exactly what you used in main.py
MODEL_NAME = "text-embedding-3-small"
VECTOR_STORE_PATH = "faiss_index"

def retrieve_documents(query, k=2):
    """
    Loads the OpenAI-based FAISS index and searches for the top K relevant chunks.
    """
    # 1. Initialize the same OpenAI embedding model
    # Ensure your OPENAI_API_KEY is in your environment variables (.env)
    embeddings = OpenAIEmbeddings(model=MODEL_NAME)

    # 2. Check if the index exists before trying to load it
    if not os.path.exists(VECTOR_STORE_PATH):
        print("Warning: No knowledge base found. Please upload documents first.")
        return []

    try:
        # 3. Load the index (allowing deserialization for local files)
        vector_store = FAISS.load_local(
            VECTOR_STORE_PATH, 
            embeddings, 
            allow_dangerous_deserialization=True
        )

        # 4. Perform the similarity search
        # This returns a list of LangChain Document objects
        relevant_docs = vector_store.similarity_search(query, k=k)
        
        return relevant_docs

    except Exception as e:
        print(f"Error during retrieval: {e}")
        return []