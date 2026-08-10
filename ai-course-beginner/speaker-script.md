# Speaker Script — Programming with AI Agents

Timed notes, keyed to slide numbers in `slides.md`. Times are targets, not
gospel. Total talk ≈ 45 min. Segment 4 (hands-on) is your shock absorber:
trim it to 6 min if demos overran, stretch to 11 if you're ahead.

Running clock in **[mm:ss]** is elapsed-at-*start*-of-slide.

---

## Part 1 — Hook (3 min)

### S1 · Title **[00:00]** — 30s
"Hi — I'm Niklas. Quick show of hands: who's used an AI coding tool for
real work? … Keep that in mind. In 45 minutes you'll all have driven one on
your own laptop. This is hands-on, so keep the lid open."

### S2 · Your job just changed **[00:30]** — 75s
"The shift is simple but it's real: you go from *typing every line* to
*directing something that types them for you*. The mental model I want you to
hold all session is: senior dev plus a tireless junior. The junior is fast,
never tired, and occasionally very confidently wrong. Your job — owning
whether the code is correct — does not move an inch."

### S3 · What you'll leave with **[01:45]** — 75s
"Three things. Use one today. Understand *why* it works so you're not
cargo-culting. And know the failure modes, because that's what separates
someone who's productive with these tools from someone who ships their
bugs faster." Transition: "Start with the model."

---

## Part 2 — Mental model (5 min)

### S4 · What an LLM is **[03:00]** — 90s
"Under the hood it's a next-token predictor. That sounds reductive but the
consequences are the whole game. It's **not a database** — it doesn't look
facts up, it *generates* plausible text. It's **not deterministic** — same
prompt twice, different answers. So treat every output like a sharp
colleague's first draft: often right, always worth a glance. If you remember
one thing here: it's a reasoner, not an oracle."

### S5 · What an agent is **[04:30]** — 90s
"An *agent* is that model put in a loop and handed tools. Read a file, edit a
file, run a shell command, run the tests, look at the result, decide the next
step. That's it. When people say 'AI agent' they mean this loop. Everything
fancy — Claude Code, Copilot, the thing I build at work — is this loop with
better tools and better plumbing."

### S6 · Context window **[06:00]** — 90s
"The loop has a working memory: the context window. Whatever's in it is what
the agent knows *right now*. Leave the error message out and it'll guess.
Put the right three files in and it nails it. This is why the pros obsess over
context: a `CLAUDE.md` with standing rules, memory files for facts across
sessions, and `/compact` to free space in a long chat. Managing what's in the
window *is* the skill." Transition: "So how do you actually talk to it?"

### QC1 · Quick check (poll, ~30s)
Ask it as a show-of-hands *before* clicking to the answer line: "Agent's wrong
about your private repo — retrain, add to context, or ask harder?" Let them
vote, then: "It's context — B. It can only use what's in the window. Hold that
thought, it comes back as RAG later." *Uses buffer; skip if behind.*

---

## Part 3 — Core skill (6 min)

### S7 · Instructions vs intent **[07:30]** — 2 min
"Biggest beginner mistake: giving instructions instead of intent. If you say
'add a try/except on line 42', you already did the hard thinking — you're just
using an expensive autocomplete. Instead give it the *goal and the
constraints*: 'this endpoint 500s on bad JSON, make it fail gracefully with a
400 and add a test.' Now it's doing the reasoning and you're doing the
judging. That's the trade you want."

### S8 · How I actually work **[09:30]** — 2 min
"Here's my literal loop at CARIAD. One: state high-level intent — the outcome.
Two: trust the agent for the detail; I don't micromanage the code. Three, and
this is non-negotiable: I review the diff. Every time. The review is where my
fifteen years of judgement actually gets spent. I give direction and taste;
it gives volume and speed."

### S9 · Three levers **[11:30]** — 2 min
"Three levers beginners leave on the table. **Context** — paste the actual
error, name the actual files; don't make it hunt. **Plan first** — tell it to
show a plan before writing code; catching a wrong turn in a plan costs
seconds, in a diff it costs minutes. **Verify** — tell it to run the tests and
fix until green, so it checks its own work. Look at the table: same bug, two
prompts. The right one hands over the trace and asks for verification. Watch me
do exactly this now."

