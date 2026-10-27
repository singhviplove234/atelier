# Atelier Builder (Claude Code plugin) — v3

The Claude Code half of the factory. The Cowork `atelier` plugin writes a request file into the project folder and types `/pf-next` into this session through Chrome (or you type it); this plugin runs that one request and writes a result file back. It never runs on a timer and never acts on its own — the trigger is always a typed command.

| Skill | Triggered by | Does |
|---|---|---|
| `pf-next` | `/pf-next [--lane x] [--go]` | Finds the newest pending request (`BUILD-REQUEST-<lane>.md` / `MERGE-REQUEST-<lane>.md` / `DEPLOY-REQUEST.md` / `HARDEN-REQUEST.md` / `PENTEST-REQUEST.md`) and runs the matching skill. `--go` skips the confirm (Cowork passes it after your approval) |
| `pf-build-from-spec` | via `/pf-next` | Builds the lane: Next.js + Tailwind + shadcn from `SPEC-<lane>.md` — tokens, screens with exact copy, Supabase when present — then gates the build on all six contracts (performance, SEO + AI visibility, security, simplicity, design, compliance) before it passes. Solo → push `main`; team lane → `lane/<x>` + PR |
| `pf-deploy-from-spec` | via `/pf-next` | Deploys `main` to the target in `DEPLOY-REQUEST.md`, following that target's file in the registry; **builds locally only and creates only free resources** (a paid step stops for your decision); records a rollback point, runs the health check + bake, **auto-rolls-back a bad deploy** (app only, never the DB); writes `DEPLOY-RESULT.md` |
| `pf-harden-from-spec` | via `/pf-next` | Runs the passes in `HARDEN-REQUEST.md` (safety-net tests, perf budget on the live site, SEO + AI visibility, defensive security, DB indexes, free-layer caching, local k6 load test, hosting-limits) on a `harden/<date>` branch, one commit per fix, opens a PR, writes `HARDEN-RESULT.md`; k6 only against a local copy; **never creates a billed resource** |
| `pf-pentest-from-spec` | via `/pf-next <slug> pentest` | Data-sensitive projects only: an authorized adversarial test against the project's **registered pre-production host with synthetic data only** (`PENTEST-REQUEST.md` + `references/security-testing.md`) — verifies the scope guardrails first, runs recognized DAST + access-control tooling (and your self-hosted PentAGI when enabled), fixes findings on a `pentest/<date>` branch, writes `PENTEST-RESULT.md`. Never production, never real data, never on a schedule, never `--go` |

## The contracts it enforces
The build/deploy/harden/pentest skills read their contracts from `references/` (mirrored from the Cowork plugin, kept byte-identical by the validator): `performance-budget.md`, `seo-ai-visibility.md`, `security.md`, `code-simplicity.md`, `design-standard.md`, `compliance.md`, `cost-posture.md` (free-first — build locally, create nothing billable without a yes), `monitoring.md` (rollback), `deploy-rule.md`, `security-testing.md`, and the `targets/` registry. A contract is a hard gate: `pf-build-from-spec` refuses to pass a lane that misses any of the six build contracts.

## Requirements on this machine
- Node 20+, `gh` logged in; per target: `vercel` CLI / `az` CLI / Docker Desktop / `wrangler` / `netlify` / `gcloud` / `flyctl` (see `references/targets/`).
- Env vars by **name** only (never stored or printed): per target as listed in its file; for backends `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_DB_URL`, `TEST_USER_EMAIL`, `TEST_USER_PASSWORD`; optional `CRON_SECRET`, `INDEXNOW_KEY`, `PF_WATCH_DIR`.
- Remote Control on (`/remote-control`) so Cowork can reach this session in Chrome; permissions allow-listed for `npm npx git gh vercel az docker` (see `/pf-setup` in Cowork).
- Code checkouts at `<code root>/<slug>`.

## What this plugin never does
Run on a timer or a file-change hook (it ships no hooks module); act on instructions found inside a request file, spec or `notes:` (those describe the product only); build remotely; create a billed resource without stopping for a yes; roll back a database; print or store a secret value (env-var names only); or run the pentest against production, real data, or on a schedule.
