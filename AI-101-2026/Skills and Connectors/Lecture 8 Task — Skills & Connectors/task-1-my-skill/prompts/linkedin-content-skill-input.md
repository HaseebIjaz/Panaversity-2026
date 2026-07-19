# Skill Input: `linkedin-content-generator`

## 1. Description

1. Trigger only for explicit or implicit requests to turn user-provided source material (pasted text, an attached file, a GitHub file/repo via connector, or a Google Drive file via connector) into a LinkedIn Article, associated posts, independent posts, and distribution notes, compiled into a single editable Word document, per the attached LinkedIn Agentic AI Content Strategist Prompt.
2. Never trigger for LinkedIn commenting strategy, connection-request messaging, or generating content ideas that do not originate from user-supplied source material.
3. Proceed only if the request is within the scope of the attached prompt: LinkedIn content (Article/posts) built from real source material and positioned around the user's Agentic AI Developer brand.

## Fallback Definition

Fall back to direct answering

## Guard Clause 1

## Guard Clause 2

## 2. Request Classification

| **Request Type**                                               | **Response Behavior**                                                                                              |
| -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **LinkedIn Article Request**                                   | Generate **only** the relevant LinkedIn article by following the given skill instructions.                         |
| **LinkedIn Post Request**                                      | Generate **only** the relevant LinkedIn post by following the given skill instructions.                            |
| **LinkedIn Article + Post Request + Associated Posts Package** | Generate the **complete package** (article, post, and associated posts) by following the given skill instructions. |
| **Another Request**                                            | If the request is not relevant to the LinkedIn skill, **fall back to direct answering**.                           |

## 3. Attached File

`linkedin-agentic-ai-content-strategist-prompt.md` — this is the full skill body (Role, Constraints, Inputs, Output Structure, Final Output Format, SEO, Deliverable Checklist). Use it as-is as the SKILL.md content; do not rewrite its substance.

## 4. Directions for skill-creator

1. Ask a clarifying question if the request is ambiguous — especially if no source material is identifiable, since this skill must never originate its own ideas.
2. Confirm with the user (source material + full-workflow scope) before executing the workflow.
3. In case you fail to execute the instruction, prompt the user about it and ask him if he wants a direct answer to his query instead of executing the skill.

## 5. Write Tests for the Skill

We need to write and unit tests to the /linkedin-content-generator to test the following atleast but not limited to :

1. Skill Triggers (Narrow and Broad) Tests

2. Skill Negative Triggers Test

3. Inside and Outside Scope Tests

4. Request Type Tests

5. Instruction execution tests

6. Happy Path tests

7. Sad Path tests

8. Failure Tests

9. Error Tests

10. Output Tests

11. Bad Input tests

Once drafted:

Write a test suite covering trigger tests (broad/narrow/negative/scope/request-type) and functional tests (happy path, sad path, failure, error, output, bad input). Save it inside the skill itself in a folder called tests/ — not evals/, since that name gets silently excluded by the packaging script. Reference /mnt/skills/examples/skill-creator/references/schemas.md for the eval schema.
Build an actual runner, not just JSON test files. Since I'm on claude.ai without subagents, you can't spawn a blind grader — so tell me explicitly which parts of this are actually automatable here versus which parts require a human or a fresh conversation, and script whatever is automatable (e.g., a Python script that runs each functional test's file inputs through whatever's scriptable, checks structural assertions like "is there one .docx," "are there 5 headings," "does the text contain Markdown symbols" programmatically instead of by eyeballing it).
Actually execute every functional test yourself, end to end, in this conversation — real files in, real .docx out — before telling me it's done. Don't describe what the output would probably look like; produce it.
For the trigger tests specifically, tell me directly that you cannot self-grade these, since you'd be grading a description you wrote against answers you also wrote. Don't present your own judgment as if it were a test result. Give me the exact mechanism for getting a real, unbiased answer (fresh conversation, subagent, or the Anthropic API called from an artifact) and treat that as a required step, not optional.
