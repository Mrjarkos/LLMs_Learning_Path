"""Generate a self-contained fallback walkthrough of the live demo.

If the live agent demo fails on the day (network, model latency, laptop
gremlins), open demo-fallback.html and narrate it instead. It runs the REAL
demo commands against a throwaway copy of the sample repo, captures the actual
pytest output (red -> green), and renders it as a terminal-styled storyboard
with the canned prompts you'd have typed.

Run:  python record_fallback.py
No external tools (no asciinema/Chromium). Never touches the real sample-repo.
"""

import html
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
SAMPLE = (HERE / ".." / "sample-repo").resolve()

BUGGY_MEDIAN = """    ordered = sorted(values)
    mid = len(ordered) // 2
    return ordered[mid]"""

FIXED_MEDIAN = """    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2 == 0:
        return (ordered[mid - 1] + ordered[mid]) / 2
    return ordered[mid]"""

INTENT_PROMPT = (
    "The test `test_median_even` fails: the median of an even-length list "
    "should be the average of the two middle values, not the higher one. "
    "Show me a plan before changing anything, then fix `statslib.py` and run "
    "the tests until they pass."
)

EXAMPLE_PLAN = """Plan:
  1. Read statslib.py -> median() returns ordered[mid]; for even length that's
     the higher middle element, not the average.
  2. Branch on parity: if len is even, return the mean of the two middle
     values; otherwise keep ordered[mid].
  3. Run pytest to confirm test_median_even (and the others) pass.
Proceed?"""

STEER_PROMPT = (
    "Good. Now also make `median` raise a clear ValueError on an empty list "
    "instead of an IndexError, and add a test for it."
)


def run(cmd, cwd):
    """Run a command, return (exit_code, combined_output)."""
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).rstrip()


def build():
    if not SAMPLE.exists():
        sys.exit(f"sample-repo not found at {SAMPLE}")

    work = Path(tempfile.mkdtemp(prefix="demo-fallback-"))
    try:
        for name in ("statslib.py", "test_statslib.py", "stats.py"):
            shutil.copy(SAMPLE / name, work / name)

        # Beat 1 — red
        red_code, red_out = run([sys.executable, "-m", "pytest", "-q"], work)

        # Apply the fix the agent would make
        src = (work / "statslib.py").read_text(encoding="utf-8")
        if BUGGY_MEDIAN not in src:
            sys.exit("could not locate the buggy median block to patch")
        (work / "statslib.py").write_text(
            src.replace(BUGGY_MEDIAN, FIXED_MEDIAN), encoding="utf-8")

        # Beat 5 — green
        green_code, green_out = run([sys.executable, "-m", "pytest", "-q"], work)
    finally:
        shutil.rmtree(work, ignore_errors=True)

    render(red_out, red_code, green_out, green_code)


def term(text):
    return f'<pre class="term">{html.escape(text)}</pre>'


def prompt(text):
    return (f'<div class="prompt"><span class="tag">you type &rarr;</span>'
            f'{html.escape(text)}</div>')


def diff_block():
    return (
        '<pre class="term diff">'
        '<span class="ctx">def median(values: List[float]) -&gt; float:</span>\n'
        '<span class="ctx">    ordered = sorted(values)</span>\n'
        '<span class="ctx">    mid = len(ordered) // 2</span>\n'
        '<span class="add">+    if len(ordered) % 2 == 0:</span>\n'
        '<span class="add">+        return (ordered[mid - 1] + ordered[mid]) / 2</span>\n'
        '<span class="ctx">    return ordered[mid]</span>'
        '</pre>')


def render(red_out, red_code, green_out, green_code):
    def beat(n, title, note, *blocks):
        return f"""
<section class="beat">
  <div class="bn">Beat {n}</div>
  <h2>{title}</h2>
  <p class="note">{note}</p>
  {''.join(blocks)}
</section>"""

    body = "".join([
        beat(1, "Show the failing test",
             "Run the suite live so the room sees the red.",
             term("$ python -m pytest -q\n" + red_out),
             f'<p class="status bad">exit code {red_code} — 1 failed, 3 passed</p>'),
        beat(2, "Give intent, not instructions",
             "Paste this — don't type it live. Notice: goal + constraints + verify.",
             prompt(INTENT_PROMPT)),
        beat(3, "Read the plan aloud",
             "The agent proposes before it edits. Read it like a junior's PR "
             "description. (Example plan — yours will vary.)",
             term(EXAMPLE_PLAN)),
        beat(4, "Approve — it edits + reruns tests",
             "One-line fix: branch on even length and average the two middles.",
             diff_block()),
        beat(5, "Green — but still read the diff",
             "The agent runs the suite itself. Verification is the step "
             "beginners skip.",
             term("$ python -m pytest -q\n" + green_out),
             f'<p class="status ok">exit code {green_code} — all passed</p>'),
        beat(6, "Steer once, in plain English",
             "Correction is conversational — you don't hand-edit.",
             prompt(STEER_PROMPT)),
    ])

    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Demo Fallback — Live-Demo Storyboard</title>
