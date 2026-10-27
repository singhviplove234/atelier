---
name: find-skill
description: Search a bundled catalogue of ~17,800 Claude skills (Anthropic, skills.sh, Vercel, VoltAgent, ComposioHQ and other curated lists), ranked by source trust and GitHub stars, and install the one the user picks. Use when the user asks to find, search for, discover, recommend, or install a skill ("is there a skill for Docker?", "find me a PDF skill", "show top skills", "install this skill from GitHub"), or pastes a GitHub / skills.sh link to a skill. Works in Claude Code, Cowork and claude.ai chats.
---

# Find Skill

Finds skills in a catalogue bundled with this skill, then installs the user's choice. Adapted from [fockus/claude-skill-find-skill](https://github.com/fockus/claude-skill-find-skill) (MIT, see `LICENSE`) to run anywhere, not only in Claude Code.

This file's folder is the **skill directory**. Run the scripts below from it, e.g. `python scripts/search.py ...` (use `python3` if `python` is missing). Everything is found relative to the scripts, so no setup is needed.

## 1. Understand the request

- A search: pull out the key words. If the request is vague ("a skill for work"), ask one question about the task or tool first.
- A direct link or `owner/repo` the user wants installed: skip to step 4.

## 2. Search

```bash
python scripts/search.py <words...> [--limit 5] [--page N] [--all] [--source NAME]
python scripts/search.py --top 20      # most-starred skills overall
python scripts/search.py --stats       # counts by source, catalogue date
```

Every word must match (name, description or tags). If nothing comes back, retry with fewer or broader words and synonyms (e.g. `excel` then `spreadsheet` then `xlsx`) before saying none exist.

## 3. Show results

Up to 5 results as a numbered list; 6 or more as a table. For each: **name**, source and trust level, stars (if known), a one-line description, and the URL. Mark the best match as recommended and say why. Put Official and Curated sources above Community ones.

- **skills.sh** entries have placeholder descriptions ("X — skill from owner/repo"). If the user is interested in one, read its real description before recommending it: download and read its `SKILL.md` (step 4 prints it) or open the URL.
- Flag risk plainly: skills run with the agent's permissions, and Community or unknown sources are unreviewed.

End with: which one(s) to install, or none. **Never install without the user's explicit choice.**

## 4. Install

First, work out where you are running:

### A. Claude Code on the user's own machine
(You can run shell commands on their computer and `~/.claude/` exists.)

```bash
python scripts/package_skill.py <url or owner/repo> --out <temp dir>
```
Then unzip the result into `~/.claude/skills/` (user-wide) or `<project>/.claude/skills/` (this project only; ask if unclear). Tell them to start a new session to load it.

### B. Cowork or a claude.ai chat
Skills can't be installed into the user's account from here, so build a zip they upload.

```bash
python scripts/package_skill.py <url or owner/repo> --out <outputs folder>
```
Use the session's outputs / shareable-files folder so the user can download the zip. Then tell them:
1. Download `<name>.zip`.
2. In the Claude app go to **Settings → Capabilities → Skills → Upload skill** and choose the zip.
3. Start a new chat or Cowork session to use it.

### Packager notes
- Accepts GitHub repo links, `/tree/<branch>/<path>` links, `owner/repo`, and `skills.sh/<owner>/<repo>/<skill>` or `officialskills.sh/...` links. For other sites, find the GitHub repo first.
- If it prints `MULTIPLE_OR_NO_MATCH` with a list, the repo holds several skills: pick the one matching the user's choice and re-run with `--path '<dir>'`.
- If it prints `DOWNLOAD FAILED`, this environment has no internet access. Give the user the GitHub link and these steps: download the repo as ZIP, keep only the folder containing `SKILL.md`, zip that folder, and upload it as in B.
- If it says there is no `SKILL.md`, it's not a Claude skill (often an awesome-list or an MCP server). Say so and suggest the closest real skill.
- After packaging, show the printed description and say in one line what the skill will do, so the user knows what they're adding.

## Catalogue freshness

The catalogue is a snapshot (see `catalogue_updated_at` in any search result). If it's more than a couple of months old, mention that newer skills may be missing. Refreshing needs the full upstream tool: run its `update-skills-catalogue.sh` in Claude Code, then `python scripts/build_catalogue.py <its catalogue.json>` and re-upload this skill.
