"""
Milestone 5 — Gradio query interface for the RAG guide.
================================================================================

This is the front door to the whole pipeline. The user types a question, and we
run it end-to-end through ask() (retrieve -> ground -> generate) and show:
  * the grounded answer (with inline source citations the model added), and
  * the list of source documents the answer was retrieved from.

HOW TO RUN
----------
    pip install -r requirements.txt        # first time only (installs gradio)
    python app.py                          # then open http://localhost:7860

The interface is intentionally minimal so a viewer can understand how to use it
from the demo video without any narration: one box to type, one button to ask,
two read-only boxes showing the answer and where it came from.
"""

from __future__ import annotations

import sys
from pathlib import Path

import gradio as gr

# query.py and embed_and_store.py live in src/, so add it to the import path.
# This lets `from query import ask` work whether you run from the project root
# or from inside src/.
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from query import ask   # noqa: E402  (import after sys.path tweak — intentional)


def handle_query(question: str):
    """Run one question through the pipeline and format it for the UI.

    Returns a (answer, sources) tuple matching the two output textboxes below.
    Empty input gets a friendly nudge instead of an error.
    """
    if not question or not question.strip():
        return "Please type a question first.", ""

    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources


# --------------------------------------------------------------------------- #
# The interface — a single-screen Q&A form.
# --------------------------------------------------------------------------- #
with gr.Blocks(title="Unofficial Program Guide — RAG Q&A") as demo:
    gr.Markdown(
        "# Unofficial Program Guide\n"
        "Ask a question about the programs covered in the guide. Answers come "
        "**only** from the retrieved source documents, and every answer lists "
        "where it was retrieved from."
    )

    inp = gr.Textbox(
        label="Your question",
        placeholder="e.g. Is the Princeton math program hard?",
    )
    btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)

    # Both clicking "Ask" and pressing Enter in the box submit the question.
    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])


if __name__ == "__main__":
    demo.launch()
