import os
from dotenv import load_dotenv
from google import genai
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

load_dotenv()

# --- Setup Clients ---
client = genai.Client()

qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY") or None,
)

# Load local Hugging Face model (Downloads on first run)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

COLLECTION = "test_docs"
LLM_MODEL = "gemini-2.5-flash"

# --- Sample documents ---
documents = [
    "Qdrant is a vector database written in Rust. It supports filtering and payload storage.",
    "BM25 is a ranking function used in information retrieval. It scores documents based on term frequency.",
    "FastAPI is a modern Python web framework for building APIs. It uses Pydantic for validation.",
    "LangGraph is a library for building stateful multi-actor applications with LLMs.",
    "RAG stands for Retrieval-Augmented Generation. It combines retrieval with LLM generation.",
    "Embeddings are dense vector representations of text. Similar meanings produce similar vectors.",
    "A vector database is a database that stores and indexes high-dimensional vectors for similarity search. It is used in RAG systems to retrieve relevant text by embedding similarity.",
]


# --- Embed and store ---
def embed(text: str) -> list[float]:
    # Returns 384-dimensional float vector locally
    return embedding_model.encode(text).tolist()


def setup_collection():
    # Delete if exists (for clean testing)
    try:
        qdrant.delete_collection(COLLECTION)
    except Exception:
        pass

    # Create collection (384 dimensions for all-MiniLM-L6-v2)
    sample_vector = embed("test")
    qdrant.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(
            size=len(sample_vector), distance=Distance.COSINE
        ),
    )

    # Insert documents
    points = []
    for i, doc in enumerate(documents):
        points.append(
            PointStruct(
                id=i,
                vector=embed(doc),
                payload={"text": doc},
            )
        )
    qdrant.upsert(collection_name=COLLECTION, points=points)
    print(
        f"Inserted {len(points)} documents into Qdrant collection '{COLLECTION}'"
    )


# --- Retrieve ---
def retrieve(query: str, top_k: int = 3):
    query_vector = embed(query)

    results = qdrant.query_points(
        collection_name=COLLECTION,
        query=query_vector,
        limit=top_k,
    )
    return results.points


# --- Generate ---
def generate(query: str, chunks: list[str]) -> str:
    context = "\n\n".join(chunks)
    prompt = f"""Answer the question using only the context below.

Context:
{context}

Question: {query}

Answer:"""

    response = client.models.generate_content(
        model=LLM_MODEL,
        contents=prompt,
    )
    return response.text


# --- Full pipeline ---
def rag(query: str):
    print(f"\n{'='*60}")
    print(f"QUERY: {query}")
    print(f"{'='*60}")

    results = retrieve(query, top_k=3)

    print("\nRETRIEVED CHUNKS:")
    for r in results:
        print(f"  [score={r.score:.4f}] {r.payload['text'][:80]}...")

    chunks = [r.payload["text"] for r in results]
    answer = generate(query, chunks)

    print(f"\nANSWER:\n{answer}")
    return answer


# --- Run ---
if __name__ == "__main__":
    setup_collection()

    queries = [
        "What is Qdrant?",
        "How does BM25 work?",
        "What is RAG?",
        "Tell me about FastAPI",
        "What is a vector database?",
    ]

    for q in queries:
        rag(q)