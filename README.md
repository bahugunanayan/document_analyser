# RAG Application with Google Gemini API and Streamlit

This project demonstrates a simple Retrieval-Augmented Generation (RAG) application using the Google Gemini API and a Streamlit web interface.

## Project Structure

- `main.py`: Streamlit web app for user interaction.
- `ingest.py`: Script to ingest and embed documents from the `data/` folder.
- `retriever.py`: Retrieves relevant documents for a query using vector search.
- `gemini_api.py`: Handles communication with the Google Gemini API.
- `requirements.txt`: Lists all required Python packages.
- `data/`: Place your text documents here for ingestion.
- `vector_store/`: Stores the FAISS index and document mapping.

## How It Works

1. **Ingest Documents**: Run `python ingest.py` to embed and index all documents in the `data/` folder.
2. **Ask Questions**: Use the Streamlit app (`python -m streamlit run main.py`) to ask questions. The app retrieves relevant docs and sends them to Gemini for an answer.

## Setup Instructions

1. Install dependencies:
   ```
pip install -r requirements.txt
   ```
2. Set your Google Gemini API key in a `.env` file:
   ```
GEMINI_API_KEY=your_api_key_here
   ```
3. Add your documents (plain text files) to the `data/` folder.
4. Run the ingestion script:
   ```
python ingest.py
   ```
5. Launch the web app:
   ```
streamlit run main.py
   ```

## File-by-File Explanation

- **main.py**: The entry point. Provides a web UI for users to enter questions. Calls the retriever and Gemini API modules.
- **ingest.py**: Reads all files in `data/`, generates embeddings, and stores them in a FAISS index for fast retrieval.
- **retriever.py**: Loads the FAISS index and finds the most relevant documents for a given query using vector similarity.
- **gemini_api.py**: Sends the user’s question and retrieved docs to the Gemini API and returns the generated answer.
- **requirements.txt**: Lists all Python dependencies.
- **data/**: Folder for your knowledge base documents.
- **vector_store/**: Stores the vector index and document mapping.

## How the Dots Connect

- When a user asks a question, the app retrieves the most relevant documents using vector search (retriever.py).
- These documents, along with the question, are sent to the Gemini API (gemini_api.py).
- The Gemini API generates a context-aware answer, which is displayed in the Streamlit app (main.py).

---

Feel free to ask for deeper explanations or code walkthroughs for any part of the project! This README will be updated as we add more features or details.