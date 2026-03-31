import os
import requests
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Using the stable Gemini 2.5 Flash Lite endpoint
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"

def generate_answer(query, docs):
    # 1. Prepare the retrieved context
    # If docs are LangChain objects, we extract page_content; otherwise, use as string.
    context_text = ""
    for doc in docs:
        if hasattr(doc, 'page_content'):
            context_text += f"\n---\n{doc.page_content}"
        else:
            context_text += f"\n---\n{doc}"

    # 2. THE HARD-CODED SYSTEM PROMPT
    system_instruction = (
        "You are a specialized Assistant that ONLY answers questions based on the provided Context. "
        "Strictly follow these rules:\n"
        "1. Use ONLY the provided Context to answer the question.\n"
        "2. If the answer is NOT found in the Context, respond EXACTLY with: "
        "'I'm sorry, but the information requested is not present in the uploaded documents.'\n"
        "3. Do not use external knowledge or your own training data to supplement the answer.\n"
        "4. Be concise and professional."
    )

    # 3. Construct the Final Prompt for the API
    final_prompt = f"""
{system_instruction}

DOCUMENT CONTEXT:
{context_text}

USER QUESTION: 
{query}

FINAL ANSWER:
"""

    data = {
        "contents": [{"parts": [{"text": final_prompt}]}],
        "generationConfig": {
            "temperature": 0.1,  # Low temperature ensures more factual/less creative output
            "topP": 0.95,
            "maxOutputTokens": 1024,
        }
    }

    try:
        response = requests.post(GEMINI_API_URL, json=data)
        if response.status_code == 200:
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"Error: API returned status code {response.status_code} - {response.text}"
    except Exception as e:
        return f"System Error: {str(e)}"