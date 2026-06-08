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

**Chunk size:** My chunking size will be 300-500 characters, likely being 400 to find a good inbetween. This is because most of my sources are short form responses through web forums so larger chunks could make the scope of retrieval too large and have unrelated content included.

**Overlap:** 100 - 125 characters. My overlap range will be about 100-125 characters, this is so that general flow of ideas are well maintained, but small enought that it doesn't contribute to bad retrieval.

**Reasoning:** These values were chosen since I am using mainly short forums to get my information. Since many of these are smaller, short form responses the larger responses will only lead to poor retrieval and then bad responses. 

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** I'll be using the all-MiniLM-L6 via sentence-transformers. 

**Top-k:** My Top-k will be 5 chunks per query. I will use this at first and then adjust if I realize that the responses don't come out well. 

**Production tradeoff reflection:** If cost was not an issue I would considered accuracy on domain-specific text and context length over anything else. I would want to focus more on having more infomration and ensuring that it is very specific. These two would ensure that the accuracy is better. 

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What do students say about the difficulty of Princeton Math Major?|Commonly described as a very challenging and proof-heavy major, requiring abstract thinking and there being a significant work load |
| 2 |How does Princeton Math compare to other top schools? |It is generally described as compariable to rigor to MIT and Harvard, other top universities, and emphasized for its theoretical focus|
| 3 |What is the Mat215/216/217 sequence and how is it gernally descirbed by students?|It's described as a rigorous proof-based introduction to higher-level mathematics and is often challenging for those transitoning from calculus.|
| 4 |What is the general structure or focus of the Princeton Math Major |It highly emphasizes theoretical mathmematics and includes coreses in analyis and algebra, then moving to advanced electives and topics |
| 5 |What is reuqired for the Princeton Math major? |The Math major requires 8 departmental courses. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.One potential risk is that there may be off-topic retrival from the Quora sources. I am unsure how it will exactly scrape quora but quora tends to also have responses on other topics or similar topics so I fear that there could be some off topic retrival due to the nature of that web forum. Also at times people include personal annacdotes or irrelavent information that could also be mixed in witht the relavent information making the risk of off-topic information much higher.

2.I am also worried about chunks splitting key information. This is mainly because there are three sources that fucntion as longer documents and I am prioritizing a size that focuses on smaller document lenghts since that is better suited for the majority of my documents. This could lead to some key infomration being split up but I am hoping that the overlap does take care of this issue well. 

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

#1. Document ingestion from the URLS -> #2.Chunking using the parameters chosen above -> #3. Embedding and Vector making -> #4. Retrival using the Top-K = 5 -> #5. Using retrieved chunks generate a final answer and display on UI
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


**Milestone 3 — Ingestion and chunking:** -> I will use claude code and my chunking strategy to first code a method that will scrape the documents and produce chunks. This will allow me to see are in my chunks and tell me whether I am chunking well enough that later it will develop/build good responses. I also want to print the total number of chunks being produced, this will allow me to know if I am chunking well enough and also give me good ideas with how to alter my Top-K value that I want to begin with before actually coding any part of the retrieval section.

**Milestone 4 — Embedding and retrieval:** -> I will use claude code and my embedding and retrieval strategy to first code the method. I will make sure that I understand the code and ensure that the fuction made will print the top k responses. Then I will tesk the retrival and if there is an issue then debug and edit the code to get the best results possible.

**Milestone 5 — Generation and interface:** Using my pipeline diagram to essentially code using claude and maybe chatgpt the respose generation and the UI interface.
