# End-to-end runs (v2)

Prereq: `/pf-setup` completed on every seat involved (folder connected, Code session URL recorded, permissions allow-listed, `gh` logged in, target credentials by env var name).

## Run 1 — solo landing page → user-chosen target
1. `/pf-design "PF Landing Fixture"` — screens Home, Contact; backend no; Lanes `solo`. Approve.
2. `/pf-build` — expect: request written, Chrome opens your Code session, `/pf-next --lane solo --go` typed, build runs, Cowork reports `acceptance: 4/4`. Approve → `lanes.solo.status == merged`, `gates.build == approved`.
3. `/pf-deploy` — expect the target question (recommended `vercel`, alternatives listed). Pick one → "Deploy now?" → Yes → Chrome types `/pf-next --go` → result → health check 200 → `live_url`.
Expected `factory.json`: all gates approved; `deploy.chosen_by` recorded; log ≥ 8 entries.

## Run 2 — team app, two lanes → azure-container-apps
Seats: PM (also lane `frontend`), lane `backend` (second Cowork task, second Code session).
1. PM: `/pf-design "PF App Fixture"` — Login, Dashboard, Settings; backend yes (notes table, nightly cron); Lanes `frontend, backend`. Approve. `/pf-setup` on both seats to record each `code_url`.
2. Each seat: `/pf-build --lane <its lane>` → Chrome drives its own Code session → PR opened → approve.
3. PM: `/pf-lanes status` shows both `ok` with PRs → `/pf-merge --all-ready` → both `merged` → `gates.build == approved`.
4. PM: `/pf-deploy` → rule recommends `azure-container-apps` (cron) → Yes → local `docker build` + push → health 200.

## Run 3 — Chrome fallback
Blank `lanes.solo.code_url` and run `/pf-build`: expect the fallback wording with the exact line to type; type it; result still picked up by the poll.

Record anything that broke here and fix the skill, not the run.

## Run 4 — wrong-request guard
With a pending build for lane `backend` and a stale `DEPLOY-REQUEST.md` present, type `/pf-next pf-app deploy` in Code: expect "no pending deploy request" (stale result present) — never a build. Type `/pf-next` bare: expect only a list.

## Run 5 — Chrome session check
Point `lanes.solo.code_url` at an expired link, run `/pf-build`: expect immediate fallback with the exact line (without `--go`) and no typing into a wrong page.
