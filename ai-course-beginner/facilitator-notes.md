# Facilitator Notes

Everything you need around the content itself: prereqs email, room setup,
timing recovery, and rehearsal checklist.

---

## Prereqs email (send 3–4 days ahead)

> **Subject: Bring a laptop — AI agents workshop (45 min, hands-on)**
>
> Hi all — this session is hands-on, so a little setup beforehand saves us
> time. Please do this before you arrive (10 min):
>
> 1. **Install an AI coding agent** — either:
>    - **Copilot CLI** (works with our GitHub Enterprise):
>      `npm install -g @github/copilot` then run `copilot` and sign in, **or**
>    - **Claude Code** — [install link], sign in.
> 2. **Get the sample repo** — [link to zipped `sample-repo/` or repo URL].
> 3. **Confirm it runs** — in the repo folder:
>    ```
>    python -m pip install -r requirements.txt
>    python -m pytest -q
>    ```
>    You should see **3 passed, 1 failed** (the failure is on purpose).
>
> No prior AI experience needed — just bring a working laptop and the setup
> above. Questions before the day → [your channel].

## Room / tech setup (day of)

- [ ] Projector mirrors your terminal at **≥18pt** font, high contrast.
- [ ] Notifications OFF (Slack/Teams/email), Do Not Disturb on.
- [ ] Agent signed in, one warm-up prompt sent (pay auth/latency early).
- [ ] `sample-repo` clean copy staged; tests at 1-failed baseline.
- [ ] `demo-fallback/` (asciinema cast or screenshots) recorded and tested.
- [ ] Slides rendered to PDF (`slides.pdf`) as a backup to live Marp.
- [ ] Water, timer/stopwatch visible to you (phone face-up works).
- [ ] Spare: a colleague or you can help-desk the room during hands-on.

## Timing at a glance (elapsed at segment start)

| Segment | Start | Length |
|---|---|---|
| 1 Hook | 00:00 | 3 |
| 2 Mental model | 03:00 | 5 |
| 3 Core skill | 07:30 | 6 |
| 4 Live demo | 13:30 | 10 |
| 5 Hands-on | 23:30 | 9 |
| 6 How it's built | 32:30 | 9 |
| 7 Takeaways | 40:45 | 3 |
| Q&A / buffer | 43:45 | ~1+ |

> **Poll moments + quiz:** the deck has two 30-second "Quick check" poll
> slides (after mental-model, after core-skill) and an optional quiz slide
> pointing at `quiz.html`. They live inside the buffer — if you're behind,
> skip the polls first, then the quiz slide. The quiz itself is self-contained
> and great to send round afterwards regardless.

## Timing recovery plan

- **Running long after the demo?** Hands-on is the shock absorber — cut it to
  6 min (drop stretch goals, one checkpoint). Then trim S16 to 30s.
- **Running long after hands-on?** Compress Part 5: keep S13 (agents) + S14
  (RAG), collapse S15+S16 into "tools let it act; it runs on Databricks."
- **Running short?** After S9, take one audience prompt ("what would you ask
  it?") and critique it live. Add a second steer in the demo (Beat 6).
- **Hard stop looming?** The must-keep spine is S2, S5, S7–S9, the demo, and
  S17–S18. Everything else is expandable/collapsible.

## Audience calibration

- **All beginners:** slow down Part 1, spend the saved time in hands-on.
- **Mixed/senior room:** trim Part 1 to 3 min total, expand Part 5 (they'll
  ask about RAG/MCP), invite architecture questions.
- **Skeptics in the room:** lean on S18 (pitfalls) early — credibility comes
  from naming the failure modes before they do.

## Rehearsal checklist (do once, end to end)

- [ ] Render deck: `npx @marp-team/marp-cli slides.md --pdf`
- [ ] Dry-run the **live demo** on the sample repo with a stopwatch. If
      segment 4 > 12 min, trim beats.
- [ ] Do the **hands-on** yourself cold, timed — confirm ~7 min is realistic.
- [ ] Read the deck aloud against `speaker-script.md` — confirm 42–45 min.
- [ ] Record `demo-fallback/` while you're at it.

## Files in this package

```
ai-course-beginner/
├── index.html           # course home — open this first
├── slides.md / .html    # Marp deck with SVG diagrams (render to HTML)
├── quiz.html            # interactive 10-question quiz
├── speaker-script.md    # timed notes per slide
├── demo-runbook.md      # live-demo beats + fallbacks
├── handout-exercise.md  # attendee hands-on sheet
├── facilitator-notes.md # this file
├── build_html.py        # regenerates the HTML pages
├── assets/              # loop.svg · rag.svg · arch.svg (editable diagrams)
└── sample-repo/         # stats-cli: seeded bug + failing test
    ├── README.md
    ├── requirements.txt
    ├── stats.py
    ├── statslib.py
    └── test_statslib.py
```
Rebuild after editing any `.md`: `python build_html.py` (HTML pages) and
`npx @marp-team/marp-cli slides.md --html` (deck).

## Adapting this later

- Swap **Forge** in Part 5 for whatever app you know best — the RAG/agents/MCP
  points are generic; the specifics just need to be *yours* so you can answer
  follow-ups.
- Non-Python audience: reimplement `sample-repo` in their language; keep the
  same seeded-bug + hands-on shape.
- Longer slot (90 min): add a second hands-on where they write a `CLAUDE.md`
  for their own repo and watch the agent respect it.
