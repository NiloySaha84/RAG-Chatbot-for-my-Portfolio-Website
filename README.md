# Portfolio Chatbot

A RAG-powered portfolio chatbot for my personal website. It indexes resume and project documents from the local `knowledge-base/` directory, stores embeddings in Chroma, and serves a chat UI with Gradio mounted on a FastAPI app.

## Features

- Answers questions about my projects, education, experience, and skills
- Loads PDF and Markdown content from a local knowledge base
- Builds and reuses a persistent Chroma vector store
- Exposes both a FastAPI backend and a Gradio chat interface

## Tech Stack

- Python 3.11+
- FastAPI
- Gradio
- LangChain
- ChromaDB
- Hugging Face embeddings
- OpenAI chat model
- `pypdf` for PDF ingestion

## Project Structure

```text
portfolioBot/
├── app.py
├── chatbot_engine.py
├── chatbot.ipynb
├── pyproject.toml
├── uv.lock
├── .env
└── knowledge-base/
    ├── Resume/
    │   └── NiloySahaResume.pdf
    └── Projects/
        ├── *.md
        └── ...
```

## Requirements

- Python 3.11 or newer
- `uv` installed
- An OpenAI API key

## Endpoints

- `/` - basic status message
- `/health` - health check
- `/gradio` - chatbot UI

## How It Works

1. `chatbot_engine.py` loads documents from `knowledge-base/`
2. PDF files in `knowledge-base/Resume/` are parsed with `PyPDFLoader`
3. Markdown files in `knowledge-base/Projects/` are loaded with `DirectoryLoader`
4. Documents are split into chunks and stored in Chroma under `vector_db/`
5. A retriever fetches relevant chunks for each question
6. The LLM answers using a constrained system prompt tailored to the portfolio

## Notes

- The vector store is cached locally in `vector_db/`
- Set `REBUILD_VECTOR_DB=true` to force a fresh index build
- `chatbot.ipynb` contains the notebook version of the same chatbot workflow

