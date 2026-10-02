import os
from dotenv import load_dotenv
from google import genai
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

load_dotenv()

# --- Chunk config (change these between runs) ---
CHUNK_SIZE = 200     # try 50, 100, 200
OVERLAP = 40         # try 10, 20, 40

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


def chunk_text(text, chunk_size=200, overlap=50):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start = end - overlap
    return chunks


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


# --- The long document (from Day 4) ---
LONG_DOC = """
Retrieval-Augmented Generation (RAG) is a technique that combines information retrieval with large language model generation. The core idea is simple: instead of relying on the LLM's internal knowledge alone, you retrieve relevant documents from an external knowledge base and pass them to the LLM as context.

A RAG pipeline has three main stages. First, ingestion: documents are loaded, split into chunks, embedded into vectors, and stored in a vector database. Second, retrieval: a user query is embedded, and the system searches the vector database for the most similar chunks. Third, generation: the retrieved chunks are passed to the LLM along with the query, and the LLM generates an answer grounded in the retrieved context.

Chunking is a critical part of the ingestion stage. If chunks are too large, they contain multiple topics and the embedding becomes a blurred average of everything. If chunks are too small, they lose context and the retrieved fragment may not answer the question. A common approach is to use chunk sizes of 256 to 512 tokens with 10 to 20 percent overlap between chunks.

Overlap matters because it prevents information from being cut off at chunk boundaries. If a sentence spans two chunks, overlap ensures the full meaning appears in at least one chunk. Without overlap, retrieval quality drops on queries that depend on cross-boundary context.

Vector databases like Qdrant store embeddings and support fast similarity search. Cosine similarity is the most common distance metric. BM25 is a keyword-based ranking function that complements vector search by matching exact terms. Hybrid retrieval combines both: BM25 catches exact matches that embeddings miss, and embeddings catch semantic matches that BM25 misses.
"""


# --- Add chunked pieces of long doc to documents ---
long_doc_chunks = chunk_text(LONG_DOC, chunk_size=CHUNK_SIZE, overlap=OVERLAP)
documents.extend(long_doc_chunks)

print(f"\n{'='*60}")
print(f"CHUNK CONFIG: size={CHUNK_SIZE}, overlap={OVERLAP}")
print(f"Long doc produced {len(long_doc_chunks)} chunks")
print(f"Total documents in index: {len(documents)}")
print(f"{'='*60}\n")


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
        "What is chunking?",
        "Chunk overlap",
        "Hybrid retrieval",
    ]

    for q in queries:
        rag(q)