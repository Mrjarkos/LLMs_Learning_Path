# Live-Demo Runbook — Segment 4 (10 min)

The demo where you drive an agent on the `sample-repo` bug in front of the
room. Goal: show the **loop** — plan → approve → edit → tests green → review →
steer once. Narrate the loop, not the typing.

---

## 0. Before the talk (do this the morning of)

- [ ] `git clone`/copy `sample-repo/` to a clean throwaway folder. **Never
      demo on a real CARIAD repo.**
- [ ] `python -m pip install -r requirements.txt`
- [ ] `python -m pytest -q` → confirm **1 failed, 3 passed** (the seeded
      median bug).
- [ ] Sign in to your agent (Claude Code *or* Copilot CLI) and send ONE warm-up
      prompt so auth/model latency is paid before you're on stage.
- [ ] Font size up (terminal ≥ 18pt). Turn off notifications.
- [ ] Have `demo-fallback/` ready (see §4).

## 1. Tool choice

| | Primary | Corporate-safe alternative |
|---|---|---|
| Tool | **Claude Code** (your daily driver) | **Copilot CLI** `@github/copilot` 1.0.45 |
| Why | richest agent loop, plan mode | already installed, works with VW GHE |
| Launch | `claude` in the repo folder | `copilot` in the repo folder |

Pick one to drive live; keep the other as a mental backup. Beats below are
written tool-agnostic.

## 2. The beats (≈10 min)

**Beat 1 — show the failure (1 min).** Run the tests live:
```bash
python -m pytest -q
```
"One red. `test_median_even` says the median of `[1,2,3,4]` should be 2.5, and
we return 3. Let's have the agent fix it — but notice *how* I ask."

**Beat 2 — the intent prompt (30s).** Paste this (don't type it live):
> The test `test_median_even` in this repo fails: median of an even-length
> list should be the average of the two middle values, not the higher one.
> Show me a plan before changing anything, then fix `statslib.py` and run the
> tests until they pass.

**Beat 3 — read the plan aloud (1.5 min).** When it proposes a plan: "See — it
planned before touching code. I read this exactly like a junior's proposal.
Does the approach match what I'd do? Yes — average the two middle elements for
even length." Then approve.

**Beat 4 — let it act (1.5 min).** It edits `statslib.py` and reruns pytest.
"I'm not typing — it's editing the file and running the tests itself. That
verify step is the one beginners skip."

**Beat 5 — green + review the diff (2 min).** Tests pass. "Green. But I always
read the diff." Walk the diff out loud — one or two lines. "This is where my
judgement gets spent, not in the typing."

**Beat 6 — steer once, in plain English (2 min).** Deliberately ask for a
small improvement to show correction is conversational:
> Good. Now also make `median` handle an empty list by raising a clear
> ValueError instead of an IndexError, and add a test for it.
Let it work, glance at the result.

**Beat 7 — land it (1 min).** "That's the entire job: direction, approval,
review, steer. No magic — just the loop from slide five. Now you do it."

## 3. Narration cheat-sheet (say these)

- "Watch the loop, not the typing."
- "It planned first — I read it like a PR description."
- "It ran the tests itself — verification isn't optional."
- "Green, but I still read the diff."
- "I steer in plain English, I don't hand-edit."

## 4. Fallbacks (when live fails)

- **Model slow / network flaky:** switch narration to the pre-recorded
  `asciinema` cast (`asciinema play demo-fallback/median-fix.cast`) or the
  screenshot deck in `demo-fallback/`. Record this the day before.
- **Agent goes sideways:** you have the canned prompts above — re-paste
  verbatim rather than improvising under pressure.
- **Total outage:** talk the audience through the screenshots; the *loop* is
  the lesson, live execution is the garnish.
- **Time blown:** skip Beat 6 (the steer) entirely — Beats 1–5 make the point.

## 5. Reset between rehearsals

```bash
git checkout -- statslib.py test_statslib.py   # or restore from a clean copy
python -m pytest -q                            # back to 1 failed, 3 passed
```
