# Loom Script — Polish Business Law RAG Assistant

**Target length:** 3 minutes (Upwork attention span — anything longer gets skipped)
**Format:** Screen recording + webcam in corner
**Goal:** Make a client think "I want this guy to build mine"

---

## Pre-record checklist

- [ ] App deployed and live (HF Spaces or Streamlit Cloud)
- [ ] At least 10 documents indexed and queryable
- [ ] Test 3 questions in advance — make sure answers are good
- [ ] Open these tabs in order: live app → GitHub repo → README → architecture diagram
- [ ] Quiet room, decent mic (phone earbuds are fine)
- [ ] Look at the camera, not the screen, when introducing yourself

---

## The Script (with timing)

### 0:00 – 0:20 · The Hook

> "Hey, I'm [Name] — backend dev based in Poland. I build production RAG systems and AI agents.
>
> Most 'AI chatbots' you'll see on Upwork are wrappers around ChatGPT that hallucinate.
> This one doesn't — every answer cites the exact source paragraph.
> Let me show you."

**Action:** Camera on, then cut to live app.

---

### 0:20 – 1:00 · The Demo (this is the money shot)

**Action:** Type a real question into the live app. Suggested:

> *"How do I register a JDG as a non-EU citizen in Poland?"*

Wait for answer. As it streams in, say:

> "It's pulling from official Polish government documents I indexed.
> Notice it tells me what it knows AND what it doesn't.
> And here —"

**Action:** Click the "Sources" expander.

> "Every claim links back to a real document. If I were a lawyer, I could verify this in 30 seconds.
> This is what 'production' means in RAG — not just 'it answered something'."

Ask one more question, harder one:

> *"What's the VAT threshold and does it apply to B2B services?"*

> "Multi-part question — it pulls from two different docs and synthesizes. And cites both."

---

### 1:00 – 2:00 · The Architecture

**Action:** Cut to architecture diagram / README.

> "Quick tour of what's under the hood.
>
> Two phases — indexing and querying.
> Indexing happens once: chunk the documents, embed them with OpenAI, store in ChromaDB.
> Querying happens per message: embed the question, retrieve top 5 chunks using **hybrid search** — that's semantic plus keyword. Keyword catches things like exact statute numbers that pure semantic search misses.
>
> Then it goes to GPT-4o-mini with strict instructions: answer only from the context, cite sources, don't guess.
>
> Costs: about half a cent per question at scale.
> Latency: 1-2 seconds.
> Hosted on HuggingFace Spaces — free."

**Action:** Cut to code briefly.

> "The whole thing is roughly 400 lines of Python. Clean, typed, tested.
> There's an eval harness in here too — `scripts/eval.py` runs 20 test questions and tells me if a code change broke retrieval quality. Most freelancers skip this. Without it, you don't actually know if your RAG works."

---

### 2:00 – 2:40 · What I'd Build For You

**Action:** Back to camera.

> "I built this in 2 days as a portfolio piece. For your project, I'd build something similar but tailored:
>
> If you have **internal docs** — wikis, contracts, product manuals — I can index them and give your team an AI assistant that actually knows your business.
>
> If you have **customer support tickets**, same thing: support agents get instant draft replies citing the relevant docs.
>
> If you have **compliance documents** — legal, medical, financial — the citation requirement matters even more, because you need to defend every answer.
>
> Typical scope: 1-3 weeks. Typical cost: 1-5 thousand USD depending on size. I scope honestly — sometimes the right answer is a simpler tool, and I'll tell you that."

---

### 2:40 – 3:00 · The CTA

> "I'm based in Poland — CET timezone, overlaps with both US East Coast and full EU workday.
> Fast response, ship in milestones, no surprises on cost.
>
> If you've got a project where the AI side needs to actually work — not just demo well — message me on Upwork. I'll send back a Loom on how I'd approach your specific case.
>
> Thanks for watching."

---

## Three things that make this Loom outperform 90% of others

1. **You demo before you architect.** Most freelancers explain the stack first and viewers bounce. Show it working first.
2. **You admit limits.** "It tells me what it knows AND what it doesn't" is a trust move. Clients have been burned by overpromising freelancers.
3. **You quote real numbers.** Cost per question, latency, build time, line count. This signals "I've done this before" more than any badge.

---

## Things to NOT say

- ❌ "I'm new on Upwork but..." (kills your authority instantly)
- ❌ "Hi guys/everyone" (clients aren't "everyone" — they're one person)
- ❌ Reading from a script visibly (rehearse 3x, then talk freely)
- ❌ "Cutting-edge" / "state-of-the-art" / "next-gen" (empty buzzwords clients filter out)
- ❌ Apologizing for the demo data choice ("this is just a sample...") — own the choice
