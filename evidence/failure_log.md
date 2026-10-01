# Failure Log — Day 5

**Date:** 01-10-26
**Project:** DocMind
**Stage:** Day 5 — actual chunking experiment

---

## Setup

- 7 short documents + 4 chunks from long document = 11 total
- Chunk size: 100 words, 20-word overlap
- Same embedding model, same retrieval, same LLM

---

## Before vs After

| Query               | Day 4 (single doc) | Day 5 (chunked) | Change  |
| ------------------- | ------------------ | --------------- | ------- |
| "What is chunking?" | 0.4533             | 0.5459          | +0.0926 |
| "Chunk overlap"     | 0.4208             | 0.5566          | +0.1358 |
| "Hybrid retrieval"  | 0.5103             | 0.5839          | +0.0736 |

All scores improved. Chunking made embeddings more focused.

---

## Observation 1: Scores improved across the board

Every query returned a higher top-1 score after chunking. The system is now more confident when it finds relevant content.

This confirms: smaller, focused chunks produce better embeddings.

---

## Observation 2: Score gap collapsed for multi-chunk concepts

Query: "Hybrid retrieval"

| Rank | Score  | Chunk topic |
| ---- | ------ | ----------- |
| 1    | 0.5839 | chunk sizes |
| 2    | 0.5833 | BM25        |
| 3    | 0.5601 | RAG         |

Gap between rank 1 and rank 2: **0.0006**. The system cannot distinguish which chunk is more relevant.

Reason: "Hybrid retrieval" is a concept that depends on information split across multiple chunks. The chunk talking about chunk sizes mentions "chunks" and "embeddings" — which are semantically close to "hybrid retrieval." The chunk about BM25 mentions "ranking" and "vector search" — also close.

No single chunk defines "hybrid retrieval." The concept is fragmented.

---

## Observation 3: The LLM is now doing cross-chunk synthesis

For "Hybrid retrieval," the answer was correct:

> "Hybrid retrieval combines both: BM25 catches exact matches that embeddings miss, and embeddings catch semantic matches that BM25 misses."

But this answer was not in any single retrieved chunk. Gemini combined information from two chunks (one about BM25, one about chunk sizes) to produce it.

The LLM is patching over a retrieval problem.

---

## Trade-off Confirmed

Chunking:

- **Improves** retrieval for narrow, single-concept queries
- **Weakens** retrieval for cross-chunk concepts

This is the classic RAG chunking trade-off. Smaller chunks = focused retrieval. Larger chunks = context preserved. No single chunk size is optimal for everything.

---

## What This Tells Me

1. **Chunking improves scores, but not uniformly.**
2. **Concepts that span chunks become retrieval problems.**
3. **The LLM hides this by synthesizing across chunks.** It works, but it's fragile.
4. **Chunk size is a tunable parameter.** 100 words is a starting point, not the answer.
5. **The next experiment should compare chunk sizes.** Test 50, 100, 200. Measure.

---

## Next Experiment (Day 6)

Compare chunk sizes:

- 50 words, 10 overlap
- 100 words, 20 overlap (already done)
- 200 words, 40 overlap

For each, run the same 3 queries. Record top-1 score and gap. Find the sweet spot for this document set.

---

## Honest Summary

Chunking worked. Scores went up. But the experiment exposed a new problem: multi-concept queries split across chunks have weak retrieval.

The LLM is compensating by combining chunks. This works today but will not scale.

Next: find the right chunk size through measurement, not guessing.
