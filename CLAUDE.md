# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repo shape

Hugo site (theme `m10c`) deployed to GitHub Pages. Two git submodules:

- `content/` → `git@github.com:wangzw/blog.git` — **all posts live here, not in the parent repo**
- `themes/m10c/` → theme

The parent repo tracks everything except the posts: configuration, layout overrides, styles, translations, `scripts/`, the files in `static/`, the deploy workflow and the submodule pointers. Editing `content/` is editing the `blog` repo; changes must be pushed **inside the submodule first**, then the parent repo must bump its submodule pointer.

## Commit Convention

Supplements the `commit-convention` skill.

### Scopes

- `assets`: `assets/`, the stylesheet that extends the theme
- `ci`: `.github/workflows/`, the workflow that builds and deploys
- `config`: `hugo.toml` and `archetypes/`, the site configuration and the scaffolding for new content
- `content`: the `content` submodule, where the posts and pages live
- `i18n`: `i18n/`, the Chinese interface strings
- `layouts`: `layouts/`, the template overrides
- `scripts`: `scripts/`, the IndexNow helper, the Markdown rendition check and their tests
- `skills`: `.claude/skills/`, the project's own skills
- `static`: `static/`, the files served from the domain root
- `theme`: the `themes/m10c` submodule pointer
- `site`: cross-cutting changes
- `repo`: repository-level configuration such as `.gitignore`, `.gitmodules`, `README.md` and this file

### Rules

- A post change is a commit inside the `content` submodule; the parent repository then records it in a separate commit that bumps the pointer and states what the submodule commits contain.

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
   Tags and description are localized — write tags in the same language as the body. Write a `description` anyway: without one the page falls back to its plain-text summary, and that text is what the meta description, social cards, JSON-LD and `/llms.txt` show.
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

