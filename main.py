import os
import base64
import random
import streamlit as st
import pandas as pd
from pypdf import PdfReader
from docx import Document
from retriever import retrieve_documents
from answer import generate_answer

DATA_FOLDER = "data"
os.makedirs(DATA_FOLDER, exist_ok=True)

# ── Helpers ──────────────────────────────────────────────

def save_file(name, data):
    with open(os.path.join(DATA_FOLDER, name), "wb") as f:
        f.write(data)

def load_persisted_files():
    if "_files_loaded" in st.session_state:
        return
    for fname in os.listdir(DATA_FOLDER):
        fpath = os.path.join(DATA_FOLDER, fname)
        if os.path.isfile(fpath):
            with open(fpath, "rb") as f:
                st.session_state["file_bytes"][fname] = f.read()
            if fname not in st.session_state["files"]:
                st.session_state["files"].append(fname)
    st.session_state["_files_loaded"] = True

def add_to_knowledge_base(text, filename):
    from langchain_community.vectorstores import FAISS
    from langchain_openai import OpenAIEmbeddings
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_core.documents import Document as LDoc
    emb = OpenAIEmbeddings(model="text-embedding-3-small")
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = [LDoc(page_content=c, metadata={"source": filename}) for c in splitter.split_text(text)]
    path = "faiss_index"
    if os.path.exists(path):
        vs = FAISS.load_local(path, emb, allow_dangerous_deserialization=True)
        vs.add_documents(docs)
    else:
        vs = FAISS.from_documents(docs, emb)
    vs.save_local(path)

def extract_text(f):
    ext = f.name.rsplit(".", 1)[-1].lower()
    try:
        if ext == "txt":   return f.read().decode("utf-8")
        if ext == "pdf":   return "\n".join(p.extract_text() for p in PdfReader(f).pages if p.extract_text())
        if ext == "docx":  return "\n".join(p.text for p in Document(f).paragraphs)
        if ext in ("xlsx", "csv"):
            return (pd.read_excel(f) if ext == "xlsx" else pd.read_csv(f)).to_string()
    except Exception as e:
        st.error(f"Error reading {f.name}: {e}")
    return None

def file_bytes(name):
    if name in st.session_state.get("file_bytes", {}):
        return st.session_state["file_bytes"][name]
    path = os.path.join(DATA_FOLDER, name)
    if os.path.isfile(path):
        with open(path, "rb") as f:
            data = f.read()
        st.session_state["file_bytes"][name] = data
        return data
    return None

# ── Query handler ────────────────────────────────────────

def handle_input():
    q = st.session_state["user_query"]
    if not q:
        return
    st.session_state["chat"].append({"role": "user", "text": q})
    is_dev = st.session_state.get("dev_mode", False)
    with st.spinner("Dev mode..." if is_dev else "Analyzing..."):
        try:
            if is_dev:
                answer = f"🧪 **Dev Mode** — `{q}`\n\n{random.choice(['Placeholder response.','Simulated answer.','Dummy output — no API used.'])}"
                sources = []
            else:
                docs = retrieve_documents(q)
                sources = list({d.metadata.get("source", "?") for d in docs if hasattr(d, "metadata")})
                answer = generate_answer(q, docs)
            st.session_state["chat"].append({"role": "assistant", "text": answer, "sources": sources})
        except Exception as e:
            st.session_state["chat"].append({"role": "assistant", "text": f"⚠️ {e}", "sources": []})
    st.session_state["user_query"] = ""

# ── Page config ──────────────────────────────────────────

st.set_page_config(page_title="Nexus | Enterprise AI", layout="centered", page_icon="🛡️")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html, body, [data-testid="stAppViewContainer"] {
    overflow: hidden !important; height: 100vh;
    background-color: #020203 !important;
    background-image:
        radial-gradient(ellipse at 85% 40%, rgba(255, 20, 60, 0.35), transparent 45%),
        radial-gradient(ellipse at 15% 70%, rgba(0, 220, 255, 0.3), transparent 45%),
        radial-gradient(ellipse at 50% 10%, rgba(255, 100, 10, 0.2), transparent 40%),
        linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px) !important;
    background-size: 100% 100%, 100% 100%, 100% 100%, 30px 30px, 30px 30px !important;
    background-attachment: fixed !important;
    color: #e0e0e0 !important; font-family: 'Inter', sans-serif !important;
}
.main .block-container { max-height:100vh; overflow:hidden !important; padding-top:2rem;
    max-width:850px; margin:0 auto; }
header, footer, .stDeployButton { display:none !important; }

