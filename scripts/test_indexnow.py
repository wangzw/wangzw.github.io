"""Tests for indexnow.py. Run: python3 -m unittest discover -s scripts -v"""
import contextlib
import io
import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import indexnow

KEY = "0123456789abcdef0123456789abcdef"


def sitemap(*entries):
    """entries are (loc, lastmod or None)."""
    urls = "".join(
        f"<url><loc>{loc}</loc>" + (f"<lastmod>{lastmod}</lastmod>" if lastmod else "") + "</url>"
        for loc, lastmod in entries
    )
    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + urls + "</urlset>"
    )


def run(argv):
    """Run the script's main(); return (exit code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = indexnow.main(argv)
    return code, out.getvalue(), err.getvalue()


class Recorder(BaseHTTPRequestHandler):
    status = 200
    received = []
    log = []

    def do_POST(self):
        length = int(self.headers["Content-Length"])
        Recorder.received.append((self.headers["Content-Type"], json.loads(self.rfile.read(length))))
        self.send_response(Recorder.status)
        self.end_headers()
        self.wfile.write(b"reply from test server")

    def log_message(self, format, *args):
        # Keep the access log out of the test output.
        Recorder.log.append(format % args)


class FlakySitemap(BaseHTTPRequestHandler):
    """Answers the first `failures` GET requests with a 503, then serves `body`."""
    failures = 0
    body = b""
    requests = 0

    def do_GET(self):
        FlakySitemap.requests += 1
        if FlakySitemap.requests <= FlakySitemap.failures:
            self.send_response(503)
            self.end_headers()
            return
        self.send_response(200)
        self.end_headers()
        self.wfile.write(FlakySitemap.body)

    def log_message(self, format, *args):
        pass  # keep the access log out of the test output


class IndexNowTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "static").mkdir()
        (self.tmp / "static" / f"{KEY}.txt").write_text(KEY)
        (self.tmp / "static" / "robots.txt").write_text("not a key")

    def write(self, name, text):
        path = self.tmp / name
        path.write_text(text, encoding="utf-8")
        return str(path)

    def test_diff_reports_new_and_changed_urls_only(self):
        old = self.write("old.xml", sitemap(
            ("https://example.com/en/a/", "2026-04-01T00:00:00+08:00"),
            ("https://example.com/en/b/", "2026-04-02T00:00:00+08:00"),
            ("https://example.com/en/gone/", "2026-04-03T00:00:00+08:00"),
            ("https://example.com/en/nodate/", None),
        ))
        new = self.write("new.xml", sitemap(
            ("https://example.com/en/a/", "2026-04-01T00:00:00+08:00"),    # unchanged
            ("https://example.com/en/b/", "2026-04-09T00:00:00+08:00"),    # lastmod moved
            ("https://example.com/en/c/", "2026-04-09T00:00:00+08:00"),    # new
            ("https://example.com/en/nodate/", None),                      # unchanged, no lastmod
        ))
        code, out, _ = run(["diff", "--old", old, "--new", new])
        self.assertEqual(code, 0)
        self.assertEqual(out.split(), ["https://example.com/en/b/", "https://example.com/en/c/"])

    def test_same_instant_in_another_offset_is_not_a_change(self):
        old = self.write("old.xml", sitemap(("https://example.com/en/a/", "2026-04-01T00:00:00+08:00")))
        new = self.write("new.xml", sitemap(("https://example.com/en/a/", "2026-03-31T16:00:00+00:00")))
        self.assertEqual(run(["diff", "--old", old, "--new", new])[1], "")

    def test_diff_merges_several_sitemaps_and_writes_output_file(self):
        old_en = self.write("old-en.xml", sitemap(("https://example.com/en/", "2026-04-01T00:00:00+08:00")))
        old_zh = self.write("old-zh.xml", sitemap(("https://example.com/zh/", "2026-04-01T00:00:00+08:00")))
        new_en = self.write("new-en.xml", sitemap(("https://example.com/en/", "2026-04-01T00:00:00+08:00")))
        new_zh = self.write("new-zh.xml", sitemap(("https://example.com/zh/", "2026-05-01T00:00:00+08:00")))
        target = self.tmp / "urls.txt"
        code, out, _ = run(["diff", "--old", old_en, old_zh, "--new", new_en, new_zh, "--output", str(target)])
        self.assertEqual(code, 0)
        self.assertEqual(target.read_text().split(), ["https://example.com/zh/"])
        self.assertIn("1 new or changed", out)

    def test_diff_with_unreadable_live_sitemap_warns_and_submits_nothing(self):
        new = self.write("new.xml", sitemap(("https://example.com/en/a/", None)))
        code, out, err = run(["diff", "--old", str(self.tmp / "missing.xml"), "--new", new])
        self.assertEqual(code, 0)
        self.assertEqual(out, "")
        self.assertIn("::warning", err)

    def serve_flaky(self, failures, body):
        FlakySitemap.failures, FlakySitemap.body, FlakySitemap.requests = failures, body.encode(), 0
        server = HTTPServer(("127.0.0.1", 0), FlakySitemap)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        return f"http://127.0.0.1:{server.server_port}/sitemap.xml"

    def test_diff_retries_a_live_sitemap_that_fails_once(self):
        # A single failed fetch must not drop the URLs for good: after the deploy
        # they are in the live sitemap, so no later diff would report them.
        indexnow.RETRY_DELAY = 0
        old = self.serve_flaky(1, sitemap(("https://example.com/en/a/", None)))
        new = self.write("new.xml", sitemap(
            ("https://example.com/en/a/", None),
            ("https://example.com/en/b/", None),
        ))
        code, out, err = run(["diff", "--old", old, "--new", new])
        self.assertEqual(code, 0)
        self.assertEqual(out.split(), ["https://example.com/en/b/"])
        self.assertNotIn("::warning", err)
        self.assertEqual(FlakySitemap.requests, 2)

    def test_diff_gives_up_on_a_live_sitemap_that_keeps_failing(self):
        indexnow.RETRY_DELAY = 0
        old = self.serve_flaky(99, "")
        new = self.write("new.xml", sitemap(("https://example.com/en/a/", None)))
        code, out, err = run(["diff", "--old", old, "--new", new])
        self.assertEqual(code, 0)
        self.assertEqual(out, "")
        self.assertIn("::warning", err)
        self.assertEqual(FlakySitemap.requests, indexnow.FETCH_ATTEMPTS)

    def test_diff_rejects_a_sitemap_index(self):
        index = self.write("index.xml", '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"/>')
        new = self.write("new.xml", sitemap(("https://example.com/en/a/", None)))
        code, out, err = run(["diff", "--old", index, "--new", new])
        self.assertEqual((code, out), (0, ""))
        self.assertIn("urlset", err)

    def test_submit_dry_run_prints_the_request_and_sends_nothing(self):
        urls = self.write("urls.txt", "https://example.com/en/a/\nhttps://example.com/en/a/\nhttps://other.org/x/\n")
        code, out, _ = run(["submit", urls, "--static-dir", str(self.tmp / "static"), "--dry-run",
                            "--endpoint", "http://127.0.0.1:1/never-called"])
        self.assertEqual(code, 0)
        self.assertIn('"host": "example.com"', out)
        self.assertIn(f'"key": "{KEY}"', out)
        self.assertEqual(out.count("https://example.com/en/a/"), 1)  # duplicates collapse
        self.assertIn("::warning", out)                               # the foreign host was dropped
        self.assertNotIn('"https://other.org/x/"', out)

    def test_submit_with_no_urls_does_nothing(self):
        urls = self.write("urls.txt", "\n")
        code, out, _ = run(["submit", urls, "--static-dir", str(self.tmp / "static")])
        self.assertEqual(code, 0)
        self.assertIn("nothing to submit", out)

    def serve(self, status):
        Recorder.status, Recorder.received = status, []
        server = HTTPServer(("127.0.0.1", 0), Recorder)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        return f"http://127.0.0.1:{server.server_port}/indexnow"

    def test_submit_posts_the_documented_json_body(self):
        endpoint = self.serve(200)
        urls = self.write("urls.txt", "https://example.com/en/a/\n")
        code, out, _ = run(["submit", urls, "--static-dir", str(self.tmp / "static"), "--endpoint", endpoint])
        self.assertEqual(code, 0)
        self.assertEqual(Recorder.received, [(
            "application/json; charset=utf-8",
            {"host": "example.com", "key": KEY, "urlList": ["https://example.com/en/a/"]},
        )])
        self.assertNotIn("::warning", out)

    def test_rejected_submission_is_a_warning_not_a_failure(self):
        endpoint = self.serve(403)
        urls = self.write("urls.txt", "https://example.com/en/a/\n")
        code, out, _ = run(["submit", urls, "--static-dir", str(self.tmp / "static"), "--endpoint", endpoint])
        self.assertEqual(code, 0)
        self.assertIn("HTTP 403", out)
        self.assertIn("reply from test server", out)
        self.assertIn("::warning", out)

    def test_unreachable_endpoint_is_a_warning_not_a_failure(self):
        urls = self.write("urls.txt", "https://example.com/en/a/\n")
        code, out, _ = run(["submit", urls, "--static-dir", str(self.tmp / "static"),
                            "--endpoint", "http://127.0.0.1:1/indexnow"])
        self.assertEqual(code, 0)
        self.assertIn("::warning", out)

    def test_missing_key_file_is_a_warning_not_a_failure(self):
        urls = self.write("urls.txt", "https://example.com/en/a/\n")
        empty = self.tmp / "nokey"
        empty.mkdir()
        code, out, _ = run(["submit", urls, "--static-dir", str(empty), "--dry-run"])
        self.assertEqual(code, 0)
        self.assertIn("::warning", out)


if __name__ == "__main__":
    unittest.main()
