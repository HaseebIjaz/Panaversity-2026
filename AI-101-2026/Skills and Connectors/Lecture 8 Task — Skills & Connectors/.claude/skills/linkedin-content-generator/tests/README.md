# Test suite for linkedin-content-generator

This directory is for validating the skill itself — it is not part of the skill's runtime behavior and is never read while the skill is actually generating content for a user.

## Contents

- `trigger-tests.json` — 17 tests checking whether the skill correctly fires (or correctly doesn't) for a given prompt, evaluated against the frontmatter `description` only. Categories: narrow triggers, broad/implicit triggers, negative triggers, in/out-of-scope near-misses, request-type classification (article-only / post-only / full-package / ambiguous).
- `functional-tests.json` — 16 tests that require actually running the skill end-to-end and grading the real output against assertions. Categories: instruction execution (constraint compliance), happy path, sad path, failure handling, error handling, output structure, bad input handling.
- `files/` — sample source material referenced by the functional tests (thin notes, mixed-relevance notes, a corrupted attachment, an oversized dump, non-English notes, etc.) so the functional tests are runnable as-is rather than hypothetical.

## How to actually run these

**Primary path: the `/test-skill` command.** If you have `test-skill.md` installed at `~/.claude/commands/test-skill.md` (a personal, global Claude Code command — not bundled in this skill, since it's reusable infrastructure meant to work across every skill you build, not just this one), run:

```
/test-skill linkedin-content-generator
```

`test-skill.md` is the single source of truth for exactly how these tests get executed (subagent isolation, orchestration, reporting) — this README doesn't restate that procedure, so if you're wondering how a test case actually runs, read `test-skill.md`, not here. If you don't have the command installed yet, ask Claude Code to create it: a personal command at `~/.claude/commands/test-skill.md` that takes a skill name as `$ARGUMENTS` and runs this skill's `tests/` suite.

**Manual fallback, if you don't want to install the command:** Trigger tests need a judge that hasn't seen the expected answers — a fresh Claude instance with this skill available. Paste each `query` in as if it were a real user message, observe whether the skill gets consulted, and compare to `should_trigger`. Grading these from inside the same conversation where the skill was authored isn't a real test — the grader already knows the answer key. Functional tests need real execution: follow SKILL.md exactly as written for the given `prompt` (with the listed `files` as input), produce the actual output, then check it against `expectations`.

For a fully automated version with benchmarking and an HTML review viewer, use Claude Code's skill-creator plugin directly (`/plugin install skill-creator@claude-plugins-official`) against this directory, adjusting field names to match `references/schemas.md` if needed since these were authored by hand.

## Updating

If SKILL.md's triggering logic or workflow changes, revisit these tests — particularly `trigger-tests.json`, since it's evaluated against the literal description text and will drift out of sync silently if the description changes without the tests being re-checked.
