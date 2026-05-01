# A — Source Context

> **This file documents the data the curator reads.** Most users won't
> edit it — the schema below tracks what `fetch_reddit.py` produces, and
> changing it here without changing the fetcher just confuses the
> curator. Touch this file when you:
> - **Add a new source** (a new fetcher → a new schema section here)
> - **Change the fetcher's output shape** (keep this in sync)
> - **Tighten the curation rules at the bottom**
>
> For day-to-day preference changes (what gets ranked highly, what gets
> filtered out), edit B instead.
>
> Sections:
> 1. **Source** — endpoint and field schema (descriptive)
> 2. **How to read these fields during curation** (descriptive)
> 3. **Rules the curator must follow** (editable — these are hard rules
>    that override anything in B)

The pipeline pulls posts from Reddit's front page. Each post in
`posts/<date>-reddit.json` carries the schema below.

---

## 1. Source

### Reddit

**Endpoint:** `https://www.reddit.com/.json` (the logged-out front page — what r/popular shows). No auth; uses a custom User-Agent.

**Fields per post:**

- `source` — always `"reddit"`
- `title` — Reddit headline, truncated to 120 chars
- `author` — `u/<username>`
- `subreddit` — `r/<name>`
- `date` — ISO 8601 from `created_utc`
- `url` — Reddit thread permalink (`https://www.reddit.com/r/.../comments/...`)
- `external_url` — for link posts, the URL the post points at (article, video, image). Empty string for self-posts.
- `post_type` — `"self"` or `"link"`
- `text` — selftext (full body for self-posts; caption-only or empty for link posts)
- `article_text`, `article_title`, `article_site` — set when `external_url` is an article and trafilatura extracted it. Empty for media-only links, paywalls, JS-only sites.
- `image_path` — repo-relative path to a downloaded image (e.g. `posts/images/2026-04-29/r136w0x49wxg1.jpeg`) when `external_url` is a direct `.jpg/.jpeg/.png/.gif/.webp`. Empty for videos, galleries, articles, self-posts.
- `score` — net upvotes
- `num_comments` — comment count
- `tags` — `[link_flair_text]` if present; user-applied flair, NOT a hard category

**Filtering at fetch time:** stickied admin posts and `over_18` posts are dropped before the JSON is written.

---

## 2. How to read these fields during curation

- **`title` is the headline. `text` / `article_text` / `image_path` is the content.** For Reddit link posts, the Reddit headline is often clickbait or vague; the linked article (`article_text`) or downloaded image is what should drive scoring.
- **When `image_path` is non-empty, use the Read tool to see the image.** Reddit headlines like *"This is what making a difference looks like"* are uninformative; the image often reveals a specific, scoreable subject. Read the image, then synthesize a calmer, descriptive title from what you actually see.
- **When `article_text` is non-empty, score on the article body, not the Reddit headline** — the headline is usually framed for clicks, the article body for accuracy.
- **Empty `article_text` AND empty `image_path` on a link post** = the link points at a video, gallery, or unfetchable site. The Reddit headline is all you have; rank accordingly (often low).

---

## 3. Rules the curator must follow

> *Edit this list. These are hard rules that override anything in B —
> they exist for safety, attribution, and ToS reasons.*

- Public content only — drop anything marked private or blocked at fetch time.
- Always preserve the original `url` byte-for-byte. Never paraphrase, shorten, or redirect through a tracker.
- Don't reproduce more than ~30 words of any post verbatim. Summarize.
- Don't impersonate the author or invent quotes.
- Respect Reddit's terms of service.
