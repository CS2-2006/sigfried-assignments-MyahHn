#!/usr/bin/env python3
"""Render a curator JSON file into an HTML digest and a Markdown reflection.

Input:  digests/<YYYY-MM-DD>.json (matching references/output_schema.md)
Output: digests/<YYYY-MM-DD>.html  (single-day view)
        digests/all.html           (combined feed, every JSON in digests/, newest first)
        reflections/<YYYY-MM-DD>.md

Pure stdlib. No external deps — runs with plain `python` or `uv run`.
"""

from __future__ import annotations

import json
import sys
from html import escape
from pathlib import Path


PAGE_CSS = """
:root {
  --bg: #fafaf7;
  --surface: #ffffff;
  --ink: #1f2330;
  --muted: #6b7280;
  --line: #e7e5df;
  --accent: #4f46e5;
  --accent-soft: #eef2ff;
  --wild: #fff7ed;
  --wild-edge: #fb923c;
}
* { box-sizing: border-box; }
body {
  font-family: -apple-system, system-ui, "Segoe UI", sans-serif;
  max-width: 680px;
  margin: 3em auto;
  padding: 0 1.25em;
  line-height: 1.55;
  color: var(--ink);
  background: var(--bg);
}
h1 {
  font-size: 1.4rem;
  font-weight: 600;
  letter-spacing: -0.01em;
  margin: 0 0 0.25em;
}
.subtitle { color: var(--muted); font-size: 0.9rem; margin-bottom: 2.5em; }
h2 {
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
  margin: 2.5em 0 1em;
}
ol, ul { padding: 0; margin: 0; list-style: none; }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
.muted { color: var(--muted); font-size: 0.9rem; }

.day {
  margin-bottom: 4em;
  padding-top: 1.5em;
  border-top: 1px solid var(--line);
}
.day:first-of-type { border-top: none; padding-top: 0; }
.day-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 1.25em;
}
.day-date {
  font-size: 1rem;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: -0.01em;
}
.day-anchor {
  font-size: 0.75rem;
  color: var(--muted);
  font-variant-numeric: tabular-nums;
}

.item {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 1em 1.1em;
  margin-bottom: 0.75em;
}
.item-head {
  display: flex;
  align-items: baseline;
  gap: 0.75em;
}
.rank {
  color: var(--accent);
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  font-size: 0.95rem;
  min-width: 1.1em;
}
.item-title {
  font-size: 1rem;
  font-weight: 500;
  color: var(--ink);
  flex: 1;
}
.item-title:hover { color: var(--accent); text-decoration: none; }
.item-meta { margin-top: 0.5em; }
.item-meta > summary {
  cursor: pointer;
  color: var(--muted);
  font-size: 0.8rem;
  list-style: none;
  padding: 0.15em 0;
  user-select: none;
}
.item-meta > summary::-webkit-details-marker { display: none; }
.item-meta > summary::before {
  content: "›";
  display: inline-block;
  margin-right: 0.4em;
  transition: transform 0.15s ease;
}
.item-meta[open] > summary::before { transform: rotate(90deg); }
.meta-body {
  margin-top: 0.5em;
  padding-top: 0.75em;
  border-top: 1px dashed var(--line);
}
.reason { margin: 0 0 0.75em; font-size: 0.92rem; }
.meta-row { display: flex; align-items: center; gap: 0.5em; margin-top: 0.4em; flex-wrap: wrap; }
.meta-label {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
}
.score { font-variant-numeric: tabular-nums; font-size: 0.85rem; }
.tag {
  display: inline-block;
  padding: 0.1em 0.55em;
  border-radius: 999px;
  background: var(--accent-soft);
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 500;
}
.source {
  display: inline-block;
  padding: 0.1em 0.55em;
  border-radius: 4px;
  font-size: 0.65rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  background: #eef2f7;
  color: #4b5563;
  flex-shrink: 0;
}
.source-reddit  { background: #ffedd5; color: #c2410c; }

.original-block { margin-top: 0.7em; }
.original-text {
  margin: 0.3em 0 0;
  padding: 0.4em 0.7em;
  border-left: 2px solid var(--line);
  color: var(--muted);
  font-size: 0.85rem;
  font-style: italic;
  line-height: 1.45;
}

.skip-block, .reflection, .filtered-block { margin-top: 1.5em; font-size: 0.85rem; }
.skip-block > summary, .reflection > summary, .filtered-block > summary {
  cursor: pointer;
  color: var(--muted);
  padding: 0.5em 0;
}
.skip { margin-top: 0.5em; }
.skip li {
  padding: 0.4em 0;
  border-bottom: 1px solid var(--line);
  font-size: 0.92rem;
}
.skip li:last-child { border-bottom: none; }
.filtered { margin-top: 0.5em; }
.filtered li {
  display: flex;
  align-items: baseline;
  gap: 0.6em;
  padding: 0.35em 0;
  border-bottom: 1px solid var(--line);
  font-size: 0.88rem;
}
.filtered li:last-child { border-bottom: none; }
.filtered li a { flex: 1; color: var(--muted); }
.filter-rule {
  display: inline-block;
  padding: 0.05em 0.5em;
  border-radius: 3px;
  font-size: 0.65rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  background: #f3f4f6;
  color: #6b7280;
}
.rule-drama      { background: #fce7f3; color: #be185d; }
.rule-politics   { background: #ede9fe; color: #6d28d9; }
.rule-ragebait   { background: #fee2e2; color: #b91c1c; }
.rule-crypto     { background: #fef3c7; color: #92400e; }
.rule-repetitive { background: #e5e7eb; color: #4b5563; }
.rule-meme       { background: #ccfbf1; color: #0f766e; }
.reflection pre {
  white-space: pre-wrap;
  background: var(--surface);
  border: 1px solid var(--line);
  padding: 1em;
  border-radius: 6px;
  font-size: 0.85rem;
}

.wildcard {
  margin-top: 1.5em;
  padding: 1em 1.1em;
  background: var(--wild);
  border-left: 3px solid var(--wild-edge);
  border-radius: 4px;
}
.wildcard h2 { margin-top: 0; color: var(--wild-edge); }
.wildcard p { margin: 0.3em 0; }
"""