Every post is also published as Markdown at `<post URL>index.md` (linked from the post's `<head>`, from `/llms.txt` and in full from `/llms-full.txt` and `/llms-full-zh.txt`). That file is the source as written, so **posts must not use shortcodes** (nor may the About page, which is published the same way); the build fails with the page's path if one does. Mermaid code blocks are fine.

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
| Test the scripts | `python3 -m unittest discover -s scripts -v` |
| Check the Markdown renditions of a build | `python3 scripts/check_markdown.py public` |

Hugo version in CI: `0.165.0` (extended). Match locally if debugging rendering differences.

## Deployment

`.github/workflows/update-content.yaml` runs on (a) every push to `main`, (b) a daily UTC-midnight cron that auto-syncs the `content` submodule and deploys if it moved, and (c) manual dispatch. Pushes bypass the "did submodule change" check and always deploy. There is no staging — `main` is production.

IndexNow: after the Hugo build and before the deploy, the build job runs `scripts/indexnow.py diff`, which compares the live `/en/sitemap.xml` and `/zh/sitemap.xml` with the fresh ones in `public/` and keeps the URLs that are new or whose `<lastmod>` changed. When there are any, the `indexnow` job (it needs a successful `deploy`) runs `scripts/indexnow.py submit`. A failed comparison or submission is printed as a `::warning::` annotation and the script exits 0, so it can never fail the deploy; no URLs means no request. The key is public by design: it is `static/<key>.txt` (the file name and the content are the key), served at the domain root; the script finds it there. Dry run: `python3 scripts/indexnow.py submit <urls-file> --dry-run`.

## Markdown for agents

A request with `Accept: text/markdown` gets the Markdown rendition of the page; HTML stays the default. GitHub Pages cannot negotiate, so two parts work together:

- **This repo** publishes an `index.md` next to the `index.html` of every page under `/en/` and `/zh/` (`[outputs]` in `hugo.toml`, `layouts/_default/single.md` and `list.md`) and one at the root (`/index.md`, the text of `/llms.txt`). GitHub Pages serves them as `text/markdown; charset=utf-8`.
- **Cloudflare** (zone `zhanwei.wang`, in front of GitHub Pages) holds two Transform Rules. They are set in the dashboard under Rules, not in this repo.

URL Rewrite Rule, rewriting the path dynamically to `concat(http.request.uri.path, "index.md")` and preserving the query:

```
http.host eq "zhanwei.wang"
and (http.request.uri.path eq "/" or starts_with(http.request.uri.path, "/en/") or starts_with(http.request.uri.path, "/zh/"))
and ends_with(http.request.uri.path, "/")
and not (http.request.uri.path contains "/page/")
and any(http.request.headers["accept"][*] contains "text/markdown")
```

Response Header Transform Rule, **adding** (not setting, the origin sends `Vary: Accept-Encoding`) the header `Vary: Accept`. It uses the `raw.` field because the rewrite has already changed `http.request.uri.path`:

```
http.host eq "zhanwei.wang" and ends_with(raw.http.request.uri.path, "/")
```

- Pager pages and their aliases (`/page/N/`) have no rendition, so the rule skips them and they stay HTML.
- A page in the rule's scope without an `index.md` would answer a Markdown request with a 404. `scripts/check_markdown.py` repeats the scope (`PREFIXES`, `EXCLUDED`) and the build job runs it after Hugo: such a page stops the deploy. A front matter `aliases` entry under `/en/` or `/zh/` is such a page. Change the rule and the script together, and add a language to both.
- Check the live site: `curl -sI -H "Accept: text/markdown" https://zhanwei.wang/en/` must show `content-type: text/markdown; charset=utf-8` and `vary: Accept`; without the header the same URL is `text/html`.

## Layout overrides

- `layouts/alias.html` — the template of **every** alias page Hugo writes: the root `/` (redirect to a language, `defaultContentLanguageInSubdir`) and old URLs such as `/en/page/1/`. The script reads `localStorage.preferred-lang`, falls back to `navigator.languages`, defaults to `en`, and only runs at `/`; the meta refresh handles the other aliases. The body is for fetchers without JavaScript. Nothing in the template data tells the root from `/en/page/1/` (same target), so an alias to the default-language home lists every language, any other alias links to its target. Touching this affects first-visit UX for every visitor.
- `layouts/404.html`, `layouts/partials/root-404.html` — the 404 page in the language of the site (strings in `i18n/zh.toml`). GitHub Pages only serves `/404.html` at the root, so the 404 page of the non-default language also publishes that file, a bilingual page with links to `/en/` and `/zh/`; it comes from there because the Chinese text is read through `i18n`. It is produced by a plain `hugo` build, no workflow step.
- `layouts/_markup/render-codeblock-mermaid.html` — renders ```` ```mermaid ```` code blocks as diagrams. It loads mermaid from jsdelivr, once per page and only on pages that contain a diagram; the theme itself has no mermaid support.
- `layouts/_default/baseof.html` — copy of the theme's base template with these changes: it calls the `seo.html` and `twitter_cards.html` partials, calls `llms.html` (default-language home only) and `llms-full.html` (every home), takes the meta description from `page-description.html`, puts the page number into the `<title>` of the second and later pages of a list, falls back to the language home page's feed for the RSS link, shows `params.motto` under the avatar (`params.description` is the meta description and is not displayed), and lists `params.projects` in a "Projects" section at the bottom of the sidebar (a `<p>`, not a heading, so no heading comes before the page's `<h1>`), styled in `assets/css/_extra.scss`.
- `layouts/partials/language.html` — the language switcher; on a page with a translation it links to that translation, otherwise (and on the 404 page) to the home page of the language. Keeps the theme's `onclick` that stores `preferred-lang`.
- `layouts/partials/page-description.html` — the one description of a page: its own, else the plain-text summary, else the site description. The expression is the one in Hugo's embedded opengraph template (which still writes `og:*`), so meta description, `og:description`, `twitter:description`, JSON-LD, `llms.txt` and the Markdown rendition agree. `llms.txt` and the Markdown rendition collapse it onto one line.
- `layouts/partials/page-image.html` — the absolute URL of the share image: the page's `images`, else `params.images`. Used by `twitter_cards.html` and the JSON-LD.
- `layouts/partials/person.html` — the schema.org `Person` of the author, in the language of the current site. `@id` is `https://zhanwei.wang/#person` in both languages; `alternateName` lists the author names of the other languages (`languages.*.params.author`) and then `params.author_handle`; `sameAs` comes from `params.social`.
- `layouts/partials/pager-number.html` — the page number of a paginated list page (1 otherwise).
- `layouts/_default/single.html` — copy of the theme's post template, plus an "Updated <date>" entry in the post meta (see "Revising a published post") and, for posts, previous/next links and up to three related posts after the article. Related posts come from `[related]` in `hugo.toml` (shared tags decide, the year breaks ties); both blocks are styled in `assets/css/_extra.scss` and are left out when empty.
- `layouts/_default/single.md`, `layouts/partials/post-markdown.html` — the Markdown rendition of a post or the About page (`index.md`: H1 title, date and canonical URL line, description, source body; no date on a page without one). It comes from the `markdown` output format in `hugo.toml`, which `[outputs]` gives to every page kind (see "Markdown for agents"). `llms-full.html` reuses the partial.
- `layouts/_default/list.md` — the Markdown rendition of a list page (a home page, `/posts/`, the tags overview, a tag): what the HTML page lists, without pagination, every entry linking to the Markdown rendition of its target. A home page also links to the menu pages and the other language and lists `params.projects`.
- `layouts/partials/markdown-url.html` — the URL of a page's Markdown rendition (its permalink when it has none); used by `list.md` and `llms.html`.
- `layouts/partials/is-updated.html` — true when `lastmod` is a day or more after `date`; used by `single.html` and `post-markdown.html`.
- `layouts/partials/seo.html` — `noindex, follow` robots meta for pages with `noindex = true`, canonical link, hreflang alternates (`x-default` is the English page), the `text/markdown` alternate link of the page (left out on the second and later pages of a list, which have no rendition) and JSON-LD: `WebSite` + `Person` on the home pages, `BlogPosting` (with `image` and the full `Person` as author) on posts, `ProfilePage` (its `mainEntity` is the same `Person`) on the About page `/about`. Fields with no value are left out.
- `layouts/partials/twitter_cards.html` — replaces Hugo's embedded Twitter card template so the card stays `summary`; the default share image (`params.images`) is the square avatar, which the large-image card would crop.
- `layouts/partials/llms.html` — publishes `/llms.txt` at the domain root, listing the posts of both languages (linking to their `index.md`; the `: description` part is left out when there is none, brackets in titles are escaped), `params.projects` with the `llms` file of each project in every language, and, under "Optional", the two llms-full files. It publishes the same text as `/index.md`, the Markdown rendition of the root URL, which is an alias page and has none of its own.
- `layouts/partials/llms-full.html` — publishes `/llms-full.txt` (English) and `/llms-full-zh.txt` (Chinese): the Markdown renditions of all posts of that language, concatenated. It runs on each language's home page so the labels come out in that language.
- `layouts/robots.txt` — open to every crawler; it declares `Content-Signal: ai-train=yes, search=yes, ai-input=yes` (https://contentsignals.org/) and points to the root sitemap index `/sitemap.xml` (Hugo's built-in template), which lists the two language sitemaps.
- `params.projects` in `hugo.toml` — the author's projects, each a site of its own (currently peers). They are only linked: from the sidebar, the Markdown rendition of the home pages and `/llms.txt` (`llms` is the project's `llms.txt`). `languages.zh.params.projects` repeats the list with the Chinese URLs.
- Tag pages (`/tags/` and every tag) are `noindex, follow` and left out of the sitemaps: a site-level `cascade` in `hugo.toml` sets `noindex = true` and `sitemap.disable = true` on `taxonomy` and `term` pages. To keep another page out of the index, set the same two keys in its front matter. A second `cascade` gives the Chinese tags overview its title "标签" (the taxonomy name is not translated by Hugo), so keep it equal to "Tags" in `i18n/zh.toml`.
- The About page is `content/about.{en,zh}.md`, linked from the menu by `pageRef` in `hugo.toml`.
- Other templates come from the theme; override by copying into `layouts/` before editing.
