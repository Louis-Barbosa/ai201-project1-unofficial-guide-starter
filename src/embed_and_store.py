"""
Milestone 4 — Embedding + vector storage + retrieval.
================================================================================

WHAT THIS SCRIPT DOES (the big picture)
---------------------------------------
1. LOAD     : reads the chunk records produced by chunk_documents.py (chunks.json).
2. EMBED    : turns each chunk's text into a vector (a list of numbers) using the
              all-MiniLM-L6-v2 model from sentence-transformers. Chunks with
              similar meaning end up with vectors that point in similar directions.
3. STORE    : saves those vectors — plus each chunk's text and source metadata —
              into a ChromaDB collection on disk (vectorstore/), so we only have
              to embed the documents once.
4. RETRIEVE : given a question, embed it the SAME way and ask ChromaDB for the
              Top-K (=5) chunks whose vectors are closest to the question's vector.

WHY all-MiniLM-L6-v2 + Top-K = 5 (from planning.md)
---------------------------------------------------
    embedding model : all-MiniLM-L6-v2  (small, fast, runs locally, 384-dim vectors)
    top_k           : 5 chunks per query (tight enough to stay relevant; can be
                      tuned later if answers come out thin or noisy)

Common ways to run it:

    python src/embed_and_store.py                 # build the vector store from chunks.json
    python src/embed_and_store.py --rebuild       # wipe and rebuild the collection
    python src/embed_and_store.py --query "is harvard math hard?"   # test retrieval
"""

from __future__ import annotations

# --- standard library imports ------------------------------------------------
import argparse          # parses command-line flags like --query / --rebuild
import json              # reads chunks.json back into Python objects
from pathlib import Path # tidy, OS-independent file paths

# --- third-party imports -----------------------------------------------------
# These come from requirements.txt (sentence-transformers, chromadb). They are
# imported lazily inside functions where possible so that simply importing this
# module (e.g. from the Milestone 5 UI) stays cheap.
import chromadb                                   # the on-disk vector database
from sentence_transformers import SentenceTransformer   # the embedding model


# --------------------------------------------------------------------------- #
# Paths and constants — where things live and which model/collection we use.
# --------------------------------------------------------------------------- #
# __file__ is this script (src/embed_and_store.py). .parent.parent climbs from
# src/ up to the project root, so paths work no matter where you run from.
ROOT = Path(__file__).resolve().parent.parent
CHUNKS_PATH = ROOT / "chunks.json"        # input: the chunks from Milestone 3
VECTORSTORE_DIR = ROOT / "vectorstore"    # output: ChromaDB's on-disk files

EMBED_MODEL_NAME = "all-MiniLM-L6-v2"     # the sentence-transformers model id
COLLECTION_NAME = "guide_chunks"          # name of the collection inside ChromaDB
DEFAULT_TOP_K = 5                         # how many chunks retrieval returns


