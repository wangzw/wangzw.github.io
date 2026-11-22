#!/usr/bin/env python3
"""Tell search engines which pages changed in a deploy, through IndexNow.

IndexNow (https://www.indexnow.org/documentation) is meant for URLs that were
added, updated or deleted, not for the whole site on every deploy. Two steps:

  diff    compare the sitemaps that are live now with the freshly built ones and
          print the URLs that are new or whose <lastmod> changed
  submit  send a list of URLs to the IndexNow endpoint (--dry-run only prints it)

Neither step ever exits non-zero because of a network or data problem: a failure
is printed as a GitHub Actions `::warning::` annotation and the deploy goes on.
The key is public by design: it is the stem of the single static/<key>.txt file
whose content is the key itself, and the site serves that file at its root.

Standard library only, Python 3.8 or later.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ENDPOINT = "https://api.indexnow.org/indexnow"
MAX_URLS_PER_REQUEST = 10000  # limit of one POST, per the documentation
SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
KEY_PATTERN = re.compile(r"[A-Za-z0-9-]{8,128}")  # allowed key characters and length
USER_AGENT = "indexnow-script"
FETCH_ATTEMPTS = 3  # tries for one live sitemap before giving up
RETRY_DELAY = 5  # seconds between those tries


class Reporter:
    """Writes progress lines; annotations go where the GitHub runner reads them."""

    def __init__(self, stream):
        self.stream = stream

    def info(self, message: str) -> None:
        print(message, file=self.stream, flush=True)

    def warning(self, message: str) -> None:
        print(f"::warning title=IndexNow::{message}", file=self.stream, flush=True)


def read_source(source: str) -> bytes:
    """Read a sitemap from a file path or an http(s) URL.

    A URL is tried FETCH_ATTEMPTS times. Giving up after one failed fetch would
    lose the URLs of this deploy for good: once deployed they are in the live
    sitemap, so the diff of a later deploy no longer reports them.
    """
    if not source.startswith(("http://", "https://")):
        return Path(source).read_bytes()
    request = urllib.request.Request(source, headers={"User-Agent": USER_AGENT})
    for attempt in range(1, FETCH_ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.read()
        except OSError:  # urllib.error.URLError and timeouts are OSError
            if attempt == FETCH_ATTEMPTS:
                raise
            time.sleep(RETRY_DELAY)
    raise AssertionError("unreachable")


def parse_sitemap(data: bytes) -> dict[str, str | None]:
    """Return {loc: lastmod} for a <urlset> sitemap (lastmod is None when absent)."""
    root = ET.fromstring(data)
    if root.tag != f"{SITEMAP_NS}urlset":
        raise ValueError(f"expected a <urlset> sitemap, found <{root.tag}>")
    entries: dict[str, str | None] = {}
    for url in root.findall(f"{SITEMAP_NS}url"):
        loc = (url.findtext(f"{SITEMAP_NS}loc") or "").strip()
        if loc:
            entries[loc] = (url.findtext(f"{SITEMAP_NS}lastmod") or "").strip() or None
    return entries


def normalize_lastmod(value: str | None) -> str | None:
    """Make two spellings of the same instant compare equal."""
    if value is None:
        return None
    try:
        moment = datetime.fromisoformat(value)
    except ValueError:
        return value
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(timezone.utc).isoformat()


def changed_urls(old: dict[str, str | None], new: dict[str, str | None]) -> list[str]:
    """URLs of `new` that are absent from `old` or carry a different lastmod."""
    return [
        url
        for url, lastmod in new.items()
        if url not in old or normalize_lastmod(old[url]) != normalize_lastmod(lastmod)
    ]


def load_all(sources: list[str]) -> dict[str, str | None]:
    entries: dict[str, str | None] = {}
    for source in sources:
        entries.update(parse_sitemap(read_source(source)))
    return entries


def run_diff(args: argparse.Namespace) -> int:
    out = open(args.output, "w", encoding="utf-8") if args.output else sys.stdout
    report = Reporter(sys.stdout if args.output else sys.stderr)
    try:
        try:
            old = load_all(args.old)
            new = load_all(args.new)
        except Exception as error:  # network, file or XML problem: skip, never fail
            report.warning(f"could not compare the sitemaps ({error}); nothing will be submitted for this deploy")
            return 0
        urls = changed_urls(old, new)
        report.info(f"IndexNow: {len(new)} URLs in the new sitemaps, {len(old)} in the live ones, {len(urls)} new or changed")
        for url in urls:
            print(url, file=out)
    finally:
        if args.output:
            out.close()
    return 0


def find_key(static_dir: Path) -> str:
    """The key is the stem of the one file in static_dir whose content is that stem."""
    keys = []
    for path in sorted(static_dir.glob("*.txt")):
        if KEY_PATTERN.fullmatch(path.stem) and path.read_text(encoding="utf-8").strip() == path.stem:
            keys.append(path.stem)
    if len(keys) != 1:
        raise ValueError(f"expected exactly one IndexNow key file in {static_dir}, found {len(keys)}")
    return keys[0]


def post_json(endpoint: str, payload: dict) -> tuple[int, str]:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json; charset=utf-8", "User-Agent": USER_AGENT},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8", "replace")


def run_submit(args: argparse.Namespace) -> int:
    report = Reporter(sys.stdout)
    try:
        text = Path(args.urls_file).read_text(encoding="utf-8") if args.urls_file else sys.stdin.read()
        urls = list(dict.fromkeys(line.strip() for line in text.splitlines() if line.strip()))
        if not urls:
            report.info("IndexNow: no new or changed URLs, nothing to submit")
            return 0
        host = args.host or urllib.parse.urlsplit(urls[0]).netloc
        foreign = [url for url in urls if urllib.parse.urlsplit(url).netloc != host]
        if foreign:
            report.warning(f"skipping {len(foreign)} URLs that do not belong to {host}, first: {foreign[0]}")
            urls = [url for url in urls if url not in foreign]
        key = find_key(Path(args.static_dir))
        failed = False
        for start in range(0, len(urls), MAX_URLS_PER_REQUEST):
            payload = {"host": host, "key": key, "urlList": urls[start:start + MAX_URLS_PER_REQUEST]}
            if args.dry_run:
                report.info(f"IndexNow dry run: would POST to {args.endpoint}")
                report.info(json.dumps(payload, indent=2, ensure_ascii=False))
                continue
            status, body = post_json(args.endpoint, payload)
            report.info(f"IndexNow: HTTP {status} for {len(payload['urlList'])} URLs, response: {body or '(empty)'}")
            if status not in (200, 202):  # 200 received, 202 received and key validation pending
                failed = True
                report.warning(f"submission was not accepted: HTTP {status} {body or '(empty response)'}")
        if not failed and not args.dry_run:
            report.info(f"IndexNow: submitted {len(urls)} URLs for {host}")
    except Exception as error:  # network or key file problem: report, never fail the deploy
        report.warning(f"submission failed: {error}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").partition("\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)

    diff = commands.add_parser("diff", help="print the URLs that are new or whose lastmod changed")
    diff.add_argument("--old", nargs="+", required=True, metavar="SITEMAP", help="sitemaps that are live now (file or URL)")
    diff.add_argument("--new", nargs="+", required=True, metavar="SITEMAP", help="freshly built sitemaps (file or URL)")
    diff.add_argument("--output", metavar="FILE", help="write the URLs here (progress goes to stdout); default: URLs on stdout, progress on stderr")
    diff.set_defaults(run=run_diff)

    submit = commands.add_parser("submit", help="send URLs to IndexNow")
    submit.add_argument("urls_file", nargs="?", metavar="URLS_FILE", help="one URL per line; default: stdin")
    submit.add_argument("--host", help="site host name; default: the host of the first URL")
    submit.add_argument("--static-dir", default="static", help="directory holding the <key>.txt file (default: static)")
    submit.add_argument("--endpoint", default=ENDPOINT, help=f"IndexNow endpoint (default: {ENDPOINT})")
    submit.add_argument("--dry-run", action="store_true", help="print the request instead of sending it")
    submit.set_defaults(run=run_submit)

    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    sys.exit(main())
