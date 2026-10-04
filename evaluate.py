
from rag import rag, retrieve, setup_collection                          # import the retrieve function from rag.py
from rag import embed                               # import embed function if needed

# --- Evaluation set ---
# Each entry: a query + a keyword that must appear in the correct chunk
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


def evaluate_retrieval(eval_set, top_k=3):
    # Counters for how many queries were correct at rank 1 and rank 3
    hits_at_1 = 0
    hits_at_3 = 0

    # Reciprocal ranks for every query, used to compute MRR at the end
    reciprocal_ranks = []

    print(f"\n{'='*70}")
    print(f"{'Query':<42}{'Rank':<8}{'Result':<10}")
    print(f"{'='*70}")

    for item in eval_set:
        query = item["query"]
        keyword = item["keyword"]

        # Retrieve top_k chunks for this query
        results = retrieve(query, top_k=top_k)

        # Find which rank contains the keyword
        rank_found = None
        for rank, r in enumerate(results, start=1):
            text = r.payload["text"].lower()
            if keyword.lower() in text:
                rank_found = rank
                break

        # Update counters
        if rank_found == 1:
            hits_at_1 += 1
        if rank_found is not None and rank_found <= 3:
            hits_at_3 += 1

        # Update reciprocal rank
        if rank_found is not None:
            reciprocal_ranks.append(1.0 / rank_found)
        else:
            reciprocal_ranks.append(0.0)

        # Print this query's row
        if rank_found == 1:
            marker = "correct"
        elif rank_found is not None:
            marker = "late"
        else:
            marker = "miss"
        print(f"{query:<42}{str(rank_found):<8}{marker:<10}")

    # Compute final metrics
    n = len(eval_set)
    precision_at_1 = hits_at_1 / n
    precision_at_3 = hits_at_3 / n
    mrr = sum(reciprocal_ranks) / n

    print(f"\n{'-'*70}")
    print(f"Precision@1 : {precision_at_1:.2f}")
    print(f"Precision@3 : {precision_at_3:.2f}")
    print(f"MRR         : {mrr:.4f}")
    print(f"{'-'*70}")

    return {
        "precision@1": precision_at_1,
        "precision@3": precision_at_3,
        "mrr": mrr,
    }


if __name__ == "__main__":
    setup_collection()
    evaluate_retrieval(eval_set, top_k=3)