# --------------------------------------------------------------------------- #
# Model loading — cache the model so we only build it once per process.
# --------------------------------------------------------------------------- #
# Loading a SentenceTransformer reads model weights off disk (and downloads them
# the first time), which is slow. We keep the loaded model in a module-level
# variable so repeated calls (e.g. embedding documents, then embedding queries)
# reuse the same object instead of reloading it every time.
_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    """Return the all-MiniLM-L6-v2 model, loading it on first use only."""
    global _model
    if _model is None:
        # The first call downloads the model (~80 MB) to a local cache; later
        # calls and later runs reuse that cached copy.
        _model = SentenceTransformer(EMBED_MODEL_NAME)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Turn a list of strings into a list of embedding vectors.

    Each returned vector is a list of 384 floats (all-MiniLM-L6-v2's size).
    We convert to plain Python lists because that is what ChromaDB expects.
    """
    model = get_model()
    # convert_to_numpy keeps encoding fast; .tolist() hands ChromaDB plain lists.
    vectors = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return vectors.tolist()


# --------------------------------------------------------------------------- #
# ChromaDB — open (or create) the on-disk database and collection.
# --------------------------------------------------------------------------- #
def get_collection(rebuild: bool = False) -> "chromadb.api.models.Collection.Collection":
    """Return the ChromaDB collection we store chunk vectors in.

    chromadb.PersistentClient(path=...) opens a database that lives on disk in
    VECTORSTORE_DIR, so the vectors survive between runs (unlike an in-memory
    client). get_or_create_collection returns the collection if it already
    exists, or makes a new one if it doesn't.

    We pass metadata={"hnsw:space": "cosine"} so ChromaDB measures distance with
    cosine similarity — the right choice for sentence-transformers embeddings,
    where what matters is the *direction* of a vector, not its length.

    rebuild=True deletes any existing collection first, giving a clean slate
    (useful after you re-chunk and want to re-embed everything).
    """
    client = chromadb.PersistentClient(path=str(VECTORSTORE_DIR))

    if rebuild:
        # delete_collection raises if it doesn't exist, so guard it.
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


# --------------------------------------------------------------------------- #
# Build — load chunks, embed them, and store them in ChromaDB.
# --------------------------------------------------------------------------- #
def load_chunks(path: Path = CHUNKS_PATH) -> list[dict]:
    """Read the chunk records written by chunk_documents.py."""
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Run `python src/chunk_documents.py` first to "
            f"create it."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def build_store(chunks_path: Path = CHUNKS_PATH, rebuild: bool = False) -> int:
    """Embed every chunk and store it in ChromaDB. Returns the chunk count.

    ChromaDB's collection.add() takes four parallel lists, all the same length:
      * ids        — a unique string per chunk (we reuse the chunk's own id).
      * embeddings — the vector for each chunk (from embed_texts()).
      * documents  — the raw chunk text (so retrieval can hand it back to us).
      * metadatas  — a dict per chunk of extra info we want to keep, e.g. which
                     source file it came from and its position in that file.
    """
    records = load_chunks(chunks_path)
    collection = get_collection(rebuild=rebuild)

    # Pull the four parallel lists out of the chunk records.
    ids = [r["id"] for r in records]
    documents = [r["text"] for r in records]
    metadatas = [
        {
            "source": r["source"],            # which document the chunk came from
            "chunk_index": r["chunk_index"],  # its position within that document
            "char_count": r["char_count"],    # handy for inspection
        }
        for r in records
    ]

    # Embed all the chunk texts in one batch (faster than one call per chunk).
    embeddings = embed_texts(documents)

    # upsert (instead of add) means re-running on the same ids updates them
    # rather than erroring on a duplicate id — safe to run repeatedly.
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )
    return len(records)


# --------------------------------------------------------------------------- #
# Retrieve — the function the answer-generation step (Milestone 5) will call.
# --------------------------------------------------------------------------- #
def retrieve(query: str, top_k: int = DEFAULT_TOP_K) -> list[dict]:
    """Return the ``top_k`` chunks most relevant to ``query``.

    Steps:
      1. Embed the query with the SAME model used for the chunks. (Using the same
         model is essential — vectors from different models aren't comparable.)
      2. Ask ChromaDB for the nearest stored vectors via collection.query().
      3. Repackage Chroma's columnar result into a simple list of dicts, one per
         retrieved chunk, each carrying its text + source info + a relevance score.

    Each returned dict looks like:
        {
            "text":        "<the chunk text>",
            "source":      "Reputation.txt",
            "chunk_index": 3,
            "distance":    0.41,   # cosine distance: smaller = more relevant
            "similarity":  0.59,   # 1 - distance, so larger = more relevant
        }
    The list is ordered from most to least relevant.
    """
    collection = get_collection()

    # Embed the query. embed_texts takes a list, so wrap it and take [0].
    query_embedding = embed_texts([query])[0]

    # n_results=top_k asks Chroma for the K nearest vectors. include= says which
    # stored fields we want back alongside the ids (documents, metadata, the
    # cosine distances). Chroma returns each field as a list-of-lists because it
    # supports several queries at once; we sent one query, so we read index [0].
    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    documents = result["documents"][0]
    metadatas = result["metadatas"][0]
    distances = result["distances"][0]

    # zip(...) walks the three parallel lists together, one retrieved chunk at a
    # time, so we can bundle each chunk's text, metadata, and distance into a dict.
    hits: list[dict] = []
    for text, meta, distance in zip(documents, metadatas, distances):
        hits.append({
            "text": text,
            "source": meta.get("source"),
            "chunk_index": meta.get("chunk_index"),
            "distance": distance,
            "similarity": 1 - distance,   # convenience: higher = closer
        })
    return hits


# --------------------------------------------------------------------------- #
# Display helper — pretty-print retrieved chunks while developing.
# --------------------------------------------------------------------------- #
def print_hits(query: str, hits: list[dict]) -> None:
    """Print retrieval results in a readable way for manual testing."""
    print("=" * 72)
    print(f"QUERY: {query}")
    print("=" * 72)
    if not hits:
        print("(no results — is the vector store built?)")
        return
    for rank, h in enumerate(hits, start=1):
        print(f"#{rank}  source={h['source']}  chunk={h['chunk_index']}  "
              f"similarity={h['similarity']:.3f}")
        print(h["text"])
        print("-" * 72)


# --------------------------------------------------------------------------- #
# main — what runs when you execute this file from the command line.
# --------------------------------------------------------------------------- #
def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--chunks", type=Path, default=CHUNKS_PATH,
                        help="path to chunks.json (default: chunks.json)")
    parser.add_argument("--rebuild", action="store_true",
                        help="wipe the existing collection and re-embed from scratch")
    parser.add_argument("--query", type=str, default=None,
                        help="run a retrieval test with this question and exit")
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K,
                        help=f"how many chunks to retrieve (default: {DEFAULT_TOP_K})")
    args = parser.parse_args()

    # --query mode: just test retrieval against the already-built store.
    if args.query is not None:
        hits = retrieve(args.query, top_k=args.top_k)
        print_hits(args.query, hits)
        return

    # Normal mode: build (or rebuild) the vector store from chunks.json.
    count = build_store(args.chunks, rebuild=args.rebuild)
    print(f"Embedded and stored {count} chunks -> {VECTORSTORE_DIR}")
    print(f"Collection: '{COLLECTION_NAME}'  |  model: {EMBED_MODEL_NAME}")


# This guard means main() only runs when the file is executed directly, not when
# retrieve()/build_store() are imported by the Milestone 5 query interface.
if __name__ == "__main__":
    main()
