# Explanation

Concept-oriented background and design discussion. Read this when you
want to understand *why* the project is shaped the way it is. For
step-by-step instructions see [Tutorial](tutorial.md) and
[How-to](how-to.md); for field-by-field details see
[Reference](reference.md).

## The A/B/C framework

The project separates context into three files because each answers a
different question:

- **A — Source context.** *What does the data look like?* Descriptive:
  fetcher output schema, field meanings, source quirks. Edited only when
  the data shape changes (a new fetcher, a new field).
- **B — Preference context.** *What do I, the user, want?* Preferential:
  topics that should rank highly, hard filters that drop content,
  ranking priorities, output style. The primary user file. Edit often.
- **C — Process guide.** *How should the curator work?* Procedural: load
  posts, filter, score, dedup, output JSON, reflect. Edit when changing
  the curation procedure itself, not your tastes.

The split exists so that changes are localized:

- Add a Reddit field → A moves.
- Decide to filter sports → B moves.
- Reweight scoring → C moves.

Conflating the three — putting "filter sports" in C, or "score on
relevance only" in B — makes future tuning ambiguous and the curator's
behavior harder to reason about.

## The curator runs in conversation, not in a script

There is no Python script that scores posts. The fetcher produces raw
JSON. The renderer produces HTML from a curated JSON. The *curation step
in between* is performed by Claude in the `/signal-finder` interactive
session: A, B, and C are loaded into Claude's context as instructions;
the posts JSON is loaded as data; Claude writes the digest JSON to disk.

This is a deliberate architectural choice. It lets you change the
curator's behavior by editing prose, not code. It means the same setup
adapts to any new source whose fetcher writes JSON in a recognizable
shape. And it makes the project legible to students: there is no hidden
ML model deciding things — every decision is governed by markdown.

The pedagogical point: editing B will visibly change tomorrow's digest;
the AI itself does not change between today and tomorrow. **Bad
curation is usually a context problem, not an AI problem.**

## Why "hard filters only"

B has both an *I want* list (positive signal — raises the score) and an
*I do not want* list (hard filter — drops the post outright). The
*Inclusion bias* section governs the gap between them.

The default setting is *hard filters only*: anything that doesn't hit a
"do not want" rule survives, gets a relevance score, and lands in the
digest. Off-topic content sinks to the tail; the user scrolls past it.

The alternative — "include only things that match my interests" — has a
common failure mode: the curator over-gatekeeps. Every borderline call
leans toward exclusion, and the digest shrinks to a narrow list that
feels safer than it is informative. Letting low-relevance posts
through forces the curator to score honestly rather than hide its
uncertainty by dropping items.

The user owns the decision to scroll. The curator owns ranking.

## Why `filtered_out` exists

Earlier versions of the digest dropped filtered posts silently. After a
B edit you'd re-run with no way to see what changed; the only signal was
the digest's contents. With `filtered_out` populated, you can audit:

- Did my new "Sports" rule actually fire? *(look for entries with
  `rule: "sports"`)*
- Is "drama" over-firing on borderline cases? *(count entries with
  `rule: "drama"`)*
- Is the curator unsure what to do with edge cases? *(filtered count vs.
  digest_items count tells the story)*

Without the audit trail, the curator's filter decisions live only in the
session and evaporate at the end of the run. With it, they're durable on
disk and inspectable in the rendered HTML's *Filtered out* dropdown.

The rule labels are not a fixed vocabulary — whatever you write in B §2
becomes a valid rule, and the renderer just shows it as a pill. This
keeps the "what to filter" question in B where it belongs, instead of
forcing you to extend an enum elsewhere.

## Vision via the harness, not the API

When a Reddit post points to a direct image, the fetcher downloads it to
`posts/images/<date>/`. During curation, Claude uses its built-in `Read`
tool to view the image — exactly the same way it reads any local file
you hand it. No Anthropic API call, no API key, no per-image cost.

This works because Claude is a multimodal model running in the Claude
Code session. The harness is the runtime; the image just becomes part of
the conversation.

Outside that session — say, in an unattended cron job — the same trick
doesn't apply; you'd need an API key and a vision call. The current
project leans on the harness because the daily entry point is
interactive (a student or instructor typing `/signal-finder`). For
unattended use, you'd add an `ANTHROPIC_API_KEY` and call the API
directly from a script.

## The fetcher fetches raw; the curator decides

The fetcher doesn't apply B's preferences. Stickied admin posts and NSFW
posts get dropped at fetch time, but otherwise everything found goes
into the posts JSON. The "do you actually want this?" question is the
curator's job at curation time.

Two reasons:

1. Filtering at fetch time would couple the fetcher to B; you'd have to
   re-fetch every time B changed.
2. Keeping raw posts on disk means you can re-curate the same data with
   different B settings and compare. The "developer persona vs. gardener
   persona" exercise relies on this — same posts, two B files, two very
   different rankings.

## The digest is a flat ranked list, not a feed

There's no fixed "Top 5 / Skip-worthy / Wildcard" segmentation in the
default output. Every post that survives hard filters lives in
`digest_items`, sorted by score. The renderer presents this as one
continuous list with a small *Filtered out* dropdown at the bottom.

This shape was chosen for a doom-scroll feel: a single column, no obvious
break, the highest-scored content at the top, dross at the tail. The
schema still supports `wildcard` and `skip_worthy` if you want to bring
back segmentation — see [How-to: restore the wildcard / skip-worthy
sections](how-to.md#restore-the-wildcard--skip-worthy-sections).

## Why the renderer is a Python script and not me

The HTML scaffolding (CSS, the day-section structure, the tag pills, the
collapsed dropdowns) is identical every run. Asking Claude to regenerate
it daily would burn tokens for zero pedagogical value and risk
inconsistency between runs. Bundling it as a single Python script lets
the cognitive work (filter, score, rank, reflect) stay in Claude's
hands, and the deterministic work (HTML formatting) stays in code.

The split — *cognitive work in conversation, deterministic work in
scripts* — is a load-bearing pattern in this kind of context-engineered
system. When the renderer changes, edit one file. When your taste
changes, edit a different file.

## Why a one-line `suggested_edit` in the reflection

The reflection step exists so the system improves itself. After every
run, Claude names a specific weakness in A or B that this particular
batch of posts revealed, and writes a single-line edit you could paste
in to fix it.

Single-line is intentional. A multi-line edit is a plan, not an
edit — it requires interpretation. A one-line edit is something you can
paste in without rewriting. The constraint forces specificity. If
Claude can't compress the suggestion to one line, the suggestion isn't
sharp enough.
