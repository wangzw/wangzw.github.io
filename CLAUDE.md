# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repo shape

Hugo site (theme `m10c`) deployed to GitHub Pages. Two git submodules:

- `content/` → `git@github.com:wangzw/blog.git` — **all posts live here, not in the parent repo**
- `themes/m10c/` → theme

The parent repo only tracks configuration, layout overrides, and submodule pointers. Editing `content/` is editing the `blog` repo; changes must be pushed **inside the submodule first**, then the parent repo must bump its submodule pointer.

## Publishing a blog post — the canonical flow

Every post MUST be bilingual. Hugo is configured with `defaultContentLanguage = "en"` and `defaultContentLanguageInSubdir = true`, and the root URL (`layouts/alias.html`) redirects visitors to `/en/` or `/zh/` based on their browser language. A post that exists in only one language will 404 for half the audience.

1. Create **two** files in `content/posts/`, sharing the same slug:
   - `content/posts/<slug>.zh.md`
   - `content/posts/<slug>.en.md`
2. Use **TOML front matter** (`+++`), not YAML. Minimal required keys:
   ```toml
   +++
   title = "..."
   date = "YYYY-MM-DDTHH:MM:SS+08:00"
   description = "..."
   tags = ["...", "..."]
   +++
   ```
   Tags and description are localized — write tags in the same language as the body.
3. Preview locally with `hugo server` (served at http://localhost:1313; `/en/` and `/zh/` prefixes).
4. Commit inside the submodule:
   ```bash
   cd content && git add posts/<slug>.*.md && git commit -m "..." && git push
   ```
5. Bump the parent repo pointer:
   ```bash
   cd .. && git add content && git commit -m "Update content submodule: ..." && git push
   ```
   (A daily cron workflow also syncs the submodule, so step 5 can be skipped for non-urgent posts — but pushing it yourself deploys immediately.)

## ⚠️ Date / timezone — the recurring trap

The CI build runs with `TZ=Asia/Shanghai` (see `.github/workflows/update-content.yaml`). Hugo's default behavior is to **hide posts whose `date` is in the future** relative to build time. Consequences:

- **Always write `date` with an explicit `+08:00` offset.** A bare `date = "2026-04-17"` is parsed as midnight UTC, which is 08:00 CST — so a post added in the morning CST will be "in the future" and invisible. Commit `42400f5` ("Fix publish date to avoid future-date issue in Hugo build") is exactly this bug.
- The two language files of the same post should share the same `date`.
- If a post must appear immediately, set the time to an hour earlier than "now in CST" (e.g. today's date with `T00:00:00+08:00`) to stay safely in the past under any reasonable build clock.

## Common commands

| Task | Command |
|---|---|
| Local preview (auto-reload, includes drafts) | `hugo server -D` |
| Production-style local build | `hugo --gc --minify` |
| Build output location | `public/` (gitignored) |
| Sync submodules after fresh clone | `git submodule update --init --recursive` |
| Pull latest content only | `git submodule update --remote content` |

Hugo version in CI: `0.157.0` (extended). Match locally if debugging rendering differences.

## Deployment

`.github/workflows/update-content.yaml` runs on (a) every push to `main`, (b) a daily UTC-midnight cron that auto-syncs the `content` submodule and deploys if it moved, and (c) manual dispatch. Pushes bypass the "did submodule change" check and always deploy. There is no staging — `main` is production.

## Layout overrides

- `layouts/alias.html` — root-URL language detection + redirect. Reads `localStorage.preferred-lang`, falls back to `navigator.languages`, defaults to `en`. Touching this affects first-visit UX for every visitor.
- `layouts/asde/list.html` — custom list for the `asde` section (EN-only, exposed via EN menu in `hugo.toml`).
- Post/tag templates come from the theme; override by copying into `layouts/` before editing.
