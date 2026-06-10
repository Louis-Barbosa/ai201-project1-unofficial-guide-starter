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

**Embedding model:** I'll be using the all-MiniLM-L6 via sentence-transformers. I chose this because it's considered to be highly efficient, considerably lightweight, free, and for this sort of project could do all the work I need it to do relatively quickly. Using a different modle would be more expensive and while this may increase the efficienty and speed that isn't needed here. 

**Production tradeoff reflection:**
If cost was not an issue I would considered accuracy on domain-specific text and context length over anything else. I would want to focus more on having more infomration and ensuring that it is very specific. These two would ensure that the accuracy is better. 

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:** The instructions that I gave the model was "My RAG pipeline is already implemented through the first four stages: 1. Document ingestion from the collected URLs 2. Chunking using the parameters defined in my planning document 3. Embedding generation and vector store creation 4. Retrieval using Top-K = 5 I want you to generate the code for the final two components of the pipeline: 5. Grounded answer generation using an LLM 6. A user-facing query interface The generation stage must use Groq's `llama-3.3-70b-versatile` model. Initialize the client using: ```python from groq import Groq ``` and load the `GROQ_API_KEY` from the `.env` file. The system must be fully grounded in the retrieved context. Retrieved chunks should be passed to the model as context, and the prompt should explicitly instruct the model to answer using only the provided documents. If the retrieved context does not contain enough information to answer the question, the model must respond exactly: "I don't have enough information on that." The prompt should strongly discourage hallucination by instructing the model not to use outside knowledge, make assumptions, or generate unsupported information. The output format should include: * A grounded answer generated from the retrieved chunks * Source attribution identifying which document(s) were used Source attribution should be programmatically guaranteed rather than relying solely on the model. Append the retrieved source filenames after generation and return them separately in the response structure. Responses should resemble the following style: "According to student reviews of Professor Smith (source: rmp_smith_reviews.txt), exams are heavily curved and focus on lecture material rather than the textbook. Several reviewers specifically recommend attending every class." The answer should always be traceable to the retrieved text and accompanied by source citations. Please generate a complete `query.py` implementation containing an end-to-end `ask(question)` function that: * Retrieves the top 5 chunks * Builds the context string * Sends the context and question to Groq * Returns a dictionary containing: * `answer` * `sources` Also generate a Gradio interface in `app.py`. Use: ```python import gradio as gr from query import ask ``` The interface should contain: * A textbox for entering a question * An Ask button * An Answer output box * A Retrieved Sources output box The UI should display the generated answer separately from the source list. The source list should be formatted from the returned `sources` field. The final system should support the following flow: User Question → Retrieval (Top-K=5) → Context Construction → Groq Generation → Answer + Source Attribution → Gradio Interface Ensure the generated code is complete, runnable, and follows best practices for a grounded RAG application." 

