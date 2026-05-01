#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "trafilatura>=1.12",
# ]
# ///
"""
Fetch Reddit's front page and write to posts/<YYYY-MM-DD>-reddit.json.

For link posts that point to articles (not Reddit-hosted media, not video sites),
this script also fetches the linked page and extracts the main body using
trafilatura. The cleaned article text is stored in `article_text`; selftext
stays in `text`.

Image link posts (i.redd.it/*.jpg, etc.) are downloaded to
posts/images/<date>/<basename> when --download-images (default) is on, and the
local relative path is stored in `image_path`. This lets the curator inspect
the image via the Read tool during /signal-finder, which is what produces
informative titles for posts whose Reddit headline is uninformative.

Usage:
    python3 fetch_reddit.py [--limit N] [--no-extract] [--no-download-images]

Requires `trafilatura` in the active Python env (pip install -r
requirements.txt). `uv run fetch_reddit.py` also works — uv reads the
inline `# /// script` metadata block above.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import trafilatura

ROOT = Path(__file__).parent
POSTS_DIR = ROOT / "posts"
IMAGES_DIR = POSTS_DIR / "images"
USER_AGENT = "MPA-2026-signal-finder/0.1 (educational use; contact via repo)"

# Hosts where article extraction won't yield useful text (media, JS-only walls).
SKIP_EXTRACT_HOSTS = {
    "v.redd.it",
    "i.redd.it",
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "youtu.be",
    "twitter.com",
    "x.com",
    "www.x.com",
    "www.twitter.com",
    "tiktok.com",
    "www.tiktok.com",
}

# File extensions that aren't articles.
SKIP_EXTRACT_EXTS = (
    ".jpg", ".jpeg", ".png", ".gif", ".webp",
    ".mp4", ".webm", ".mov", ".m4v",
    ".pdf",
)

# Image extensions worth downloading for vision-aware titles.
IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".gif", ".webp")

# Hosts where we will *not* download even if the URL looks image-like.
SKIP_IMAGE_HOSTS = {"v.redd.it"}

MAX_ARTICLE_WORDS = 1500
MAX_IMAGE_BYTES = 8 * 1024 * 1024  # 8 MB


def should_extract(url: str) -> bool:
    if not url:
        return False
    try:
        parsed = urllib.parse.urlparse(url)
    except ValueError:
        return False
    host = (parsed.hostname or "").lower()
    if host in SKIP_EXTRACT_HOSTS:
        return False
    path = (parsed.path or "").lower()
    if path.endswith(SKIP_EXTRACT_EXTS):
        return False
    if host.endswith("reddit.com") and "/gallery/" in path:
        return False
    return True


def should_download_image(url: str) -> bool:
    if not url:
        return False
    try:
        parsed = urllib.parse.urlparse(url)
    except ValueError:
        return False
    host = (parsed.hostname or "").lower()
    if host in SKIP_IMAGE_HOSTS:
        return False
    path = (parsed.path or "").lower()
    return path.endswith(IMAGE_EXTS)


def extract_article(url: str) -> dict:
    """Return {'article_text','article_title','article_site'}; empty strings on failure."""
    blank = {"article_text": "", "article_title": "", "article_site": ""}
    try:
        downloaded = trafilatura.fetch_url(url)
    except Exception as e:
        print(f"  fetch error: {e}", file=sys.stderr)
        return blank
    if not downloaded:
        return blank
    try:
        out = trafilatura.extract(
            downloaded,
            output_format="json",
            include_comments=False,
            include_tables=False,
            with_metadata=True,
            favor_precision=True,
        )
    except Exception as e:
        print(f"  extract error: {e}", file=sys.stderr)
        return blank
    if not out:
        return blank
    data = json.loads(out)
    text = (data.get("text") or "").strip()
    words = text.split()
    if len(words) > MAX_ARTICLE_WORDS:
        text = " ".join(words[:MAX_ARTICLE_WORDS]) + " …"
    return {
        "article_text": text,
        "article_title": (data.get("title") or "").strip(),
        "article_site": (data.get("hostname") or "").strip(),
    }


def download_image(url: str, dest_dir: Path) -> str:
    """Download image to dest_dir/<basename>; return repo-relative path or ''."""
    try:
        parsed = urllib.parse.urlparse(url)
    except ValueError:
        return ""
    name = Path(parsed.path).name
    if not name:
        return ""
    dest_dir.mkdir(parents=True, exist_ok=True)
    out = dest_dir / name
    if out.exists() and out.stat().st_size > 0:
        return str(out.relative_to(ROOT))
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            length = resp.headers.get("Content-Length")
            if length and int(length) > MAX_IMAGE_BYTES:
                print(f"  skip oversize image ({length} bytes): {url}", file=sys.stderr)
                return ""
            data = resp.read(MAX_IMAGE_BYTES + 1)
        if len(data) > MAX_IMAGE_BYTES:
            print(f"  skip oversize image: {url}", file=sys.stderr)
            return ""
        out.write_bytes(data)
        return str(out.relative_to(ROOT))
    except Exception as e:
        print(f"  image download error: {e}", file=sys.stderr)
        return ""


def fetch_front_page(limit: int, do_extract: bool, do_download_images: bool, today_iso: str) -> list[dict]:
    url = f"https://www.reddit.com/.json?limit={limit}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=15) as resp:
        payload = json.loads(resp.read().decode("utf-8"))

    image_dir = IMAGES_DIR / today_iso

    posts: list[dict] = []
    for child in payload.get("data", {}).get("children", []):
        d = child.get("data", {})
        if d.get("stickied") or d.get("over_18"):
            continue
        permalink = d.get("permalink", "")
        thread_url = f"https://www.reddit.com{permalink}" if permalink else ""
        external_url = d.get("url_overridden_by_dest") or d.get("url") or ""
        is_self = bool(d.get("is_self"))
        if is_self:
            external_url = ""
        created_iso = (
            datetime.fromtimestamp(d["created_utc"], tz=timezone.utc).isoformat()
            if d.get("created_utc")
            else ""
        )
        title = d.get("title", "") or "(no title)"

        article = {"article_text": "", "article_title": "", "article_site": ""}
        if do_extract and external_url and should_extract(external_url):
            print(f"  extracting: {external_url}", file=sys.stderr)
            article = extract_article(external_url)

        image_path = ""
        if do_download_images and external_url and should_download_image(external_url):
            print(f"  image:      {external_url}", file=sys.stderr)
            image_path = download_image(external_url, image_dir)

        posts.append(
            {
                "source": "reddit",
                "title": title[:120].strip(),
                "author": f"u/{d.get('author', '')}",
                "subreddit": f"r/{d.get('subreddit', '')}",
                "date": created_iso,
                "url": thread_url,
                "external_url": external_url,
                "post_type": "self" if is_self else "link",
                "text": d.get("selftext", "") or "",
                "article_text": article["article_text"],
                "article_title": article["article_title"],
                "article_site": article["article_site"],
                "image_path": image_path,
                "score": d.get("score", 0) or 0,
                "num_comments": d.get("num_comments", 0) or 0,
                "tags": [d.get("link_flair_text")] if d.get("link_flair_text") else [],
            }
        )
    return posts


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch Reddit front page -> posts/<date>-reddit.json"
    )
    parser.add_argument("--limit", type=int, default=50, help="posts to fetch (default 50)")
    parser.add_argument(
        "--no-extract",
        action="store_true",
        help="skip article extraction for link posts",
    )
    parser.add_argument(
        "--no-download-images",
        action="store_true",
        help="skip downloading images for image posts",
    )
    args = parser.parse_args()

    POSTS_DIR.mkdir(exist_ok=True)
    today = datetime.now(timezone.utc).date().isoformat()
    out = POSTS_DIR / f"{today}-reddit.json"

    print(f"Fetching {args.limit} posts from reddit.com front page...", file=sys.stderr)
    try:
        posts = fetch_front_page(
            args.limit,
            do_extract=not args.no_extract,
            do_download_images=not args.no_download_images,
            today_iso=today,
        )
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.reason}", file=sys.stderr)
        return 1
    except urllib.error.URLError as e:
        print(f"network error: {e.reason}", file=sys.stderr)
        return 1

    out.write_text(json.dumps(posts, indent=2, default=str))
    extracted = sum(1 for p in posts if p["article_text"])
    imaged = sum(1 for p in posts if p["image_path"])
    print(
        f"Wrote {len(posts)} posts ({extracted} articles, {imaged} images) to {out}",
        file=sys.stderr,
    )
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
