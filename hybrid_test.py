# hybrid_test.py

import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from rank_bm25 import BM25Okapi

from rag import documents, retrieve, embed, COLLECTION

load_dotenv()

qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY") or None,
)

# --- BM25 index built from the same documents ---
tokenized_docs = [doc.lower().split() for doc in documents]
bm25 = BM25Okapi(tokenized_docs)


def retrieve_vector(query, top_k=10):
    """Return list of {text, score} sorted by vector similarity."""
    results = retrieve(query, top_k=top_k)
    return [
        {"text": r.payload["text"], "score": float(r.score)}
        for r in results
    ]


def retrieve_bm25(query, top_k=10):
    """Return list of {text, score} sorted by BM25."""
    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)
    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
    return [
        {"text": documents[i], "score": float(s)}
        for i, s in ranked[:top_k]
    ]


def rrf_fuse(ranked_lists, k=60):
    """
    Reciprocal Rank Fusion.
    Takes multiple ranked lists (each item has 'text').
    Returns a single ranked list of {text, score}.
    """
    fused_scores = {}
    for ranked in ranked_lists:
        for rank, item in enumerate(ranked, start=1):
            text = item["text"]
            fused_scores[text] = fused_scores.get(text, 0) + 1.0 / (k + rank)

    fused = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
    return [{"text": t, "score": s} for t, s in fused]


def retrieve_hybrid(query, top_k=3):
    """Vector + BM25 combined with RRF, return top_k."""
    vector_results = retrieve_vector(query, top_k=10)
    bm25_results = retrieve_bm25(query, top_k=10)
    fused = rrf_fuse([vector_results, bm25_results])
    return fused[:top_k]


# --- Evaluation ---
eval_set = [
    {"query": "What is a vector database?",  "keyword": "stores and indexes high-dimensional"},
    {"query": "What is Qdrant?",              "keyword": "written in Rust"},
    {"query": "How does BM25 work?",          "keyword": "term frequency"},
    {"query": "What is RAG?",                 "keyword": "Retrieval-Augmented Generation"},
    {"query": "What is FastAPI?",             "keyword": "web framework"},
    {"query": "What is chunking?",            "keyword": "ingestion stage"},
    {"query": "What is chunk overlap?",       "keyword": "cut off at chunk boundaries"},
    {"query": "What is hybrid retrieval?",    "keyword": "BM25 catches exact matches"},
    {"query": "What are embeddings?",         "keyword": "dense vector representations"},
    {"query": "What is LangGraph?",           "keyword": "stateful multi-actor"},
]


def evaluate(fn, name, top_k=3):
    hits_at_1 = 0
    hits_at_3 = 0
    reciprocal_ranks = []

    print(f"\n{'='*70}")
    print(f"MODE: {name}")
    print(f"{'='*70}")

    for item in eval_set:
        query = item["query"]
        keyword = item["keyword"]
        results = fn(query, top_k=top_k)

        rank_found = None
        for rank, r in enumerate(results, start=1):
            if keyword.lower() in r["text"].lower():
                rank_found = rank
                break

        if rank_found == 1:
            hits_at_1 += 1
        if rank_found is not None and rank_found <= 3:
            hits_at_3 += 1
        reciprocal_ranks.append(1.0 / rank_found if rank_found else 0.0)

        marker = "correct" if rank_found == 1 else ("late" if rank_found else "miss")
        print(f"  {query:<42}{str(rank_found):<8}{marker:<10}")

    n = len(eval_set)
    p1 = hits_at_1 / n
    p3 = hits_at_3 / n
    mrr = sum(reciprocal_ranks) / n

    print(f"\n  Precision@1: {p1:.2f}")
    print(f"  Precision@3: {p3:.2f}")
    print(f"  MRR: {mrr:.4f}")

    return {"precision@1": p1, "precision@3": p3, "mrr": mrr}


if __name__ == "__main__":
    print("\nRunning hybrid retrieval evaluation...")
    evaluate(retrieve_vector, "VECTOR")
    evaluate(retrieve_bm25, "BM25")
    evaluate(retrieve_hybrid, "HYBRID")