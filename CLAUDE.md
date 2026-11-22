# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repo shape

Hugo site (theme `m10c`) deployed to GitHub Pages. Two git submodules:

- `content/` → `git@github.com:wangzw/blog.git` — **all posts live here, not in the parent repo**
- `themes/m10c/` → theme

The parent repo tracks everything except the posts: configuration, layout overrides, styles, translations, `scripts/`, the files in `static/`, the deploy workflow and the submodule pointers. Editing `content/` is editing the `blog` repo; changes must be pushed **inside the submodule first**, then the parent repo must bump its submodule pointer.

## Publishing a blog post — the canonical flow

Writing a new post starts with the `blog-post` skill (`.claude/skills/blog-post/`): gather the author's material, list the claims, write straight through, then translate. The steps below are the publishing mechanics that follow it.

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

Every post is also published as Markdown at `<post URL>index.md` (linked from the post's `<head>`, from `/llms.txt` and in full from `/llms-full.txt` and `/llms-full-zh.txt`). That file is the source as written, so **posts must not use shortcodes**; the build fails with the post's path if one does. Mermaid code blocks are fine.

### Revising a published post

When you change a post after it was published, set `lastmod` in the front matter of **both** language files, with an explicit `+08:00` offset and the same value in both:

```toml
date = "2026-04-27T00:00:00+08:00"
lastmod = "2026-05-20T10:30:00+08:00"
```

Hugo uses `lastmod` for the sitemap `<lastmod>`, JSON-LD `dateModified` and `article:modified_time`; without it they fall back to `date`. The post page shows "Updated <date>" next to the publication date once `lastmod` is a day or more after `date`. The deploy workflow submits a URL to IndexNow only when it is new or its sitemap `lastmod` changed, so a revision without `lastmod` is not announced to search engines.

## ⚠️ Date / timezone — the recurring trap

The CI build runs with `TZ=Asia/Shanghai` (see `.github/workflows/update-content.yaml`). Hugo's default behavior is to **hide posts whose `date` is in the future** relative to build time. Consequences:

- **Always write `date` with an explicit `+08:00` offset.** A bare `date = "2026-04-17"` is parsed as midnight UTC, which is 08:00 CST — so a post added in the morning CST will be "in the future" and invisible. Commit `42400f5` ("Fix publish date to avoid future-date issue in Hugo build") is exactly this bug.
- The two language files of the same post should share the same `date` (and the same `lastmod`, see "Revising a published post").
- If a post must appear immediately, set the time to an hour earlier than "now in CST" (e.g. today's date with `T00:00:00+08:00`) to stay safely in the past under any reasonable build clock.

## Common commands

| Task | Command |
|---|---|
| Local preview (auto-reload, includes drafts) | `hugo server -D` |
| Production-style local build | `hugo --gc --minify` |
| Build output location | `public/` (gitignored) |
| Sync submodules after fresh clone | `git submodule update --init --recursive` |
| Pull latest content only | `git submodule update --remote content` |
| Test the IndexNow script | `python3 -m unittest discover -s scripts -v` |

Hugo version in CI: `0.165.0` (extended). Match locally if debugging rendering differences.

## Deployment

`.github/workflows/update-content.yaml` runs on (a) every push to `main`, (b) a daily UTC-midnight cron that auto-syncs the `content` submodule and deploys if it moved, and (c) manual dispatch. Pushes bypass the "did submodule change" check and always deploy. There is no staging — `main` is production.

IndexNow: after the Hugo build and before the deploy, the build job runs `scripts/indexnow.py diff`, which compares the live `/en/sitemap.xml` and `/zh/sitemap.xml` with the fresh ones in `public/` and keeps the URLs that are new or whose `<lastmod>` changed. When there are any, the `indexnow` job (it needs a successful `deploy`) runs `scripts/indexnow.py submit`. A failed comparison or submission is printed as a `::warning::` annotation and the script exits 0, so it can never fail the deploy; no URLs means no request. The key is public by design: it is `static/<key>.txt` (the file name and the content are the key), served at the domain root; the script finds it there. Dry run: `python3 scripts/indexnow.py submit <urls-file> --dry-run`.

## Layout overrides

- `layouts/alias.html` — root-URL language detection + redirect. Reads `localStorage.preferred-lang`, falls back to `navigator.languages`, defaults to `en`. Touching this affects first-visit UX for every visitor.
- `layouts/asde/list.html` — custom list for the `asde` section (EN-only, exposed via EN menu in `hugo.toml`).
- `layouts/_markup/render-codeblock-mermaid.html` — renders ```` ```mermaid ```` code blocks as diagrams. It loads mermaid from jsdelivr, once per page and only on pages that contain a diagram; the theme itself has no mermaid support.
- `layouts/_default/baseof.html` — copy of the theme's base template with these changes: it calls the `seo.html` and `twitter_cards.html` partials, calls `llms.html` (default-language home only) and `llms-full.html` (every home), falls back to the site description when a page has none, shows `params.motto` under the avatar (`params.description` is the meta description and is not displayed), and lists `params.projects` in a "Projects" section at the bottom of the sidebar, styled in `assets/css/_extra.scss`.
- `layouts/_default/single.html` — copy of the theme's post template, plus an "Updated <date>" entry in the post meta (see "Revising a published post") and, for posts, previous/next links and up to three related posts after the article. Related posts come from `[related]` in `hugo.toml` (shared tags decide, the year breaks ties); both blocks are styled in `assets/css/_extra.scss` and are left out when empty.
- `layouts/_default/single.md`, `layouts/partials/post-markdown.html` — the Markdown rendition of a post (`index.md`: H1 title, date and canonical URL line, description, source body). It comes from the `markdown` output format in `hugo.toml`, which a site-level `cascade` gives to pages under `/posts/` only. `llms-full.html` reuses the partial.
- `layouts/partials/is-updated.html` — true when `lastmod` is a day or more after `date`; used by `single.html` and `post-markdown.html`.
- `layouts/partials/seo.html` — `noindex, follow` robots meta for pages with `noindex = true`, canonical link, hreflang alternates (`x-default` is the English page), the `text/markdown` alternate link of a post and JSON-LD (`WebSite` + `Person` on the home pages, `BlogPosting` on posts).
- `layouts/partials/twitter_cards.html` — replaces Hugo's embedded Twitter card template so the card stays `summary`; the default share image (`params.images`) is the square avatar, which the large-image card would crop.
- `layouts/partials/llms.html` — publishes `/llms.txt` at the domain root, listing the posts of both languages (linking to their `index.md`), `params.projects` and, under "Optional", the two llms-full files.
- `layouts/partials/llms-full.html` — publishes `/llms-full.txt` (English) and `/llms-full-zh.txt` (Chinese): the Markdown renditions of all posts of that language, concatenated. It runs on each language's home page so the labels come out in that language.
- `layouts/robots.txt`, `layouts/sitemapindex.xml` — open to every crawler; both also list the sitemaps of `params.projects` in `hugo.toml`, which are sites served under this domain from other repositories (currently `/peers/`).
- Tag pages (`/tags/` and every tag) are `noindex, follow` and left out of the sitemaps: a site-level `cascade` in `hugo.toml` sets `noindex = true` and `sitemap.disable = true` on `taxonomy` and `term` pages. To keep another page out of the index, set the same two keys in its front matter.
- Other templates come from the theme; override by copying into `layouts/` before editing.
