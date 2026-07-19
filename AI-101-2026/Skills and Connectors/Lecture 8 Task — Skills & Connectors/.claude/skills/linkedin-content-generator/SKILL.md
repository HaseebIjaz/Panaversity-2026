---
name: linkedin-content-generator
description: Turns user-supplied source material (pasted text, an attached file, a GitHub file/repo via connector, or a Google Drive file via connector) into LinkedIn content — Article, posts, hashtags, distribution notes — positioned around the user's Agentic AI Developer brand, compiled into one editable Word (.docx). Requires both — real source material was actually supplied (not just a topic named), AND the ask is specifically LinkedIn — stated directly or via signals like "share professionally"/"build my profile," not a platform-less "make this a post." Trigger for turning notes, a transcript, or a project writeup into a LinkedIn article, post(s), or "content package," even unnamed. Do NOT trigger for commenting strategy, connection-request messaging, other platforms (X/Twitter, blogs), or content with no source material supplied — ask for it instead of inventing a topic.
---

# LinkedIn Content Generator

Turns a piece of source material the user actually provides into a complete, ready-to-post LinkedIn content package, positioned around their Agentic AI Developer brand. The full strategist brief this skill implements lives in `references/content-strategist-prompt.md` — read it in full before drafting anything. It is long on purpose: it encodes the voice, the non-negotiable constraints, and the exact output structure this skill must follow. This SKILL.md file covers triggering, request routing, and the confirmation checkpoints; the reference file covers everything about how to actually write the content.

## Why the guard clauses in this skill matter

The single most important constraint in the reference brief is that **this skill never originates ideas** — every article, post, hook, or lesson must trace back to something the user actually gave you. That's what makes the output usable for building genuine professional authority rather than generic AI-hype filler. Because of that, getting the input right before you start drafting matters more than for a typical content-generation task — so this skill opens with a mandatory Guard Clause Phase, not a soft suggestion to check things.

The Guard Clause Phase below is different in kind from the scope-confirmation checkpoint later in Step 1: the guard clauses are a hard stop that runs on *every* request regardless of type, before any classification or drafting happens. The Step 1 confirmation is a softer courtesy check that only applies to full-package runs. Don't conflate the two — a request can clear the guard clauses fine and still warrant a scope confirmation later.

## Fallback Definition

**Fall back to direct answering.** Whenever a guard clause below fails, that means: stop the skill's content-generation workflow entirely — don't classify the request, don't draft anything, don't produce a deliverable — and just respond to the user in plain conversation instead, the way you would if this skill didn't exist. Both guard clauses point back to this same definition; what differs between them is only what you actually say in that direct answer:

- If it's Guard Clause 1 that failed (no real source material), the direct answer is: explain that this skill works from source material the user provides, not from a topic alone, and ask them to paste, attach, or link what they want turned into content.
- If it's Guard Clause 2 that failed (not actually a LinkedIn ask), the direct answer is: say plainly that this isn't something this skill covers, briefly name what it does cover, and then either answer the user's underlying question directly or point them to the right tool (e.g. the `docx` skill for a plain Word report).

In neither case do you invent LinkedIn content to satisfy the request — falling back to direct answering is the whole point of the guard failing.

## Step 0 — Guard Clause Phase (always run this first, every time)

Two conditions gate everything else in this skill. Check both on every request, no matter how confident or familiar it feels — a request that seems obviously in-scope can still fail one of these. If either check fails, stop immediately: do not classify the request, do not draft anything, do not proceed to Step 1. Use the Fallback Definition above instead.

**Guard Clause 1 — Is real source material actually present?**

Check: has the user pasted text, attached a file, or linked a GitHub/Google Drive file with actual content — not just named a topic or asked for a post about something in general?

- If YES → continue to Guard Clause 2.
- If NO → **fall back to direct answering**, per the Fallback Definition's Guard Clause 1 case above. Do not fill the gap yourself with an idea, example, statistic, or anecdote of your own — that's the one thing this skill must never do, even if the ask is short or the user seems to want something quick.

**Guard Clause 2 — Is this actually a LinkedIn post/article request?**

Check: is the user asking for LinkedIn content specifically — either stated directly ("LinkedIn post," "LinkedIn article," "content package"), or through a clear implicit signal like "share this professionally" or "build my profile" — as opposed to commenting strategy, connection-request messaging, a different platform (X/Twitter, a blog, a newsletter), or a generic "make this a post" with no platform in view at all?

