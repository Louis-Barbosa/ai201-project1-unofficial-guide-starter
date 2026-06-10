"""
Milestone 3 — Document ingestion + cleaning + chunking.
================================================================================

WHAT THIS SCRIPT DOES (the big picture)
---------------------------------------
1. INGEST   : reads every .txt file in the documents/ folder.
2. CLEAN    : strips HTML, boilerplate (cookie banners, nav menus, "Read more",
              share buttons, comment counts, footers, etc.) leaving only the
              real content (reviews, opinions, descriptions, course numbers...).
3. CHUNK    : cuts each cleaned document into small overlapping pieces of text.
4. REPORT   : prints how many chunks were made and shows a few examples, then
              saves everything to chunks.json for the embedding step (Milestone 4).

CHUNKING STRATEGY (from planning.md)
------------------------------------
    chunk size : ~400 chars (allowed range 300-500)
    overlap    : ~110 chars (allowed range 100-125)
Why: most sources are short-form forum responses, so small chunks keep the
retrieval scope tight, while the overlap keeps the flow of ideas across cuts.

This file only uses the Python standard library, so it runs with no extra
installs. Common ways to run it:

    python src/chunk_documents.py                 # clean, chunk, save, summarize
    python src/chunk_documents.py --preview 5     # also print the first 5 chunks
    python src/chunk_documents.py --show Reputation.txt   # view one document
"""

from __future__ import annotations

# --- standard library imports ------------------------------------------------
import argparse          # parses command-line flags like --size / --preview
import html              # turns HTML entities (&amp;, &#39;) back into characters
import json              # writes the chunks out to chunks.json
import re                # regular expressions, used for all the cleaning patterns
from collections import Counter   # counts how often each line appears across docs
from pathlib import Path          # tidy, OS-independent file paths


# --------------------------------------------------------------------------- #
# Paths — where to read documents from and where to write the result.
# --------------------------------------------------------------------------- #
# __file__ is this script (src/chunk_documents.py). .parent.parent climbs up
# from src/ to the project root, so the paths work no matter where you run from.
ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "documents"          # folder full of .txt source documents
DEFAULT_OUT = ROOT / "chunks.json"     # default place to save the chunks


# --------------------------------------------------------------------------- #
# Cleaning — regular expressions used to strip HTML and boilerplate.
# Each `re.compile(...)` builds a reusable pattern once at import time.
# --------------------------------------------------------------------------- #

# Whole blocks whose *contents* are never readable text (code, styling, etc.).
# DOTALL lets "." match newlines so the block is removed even across many lines.
_SCRIPT_STYLE_RE = re.compile(
    r"<(script|style|noscript|svg|head)\b[^>]*>.*?</\1>",
    re.IGNORECASE | re.DOTALL,
)
# HTML comments: <!-- ... -->
_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)

# "Block-level" tags. When we delete these we replace them with a newline, so a
# page's paragraph/list structure becomes line breaks instead of run-on text.
_BLOCK_TAG_RE = re.compile(
    r"</?(p|div|br|li|ul|ol|tr|h[1-6]|section|article|header|footer|nav)\b[^>]*>",
    re.IGNORECASE,
)
# Any remaining tag (e.g. <span>, <a href=...>) — deleted with no replacement.
_ANY_TAG_RE = re.compile(r"<[^>]+>")

