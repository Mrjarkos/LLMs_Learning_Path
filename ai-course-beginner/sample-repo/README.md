# stats-cli — course sample repo

A tiny command-line tool that prints basic statistics for a list of numbers.
Deliberately small so an AI agent can reason about the whole thing at once.

There is **one seeded bug** (see `test_statslib.py`) used for the live demo,
and a hands-on task described in the course handout.

## Setup

```bash
python -m pip install -r requirements.txt
```

## Run

```bash
python stats.py 4 8 15 16 23 42
# count: 6
# mean:  18.0
# median: 15.5
```

## Test

```bash
python -m pytest -q
```

One test starts **red** on purpose — that's the demo bug. The rest are green.
