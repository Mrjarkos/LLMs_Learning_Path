"""Build polished, self-contained HTML artifacts for the AI course package.

Converts each markdown doc to a standalone styled HTML page (embedded CSS, no
external requests — respects the corp-boundary rule) and generates an
index.html landing page linking every artifact.

Run:  python build_html.py
"""

import re
from pathlib import Path

import markdown

ROOT = Path(__file__).parent

# (source_md, output_html, nav_title, subtitle)
DOCS = [
    ("speaker-script.md", "speaker-script.html", "Speaker Script",
     "Timed notes, slide by slide"),
    ("demo-runbook.md", "demo-runbook.html", "Demo Runbook",
     "Live-demo beats + fallbacks"),
    ("handout-exercise.md", "handout-exercise.html", "Hands-On Handout",
     "Attendee exercise sheet"),
    ("facilitator-notes.md", "facilitator-notes.html", "Facilitator Notes",
     "Prereqs, room setup, timing recovery"),
]

CSS = """
:root {
  --ink: #1a1d24; --muted: #5b6472; --line: #e4e7ec; --bg: #f7f8fa;
  --card: #ffffff; --accent: #4f46e5; --accent-weak: #eef0ff;
  --code-bg: #1e222b; --code-ink: #e6e9ef; --ok: #0f9d58; --warn: #b26a00;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0; background: var(--bg); color: var(--ink);
  font: 16px/1.65 -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
}
.wrap { max-width: 820px; margin: 0 auto; padding: 0 24px 96px; }
header.page {
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  color: #fff; padding: 40px 0 34px; margin-bottom: 40px;
}
header.page .wrap { padding-bottom: 0; }
header.page .kicker {
  text-transform: uppercase; letter-spacing: .14em; font-size: 12px;
  opacity: .85; margin: 0 0 8px;
}
header.page h1 { margin: 0; font-size: 30px; line-height: 1.15; }
header.page p.sub { margin: 10px 0 0; opacity: .9; font-size: 16px; }
a.back {
  display: inline-block; margin-top: 18px; color: #fff; text-decoration: none;
  font-size: 14px; opacity: .9; border-bottom: 1px solid rgba(255,255,255,.4);
}
a.back:hover { opacity: 1; }
h1, h2, h3 { line-height: 1.25; }
h2 {
  margin-top: 40px; padding-bottom: 6px; border-bottom: 2px solid var(--line);
  font-size: 22px;
}
h3 { margin-top: 28px; font-size: 17px; color: #2b2f38; }
a { color: var(--accent); }
p, li { color: #2b2f38; }
blockquote {
  margin: 18px 0; padding: 12px 18px; background: var(--accent-weak);
  border-left: 4px solid var(--accent); border-radius: 6px; color: #322f6b;
}
code {
  background: #eef0f3; padding: .12em .4em; border-radius: 4px;
  font: 13.5px/1.5 "SF Mono", "Cascadia Code", Consolas, monospace; color: #b3306b;
}
pre {
  background: var(--code-bg); color: var(--code-ink); padding: 16px 18px;
  border-radius: 10px; overflow-x: auto; font-size: 13.5px; line-height: 1.55;
}
pre code { background: none; color: inherit; padding: 0; }
table {
  border-collapse: collapse; width: 100%; margin: 18px 0; font-size: 14.5px;
  background: var(--card); border-radius: 8px; overflow: hidden;
  box-shadow: 0 1px 2px rgba(16,24,40,.06);
}
th, td { text-align: left; padding: 10px 14px; border-bottom: 1px solid var(--line); }
th { background: #f0f1f6; font-weight: 600; }
tr:last-child td { border-bottom: none; }
hr { border: none; border-top: 1px solid var(--line); margin: 34px 0; }
figure { max-width: 580px; margin: 24px auto; }
figure svg { width: 100%; height: auto; display: block; }
ul { padding-left: 22px; }
li.task { list-style: none; margin-left: -22px; }
li.task .box { color: var(--muted); margin-right: 8px; }
li.task.done .box { color: var(--ok); }
.footer { margin-top: 60px; color: var(--muted); font-size: 13px; text-align: center; }
/* Landing page cards */
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 18px; margin-top: 8px; }
.card {
  background: var(--card); border: 1px solid var(--line); border-radius: 12px;
  padding: 20px; text-decoration: none; color: inherit; display: block;
  transition: transform .12s ease, box-shadow .12s ease, border-color .12s;
}
.card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(16,24,40,.10);
  border-color: #c7c9f5; }
.card .tag {
  display: inline-block; font-size: 11px; letter-spacing: .08em; text-transform: uppercase;
  color: var(--accent); background: var(--accent-weak); padding: 3px 8px; border-radius: 20px;
}
.card h3 { margin: 12px 0 6px; }
.card p { margin: 0; color: var(--muted); font-size: 14px; }
.meta { display: flex; gap: 22px; flex-wrap: wrap; margin: 24px 0 0; font-size: 14px; color: var(--muted); }
.meta b { color: var(--ink); }
@media print {
  header.page { background: none; color: #000; border-bottom: 2px solid #000; }
  header.page .kicker, a.back { color: #000; }
  .card:hover { transform: none; box-shadow: none; }
  body { background: #fff; }
}
"""


