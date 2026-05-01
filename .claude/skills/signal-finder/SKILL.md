---
name: signal-finder
description: Generate today's curated digest from Reddit's front page using the A/B/C context-engineering framework. Use this skill whenever the user runs /signal-finder, asks for "today's digest," asks "what's worth reading from Reddit," wants to refresh their curated picks, or asks Claude to rank/filter the Reddit front page. The skill pulls the source, applies the user's context files in `context/`, and writes a ranked HTML digest plus a markdown reflection on what's weak in A or B.
---

# Signal Finder

The lesson: **the harness is the runtime, and the markdown files in `context/` are the context that makes it behave correctly.** No API call. The cognitive work (filter, score, rank, reflect) happens in your reasoning. The deterministic work (HTML formatting) happens in a bundled script. The user's preferences live in `context/B_preference_context.md` and the curation process lives in `context/C_process_guide.md` — those two are the active context for ranking.

## Workflow

1. **Fetch posts.** Run `python3 fetch_reddit.py`. It writes `posts/<YYYY-MM-DD>-reddit.json` and downloads any direct images to `posts/images/<YYYY-MM-DD>/`. No AI runs in this step — it's just the source connector. (Students who installed deps with `uv` can substitute `uv run fetch_reddit.py`.)
2. **Load the active context.** Read these two files — they are the *minimum* needed to do the work:
   - `context/C_process_guide.md` — the steps you must follow
   - `context/B_preference_context.md` — the user's taste
3. **Read the posts JSON** from step 1. For each post with a non-empty `image_path`, use the Read tool on that path before scoring; the image often reveals what the Reddit headline obscured.
4. **Execute C's process** against the posts, applying B's preferences. Produce a single JSON object matching the schema in `references/output_schema.md` (read it now if you don't have the shape memorized). Save your JSON to `digests/<YYYY-MM-DD>.json` — keeping it on disk lets the user re-render or debug without recomputing the curation.
5. **Render.** Run `python3 .claude/skills/signal-finder/scripts/render_digest.py digests/<YYYY-MM-DD>.json`. The script is pure stdlib — no extra deps needed. It writes `digests/<YYYY-MM-DD>.html` and `reflections/<YYYY-MM-DD>.md`. Don't hand-write the HTML — the script handles deterministic formatting so every run looks consistent.
6. **Print the digest path** so the user can `open` it.

## Just-in-time references

Don't read these unless you actually need them. Reading them eagerly wastes context.

- **`references/output_schema.md`** — the exact JSON shape your step-4 output must match. Read once if you're unsure of the shape; ignore otherwise.
- **`references/rules.md`** — hard constraints (link integrity, citation specificity, reflection concreteness, content respect). Read if you're about to do something that might violate one — e.g. before writing `reason_matched` lines, or before composing the reflection.
- **`context/A_source_context.md`** — describes the post fields and platform rules. The post JSON is largely self-describing, so consult A only if a field's meaning is unclear or you need a rule it spells out.

## Why this skill is split this way

- The renderer is a script because rewriting the same HTML scaffolding every day burns tokens for zero value. Bundle it once, reuse it forever.
- B and C are the *active* context — load them. A is a *lookup* — open it only when a question arises.
- References are pulled in on demand so the skill body stays lean enough to read top-to-bottom in a few seconds.

The pedagogical point students should take away: the AI didn't change between yesterday and today, but editing B or C will visibly change tomorrow's digest. **Bad curation is usually a context problem, not an AI problem.**
