---
name: pf-ship
description: "Runs the whole Atelier pipeline end to end for one project — optional plan, then design, build (all lanes), merge, deploy, harden, monitor, pentest for data-sensitive projects, and delivery to a client — calling each stage in turn, honoring the chosen handoff mode, and pausing only at the human gates (plan sign-off, design sign-off, deploy go-live, harden merge, pentest scope, client-data go-live, delivery acceptance). Resumable: it picks up from wherever factory.json left off. Use when the user says /pf-ship, 'ship it end to end', 'run the whole pipeline', 'take this all the way', or 'build and launch it'. Supports --from a stage name, --handoff event|cloud, and --dry-run."
---

# /pf-ship [idea|slug] [--from design|build|merge|deploy|harden|pentest|deliver] [--handoff event|cloud] [--dry-run]

The conductor. It does **not** build or deploy itself — it runs the existing `/pf-*` stages in order, checks each one's gate and result, and moves to the next **automatically when a stage passes**, stopping **only** at a human gate. Autonomy means the plumbing runs itself; your judgment gates do not move.

Read first:
- `${CLAUDE_PLUGIN_ROOT}/references/state-schema.md`
- `${CLAUDE_PLUGIN_ROOT}/references/handoff.md`

## 0. Flags & handoff
- `--dry-run`: print the plan (the stages it would run and where it would pause) and stop — write nothing.
- `--from <stage>`: begin at that stage; earlier stages are skipped **only** if their gate already shows done, never if a gate is still `pending`.
- `--handoff event|cloud`: pass this mode to every stage this run (otherwise each stage uses `factory.json.handoff.mode`, default `event`).
- `--guarded` / `--streamlined`: set the autonomy level for this run (see below), overriding `factory.json.ship_mode`.

## Autonomy level (how many gates it pauses at)
`factory.json.ship_mode` (default **guarded**):
- **guarded (default)** — pause at **every** human gate: plan sign-off, design sign-off, the preview, deploy go-live, harden merge, pentest scope, client-data go-live, delivery acceptance. Nothing advances without your yes at each.
- **streamlined** — for **low-stakes projects only** (`brief.data_sensitivity: normal` — an internal tool, a marketing/brand site): auto-advance plan → design → build → deploy **to a preview** as each stage passes its gates, and pause **once** at **go-live** (you review the finished preview and say yes to make it public). Design and build are auto-approved only because you still see the result at that single go-live review before anything is public.
- **Streamlined never applies to `data_sensitivity: high`.** Those stay guarded, and the pentest-scope and client-data gates always hold whatever the mode. If `--streamlined` is passed on a data-sensitive project, fall back to guarded and say why.

## 1. Locate / start the project
If given an idea (not an existing slug), start at design: run `/pf-design` on it. If given a slug, or there is a single project under the connected `Atelier` folder, read its `factory.json` and resume from the first unfinished stage below. If there is more than one project and none was named, ask which with AskUserQuestion. On `--dry-run`, print the plan from the current state and stop.

## 2. The sequence (each step = run the stage, then decide)
Work out the next stage from `factory.json` and run its skill, then act on the outcome. The **autonomy level** above decides where it pauses: **guarded** (default) stops at every gate below; **streamlined** (low-stakes only) auto-advances to a preview and stops once at go-live. **Stage 0 — Plan (optional):** if the project was started with `/pf-plan` (the PM/BA/PO stage, `references/planning.md`), pf-ship begins there — run `/pf-plan` and wait on **plan sign-off** (`gates.plan`) before design; a small/solo project started straight at design skips planning. The numbered stages:

