# Control panel — one live view of every Atelier project

Standing requirement: Phase 4, the one-stop front. A single dashboard that shows **every project the factory is running** at a glance — its stage, its gates, its health, its maintenance and growth status — so the user never has to open each project to know where things stand. Built by `/pf-board`. Free; and it updates **without re-asking permission every time**.

## What it shows (across all projects under the Atelier folder)
A factory-wide summary line, then a row/card per project:
- **Project** — name + methodology (ship-it / agile / kanban) + a data-sensitivity flag.
- **Stage** — the furthest point reached: Plan → Design → Build → Deploy → Live (from `gates` + `deploy.live_url`).
- **Gates** — plan / design / build / deploy: pending or approved, and what it is waiting on.
- **Lanes** — n merged / n total (from `lanes`), or "solo".
- **Live** — the `live_url` and its health: up / down / unknown (from `monitoring` + the last health check).
- **Handoff** — mode A (local) or B (cloud).
- **Maintenance** — last run, backups in place, restore tested (from `maintenance`).
- **Growth** — last growth report (from `growth`).
- **Needs you** — anything waiting on a human gate or a review, or empty.
Summary: total projects · n live · n healthy / n with an issue · n waiting on you.

## How it stays live without re-asking permission (the artifact rule again)
The panel is a **published Artifact with a shared database** (the `db` capability; or the Dashboard artifact type). It is **published once** (one approval). Every refresh **writes rows to its database** (ArtifactData / write_db), **never republishes the page** — so keeping it current never re-prompts a page-update approval. The page renders live from the db. `/pf-board` upserts those rows from each project's `factory.json` + `lanes/<lane>.json`.

## db schema (the `projects` collection, one document per slug)
`slug`, `name`, `methodology`, `data_sensitivity`, `stage`, `gates` (plan/design/build/deploy), `lanes` (merged/total or "solo"), `live_url`, `health` (up/down/unknown), `handoff_mode`, `maintenance` (last_run / backups / restore_tested), `growth` (last_run), `needs` (what is waiting on the user, or empty), `updated`. A `meta/summary` document holds the factory-wide counts.

## Rules
- **No secrets, no personal data on the panel** — URLs, statuses and counts only; never an env value, token or customer record (ties to `security.md` / `compliance.md`).
- **Free** — a published Artifact costs nothing; no new service.
- **Read-only mirror** — the panel reflects state; it does **not** change any project. Acting on a project is still done through that project's `/pf-*` skills and their gates.
- **Safe to schedule** — a refresh only reads project state and writes the panel db; it never deploys, merges or changes a project.

## How it is invoked
`/pf-board` — create the panel if it does not exist (publish once), then refresh every project's row from disk and open it. `/pf-board --schedule daily` sets a refresh cadence. `--check` prints the summary in chat without opening the panel.
