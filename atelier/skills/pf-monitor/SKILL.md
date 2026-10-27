---
name: pf-monitor
description: "Phase-2 safety net for a deployed project: sets up free uptime + error monitoring and alerts to the user, and confirms auto-rollback is configured so a bad deploy heals itself. Recommends the Azure-native free stack (App Insights availability + exceptions + Monitor email/push alert), offers Sentry or UptimeRobot, guides the account steps, keeps personal data out of reports, and records the result. Use when the user says /pf-monitor, 'set up monitoring', 'watch the site', 'alert me if it goes down', 'is it being monitored', or 'add error tracking'. Supports --check and --dry-run. Recommend-only for anything billable."
---

# /pf-monitor <slug> [--check] [--dry-run]

Put eyes on a live product and make a bad deploy heal itself. Read first:
- `${CLAUDE_PLUGIN_ROOT}/references/monitoring.md` (this stage's contract — follow it)
- `${CLAUDE_PLUGIN_ROOT}/references/cost-posture.md` (free-first; a tier is paid only when forced, on a yes)
- `${CLAUDE_PLUGIN_ROOT}/references/state-schema.md`

## 0. Flags
`--check`: report what monitoring / alerts / rollback are currently live for this project and stop. `--dry-run`: print the stack it would set up and the steps; create nothing; stop.

## 1. Gate
Locate the project; read `factory.json`. Require `deploy.live_url` (a deployed site). If empty: "Deploy the site first (`/pf-deploy`) — there's nothing live to monitor yet." and stop. Seat = `pm_lane`.

## 2. Recommend the free stack (per `monitoring.md` A2, with pros & cons)
Present the choice with **pros and cons** (per `monitoring.md` A2 / `recommendations.md`), not the upside alone: **Azure-native (App Insights + Monitor)** *(Recommended — one account, one pane, $0; cons: plainer error traces, Azure-tied)* vs **Sentry + UptimeRobot** *(best-in-class errors + simple uptime, provider-neutral; cons: two more accounts/dashboards/keys)*. State the recommendation in one plain line, offer the alternative with AskUserQuestion, and keep it **minimal** — one stack unless the user asks for more. Never propose a paid tier because it is "better"; paid only when real volume forces it, with the monthly price + a yes.

## 3. Set up (what Claude can, guide the rest)
Per `monitoring.md` A–C:
- Ensure a `/api/health` route exists (returns 200 + app/DB reachability). If the repo lacks one, record it as a one-line task for the next build.
- **App Insights:** via the Azure tools, create/confirm an App Insights resource in the project's resource group (free grant), wire an availability test on `/api/health` (~5 min), confirm exceptions are captured. Its connection string is set as an env var the `/pf-setup` way — Claude pre-fills the name, the user sets the value.
- **Alerts:** create an Azure Monitor action group to the user's email + Azure-app push, with the rules from `monitoring.md` B (down 2+ checks, error-rate spike, p95 past the budget for a sustained window, cert < 14 days). Recommend email + push; SMS only on a yes with the per-message price.
- **PII scrubbing:** confirm the app strips request bodies, tokens and personal records before any error is sent (`monitoring.md` C); for Sentry, the `beforeSend` scrubber is a build task.
- **Sentry / UptimeRobot (if chosen):** open the signup/project page in Chrome, pre-fill the non-secret fields, stop; the user signs up and pastes the DSN/key, stored as an env var by name.

## 4. Verify and record
Fire **one test alert** (a deliberate failing check or a test event) and confirm it reaches the user. Record `factory.json.monitoring` (`uptime`, `errors`, `alerts`, `rollback`, `health_route`) and `log {stage:"monitor", event:"set up <stack>"}`. Report what is live and what is pending anything waiting on the user's signup/secret.

## 5. Auto-rollback
Confirm the deploy target is set for auto-rollback per `monitoring.md` D (last-good artifact kept / Container Apps previous revision; bake window; **app-only** revert; DB migration **flagged, not reverted**). If the target cannot auto-rollback, say so and give the one manual revert command for that target. This is configuration + a note, not a billable resource.

## Never
- Propose or create a paid monitoring tier because it is nicer — free-first, paid only when real volume forces it, with the price + a yes.
- Send any personal data, token or secret into an error report or alert.
- Auto-revert a database migration (flag it for a human); roll back the **app version only**.
- Enter a secret value yourself — the user sets secrets; Claude pre-fills names.
