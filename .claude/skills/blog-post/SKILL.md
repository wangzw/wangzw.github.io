---
name: blog-post
description: How to write a new post for this blog. Use it whenever the user asks to write, draft, outline or plan a blog post, article or essay for this site, or hands over notes, a transcript, a session log or a topic and wants a post out of it. The method is material first - gather what the author actually did and thinks, list the claims, then write straight through - because outline-first drafting is what made earlier posts read as templated. Do not start drafting from a topic alone.
---

# Writing a post for this blog

## Why this is not an outline-first workflow

Earlier posts here were reviewed by twenty independent readers. The complaint they raised most was not a word or a phrase. It was that each post made its main point three to five times: once in the introduction, again in a section heading, again at the end of that section, again in the conclusion. Every section had been written as a small article of its own, with an opener, an argument and a closing line that restated the thesis.

That shape is decided before the first sentence exists. A draft grown from a fixed outline (hook, context, three to five sections, practical tips, summary, call to action) fills every slot, and every slot gets rounded off. Review after the fact cannot repair it, because each repetition carries a little content of its own and cutting it damages the post.

So the order here is reversed. Material comes first, the post comes from the material, and structure appears last.

The steps below are the speak-like-human writing guidance (`references/writing.md` in that skill) applied to this blog. If that skill is installed, its guidance and this file agree; where this file is more specific, follow this file.

Publishing mechanics (two language files per post, TOML front matter, the date and timezone trap, the submodule commit flow) are in the repository's `CLAUDE.md`. Follow it; this skill does not repeat it.

## 1. Gather the author's material

A post needs something only the author has: what they did, what happened, what they concluded. Without it the only thing that can be written is a generic skeleton, and that is exactly what reads as templated.

Material can be notes, a spoken account, chat or session logs, commit history, pull requests, measurements, an earlier draft. If the author gives a topic and nothing else, ask before writing. Ask about things only they know, a few questions at a time:

- What happened, in order? What did you try first, and what made you change course?
- What surprised you, or turned out to be wrong?
- Which numbers were measured, and where do they come from? Which are rough impressions?
- Which examples really happened, and which are illustrations you made up?
- What would you tell a colleague who is about to do the same thing?
- What are you still unsure about?
- What must not be published (internal names, people, customers, unreleased work)?

Rough answers are enough. Ten minutes of the author talking is worth more than any amount of polishing later.

Research is allowed for checking facts, finding the right link, and quoting a source accurately. It does not stand in for the author's experience: do not research a topic and fill the post with what the research found.

Keep the material outside the repository unless the author says where to put it. `content/` is a public repository, and raw notes usually contain things that should not be published.

Everything in the post must trace back to this material or to a cited public source. Do not invent projects, incidents, figures, file names, quotes or first-person experience, and do not carry in details from the session context, memory or other files that the author did not offer for this post.

## 2. List the claims, not an outline

Write down what the post will say, one line per claim. For each line note:

- where it comes from in the material;
- whether it is something that happened, something measured, the author's judgement, a hypothetical illustration, or a cited source;
- anything the author flagged as uncertain.

There are no slots in this list. It has no "introduction", "background" or "conclusion", and no target number of sections. If the material supports four claims, the list has four lines.

Each claim gets one home. If two lines say the same thing, merge them now.

Show the list to the author before drafting. It takes them two minutes to cross out what they do not want to say, fix what was misread and add what is missing, and it is far cheaper than finding out from a finished draft.

## 3. Write straight through

One writer, start to finish, in one pass. Do not hand sections to subagents: a writer who sees one section cannot know what the others already said, and will say it again.

Write in the order a person would tell this to a colleague. That is usually the order things happened, or the order in which one thing explains the next. It is rarely "problem, name, mechanism, remedy".

While writing:

- Say each claim once, where it belongs. When a later passage depends on it, point back in a clause and move on. Do not argue it again.
- Start with the first real thing. No hook formula, no rhetorical question to the reader, no "in this post we will".
- Stop when the content ends. No summary of what was just said, no takeaways list, no call to action, no question to the audience. If the last paragraph ends on a fact, a number or a link, that is a good ending.
- Let length follow the material. A point that needs three paragraphs gets three; a point that needs one sentence gets one. Sections of very different length are fine.
- Add headings after the text exists, as labels for what is there. Do not write to fill a heading.
- Use a list or a table when the material is a list or a table: steps, fields, a comparison along the same dimensions. Do not turn an argument into bullets, and do not pad a list to a round number.
- Keep the status of every example visible. If it is hypothetical, say so in the sentence. Do not tell an illustration as if it happened.
- Leave the author's hedges and limits in. "We don't handle this case" and "I'm not sure this generalizes" belong in the post.
- No keyword repetition for search engines. The description says what the post is about in a sentence or two and does not announce its skeleton ("five forms, five causes, nine remedies").

Write the first version in the language the author gave the material in.

## 4. Check the draft against the claim list

Before any outside review, go down the claim list and find every place the draft states each claim.

- Stated more than once: keep it where it is argued best. Turn the other places into a short reference back, or cut them. Check that nothing unique goes out with the cut.
- Not stated at all: either it was dropped on purpose, or the draft is missing something. Decide which.
- In the draft but not on the list: where did it come from? If it is not in the material, remove it or ask the author.

Then check every number, name, path, link and quotation against the material.

## 5. Language check

Run the language skill for the draft's language: speak-like-chinese for Chinese, an English style skill for English.

That is the last required check. The adversarial review in the speak-like-human skill is not part of this flow: it spawns several subagents per post, and it runs only when the author asks for it. If the author does ask, pass the material as the author's notes so its guard and auditor can check that nothing unsourced was added.

## 6. The second language

Translate the finished post. Do not write the other version from the claim list or from the material, because two independently generated versions drift apart: different examples, different emphasis, different conclusions.

The translation keeps the same claims in the same order with the same numbers and the same structure. Title, description and tags are written in the target language. Both files share one `date`. Then run the language skill for that language over the translation, since a faithful translation can still read as translated.

## 7. Publish only when asked

Preview with `hugo server -D`. Commit and push only when the author asks, following the flow in `CLAUDE.md`.
