---
description: Run the bundled test suite for a specified skill, using one isolated subagent per test case, and produce a report
argument-hint: [skill-name-or-path]
allowed-tools: Bash, Read, Write, Task
---

Run the test suite for the skill: $ARGUMENTS

This command is generic — it does not assume any particular skill's file layout, test filenames, or test count. It works against any skill that bundles a `tests/` folder (not `evals/` — that name gets excluded from packaging, so skills use `tests/` for bundled test suites). What it is strict about, regardless of which skill you point it at, is the multiagent execution model and producing a real report at the end.

## Step 1 — Locate and discover, generically

1. Locate the skill directory matching $ARGUMENTS (check project skills, `~/.claude/skills/`, or the path if given directly).
2. Look inside its `tests/` folder. If a `README.md` is present there, read it for context on what the tests cover — but don't assume one exists or that it's named exactly that.
3. Discover every test-definition file in `tests/` yourself (e.g. any `.json` files present) rather than expecting specific filenames. Read each one and classify what kind of test each individual entry is from its own structure, not from the filename:
   - An entry with a `should_trigger` field is a **trigger test**: it checks whether the skill would be consulted for a given query, judged against the skill's frontmatter description alone.
   - An entry with an `expectations` field (and typically a `prompt` and optionally `files`) is a **functional test**: it requires actually executing the skill and checking the real output against those expectations.
   - If you find an entry that doesn't clearly match either shape, don't guess — note it as unclassifiable in the final report rather than silently skipping it or forcing it into one of the two categories.
4. Any other files under `tests/` (sample source material, fixtures) are inputs the functional tests may reference — read them as needed, don't treat them as test cases themselves.

## Step 2 — The multiagent execution model (this part is strict, not generic)

You (the agent running this command) are the **orchestrating agent**, not a test runner. You never execute a test case yourself and you never grade one yourself. Every individual test case you discovered in Step 1 — regardless of how many files it came from or how many total cases there are — gets its own separate subagent, spawned individually via the Task tool. One subagent per test case, run as an independent, isolated agent with no shared context and no visibility into any other test case, any other subagent, or this orchestrating session. Each subagent does its one job and reports its result back to you; your job is to spawn all of them, collect every result as it comes back, and only then aggregate. Do not batch multiple test cases into a single subagent call, and do not answer for a subagent yourself even when the answer feels obvious — the isolation is the entire point, not an implementation detail.

- **For a trigger test entry**: the subagent receives ONLY that entry's query and the skill's frontmatter description — not this command, not the expected `should_trigger` value, not any other context from this session, and not any other subagent's query or result. It answers whether it would consult the skill for that query and why. You compare its answer against the expected value yourself afterward — the subagent stays blind to the expected answer the whole time, but you are not.
- **For a functional test entry**: the subagent receives the skill and that entry's `prompt` plus any referenced `files`, and actually executes the skill end to end — real files in, real output produced, no shortcuts. You grade the returned output against that entry's `expectations` yourself afterward, or delegate grading to a further isolated subagent for an extra layer of blindness — either way, grading happens after the subagent reports back, not inside it.

Do not grade any test yourself using your own judgment in place of a subagent's actual execution, and do not let one subagent see another's results.

## Step 3 — Produce a report

Once every subagent has reported back, write an actual report file to disk — don't just summarize in chat and stop there. Ask the user where they want it saved before writing it — this is a cheap question, so ask it upfront (before spawning subagents) rather than making them wait through the whole run first. Offer exactly these two options rather than picking one yourself:

1. **Current directory** — wherever this command is being run from, e.g. `./test-reports/<skill-name>-<YYYY-MM-DD-HHMM>.md`. Makes sense for a one-off check tied to whatever project/session you're in right now.
2. **Global location** — `~/.claude/test-reports/<skill-name>/<YYYY-MM-DD-HHMM>.md`. Makes sense if you want a running history of test runs for a skill that persists across projects and sessions, independent of where you happened to invoke the command from.

Create the destination folder if it doesn't exist, whichever the user picks. The report must include:

1. A summary line: total test cases run, pass count, fail count, and any unclassifiable entries from Step 1.
2. A pass/fail breakdown grouped by whatever categories the test data itself specifies (if entries have a `category` field, group by that; otherwise group by trigger vs. functional).
3. For every failure: which specific test case failed, what was expected, what actually happened, and why it counts as a failure — not just a pass/fail mark.
4. The skill name, the timestamp, and how many subagents were spawned in total, as a record of what this run actually covered.

After writing the file, present it to the user (e.g. via present_files if available) and give a short plain-language summary in chat — don't make the user open the file to learn whether the run passed or failed.