<style>
:root{{--ink:#1a1d24;--muted:#5b6472;--line:#e4e7ec;--bg:#f7f8fa;--accent:#4f46e5;
  --code-bg:#12151c;--code-ink:#e6e9ef;--ok:#0f9d58;--bad:#d93838}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.6 -apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}}
.wrap{{max-width:820px;margin:0 auto;padding:0 22px 90px}}
header.page{{background:linear-gradient(135deg,#4f46e5,#7c3aed);color:#fff;padding:36px 0 28px}}
header.page .wrap{{padding-bottom:0}}
.kicker{{text-transform:uppercase;letter-spacing:.14em;font-size:12px;opacity:.85;margin:0 0 8px}}
header.page h1{{margin:0;font-size:26px}}
header.page p{{margin:8px 0 0;opacity:.9}}
a.back{{display:inline-block;margin-top:14px;color:#fff;text-decoration:none;font-size:14px;
  opacity:.9;border-bottom:1px solid rgba(255,255,255,.4)}}
.banner{{background:#fff6e6;border:1px solid #f0d9a8;color:#7a5600;border-radius:10px;
  padding:12px 16px;margin:24px 0;font-size:14.5px}}
.beat{{background:#fff;border:1px solid var(--line);border-radius:14px;padding:22px;margin:20px 0;
  box-shadow:0 1px 2px rgba(16,24,40,.05)}}
.bn{{color:var(--accent);font-weight:700;font-size:12px;letter-spacing:.08em;text-transform:uppercase}}
.beat h2{{margin:4px 0 6px;font-size:19px}}
.note{{margin:0 0 14px;color:var(--muted);font-size:14.5px}}
pre.term{{background:var(--code-bg);color:var(--code-ink);padding:16px 18px;border-radius:10px;
  overflow-x:auto;font:13px/1.55 "Cascadia Code",Consolas,monospace;white-space:pre-wrap;word-break:break-word}}
pre.diff .add{{color:#7ee2a8}}
pre.diff .ctx{{color:#aeb4c0}}
.prompt{{background:#eef0ff;border:1px solid #c7c9f5;border-radius:10px;padding:14px 16px;
  color:#312e81;font-size:15px}}
.prompt .tag{{display:block;font-size:11px;letter-spacing:.08em;text-transform:uppercase;
  color:var(--accent);font-weight:700;margin-bottom:6px}}
.status{{font-weight:700;font-size:13px;margin:10px 0 0}}
.status.ok{{color:var(--ok)}}
.status.bad{{color:var(--bad)}}
.footer{{margin-top:44px;color:var(--muted);font-size:13px;text-align:center}}
</style>
</head>
<body>
<header class="page"><div class="wrap">
<p class="kicker">Live-demo fallback</p>
<h1>If the live demo fails — narrate this</h1>
<p>Real pytest output captured from the sample repo. Talk the room through the loop.</p>
<a class="back" href="../index.html">&larr; Course home</a>
</div></header>
<main class="wrap">
<div class="banner"><b>How to use:</b> only if the live agent won't cooperate.
The commands and their red/green output below are real; the plan and prompts
are the canned ones from <code>demo-runbook.md</code>. Read it beat by beat —
the <i>loop</i> is the lesson, live execution is the garnish.</div>
{body}
<div class="footer">Generated by record_fallback.py &middot; regenerate anytime</div>
</main>
</body></html>"""

    out = HERE / "demo-fallback.html"
    out.write_text(doc, encoding="utf-8")
    print(f"  wrote {out.name}  (red exit {red_code} -> green exit {green_code})")


if __name__ == "__main__":
    print("Building demo fallback...")
    build()
    print("Done.")
