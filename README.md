# signal-finder

A Reddit front-page digest curator built around the **A/B/C
context-engineering framework**. The fetcher produces raw post JSON;
Claude Code runs the curation in conversation; a small renderer turns
the curated JSON into a single-day HTML digest plus a combined feed.

This repo is teaching material for MPA 2026. The lesson it carries is
small but important: a tiny set of markdown files (the A, B, and C
context documents in `context/`) controls a working content-curation
product without changing any code. **Bad curation is usually a context
problem, not an AI problem.**

## Quickstart

One-time setup (Python 3.10+ required):

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Then in Claude Code, from this repo:

```
/signal-finder                 # fetches Reddit, curates, renders
```

Then in your shell:

```sh
open digests/all.html          # read the rendered digest
```

Before your first run, open `context/B_preference_context.md` and fill
in the placeholders — that file is empty by design so you can put your
own preferences in it.

> If you already use [`uv`](https://docs.astral.sh/uv/), you can skip
> the venv step — substitute `uv run` for `python3` in any command, and
> `uv` will resolve dependencies on the fly from each script's inline
> metadata.

## Documentation

This project follows the [Diátaxis](https://diataxis.fr/) documentation
framework. Each doc serves one purpose; pick the one that matches your
goal.

| You want to… | Read |
|---|---|
| **Learn the project** by producing your first digest | [Tutorial](docs/tutorial.md) |
| **Get a specific thing done** (change a setting, add a source, audit filters) | [How-to guides](docs/how-to.md) |
| **Look up a field, flag, file path, or schema** | [Reference](docs/reference.md) |
| **Understand why** the project is shaped the way it is | [Explanation](docs/explanation.md) |

## Repository layout

| Path | What's there |
|---|---|
| `context/` | The **A/B/C** context files — read by the curator on every run. Edit B to set your preferences. |
| `fetch_reddit.py` | Reddit front-page connector |
| `extract_url.py` | Probe for testing trafilatura on a single URL |
| `.claude/skills/signal-finder/` | The Claude Code skill (workflow + renderer + schema) |
| `posts/` | Cached fetched posts (gitignored) |
| `digests/` | Curated JSON + rendered HTML (gitignored) |
| `reflections/` | Per-run markdown reflection (gitignored) |
