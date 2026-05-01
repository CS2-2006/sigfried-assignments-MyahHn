#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "trafilatura>=1.12",
# ]
# ///
"""
Probe: fetch a URL and extract its main content with trafilatura.

Usage:
    python3 extract_url.py <url>     # requires trafilatura in the active env
    uv run extract_url.py <url>      # alternative; uv reads inline metadata

Prints a short header (title, author, word count) followed by the cleaned text.
Used to test how well content extraction works on real Reddit link targets
before we wire it into the digest pipeline.
"""

from __future__ import annotations

import sys

import trafilatura


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: extract_url.py <url>", file=sys.stderr)
        return 2

    url = sys.argv[1]
    print(f"# Fetching: {url}", file=sys.stderr)
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        print("ERROR: fetch failed (network, paywall, or 4xx/5xx)", file=sys.stderr)
        return 1

    extracted = trafilatura.extract(
        downloaded,
        output_format="json",
        include_comments=False,
        include_tables=False,
        with_metadata=True,
        favor_precision=True,
    )
    if not extracted:
        print("ERROR: extraction returned nothing (page may be JS-only or empty)", file=sys.stderr)
        return 1

    import json as _json

    data = _json.loads(extracted)
    text = data.get("text", "") or ""
    print(f"# title:   {data.get('title') or '(none)'}")
    print(f"# author:  {data.get('author') or '(none)'}")
    print(f"# date:    {data.get('date') or '(none)'}")
    print(f"# site:    {data.get('hostname') or '(none)'}")
    print(f"# words:   {len(text.split())}")
    print()
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
