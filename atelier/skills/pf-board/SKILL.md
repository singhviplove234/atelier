---
name: pf-board
description: "The factory control panel: one live dashboard showing every Atelier project at a glance — its stage, gates, lanes, live URL and health, handoff mode, maintenance and growth status, and what's waiting on you. Built as a published artifact with a shared database so it refreshes by writing data rows, never by republishing (no repeated update prompts). Use when the user says /pf-board, 'show all my projects', 'the control panel', 'factory status', 'what's the state of everything', or 'where does each project stand'. Supports --schedule and --check. Read-only: it mirrors state, it never changes a project."
---

# /pf-board [--schedule daily|weekly] [--check]

One live view of every project the factory is running. Read first:
- `${CLAUDE_PLUGIN_ROOT}/references/control-panel.md` (what it shows + the db schema + the update rule)
- `${CLAUDE_PLUGIN_ROOT}/references/state-schema.md` (the per-project state it reads)

Load the `artifact-capabilities` skill before creating the panel (for the `db` capability).

## 0. Flags
`--check`: print the factory-wide summary + a one-line-per-project status in chat; do not open the panel; stop. `--schedule daily|weekly`: set a refresh cadence and stop.

## 1. Gather
List every project: each `factory.json` under the connected `Atelier` folder. For each, read `factory.json` (+ `lanes/<lane>.json`) and compute its row per `control-panel.md`: stage, gates, lanes merged/total, `live_url` + health (from `monitoring` + a quick health check if live), handoff mode, maintenance, growth, and **needs** (any pending human gate or open review). Compute the summary counts.

## 2. Create or find the panel
Find it: Artifact `list` for the title **"Atelier — Control Panel"**. If absent, create it per `control-panel.md` — a **published Artifact with the `db` capability** (or the Dashboard type): a page that renders the `projects` collection as a status table / cards with a summary header, coloured by health and gate state. **Publish once** (one approval). Put nothing secret on it.

## 3. Refresh (db writes, never republish)
Upsert one document per project into the db `projects` collection and the `meta/summary` doc (ArtifactData / write_db) — a **data update, not a page republish**, so it does not re-prompt the page-update approval. The page shows the new state live.

## 4. Show
Open the panel for the user (Artifact `open`) and give a one-line chat summary (e.g. "4 projects · 2 live and healthy · 1 waiting on your deploy yes · 1 in build"). On `--check`, give only the chat summary.

## 5. Schedule (optional)
On `--schedule`, create a recurring task to run `/pf-board` refresh; it only reads project state and writes the panel db, so it is safe to schedule and never changes a project.

## Never
- Put a secret, token or personal record on the panel — statuses, URLs and counts only.
- Change any project from the panel — it mirrors; acting on a project goes through that project's skill and its gates.
- Republish the page to update data — always write the **db** instead.
