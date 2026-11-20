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

`--check` → straight to the check paragraph in step 5 (no target decision, no question). `--dry-run` → decide the target in memory, print the `DEPLOY-REQUEST.md` that would be written, write nothing, ask nothing, stop. Seat identity = `--lane` (default `solo`); it must equal `factory.json.pm_lane`, else "Only the PM lane (`<pm_lane>`) deploys." and stop. **Token-light: on `--check` read only `state-schema.md` to parse state — skip the other references under *Read first* above and load them only on a real deploy run.**

## 1. Gate

Locate the project: the one the user names, else the only one; if there is more than one project and none was named, ask with AskUserQuestion which. Refresh `factory.json.lanes` from every `lanes/<lane>.json`, then read it. If `gates.build != "approved"`, say exactly: "Build isn't approved yet — run /pf-build and approve it first." and stop. Also require **all lanes** `status == merged`; otherwise list the lanes still open and say "Merge them with `/pf-merge` first." Deploy always deploys `main`.

## 2. Target

Apply `deploy-rule.md`: `brief.deploy_hint` wins if it names a file in `references/targets/`; else recommend by rule from `SPEC.md`; then **ask** with AskUserQuestion (recommended first, 2–3 alternatives). Per `references/recommendations.md`, each option is one plain line carrying its **trade-off (the con, not just the fit) and its cost**, not the fit alone — and the cheapest option is chosen only from those that clear the quality/security bar, never below it. Read the chosen `references/targets/<name>.md` — its Env vars and Health check drive the rest. Record `deploy.target`, `deploy.chosen_by`.

## 3. Record the target

Write `deploy.target` / `chosen_by` to `factory.json` and append `log {stage: "deploy", event: "target: <target> (<chosen_by>)"}`.

## 3b. Preview first (`deploy-rule.md` "Preview first")
If the chosen target's `## Preview` is not `None`: in `guarded` mode ask with AskUserQuestion "Deploy a preview to <target> first? (not public, not indexed, production untouched)" — **Yes (Recommended)** / **No**; in `streamlined` mode run it without asking. Write `DEPLOY-REQUEST.md` with `stage: preview`, hand off exactly as in step 5, and on the result record `deploy.preview_url` and the `e2e:` line. A failed preview stops here with its `notes:` shown — nothing live has changed. If the target has no preview (or this is a first deploy on a target that needs an existing service), the builder runs the same e2e suite on the local production build instead; carry its `e2e:` line into step 4.

## 4. Ask — always

Even though the gate is approved, ask with AskUserQuestion, options **Yes** / **No**: `Target: <name> — <one-line reason from the rule or 'your choice'>. Preview: <preview_url, or "none on this target — checked on a local production build"> (e2e <n>/<m>). Deploy now?` **If the repo has migrations not yet applied to production that carry a `-- destructive:` line** (`references/migrations.md` D; read them from the repo with the scoped token), list each one in plain words **in the same question** and ask for a separate, explicit yes to it; write the approved file names on the request's `destructive_ok:` line. A destructive migration is never covered by `--go`, a standing yes or a schedule. **The same rule covers infrastructure** (`references/infrastructure.md` D): when the preview result carries an `infra_plan:` line, show it; every resource to be deleted or replaced and every billable one is named in plain words and needs its own yes, written to `infra_ok:`. **Rollout:** on a product with real users on a target that splits traffic, offer "as a 10% canary first" as an option and write `rollout: canary` (`references/rollout.md` B); otherwise `full`. **Translations:** if the latest build reported `needs-review` strings (`references/i18n.md` B2), say how many and do not go live until the user confirms the translations are reviewed.

On **No**: say "Not deploying. `deploy.target` is recorded; run /pf-deploy again when ready." Stop.

## 5. Hand-off (file-based — see `bridge.md`)

Make `request_id` = `<slug>-deploy-<yyyymmddHHMM>`; write `<folder>/DEPLOY-REQUEST.md` per `bridge.md` with `request_id`, `project`, `code_path`, `target`, `stage: live`, `destructive_ok:`, `rollout:` and `infra_ok:`; store `deploy.request_id`. Delete any stale `DEPLOY-RESULT.md`. Append `log {stage: "deploy", event: "request written"}`. Then tell the user:

