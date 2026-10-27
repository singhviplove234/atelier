---
name: pf-bootstrap
description: "One-time, once-per-Claude-account setup that makes Atelier fully equipped: it checks which of the recommended helper skills are already present, then uses the bundled find-skill to install the missing ones from their official sources (with your go-ahead). Run automatically on the first /pf-setup, or on demand. Use when the user says /pf-bootstrap, 'set up atelier's skills', 'install the recommended skills', 'first-run setup', or 'make sure atelier has everything'. Idempotent — safe to re-run; it only installs what's missing."
---

# /pf-bootstrap

Make this Claude account fully equipped for Atelier. Atelier **bundles** three
permissively-licensed skills (`find-skill`, `humanizer`, `design-md`) so they
are always present. A handful of other helper
skills can't be redistributed (Anthropic's are proprietary; some ship with no
license), so instead of copying them, this step **installs them from their
official sources** onto your account, once. After it runs, Atelier knows how
and when to use all of them (`${CLAUDE_PLUGIN_ROOT}/references/skill-catalog.md`).

Read first:
- `${CLAUDE_PLUGIN_ROOT}/references/skill-catalog.md` (the full list + what each is for)
- the bundled `find-skill` skill (this does the searching + installing)

## 0. Run-once marker
The marker lives at `<Atelier folder>/.atelier/bootstrap.json` (names + date only, no secrets). On start:
- If it exists and lists every recommended skill as present, say "Atelier is already set up on this account — all recommended skills are installed." and stop (unless the user passed `--recheck`).
- Otherwise continue. The marker makes this safe to re-run: it only ever installs what is missing.

## 1. Take stock
List the skills available in this session. For each entry in `skill-catalog.md`, mark it:
- **bundled** — `find-skill`, `humanizer`, `design-md` → always present, nothing to do.
- **built-in** — `docs`, `docx`, `pdf`, `pptx`, `/code-review`, `/security-review` → present in Claude already, nothing to install.
- **present** — already installed on this account.
- **missing** — a recommended skill not yet available → candidate to install.

## 2. Show the plan and get one go-ahead
List the **missing** skills in one place, each with a one-line "what it's for" from the catalog, grouped by tier:
- **Core factory helpers** (strongly recommended): `tech-doc-audit`, `swot-analysis`, `llmcouncil`.
- **Design polish** (optional): `impeccable`, `emil-design-eng`, `design-taste-frontend`, `high-end-visual-design`, `minimalist-ui`, `industrial-brutalist-ui`, `gpt-taste`, `stitch-design-taste`, `redesign-existing-projects`, `animate`, `improve-animations`, `animation-performance`, `animated-ui-libraries`.
- **Copy & brand** (optional): `remove-ai-marks`, `brandkit`.
- **Build discipline** (optional, Claude Code): `superpowers`.

Then ask **once** with AskUserQuestion: install **all** missing, **core only**, or **none/choose**. This single batched confirmation is the explicit user choice `find-skill` requires; never install a skill without it.

## 3. Install the chosen set (via the bundled find-skill)
For each chosen skill, use the bundled `find-skill` to locate it from an **official or curated source** and install it the way `find-skill` describes for this surface:
- **Claude Code on the user's machine** — `find-skill` packages the skill and unzips it into `~/.claude/skills/`; tell the user to start a new session to load the new skills.
- **Cowork / claude.ai chat** — skills can't be installed into the account from here, so `find-skill` packages each as a zip in the outputs folder; give the user the list and the steps (Settings → Capabilities → Skills → Upload skill → pick each zip → start a new session). Deliver the zips with the file tool.

Prefer the **official** source for each (Anthropic's skills from Anthropic's own skill source; community skills from the author's repo). If `find-skill` finds only a community mirror for something, say so and let the user decide. If a download fails (no network), hand the user the official link and the manual upload steps rather than guessing. Never type a credential; installing a skill needs none.

## 4. Record and report
Write `<Atelier folder>/.atelier/bootstrap.json`: `{ "ran": "<date>", "account_hint": "<non-identifying>", "installed": [...], "bundled": [...], "skipped": [...] }` — names and dates only. Report what is now installed, what the user still needs to upload (Cowork case) and the one action to finish (start a new session), and point to `skill-catalog.md` for how each is used. A new session (or upload) is required before the freshly-installed skills are callable.

## Never
- Copy a skill's files into Atelier or into this repo — installation always pulls from the skill's **own official source**; Atelier redistributes only the three bundled skills whose licenses allow it.
- Install anything without the single batched user go-ahead in step 2.
- Install a skill whose only source is an unknown/untrusted mirror without flagging the risk and getting a yes.
- Claim a skill is installed before a new session has loaded it; say the session restart (or upload) is still needed.
- Store anything identifying or any secret in the marker file.