### QC2 · Quick check (poll, ~30s)
Show-of-hands: "Which is *intent*, not an instruction — A, B, or C?" Answer C:
"Goal plus constraints; the agent picks the how. That's the mode you want."
Then straight into the demo. *Uses buffer; skip if behind.*

---

## Part 4 — Live demo (10 min)

### S10 · Demo **[13:30]** — 10 min
> Drive from `demo-runbook.md`. Narrate the LOOP, not the typing.
Key lines to say out loud:
- (on plan) "See — it planned before touching anything. I read this like a
  junior's proposal."
- (on approve) "I approve, and now it edits and runs the tests itself."
- (on green) "Green. But I still read the diff — watch."
- (on steering) "I don't love this bit — I'll just tell it, in plain English."
Land it: "That's the whole job. Direction, approval, review. Your turn."

---

## Part 5 — Hands-on (9 min)

### S11 · Your turn **[23:30]** — 9 min
"Repo you cloned this morning. Task's on the slide and in the handout: add
input validation plus a test to one function. Three checkpoints — it planned,
tests pass, and you can explain one line it wrote. That last one matters: if
you can't explain it, you can't own it. Stuck for a minute? Wave, I'll come
over. Go."
> Circulate. Watch for: no sign-in, wrong repo, prompt too vague. Give a
60-second warning before pulling them back.

---

## Part 6 — How it's built (9 min)

### S12 · Bridge **[32:30]** — 45s
"Here's the fun part. The tool you just drove is *itself* an AI app. I build
these for a living, so let me pull the curtain back with one I made: Forge."

### S13 · Agents plural **[33:15]** — 2 min
"Forge does root-cause analysis on automotive software stacks. It's not one
agent — it's several. A planner breaks the question down, specialists dig into
logs and code and our stack graphs, each running that same read-plan-act loop
from slide five. That's the reveal: an 'AI app' is usually just several agents,
your data, and a UI on top."

### S14 · RAG **[35:15]** — 2 min
"One concept you'll hear constantly: RAG. The model was never trained on your
private repo, so it *can't* know it. The trick is retrieval: take the question,
find the relevant chunks of your data, stuff them into the context, *then* let
it answer. Forge mirrors an internal stack-graph repo into a vector store and
pulls the relevant pieces per question. RAG is just: hand the model the right
pages before it answers."

### S15 · Tools & MCP **[37:15]** — 2 min
"How does an agent get a new power? You hand it a typed tool description — a
name, its inputs, what it does. I run a FastMCP server exposing twenty-odd
curated tools. The model reads the menu, picks a tool, fills in the inputs,
and gets a result back. Tools are how a text-predictor touches the real world
— databases, APIs, the filesystem. MCP is just a shared standard for writing
that menu."

### S16 · Where it runs **[39:15]** — 1.5 min
"Wiring it together: a Databricks App is the UI, requests hit the agent loop,
the loop calls a model through a LiteLLM gateway, and reaches out to MCP tools
and the vector store. Notice it's the *same loop* from the mental-model
section — just productionized. Nothing new, only bigger."

---

## Part 7 — Takeaways (3 min)

### S17 · Habits **[40:45]** — 1 min
"Habits that make this work: small tasks, review every diff, keep a CLAUDE.md
so you set rules once, always make it run tests, and commit often — cheap undo
beats a perfect prompt."

### S18 · Pitfalls **[41:45]** — 1 min
"Pitfalls to expect: it'll hallucinate an API that doesn't exist; it'll be
fluent and wrong; over-broad prompts make a mess; and both trust extremes hurt
— never trusting it is slow, always trusting it ships bugs. The universal fix:
small scope plus verify."

### QUIZ · Test yourself **[42:15]** — 30s
"There's a 10-question quiz in the pack — `quiz.html`, instant feedback, works
offline. Do it now as a warm-down or take it with you." If the room's engaged
and you're on time, run Q1–Q2 live on the projector; otherwise just point to
it. *This slide is optional — cut it first if you're over.*

### S19 · Next steps **[42:45]** — 90s
"Install one of these this week, run the repo again on a task of your own, and
read — or write — a CLAUDE.md for your project. Put your office-hours channel
on this slide before you present. Thanks — what questions do you have?"

> **If running long:** cut S16 to 30s and S13 to 90s.
> **If running short:** open the floor after S9 for one 'what would you ask it'
> example from the audience before the demo.
