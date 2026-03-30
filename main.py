import streamlit as st
from retriever import retrieve_documents
from gemini_api import generate_answer

st.title("RAG App with Google Gemini")

query = st.text_input("Ask a question:")

if query:
    docs = retrieve_documents(query)
    answer = generate_answer(query, docs)
    st.write("## Answer:")
    st.write(answer)
    st.write("---")
    st.write("### Retrieved Documents:")
    for doc in docs:
        st.write(doc)