# Line-level boilerplate. After HTML is gone we look at the text line by line and
# DROP any line matching one of these patterns. The patterns are deliberately
# specific/anchored (^...$ means "the whole line") so they remove site chrome
# without accidentally deleting a real review sentence.
_BOILERPLATE_LINE_RES = [
    # --- Cookie / consent banners ---
    re.compile(r"\b(accept|manage|reject)\s+(all\s+)?cookies?\b", re.I),
    re.compile(r"\bwe use cookies\b", re.I),
    re.compile(r"\b(cookie|privacy)\s+(policy|settings|preferences)\b", re.I),
    re.compile(r"\bthis (site|website) uses cookies\b", re.I),
    # --- Navigation / page chrome ---
    re.compile(r"^\s*(home|menu|search|sign\s*in|log\s*in|sign\s*up|register|"
               r"subscribe|skip to (main )?content)\s*$", re.I),
    re.compile(r"^\s*(back to top|jump to|toggle navigation)\b", re.I),
    # --- Share / social buttons ---
    re.compile(r"^\s*(share|tweet|pin it|copy link|share (on|to)\b.*)\s*$", re.I),
    re.compile(r"^\s*(facebook|twitter|whatsapp|linkedin|reddit|email)\s*$", re.I),
    # --- "Read more" / continue-reading links ---
    re.compile(r"^\s*(read more|see more|show more|continue reading|view more)\b.*$", re.I),
    re.compile(r"^\s*\.\.\.\s*more\s*$", re.I),
    # --- Engagement counters: "12 comments", "3.4k upvotes", "120 views" ---
    re.compile(r"^\s*[\d.,]+\s*[kKmM]?\s*(comments?|replies|upvotes?|likes?|"
               r"points?|views?|shares?|followers?)\s*$", re.I),
    # --- Reddit/forum action buttons sitting on their own line ---
    re.compile(r"^\s*(reply|report|save|award|give award|hide|crosspost|edit|"
               r"delete|permalink|embed|source)\s*$", re.I),
    re.compile(r"^\s*(add a comment|leave a comment|post a comment)\s*$", re.I),
    re.compile(r"^\s*(upvote|downvote|vote)\s*$", re.I),
    # --- Quora / forum chrome ---
    re.compile(r"^\s*(related questions?|sponsored|promoted|advertisement|ad)\s*$", re.I),
    re.compile(r"^\s*\d+\s+answers?\s*$", re.I),
    re.compile(r"^\s*(view \d+ (upvoters?|other answers?)|originally answered:)\b", re.I),
    # --- Footers ---
    re.compile(r"^\s*(©|\(c\)|copyright)\b", re.I),
    re.compile(r"^\s*all rights reserved\b", re.I),
    re.compile(r"^\s*(terms of service|terms of use|contact us|about us|"
               r"privacy|sitemap|help center|careers)\s*$", re.I),
    re.compile(r"^\s*powered by\b", re.I),
]


def strip_html(raw: str) -> str:
    """Remove HTML markup from a string, leaving readable text + line breaks.

    Order matters: kill the unreadable blocks first, then turn structural tags
    into newlines, then delete every other tag, then decode entities last.
    """
    text = _SCRIPT_STYLE_RE.sub(" ", raw)   # 1) drop <script>/<style>/... contents
    text = _COMMENT_RE.sub(" ", text)       # 2) drop <!-- comments -->
    text = _BLOCK_TAG_RE.sub("\n", text)    # 3) block tags -> line breaks
    text = _ANY_TAG_RE.sub("", text)        # 4) remove all leftover inline tags
    text = html.unescape(text)              # 5) &amp; -> &, &#39; -> ', etc.
    return text


def _is_boilerplate(line: str) -> bool:
    """Return True if a single line matches any boilerplate pattern above."""
    # any(...) stops at the first matching pattern, so this is cheap.
    return any(rx.search(line) for rx in _BOILERPLATE_LINE_RES)


def clean_text(raw: str) -> str:
    """Clean ONE document: strip HTML + boilerplate, keep the real content.

    Returns tidy text where paragraphs are separated by single blank lines.
    """
    text = strip_html(raw)

    kept: list[str] = []   # the lines we decide to keep, in order
    prev = None            # the previous kept line, used to skip exact duplicates
    for line in text.splitlines():
        # Collapse any run of spaces/tabs into one space, then trim the ends.
        line = re.sub(r"[ \t ]+", " ", line).strip()
        if not line:
            prev = None     # a blank line resets the duplicate check
            continue
        if _is_boilerplate(line):
            continue        # skip cookie banners, nav, share buttons, etc.
        if line == prev:
            continue        # skip a line identical to the one right before it
        kept.append(line)
        prev = line

    # Join kept lines, then squeeze 3+ newlines down to a single blank line so
    # paragraph spacing stays consistent.
    cleaned = "\n".join(kept)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def drop_cross_document_boilerplate(cleaned: dict[str, str],
                                    min_doc_fraction: float = 0.6,
                                    max_len: int = 80) -> dict[str, str]:
    """Remove short lines that repeat across MOST documents.

    A site header/footer is the same text on every page. So we count, for each
    short line, how many documents contain it; if it shows up in at least
    ``min_doc_fraction`` of them, we treat it as boilerplate and remove it.
    Only short lines (< ``max_len`` chars) are eligible, so real repeated
    sentences are never deleted.

    ``cleaned`` maps filename -> cleaned text. Returns the same shape, filtered.
    """
    if len(cleaned) < 3:
        return cleaned   # too few docs to tell what "appears on every page" means

    # Count, per line, in how many DISTINCT documents it appears.
    line_doc_counts: Counter[str] = Counter()
    for text in cleaned.values():
        for line in set(text.splitlines()):   # set() so a line counts once per doc
            if len(line) < max_len:
                line_doc_counts[line] += 1

    # A line must appear in at least this many documents to be "boilerplate".
    threshold = max(2, int(len(cleaned) * min_doc_fraction))
    common = {ln for ln, c in line_doc_counts.items() if c >= threshold}
    if not common:
        return cleaned   # nothing repeats enough; leave everything as-is

    # Rebuild each document without the common boilerplate lines.
    out: dict[str, str] = {}
    for name, text in cleaned.items():
        lines = [ln for ln in text.splitlines() if ln not in common]
        out[name] = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()
    return out


