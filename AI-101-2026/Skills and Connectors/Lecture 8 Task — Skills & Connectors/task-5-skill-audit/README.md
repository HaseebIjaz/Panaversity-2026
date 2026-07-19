## 🔍 Skill Security Checklist — `linkedin-content-generator`

✅ **No hardcoded external servers** — no URLs, endpoints, or webhooks baked in

✅ **No credential handling** — zero mention of passwords, tokens, API keys, or auth

✅ **No data exfiltration paths** — nothing sends, uploads, or posts your data anywhere

✅ **No auto-publishing** — output is a local .docx you paste into LinkedIn yourself

✅ **No executable code** — Markdown and JSON only; no scripts, binaries, or eval/exec patterns

✅ **No hidden instructions** — no prompt injections or attempts to override my guidelines

✅ **Network use is user-initiated only** — web search (to verify algorithm claims) and GitHub/Drive fetches happen only when _you_ provide a link

✅ **Conservative guardrails** — refuses to invent content or fabricate stats; asks you instead

⚠️ **One minor note** — the tests README suggests a human optionally install a Claude Code plugin for automated testing; it's an instruction to you, never executed by the skill

---

## 🏁 Verdict

🟢 **CLEAN — Safe to use.** Your data stays between you and the document it produces.