def render_tasklists(html: str) -> str:
    """Turn '<li>[ ] ...' / '<li>[x] ...' into styled checkbox items."""
    html = re.sub(r"<li>\[ \]\s*",
                  '<li class="task"><span class="box">&#9744;</span>', html)
    html = re.sub(r"<li>\[[xX]\]\s*",
                  '<li class="task done"><span class="box">&#9745;</span>', html)
    return html


def page(title: str, subtitle: str, body: str, *, back=True) -> str:
    back_link = '<a class="back" href="index.html">&larr; Course home</a>' if back else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — AI Course</title>
<style>{CSS}</style>
</head>
<body>
<header class="page"><div class="wrap">
<p class="kicker">Programming with AI Agents</p>
<h1>{title}</h1>
<p class="sub">{subtitle}</p>
{back_link}
</div></header>
<main class="wrap">
{body}
<div class="footer">CARIAD &middot; beginner AI course &middot; built from the course markdown</div>
</main>
</body></html>"""


def convert_doc(src, out, title, subtitle):
    md = (ROOT / src).read_text(encoding="utf-8")
    html_body = markdown.markdown(
        md, extensions=["tables", "fenced_code", "sane_lists", "attr_list"]
    )
    html_body = render_tasklists(html_body)
    (ROOT / out).write_text(page(title, subtitle, html_body), encoding="utf-8")
    print(f"  {src} -> {out}")


def build_index():
    cards = [
        ("Deck", "Slides", "slides.html",
         "The illustrated deck with SVG diagrams. Present fullscreen; press "
         "<b>P</b> for presenter view. Ctrl/Cmd+P &rarr; Save as PDF."),
        ("Quiz", "Quiz · Level 1", "quiz.html",
         "10 fundamentals with instant feedback, explanations, and a score."),
        ("Quiz", "Quiz · Level 2", "quiz-advanced.html",
         "10 harder, scenario-based questions for once the basics click."),
    ]
    for src, out, title, subtitle in DOCS:
        cards.append(("Facilitator", title, out, subtitle))
    cards.append(("Backup", "Demo fallback", "demo-fallback/demo-fallback.html",
                  "Terminal storyboard to narrate if the live demo fails."))
    cards.append(("Code", "Sample repo", "sample-repo/README.md",
                  "stats-cli: seeded bug + failing test for demo & hands-on."))

    card_html = "\n".join(
        f'<a class="card" href="{href}"><span class="tag">{tag}</span>'
        f'<h3>{t}</h3><p>{d}</p></a>'
        for tag, t, href, d in cards
    )
    loop_svg = (ROOT / "assets" / "loop.svg").read_text(encoding="utf-8")
    body = f"""
<p>A 45-minute, hands-on introduction to programming with AI agents, for
developers who are new to AI. Everything below is self-contained — open the
deck to present, hand out the exercise sheet, and drive the live demo from the
runbook.</p>

<figure style="margin:24px 0;text-align:center">
{loop_svg}
<figcaption style="color:#5b6472;font-size:14px;margin-top:6px">
The one idea the whole course hangs on: an agent is an LLM in this loop.
</figcaption>
</figure>

<div class="meta">
  <span><b>45</b> minutes</span>
  <span><b>7</b> segments</span>
  <span><b>1</b> live demo</span>
  <span><b>1</b> hands-on exercise</span>
</div>

<h2>Artifacts</h2>
<div class="cards">
{card_html}
</div>

<h2>Run order on the day</h2>
<ol>
<li>Open <b>Slides</b> and present segments 1&ndash;3 (mental model + core skill).</li>
<li>Drive the <b>Live demo</b> from the runbook on the sample repo.</li>
<li>Hand out the <b>Exercise sheet</b>; attendees do the hands-on.</li>
<li>Return to slides for &ldquo;how it&rsquo;s built&rdquo; + takeaways.</li>
</ol>

<h2>Render / rebuild</h2>
<pre><code>python build_html.py                       # rebuild these HTML pages
python build_quizzes.py                    # rebuild both quiz levels
python demo-fallback/record_fallback.py    # rebuild the demo fallback
npx @marp-team/marp-cli slides.md --html   # rebuild the deck HTML</code></pre>
<p><small>PDF export via Marp needs a local Chrome/Chromium (blocked on this
machine). For a PDF, open the deck and use your browser&rsquo;s
&ldquo;Save as PDF&rdquo;.</small></p>
"""
    (ROOT / "index.html").write_text(
        page("AI Agents — Course Home",
             "45-minute beginner course for programmers", body, back=False),
        encoding="utf-8",
    )
    print("  index.html")


if __name__ == "__main__":
    print("Building HTML artifacts...")
    for args in DOCS:
        convert_doc(*args)
    build_index()
    print("Done.")
