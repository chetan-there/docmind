# Retrieval Evaluation — Day 7

## Evaluation set

10 queries, each with a known keyword that must appear in the correct chunk.

## Results

### 50/10 config

- Precision@1: 0.90
- Precision@3: 1.00
- MRR: 0.9500

### 100/20 config

- Precision@1: 0.90
- Precision@3: 1.00
- MRR: 0.9500

### 200/40 config

Not evaluated with Day 7 script.

## Observation

Both 50/10 and 100/20 achieved identical retrieval metrics.
Chunk size does not affect retrieval correctness on this eval set,
but did affect score confidence (Day 6).

## Failed queries

"What is chunk overlap?" — rank 2 in both configs.
