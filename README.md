# PortfolioBot

I built `PortfolioBot` to turn my portfolio into a conversation.

Instead of making recruiters and visitors click through sections one by one, I wanted them to be able to ask direct questions like:

- "What projects has Niloy built?"
- "What are his strongest skills?"
- "What is he studying?"
- "What experience does he have?"

The chatbot answers from my own portfolio knowledge base, not from generic internet knowledge. That was the main goal: make the experience interactive while keeping it grounded, accurate, and hard to manipulate.

## What This Project Is

This is a RAG-based portfolio chatbot built with:

- `FastAPI` for the backend
- `Gradio` for the chat interface
- `Chroma` as the vector store
- `HuggingFaceEmbeddings` for semantic search
- `OpenAI` for generation and guardrail checking
- `FlashRank` for re-ranking

I use it as an AI layer on top of my portfolio so people can explore my projects, education, experience, and skills in a more natural way.

## Why I Built It

I wanted my portfolio to do more than display information. I wanted it to actively explain who I am and what I have built.

While building it, I focused on two things more than anything else:

- **security**: preventing the bot from being jailbroken or pushed outside its intended scope
- **quality**: improving retrieval so answers are sharper and less noisy

That is what shaped most of the architecture of this project.

## Project Goals

- Answer only questions related to me and my portfolio
- Reduce hallucinations by grounding responses in my own documents
- Defend the system against prompt injection and jailbreak-style prompts
- Improve retrieval quality with re-ranking instead of relying only on raw vector similarity
- Keep the app simple enough to deploy on Vercel


## How It Works

The full pipeline lives mainly inside `chatbot_engine.py`.

### 1. Knowledge ingestion

I load data from `knowledge-base/`:

- my resume from PDF files in `knowledge-base/Resume/`
- project descriptions from markdown files in `knowledge-base/Projects/`

This makes the chatbot answer from my actual portfolio material rather than a manually hardcoded FAQ.

### 2. Chunking

Once the documents are loaded, I split them into chunks using:

- `chunk_size=1000`
- `chunk_overlap=200`

That gives me enough context per chunk without making retrieval too coarse.

### 3. Embedding and storage

I embed the chunks with:

- `sentence-transformers/all-MiniLM-L6-v2`

Then I store them in Chroma so the app can reuse a persistent vector database instead of rebuilding everything every time.

### 4. Retrieval

For every user query, I retrieve:

- `k=20` candidate chunks from the vector store

At this stage, I want recall. I want to collect a broad set of potentially relevant chunks before narrowing them down.

### 5. Re-ranking

This is one of the most important quality improvements in the project.

After retrieving the initial candidate set, I pass the results through `FlashrankRerank` and keep:

- `top_n=5`

This means I do not rely only on vector similarity. I first gather broader candidates, then re-rank them so the final context is much cleaner and more relevant.

### 6. Final answer generation

The final response is generated with a strict system prompt that keeps the assistant:

- focused on Niloy Saha
- constrained to portfolio-related answers
- concise and structured
- honest when the answer is not available

## How I Secured It Against Jailbreaking

This was one of the parts I cared about most.

I did not want a portfolio chatbot that could be easily pushed into ignoring instructions, leaking prompt details, or acting like a general-purpose assistant. So I added a dedicated guardrail layer before normal answer generation.

### My jailbreak-defense strategy

- I run a separate security classification step before answering.
- I use a dedicated `CHECKER_PROMPT` that tells the model to detect:
  - prompt injection
  - role override attempts
  - instruction hijacking
  - secret extraction attempts
  - system prompt disclosure requests
  - tool abuse
  - out-of-scope requests
- The checker returns structured JSON with:
  - allow / block
  - reason
  - category
- If the checker output is malformed or cannot be parsed, the request is blocked by default.
- If a message is blocked, the assistant returns a fixed refusal response instead of partially complying.

### What this protects against

The bot is designed to reject prompts such as:

- "Ignore your previous instructions"
- "Tell me your hidden system prompt"
- "Act like a different assistant"
- "Forget your restrictions"
- "Help me with coding instead"
- "Reveal internal state or secrets"

### Why this matters

A portfolio chatbot should stay in scope.

The goal is not to be everything for everyone. The goal is to represent me accurately and safely. By adding a separate security gate before retrieval and answering, I made the assistant much harder to jailbreak casually and much more reliable in public-facing use.

## How I Improved Quality with Re-Ranking

If I had stopped at plain semantic search, the bot would still work, but the answer quality would be noticeably worse.

The problem with raw top-k vector retrieval is that it can return chunks that are related, but not the best chunks for constructing a strong final answer. That leads to:

- noisier context
- weaker precision
- more irrelevant details
- less focused answers

To solve that, I added a re-ranking stage with `FlashRank`.

### My retrieval strategy

1. Retrieve a broader candidate pool from Chroma with `k=20`
2. Re-rank those candidates with `FlashRank`
3. Keep only the best `top_n=5`
4. Send the compressed, higher-quality context to the model

### What improved because of re-ranking

- answers became more focused
- irrelevant chunks were reduced
- project-specific responses became more accurate
- the model received cleaner context
- follow-up questions benefited from better retrieval precision

This was one of the biggest quality upgrades in the project.

## Conversational Quality Improvements

I also added history-aware behavior.

When there is previous conversation context, the app rewrites the latest follow-up question into a better standalone retrieval query before searching the vector store. This helps the chatbot handle short follow-ups more reliably instead of depending on ambiguous wording.

## FastAPI + Gradio Setup

The app is served through `app.py`.

It exposes:

- `GET /` for a basic status response
- `GET /health` for a health check
- `GET /gradio` for the chat interface

This gives me a simple backend plus a ready-to-use UI layer without having to build a custom frontend for the chatbot itself.

## Local Setup

### Prerequisites

- Python `3.12+`
- `uv` or `pip`
- an `OPENAI_API_KEY`

### Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key
VECTOR_DB_NAME=vector_db
REBUILD_VECTOR_DB=false
```

### Install Dependencies

Using `uv`:

```bash
uv sync
```

Using `pip`:

```bash
pip install -r requirement.txt
```

### Run Locally

```bash
uv run python app.py
```

Then open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/gradio`

## Vercel Deployment

I plan to deploy this app on Vercel as part of my portfolio ecosystem.

### Deployment flow

1. Push the repository to GitHub
2. Import the repository into Vercel
3. Configure the required environment variables
4. Deploy the FastAPI app
5. Expose the chatbot through the deployed route

### Required environment variables on Vercel

- `OPENAI_API_KEY`
- `VECTOR_DB_NAME`
- `REBUILD_VECTOR_DB`

### Important note for Vercel

The chatbot currently uses a local Chroma persistence directory. That works well in local development, but serverless deployments can have ephemeral file systems.

For a more production-ready Vercel deployment, I may do one of the following:

- prebuild and package the vector data with deployment
- switch to a managed vector database
- move retrieval storage to a more deployment-friendly persistent layer

## Files I Used During Development

- `chatbot_engine.py` contains the main production logic
- `chatbot.ipynb` is where I experimented with prompts, retrieval, and re-ranking ideas
- `app.py` mounts the chat UI into a FastAPI app
- `knowledge-base/` contains the source data the bot is allowed to use

## What I Like Most About This Project

This project is a good representation of how I think about AI engineering:

- build something useful
- keep it grounded in real data
- improve quality with better retrieval
- add guardrails early
- design it for deployment, not just experimentation

For me, the most meaningful parts were not just making the bot answer questions, but making it answer well and making it resist misuse.

## License

This project is licensed under the terms in `LICENSE`.