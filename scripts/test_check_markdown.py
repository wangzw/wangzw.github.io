"""Tests for check_markdown.py. Run: python3 -m unittest discover -s scripts -v"""
import contextlib
import io
import tempfile
import unittest
from pathlib import Path

import check_markdown


def build(root, pages):
    """pages maps a URL path to whether the page has an index.md next to its index.html."""
    for url_path, has_markdown in pages.items():
        directory = Path(root) / url_path.strip("/")
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "index.html").write_text("<html></html>", encoding="utf-8")
        if has_markdown:
            (directory / "index.md").write_text("# Title\n", encoding="utf-8")


def run(pages):
    """Build a site from `pages`, run the script on it; return (exit code, stdout)."""
    out = io.StringIO()
    with tempfile.TemporaryDirectory() as root:
        build(root, pages)
        with contextlib.redirect_stdout(out):
            code = check_markdown.main([root])
    return code, out.getvalue()


class CheckMarkdownTest(unittest.TestCase):
    def test_complete_site_passes(self):
        """A site whose root, home, list and regular pages all have an index.md passes."""
        code, out = run({"/": True, "/en/": True, "/zh/posts/": True, "/zh/tags/测试/": True, "/en/about/": True})
        self.assertEqual(code, 0)
        self.assertIn("all 5 pages", out)

    def test_page_without_rendition_fails(self):
        """A page in scope without an index.md fails the check and is named."""
        code, out = run({"/": True, "/en/": True, "/en/about/": False, "/zh/posts/a/": False})
        self.assertEqual(code, 1)
        self.assertIn("::error title=Markdown renditions::/en/about/ has no index.md", out)
        self.assertIn("::error title=Markdown renditions::/zh/posts/a/ has no index.md", out)
        self.assertNotIn("::/en/ ", out)

    def test_root_needs_a_rendition(self):
        """The root URL is in scope although no Hugo page is published there."""
        code, out = run({"/": False, "/en/": True})
        self.assertEqual(code, 1)
        self.assertIn("::/ has no index.md", out)

    def test_pager_and_alias_pages_are_exempt(self):
        """Pager pages and their aliases, which the rewrite rule skips, need no index.md."""
        code, _ = run({"/": True, "/en/": True, "/en/page/1/": False, "/en/tags/go/page/2/": False})
        self.assertEqual(code, 0)

    def test_other_sites_under_the_domain_are_exempt(self):
        """A directory outside the language trees, such as another project's site, is not checked."""
        code, _ = run({"/": True, "/en/": True, "/peers/": False, "/english/": False})
        self.assertEqual(code, 0)

    def test_directory_without_pages_fails(self):
        """A directory with no page in scope fails: a wrong path must not pass."""
        code, out = run({"/peers/": True})
        self.assertEqual(code, 1)
        self.assertIn("no page found", out)


if __name__ == "__main__":
    unittest.main()
