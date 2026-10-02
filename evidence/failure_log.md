# Failure Log — Day 6

**Date:** 02-10-26
**Project:** DocMind
**Stage:** Day 6 — chunk size comparison

---

## Experiment

Tested three chunk sizes on the same 3 queries. Same embedding model, same retrieval, same LLM.

- 50 words / 10 overlap → 7 chunks
- 100 words / 20 overlap → 4 chunks
- 200 words / 40 overlap → 2 chunks

---

## Results

| Query               | 50/10 top score | 100/20 top score | 200/40 top score |
| ------------------- | --------------- | ---------------- | ---------------- |
| "What is chunking?" | **0.5944**      | 0.5459           | 0.4441           |
| "Chunk overlap"     | **0.6470**      | 0.5566           | 0.4120           |
| "Hybrid retrieval"  | 0.5833          | **0.5839**       | 0.5469           |

Score gap (rank 1 − rank 2):

| Query               | 50/10 gap | 100/20 gap | 200/40 gap |
| ------------------- | --------- | ---------- | ---------- |
| "What is chunking?" | 0.0297    | **0.2841** | 0.2019     |
| "Chunk overlap"     | 0.0875    | **0.1424** | 0.0305     |
| "Hybrid retrieval"  | 0.0644    | 0.0006     | 0.0288     |

---

## Observations

**1. Smaller chunks score higher for narrow queries.**
50/10 produced the highest top-1 score for both "What is chunking?" (0.5944) and "Chunk overlap" (0.6470). Smaller chunks produce sharper embeddings that match specific queries more confidently.

**2. Medium chunks have the clearest score gap.**
100/20 produced the largest rank-1 to rank-2 gap for "What is chunking?" (0.2841) and "Chunk overlap" (0.1424). The system is most confident in its top choice with 100-word chunks.

**3. Large chunks blur everything.**
200/40 produced the lowest top-1 scores across all queries. The 2 chunks are too broad. Concepts get diluted.

**4. No chunk size wins everywhere.**
For "Hybrid retrieval," 100/20 and 50/10 tie (0.5839 vs 0.5833). For narrow queries, 50/10 wins on score. For confidence, 100/20 wins.

**5. Bigger chunks collapse the score gap on cross-concept queries.**
At 200/40, "Chunk overlap" had a gap of 0.0305. At 100/20, it was 0.1424. Bigger chunks lose distinction between topics.

---

## What This Tells Me

1. **Chunk size is a tunable parameter that measurably affects retrieval quality.**
2. **There is no universal best chunk size.** It depends on query patterns and document structure.
3. **Score gap is as important as top score.** High score with small gap = uncertain retrieval.
4. **100 words / 20 overlap is a reasonable default** for this document set. It balances top score and confidence.
5. **Real RAG systems need evaluation metrics.** Without measuring, you cannot choose chunk size intelligently.

---

## Next Experiment (Day 7)

Evaluate retrieval properly. Currently I'm eyeballing scores. I need real metrics.

Plan:

- Build a small evaluation set: 10 queries with known correct answers
- Compute precision@k (is the correct chunk in the top k?)
- Compute MRR (mean reciprocal rank — how high does the correct chunk rank?)
- Compare chunk configs using these metrics

This moves from "the scores look better" to "retrieval precision improved by X%."