# --------------------------------------------------------------------------- #
# Chunking — split cleaned text into small overlapping pieces.
# --------------------------------------------------------------------------- #
def chunk_text(text: str, size: int = 900, overlap: int = 250) -> list[str]: #this exists so that if there aren't any arguments called, it will default to the chunk size and overlap that we have found to be best for our data. There can easily be overriding arguments passed in if we want to experiment with different chunk sizes and overlaps, but this way we have a good default to start with. To check what currently override it check lines 376 and 378.
    """Split ``text`` into ~``size``-char chunks that overlap by ~``overlap`` chars.

    How it works (a sliding window):
      * Take a window of `size` characters starting at `start`.
      * Pull the window's END back to the last space so a word isn't cut in half.
      * Save that slice as a chunk.
      * Move `start` forward to (end - overlap) so the next chunk repeats the
        last ~overlap chars, then snap that start to a word boundary too.
      * Repeat until we reach the end of the text.
    """
    if overlap >= size:
        # Otherwise the window could fail to move forward -> infinite loop.
        raise ValueError("overlap must be smaller than size")

    text = text.strip()
    n = len(text)
    if n == 0:
        return []            # empty document -> no chunks
    if n <= size:
        return [text]        # short document fits in a single chunk

    chunks: list[str] = []
    start = 0
    while start < n:
        end = min(start + size, n)
        if end < n:
            # Snap END back to the last space inside the window so we don't
            # split a word. rfind returns -1 if no space is found.
            ws = text.rfind(" ", start + 1, end)
            if ws > start:
                end = ws

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= n:
            break            # we've consumed the whole document

        # Step the window forward but keep ~overlap chars of the previous chunk.
        next_start = end - overlap
        ws = text.rfind(" ", 0, next_start)   # snap start to the start of a word
        if ws + 1 > start:
            next_start = ws + 1
        if next_start <= start:               # safety: always move forward
            next_start = end
        start = next_start

    return chunks


# --------------------------------------------------------------------------- #
# Pipeline — tie ingestion, cleaning, and chunking together.
# --------------------------------------------------------------------------- #
def load_documents(docs_dir: Path) -> dict[str, str]:
    """Read every .txt file in ``docs_dir`` into a {filename: raw_text} dict."""
    files = sorted(p for p in docs_dir.glob("*.txt") if p.is_file())
    # errors="replace" means a stray bad byte won't crash the whole run.
    return {p.name: p.read_text(encoding="utf-8", errors="replace") for p in files}


def build_chunks(docs_dir: Path = DOCS_DIR,
                 size: int = 400,
                 overlap: int = 110) -> list[dict]:
    """Run the full pipeline and return a flat list of chunk records.

    Each record is a dict with: id, source, chunk_index, char_count, text.
    """
    raw_docs = load_documents(docs_dir)
    if not raw_docs:
        raise FileNotFoundError(f"No .txt documents found in {docs_dir}")

    # Clean each document, then remove site-wide boilerplate across documents.
    cleaned = {name: clean_text(raw) for name, raw in raw_docs.items()}
    cleaned = drop_cross_document_boilerplate(cleaned)

    # Chunk every cleaned document and flatten into one list with metadata.
    records: list[dict] = []
    for name, text in cleaned.items():
        for i, chunk in enumerate(chunk_text(text, size=size, overlap=overlap)):
            records.append({
                "id": f"{name}::chunk_{i}",  # unique id, e.g. "Reputation.txt::chunk_0"
                "source": name,              # which document this came from
                "chunk_index": i,            # position of this chunk within the doc
                "char_count": len(chunk),    # handy for spotting odd chunk sizes
                "text": chunk,               # the actual chunk text
            })
    return records


