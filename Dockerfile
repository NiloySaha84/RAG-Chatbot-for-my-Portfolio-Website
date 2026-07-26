FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/app/.cache/huggingface

WORKDIR /app

# CPU-only torch keeps the image several GB smaller than the default CUDA build.
RUN pip install torch==2.10.0 --index-url https://download.pytorch.org/whl/cpu

COPY requirements-deploy.txt .
RUN pip install -r requirements-deploy.txt

# Bake the embedding and reranker models into the image so startup
# does not depend on downloading them at runtime.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')" \
 && python -c "from flashrank import Ranker; Ranker()"

COPY app.py chatbot_engine.py ./
COPY knowledge-base/ knowledge-base/
COPY chroma_db/ chroma_db/

EXPOSE 8000

CMD uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}
