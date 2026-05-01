# B — Preference Context

> **This is your preferences file. Fill it in.**
>
> Every section in this file is read by the curator on every run. Adding
> bullets to a list, reordering a priority, or rewriting the prose will
> visibly change tomorrow's digest. Bad curation is usually a context
> problem, not an AI problem — this is where you steer it.
>
> Sections (in the order the curator reads them):
> 1. **I want** — topics worth surfacing
> 2. **I do not want** — hard filter rules (drop on match, recorded in `filtered_out`)
> 3. **Inclusion bias** — how strict to be on borderline cases
> 4. **Ranking priorities** — tiebreakers for similar scores
> 5. **Output style** — how items get presented in the digest

---

## 1. I want

> *List the topics or kinds of posts you want surfaced. Add or remove
> bullets to shape what the curator ranks highly. These are positive
> signals — they raise scores, not gates. Be concrete: "Hands-on
> woodworking projects" beats "interesting stuff." Aim for 3–10 bullets.*

- (replace this line with a topic you want ranked highly)
- (add as many bullets as you like)

---

## 2. I do not want

> *Posts matching ANY of these rules are dropped at filter time and shown
> under "Filtered out" in the rendered digest with the rule that fired.
> Each bullet should be one short label (e.g. `politics`, `sports`,
> `drama`). Whatever label you write here is what the curator will record
> in `filtered_out[].rule`. The renderer applies a colored pill to
> matching rule names. Examples or notes can go beneath each label.*

- (replace this line with a single short rule label, e.g. `politics`)
- (add more bullets, or remove this section entirely if you want no hard filters)

---

## 3. Inclusion bias

> *Edit the prose. Tightening it makes the digest shorter and tidier;
> loosening it brings in more dross. The default below is "hard filters
> only" — the curator does not gatekeep beyond the rules in section 2.
> Replace the prose to switch to a stricter mode (e.g. "include only
> posts that match at least one bullet in §1").*

Hard filters are the only grounds for exclusion. If a post doesn't hit a rule under "I do not want", it goes in — period. No carve-outs for "off-topic," "low-information," "thin reply," or "off my central interests." I'll scroll past anything I don't want to read. The curator's job ends at the hard filter line; any item that survives gets a rank and a reason, however low.

---

## 4. Ranking priorities (highest first)

> *List your tiebreakers. When two posts score similarly, the order below
> decides. Edit and reorder freely.*

1. (your top tiebreaker — e.g. "Hands-on > theoretical")
2. (next tiebreaker)
3. (and so on)

---

## 5. Output style

> *Edit the bullets. Shapes title style, summary length, and presentation
> in the rendered digest. The defaults below are reasonable starting
> points; rewrite to taste.*

- Short summaries (1–2 sentences)
- Always include the original link
- Explain why each item was selected, in plain language referencing §1
- Titles should be informative, not sensational. Describe what the post or article is actually about. Avoid hype words, dramatic framing, and click-bait phrasing. If the source headline leans sensational, write a calmer replacement.
