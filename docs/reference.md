# Reference

Authoritative descriptions of the project's structure, file paths, data
shapes, and command-line interfaces. Look things up here; don't read
linearly. For task-oriented guidance see [How-to](how-to.md); for
conceptual background see [Explanation](explanation.md).

## Repository layout

| Path | Tracked? | Purpose |
|---|---|---|
| `README.md` | yes | Project orientation and docs index |
| `docs/` | yes | This documentation |
| `context/A_source_context.md` | yes | Source schema (descriptive) |
| `context/B_preference_context.md` | yes | User preferences (the primary user-edited file) |
| `context/C_process_guide.md` | yes | Curation procedure |
| `fetch_reddit.py` | yes | Reddit front-page fetcher |
| `extract_url.py` | yes | trafilatura probe |
| `.claude/skills/signal-finder/SKILL.md` | yes | Skill workflow |
| `.claude/skills/signal-finder/scripts/render_digest.py` | yes | HTML/MD renderer |
| `.claude/skills/signal-finder/references/output_schema.md` | yes | Digest JSON schema |
| `.claude/skills/signal-finder/references/rules.md` | yes | Hard rules (link integrity, citations, content respect) |
| `pyproject.toml`, `uv.lock` | yes | Project metadata |
| `posts/<date>-reddit.json` | no | Reddit posts cache |
| `posts/images/<date>/` | no | Reddit image downloads |
| `digests/<date>.json` | no | Curator output |
| `digests/<date>.html` | no | Single-day rendered HTML |
| `digests/all.html` | no | Combined rendered feed |
| `reflections/<date>.md` | no | Per-run reflection |

`posts/`, `digests/`, and `reflections/` are excluded by `.gitignore`.

## Hard filter rules

The `rule` field in `filtered_out[]` is the exact label you wrote in
`B_preference_context.md` §2 *I do not want* — there is no fixed
vocabulary. The renderer has built-in pill colors for these labels:

- `drama`
- `politics`
- `ragebait`
- `crypto`
- `repetitive`
- `meme`

Any other label gets a neutral gray pill.

## Reddit post schema

Each entry in `posts/<date>-reddit.json`.

| Field | Type | Notes |
|---|---|---|
| `source` | string | Always `"reddit"` |
| `title` | string | Reddit headline, ≤120 chars |
| `author` | string | `u/<username>` |
| `subreddit` | string | `r/<name>` |
| `date` | string | ISO 8601 from `created_utc` |
| `url` | string | Reddit thread permalink |
| `external_url` | string | URL the post points at; empty for self-posts |
| `post_type` | `"self"` \| `"link"` | |
| `text` | string | Selftext |
| `article_text` | string | trafilatura-extracted body, ≤1500 words |
| `article_title` | string | Extracted article title |
| `article_site` | string | Extracted hostname |
| `image_path` | string | Repo-relative path if a direct image was downloaded |
| `score` | int | Net upvotes |
| `num_comments` | int | |
| `tags` | array&lt;string&gt; | Link flair, if any |

Stickied admin posts and `over_18` posts are dropped at fetch time.

## Digest JSON schema

Each `digests/<date>.json`. Required vs optional reflects current C; the
schema supports more.

| Field | Required | Notes |
|---|---|---|
| `digest_items[]` | yes | Sorted by `relevance_score` desc |
| ↳ `rank` | yes | 1-indexed |
| ↳ `source` | yes | `"reddit"` |
| ↳ `title` | yes | Synthesized informative title |
| ↳ `original_title` | yes | Source's own headline, byte-faithful |
| ↳ `url` | yes | Post URL, copied byte-for-byte from input |
| ↳ `tags` | yes | Curator-chosen tags (array of strings) |
| ↳ `relevance_score` | yes | Float 0.0–1.0 |
| ↳ `reason_matched` | yes | 1–2 sentence justification citing B |
| `skip_worthy[]` | no | Optional; omit unless used |
| `wildcard` | no | Optional; off-track interesting pick |
| `filtered_out[]` | yes | Audit trail |
| ↳ `url`, `title`, `rule` | yes | `rule` is the exact label from B §2 that fired |
| `reflection.weakness_in_a` | yes | Specific gap in A revealed this run |
| `reflection.weakness_in_b` | yes | Specific gap in B revealed this run |
| `reflection.suggested_edit` | yes | One-line edit ready to paste into A or B |

The renderer is null-safe on optional fields — omit them rather than
including empty arrays.

## CLI: `fetch_reddit.py`

```
python3 fetch_reddit.py [--limit N] [--no-extract] [--no-download-images]
```

Requires `trafilatura` in the active Python env (`pip install -r
requirements.txt`). `uv run fetch_reddit.py` works as well — `uv` reads
the inline script metadata at the top of the file.

| Flag | Default | Notes |
|---|---|---|
| `--limit` | 50 | Posts to fetch from `/.json` |
| `--no-extract` | off | Skip trafilatura article extraction |
| `--no-download-images` | off | Skip image downloads |

No auth. Writes `posts/<UTC-date>-reddit.json` and (unless suppressed)
`posts/images/<UTC-date>/<basename>`.

### What gets extracted vs downloaded vs skipped

| External URL pattern | Article extraction | Image download |
|---|:---:|:---:|
| Article on a typical news/blog site | yes | no |
| `i.redd.it/*.jpg \| .jpeg \| .png \| .gif \| .webp` | no | yes |
| `v.redd.it/*` (Reddit-hosted video) | no | no |
| `youtube.com`, `youtu.be`, `twitter.com`, `x.com`, `tiktok.com` | no | no |
| Reddit gallery (`/gallery/...`) | no | no |
| Direct video (`.mp4`, `.webm`, `.mov`, `.m4v`) or PDF | no | no |
| Self-post | n/a | n/a |

Image downloads are capped at 8 MB. Articles are truncated to 1500 words.

## CLI: `extract_url.py`

```
python3 extract_url.py <url>
```

Prints the cleaned article text, plus title, author, date, hostname, and
word count to stdout. Used as a probe to verify a site extracts cleanly.

## CLI: `render_digest.py`

```
python3 .claude/skills/signal-finder/scripts/render_digest.py <path-to-digest-json>
```

Pure stdlib — works without the venv.

Always writes three files:

- `digests/<date>.html` — single-day view
- `digests/all.html` — combined feed of every JSON in `digests/`,
  sorted newest day first
- `reflections/<date>.md` — markdown reflection extracted from the JSON

The date is taken from the input filename's stem.

## /signal-finder skill workflow

Defined in `.claude/skills/signal-finder/SKILL.md`. When invoked:

1. Run `python3 fetch_reddit.py`.
2. Read `context/C_process_guide.md` and `context/B_preference_context.md`.
3. Read `posts/<date>-reddit.json`. For each post with a non-empty
   `image_path`, use the Read tool on that path before scoring.
4. Apply C's procedure using B's preferences. Write `digests/<date>.json`
   matching the schema.
5. Run `render_digest.py` against the new JSON.
6. Print the digest path.

## Hard rules (override anything in B)

From `context/A_source_context.md` §3 and
`.claude/skills/signal-finder/references/rules.md`:

- Public content only.
- Preserve the original `url` byte-for-byte. No paraphrasing, shortening,
  or tracker redirects.
- ≤30 words verbatim from any post.
- No author impersonation, no invented quotes.
- `reason_matched` must cite B specifically; generic praise is rejected.
- `weakness_in_a` and `weakness_in_b` must name a specific gap; vague
  reflections are rejected.
- `suggested_edit` is exactly one line of paste-ready text.

## Environment variables

None. Reddit's front page is public and requires no auth.
