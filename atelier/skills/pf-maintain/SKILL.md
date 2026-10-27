---
name: pf-maintain
description: "Phase-3 production-support stage: keeps a live product patched, secure, within its contracts, and recoverable. Each run checks dependencies and security advisories, re-runs the contracts on the live site, checks certs and host limits, verifies backups and periodically tests a restore, then opens a maintenance PR (never auto-merged for data-sensitive projects). Can run on a schedule the user approves. Use when the user says /pf-maintain, 'maintain the site', 'keep it patched', 'production support', 'update dependencies', 'check the backups', or 'set up weekly maintenance'. Supports --schedule, --check, --dry-run. Never auto-deploys a sensitive project and never runs the pentest."
---

# /pf-maintain <slug> [--schedule weekly|monthly] [--check] [--dry-run]

Keep a live product healthy over time — the factory as production support. Read first:
- `${CLAUDE_PLUGIN_ROOT}/references/maintenance.md` (this stage's contract, incl. backups & restore)
- `${CLAUDE_PLUGIN_ROOT}/references/security.md`, `performance-budget.md`, `seo-ai-visibility.md` (the contracts it re-checks)
- `${CLAUDE_PLUGIN_ROOT}/references/cost-posture.md` (spend watch), `recommendations.md` (any option it surfaces), `state-schema.md`

## 0. Flags
`--schedule weekly|monthly`: set/confirm the recurring schedule (via the scheduled-task tools; the user approves) and stop. `--check`: report last run, what is pending, backup/restore status, **secrets due for rotation, and the latest spend-vs-forecast reading**; stop. `--dry-run`: print what it would do; change nothing; stop.

## 1. Gate
Locate the project; read `factory.json`. Require `deploy.live_url` (something is live to maintain). Seat = `pm_lane`.

## 2. The pass (per `maintenance.md` A, on a `maintenance/<date>` branch)
Dependencies + advisories (`npm outdated`/`audit`, `osv-scanner`) → apply safe patch/minor updates, hold majors with a note; a light `/pf-harden` re-check for drift (perf/SEO/security/a11y); certs + host limits; backups healthy + periodic restore drill (step 4). Open **one** `maintenance/<date>` PR with everything.

## 3. Merge policy (`maintenance.md` A5)
`data_sensitivity: high` → the PR **waits for the user's review + merge**, then the normal deploy (auto-rollback applies). Low-stakes site → if the user pre-authorized, auto-merge only **safe** updates (patch/minor, green tests); majors and any contract failure always wait. **Never auto-deploy a sensitive project.**

## 4. Backups & restore (`maintenance.md` C)
Confirm code is on GitHub (authoritative) and data backups ran (Supabase daily; the Blob dump if set up). Periodically (and on `--check`) run a **restore drill**: restore the latest backup into a scratch DB and verify it loads — report pass/fail. If no off-Supabase / longer-retention backup exists and the project's data warrants it, recommend `/pf-setup backup` (free `pg_dump` → Azure Blob). **Never back up a secret.**

## 4b. Secret hygiene & rotation (`maintenance.md` E)
Read `maintenance.secret_rotation` (names + last-rotated dates only — **never values**). Flag any secret past its cadence (tokens 90d, DB keys 180d, shorter for `data_sensitivity: high`) and any to retire now (a leave/leak/over-scope event the user mentions). For each due secret, **guide** the rotation: open the provider's key page in Chrome, tell the user exactly which key to regenerate and the scope, wait while **the user** generates it, update the env var **by name** (prefill the name, never the value), verify the new key with a health check, then have the old one revoked. Record the new date in `maintenance.secret_rotation`. Claude never types, pastes, stores or reads a secret value.

## 4c. Spend vs forecast (`maintenance.md` F)
Per provider the project uses: read the real month-to-date bill / free-tier usage — via the Azure cost tools where available, else open the provider's billing page in Chrome and read it (no payment method needed to read). Compare to `planning.budget_forecast`, to $0, and to each free-tier limit; flag anything over ~80% of a free limit or above the forecast. **Recommend-only** — report the number and the cheapest option that still clears the quality/security bar (`cost-posture.md`, `recommendations.md`); never downgrade the product to dodge a bill and never create/change anything billable without a yes. Record in `maintenance.spend` (numbers + date, no payment details).

## 5. Schedule (`maintenance.md` B)
On `--schedule`, create the recurring task (the scheduled-task tools) scoped to run `/pf-maintain` for this project; confirm the cadence with the user. A scheduled run **proposes** (PR) + alerts; it never deploys/merges a sensitive project and never runs the pentest. The user can change/stop it anytime.

## 6. Record
Write `factory.json.maintenance` (`schedule`, `last_run`, `backups`, `restore_tested`, `open_pr`, `secret_rotation`, `spend`); `log {stage:"maintain", event:"<summary>"}`. Report what it found, the PR link, the backup/restore status, any secrets due for rotation, and the spend-vs-forecast reading.

## Never
- Auto-deploy or auto-merge a `data_sensitivity: high` project — it proposes, the user merges.
- Run the pentest, or schedule anything that deploys without the go-live yes.
- Roll back or auto-revert a database; back up or print a secret.
- Type, paste, read or store a secret value during rotation — the env-var **name** only; never revoke the old key before the new one is verified live.
- Downgrade the product or create/change anything billable to act on a spend alert — spend findings are recommend-only (price + yes).
- Recommend a paid tier unless the project's real recovery/scale needs force it (price + yes).
