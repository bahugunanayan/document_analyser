import os
import requests
from dotenv import load_dotenv
import prompt

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def generate_answer(query, docs, mock=False):
    """Generate an answer using OpenAI Chat Completions.

    - If `mock` is True returns a fast, zero-cost placeholder.
    - `docs` is an iterable of objects with a `page_content` attribute (or strings).
    """
    if mock:
        return f"DEV MODE: I found {len(docs)} chunks. This is a fake answer to save your API credits!"

    if not OPENAI_API_KEY:
        return "Error: OPENAI_API_KEY not found in environment variables."

    # Build context from documents
    def _content(d):
        return getattr(d, "page_content", str(d))

    context = "\n\n".join([_content(d) for d in docs]) if docs else "No relevant documents found."

    # Compose system prompt from prompt.py pieces
    system_prompt = (
        (getattr(prompt, "prompt1", "") or "")
        + (getattr(prompt, "prompt2", "") or "")
        + (getattr(prompt, "prompt3", "") or "")
        + (getattr(prompt, "prompt4", "") or "")
        + (getattr(prompt, "prompt5", "") or "")
        + (getattr(prompt, "prompt6", "") or "")
    )

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
        ],
        "temperature": 0.2,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"OPENAI ERROR: {e}")
        return f"⚠️ OpenAI Error: {e}"