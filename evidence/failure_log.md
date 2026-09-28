# Failure Log — Day 1

**Date:** 27-09-26
**Project:** DocMind
**Stage:** Day 1 — basic vector-search RAG pipeline

---

## Setup

- 6 test documents stored in Qdrant
- Embedding model: `all-MiniLM-L6-v2` (384 dimensions, local)
- Retrieval: top-3 by cosine similarity
- Generation: Gemini 1.5 Flash
- No chunking — each document is a single chunk
- No BM25, no hybrid ranking, no re-ranking

---

## What Worked

- Pipeline runs end-to-end without errors
- 4 out of 5 queries returned correct answers
- Top-1 retrieved chunk was correct for queries 1, 2, 3, and 4
- Gemini used the retrieved context and did not hallucinate

---

## What Failed

### Failure 1: Retrieval returns "similar" chunks, not "answering" chunks

**Query:** "What is a vector database?"

**Retrieved chunks:**

| Rank | Score  | Chunk                                                                                            |
| ---- | ------ | ------------------------------------------------------------------------------------------------ |
| 1    | 0.4880 | "Qdrant is a vector database written in Rust. It supports filtering and payload storage."        |
| 2    | 0.3694 | "Embeddings are dense vector representations of text. Similar meanings produce similar vectors." |
| 3    | 0.2300 | "LangGraph is a library for building stateful multi-actor applications with LLMs."               |

**Gemini response:**

> "The provided context states that 'Qdrant is a vector database written in Rust'... However, the context does not define what a vector database is."

**Observation:**

The top chunk MENTIONS vector databases but does not DEFINE them. The system had no chunk that actually answered the question. Retrieval found semantically related text, not answer-bearing text.

**Root cause (hypothesis):**

The document set did not contain a chunk that defines "vector database." The retrieval system can only return what exists in the index. This is a **coverage problem**, not an embedding problem.

**But there is a second issue:**

The score gap between rank 1 (0.4880) and rank 3 (0.2300) is small. The system has weak confidence separation. Even if a defining chunk existed, there is no guarantee it would rank first.

---

### Failure 2: Low confidence scores across the board

**Observed scores across all 5 queries:**

| Query                        | Top-1 score |
| ---------------------------- | ----------- |
| "What is Qdrant?"            | 0.5642      |
| "How does BM25 work?"        | 0.6843      |
| "What is RAG?"               | 0.7174      |
| "Tell me about FastAPI"      | 0.5906      |
| "What is a vector database?" | 0.4880      |

**Observation:**

Even the best matches only reach 0.49–0.72. For `all-MiniLM-L6-v2`, this is expected — it is a small, fast embedding model. But it means "related" is not "confident."

**Implication:**

We cannot rely on cosine score thresholds for filtering. We need better ranking signals (BM25, re-ranking) and better evaluation, not just embedding model swaps.

---

### Failure 3: Irrelevant chunks appear in top-3

**Query:** "What is a vector database?"

Chunk 3 returned "LangGraph is a library for building stateful multi-actor applications with LLMs." This is completely unrelated to the query.

**Observation:**

Top-3 retrieval is returning noise. The system has no mechanism to reject weak matches. Without a score floor or better ranking, top-K will always return K chunks — even when only 1 is relevant.

---

## What This Tells Me

1. **Retrieval quality is the bottleneck, not generation.** Gemini correctly said "I don't know" when the context was insufficient. The LLM is not the problem.

2. **Semantic similarity is not the same as answering.** A chunk can be about the same topic and still not answer the question.

3. **Scores are weak.** Local embeddings produce low-confidence matches on small document sets. This needs measurable evaluation, not vibes.

4. **Coverage matters.** If the answer is not in the index, no retrieval system can find it. This is a design problem, not a model problem.

5. **No evaluation = no improvement.** I currently have no way to measure whether retrieval is getting better. I need precision@k and recall before I change anything.

---

## Next Experiments (Not Today)

- Add a document that defines "vector database" — does retrieval find it?
- Test chunking: split documents into smaller pieces. Does retrieval improve?
- Add BM25 — does exact keyword matching help?
- Implement Reciprocal Rank Fusion — does combining BM25 + vector beat either alone?
- Build an evaluation script — measure precision@k on 20 queries

---

## Honest Summary

Day 1 pipeline works, but the retrieval layer is shallow.

The system retrieves text that is _about_ the topic, not text that _answers_ the question.

This is the first real engineering problem of the project.
