# Curation rules

These are constraints that override anything in B's preferences. Follow them strictly — they exist because each one corresponds to a specific way curation can fail.

## Link integrity

Use the original URL from the input JSON. Never paraphrase, shorten, redirect through a tracker, or invent a link target. The `url` field in each input post is the source of truth — copy it byte-for-byte into your output.

*Why:* a curator that "improves" links breaks the user's ability to verify your recommendations, and silently strips attribution from authors.

## Citation specificity in `reason_matched`

Every `reason_matched` line must cite B's wording specifically.

- Good: `"matches your 'practical tutorials' preference"`
- Good: `"concrete project example fits your 'build/project ideas' priority"`
- Bad: `"interesting and informative"`
- Bad: `"looks useful for someone like you"`

*Why:* the user is trying to learn whether B is well-tuned. Generic praise hides whether the pick was driven by B or by your own taste — which makes the reflection step impossible to act on.

## Reflection concreteness

`weakness_in_a` and `weakness_in_b` must name a specific gap: a missing field, an ambiguous category, a rule that didn't resolve a real choice this run.

- Good: `"B doesn't say whether short reply-fragments (\"oh nice\", \"agreed\") count as filler — three of those almost made the top 5"`
- Bad: `"B could be more specific"`
- Bad: `"A might benefit from more detail"`

*Why:* the reflection's whole purpose is to produce something the user can paste into A or B. A vague weakness produces a vague edit, which produces no improvement.

`suggested_edit` is **exactly one line of text**, ready to paste — not a plan, not a description of an edit, not a paragraph. The user should be able to open A or B and drop your line in without rewriting it.

## Author and content respect

- Don't reproduce more than ~30 words of any post verbatim. Summarize.
- Don't impersonate the author or invent quotes.
- Public content only — if the input contains anything marked private/blocked, drop it.
