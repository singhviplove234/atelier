# Product planning — the PM / BA / PO stage (discovery → plan → living dashboard)

Standing requirement: before design, the factory acts as a **product manager / business analyst / product owner**. From a short description of what the user wants to build, `/pf-plan` interviews the user for the complete requirement, then produces the planning artifacts a real product team would, decides solo vs team (and which lanes), forecasts a budget, picks a methodology and sets up a living progress dashboard — all **without ever overriding the cost posture**.

## The golden rule: a budget never loosens the cost posture
Asking for a budget is for **planning and forecasting only**. **A stated budget does not unlock paid options.** `cost-posture.md` decides spend exactly the same with or without a budget: free-first, our credits for overflow, paid only when a free option genuinely cannot meet a real requirement — and then the cheapest that clears the bar, with the price, on an explicit yes. Having a budget available is **never** a reason to suggest a paid tier the project does not need. Most projects still forecast **$0/month**. The budget is context, not permission.

## 1. Discovery interview (gather the complete requirement)
From the user's one-liner, ask (AskUserQuestion, a few at a time, skipping anything already given):
- **Product & users:** what it does, who uses it, the core problem, the one outcome that defines success.
- **Scope & MVP:** must-have now vs later; the smallest version worth shipping.
- **Data & integrations:** what data it holds — if any is client/financial/personal → `brief.data_sensitivity: high`; external services/APIs; auth.
- **Scale & audience:** internal/hobby vs client-facing/production; expected users; uptime needs.
- **Budget & timeline:** any budget (for forecasting only — see the golden rule) and any hard deadline.
- **Design direction** if not obvious (brand / product / editorial / marketing).
- **Team:** will others build alongside the user (→ lanes)?
Record everything into `factory.json.brief` (extending the existing brief) and a requirements doc. When working unattended, make the most reasonable assumptions, state them plainly at the top of the plan, and proceed rather than blocking.

## 2. Solo vs team — and create the lanes
Decide from scope and the team answer:
- **Solo lane** — one builder owns everything: a marketing/brand site, a landing page, a small tool, a single-surface app (e.g. a premium brand site).
- **Team lanes** — several surfaces that can be built in parallel by different seats: a multi-surface product with genuinely separable areas (e.g. **a multi-surface product** — a delivery app, a reviewer console, an API — each its own lane).
Rule of thumb: split into a lane per independently-buildable surface **only** when the project has separable areas **and** more than one seat will build; otherwise solo. Recommend the split in one line with the reason; on a yes, create the lanes with `/pf-lanes add` (sets `pm_lane`, each lane's `branch`/`scope`). **Never over-split a solo-sized project** — more lanes than the work needs is pure overhead.

## 3. Budget forecast (under the cost posture)
Produce a plain forecast: for the chosen stack and the project's real size/scale, what it runs on and what that costs — **free-first**, so the baseline line is almost always "**$0/month** on the free tiers (Azure SWA Free + Supabase free)". Only where the project's real requirements force a paid tier (commercial licence, bandwidth beyond free, an always-on DB, compliance, scale) does the forecast show that line: the cheapest option that clears the bar, its monthly price, and what triggers it — **recommend-only, nothing created**. Include a **10x-traffic line** (what would start to cost money at scale) so the user sees it coming. The forecast never pads in paid options because a budget exists; if the whole project is free, it says so.

## 4. Methodology — pick one and follow it
Choose from the project's size and shape, state it, then follow it strictly:
- **Ship-it (lightweight)** — a small/solo project (a site, a landing page, a small tool): brief → design → build → deploy, no sprints. **Brand-class.**
- **Agile / Scrum-lite** — a larger multi-surface or team project (**data-sensitive**): an MVP scope, a backlog of user stories, sprints, and the living dashboard (section 6).
- **Kanban** — ongoing / maintenance-heavy work with no fixed scope (e.g. a product in **production support**): a flowing board with WIP limits.
State which and why in one line; for Agile, break the MVP into user stories and group them into sprints.

## 5. The planning documents (what a product team makes)
Generate the set the project warrants, as **living docs** (Claude Docs) by default, exported to **Word/PDF on request**:
- **Product brief / PRD** — problem, users, goals, scope (MVP vs later), success metrics.
- **Architecture overview** — the stack, the pieces and how they fit (a diagram), data-model sketch, integrations, hosting.
- **MVP definition** — the smallest shippable slice and its acceptance.
- **Tech-stack decision** — what and why (locked at design approval).
- **Budget forecast** — section 3.
For an Agile project also: **the backlog (user stories)** and **the sprint plan**. Size each to the project — a small project gets a one-page brief, not a binder; never generate a document the project does not need.

## 6. The living progress dashboard (and the artifact-update fix)
For an Agile/team project, create a **living dashboard** the user monitors progress from, built so it updates **without re-asking permission every time**:
- It is a **published Artifact with a shared database** (the `db` capability; or the Dashboard artifact type). The page is **published once** (one approval). Thereafter the PM and each lane report progress by **writing rows to its database** (ArtifactData / write_db) — **never by republishing the page**. Row writes are lightweight data updates: they do not re-trigger the page-update approval, so a lane authorized to report progress simply writes its status. **This is the fix for "every artifact update asks permission": don't rebuild the page, update its data.**
- It shows: the current sprint/stage, each lane's status and gate, the story/sprint board, the budget line, and the latest build/deploy/harden/pentest results — read live from the db, which mirrors `factory.json` + each lane's `lanes/<lane>.json`.
- A small/solo project gets a **one-line status in chat** instead; a full dashboard there would be overkill.

## 7. After launch — the factory keeps it running (maintenance)
Planning does not end at launch. For a product that stays live, the factory moves it to the **Kanban/maintenance** methodology and the post-launch loops (monitoring + alerts, the maintenance patch/upgrade pass, the growth loop — see the roadmap). The plan names who/what maintains it and sets the project up so `/pf-harden`, the maintenance loop and monitoring keep it healthy — the factory is the builder **and** the production-support/maintenance role, not just a one-time build.

## 8. Hand to the pipeline
Write the brief + requirements, record `planning.methodology`, `planning.budget_forecast`, `planning.documents` and `planning.dashboard_url` in `factory.json`. **GATE — plan sign-off:** the user approves the requirement set, the lanes and the methodology before anything is designed; on approval set `gates.plan = approved`, then hand to `/pf-design`. Under `/pf-ship`, pf-plan is **stage 0** — it runs first, and plan sign-off precedes design sign-off.