# --------------------------------------------------------------------------- #
# Display helpers — for eyeballing the data while developing.
# --------------------------------------------------------------------------- #
def show_document(name: str | None = None,
                  docs_dir: Path = DOCS_DIR,
                  cleaned: bool = True,
                  max_chars: int = 2000) -> None:
    """Print one document so you can see what it looks like.

    name     : the filename to show (e.g. "Reputation.txt"). If None, the first
               document in the folder (alphabetically) is shown.
    cleaned  : True prints the cleaned text (what actually gets chunked);
               False prints the raw, untouched file.
    max_chars: only the first this-many characters are printed, so a huge file
               doesn't flood the terminal.
    """
    docs = load_documents(docs_dir)
    if not docs:
        print(f"No .txt documents found in {docs_dir}")
        return

    # Default to the first document if no name was given.
    if name is None:
        name = sorted(docs)[0]
    if name not in docs:
        print(f"'{name}' not found. Available documents:")
        for n in sorted(docs):
            print(f"  - {n}")
        return

    raw = docs[name]
    text = clean_text(raw) if cleaned else raw
    label = "CLEANED" if cleaned else "RAW"

    print("=" * 72)
    print(f"DOCUMENT: {name}   [{label}]   ({len(text)} chars total)")
    print("=" * 72)
    print(text[:max_chars])
    if len(text) > max_chars:
        print(f"\n... (truncated — showing first {max_chars} of {len(text)} chars)")
    print("=" * 72)


def print_chunk_count(records: list[dict]) -> None:
    """Print how many chunks were made overall and per document."""
    # Tally chunks per source document.
    by_source: dict[str, int] = {}
    for r in records:
        by_source[r["source"]] = by_source.get(r["source"], 0) + 1

    print("\nChunks per document")
    print("-" * 44)
    for source in sorted(by_source):
        print(f"  {source:<34}{by_source[source]:>6}")
    print("-" * 44)
    print(f"  {'TOTAL CHUNKS':<34}{len(records):>6}")


def print_sample_chunks(records: list[dict], count: int = 5) -> None:
    """Print the first ``count`` chunks so you can see what they look like."""
    print(f"\nFirst {count} chunk(s)")
    print("=" * 72)
    for r in records[:count]:
        print(f"[{r['id']}]  ({r['char_count']} chars)")
        print(r["text"])
        print("-" * 72)


# --------------------------------------------------------------------------- #
# main — what runs when you execute this file from the command line.
# --------------------------------------------------------------------------- #
def main() -> None:
    # Define the command-line flags the script accepts.
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--docs", type=Path, default=DOCS_DIR,
                        help="folder of .txt documents (default: documents/)")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT,
                        help="output JSON path (default: chunks.json)")
    parser.add_argument("--size", type=int, default=700, #here is the default chunk size, this may be changed depending on results. 
                        help="chunk size in characters (default: 400)")
    parser.add_argument("--overlap", type=int, default=250, #here is the default chunk overlap, this may be changed depending on results. 
                        help="overlap between chunks in characters (default: 110)")
    parser.add_argument("--preview", type=int, default=5,
                        help="print the first N chunks (default: 5, use 0 to skip)")
    parser.add_argument("--show", nargs="?", const="", default=None, metavar="DOC",
                        help="print a document then exit. Give a filename, or leave "
                             "blank to show the first document.")
    parser.add_argument("--raw", action="store_true",
                        help="with --show, print the raw file instead of cleaned text")
    args = parser.parse_args()

    # --show mode: just display a document and stop (no chunking/saving).
    if args.show is not None:
        show_document(name=args.show or None, docs_dir=args.docs,
                      cleaned=not args.raw)
        return

    # Normal mode: build chunks, save them, then report.
    records = build_chunks(args.docs, size=args.size, overlap=args.overlap)
    args.out.write_text(json.dumps(records, ensure_ascii=False, indent=2),
                        encoding="utf-8")

    print_chunk_count(records)                 # how many chunks were made
    if args.preview:
        print_sample_chunks(records, count=args.preview)   # show a few chunks
    print(f"\nWrote {len(records)} chunks -> {args.out}")


# This guard means main() only runs when the file is executed directly
# (python src/chunk_documents.py), not when it's imported by another script.
if __name__ == "__main__":
    main()
