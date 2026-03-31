import os
import io
import streamlit as st
import pandas as pd
from pypdf import PdfReader
from docx import Document
from retriever import retrieve_documents
from gemini_api import generate_answer

# --- 1. THE HIDDEN BACKEND: INCREMENTAL INGESTION ---

def add_to_knowledge_base(text, filename):
    """
    Handles ingestion silently in the background.
    """
    from langchain_community.vectorstores import FAISS
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document as LangDocument

    # Setup Embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store_path = "faiss_index"

    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_text(text)
    
    # Create Document objects with metadata
    docs = [LangDocument(page_content=t, metadata={"source": filename}) for t in chunks]

    if os.path.exists(vector_store_path):
        # Load and MERGE new data
        vector_store = FAISS.load_local(vector_store_path, embeddings, allow_dangerous_deserialization=True)
        vector_store.add_documents(docs)
    else:
        # Create brand new index
        vector_store = FAISS.from_documents(docs, embeddings)

    # Save updated index
    vector_store.save_local(vector_store_path)

# --- 2. UNIVERSAL FILE EXTRACTOR ---

def extract_text(uploaded_file):
    ext = uploaded_file.name.split('.')[-1].lower()
    try:
        if ext == 'txt':
            return uploaded_file.read().decode("utf-8")
        elif ext == 'pdf':
            return "\n".join([p.extract_text() for p in PdfReader(uploaded_file).pages if p.extract_text()])
        elif ext == 'docx':
            return "\n".join([para.text for para in Document(uploaded_file).paragraphs])
        elif ext in ['xlsx', 'csv']:
            df = pd.read_excel(uploaded_file) if ext != 'csv' else pd.read_csv(uploaded_file)
            return df.to_string()
    except Exception as e:
        st.error(f"Error reading {uploaded_file.name}: {e}")
    return None

# --- 3. STREAMLIT FRONTEND ---

st.set_page_config(page_title="Private AI Knowledge Base", layout="centered")
st.title("📚 Intelligent RAG Assistant")

# Knowledge Base Upload Section
with st.expander("➕ Add Data to Knowledge Base"):
    uploaded_files = st.file_uploader("Upload files", type=["txt", "pdf", "docx", "csv", "xlsx"], accept_multiple_files=True)
    if uploaded_files:
        for uploaded in uploaded_files:
            with st.status(f"Processing {uploaded.name}...", expanded=False) as status:
                text = extract_text(uploaded)
                if text:
                    add_to_knowledge_base(text, uploaded.name)
                    status.update(label=f"✅ {uploaded.name} is now searchable!", state="complete")

st.divider()

# The Chat Interface
query = st.text_input("Ask a question about your documents:")

if query:
    with st.spinner("Searching internal documents..."):
        # Retrieve context
        context_docs = retrieve_documents(query)
        
        # Generate answer using Gemini
        answer = generate_answer(query, context_docs)
        
        # Display Answer
        st.markdown("### Answer")
        st.write(answer)
        
        # Display Sources with corrected indentation and logic
        st.divider()
        with st.expander("View Source Context"):
            for doc in context_docs:
                # Type checking to avoid AttributeError
                if hasattr(doc, 'metadata'):
                    source_name = doc.metadata.get('source', 'Unknown')
                    content = doc.page_content
                else:
                    source_name = "Unknown Source"
                    content = str(doc)

                st.caption(f"From: {source_name}")
                st.info(content)