- If YES → continue to Step 1.
- If NO → **fall back to direct answering**, per the Fallback Definition's Guard Clause 2 case above.

Source material, when Guard Clause 1 passes, can take any of these forms:
- Raw text pasted directly into the conversation
- An attached file (notes, transcript, doc)
- A GitHub file/repo pulled via connector
- A Google Drive file pulled via connector

If the source material technically exists but is thin or ambiguous in a spot that would require inventing a detail (a number, an outcome, a cause) to draft anything usable, that's not a guard-clause failure — both checks passed — but it does mean pausing in Step 1 to ask for more detail before drafting, rather than guessing.

## Step 1 — Classify the request and confirm scope

Once source material is identified, classify what's actually being asked before running the full workflow:

| Request type | What to produce |
|---|---|
| **Article only** | Just the long-form LinkedIn Article, per the reference brief's Article guidance. |
| **Post(s) only** | Just the relevant short-form post(s) — no Article, no full package. |
| **Full package** ("content package," "turn this into LinkedIn content," or anything not scoped down to just one piece) | The complete deliverable: Article + posts associated with the Article + independent posts + hashtags + distribution notes, per the reference brief's Output Structure and Final Output Format. |
| **Anything outside LinkedIn content from user material** (commenting strategy, connection-request messages, or a topic not derived from supplied material) | Out of scope for this skill — fall back to answering directly, or say plainly that this isn't something this skill covers. |

For a **full package** run specifically, briefly confirm with the user before executing: what source material you're using, and that you're producing the complete package (Article + associated posts + independent posts + hashtags + distribution notes) as a single .docx. This is a longer, harder-to-redo piece of work than a single post, so a quick confirmation up front saves a full rewrite later. For an Article-only or Post-only request, you can generally proceed directly — the scope is already clear from the request.

## Step 2 — Draft the content

Read `references/content-strategist-prompt.md` in full and follow it exactly: the Role, the Non-Negotiable Operating Constraints (especially algorithm claims must be verified via search, never invented — see Constraint 2), the Voice, the Output Structure, and the SEO/keyword guidance. That file is the actual content specification; nothing here overrides it.

A few points worth surfacing explicitly because they're easy to miss on a skim:

- **Verify algorithm claims live.** Any recommendation about formatting, dwell time, posting cadence, hashtag counts, or content-type ranking must be checked against current, searchable information before it goes in the distribution notes — not written from memory or general "growth hacker" convention. If something can't be verified, say so explicitly in the notes rather than stating it as fact.
- **Article + posts are one interconnected system**, not separate deliverables — sequencing and cross-references between them should reflect that.
- **LinkedIn-ready formatting inside each piece of content**: no Markdown syntax (no `#`, `**`, `-` bullets) inside the Article or post text itself, since LinkedIn's editor doesn't render Markdown. Use line breaks, plain-text numbering ("1.", "2."), and capitalization for emphasis instead. Word document headings (for organizing the doc itself, e.g. "Article," "Post 3") are the one place normal Word heading styles are fine, since those aren't meant to be pasted into LinkedIn.

## Step 3 — Assemble the deliverable

The final output for an Article-only or Post-only request can be delivered inline in the conversation if the user just wants the text, or as a .docx if they'd clearly prefer something to save/edit — use judgment or ask if unclear.

For a **full package**, the deliverable is always a single Word (.docx) document (never scattered messages or multiple files), organized with clear section headings so each piece is easy to find and edit independently:
1. Article
2. Posts Associated With the Article
3. Independent Posts
4. Hashtags (per piece)
5. Distribution Notes & Suggestions

Consult `/mnt/skills/public/docx/SKILL.md` for how to actually build the Word document — it covers formatting, headings, and output conventions for this environment. Once the .docx is built, share it with `present_files` so the user can open and edit it.

## If execution fails partway through

If you're unable to complete the workflow as specified (source material turns out to be unusable, a required piece can't be produced, etc.), don't silently produce a partial or degraded result. Tell the user what went wrong and ask whether they'd like a direct answer to their underlying question instead of the full skill workflow.

## Testing this skill

This is relevant only when validating or iterating on the skill itself, not during normal use — skip it entirely for real content-generation requests. A bundled test suite (trigger tests + functional tests + sample source files) lives in `tests/`; see `tests/README.md` for what it covers and how to run it.
