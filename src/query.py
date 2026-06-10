"""
Milestone 5 — Answer generation grounded in retrieved context.
================================================================================

WHAT THIS SCRIPT DOES (the big picture)
---------------------------------------
This is step #5 of the RAG pipeline:

    #1 ingest -> #2 chunk -> #3 embed/store -> #4 retrieve (Top-K=5) -> #5 GENERATE

Given a question, we:
  1. RETRIEVE : pull the Top-K most relevant chunks from the vector store
                (reusing retrieve() from embed_and_store.py — step #4).
  2. PROMPT   : stitch those chunks into a context block and wrap them in a
                prompt that *explicitly* tells the LLM to answer ONLY from that
                context, and to say so when the context is insufficient.
  3. GENERATE : send the prompt to Groq's llama-3.3-70b-versatile model and read
                back the answer.
  4. ATTRIBUTE: return both the answer AND the list of source documents the
                answer was grounded in, so every response is traceable.

WHY "answer only from context" matters
---------------------------------------
A plain LLM will happily answer from its own training data, which may be wrong,
out of date, or invented (a "hallucination"). The whole point of RAG is that the
answer is *grounded* in documents we control and can cite. The prompt below is
what enforces that — it is the single most important part of this file.

HOW TO RUN
----------
    python src/query.py "Is the Princeton math program hard?"
    python src/query.py "..." --top-k 3

Or import ask() from the UI (app.py):
    from query import ask
    result = ask("your question")     # -> {"answer": ..., "sources": [...], "hits": [...]}
"""

from __future__ import annotations

# --- standard library imports ------------------------------------------------
import argparse
import os
from pathlib import Path

# --- third-party imports -----------------------------------------------------
from dotenv import load_dotenv     # reads GROQ_API_KEY out of the .env file
from groq import Groq              # the OpenAI-compatible Groq client

# Step #4 lives in embed_and_store.py — we reuse its retrieve() unchanged so the
# generation step and the retrieval test share exactly the same code path.
from embed_and_store import retrieve, DEFAULT_TOP_K


# --------------------------------------------------------------------------- #
# Configuration — model id and where the API key comes from.
# --------------------------------------------------------------------------- #
# Load .env from the project root (this file lives in src/, so climb one level).
ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

# Groq's free-tier 70B model. It is OpenAI-compatible, so the chat-completions
# call below looks just like the OpenAI SDK's.
LLM_MODEL = "llama-3.3-70b-versatile"

# A fallback message the model is told to use when the retrieved context does
# not actually contain the answer. Keeping it as a constant means the UI and
# tests can recognise it if they ever need to.
INSUFFICIENT_CONTEXT_MSG = "I don't have enough information on that."


# --------------------------------------------------------------------------- #
# Groq client — created once and reused, like the embedding model.
# --------------------------------------------------------------------------- #
_client: Groq | None = None


def get_client() -> Groq:
    """Return a Groq client, creating it on first use.

    The client reads the key from the GROQ_API_KEY environment variable (which
    load_dotenv() populated from .env). We check it explicitly so a missing key
    produces a clear error instead of a confusing one from deep inside the SDK.
    """
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key or api_key == "your_key_here":
            raise RuntimeError(
                "GROQ_API_KEY is not set. Copy .env.example to .env and put your "
                "free Groq key in it (get one at https://console.groq.com)."
            )
        _client = Groq(api_key=api_key)
    return _client


# --------------------------------------------------------------------------- #
# Prompt building — turn retrieved chunks into a grounded prompt.
# --------------------------------------------------------------------------- #
# The system prompt sets the rules once. The user prompt carries the context and
# the question. Splitting them this way is the standard chat-completions pattern
# and makes the "answer only from context" instruction hard for the model to
# ignore.
SYSTEM_PROMPT = (
    "You are a helpful assistant for an unofficial university program guide. "
    "Answer the question using ONLY the information in the provided documents. "
    "If the documents don't contain enough information to answer, reply exactly: "
    f"\"{INSUFFICIENT_CONTEXT_MSG}\" "
    "Do not use outside knowledge and do not guess. "
    "When you answer, cite the source document(s) you used inline, like "
    "(source: filename.txt)."
)


def build_context_block(hits: list[dict]) -> str:
    """Format the retrieved chunks into a single numbered context string.

    Each chunk is labelled with its source filename so the model can cite it and
    so a human reading the prompt can see exactly what the answer is allowed to
    draw on. We include the source on every chunk because that is the unit the
    model is asked to attribute its answer to.
    """
    blocks = []
    for i, h in enumerate(hits, start=1):
        blocks.append(
            f"[Document {i} — source: {h['source']}]\n{h['text']}"
        )
    return "\n\n".join(blocks)


def build_user_prompt(question: str, hits: list[dict]) -> str:
    """Assemble the user-turn prompt: the context block followed by the question."""
    context = build_context_block(hits)
    return (
        "Here are the retrieved documents:\n\n"
        f"{context}\n\n"
        "================================================================\n"
        f"Question: {question}\n\n"
        "Answer using only the documents above, and cite the source(s) you used."
    )


# --------------------------------------------------------------------------- #
# ask() — the end-to-end function the UI calls.
# --------------------------------------------------------------------------- #
def ask(question: str, top_k: int = DEFAULT_TOP_K) -> dict:
    """Answer ``question`` from retrieved context and report the sources used.

    Returns a dict:
        {
            "answer":  "<the model's grounded answer, with inline (source: ...)>",
            "sources": ["rmp_smith_reviews.txt", ...],   # de-duplicated, ordered
            "hits":    [ ... ],   # the raw retrieved chunks, for inspection/UI
        }

    The ``sources`` list is built programmatically from the retrieved chunks, so
    even if the model forgets to cite, the response is still attributable. The
    prompt also asks the model to cite inline — so attribution happens both ways.
    """
    # --- step #4: retrieve the Top-K most relevant chunks --------------------
    hits = retrieve(question, top_k=top_k)

    # De-duplicate source filenames while preserving retrieval order (most
    # relevant first). dict.fromkeys keeps first-seen order and drops repeats.
    sources = list(dict.fromkeys(h["source"] for h in hits))

    # If retrieval came back empty, the store isn't built / nothing matched.
    # Don't bother calling the LLM — there is nothing to ground an answer in.
    if not hits:
        return {
            "answer": INSUFFICIENT_CONTEXT_MSG,
            "sources": [],
            "hits": [],
        }

    # --- step #5: generate a grounded answer ---------------------------------
    client = get_client()
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(question, hits)},
        ],
        # temperature=0 makes the model as deterministic and faithful to the
        # context as possible — we want it grounded, not creative.
        temperature=0,
    )
    answer = response.choices[0].message.content.strip()

    return {"answer": answer, "sources": sources, "hits": hits}


# --------------------------------------------------------------------------- #
# main — quick command-line test, mirroring embed_and_store.py's style.
# --------------------------------------------------------------------------- #
def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("question", help="the question to answer")
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K,
                        help=f"how many chunks to retrieve (default: {DEFAULT_TOP_K})")
    args = parser.parse_args()

    result = ask(args.question, top_k=args.top_k)

    print("=" * 72)
    print(f"QUESTION: {args.question}")
    print("=" * 72)
    print(result["answer"])
    print("-" * 72)
    print("Retrieved from:")
    for s in result["sources"]:
        print(f"  • {s}")


if __name__ == "__main__":
    main()
