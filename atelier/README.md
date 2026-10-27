# Atelier (Cowork plugin) — v3

Takes an idea all the way: **plan → design → build → deploy → harden → monitor → maintain → grow**, and keeps it running afterward. Works for one Cowork seat or a team of seats (one seat is the **PM**). You're involved only at approval gates and at the few steps a human must do. Nothing is ever compromised on quality or security to save cost (`references/recommendations.md`).

## The pipeline at a glance
`/pf-plan` (PM/BA/PO: requirements, budget, lanes, methodology, docs) → `/pf-design` → `/pf-build` (per lane) → `/pf-merge` → `/pf-deploy` → `/pf-harden` → `/pf-pentest` (data-sensitive only) → `/pf-monitor` → then the ongoing loops `/pf-maintain` and `/pf-grow`. **`/pf-ship` runs the whole chain** and pauses only at your gates; **`/pf-board`** shows every project at a glance.

## Commands

| Command | Who | Does | Stops for |
|---|---|---|---|
| `/pf-setup` | each seat, once | One-time setup: `/pf-setup project <slug>` stands up the whole toolchain for a project (Code session, GitHub, the chosen platform's CLI/auth, DB, tokens, handoff, monitoring, backup). Opens pages in Chrome, pre-fills what's safe, you type secrets and click submit | each step |
| `/pf-plan <idea>` | PM | PM/BA/PO: interviews for the full requirement, forecasts the budget (under the cost posture — a budget never unlocks paid), decides solo vs team lanes and creates them, picks a methodology, writes the product docs (PRD, architecture, MVP, stack, budget) + a living dashboard, audits the plan with **tech-doc-audit** (11 roles) | plan sign-off |
| `/pf-design <idea>` | any seat | Brief (incl. lanes + deploy hint) → Claude Design artboards from the shared Design System, to the chosen **design direction** | your approval of the design |
| `/pf-lanes add/list/status` | PM | Declare team lanes; see every lane's state. If you have your own team-lane standard skill, lanes run inside it; otherwise the built-in lane steps are used | — |
| `/pf-build [--lane x]` | each lane's seat | Writes `SPEC.md` + `BUILD-REQUEST-<lane>.md`; hands off by the chosen **handoff mode** (A: build on your machine, wake on the GitHub event; B: build in the cloud, result inline) and runs `/pf-next` on the Code side | your approval of the lane's build |
| `/pf-merge --lane x` | PM | Merges an approved lane's PR into `main`; flips the build gate when all lanes are merged | "merge?" |
| `/pf-deploy` | PM | Picks the platform by **fit** across providers (`references/platform-selection.md`), asks "deploy now?", deploys `main`, runs the health check, and **auto-rolls-back** a bad deploy (app only, never the DB) | "deploy now?" |
| `/pf-harden` | PM | After deploy: safety-net tests, speed budget on the live site, SEO, defensive security, DB indexes, free caching, local k6 load test, hosting-limits check; one commit per fix on a PR; nothing paid is created | "harden now?", "merge + redeploy?" |
| `/pf-pentest` | PM | Data-sensitive only: authorized adversarial test against a pre-production staging host with synthetic data | explicit yes, every run (never `--go`) |
| `/pf-monitor` | PM | Free uptime + error monitoring + alerts to you, and confirms auto-rollback | — |
| `/pf-maintain [--schedule]` | PM | Keeps it patched, re-checks the contracts for drift, verifies backups + runs a **tested restore**; proposes a PR (never auto-merged for sensitive) | your merge |
| `/pf-grow [--schedule]` | PM | Reads Search Console/GA4/Clarity, proposes the next SEO/content/conversion fixes; changes nothing on its own | — |
| `/pf-board` | PM | One live control panel of every project — stage, gates, health, maintenance, what's waiting on you | — |
| `/pf-ship <idea|slug>` | PM | The conductor: runs the whole chain, pausing only at the human gates. `ship_mode` guarded (default) or streamlined (low-stakes only) | each gate (or just go-live, streamlined) |

Solo = a team of one: the single lane is `solo`, it pushes to `main`, and `/pf-merge` is never needed.

## How it's built and shipped (handoff modes, event-wake)
`references/handoff.md`. **Mode A (default, $0):** Claude Code builds on your machine, started through **Chrome** (`/pf-next`), and the PM **wakes on the GitHub PR/push event** rather than polling. **Mode B (cloud):** the build runs in the cloud, result inline, no machine needed. You choose per project with pros/cons/cost shown; data-sensitive projects stay on A unless you opt in with the warning. Secrets never leave your machine in A; in B they're reached via Key Vault, never stored. The file bridge (request/result files) stays the durable record and fallback.

## Platform & stack — any provider, free-first
`references/platform-selection.md`. The factory is **not locked to Azure**. For each project it evaluates the real needs and recommends the best-fit platform — Azure, AWS, GCP, Oracle, Vercel, Cloudflare, Netlify, Render, Fly.io, an open-source self-host, or a free static host — the cheapest option that clears the quality/security bar, with pros/cons/cost, and you pick. Targets live in `references/targets/<name>.md` (vercel, azure-static-web-apps, azure-container-apps, cloudflare-pages, netlify, github-pages, aws-amplify, gcp-cloud-run, render, fly-io, oracle); add a provider by adding a file. All build **locally** and upload — no GitHub-hosted build/deploy minutes.

## The contracts — what every build must meet (the quality + security spine)
Each is a hard gate at build (enumerated in `/pf-build` acceptance) and re-checked live by `/pf-harden`:
- **Speed** (`performance-budget.md`) — mobile Lighthouse ≥ 90, LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1, ≤ 200 KB JS/route, plus a motion-weight budget for motion-led sites.
- **Found everywhere — SEO + AI engines** (`seo-ai-visibility.md`) — metadata, sitemap, robots allow-list for Google/Bing/ChatGPT/Claude/Perplexity, `llms.txt`, JSON-LD, answer-first copy; plus a free measurement foundation (GA4/Search Console/Clarity).
- **Secure by default** (`security.md`) — RLS on every table with isolation tests, Supabase Auth, input validation, rate limits, security headers, secret scan, dependency audit; data-sensitive projects gate on CI. Defensive, own-deployment only — this is not penetration testing (for that, `/pf-pentest`).
- **Simple, handoff-ready code** (`code-simplicity.md`) — the simplest correct version, reuse over reinvention, no dead code, checked before it passes; never at the cost of correctness, security or performance.
- **The right design for each project** (`design-standard.md`) — `/pf-design` picks a **design direction** (brand/product/editorial/marketing) and executes it to an **Apple-grade design** bar with a performant motion layer; Inter/Lucide, WCAG AA, reduced-motion honoured — never Apple's own fonts/symbols, never at the cost of speed or a11y.
- **Legal & compliance** (`compliance.md`) — dependency licences, privacy + consent, terms + data-deletion, no copied assets, attribution/NOTICES, data-subject access/correct/delete, third-party API terms, AI-output provenance; minors/health/financial flagged for a lawyer. Each build also writes a tight **project CLAUDE.md**.
- **Free-first, quality/security never compromised** (`cost-posture.md`, `recommendations.md`) — the cheapest option *from those that clear the bar*; a stated budget never unlocks paid; paid only when a real need forces it, with the price, on a yes.
- **Reviewed by Claude's own reviewer** — every build runs the **built-in** `/code-review` and `/security-review` (free, in-session) and fixes Critical/High before it passes; optional Superpowers adds plan-first + self-verify.

## Keep it running (the production-support half)
- **Monitor** (`monitoring.md`) — free uptime + error tracking + alerts (Azure-native default; Sentry/UptimeRobot alternatives, pros/cons shown), PII scrubbed, plus **auto-rollback** on a bad deploy (app only, DB flagged not reverted).
- **Maintain, rotate & back up** (`maintenance.md`) — a schedulable patch/upgrade + drift-recheck pass that proposes a PR, plus two hygiene checks it reports (never commits): **secret rotation** (tracks each key's name + age, guides you through rotating on cadence or on a leave/leak — Claude only ever knows the env-var *name*, never the value) and **spend vs forecast** (reads the real month-to-date bill / free-tier usage per provider and alerts before anything bills, recommend-only). Backup plan: **code on GitHub** (authoritative), **data on Supabase daily + a free off-site `pg_dump` to Azure Blob**, and a **tested restore drill** — a backup you've never restored isn't trusted. Never backs up a secret.
- **Grow** (`growth.md`) — reads the site's own analytics and proposes the next SEO/content/conversion fixes; recommend-only, each chosen item goes through the normal build/harden flow.

## Adversarial testing for data-sensitive projects — penetration testing (`pf-pentest`)
Any project that will hold clients' private or financial data sets `brief.data_sensitivity: high` and gets `/pf-pentest`: an authorized attack-test against a **pre-production staging host of your own, with synthetic data only**, registered via `/pf-setup pentest`. Two versions you keep and choose between with pros/cons — **scanners** (recognized tools, no PentAGI), the **PentAGI agent**, or **both** — recommended per project, a second confirmation before the agent runs. Most gated stage: an explicit human yes every run (never `--go`, never a schedule, never production or real data). Your own self-hosted PentAGI is orchestrated, never bundled. Still not a substitute for a client-authorized third-party pentest before a major launch.

## Skills the factory uses (`references/skill-catalog.md`)
Atelier is one-stop: it **bundles** the three skills whose licenses permit it (`find-skill`, `humanizer`, `design-md` — see `THIRD-PARTY-NOTICES.md`), relies on Claude's **built-in** `/code-review`, `/security-review` and document skills, and on first run **installs the rest from their official sources** via `/pf-bootstrap` (`tech-doc-audit`, `swot-analysis`, `llmcouncil`, the design-taste and animation skills, `remove-ai-marks`, `brandkit`, optionally Superpowers). It never copies a non-redistributable skill into this repo. After the first run, `references/skill-catalog.md` tells Atelier exactly which skill to use when, and how. A skill never overrides a contract or a gate.

## How Cowork and Claude Code talk
The bridge is request/result files + **Chrome** driving the Code session (`references/bridge.md`), with the completion signal set by the handoff mode (event-wake in A, inline in B). The trigger is always a typed `/pf-next` command, by you or the seat on your behalf; nothing auto-runs from a file. If Chrome can't do it, the seat tells you the one line to type.

## What Claude never does
Type passwords, tokens or card numbers; click the final submit on account, payment or DNS pages; store a secret anywhere (env-var names only); deploy without "deploy now?" = yes; run the pentest on a schedule or against real data; redistribute a skill whose license forbids it (the three bundled skills ship under their own permissive licenses — `THIRD-PARTY-NOTICES.md`; everything else installs from its own source); or let cost override the quality/security a project needs.

## Folders & files
- Projects (state, brief, spec, docs, request/result files): the connected `Atelier` folder → `<project>/` (with `factory.json`, `lanes/<lane>.json`).
- Code checkouts: `<code root>/<project>/` on each lane's machine.
- Contracts: `references/*.md` (the files named above) + `references/targets/`. State shape: `references/state-schema.md`. Validator: `tests/check.sh`.
