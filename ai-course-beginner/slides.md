---
marp: true
title: Programming with AI Agents — A Working Programmer's Intro
author: Niklas (CARIAD)
paginate: true
theme: default
class: lead
---

<!--
Render:  npx @marp-team/marp-cli slides.md --pdf
Preview: npx @marp-team/marp-cli slides.md --preview
Speaker notes live in speaker-script.md, keyed by slide number.
-->

<style>
section svg { display: block; margin: 8px auto; max-width: 100%; height: auto; }
figure.dia { margin: 0; text-align: center; }
figure.dia figcaption { color: #5b6472; font-size: 15px; margin-top: 6px; }
.quiz-badge {
  display: inline-block; background: #eef0ff; color: #4f46e5; font-weight: 700;
  padding: 4px 14px; border-radius: 20px; letter-spacing: .08em; font-size: 15px;
}
.answer { color: #0b6b3d; font-weight: 700; }
</style>

# Programming with AI Agents
### A working programmer's intro

45 minutes · beginner-friendly · bring a laptop

<!-- S1 -->

---

## Your job just changed

You used to type **every line**.

Now you can **direct an agent** that types them for you.

> Think: a senior dev pairing with a tireless, fast, slightly overconfident junior.

**You still own correctness.** That never moves.

<!-- S2 -->

---

## What you'll leave with

1. **Use** an AI coding agent today — on your own machine
2. **Understand** why it works (and why it sometimes doesn't)
3. **Recognize** its failure modes before they bite you

No hype. Just the working model I use daily.

<!-- S3 -->

---

# Part 1 · The mental model
### 5 minutes

<!-- section divider -->

---

## What an LLM actually is

A **next-token predictor** trained on a lot of text and code.

- Not a database → it doesn't "look up" facts
- Not deterministic → same prompt, different runs
- It's a **reasoner** that produces plausible text

**Consequence:** treat output like a smart colleague's first draft — useful, and you verify it.

<!-- S4 -->

---

## What an *agent* is

An LLM **in a loop**, with **tools**.

<figure class="dia">
<svg viewBox="0 0 760 400" xmlns="http://www.w3.org/2000/svg" width="620" font-family="Segoe UI, Helvetica, Arial, sans-serif" role="img" aria-label="The agent loop: read, plan, act, then observe and repeat">
  <defs>
    <marker id="loopArrow" markerWidth="9" markerHeight="9" refX="6" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L6,3 L0,6 Z" fill="#4f46e5"/>
    </marker>
  </defs>
  <rect x="70"  y="50"  width="200" height="80" rx="16" fill="#eef0ff" stroke="#4f46e5" stroke-width="2.5"/>
  <text x="170" y="99"  text-anchor="middle" font-size="27" font-weight="700" fill="#312e81">READ</text>
  <rect x="490" y="50"  width="200" height="80" rx="16" fill="#eef0ff" stroke="#4f46e5" stroke-width="2.5"/>
  <text x="590" y="99"  text-anchor="middle" font-size="27" font-weight="700" fill="#312e81">PLAN</text>
  <rect x="490" y="270" width="200" height="80" rx="16" fill="#4f46e5" stroke="#4338ca" stroke-width="2.5"/>
  <text x="590" y="319" text-anchor="middle" font-size="27" font-weight="700" fill="#ffffff">ACT</text>
  <rect x="70"  y="270" width="200" height="80" rx="16" fill="#eef0ff" stroke="#4f46e5" stroke-width="2.5"/>
  <text x="170" y="312" text-anchor="middle" font-size="24" font-weight="700" fill="#312e81">OBSERVE</text>
  <text x="170" y="334" text-anchor="middle" font-size="13" fill="#5b6472">(tests, output, errors)</text>
  <line x1="270" y1="90"  x2="478" y2="90"  stroke="#4f46e5" stroke-width="3" marker-end="url(#loopArrow)"/>
  <line x1="590" y1="130" x2="590" y2="258" stroke="#4f46e5" stroke-width="3" marker-end="url(#loopArrow)"/>
  <line x1="490" y1="310" x2="282" y2="310" stroke="#4f46e5" stroke-width="3" marker-end="url(#loopArrow)"/>
  <line x1="170" y1="270" x2="170" y2="142" stroke="#4f46e5" stroke-width="3" marker-end="url(#loopArrow)"/>
  <text x="380" y="192" text-anchor="middle" font-size="17" font-weight="600" fill="#1a1d24">the loop is</text>
  <text x="380" y="216" text-anchor="middle" font-size="17" font-weight="600" fill="#1a1d24">the whole trick</text>
</svg>
</figure>

Tools = read file · edit file · run shell · search · run tests.

The loop is the whole trick. That's all an "agent" is.

<!-- S5 -->

---

## Context window = its working memory

Everything the agent "knows" *right now* is what's in its context.

- Fill it with the right files → good output
- Leave the error message out → it guesses

This is why these matter:
- `CLAUDE.md` — standing project rules
- memory files — facts that survive sessions
- `/compact` — reclaim room in a long session

**Managing context is the skill.**

<!-- S6 -->

---

## Quick check ✋

> Your agent confidently answers a question about your **private repo** — which it was never trained on — and gets it **wrong**. Best fix?

**A.** Retrain the model on your repo
**B.** Put the relevant files into its **context**
**C.** Rephrase the question more forcefully

<span class="answer">→ B. It can only reason over what's in its context window.</span>

<!-- QC1 -->

---

# Part 2 · The core skill
### Prompting as *intent* — 6 minutes

<!-- section divider -->

---

## Instructions vs. intent

❌ **Instruction** (you did the thinking):
> "Add a try/except around line 42."

✅ **Intent** (agent does the thinking):
> "This endpoint 500s on malformed JSON. Make it fail gracefully with a 400, and add a test."

Give it the **goal + the constraints**, not the keystrokes.

<!-- S7 -->

---

## How I actually work

1. State **high-level intent** — what outcome I want
2. **Trust the agent** for the implementation detail
3. **Review the diff** — every time, no exceptions

> I give direction and judgement. It gives volume and speed.

The review step is where *my* expertise lives.

<!-- S8 -->

---

## Three levers beginners underuse

**1. Give it context** — paste the error, name the files.

**2. Let it plan first** — "plan before you code" catches wrong turns cheaply.

**3. Ask it to verify** — "run the tests and fix until green."

| Weak prompt | Strong prompt |
|---|---|
| "fix the bug" | "`test_parse` fails with KeyError on empty input — here's the trace. Fix it and rerun the tests." |

<!-- S9 -->

---

## Quick check ✋

> Which one is **intent**, not an instruction?

**A.** "Rename the variable on line 12 to `count`."
**B.** "Wrap lines 40–45 in a try/except."
**C.** "Users can submit an empty form and it crashes — handle it and add a test."

<span class="answer">→ C. Goal + constraints; the agent decides the *how*.</span>

<!-- QC2 -->

---

# Part 3 · Live demo
### Watch me drive one — 10 minutes

I'll take a real bug on a small repo:
plan → approve → edit → tests green → review → steer once.

*Watch the loop, not the typing.*

<!-- S10 -->

---

# Part 4 · Your turn
### Hands-on — 9 minutes

On the sample repo you cloned:

**Task:** add input validation + a test to one function.

✅ agent proposed a plan
✅ tests pass
✅ you reviewed the diff and can explain one line

Stuck for 60s? Wave me over.

<!-- S11 -->

---

# Part 5 · How is this built?
### The tool you just used is itself an AI app — 9 minutes

I build these too. Meet **Forge**.

<!-- S12 -->

---

## Agents, plural

**Forge** = a multi-agent Root-Cause-Analysis platform for automotive software stacks.

- A **planner** agent breaks the question down
- **Specialist** agents dig into logs, code, stack graphs
- Each one runs the same **read → plan → act** loop

An "AI app" is often just **several agents + your data + a UI**.

<!-- S13 -->

---

## RAG in one slide

The model **can't know** your private repo — it wasn't trained on it.

So you:

<figure class="dia">
<svg viewBox="0 0 960 360" xmlns="http://www.w3.org/2000/svg" width="880" font-family="Segoe UI, Helvetica, Arial, sans-serif" role="img" aria-label="RAG pipeline: question, retrieve relevant chunks from your data, augment the context, generate an answer">
  <defs>
    <marker id="ragArrow" markerWidth="9" markerHeight="9" refX="6" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L6,3 L0,6 Z" fill="#4f46e5"/>
    </marker>
  </defs>
  <text x="285" y="96" text-anchor="middle" font-size="13" fill="#5b6472">retrieval</text>
  <text x="485" y="96" text-anchor="middle" font-size="13" fill="#5b6472">augmentation</text>
  <text x="685" y="96" text-anchor="middle" font-size="13" fill="#5b6472">generation</text>
  <rect x="20" y="120" width="150" height="64" rx="12" fill="#ffffff" stroke="#c7c9f5" stroke-width="2"/>
  <text x="95" y="158" text-anchor="middle" font-size="18" font-weight="600" fill="#1a1d24">Question</text>
  <rect x="210" y="120" width="150" height="64" rx="12" fill="#eef0ff" stroke="#4f46e5" stroke-width="2.5"/>
  <text x="285" y="158" text-anchor="middle" font-size="18" font-weight="700" fill="#312e81">Retrieve</text>
  <rect x="400" y="120" width="170" height="64" rx="12" fill="#eef0ff" stroke="#4f46e5" stroke-width="2.5"/>
  <text x="485" y="152" text-anchor="middle" font-size="17" font-weight="700" fill="#312e81">Augment</text>
  <text x="485" y="172" text-anchor="middle" font-size="12" fill="#5b6472">put chunks in context</text>
  <rect x="610" y="120" width="150" height="64" rx="12" fill="#4f46e5" stroke="#4338ca" stroke-width="2.5"/>
  <text x="685" y="158" text-anchor="middle" font-size="18" font-weight="700" fill="#ffffff">Generate</text>
  <rect x="800" y="120" width="140" height="64" rx="12" fill="#e7f6ee" stroke="#0f9d58" stroke-width="2.5"/>
  <text x="870" y="158" text-anchor="middle" font-size="18" font-weight="700" fill="#0b6b3d">Answer</text>
  <line x1="170" y1="152" x2="198" y2="152" stroke="#4f46e5" stroke-width="3" marker-end="url(#ragArrow)"/>
  <line x1="360" y1="152" x2="388" y2="152" stroke="#4f46e5" stroke-width="3" marker-end="url(#ragArrow)"/>
  <line x1="570" y1="152" x2="598" y2="152" stroke="#4f46e5" stroke-width="3" marker-end="url(#ragArrow)"/>
  <line x1="760" y1="152" x2="788" y2="152" stroke="#4f46e5" stroke-width="3" marker-end="url(#ragArrow)"/>
  <ellipse cx="285" cy="258" rx="70" ry="16" fill="#dfe2ff" stroke="#4f46e5" stroke-width="2"/>
  <path d="M215,258 v54 a70,16 0 0 0 140,0 v-54" fill="#eef0ff" stroke="#4f46e5" stroke-width="2"/>
  <ellipse cx="285" cy="258" rx="70" ry="16" fill="#dfe2ff" stroke="#4f46e5" stroke-width="2"/>
  <text x="285" y="300" text-anchor="middle" font-size="14" font-weight="600" fill="#312e81">your data</text>
  <text x="285" y="320" text-anchor="middle" font-size="12" fill="#5b6472">(vector store)</text>
  <line x1="285" y1="242" x2="285" y2="190" stroke="#4f46e5" stroke-width="3" marker-end="url(#ragArrow)"/>
</svg>
</figure>

Forge mirrors an internal stack-graph repo into a vector store, then retrieves the relevant pieces per question.

**RAG = give the model the right pages before it answers.**

<!-- S14 -->

---

## Tools & MCP

How does an agent gain a new ability?

You hand it a **typed tool schema**: name, inputs, what it does.

- I run a **FastMCP** server exposing 20+ curated tools
- The LLM picks a tool, fills the inputs, reads the result

> **Tools are how the LLM touches the real world.**
> MCP is just a standard shape for describing them.

<!-- S15 -->

---

## Where it runs

<figure class="dia">
<svg viewBox="0 0 940 400" xmlns="http://www.w3.org/2000/svg" width="840" font-family="Segoe UI, Helvetica, Arial, sans-serif" role="img" aria-label="Architecture: user to Databricks App to the agent loop, which calls a model via a LiteLLM gateway and reaches MCP tools and a vector store">
  <defs>
    <marker id="archArrow" markerWidth="9" markerHeight="9" refX="6" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L6,3 L0,6 Z" fill="#4f46e5"/>
    </marker>
  </defs>
  <rect x="40"  y="40" width="160" height="60" rx="12" fill="#ffffff" stroke="#c7c9f5" stroke-width="2"/>
  <text x="120" y="76" text-anchor="middle" font-size="18" font-weight="600" fill="#1a1d24">User</text>
  <rect x="650" y="40" width="230" height="60" rx="12" fill="#ffffff" stroke="#c7c9f5" stroke-width="2"/>
  <text x="765" y="70" text-anchor="middle" font-size="17" font-weight="600" fill="#1a1d24">Model</text>
  <text x="765" y="89" text-anchor="middle" font-size="12" fill="#5b6472">(the LLM)</text>
  <rect x="40"  y="170" width="200" height="64" rx="12" fill="#eef0ff" stroke="#4f46e5" stroke-width="2.5"/>
  <text x="140" y="200" text-anchor="middle" font-size="16" font-weight="700" fill="#312e81">Databricks App</text>
  <text x="140" y="220" text-anchor="middle" font-size="12" fill="#5b6472">(UI)</text>
  <rect x="330" y="163" width="220" height="78" rx="14" fill="#4f46e5" stroke="#4338ca" stroke-width="2.5"/>
  <text x="440" y="197" text-anchor="middle" font-size="18" font-weight="700" fill="#ffffff">Agent loop</text>
  <text x="440" y="219" text-anchor="middle" font-size="12" fill="#dfe2ff">read &#8594; plan &#8594; act</text>
  <rect x="650" y="170" width="230" height="64" rx="12" fill="#eef0ff" stroke="#4f46e5" stroke-width="2.5"/>
  <text x="765" y="200" text-anchor="middle" font-size="16" font-weight="700" fill="#312e81">LiteLLM gateway</text>
  <text x="765" y="220" text-anchor="middle" font-size="12" fill="#5b6472">(routes to the model)</text>
  <rect x="300" y="310" width="150" height="58" rx="12" fill="#ffffff" stroke="#c7c9f5" stroke-width="2"/>
  <text x="375" y="338" text-anchor="middle" font-size="15" font-weight="600" fill="#1a1d24">MCP tools</text>
  <text x="375" y="356" text-anchor="middle" font-size="11" fill="#5b6472">(touch the world)</text>
  <rect x="470" y="310" width="150" height="58" rx="12" fill="#ffffff" stroke="#c7c9f5" stroke-width="2"/>
  <text x="545" y="338" text-anchor="middle" font-size="15" font-weight="600" fill="#1a1d24">Vector store</text>
  <text x="545" y="356" text-anchor="middle" font-size="11" fill="#5b6472">(your data / RAG)</text>
  <line x1="120" y1="100" x2="120" y2="170" stroke="#4f46e5" stroke-width="3" marker-end="url(#archArrow)"/>
  <line x1="240" y1="202" x2="318" y2="202" stroke="#4f46e5" stroke-width="3" marker-end="url(#archArrow)"/>
  <line x1="550" y1="202" x2="638" y2="202" stroke="#4f46e5" stroke-width="3" marker-end="url(#archArrow)"/>
  <line x1="765" y1="170" x2="765" y2="102" stroke="#4f46e5" stroke-width="3" marker-end="url(#archArrow)"/>
  <line x1="415" y1="241" x2="380" y2="308" stroke="#4f46e5" stroke-width="3" marker-end="url(#archArrow)"/>
  <line x1="470" y1="241" x2="535" y2="308" stroke="#4f46e5" stroke-width="3" marker-end="url(#archArrow)"/>
</svg>
</figure>

Same loop from the mental-model section — now productionized.

<!-- S16 -->

---

# Part 6 · Takeaways
### 3 minutes

<!-- section divider -->

---

## Habits that make it work

- **Small tasks** — one change at a time
- **Review every diff** — you're the senior on the PR
- **Keep a `CLAUDE.md`** — encode project rules once
- **Make it run tests** — verification is not optional
- **Commit often** — cheap undo beats careful prompts

<!-- S17 -->

---

## Pitfalls to expect

- **Hallucinated APIs** — invents a method that doesn't exist
- **Confident and wrong** — fluent ≠ correct
- **Over-broad prompts** — "refactor everything" → chaos
- **Trust extremes** — never trusting it (slow) *or* always trusting it (bugs)

The fix for all of these: **small scope + verify**.

<!-- S18 -->

---

## Test yourself

<span class="quiz-badge">QUIZ</span>

**10 quick questions** covering the whole session — mental model, prompting, RAG, tools, pitfalls.

Open **`quiz.html`** from the course folder → instant feedback, no sign-in, works offline.

Use it as a warm-down now, or send it round afterwards.

<!-- QUIZ -->

---

## Next steps

- **Install:** Claude Code *or* Copilot CLI (`@github/copilot`)
- **Try:** the hands-on repo again on a task of your own
- **Read:** your project's `CLAUDE.md` — or write one
- **Ask:** [your channel / office hours here]

**Go direct an agent this week.**

Thank you — questions?

<!-- S19 -->