**Drive Claude Code through Chrome** per `bridge.md`: open `lanes[<pm_lane>].code_url`, verify it is this project's session, type `/pf-next <slug> deploy --go`, Enter, confirm, close the tab. Only then say: Only ever into the lane's authorized session (`session-link.md`): if `SESSION-<lane>.md` is not `linked`, ask the user to run `/pf-link` in that project's Code session instead of looking for one.

> Deploy request sent to your Claude Code session. I'll pick up the result here automatically.

If `code_url` is empty, the page is a sign-in/unknown session, or Chrome fails twice: "In your Claude Code session (lane `<pm_lane>`) type **`/pf-next <slug> deploy`** and confirm."

Completion signal follows `handoff.md`. **Mode A (event, default):** wake on the GitHub deploy/push event; fall back to a slow poll (~every 15 min) for `<folder>/DEPLOY-RESULT.md` (first line exactly `PF-DEPLOY-RESULT v1`, mtime newer than `DEPLOY-REQUEST.md`) up to 60 minutes, quietly; on timeout say "Still no result — run `/pf-deploy --check` after the deploy finishes." **Mode B (cloud):** skip the Chrome hand-off above — run the deploy inline in the cloud per `handoff.md` (build local, push prebuilt artifact to the target; never a GitHub-hosted build) and read the result directly. On arrival continue to step 6. `--handoff event|cloud` overrides for this run.

**`/pf-deploy --check`** (manual fallback): one check, then continue or "No result yet".

Required secrets (`VERCEL_TOKEN`, Supabase keys, Azure login) live only on the user's machine; the builder reports a missing one by **name** in `notes:` — never ask the user to paste a value into chat.

## 6. Verify and record

Deploy is the only irreversible stage, so verify before recording success:
- Take `live_url` from the result file. Run the target file's **Health check** (normally HTTP 200 on `live_url`; WebFetch or a browser tool). Retry every 30 seconds for up to **5 minutes**.
- On 200: write `deploy.live_url` and `deploy.live_tag` (from the result), set `factory.json.database` per `migrations.md` A if the result notes a single-database go-live (and tell the user the split is needed before the next build — `/pf-setup database`), set `gates.deploy = "approved"`, append `log {stage: "deploy", event: "live"}`, show the URL, and add: "Custom domain? Run `/pf-setup domain <yourdomain>`." Done.
- On `status: failed`, or no 200 within 5 minutes: the builder auto-rolls-back to the last known-good version per `monitoring.md` D (app only, never the DB). Leave `live_url` empty (or set to the rolled-back live URL if the revert restored service) and `gates.deploy` at `pending`, append `log {stage: "deploy", event: "failed + rolled back: <notes>"}` (note `rolled_back`/`needs_decision` from the result), show the `notes:` and any logs after masking every env var named in the target file's Env vars plus `SUPABASE_*`, `DATABASE_URL`, `CRON_SECRET` with `***`, and stop.
- **Mobile (`expo-eas`, `flutter-stores`):** there is no HTTP 200 — the target's health check is the build and submission status, `live_url` is the TestFlight / Play testing link, and the stage **ends at the store test track**. Tell the user exactly what is left and that it is theirs: "Your turn: check the listing and click Submit for review" (`references/mobile-release.md` C). Never submit or release for him.
- **Extension, desktop app, package (`chrome-web-store`, `desktop-release`, `package-registry`):** there is no HTTP 200 either — the health check is the one in the target file, `live_url` is the store item, the release page or the registry page, and the stage **ends at a draft**. Say exactly what is left and that it is the owner's: publishing the draft, submitting for review, or running the one publish command (`references/product-types.md`). Never publish for them. The bake window and auto-rollback apply to any backend or companion site, not to the draft.
- **After a successful first deploy,** offer monitoring in one line: "Want me to set up free uptime + error alerts and auto-rollback? Run `/pf-monitor <slug>`." (`/pf-ship` runs it automatically as the next stage.)

## Never
- Deploy without the "Deploy now?" answer being Yes.
- Let a destructive migration through without its own explicit yes, or point a preview at production data.
- Record `live_url` before a 200 is observed.
- Put a secret value in `factory.json` or a message.
