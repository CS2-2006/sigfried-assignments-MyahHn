# C — Curation Process

> **This file describes *how* curation runs.** The numbered steps are the
> mechanical procedure the curator follows; the "Tunable knobs" section
> below has the parameters most likely to be worth changing. If you want
> to change *what* the curator selects, edit B instead — that's where your
> preferences live.
>
> Sections:
> - **Steps** — the 10-step procedure, run in order
> - **Tunable knobs** — parameters and behaviors you might want to adjust

---

## Steps

1. Load every candidate post from the user message (these are A's output). For posts with a non-empty `image_path`, use the Read tool on that path before scoring — the image often reveals what the headline obscured.
2. Remove any post that violates a hard filter from B's "I do not want" list. For each removed post, append an entry to `filtered_out` with the post's url, title, and the rule label that fired (use the exact label as written in B §2).
3. Score each remaining post for **relevance to B** on a 0.0 – 1.0 scale.
4. Score each remaining post for **quality** (concreteness, specificity, usefulness) on a 0.0 – 1.0 scale. Combined score = `relevance * 0.7 + quality * 0.3`.
5. Deduplicate near-identical posts; keep the higher-scored one.
6. Include every post that survived hard filters in `digest_items`, sorted by combined score (highest first). No cap.
7. For each pick, write a short (1–2 sentence) `reason_matched` referencing **B specifically** — quote or paraphrase the wording of the §1 bullet that drove the score. Lower-ranked items should be honest about why they sit lower.
8. Produce one JSON object matching the schema in the system prompt. **Do not** wrap it in markdown fences. Output only the JSON, nothing else.
9. Identify the most concrete weakness in A and the most concrete weakness in B that this run revealed. Be specific — name a missing field, an ambiguous preference, a category gap.
10. Suggest exactly **ONE** one-line edit to A or B that would most improve tomorrow's digest. Put it in `reflection.suggested_edit`.

---

## Tunable knobs

> *These are the parameters most likely to be worth adjusting. Each one
> changes a specific behavior described above.*

- **Score weights** (step 4): currently `relevance * 0.7 + quality * 0.3`. Raise the relevance weight to lean harder on B's "I want" list; raise the quality weight to favor concrete/specific posts even when off-topic.
- **Output cap** (step 6): currently uncapped — every survivor lands in the digest. Replace "No cap" with "top N by combined score" if you want a tighter list.
- **`skip_worthy` and `wildcard`**: optional in this mode; omit them unless a specific item genuinely warrants being called out separately.
- **Reflection focus** (steps 9–10): currently "one weakness in A + one weakness in B + one suggested edit." If you want the reflection to focus on something else (e.g. cost, source coverage, dedup quality), rewrite steps 9–10.