**How source attribution is surfaced in the response:** Source attribution appeared in the response in parentheses next to information it was gathered from. So for example it would give a piece of information and then name the document it got it from (document.txt) and then continue to generate it's response. 

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 |What do students say about the difficulty of Princeton Math Major? |Commonly described as a very challenging and proof-heavy major, requiring abstract thinking and there being a significant work load|Students describe the Princeton Math Major as demanding, challenging, and intellectually demanding (source: ProgramDesign.txt, ProgramDifficulty.txt). They mention that it requires rigorous coursework, proof-writing, and abstraction, and that the pace is fast (source: ProgramDesign.txt). Some students found it so tough that they nearly dropped out or switched majors (source: ProgramDesign.txt, ProgramDifficulty.txt). However, those who engage actively with the material and resources find it highly rewarding (source: ProgramDesign.txt, ProgramDifficulty.txt). One student notes that studying mathematics at Princeton is "hard" and that you can expect to be surrounded by highly talented peers (source: ProgramDifficulty.txt).|Relavent|Accurate|
| 2 |How does Princeton Math compare to other top schools? |It is generally described as compariable to rigor to MIT and Harvard, other top universities, and emphasized for its theoretical focus|At the graduate level, Princeton is arguably the top school in the US in pure math (source: Reputation.txt). However, for undergraduates, there are many alternatives, and the quality of math education is comparable among top schools (source: Comparison.txt). In fact, any top-6 math program will be of similar quality (source: Comparison.txt). Princeton's math department is considered one of the top in the world, with several Fields Medal winners and Nobel Prize winners among its faculty (source: Reputation.txt). Compared to other top schools like MIT, Princeton offers a more well-rounded education, while MIT has a stronger focus on STEM (source: Reputation.txt). For graduate school, Princeton is probably a bit more prestigious than other top schools, but the difference is minimal (source: Comparison.txt). | Partially Relevant|Accurate|
| 3 |What is the Mat215/216/217 sequence and how is it generally described by students?|It's described as a rigorous proof-based introduction to higher-level mathematics and is often challenging for those transitoning from calculus.| he MAT 215-217 sequence is part of a recommended program for prospective mathematics majors, which also includes the option of starting with MAT 216, followed by MAT 218 (source: ProgramPrereqs.txt). As for how the sequence is generally described by students, one student mentions that "216 is a little hard, but it is not what people chalk it up to be" (source: FirstYearCourse.txt), while another student warns that MAT 216 is a "pretty brutal time commitment" and advises students to only take it if they truly enjoy math and are prepared for the challenge (source: FirstYearCourse.txt).|Relavent|Accurate|
| 4 |What is the general structure or focus of the Princeton Math Major?|It highly emphasizes theoretical mathmematics and includes coreses in analyis and algebra, then moving to advanced electives and topics|The Princeton Math Major is a highly structured and well-supported program that balances core theory courses, advanced electives, qualifying exams (if applicable), senior requirements (senior thesis or independent work), and appropriate breadth (computer science/physics/analysis/logic) and depth (source: TypicalCourseWork.txt). The program is demanding and emphasizes proof-writing, abstraction, and generality, with a focus on rigorous coursework and early research opportunities (source: ProgramDesign.txt, ProgramDifficulty.txt). A typical four-year course plan for a pure mathematics major at Princeton reflects the university's curriculum patterns, and students are encouraged to take classes in their interest area during junior and senior year (source: TypicalCourseWork.txt). |Relevant|Accurate|
| 5 |What is required for the Princeton Math major? |The Math major requires 8 departmental courses |A typical four-year course plan for a pure mathematics major at Princeton balances core theory courses, advanced electives, qualifying exams (if applicable), senior requirements (senior thesis or independent work), and appropriate breadth (computer science/physics/analysis/logic) and depth (source: TypicalCourseWork.txt). The perceived difficulty depends primarily on prior proof experience, study habits, and willingness to use faculty and peer resources (source: ProgramDesign.txt). Additionally, the program requires rigor and abstraction, with an emphasis on proof-writing, abstraction, and generality, as well as a fast pace with time-consuming problem sets that often require original thought (source: ProgramDesign.txt). It also requires students to be able to visualize proofs, wrap their mind around the architecture of a solution, and be able to discuss the mechanics of a proof and/or solution with other people (source: ProgramDifficulty.txt) |Relavent|Accurate|

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
Question 2: How does Princeton Math compare to other top schools?

**What the system returned:** 
The System returned accurate yet slightly irrelavent information. They included information regarding some of the achievements and notability of the department saying "Princeton's math department is considered one of the top in the world, with several Fields Medal winners and Nobel Prize winners among its faculty ". While it could be argued that discussing the faculty achievements can be valuable, I feel that it is irrelavent when comparing the quality of two institutions different departments. This could likely have occured since the begining of that sentence does have relavent information and since it was all chunked together it happened to be included along with the rest of the response. 

**Root cause (tied to a specific pipeline stage):** 
I believe the root cause was liklely at the chunking stage of the pipeline. At the chunking stage since two pieces of information with seperate information together, although the chunking values I used are what worked best for the entire model. This leads me to believe that potentially the embedding stage did not see the inclusion of faculty achievements are irrelavent information since it is attached to the initial phrase that "Princeton's math department is considered one of the top in the world,...". However, this issue initially stems from the chunk having two different pieces of information together. 

**What you would change to fix it:** 
I would potentially continue to play arround with the chunking values to see if there are ways to mitigate this issue. I'm certain with more time I can find better values for both chunking and overlapping that will avoid the potential issue of multiple pieces of information to be attached to one another. 

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:** 
One way that the spec helped me during implementation was that it allowed me to better understand and develop the pipeline I was creating. It allowed me to plan out things such as potential chunking and overlapping values or made me plan out what embedding model I would use. When I was then producing code I knew better both what I was working with and what I would tell the AI model to help me produce. 

**One way your implementation diverged from the spec, and why:** 
One way that my implementation divered from the spec was that I needed to change the values of the overlapping and chunking. This was because my initial values that I had planned to use were way to small and caused fragmentation. This fragmentation could then cause larger issues when embedding and eventually retrieving the information. 

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