def render_reflection_md(reflection: dict) -> str:
    return (
        "# Reflection\n\n"
        "## Weakness in A (source context)\n"
        f"{reflection.get('weakness_in_a', '(none)')}\n\n"
        "## Weakness in B (preference context)\n"
        f"{reflection.get('weakness_in_b', '(none)')}\n\n"
        "## Suggested edit before tomorrow's run\n"
        f"{reflection.get('suggested_edit', '(none)')}\n"
    )


def render_day_section(result: dict, date_iso: str, with_header: bool = True) -> str:
    """Render the inner content for a single day (no <html> shell)."""
    items_html: list[str] = []
    for item in result.get("digest_items", []):
        url = escape(item.get("url", ""))
        title = escape(item.get("title", ""))
        rank = item.get("rank", "?")
        relevance = item.get("relevance_score", 0)
        source = (item.get("source") or "").lower()
        source_badge = (
            f'<span class="source source-{escape(source)}">{escape(source)}</span>'
            if source
            else ""
        )
        tags = "".join(
            f'<span class="tag">{escape(t)}</span>' for t in item.get("tags", [])
        )
        reason = escape(item.get("reason_matched", ""))
        original_title = (item.get("original_title") or "").strip()
        original_block = (
            f"""<div class="original-block">
        <div class="meta-label">original</div>
        <blockquote class="original-text">{escape(original_title)}</blockquote>
      </div>"""
            if original_title
            else ""
        )
        items_html.append(
            f"""<li class="item">
  <div class="item-head">
    <span class="rank">{rank}</span>
    <a class="item-title" href="{url}">{title}</a>
    {source_badge}
  </div>
  <details class="item-meta">
    <summary>details</summary>
    <div class="meta-body">
      <p class="reason">{reason}</p>
      <div class="meta-row">
        <span class="meta-label">relevance</span>
        <span class="score">{relevance}</span>
      </div>
      <div class="meta-row tags">{tags or '<span class="muted">no tags</span>'}</div>
      {original_block}
    </div>
  </details>
</li>"""
        )

    skip_items: list[str] = []
    for item in result.get("skip_worthy", []):
        skip_items.append(
            f"""<li>
  <a href="{escape(item.get('url', ''))}">{escape(item.get('title', ''))}</a>
  <span class="muted">— {escape(item.get('reason_skipped', ''))}</span>
</li>"""
        )
    skip_html = ""
    if skip_items:
        skip_html = f"""
  <details class="skip-block">
    <summary>Skip-worthy</summary>
    <ul class="skip">{''.join(skip_items)}</ul>
  </details>
"""

    wc = result.get("wildcard") or {}
    wildcard_html = ""
    if wc:
        wildcard_html = f"""
  <section class="wildcard">
    <h2>Wildcard</h2>
    <p><a href="{escape(wc.get('url', ''))}">{escape(wc.get('title', ''))}</a></p>
    <p class="muted">{escape(wc.get('reason', ''))}</p>
  </section>
"""

    filtered_items: list[str] = []
    for item in result.get("filtered_out", []):
        rule = (item.get("rule") or "").lower()
        filtered_items.append(
            f"""<li>
  <a href="{escape(item.get('url', ''))}">{escape(item.get('title', ''))}</a>
  <span class="filter-rule rule-{escape(rule)}">{escape(rule)}</span>
</li>"""
        )
    filtered_html = ""
    if filtered_items:
        filtered_html = f"""
  <details class="filtered-block">
    <summary>Filtered out ({len(filtered_items)})</summary>
    <ul class="filtered">{''.join(filtered_items)}</ul>
  </details>
"""

    reflection_md = render_reflection_md(result.get("reflection") or {})
    reflection_html = f"""
  <details class="reflection">
    <summary>How to improve A or B</summary>
    <pre>{escape(reflection_md)}</pre>
  </details>
"""

    header_html = ""
    if with_header:
        header_html = f"""  <div class="day-header">
    <span class="day-date">{date_iso}</span>
    <a class="day-anchor" href="#{date_iso}">#</a>
  </div>
"""

    return f"""<section class="day" id="{date_iso}">
{header_html}  <ol>{''.join(items_html)}</ol>
{wildcard_html}{skip_html}{filtered_html}{reflection_html}
</section>"""


