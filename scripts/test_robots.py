"""Tests for layouts/robots.txt. Run: python3 -m unittest discover -s scripts -v"""
import unittest
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "layouts" / "robots.txt"

# RFC 9309 rules plus the sitemaps.org Sitemap line; Google and Bing flag any other
# directive (Bing's robots.txt tester reports it as an error).
SUPPORTED = {"user-agent", "allow", "disallow", "sitemap"}


class RobotsTest(unittest.TestCase):
    def test_only_supported_directives(self):
        for number, line in enumerate(TEMPLATE.read_text(encoding="utf-8").splitlines(), 1):
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            directive = line.split(":", 1)[0].strip().lower()
            self.assertIn(directive, SUPPORTED, f"line {number}: {line}")


if __name__ == "__main__":
    unittest.main()
