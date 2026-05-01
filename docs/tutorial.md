# Tutorial — Build your first digest

This tutorial walks you through producing your first signal-finder digest
in under ten minutes. You will fetch Reddit's front page, fill in your
preferences, let Claude curate through the A/B/C context, and open the
rendered HTML in your browser. Then you'll edit one preference and
re-run, and watch the ranking shift.

You will not learn *why* the project is shaped this way here — see
[Explanation](explanation.md) for that. You will not learn every setting
— see [How-to guides](how-to.md). The goal of this tutorial is one
successful first run.

## What you need

- [Claude Code](https://claude.com/claude-code) installed and signed in
- Python 3.10 or newer (`python3 --version` to check)

No accounts, no API keys, no `.env` file. Reddit's front page is public.

## Step 1 — Get the project and install dependencies

```sh
git clone https://github.com/<owner>/MPA_2026.git
cd MPA_2026
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Keep the venv activated for the rest of this tutorial — when Claude
Code calls `python3 fetch_reddit.py`, it'll use this environment.

> Already using [`uv`](https://docs.astral.sh/uv/)? Skip the venv and
> pip steps — `uv run fetch_reddit.py` resolves dependencies from the
> inline metadata at the top of the script.

## Step 2 — Fill in your preferences

Open `context/B_preference_context.md` in any editor. The file is
intentionally empty — every section has placeholder bullets you need to
replace before the curator has anything to work with.

At minimum, edit:

- **§1 *I want*** — list 3–10 topics you want surfaced. Be concrete:
  *"Hands-on woodworking projects"* beats *"interesting stuff."*
- **§2 *I do not want*** — list short labels for content you want
  dropped (e.g. `politics`, `sports`, `drama`). Whatever label you write
  here is what the curator records when it filters a post.

The other sections have reasonable defaults; edit them later if you want
finer control.

Save the file.

## Step 3 — Run the curation

Open Claude Code in this repo and type:

```
/signal-finder
```

Claude will fetch posts from Reddit's front page, read the A, B, and C
context files, score and rank every post that survives the hard-filter
rules, and write the curated output to disk.

When it's done, you'll have:

```
posts/2026-04-29-reddit.json    # Reddit front page
posts/images/2026-04-29/        # Direct images downloaded for vision-aware titles
digests/2026-04-29.json         # The curated output
digests/2026-04-29.html         # Single-day rendered view
digests/all.html                # Combined feed of every digest you've produced
reflections/2026-04-29.md       # Claude's notes on what went well and what didn't
```

## Step 4 — Open the digest

```sh
open digests/all.html
```

You should see a ranked list of items. Each one has a rank number, a
synthesized title, a small `reddit` source badge, and a *details*
dropdown that reveals the curator's reason, relevance score, tags, and
the original headline.

Scroll to the bottom and click **Filtered out** to see what got dropped
and which rule fired (using the labels you wrote in B §2).

## Step 5 — Change one preference

Open `context/B_preference_context.md` again. Add or edit a bullet in
§1. For example:

```
- Climate and weather news
```

Save the file.

## Step 6 — Re-run

In Claude Code, type `/signal-finder` again. Open `digests/all.html` once
it's regenerated.

The list has re-ranked. Anything matching your new bullet has moved up;
what doesn't match has slipped down. The fetched posts didn't change.
The AI didn't change. The only thing that changed was one line in a
markdown file.

That is the whole loop. Three files in `context/` decide *what* gets
fetched, *what* you want, and *how* the curator selects. Edit them; the
digest reshapes itself.

## Where to go next

- A specific change in mind? → [How-to guides](how-to.md)
- Want to know what every field means? → [Reference](reference.md)
- Curious why the project splits context this way? → [Explanation](explanation.md)
