# Manual test script — /pf-deploy

Prereq: a project with `gates.build == approved` (from `tests/pf-build.md` case 8).

| # | Setup | Do | Expected |
|---|---|---|---|
| 1 | `gates.build == pending` | `/pf-deploy` | Refuses: "Build isn't approved yet — run /pf-build and approve it first." |
| 2 | SPEC Stack = Next.js, Data model = None, no hint | `/pf-deploy` | Target question with `vercel` (Recommended) + alternatives from the registry; pick vercel → "Target: vercel — … Deploy now?"; `deploy.chosen_by == rule`. |
| 2b | `brief.deploy_hint = cloudflare-pages` | `/pf-deploy` | No question about target; `deploy.target == cloudflare-pages`, `chosen_by == hint`; then "Deploy now?". |
| 2c | a lane not merged | `/pf-deploy` | Refuses, lists open lanes, says to `/pf-merge`. |
| 3 | SPEC Routes mention a cron job | `/pf-deploy` | Recommends `azure-container-apps` with reason "cron". |
| 4 | case 2 | answer **No** | Nothing sent; `deploy.target` stays recorded; `live_url` empty. |
| 5 | — | `/pf-deploy --dry-run` | Prints the `DEPLOY-REQUEST.md` content; writes nothing. |
| 6 | answer **Yes**, type `/pf-next` in Claude Code and confirm, wait for `DEPLOY-RESULT.md` with `http_status: 200` | wait for the poll (or `/pf-deploy --check`) | `deploy.live_url` written; `gates.deploy == approved`; shows the URL. |
| 7 | result has `status: failed`, or live URL never returns 200 within 5 minutes | `/pf-deploy --check` | `live_url` empty; notes shown; `gates.deploy` stays `pending`. |
