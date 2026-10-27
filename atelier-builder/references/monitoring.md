# Monitoring, alerts & auto-rollback — a live product is watched and can heal itself

Standing requirement: a product the factory ships must not be able to go down, error or regress without anyone knowing — and a bad deploy must not stay live. This is Phase 2 of the roadmap: the safety net that makes a live product safe to leave running. Set up by `/pf-monitor` after a deploy, re-checked by `/pf-harden`, and enforced at deploy time by auto-rollback. Free-first and minimal, like everything else — see `cost-posture.md`.

## A. What gets watched (free-first; one small stack, not five services)
Pick the cheapest option that meets the project's real need; recommend the **Azure-native** default so it stays in one account at $0 within the free grant:

1. **Uptime / availability.** The site answers and is healthy.
   - **Default (Azure-native):** an Azure Application Insights **availability test** hitting the app's `/api/health` route every ~5 min from a couple of regions — free within the App Insights data grant.
   - Alternatives, all free: **UptimeRobot** free (50 monitors, 5-min checks, email alerts) for a dead-simple external check; or a free scheduled HTTPS ping (an Azure Functions **consumption** timer, free grant) plus an Azure Monitor alert. A Supabase-free DB also gets the keep-alive ping from `pf-harden` limits so it does not pause.
2. **Errors.** Runtime exceptions in the running app.
   - **Default (Azure-native):** Application Insights captures server exceptions and failed requests automatically.
   - **Better error insight (free):** **Sentry** Developer plan (free — ~5k errors/month) for client + server, with releases and stack traces. Offer it; don't require it.
3. **Performance / regressions.** p95 latency and error rate over time (App Insights metrics or Sentry performance), so a slow regression is visible, not just a hard outage.

A `/api/health` route (returns 200 + a tiny JSON of app + DB reachability) is added at build if absent — the checks and the rollback bake window both use it.

## A2. Choosing the monitoring stack (pros & cons — see `recommendations.md`)
- **Azure-native (App Insights + Monitor)** *(Recommended)* — *Pros:* one account (if you're on Azure), one place for uptime + errors + alerts, $0 within the free grant, nothing extra to sign up for. *Cons:* error traces are less developer-friendly than Sentry; App Insights has a learning curve; tied to Azure.
- **Sentry (errors) + UptimeRobot (uptime)** — *Pros:* Sentry is best-in-class for error traces and releases (free tier); UptimeRobot is dead-simple uptime with its own alerts; both free; provider-neutral (keeps working if you leave Azure). *Cons:* two more accounts and dashboards to manage; two keys to set; split across tools instead of one pane.
- *Rule of thumb:* Azure-native by default; **add Sentry** when a project's error-debugging matters (a client-facing app with real users); add UptimeRobot only to watch uptime from outside Azure. $0 either way at small scale.

## B. Alerts (reach the user, free)
Route alerts to the user so the user learns of a problem without watching a dashboard:
- **Azure Monitor action group** — email (free) and push via the Azure mobile app (free); SMS/voice have a small per-message cost, so **recommend email + push**, and only add SMS on an explicit yes with the per-message price shown.
- UptimeRobot and Sentry both send email alerts on their own; use those when they are the chosen tool.
Alert on: **down** for 2+ consecutive checks; **error-rate spike** above a baseline; **p95 latency** past the performance budget for a sustained window; **TLS certificate** within 14 days of expiry. Tune thresholds so a single blip does not page — alert on sustained conditions, not one bad check.

## C. Privacy (alerts and error reports carry no personal data)
Error tracking must not become a data leak: scrub request bodies, tokens, cookies, auth headers and any personal records from error reports before they are sent (Sentry `beforeSend` / App Insights telemetry processors); never log a secret or a full personal record (ties into `security.md` A10 and `compliance.md`). Monitoring scripts load within the performance budget and, where they are non-essential, after consent per `compliance.md` A4 — an essential error/uptime check may run as a legitimate interest, but it still carries no PII.

## D. Auto-rollback (a bad deploy heals itself)
A deploy must never leave the product broken:
1. **Keep the last known-good version.** The deploy records the currently-live version before it ships the new one — the previous built artifact (we build locally and upload, so the prior artifact/commit is kept) or, for Container Apps, the previous **revision**.
2. **Health-check + a short bake window.** After the deploy, run the target's health check (already in `deploy-rule.md`); then watch `/api/health`, availability and error rate for a short **bake window** (~5–10 min) using the monitoring from section A.
3. **Revert on failure, automatically.** If the health check fails, or the bake window shows a clear regression (availability drop or error-rate spike well above baseline), **roll back to the last known-good version** — redeploy the prior artifact, or for Container Apps shift 100% of traffic back to the previous healthy revision — then **alert the user** with what happened and why. A deploy that passes is left live; rollback never fires on a healthy deploy.
4. **Never auto-revert the database.** Rollback is for the **app version only**. Schema/data migrations are not rolled back automatically — a migration that breaks is **flagged for the user** with the manual step, because blindly reverting a migration can lose data. Prefer backward-compatible migrations (expand-then-contract) so an app rollback stays compatible with the migrated DB.
5. **Within the gates.** Auto-rollback is a safety reaction to a *failed* deploy the user already approved — it needs no new approval to make the site safe again. A fresh *forward* deploy still needs the usual go-live yes.

## E. How it is set up and checked
- `/pf-monitor <slug>` (after the first deploy): recommend the free stack (Azure-native default), set up what it can via the Azure tools, guide the account/signup steps like `/pf-setup` (Claude pre-fills non-secret, the user does secrets/sign-in), record the result in `factory.json.monitoring`, and confirm each piece is live with a test alert.
- `/pf-harden` reports whether monitoring + alerts are in place and whether auto-rollback is configured for the target; it recommends, never creates billable resources.
- **Cost posture:** everything here is free-first and stays within free grants; a paid monitoring tier (App Insights beyond the free data grant, Sentry Team, SMS alerts) is proposed only when real volume forces it, with the monthly price, on an explicit yes. Keep it to the one Azure-native stack unless the project genuinely needs more.
