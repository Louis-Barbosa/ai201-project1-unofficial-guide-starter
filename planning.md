# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? --> #My domain is on Princeton University's MAT (Math) Major and Mat Department/Courses. While there is good information on the university's pages learning about student's opinions and experiences provides more realisitic information that's not usualy found on official pages. -> might need to change sourses 1-3.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 |Princeton |Description of MAT major |https://www.math.princeton.edu/undergraduate/majors/overview  |
| 2 |Princeton |MAT major requirments | https://www.math.princeton.edu/undergraduate/requirements|
| 3 |Princeton | MAT courses available | https://www.princeton.edu/academics/area-of-study/mathematics|
| 4 |Quora |MAT major typical four years |https://www.quora.com/For-a-pure-math-major-at-Princeton-what-is-a-typical-four-year-course-structure|
| 5 |Reddit |Opions on Math Major at Princeton |https://www.reddit.com/r/princeton/comments/6577md/the_math_major_at_princeton/|
| 6 |Reddit |MAT placement exam |https://www.reddit.com/r/princeton/comments/1s16ny8/math_placement/ |
| 7 |Quora|Opinion on MAT major difficulty |https://www.quora.com/What-is-it-like-to-study-mathematics-at-Princeton |
| 8 |Quora|Difficulty of Math Major |https://www.quora.com/How-hard-is-it-to-be-a-math-major-at-Princeton |
| 9 |Quora |Quality of Princeton Math Department |https://www.quora.com/How-good-is-Princeton-at-math |
| 10 |Quora |Comparing Princeton Math to other Universities |https://www.quora.com/For-a-math-major-which-school-is-better-MIT-Princeton-or-Harvard |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
