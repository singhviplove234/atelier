# factory.json — project state (v2)

One file per project at `<Atelier folder>/<slug>/factory.json`. Every `/pf-*` skill reads it first and writes it back after any state change, appending a `log` entry. When creating a new project and the file already exists, never overwrite it silently: ask "resume or start over?".

## Paths (cross-platform)
Two roots, both OS-neutral and overridable by a user environment variable:
- **Atelier folder** — where projects live (this file, the brief, docs, request/result files). The folder you connect to the Cowork task. Default `~/Atelier` (on Windows `%USERPROFILE%\Atelier`); override with `PF_WATCH_DIR`.
- **Code root** — where the builder checks out each repo on the build machine. Default `~/dev/atelier` (on Windows `%USERPROFILE%\dev\atelier`); override with `PF_CODE_DIR`. A project's `code_path` is `<code root>/<slug>`, and `<code root>/<slug>--<lane>` for a non-PM lane. Paths are written with the host OS's separator; the examples below use `/`.

## Lessons (read first, by every command)
If `<watch dir>/LESSONS.md` exists, read it before doing anything else and apply the active lessons whose "Applies to" names this command or its stage (`learning.md`). A lesson never relaxes a contract or a gate. Say in one line when a lesson changed what was done.

## Approval words (shared by every gate)

Flip a gate **only** on one of: `yes`, `approve`, `approved`, `go ahead`. A reply that contains a yes *and* a change ("yes, but make the header blue") is a change request, not an approval. Anything else that sounds positive (`looks good`, `ok`, `nice`, `ship it`) → ask with AskUserQuestion "Approve the <stage>? (yes/no)". Deploy exception: `gates.deploy` flips on a verified HTTP 200 after the "Deploy now?" answer was Yes — that Yes is the approval.

```json
{
  "name": "my-saas-idea",
  "created": "2026-10-16T10:00:00+05:30",
  "factory_version": "",
  "brief": {
    "one_liner": "", "audience": "", "goal": "",
    "screens": ["Home", "Pricing"],
    "backend": false, "data": "",
    "stack": "Next.js + Tailwind + shadcn/ui (TypeScript); Supabase",
    "deploy_hint": "",
    "size": "small",
    "design_direction": "product",
    "product_type": "web",
    "data_sensitivity": "normal",
    "locales": ["en-US"]
  },
  "handoff": { "mode": "event" },
  "ci": "hook",
  "database": "single",
  "infra": "none",
  "options": { "advisor": "none", "scene_3d": "none", "launch_video": "off", "grow_drafts": "off", "brand_kit": "off", "email": "none", "support": "off", "launch_pack": "off", "feedback": "off", "experiments": "off" },
  "promo": { "brief": "", "video": "" },
  "merge_policy": "ask",
  "ship_mode": "guarded",
  "planning": { "methodology": "", "budget_forecast": "", "documents": [], "dashboard_url": "" },
  "monitoring": { "uptime": "", "errors": "", "alerts": "", "rollback": "", "health_route": "", "status_page": "" },
  "maintenance": { "schedule": "", "last_run": "", "backups": "", "restore_tested": "", "open_pr": "",
    "secret_rotation": [ { "name": "SUPABASE_SERVICE_KEY", "where": "host env var", "scope": "db service", "cadence_days": 180, "last_rotated": "" } ],
    "spend": { "as_of": "", "providers": [ { "provider": "azure", "mtd": "$0.00", "forecast": "$0/month", "free_limit_note": "" } ], "alert": "" } },
  "growth": { "last_run": "", "report_url": "" },
  "brand": { "name": "", "checked": "", "logo": "", "kit": "" },
  "email": { "verified": "" },
  "launch": { "checklist": "", "date": "", "waitlist": "none" },
  "feedback": { "last_run": "", "report": "" },
  "experiments": [],
  "upgraded": { "date": "", "from": "", "items": [] },
  "artifacts": { "design_system_url": "", "design_url": "" },
  "gates": { "plan": "pending", "design": "pending", "build": "pending", "deploy": "pending", "delivery": "pending" },
  "delivery": { "recipient": "", "pack_url": "", "transfer": {}, "accepted": "", "access_after": "" },
  "code_path": "<code root>/my-saas-idea",
  "repo_url": "",
  "pm_lane": "solo",
  "lanes": {
    "solo": { "branch": "main", "code_path": "<code root>/my-saas-idea", "scope": "all", "code_url": "", "request_id": "", "request": "", "result": "", "status": "idle", "approved": false, "pr_url": "", "preview_url": "" }
  },
  "deploy": { "target": "", "chosen_by": "", "request_id": "", "preview_url": "", "live_url": "", "live_tag": "", "rollout": "full", "custom_domain": "", "netlify_site_id": "" },
  "log": [ { "ts": "2026-10-16T10:00:00+05:30", "stage": "design", "event": "created" } ]
}
```

