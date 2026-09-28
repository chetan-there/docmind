# Failure Log — Day 2

**Date:** 28-09-26
**Project:** DocMind
**Stage:** Day 2 — added definition chunk, re-tested pipeline

---

## Setup

- 7 test documents stored in Qdrant (added 1 new chunk)
- Embedding model: `all-MiniLM-L6-v2` (384 dimensions, local)
- Retrieval: top-3 by cosine similarity
- Generation: Gemini 1.5 Flash
- No chunking — each document is a single chunk
- No BM25, no hybrid ranking, no re-ranking

**Change from Day 1:**

Added one new document that explicitly defines "vector database":

> "A vector database is a database that stores and indexes high-dimensional vectors for similarity search. It is used in RAG systems to retrieve relevant text by embedding similarity."

---

## Hypothesis Before Running

If the Day 1 failure was a **coverage problem** (the answer was not in the index), then adding a chunk that defines "vector database" should fix the query.

If the failure was a **ranking problem** (the answer existed but ranked low), adding a chunk would not fix it.

---

## What Worked

- All 5 queries now return correct answers
- The new chunk ranked #1 for "What is a vector database?" with a score of 0.7775
- Gemini's answer is now directly sourced from the retrieved context
- Score separation improved significantly

---

## What Changed

### Query: "What is a vector database?"

**Before (Day 1):**

| Rank | Score  | Chunk                                                                                            |
| ---- | ------ | ------------------------------------------------------------------------------------------------ |
| 1    | 0.4880 | "Qdrant is a vector database written in Rust. It supports filtering and payload storage."        |
| 2    | 0.3694 | "Embeddings are dense vector representations of text. Similar meanings produce similar vectors." |
| 3    | 0.2300 | "LangGraph is a library for building stateful multi-actor applications with LLMs."               |

**Gemini response:**

> "The provided context states that 'Qdrant is a vector database written in Rust'... However, the context does not define what a vector database is."

**After (Day 2):**

| Rank | Score  | Chunk                                                                                                       |
| ---- | ------ | ----------------------------------------------------------------------------------------------------------- |
| 1    | 0.7775 | "A vector database is a database that stores and indexes high-dimensional vectors for similarity search..." |
| 2    | 0.4880 | "Qdrant is a vector database written in Rust. It supports filtering and payload storage."                   |
| 3    | 0.3694 | "Embeddings are dense vector representations of text. Similar meanings produce similar vectors."            |

**Gemini response:**

> "A vector database is a database that stores and indexes high-dimensional vectors for similarity search."

---

## Analysis

### 1. Coverage problem confirmed

The Day 1 failure was not a retrieval algorithm problem. The answer simply did not exist in the index. Once a chunk containing the answer was added, retrieval found it at rank 1 with high confidence (0.7775).

This confirms the hypothesis: **RAG cannot retrieve what is not in the index.** No model upgrade, no chunking strategy, and no ranking algorithm fixes missing information.

### 2. Score gap improved

|              | Day 1  | Day 2  |
| ------------ | ------ | ------ |
| Rank 1 score | 0.4880 | 0.7775 |
| Rank 2 score | 0.3694 | 0.4880 |
| Gap          | 0.12   | 0.29   |

When the correct chunk exists, retrieval has strong confidence and clear separation. When it does not, scores are low and close together.

The score gap is a signal. A small gap means "no confident match found." A large gap means "the right answer exists and was found."

### 3. Side effect: adding one chunk shifted rankings for other queries

**Query: "What is RAG?"**

Before (Day 1):

| Rank | Score  | Chunk                                              |
| ---- | ------ | -------------------------------------------------- |
| 1    | 0.7174 | "RAG stands for Retrieval-Augmented Generation..." |
| 2    | 0.1737 | "Qdrant is a vector database written in Rust..."   |
| 3    | 0.1200 | "FastAPI is a modern Python web framework..."      |

After (Day 2):

| Rank | Score  | Chunk                                              |
| ---- | ------ | -------------------------------------------------- |
| 1    | 0.7174 | "RAG stands for Retrieval-Augmented Generation..." |
| 2    | 0.2154 | "A vector database is a database that stores..."   |
| 3    | 0.1737 | "Qdrant is a vector database written in Rust..."   |

The new chunk appeared at rank 2 for a query it was not written for. Reason: the new chunk mentions "RAG systems" in its text. The embedding model picked up that shared vocabulary.

**Observation:** Retrieval is not isolated per query. Adding one chunk affects ranking across the entire collection because embeddings capture shared vocabulary between chunks.

---

## What This Tells Me

1. **Retrieval quality is a coverage problem first, ranking problem second.** Fix the index before tuning the algorithm.

2. **Score gap is a diagnostic signal.** Use it to detect when retrieval is uncertain.

3. **Embedding models are sensitive to shared vocabulary.** One chunk mentioning another chunk's topic can shift rankings for unrelated queries.

4. **Adding documents changes retrieval behavior globally.** This will matter more as the document set grows.

5. **The LLM was never the problem.** Gemini said "I don't know" when context was missing and answered correctly when context was present. The LLM is doing its job correctly.

---

## Next Experiments (Not Today)

- Test chunking: split documents into smaller pieces. Does retrieval improve or degrade?
- Add BM25 — does exact keyword matching help?
- Implement Reciprocal Rank Fusion — does combining BM25 + vector beat either alone?
- Build an evaluation script — measure precision@k on 20 queries
- Test what happens when the document set grows to 50+ chunks

---

## Honest Summary

Day 2 confirmed that the Day 1 failure was a coverage problem, not a retrieval algorithm problem.

The system now answers all 5 test queries correctly.

But the document set is still only 7 chunks. The interesting problems will start when the document set grows and retrieval has to actually choose between many relevant-looking chunks.

Next phase: BM25, hybrid ranking, and evaluation.
