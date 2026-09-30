# Failure Log — Day 4

**Date:** 30-09-26
**Project:** DocMind
**Stage:** Day 4 — long document baseline (no chunking)

---

## Setup

- 8 documents in Qdrant (added 1 long document)
- Long document: ~400 words covering RAG, chunking, overlap, vector DBs, BM25, hybrid retrieval
- Long doc stored as a single chunk
- Same pipeline: all-MiniLM-L6-v2 + Qdrant + Gemini 1.5 Flash

---

## Test Queries Added

- "What is chunking?"
- "Chunk overlap"
- "Hybrid retrieval"

---

## Observation 1: The long chunk ranks #1 for every sub-topic query

For all three queries, the same chunk — the entire long document — ranked #1.

Scores:

- "What is chunking?" → 0.4533
- "Chunk overlap" → 0.4208
- "Hybrid retrieval" → 0.5103

The system has no way to distinguish which part of the long document matters. It returns the whole thing and hopes the LLM finds the answer.

---

## Observation 2: The LLM is doing the heavy lifting

Gemini answered all three queries correctly because it read the entire long chunk and extracted the relevant paragraph.

This works today because the chunk is short enough (~400 words) for the LLM to process.

It will fail on real documents.

A 50-page PDF embedded as one vector would:

- Blur the embedding (average of many topics)
- Score low on all specific queries
- Force the LLM to process huge context with mostly irrelevant content

---

## Observation 3: Score gap collapses on specific queries

Query: "Hybrid retrieval"

Rank 1: 0.5103 (long doc)
Rank 2: 0.4873 (vector database chunk)
Gap: 0.023

0.023 is essentially noise. The retrieval system has zero confidence about which chunk is correct.

Compare to Day 2's clean separation:
Rank 1: 0.7775
Rank 2: 0.4880
Gap: 0.29

When a chunk contains a single focused topic, retrieval is confident. When a chunk contains many topics, retrieval is uncertain.

---

## What This Tells Me

1. **Chunking is not optional.** It is the difference between working and not working at scale.

2. **The LLM is masking a retrieval problem.** Gemini reads the entire chunk and finds the answer. It looks like retrieval worked. It did not.

3. **Score gap is a diagnostic tool.** A small gap = retrieval is uncertain. A large gap = retrieval is confident.

4. **This pipeline will fail on real documents.** A 50-page PDF as one chunk would return garbage.

---

## Next Experiment (Day 5)

Actually chunk the long document into 200-word pieces with 40-word overlap.

Re-run the same three queries.

Compare:

- Which chunk ranks #1 for each query
- Score of the top chunk before vs after
- Whether the answer becomes more specific

Hypothesis: chunking will increase the top-1 score because each chunk is more focused. The correct chunk will outrank the others with a clear gap.

---

## Honest Summary

Today's run established the baseline. The system works, but only because the long document is short enough that the LLM can process it entirely.

This is not retrieval. This is the LLM doing the work.

The next experiment will show whether real chunking fixes this.