1. **Design** — if `gates.design != "approved"`: run `/pf-design` (using the approved plan's brief when `gates.plan == "approved"`). **GATE — design sign-off:** it stops for your approval; pf-ship waits. On approval, continue; with no approval, pf-ship stays parked and nothing downstream runs.
2. **Build** — for every lane in `factory.json.lanes` not yet `ok`/`merged`: run `/pf-build --lane <lane>` (honoring the handoff mode; the first build records the mode per `handoff.md` after presenting its pros/cons/cost). A lane that **passes all gates** (acceptance + every contract + the review pass + edge-case tests) is approved by the conductor and merged (solo = already on `main`; team lane → `/pf-merge --lane <lane>`, which **pauses for your yes on each lane unless `factory.json.merge_policy: standing-yes` is set** — in streamlined mode set standing-yes if you want team merges to auto-advance). A lane that **fails** stops the pipeline: show its `failures:` and wait; `/pf-build --lane <lane>` re-runs continue. When every lane is merged (`gates.build == "approved"`), continue.
   - *Why build has no separate pause:* the contracts **are** the gate — a build only advances when it provably meets them, and you still see the result at the deploy gate before anything is public.
3. **Deploy** — run `/pf-deploy`. It deploys a **preview** first wherever the target has one and runs the e2e suite against it (`deploy-rule.md` "Preview first" — asked in guarded mode, automatic in streamlined). **GATE — deploy go-live:** it shows the target, the preview link with its e2e result, any destructive migration or infrastructure deletion/billable resource (each needs its own yes), the rollout (full or a 10% canary), and asks "Deploy now?"; pf-ship waits for your yes. This is where you eyeball it before it is public. On a verified HTTP 200, continue.
4. **Harden** — run `/pf-harden`. It makes the live site fast, findable and robust on a branch and opens a PR. **GATE — harden merge:** its "Merge the hardening PR and redeploy? Yes/No" is yours; pf-ship waits. On yes it merges + redeploys; on no it leaves the PR open and the pipeline is complete through deploy.
5. **Pentest** — only when `brief.data_sensitivity == "high"` **and** a target is registered in `security_testing.authorized_targets[]` (via `/pf-setup pentest`). **GATE — pentest scope:** run `/pf-pentest`, which confirms the scope out loud and runs against the registered pre-production host only. **Never with `--go`, never on a schedule, never in cloud mode** (pentest is always mode A). Whether to then load real client data is a separate human decision — **client-data go-live** — that pf-ship never makes and never automates.
6. **Monitor** — run `/pf-monitor` to put free uptime + error monitoring, alerts to you, and auto-rollback on the live site (per `references/monitoring.md`). It recommends the free Azure-native stack; anything needing your signup or a secret is flagged as pending. A small/solo site can take a lighter check; a client-facing or data-sensitive product expects this stage. After it, the product is built, shipped **and watched**. The ongoing post-launch loops run separately (on a schedule or on demand), not as a one-shot pipeline stage: **`/pf-maintain`** (patch/upgrade, contract re-checks, backups + restore drill) and **`/pf-grow`** (reads the analytics, proposes the next SEO/content fix). Point the user to those once a product is live.
7. **Deliver** — only when the plan recorded a recipient (the product is for someone else) or the user asks: run `/pf-deliver` (`references/delivery.md`). It checks the repo's docs, assembles the delivery pack from the recorded proof, and walks the ownership transfer. **GATE — delivery acceptance:** the product is delivered when the recipient accepts it — pf-ship never flips `gates.delivery`, and never transfers or changes access on any account itself. For a `data_sensitivity: high` project this stage waits for a clean pentest.

**Optional add-ons are not stages.** Anything in `references/options.md` that the project chose is carried by the stage that owns it (a 3D scene by build, a canary by deploy, a status page by monitor). The launch video has its own command — after go-live, if `options.launch_video` is `on` or the user asks, mention `/pf-promo` in one line; pf-ship never runs it on its own and never waits for it. The other optional steps with a command of their own are mentioned the same way, once, at the moment they are useful and never waited for: `/pf-brand` after the plan and before design; `/pf-setup email` and `/pf-setup support` before go-live; `/pf-launch` after monitoring is on; `/pf-feedback` and `/pf-grow` a week or more after launch. `/pf-upgrade` is offered when a project's `factory_version` is older than this plugin.

## 3. Between stages
pf-ship advances on its own **only** past a stage that passed its gate; it never skips a `pending` human gate and never flips a gate itself — each stage owns its gate per `state-schema.md` "Approval words". It reports one short line per stage ("Design approved → building 2 lanes…", "Build merged → ready to deploy"). On any stage failure it stops there with the failure shown; re-running `/pf-ship <slug>` resumes from that point. It runs unattended between gates, but a scheduled or `--go` auto-run is **never** applied to the pentest.

## Never
- Flip a human gate (design, deploy, harden-merge, pentest-scope, client-data, delivery acceptance) on the user's behalf — each is their yes.
- Run the pentest with `--go`, on a schedule, in cloud mode, or against anything but a registered pre-production host.
- Load real client data, or treat a `data_sensitivity: high` project's build as cloud-eligible without the warned yes in `handoff.md`.
- Proceed past a failed stage, or skip a stage whose gate is still `pending`.
