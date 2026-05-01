# Output schema

Your final ranking pass produces ONE JSON object with this exact shape. Save it to `digests/<YYYY-MM-DD>.json` before invoking the renderer — keeping the JSON on disk makes the run debuggable and re-renderable without recomputing the curation.

```json
{
  "digest_items": [
    {
      "rank": 1,
      "source": "reddit",
      "title": "short synthesized title — informative, not sensational (per B's output style)",
      "original_title": "the source's own headline, copied verbatim from the input JSON",
      "url": "the post's original URL, copied exactly from the input",
      "tags": ["tag1", "tag2"],
      "relevance_score": 0.0,
      "reason_matched": "1–2 sentences citing B's wording, e.g. \"matches your 'practical tutorials' preference\""
    }
  ],
  "skip_worthy": [
    {
      "title": "short title",
      "url": "url",
      "reason_skipped": "why this was related but not ranked higher"
    }
  ],
  "wildcard": {
    "title": "...",
    "url": "...",
    "reason": "why this is the wildcard (off the user's usual track but worth seeing)"
  },
  "filtered_out": [
    {
      "url": "the dropped post's URL",
      "title": "the source's headline / first ~80 chars",
      "rule": "the exact label from B §2 that fired, e.g. \"politics\" or \"sports\""
    }
  ],
  "reflection": {
    "weakness_in_a": "specific concrete gap in A_source_context.md this run revealed",
    "weakness_in_b": "specific concrete gap in B_preference_context.md this run revealed",
    "suggested_edit": "one concrete one-line edit to A or B, ready to paste"
  }
}
```

## Counts

- `digest_items`: every post that survived B's hard filters, sorted by combined score (highest first). No upper bound.
- `skip_worthy`: optional; omit unless an item didn't survive scoring but is worth pointing at anyway.
- `wildcard`: optional; omit unless one specific item is worth calling out separately as off-track-but-interesting.
- `filtered_out`: every post dropped by a hard-filter rule, with the rule that dropped it. Audit trail — lets the user see what got removed and why.

## Why save the JSON

The renderer reads this JSON from disk, derives the date from the filename, and writes both `digests/<date>.html` and `reflections/<date>.md`. Saving the JSON gives the user a debuggable artifact and lets them re-render without re-curating if they want to tweak the renderer.
