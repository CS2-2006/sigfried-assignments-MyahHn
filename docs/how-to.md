# How-to guides

Self-contained recipes for common adjustments. Each section below assumes
you've already done the [Tutorial](tutorial.md). They don't teach concepts
— for that, see [Explanation](explanation.md).

## Change what topics get ranked highly

Edit `context/B_preference_context.md` §1 *I want*. Add or remove bullets.
Save and re-run `/signal-finder`.

## Drop a category from every future digest

Edit `context/B_preference_context.md` §2 *I do not want*. Add a one-word
label (e.g. `Sports`, `Sponsored`, `Crypto`). The curator will move
matching posts to `filtered_out` instead of ranking them, recording your
exact label in the `rule` field. The label appears as a colored pill
next to each filtered item in the rendered digest.

The renderer has built-in pill colors for `drama`, `politics`,
`ragebait`, `crypto`, `repetitive`, and `meme`. Any other label gets a
neutral gray pill — perfectly readable, just not color-themed.

## Loosen or tighten the inclusion bias

Edit `context/B_preference_context.md` §3 *Inclusion bias*. The default
prose says "hard filters only — no other gatekeeping." To tighten,
replace it with something stricter, e.g. *"Include only posts with at
least one match in §1 or a relevance score ≥ 0.3."*

You can't really loosen it further — hard filters only is the floor.

## Cap the digest at top N items

Edit `context/C_process_guide.md`, step 6. Replace `No cap` with `Top N
by combined score`. The renderer needs no change; it just gets fewer
items to render.

## Reweight relevance vs quality in scoring

Edit `context/C_process_guide.md`, step 4. The default formula is
`relevance * 0.7 + quality * 0.3`. Adjust the weights:

- **Higher relevance weight** — pulls toward your *I want* list; rewards
  on-topic content even when generic.
- **Higher quality weight** — rewards specific, concrete, well-sourced
  posts even when off-topic.

## Audit what got filtered

In any rendered digest, scroll to the bottom and click **Filtered out**.
Each entry shows the dropped post's URL, title, and which rule dropped
it. Use this to:

- Confirm a new rule is firing as expected.
- Catch borderline calls the curator made.
- Spot patterns you'd like to stop filtering.

> All `python3` commands below assume you have the venv activated
> (`source .venv/bin/activate`). If you use `uv` instead, swap `python3`
> for `uv run`.

## Bump or shrink the Reddit fetch

```sh
python3 fetch_reddit.py --limit 25     # smaller pull
python3 fetch_reddit.py --limit 100    # max
```

Default is 50.

## Skip image downloads (faster fetch, cron-friendly)

```sh
python3 fetch_reddit.py --no-download-images
```

The curator will still see article extractions for link posts; image-only
posts will lack vision-aware titles. Useful when running unattended where
the harness can't view images anyway.

## Skip article extraction

```sh
python3 fetch_reddit.py --no-extract
```

Faster fetch; the curator only sees Reddit headlines and selftexts, not
the linked articles.

## Re-render a saved digest without re-curating

```sh
python3 .claude/skills/signal-finder/scripts/render_digest.py digests/2026-04-29.json
```

Rewrites `digests/2026-04-29.html` and `digests/all.html` from the
existing JSON. The renderer is pure stdlib — works without the venv.

## Test the article extractor on one URL

```sh
python3 extract_url.py https://example.com/article
```

Prints the extracted title, author, date, hostname, word count, and the
cleaned text. Lets you see whether a site extracts cleanly before
relying on it.

## Edit a single digest item by hand

Open `digests/<date>.json`, edit the item, and re-render:

```sh
python3 .claude/skills/signal-finder/scripts/render_digest.py digests/<date>.json
```

The renderer is purely formatting; nothing in the JSON is recomputed.

## Pivot the curator to a different persona for a session

Edit the lists in `context/B_preference_context.md` (§1 *I want*, §4
*Ranking priorities*). Re-run `/signal-finder`. The same posts will
re-rank under the new lens. Revert by editing back, or version-control B
and check out a different branch.

## Add a new source

1. Write `fetch_<source>.py` mirroring `fetch_reddit.py`. Output
   `posts/<date>-<source>.json`. At minimum each post must have `source`,
   `title`, `url`, and `text`.
2. Add a section to `context/A_source_context.md` documenting the new
   source's fields and any quirks.
3. The renderer auto-handles any `source` value; add a
   `.source-<name>` rule to `render_digest.py` if you want a custom
   badge color.
4. Update `.claude/skills/signal-finder/SKILL.md` step 1 to also run
   the new fetcher, and step 3 to read the new posts JSON.

## Restore the wildcard / skip-worthy sections

The current process puts every survivor in `digest_items`. To bring
back the segmented format:

1. Edit `context/C_process_guide.md` step 6: cap `digest_items` at top N
   and document `wildcard` and `skip_worthy` as required.
2. Update `references/output_schema.md` to make the two fields required
   instead of optional.

The renderer already supports both fields when present.
