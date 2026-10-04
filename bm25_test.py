# bm25_test.py

from rank_bm25 import BM25Okapi

# --- import your documents list and query ---
# Note: for now, we import the documents from rag.py
from rag import documents

# --- Build BM25 index ---
# BM25 needs tokenized documents (list of words per doc)
tokenized_docs = [doc.lower().split() for doc in documents]
bm25 = BM25Okapi(tokenized_docs)

# --- BM25 retrieval function ---
def retrieve_bm25(query, top_k=3):
    # tokenize the query the same way
    tokenized_query = query.lower().split()

    # get BM25 scores for every document
    scores = bm25.get_scores(tokenized_query)

    # sort documents by score, descending
    ranked = sorted(
        enumerate(scores),
        key=lambda x: x[1],
        reverse=True
    )

    # return top_k as (doc_index, score, doc_text)
    results = []
    for doc_idx, score in ranked[:top_k]:
        results.append({
            "index": doc_idx,
            "score": float(score),
            "text": documents[doc_idx],
        })
    return results


# --- Test ---
if __name__ == "__main__":
    test_queries = [
        "What is chunk overlap?",
        "What is BM25?",
        "vector database",
    ]

    for q in test_queries:
        print(f"\n{'='*60}")
        print(f"QUERY: {q}")
        print(f"{'='*60}")
        results = retrieve_bm25(q, top_k=3)
        for r in results:
            print(f"  [score={r['score']:.4f}] {r['text'][:80]}...")