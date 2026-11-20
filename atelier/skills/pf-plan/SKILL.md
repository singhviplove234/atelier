---
name: pf-plan
description: "The PM / BA / PO stage at the front of the factory: from a short description of what to build, interviews the user for the complete requirement (scope, users, data sensitivity, scale, budget, timeline, team), decides solo vs team lanes and creates them, forecasts a budget under the cost posture (a budget never unlocks paid options), picks a methodology and follows it, writes the product brief, architecture, MVP, stack and budget docs (plus a backlog, sprints and a living dashboard for Agile projects), then hands a ready brief to design. Use when the user says /pf-plan, 'plan a product', 'gather requirements', 'be my PM or BA', 'scope this out', or starts a new product idea and wants it planned before design. Supports --dry-run."
---

# /pf-plan [idea] [--dry-run]

The front of the factory — product manager, business analyst and product owner in one. It turns a rough idea into a complete, costed, lane-planned, methodology-driven plan, then hands a ready brief to `/pf-design`. It **never overrides the cost posture**.

Read first:
- `${CLAUDE_PLUGIN_ROOT}/references/planning.md` (this stage's contract — follow it)
- `${CLAUDE_PLUGIN_ROOT}/references/recommendations.md` (the standing rule for every option this stage offers — platform, stack, methodology, tools: each with pros, cons and cost, and quality/security never traded away for price)
- `${CLAUDE_PLUGIN_ROOT}/references/cost-posture.md` (spend rules — a budget never loosens them)
- `${CLAUDE_PLUGIN_ROOT}/references/platform-selection.md` (pick the best-fit platform/stack, any provider, free-first)
- `${CLAUDE_PLUGIN_ROOT}/references/state-schema.md`

## 0. Flags
`--dry-run`: run the interview and print the plan (requirements, lanes, methodology, budget forecast, doc list) without creating a project or any docs; stop.

## 1. Discovery interview
Per `planning.md` §1: from the idea, ask the missing pieces with AskUserQuestion, a few at a time, skipping anything already given. **At the idea stage, run the SWOT pressure-test in `${CLAUDE_PLUGIN_ROOT}/references/plan-audit.md` section A** to surface the risks and opportunities *before* committing effort — it belongs here, early, not right before build. Must end knowing: product + users + the one success outcome; MVP scope; **data sensitivity** (→ `high` if client/financial/personal); scale & audience; any budget and deadline (forecasting only); design direction; team (→ lanes). Working unattended → make the most reasonable assumptions, state them at the top of the plan, and proceed.

## 2. Solo vs team + create lanes
Per `planning.md` §2: recommend solo or a named set of team lanes in one line with the reason (single-surface site → solo; a separable multi-surface product → a lane per surface). On a yes, create them via `/pf-lanes add` and set `pm_lane`. Never over-split. **If the user maintains their own team-lane working standard as a skill, the lanes run inside it — defer to it and its binding team files** (`references/skills.md`); otherwise the factory uses its own built-in lane steps. The factory orchestrates; the user's standard, where present, governs the lane.

## 3. Budget forecast (cost posture rules, always)
Per `planning.md` §3 + `cost-posture.md`: produce the plain forecast — baseline almost always "$0/month on free tiers", a paid line **only** where a real requirement forces it (cheapest that clears the bar, price, trigger), plus a 10x-traffic line. **A stated budget never adds a paid option the project does not need.** Record as `planning.budget_forecast`.

## 3b. Platform & stack (best fit, any provider, free-first)
Per `platform-selection.md`: from the project's real needs, recommend the best-fit **platform + app framework/language + stack** in one plain line with the reason and cost — **the framework is chosen per project type (static generator for a content site, Next/Remix/SvelteKit for a web app, the fitting language for an API, WordPress/headless CMS or mobile when right), not defaulted to Next.js**, and must be a stack the factory can build to its (stack-neutral) contracts — flag any it can't here, at plan time. Provider-agnostic (Azure / AWS / GCP / Oracle / Vercel / Cloudflare / Netlify / Render / Fly / open-source self-host / a free static host), **not** an Azure default. Offer 2–3 real alternatives with AskUserQuestion (include Azure, and an open-source/self-host option when it fits), each one line with its trade-off + cost. The user picks. Record `brief.stack` + `brief.deploy_hint` (a target name). This never loosens the cost posture — free-first across every provider, paid only when a real need forces it, on a yes.

## 3c. Product-shape decisions (asked once, at plan time — never discovered mid-build)
Short checks, each only when it applies — every optional add-on and when it is offered is indexed in `${CLAUDE_PLUGIN_ROOT}/references/options.md` (offered when the project requires it, would benefit, or the user asks; one line, once; off until chosen):
- **A product with paying customers or organizations as customers** → work through `${CLAUDE_PLUGIN_ROOT}/references/saas-blueprint.md` with the user (tenancy, roles, billing, plans and limits, lifecycle email, admin back-office, account lifecycle, onboarding); record each block's decision — or "not needed — <reason>" — in the product brief, so `/pf-build` writes them into the SPEC. A product that takes payments is planned as `data_sensitivity: high` unless the user says otherwise.
- **A mobile app** → say what `${CLAUDE_PLUGIN_ROOT}/references/mobile-release.md` section A requires **before the stack is locked**: the store fees (read the current prices from Apple's and Google's pages — never from memory), that the developer accounts are the owner's, the review and testing-period time in the timeline, the supported release paths (Expo + EAS, or Flutter/native + fastlane) and whether an iOS build has a Mac or a cloud builder, and the one-line comparison with a responsive web app/PWA.
- **More than one country or language** → record `brief.locales` (source locale first) per `${CLAUDE_PLUGIN_ROOT}/references/i18n.md`; one locale needs nothing extra, more than one adds translation work and per-locale checks to the estimate — and ask who supplies and reviews the translations.
- **Several cloud resources, a data-sensitive product, or a client delivery** → set `factory.json.infra` per `${CLAUDE_PLUGIN_ROOT}/references/infrastructure.md` A (`bicep` / `opentofu` / `compose`); a static or single-service target stays `none`.
- **A risky change to a product with real users, or a feature the client switches on themselves** → name the flags (and whether releases go out as a canary) per `${CLAUDE_PLUGIN_ROOT}/references/rollout.md`; otherwise none — a flag system is never added by default.
- **A brand or product page where the product's physical form sells it** → offer the 3D product scene in one line with its cost and con (`${CLAUDE_PLUGIN_ROOT}/references/scene-3d.md`: built from photos in code, or from a real 3D file; loads only after the page; approximate for soft or organic shapes) and record `options.scene_3d`. Never suggested for a project it does not fit.
- **Who checks a push** → set `factory.json.ci` per `${CLAUDE_PLUGIN_ROOT}/references/verification.md` D: `hook` for solo/low-stakes (default), `self-hosted` for team and `data_sensitivity: high` projects (needs a runner — `/pf-setup ci`), `hosted` only for a public repo or on an explicit yes. And, when the product is for someone else, note the **recipient** (name or organization only) so `/pf-deliver` knows a delivery is expected.

## 4. Methodology
Per `planning.md` §4: pick **ship-it** (small/solo), **agile/scrum-lite** (larger/team), or **kanban** (ongoing/maintenance); state which and why; record `planning.methodology`. For agile, break the MVP into user stories grouped into sprints.

## 5. Documents
Per `planning.md` §5 (documents use the document surface Claude itself provides — `references/skills.md`): create the warranted set as living docs (Claude Docs via the docs connector; Word/PDF/PowerPoint/Excel on request via the docx/pdf/pptx/xlsx skills after the content is settled) — product brief/PRD, architecture overview (with a diagram), MVP definition, stack decision, budget forecast; plus backlog + sprint plan for agile. Size each to the project. Record their links in `planning.documents`.

**Flow diagrams are part of the set for every product:** the user journey flowchart and the screen map (`planning.md` §5), drawn before design starts and approved with the plan.

## 6. Living dashboard (agile/team only)
Per `planning.md` §6: build it as a **published Artifact with the `db` capability** (or the Dashboard type) — published **once**, then updated by **writing rows to its database** (ArtifactData), never by republishing — so progress updates do not re-prompt a page-update approval. Mirror `factory.json` + `lanes/<lane>.json` into its db; the PM and each lane write their status there. Record `planning.dashboard_url`. A solo/small project gets a one-line status in chat instead.

## 7. Audit, then plan sign-off and hand to design
**Before sign-off, audit the plan under different roles** — run the eleven-lens audit in `${CLAUDE_PLUGIN_ROOT}/references/plan-audit.md` section B on the architecture + requirements (director, PO, dev, architect, security, UI/UX, SRE, DevOps, DevSecOps, AI/ML, data/compliance) and fold the gaps in. This is the real pre-build gate — it bakes the audit-under-different-roles discipline into the stage, before a line is built. (SWOT already ran at discovery; convene the hard-decision council in `plan-audit.md` section C only for a genuinely hard fork — not routinely.) Then show the plan (requirements, lanes, methodology, budget forecast, doc links, dashboard). **GATE — plan sign-off:** ask the user to approve or adjust (per `state-schema.md` "Approval words"). On approval: set `gates.plan = "approved"`, write the brief, `log {stage:"plan", event:"approved"}`, and say "Plan approved. Run `/pf-design` — or `/pf-ship` to run the whole pipeline." On changes, revise and re-ask.

## Never
- Suggest a paid option because a budget exists, or otherwise loosen `cost-posture.md`.
- Over-split a solo-sized project into lanes.
- Build the living dashboard by republishing the page on each update — always update its **database** instead.
- Proceed to design before plan sign-off.
