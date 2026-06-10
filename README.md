# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover? 
This system is covering information about Princeton's Math Major/Department. This information is valuable because Princeton is both known for it's math department and this is focusing on people's experiences with math at princeton. This allows people to know whether this is a major they want to pursue or thoughts on whether math at Princeton is a good fit for them. 
     Why is this knowledge valuable, and why is it hard to find through official channels?
     This knowledge is valuable because it specifically focuses on other peoples experiences and thoughts. This is extremely important because a school will simply try to sell themselves best but by hearing from students/alumni you can get authentic experiences or information you'd only get from going to Princeton. 
---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 |Princeton |Description of Math major from the school; while official this is useful in filling in information about what is needed which can be helpful in explaining certain context of students experiences |https://www.math.princeton.edu/undergraduate/majors/overview|
| 2 |Princeton |MAT major requirments; this is useful as it once again provides context for some of what students/alumni say about the course work; official| https://www.math.princeton.edu/undergraduate/requirements|
| 3 |Princeton | MAT courses available; this is useful as it once again provides context for some of what students/alumni say about the course work and can provide context of what the course covers; official | https://www.princeton.edu/academics/area-of-study/mathematics|
| 4 |Quora |MAT major typical four years; This shows the typical workload a students will take over their four years as a math major; web forum; |https://www.quora.com/For-a-pure-math-major-at-Princeton-what-is-a-typical-four-year-course-structure|
| 5 |Reddit |Opinions on Math Major at Princeton; This covers a broad range from difficulty of the work to comparisons to other institutions; forum |https://www.reddit.com/r/princeton/comments/6577md/the_math_major_at_princeton/|
| 6 |Reddit |MAT placement exam; talks about a part of princeton's first year experience in regards to the first math course you take |https://www.reddit.com/r/princeton/comments/1s16ny8/math_placement/ |
| 7 |Quora|Opinion on MAT major difficulty; forum; talks about the Majors difficulty and challegnes |https://www.quora.com/What-is-it-like-to-study-mathematics-at-Princeton |
| 8 |Quora|Difficulty of Math Major; this also talks about the majors difficulty and challenges faced; forum |https://www.quora.com/How-hard-is-it-to-be-a-math-major-at-Princeton |
| 9 |Quora |Quality of Princeton Math Department; forum; talks about the quality of the math department and has some comparisons to peer institutions |https://www.quora.com/How-good-is-Princeton-at-math |
| 10 |Quora |Comparing Princeton Math to other Universities; forum; Compares princeton math to peer institutions |https://www.quora.com/For-a-math-major-which-school-is-better-MIT-Princeton-or-Harvard |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 
My initial chunk size was 400 however this was too small and was switched to 700 characters. So chunk size is 700.

**Overlap:** 
My initial chunk overlap size was 110 however this was later switched to 250 characters. So the overlap size is 250.

**Why these choices fit your documents:** 
Initially the values 400 and 110 was used for chunk size and overlap size respectively in the documents. However this was later switched to 700 and 250 to avoid fragmentation. These fit the documents well since the documents consist of smaller paragraphs since the information is being derived from a forum. This means that having a relatively small chunk size will ensure that only one idea, typically a sentence, is kept in a chunk. However if it was too small, which I saw with the initial values then there would be fragmentation as the chunk will not have an entire sentence kept within it. 

**Final chunk count:** The final chunk count was 174. This was a good amount of chunks that allowed the embedding model to produce good vectors and choose appropriate chunks. 

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**

**Production tradeoff reflection:**

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

**How source attribution is surfaced in the response:**

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
