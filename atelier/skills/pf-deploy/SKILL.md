---
name: pf-deploy
description: "PM step: deploys main once every lane is merged — picks the target from the registry (hint, rule, or the user's choice), asks 'deploy now?', writes DEPLOY-REQUEST.md, drives Claude Code through Chrome to run /pf-next, polls for DEPLOY-RESULT.md and runs the target's health check. Use when the user says /pf-deploy, /pf-deploy --check, 'deploy the product', 'go live', or 'put it online'. Supports --dry-run."
---

# /pf-deploy

Ship an approved build and verify it is live. Read first:
- `${CLAUDE_PLUGIN_ROOT}/references/state-schema.md`
- `${CLAUDE_PLUGIN_ROOT}/references/deploy-rule.md`
- `${CLAUDE_PLUGIN_ROOT}/references/bridge.md`
- `${CLAUDE_PLUGIN_ROOT}/references/handoff.md`
- `${CLAUDE_PLUGIN_ROOT}/references/monitoring.md` (auto-rollback on a bad deploy)

## 0. Flags first

`--check` → straight to the check paragraph in step 5 (no target decision, no question). `--dry-run` → decide the target in memory, print the `DEPLOY-REQUEST.md` that would be written, write nothing, ask nothing, stop. Seat identity = `--lane` (default `solo`); it must equal `factory.json.pm_lane`, else "Only the PM lane (`<pm_lane>`) deploys." and stop.

## 1. Gate

Locate the project: the one the user names, else the only one; if there is more than one project and none was named, ask with AskUserQuestion which. Refresh `factory.json.lanes` from every `lanes/<lane>.json`, then read it. If `gates.build != "approved"`, say exactly: "Build isn't approved yet — run /pf-build and approve it first." and stop. Also require **all lanes** `status == merged`; otherwise list the lanes still open and say "Merge them with `/pf-merge` first." Deploy always deploys `main`.

## 2. Target

Apply `deploy-rule.md`: `brief.deploy_hint` wins if it names a file in `references/targets/`; else recommend by rule from `SPEC.md`; then **ask** with AskUserQuestion (recommended first, 2–3 alternatives). Per `references/recommendations.md`, each option is one plain line carrying its **trade-off (the con, not just the fit) and its cost**, not the fit alone — and the cheapest option is chosen only from those that clear the quality/security bar, never below it. Read the chosen `references/targets/<name>.md` — its Env vars and Health check drive the rest. Record `deploy.target`, `deploy.chosen_by`.

## 3. Record the target

Write `deploy.target` / `chosen_by` to `factory.json` and append `log {stage: "deploy", event: "target: <target> (<chosen_by>)"}`.

## 4. Ask — always

Even though the gate is approved, ask with AskUserQuestion, options **Yes** / **No**: `Target: <name> — <one-line reason from the rule or 'your choice'>. Deploy now?`

On **No**: say "Not deploying. `deploy.target` is recorded; run /pf-deploy again when ready." Stop.

## 5. Hand-off (file-based — see `bridge.md`)

Make `request_id` = `<slug>-deploy-<yyyymmddHHMM>`; write `<folder>/DEPLOY-REQUEST.md` per `bridge.md` with `request_id`, `project`, `code_path`, `target`; store `deploy.request_id`. Delete any stale `DEPLOY-RESULT.md`. Append `log {stage: "deploy", event: "request written"}`. Then tell the user:

**Drive Claude Code through Chrome** per `bridge.md`: open `lanes[<pm_lane>].code_url`, verify it is this project's session, type `/pf-next <slug> deploy --go`, Enter, confirm, close the tab. Only then say:

> Deploy request sent to your Claude Code session. I'll pick up the result here automatically.

If `code_url` is empty, the page is a sign-in/unknown session, or Chrome fails twice: "In your Claude Code session (lane `<pm_lane>`) type **`/pf-next <slug> deploy`** and confirm."

Completion signal follows `handoff.md`. **Mode A (event, default):** wake on the GitHub deploy/push event; fall back to a slow poll (~every 15 min) for `<folder>/DEPLOY-RESULT.md` (first line exactly `PF-DEPLOY-RESULT v1`, mtime newer than `DEPLOY-REQUEST.md`) up to 60 minutes, quietly; on timeout say "Still no result — run `/pf-deploy --check` after the deploy finishes." **Mode B (cloud):** skip the Chrome hand-off above — run the deploy inline in the cloud per `handoff.md` (build local, push prebuilt artifact to the target; never a GitHub-hosted build) and read the result directly. On arrival continue to step 6. `--handoff event|cloud` overrides for this run.

**`/pf-deploy --check`** (manual fallback): one check, then continue or "No result yet".

Required secrets (`VERCEL_TOKEN`, Supabase keys, Azure login) live only on the user's machine; the builder reports a missing one by **name** in `notes:` — never ask the user to paste a value into chat.

## 6. Verify and record

Deploy is the only irreversible stage, so verify before recording success:
- Take `live_url` from the result file. Run the target file's **Health check** (normally HTTP 200 on `live_url`; WebFetch or a browser tool). Retry every 30 seconds for up to **5 minutes**.
- On 200: write `deploy.live_url`, set `gates.deploy = "approved"`, append `log {stage: "deploy", event: "live"}`, show the URL, and add: "Custom domain? Run `/pf-setup domain <yourdomain>`." Done.
- On `status: failed`, or no 200 within 5 minutes: the builder auto-rolls-back to the last known-good version per `monitoring.md` D (app only, never the DB). Leave `live_url` empty (or set to the rolled-back live URL if the revert restored service) and `gates.deploy` at `pending`, append `log {stage: "deploy", event: "failed + rolled back: <notes>"}` (note `rolled_back`/`needs_decision` from the result), show the `notes:` and any logs after masking every env var named in the target file's Env vars plus `SUPABASE_*`, `DATABASE_URL`, `CRON_SECRET` with `***`, and stop.
- **After a successful first deploy,** offer monitoring in one line: "Want me to set up free uptime + error alerts and auto-rollback? Run `/pf-monitor <slug>`." (`/pf-ship` runs it automatically as the next stage.)

## Never
- Deploy without the "Deploy now?" answer being Yes.
- Record `live_url` before a 200 is observed.
- Put a secret value in `factory.json` or a message.