.title-glow { text-align:center; font-weight:800; font-size:3rem; margin-bottom:15px;
    background:linear-gradient(90deg,#fff,#ff143c,#00dcff);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; }

.chat-window { height:55vh; overflow-y:auto; padding:20px; border-radius:16px;
    background:rgba(10,10,15,.55)!important; backdrop-filter:blur(20px);
    border:1px solid rgba(255,255,255,.12); margin-top:12px;
    box-shadow:0 10px 40px rgba(0,0,0,.5); }
.chat-window::-webkit-scrollbar { width:5px; }
.chat-window::-webkit-scrollbar-thumb { background:rgba(255,255,255,.2); border-radius:10px; }

.user-c   { display:flex; justify-content:flex-end; width:100%; margin-bottom:14px; }
.asst-c   { display:flex; justify-content:flex-start; width:100%; margin-bottom:14px; }
.user-b   { background:rgba(45,45,50,.8); color:#fff; padding:12px 18px;
    border-radius:18px 18px 4px 18px; max-width:75%; font-size:.92rem; line-height:1.6;
    border:1px solid rgba(255,255,255,.1); }
.asst-b   { background:linear-gradient(135deg,rgba(255,20,60,.2),rgba(0,220,255,.2));
    color:#fff; padding:12px 18px; border-radius:18px 18px 18px 4px; max-width:75%;
    font-size:.92rem; line-height:1.6; border:1px solid rgba(0,220,255,.4); }

.src-row  { display:flex; flex-wrap:wrap; gap:6px; margin-top:6px; }
.src-tag  { display:inline-flex; align-items:center; gap:4px; padding:3px 10px;
    border-radius:16px; font-size:.72rem; background:rgba(255,255,255,.08);
    border:1px solid rgba(255,255,255,.12); color:#aaa; text-decoration:none; }
.src-tag:hover { background:rgba(0,220,255,.15); border-color:rgba(0,220,255,.5); }
.src-tag span { color:#00dcff; }

.stTextInput div[data-baseweb="input"] { background:rgba(10,10,15,.7)!important;
    border:1px solid rgba(255,255,255,.15)!important; border-radius:12px!important; }
.stTextInput input { color:white!important; }

.dev-badge { display:inline-flex; padding:4px 14px; border-radius:20px;
    font-size:.72rem; font-weight:600; letter-spacing:.5px; text-transform:uppercase;
    background:linear-gradient(135deg,rgba(255,200,0,.2),rgba(255,100,0,.15));
    border:1px solid rgba(255,200,0,.4); color:#ffc800;
    animation:pulse 2s ease-in-out infinite; }
@keyframes pulse { 0%,100%{box-shadow:0 0 6px rgba(255,200,0,.2)} 50%{box-shadow:0 0 16px rgba(255,200,0,.5)} }

button[data-testid="stPopoverButton"] {
    background:none!important; border:none!important; box-shadow:none!important;
    padding:4px!important; font-size:1.4rem!important; cursor:pointer!important;
    opacity:.7; transition:opacity .2s;
}
button[data-testid="stPopoverButton"]:hover { opacity:1; }
button[data-testid="stPopoverButton"] svg { display:none!important; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ── Session state init ───────────────────────────────────

for k, v in {"file_bytes": {}, "files": [], "chat": [], "dev_mode": False}.items():
    if k not in st.session_state:
        st.session_state[k] = v


load_persisted_files()

# ── Main content ─────────────────────────────────────────

title_col, menu_col = st.columns([20, 1])
with title_col:
    st.markdown("<h1 class='title-glow'>⚡ Nexus: Internal AI Hub</h1>", unsafe_allow_html=True)
with menu_col:
    with st.popover("⚙️"):
        st.session_state["dev_mode"] = st.toggle("🧪 Dev Mode", value=st.session_state["dev_mode"])
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state["chat"] = []
            st.rerun()

with st.expander("🔐 Upload Documents", expanded=not st.session_state["chat"]):
    for f in st.file_uploader("Upload", type=["txt","pdf","docx","csv","xlsx"], accept_multiple_files=True, label_visibility="collapsed") or []:
        if f.name not in st.session_state["files"]:
            f.seek(0); raw = f.read()
            st.session_state["file_bytes"][f.name] = raw
            save_file(f.name, raw)
            f.seek(0)
            with st.status(f"Processing {f.name}...") as s:
                txt = extract_text(f)
                if txt:
                    add_to_knowledge_base(txt, f.name)
                    st.session_state["files"].append(f.name)
                    s.update(label="✅ Done!", state="complete")

st.text_input("Ask", placeholder="Query your knowledge base...", key="user_query",
              on_change=handle_input, label_visibility="collapsed")

# ── Chat display ─────────────────────────────────────────

if st.session_state["chat"]:
    html = "<div class='chat-window'>"
    for e in reversed(st.session_state["chat"]):
        r = e["role"]
        cls_c, cls_b = ("user-c","user-b") if r == "user" else ("asst-c","asst-b")
        icon = "✨ " if r == "assistant" else ""
        srcs = ""
        if r == "assistant" and e.get("sources"):
            tags = ""
            for s in e["sources"]:
                fb = file_bytes(s)
                if fb:
                    b64 = base64.b64encode(fb).decode()
                    ext = s.rsplit(".",1)[-1].lower()
                    mime = {"pdf":"application/pdf","txt":"text/plain","docx":"application/vnd.openxmlformats-officedocument.wordprocessingml.document","csv":"text/csv","xlsx":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}.get(ext,"application/octet-stream")
                    tags += f"<a class='src-tag' href='data:{mime};base64,{b64}' download='{s}'>⬇ <span>{s}</span></a>"
                else:
                    tags += f"<div class='src-tag'>📎 <span>{s}</span></div>"
            srcs = f"<div class='src-row'>{tags}</div>"
        html += f"<div class='{cls_c}'><div class='{cls_b}'>{icon}{e['text']}{srcs}</div></div>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)