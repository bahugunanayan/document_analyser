import os
import io
import base64
import streamlit as st
import pandas as pd
from pypdf import PdfReader
from docx import Document
from retriever import retrieve_documents
from answer import generate_answer

# --- 1. THE HIDDEN BACKEND: INGESTION ---
def add_to_knowledge_base(text, filename):
    from langchain_community.vectorstores import FAISS
    from langchain_openai import OpenAIEmbeddings
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_core.documents import Document as LangDocument

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_store_path = "faiss_index"
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_text(text)
    docs = [LangDocument(page_content=t, metadata={"source": filename}) for t in chunks]

    if os.path.exists(vector_store_path):
        vector_store = FAISS.load_local(vector_store_path, embeddings, allow_dangerous_deserialization=True)
        vector_store.add_documents(docs)
    else:
        vector_store = FAISS.from_documents(docs, embeddings)
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

# --- 3. CALLBACK TO HANDLE INPUT ---
def handle_input():
    user_query = st.session_state["user_query"]
    if user_query:
        # Add User Question
        st.session_state["chat_history"].append({"role": "user", "text": user_query})
        
        # Process the answer inside the callback to prevent loops
        with st.spinner("Analyzing..."):
            try:
                context_docs = retrieve_documents(user_query)
                if st.session_state.get("dev_mode_state", False):
                    answer = f"🤖 Dev Mode: Found {len(context_docs)} sections."
                else:
                    answer = generate_answer(user_query, context_docs)
                
                st.session_state["chat_history"].append({"role": "assistant", "text": answer})
            except Exception as e:
                st.session_state["chat_history"].append({"role": "assistant", "text": f"⚠️ Error: {str(e)}"})
        
        # Clear the input box by resetting the key
        st.session_state["user_query"] = ""

# --- 4. STREAMLIT FRONTEND CONFIG ---
st.set_page_config(page_title="KT Assistant", layout="centered")

st.markdown(
    """
    <style>
    html, body, [data-testid="stAppViewContainer"] { overflow: hidden !important; height: 100vh; }
    .main .block-container { max-height: 100vh; overflow: hidden !important; padding-top: 1rem; display: flex; flex-direction: column; }
    .chat-window { 
        height: 55vh; overflow-y: auto; padding: 20px; border: 1px solid #444; border-radius: 12px; 
        background-color: var(--secondary-background-color) !important; display: flex; flex-direction: column; 
        margin-top: 15px; opacity: 1 !important;
    }
    .user-container { display: flex; justify-content: flex-end; width: 100%; margin-bottom: 15px; }
    .assistant-container { display: flex; justify-content: flex-start; width: 100%; margin-bottom: 15px; }
    .user-bubble { background-color: #2b2b2b; color: #ffffff; padding: 10px 16px; border-radius: 18px 18px 0px 18px; max-width: 80%; border: 1px solid #444; }
    .assistant-bubble { background-color: #004a99; color: #ffffff; padding: 10px 16px; border-radius: 18px 18px 18px 0px; max-width: 80%; border: 1px solid #0056b3; }
    .stTextInput div[data-baseweb="input"] { background-color: var(--primary-background-color) !important; border: 1px solid #555 !important; border-radius: 8px !important; box-shadow: none !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar
st.sidebar.title("⚙️ Settings")
st.session_state["dev_mode_state"] = st.sidebar.checkbox("Dev Mode", value=False)
if st.sidebar.button("🗑️ Clear Chat History"):
    st.session_state["chat_history"] = []
    st.rerun()

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "processed_uploads" not in st.session_state:
    st.session_state["processed_uploads"] = []

st.title("📚 Modern Library")

# --- 5. UI SECTIONS ---
with st.expander("➕ Add Data", expanded=not st.session_state["chat_history"]):
    uploaded_files = st.file_uploader("Upload files", type=["txt", "pdf", "docx", "csv", "xlsx"], accept_multiple_files=True)
    if uploaded_files:
        for uploaded in uploaded_files:
            if uploaded.name not in st.session_state["processed_uploads"]:
                with st.status(f"Processing {uploaded.name}...") as status:
                    text = extract_text(uploaded)
                    if text:
                        add_to_knowledge_base(text, uploaded.name)
                        st.session_state["processed_uploads"].append(uploaded.name)
                        status.update(label="✅ Success!", state="complete")

st.divider()

# THE INPUT FIELD (Trigger on Enter using callback)
st.text_input("Ask a question", placeholder="Type your query and press Enter...", key="user_query", on_change=handle_input)

# --- 6. INVERTED CHAT HISTORY ---
def render_chat_box():
    chat_html = "<div class='chat-window'>"
    for entry in reversed(st.session_state["chat_history"]):
        role, text = entry["role"], entry["text"]
        container = "user-container" if role == "user" else "assistant-container"
        bubble = "user-bubble" if role == "user" else "assistant-bubble"
        chat_html += f'<div class="{container}"><div class="{bubble}">{text}</div></div>'
    chat_html += "</div>"
    st.markdown(chat_html, unsafe_allow_html=True)

if st.session_state["chat_history"]:
    render_chat_box()