| Field | Meaning |
|---|---|
| `name` | kebab-case slug; folder, `code_path` leaf and GitHub repo name |
| `brief.*` | The approved brief; `stack` locks at design approval; `deploy_hint` may name a target from `references/targets/` |
| `brief.data_sensitivity` | `normal` or `high`. `high` (data-sensitive client/financial/personal data) triggers the security CI gate (`security.md` 15) and the handoff guardrail: default mode A, cloud mode B only on an explicit warned yes (`handoff.md`) |
| `handoff.mode` | `event` (A, default — local build, GitHub-event wake) or `cloud` (B — cloud build). Set once before the first build via `/pf-build` (the PM explains both with pros/cons/cost); overridable per run with `--handoff`. See `references/handoff.md` |

| `merge_policy` | `ask` (default — `/pf-merge` asks before each merge) or `standing-yes` (opt-in, per project; the user pre-authorizes merges that are **already approved, fully reviewed and green on the current commit** — e.g. a team project). The standing yes is bounded to merges only; deploy/go-live, pentest scope and client-data go-live always ask regardless. See `pf-merge` §2 and `security.md` 16 (reads use the scoped token, fail closed) |
| `ci` | `hook` (default — the repo's pre-push hook runs `verify`), `self-hosted` or `hosted` (adds the GitHub Actions workflow). Set at plan or by `/pf-setup ci`; passed to the builder as the request's `ci:` line. See `references/verification.md` D |
| `database` | `single` (before go-live) or `split` (separate test and production databases — required from the first build after go-live, and from the first build for `data_sensitivity: high`). Names only. See `references/migrations.md` A |
| `infra` | `none` (default — static and single-service targets), `bicep`, `opentofu` or `compose`: the cloud resources are code in the repo's `infra/`, previewed and applied by the deploy. Required when a project with its own cloud resources is `data_sensitivity: high`, has more than three of them, or is a client delivery. See `references/infrastructure.md` |
| `brief.locales` | The locale list, source locale first. One entry = locale-ready basics only; more than one = full translation machinery and per-locale checks. See `references/i18n.md` |
| `deploy.rollout` | `full` (default) or `canary` (10% → bake → 100% on targets that split traffic; a percentage flag elsewhere). Chosen per deploy. See `references/rollout.md` |
| `monitoring.status_page` | URL of the public status page (client-facing or paid products), hosted on a different provider than the app. See `references/monitoring.md` F |
| `options.*` | The add-ons recorded here — `advisor` (`none`/`economy`/`extra-review`), `scene_3d` (`none`/`shapes`/`model`), `launch_video` and `grow_drafts` (`off`/`on`). Also `brand_kit`, `support`, `launch_pack`, `feedback`, `experiments` (`off`/`on`) and `email` (`none`/`address`/`transactional`/`both`). All off by default; each is defined in exactly one file, listed with every other optional choice in `references/options.md` |
| `promo.*` | Set by `/pf-promo` (`references/launch-video.md`): `brief` (the brief-pack folder), `video` (path of the rendered file from `PROMO-RESULT.md`). Never a gate |
| `ship_mode` | `guarded` (default — `/pf-ship` pauses at every human gate) or `streamlined` (low-stakes `data_sensitivity: normal` only — auto-advance to a preview, pause once at go-live). Streamlined never applies to `data_sensitivity: high`. Overridable per run with `--guarded`/`--streamlined`. See `pf-ship` |
| `planning.*` | Set by `/pf-plan` (the PM/BA/PO stage, `references/planning.md`): `methodology` (`ship-it`/`agile`/`kanban`), `budget_forecast` (plain forecast under the cost posture — a budget never unlocks paid), `documents` (links to the brief/PRD, architecture, MVP, stack, budget docs + backlog/sprints), `dashboard_url` (the living db-backed progress dashboard for agile/team projects) |
| `gates.plan` | `pending` / `approved` per "Approval words". Set by `/pf-plan` on plan sign-off; precedes `gates.design`. A project started straight at `/pf-design` leaves it `pending` (planning optional for small/solo work) |
| `monitoring.*` | Set by `/pf-monitor` (`references/monitoring.md`): `uptime`, `errors`, `alerts` (the free stack in place, e.g. "App Insights + Monitor email/push"), `rollback` (auto-rollback configured for the target), `health_route` (the `/api/health` path). Not a gate; set after the first deploy |
| `maintenance.*` | Set by `/pf-maintain` (`references/maintenance.md`): `schedule` (e.g. weekly), `last_run`, `backups` (what's in place — GitHub + Supabase daily + any Blob dump), `restore_tested` (last restore-drill result), `open_pr` (current maintenance PR), `secret_rotation[]` (each tracked secret's **name**, location, scope, cadence and last-rotated date — **never a value**; `maintenance.md` E), `spend` (month-to-date actuals vs forecast and free-tier limits per provider, `as_of` date, any `alert` — numbers only, no payment details; `maintenance.md` F). Phase 3 |
| `growth.*` | Set by `/pf-grow` (`references/growth.md`): `last_run`, `report_url` (the latest prioritized next-steps report). Recommend-only. Phase 3 |
| `factory_version` | The plugin version that created or last upgraded the project; written at creation and by `/pf-upgrade`. Empty on a project older than this field — `/pf-upgrade` then checks everything. See `references/upgrade.md` |
| `brief.product_type` | `web` (default), `mobile`, `extension`, `desktop`, `api`, `cli` or `agent`. Set at plan time; decides what a screen, a deploy and a health check mean, and which harden passes apply. See `references/product-types.md` |
| `brand.*` | Set by `/pf-brand` (`references/brand.md`): `name`, `checked` (date of the name screening), `logo`, `kit` (paths). Never a gate |
| `email.verified` | Date the sending identity (SPF, DKIM, DMARC) last passed its header check. Set by `/pf-setup email` (`references/email.md`) |
| `launch.*` | Set by `/pf-launch` (`references/launch.md`): `checklist` (where it is kept), `date` (the owner's launch date), `waitlist` (`none`/`on`). Never a gate |
| `feedback.*` | Set by `/pf-feedback` (`references/feedback.md`): `last_run`, `report`. Recommend-only |
| `experiments[]` | One entry per test (`references/experiments.md`): `id` (X1 …), `hypothesis`, `metric`, `start`, `end`, `sample`, `result` |
| `upgraded.*` | Set by `/pf-upgrade`: `date`, `from` (the version it came from), `items` (the `upgrade.md` numbers done) |
| `gates.*` | `pending` / `approved` per "Approval words". `gates.build` is approved when **every declared lane** is `ok` and merged |
| `code_path` | The PM lane's checkout, `<code root>/<slug>` |
| `pm_lane` | Name of the lane whose seat owns `/pf-merge` and `/pf-deploy` (the first lane in the brief; `solo` on solo projects). A seat identifies itself by the `--lane` it runs with |
| `lanes.<name>` | One per lane. Solo projects have exactly `solo` with `branch: main`. Team lanes use `branch: lane/<name>` |
| `lanes.<name>.code_path` | `<code root>/<slug>` for `solo` and for the PM lane; `<code root>/<slug>--<lane>` for every other lane, so two lanes on one machine never share a working tree |
| `lanes.<name>.scope` | What this lane builds: `all` (solo) or a list of screens/routes from the brief's Lanes line (e.g. `Home, Pricing` or `/api/*`). Written into `SPEC-<lane>.md` → `## Scope` |
| `lanes.<name>.code_url` | Remote Control URL of that lane's Claude Code session, set by `/pf-setup`; empty means "ask the user to type the line" |
| `lanes.<name>.request_id` | Id of the latest request (`<slug>-<lane>-<yyyymmddHHMM>`); the builder refuses a request whose id is not the one Cowork typed |
| `lanes.<name>.request` / `.result` | Paths of `BUILD-REQUEST-<lane>.md` / `BUILD-RESULT-<lane>.md` |
| `lanes.<name>.status` | `idle` → `requested` → `building` → `ok` \| `failed` → `merged` |
| `lanes.<name>.approved` | `true` once the lane's owner approved the build in `/pf-build`; `/pf-merge` requires it |
| `lanes.<name>.pr_url` | PR for `lane/<name>`; empty for `solo` |
| `deploy.target` | A name from `references/targets/`; `chosen_by` ∈ `hint` / `rule` / `user`; `request_id` of the deploy request |
| `deploy.preview_url` / `live_tag` | The last preview deployed (`deploy-rule.md` "Preview first") and the `live-<yyyymmdd-HHMM>` git tag of what is live now (the rollback and changelog marker) |
| `gates.delivery` / `delivery.*` | Set by `/pf-deliver` (`references/delivery.md`): the gate flips only on the recipient's acceptance; `recipient` (name or organization — no contact details), `pack_url`, `transfer` (per-item status), `accepted` date, `access_after` (`ended` or the retained scope). Optional stage — an unstarted delivery stays `pending` and blocks nothing |
| `deploy.live_url` | Set only after the target's health check passes. `custom_domain` set by `/pf-setup domain`. `netlify_site_id` is not a secret and may be stored |
| `log[]` | Append-only; `ts`, `stage` (`plan`/`design`/`build`/`merge`/`deploy`/`harden`/`pentest`/`monitor`/`maintain`/`deliver`/`promo`/`grow`/`setup`), `event`, optional `lane` |

## Who writes what (avoids write collisions when the folder is cloud-synced)

- Each lane's seat writes **only** `lanes/<lane>.json` in the project folder (the same shape as `lanes.<name>` above).
- The **PM seat** is the only writer of `factory.json`. `/pf-lanes status`, `/pf-merge` and `/pf-deploy` first refresh `factory.json.lanes` from every `lanes/<lane>.json`, then act. On a solo project the one seat is the PM and writes both.
- `gates.build` is set back to `pending` whenever any lane writes a new build request; it is `approved` only when every lane is `merged`.

Rules: secrets are never stored here (env var names only). Lane names are kebab-case; `solo` is reserved.

## harden (added 17 Oct 2026)
`"harden": {"request_id": "", "status": "none|requested|ok|failed", "branch": "", "pr_url": "", "budget_met": null, "last_run": ""}` — written by `/pf-harden` (PM lane only).

## security_testing (added 21 Oct 2026 — data-sensitive projects)
`brief.data_sensitivity`: `"normal"` | `"high"` (data-sensitive: client private/financial data). When `high`, a clean `/pf-pentest` is recommended as a required gate before the first client-data deploy.
```json
"security_testing": {
  "status": "none|requested|ok|failed|refused",
  "authorized_targets": [
    { "host": "https://staging.example.com", "owner": "you", "environment": "staging", "data_state": "synthetic", "registered": "2026-10-21" }
  ],
  "pentagi": { "enabled": false, "endpoint": "" },
  "last_request_id": "", "branch": "", "pr_url": "", "critical_high_open": null, "last_run": ""
}
```
Rules: a host is an eligible pentest target **only** while it is on `authorized_targets[]` with `owner: you`, `environment ∈ {staging,dev,local}` and `data_state: synthetic`. A host's `data_state` flips to `real` (and so off-limits to the pentester) once client data is loaded — client data and pentesting never share a host. `pentagi.enabled` makes the pentest run drive your own self-hosted PentAGI (`endpoint`, e.g. `http://localhost:8080`, no secret stored) against the one authorized target, only inside a human-confirmed `/pf-pentest` run, bounded to that host, stopping when the run ends.
