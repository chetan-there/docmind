# DocMind

A Hybrid RAG + Agentic AI system — built in public, one feature at a time.

**Status:** Day 1 — basic vector-search RAG pipeline working.

---

## What This Is

DocMind is a retrieval-augmented generation system that I'm building from scratch to understand how production AI systems actually work.

It starts simple (embed → search → generate) and grows into a hybrid retrieval + agentic workflow system over time.

This repo is a build log, not a finished product.

---

## Current Architecture (Day 1)

```
Query
  ↓
Embed (all-MiniLM-L6-v2)
  ↓
Qdrant vector search (top-3, cosine)
  ↓
Gemini 1.5 Flash
  ↓
Answer
```

---

## What Works Right Now

- Local embeddings with `all-MiniLM-L6-v2` (384 dims)
- Qdrant vector storage and cosine similarity search
- Top-3 chunk retrieval
- Gemini 1.5 Flash generation with retrieved context
- Tested on 5 sample queries

---

## What I Already Found Broken

Retrieval returns **semantically similar** chunks, not **answer-bearing** chunks.

Example failure:

```
Query: "What is a vector database?"

Top retrieved chunk:
  "Qdrant is a vector database written in Rust..."

Problem:
  This chunk MENTIONS vector databases but doesn't DEFINE them.
  The system had no chunk that actually answered the question.

Gemini response:
  "The context does not define what a vector database is."
```

The gap between "similar" and "answering" is the real retrieval problem. Fixing this is the next phase.

See [`evidence/failure_log.md`](evidence/failure_log.md) for details.

---

## Tech Stack

- Python 3.11+
- [Qdrant](https://qdrant.tech/) — vector database
- [sentence-transformers](https://www.sbert.net/) — local embeddings
- [Google Gemini](https://ai.google.dev/) — LLM generation
- [uv](https://github.com/astral-sh/uv) — dependency management

---

## Setup

### 1. Clone

```bash
git clone https://github.com/yourusername/docmind.git
cd docmind
```

### 2. Install dependencies

```bash
uv sync
```

Or with pip:

```bash
pip install qdrant-client sentence-transformers google-generativeai python-dotenv
```

### 3. Configure environment

Copy `.env.example` to `.env` and fill in:

```bash
GEMINI_API_KEY=your_key_here
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_key
```

Get a free Gemini key: https://aistudio.google.com/apikey
Get a free Qdrant cluster: https://cloud.qdrant.io

### 4. Run

```bash
uv run rag.py
```

---

## Project Structure

```
docmind/
├── rag.py                 # Day 1 pipeline
├── evidence/
│   ├── day1_output.txt    # Terminal output from first run
│   └── failure_log.md     # Documented retrieval failures
├── .env.example
├── .gitignore
└── README.md
```

Will grow into:

```
docmind/
├── app/                   # FastAPI backend
├── retrieval/             # BM25 + vector + hybrid ranking
├── agent/                 # LangGraph workflow
├── evaluation/            # Retrieval metrics
├── frontend/              # React UI
└── docs/                  # Architecture diagrams
```

---

## Roadmap

- [x] Day 1 — Basic vector-search RAG
- [ ] Chunking strategy experiments
- [ ] BM25 retrieval
- [ ] Hybrid ranking (RRF)
- [ ] Retrieval evaluation (precision@k, recall)
- [ ] Tool calling
- [ ] LangGraph agent workflow
- [ ] FastAPI backend
- [ ] Async + streaming
- [ ] React frontend
- [ ] Production thinking (latency, cost, guardrails)

---

## Known Limitations

- Only 6 test documents
- No chunking — documents are single chunks
- No BM25 or hybrid retrieval yet
- No evaluation metrics
- No API — runs as a script
- Uses `generate_content` instead of `Chat.send_message` (Gemini warns about this)

---

## Why This Repo Exists

I'm a 2026 Computer Engineering graduate building toward AI Engineer roles.

Instead of copying tutorials, I'm building one real system, breaking it, fixing it, and documenting the engineering story.

Every commit is a real step. Every failure is documented. No fake metrics.

---

## Connect

- LinkedIn: [your profile]
- GitHub: [your profile]
