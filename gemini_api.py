import os
import requests
from dotenv import load_dotenv

load_dotenv()
# Prefer OPENAI variables; fallback to GEMINI_API_KEY if still present
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Model selection via env
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-nano")
OPENAI_URL = os.getenv("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions")

def generate_answer(query, docs):
    # Prepare retrieved context
    context_text = ""
    for doc in docs:
        if hasattr(doc, 'page_content'):
            context_text += f"\n---\n{doc.page_content}"
        else:
            context_text += f"\n---\n{doc}"

    system_instruction = (
        "You are a specialized Assistant that ONLY answers questions based on the provided Context. "
        "Strictly follow these rules:\n"
        "1. Use ONLY the provided Context to answer the question.\n"
        "2. If the answer is NOT found in the Context, respond EXACTLY with: "
        "'I'm sorry, but the information requested is not present in the uploaded documents.'\n"
        "3. Do not use external knowledge or your own training data to supplement the answer.\n"
        "4. Be concise and professional."
    )

    user_content = f"DOCUMENT CONTEXT:\n{context_text}\n\nUSER QUESTION:\n{query}\n\nFINAL ANSWER:" 

    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.1,
        "max_tokens": 1024,
    }

    try:
        resp = requests.post(OPENAI_URL, headers=headers, json=payload)
        if resp.status_code == 200:
            rj = resp.json()
            # Chat Completions: extract the assistant message
            return rj["choices"][0]["message"]["content"]
        else:
            return f"Error: API returned status code {resp.status_code} - {resp.text}"
    except Exception as e:
        return f"System Error: {str(e)}"