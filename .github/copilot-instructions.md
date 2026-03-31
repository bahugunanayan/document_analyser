# Copilot Instructions for this Repository

This project is a small Retrieval-Augmented Generation (RAG) demo using the Google Gemini API and Streamlit. These instructions focus on what an AI coding assistant needs to know to be effective in this codebase.

Overview
- Purpose: provide searchable answers from plain-text files in `data/` by embedding them, storing vectors in `vector_store/`, and sending context+query to Google Gemini for generation.
- Key files:
  - `ingest.py` — reads files in `data/`, computes embeddings, and writes a FAISS index and a docs mapping into `vector_store/` (see `vector_store/index.faiss`, `vector_store/docs.txt`).
  - `retriever.py` — loads the FAISS index and returns the top-k relevant document texts for a query.
  - `gemini_api.py` — wraps calls to the Google Gemini API. The API key is expected in an environment variable named `GEMINI_API_KEY` (commonly from a `.env`).
  - `main.py` — Streamlit app entrypoint that wires the retriever and `gemini_api.py` to the UI.

Important workflows & commands
- Install deps: `pip install -r requirements.txt`.
- Ingest documents after any change to `data/`: `python ingest.py` (this updates `vector_store/`).
- Run the app: `streamlit run main.py` (or `python -m streamlit run main.py`).

Project-specific patterns and conventions
- Minimal surface area: prefer small, targeted changes—this repo is an example/demo app, not a large production system.
- Vector store files live in `vector_store/` and are durable: do not delete or rename them without updating `ingest.py` and `retriever.py` accordingly.
- Plain-text sources: add knowledge files as `.txt` under `data/`. `ingest.py` expects text files and splits/embeds them.
- Embedding and retrieval contract: `ingest.py` and `retriever.py` must agree on embedding model and vector dimensionality; when modifying embeddings, re-run ingestion.

Integration points and external dependencies
- Google Gemini: usage centralized in `gemini_api.py`. Changes to request shape, temperature, or prompt engineering should be made there.
- FAISS vector DB: persisted as `vector_store/index.faiss`; treat as a binary artifact produced by `ingest.py`.
- Environment: expects `GEMINI_API_KEY`. Do not hardcode secrets.

Quick examples for PRs
- When adding a new retrieval feature, update `retriever.py` and add a small example / invocation in `trial.py` or `main.py` to demonstrate it.
- When changing prompt templates sent to Gemini, edit `gemini_api.py` and validate by running the Streamlit app locally with a small sample query.

Code style & safety hints for AI edits
- Keep edits small and focused; avoid broad renames across files in one PR.
- Preserve existing file I/O and index file locations unless the change documents a migration and updates `README.md`.
- Follow the repo's current synchronous, simple structure (no concurrency additions unless necessary).

What not to change
- Do not embed API keys or credentials in code.
- Avoid changing vector storage layout without updating both `ingest.py` and `retriever.py`.

If you need clarification
- Ask for which file to modify and whether regeneration of `vector_store/` is acceptable. Regenerating the index is required when changing embedding models or text splitting.

References
- Main entry point: `main.py`
- Ingest logic: `ingest.py`
- Retrieval: `retriever.py`
- Gemini integration: `gemini_api.py`

Please review and tell me any missing details or conventions to include.