def wrap_page(title: str, subtitle: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{escape(title)}</title>
  <style>{PAGE_CSS}</style>
</head>
<body>
  <h1>{escape(title)}</h1>
  <div class="subtitle">{escape(subtitle)}</div>
{body}
</body>
</html>
"""


def render_single_html(result: dict, date_iso: str) -> str:
    body = render_day_section(result, date_iso, with_header=False)
    return wrap_page("Curated Digest", date_iso, body)


def render_combined_html(days: list[tuple[str, dict]]) -> str:
    """days is a list of (date_iso, result) sorted newest-first."""
    if not days:
        body = '<p class="muted">No digests yet.</p>'
        return wrap_page("Curated Feed", "no entries", body)

    sections = "\n".join(render_day_section(r, d, with_header=True) for d, r in days)
    span = f"{days[-1][0]} – {days[0][0]}" if len(days) > 1 else days[0][0]
    subtitle = f"{len(days)} day{'s' if len(days) != 1 else ''} · {span}"
    return wrap_page("Curated Feed", subtitle, sections)


def collect_days(digests_dir: Path) -> list[tuple[str, dict]]:
    days = []
    for path in sorted(digests_dir.glob("*.json")):
        try:
            days.append((path.stem, json.loads(path.read_text())))
        except json.JSONDecodeError:
            print(f"warning: skipping malformed JSON {path}", file=sys.stderr)
    days.sort(key=lambda dr: dr[0], reverse=True)
    return days


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: render_digest.py <path-to-curator-json>", file=sys.stderr)
        return 2

    json_path = Path(sys.argv[1]).resolve()
    if not json_path.exists():
        print(f"file not found: {json_path}", file=sys.stderr)
        return 1

    date_iso = json_path.stem
    result = json.loads(json_path.read_text())

    project_root = json_path.parent.parent
    digests_dir = project_root / "digests"
    reflections_dir = project_root / "reflections"
    digests_dir.mkdir(exist_ok=True)
    reflections_dir.mkdir(exist_ok=True)

    html_path = digests_dir / f"{date_iso}.html"
    md_path = reflections_dir / f"{date_iso}.md"
    all_path = digests_dir / "all.html"

    html_path.write_text(render_single_html(result, date_iso))
    md_path.write_text(render_reflection_md(result.get("reflection") or {}))

    days = collect_days(digests_dir)
    all_path.write_text(render_combined_html(days))

    print(f"Digest:     {html_path}")
    print(f"Reflection: {md_path}")
    print(f"Combined:   {all_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
