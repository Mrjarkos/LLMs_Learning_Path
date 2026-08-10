# Hands-On Handout — Your First Agent Task (9 min)

Print or share this. Attendees work on the `sample-repo` they cloned before
the session.

---

## Before you start (should already be done — 1 min to confirm)

- [ ] An agent is installed and you're signed in
      (**Claude Code** or **Copilot CLI** — `copilot`).
- [ ] You have the `stats-cli` sample repo cloned.
- [ ] From the repo folder, this works:
      ```bash
      python -m pip install -r requirements.txt
      python -m pytest -q      # 3 pass, 1 red — that's expected
      ```

## Your task

`parse_numbers()` in `statslib.py` currently trusts its input — feed it
`"banana"` and it blows up with an ugly `ValueError` from `float()`.

**Make it fail clearly, and prove it with a test.**

Concretely:
1. `parse_numbers` should reject any non-numeric token with a clear,
   human-readable error that names the bad token.
2. Add a test that confirms this behaviour.

## How to ask the agent (this is the skill)

Don't tell it which lines to change. Give it **intent + context + verify**.
A prompt that works:

> In `statslib.py`, `parse_numbers` crashes with a confusing error on
> non-numeric input like `"banana"`. Make it raise a clear ValueError that
> includes the offending token, add a test in `test_statslib.py` that checks
> this, and run the tests until everything passes. Show a short plan first.

Then: **read the plan**, approve, **read the diff**, and run:
```bash
python -m pytest -q
```

## You're done when (checkpoints)

- [ ] ✅ The agent proposed a **plan** before editing.
- [ ] ✅ `pytest` is **all green** (your new test included).
- [ ] ✅ You can **explain one line** the agent wrote. If you can't, you can't
      own it — ask the agent to explain it, or ask me.

## Stretch goals (if you finish early)

- Ask the agent to also reject `NaN`/`inf` strings, with a test.
- Ask it to write the **commit message** for your change, then read it
  critically — would you approve that PR?
- Add a `--help` flag to `stats.py` and let the agent wire it up.

## If you're stuck for 60 seconds

Wave me over. Common snags:
- Not signed in / model not reachable → re-run auth.
- Wrong folder → the agent must be launched *inside* the repo.
- Prompt too vague ("fix it") → give it the error and name the file.
