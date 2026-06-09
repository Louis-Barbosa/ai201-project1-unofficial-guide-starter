"""
Quick manual test for the retrieve() function (Milestone 4).
================================================================================

WHAT THIS SCRIPT DOES
---------------------
1. Makes sure the ChromaDB vector store exists. If it's empty (you haven't run
   the embedding step yet), it builds it from chunks.json for you.
2. Runs a list of sample questions through retrieve() and prints, for each hit,
   the source document, chunk index, similarity score, and the chunk text.

This is a *manual* test: you read the output and judge whether the retrieved
chunks actually look relevant to the question. It is not an automated pass/fail
test — judging relevance is part of the Milestone 4 exercise.

HOW TO RUN
----------
    python src/test_retrieve.py                       # run the built-in questions
    python src/test_retrieve.py "is harvard math hard?"   # test your own question(s)
    python src/test_retrieve.py "q1" "q2" --top-k 3   # several questions, top-3 each
"""

from __future__ import annotations

import argparse

# These come from the module we are testing. Importing build_store/retrieve here
# is exactly how the Milestone 5 UI will import retrieve(), so this also doubles
# as a check that the import path works.
from embed_and_store import build_store, get_collection, retrieve, print_hits


# A few default questions to exercise different documents. Swap these for the 5
# evaluation questions from planning.md once you have them finalized.
SAMPLE_QUESTIONS = [
    "Is the Princeton math program hard?",
    "How do the top math programs compare?",
    "What are the prerequisites for the Princeton Math program?",
    "How flexible is the course schedule for Princeton Math Major?",
    "What is the typical coursework like for Princeton Math Majors?",
]


def ensure_store_built() -> None:
    """Build the vector store from chunks.json if it isn't populated yet.

    collection.count() returns how many chunks are stored. If it's 0, nothing has
    been embedded, so we run build_store() once. If it's already populated, we
    leave it alone (re-embedding every test run would be slow).
    """
    collection = get_collection()
    if collection.count() == 0:
        print("Vector store is empty — building it from chunks.json first...\n")
        count = build_store()
        print(f"Built store with {count} chunks.\n")
    else:
        print(f"Using existing vector store ({collection.count()} chunks).\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("questions", nargs="*",
                        help="one or more questions to test (default: built-in set)")
    parser.add_argument("--top-k", type=int, default=5,
                        help="how many chunks to retrieve per question (default: 5)")
    args = parser.parse_args()

    ensure_store_built()

    # Use the questions given on the command line, or fall back to the samples.
    questions = args.questions or SAMPLE_QUESTIONS

    for question in questions:
        hits = retrieve(question, top_k=args.top_k)
        print_hits(question, hits)
        print()   # blank line between questions for readability


if __name__ == "__main__":
    main()
