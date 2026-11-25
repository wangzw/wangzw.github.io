#!/usr/bin/env python3
"""Check that every built page Cloudflare may rewrite to index.md has that file.

Exits 1 and names the pages that lack it, or when the directory holds no page at
all. Standard library only, Python 3.8 or later.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Keep both equal to the scope of the Cloudflare rewrite rule in CLAUDE.md ("Markdown for agents").
PREFIXES = ("/en/", "/zh/")
EXCLUDED = "/page/"


def in_scope(url_path: str) -> bool:
    """Whether the rewrite rule matches `url_path`, the URL path of a page (it ends with "/")."""
    return (url_path == "/" or url_path.startswith(PREFIXES)) and EXCLUDED not in url_path


def check(public: Path) -> tuple[int, list[str]]:
    """Return the number of pages in scope under `public` and the URL paths of those without an index.md."""
    pages = 0
    missing = []
    for html in sorted(public.rglob("index.html")):
        relative = html.parent.relative_to(public).as_posix()
        url_path = "/" if relative == "." else f"/{relative}/"
        if not in_scope(url_path):
            continue
        pages += 1
        if not (html.parent / "index.md").is_file():
            missing.append(url_path)
    return pages, missing


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").partition("\n")[0])
    parser.add_argument("public", nargs="?", default="public", help="the Hugo output directory (default: public)")
    args = parser.parse_args(argv)

    pages, missing = check(Path(args.public))
    if pages == 0:
        print(f"::error title=Markdown renditions::no page found in {args.public}; is it the Hugo output directory?")
        return 1
    for url_path in missing:
        print(
            f"::error title=Markdown renditions::{url_path} has no index.md; "
            "a request that accepts text/markdown would get a 404 there"
        )
    if missing:
        return 1
    print(f"Markdown renditions: all {pages} pages have an index.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
