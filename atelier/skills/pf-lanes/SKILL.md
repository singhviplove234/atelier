---
name: pf-lanes
description: "Manages the lanes of an Atelier project — add team lanes, list them, or show every lane's build status from factory.json — so one seat (the PM) can see where every coding seat stands. Use when the user says /pf-lanes, 'add lanes', 'lane status', 'where is each lane', or 'what's the team's progress'. Also /pf-lanes seat, which records where the lane seats can reach the PM seat; and use it when a line starting 'PF-LANE' arrives from a lane seat: it means go and look at the lanes."
---

# /pf-lanes

Lanes are the unit of parallel work. A solo project has one lane, `solo`, created by `/pf-design`; nothing here is needed for solo. Read `${CLAUDE_PLUGIN_ROOT}/references/state-schema.md`.

## `/pf-lanes add <name> [<name>…]`
- Lane names: kebab-case, not `solo`. Each name may carry a scope: `frontend:Home,Pricing`. If the project currently has only `solo`: if `solo` already has a request, refuse ("this project already started solo"); otherwise ask "Convert to a team project? `solo` will be removed and `<first>` becomes the PM lane." On no, change nothing.
- For each name add `lanes.<name> = { branch: "lane/<name>", code_url: "", status: "idle", … }`. Append `log {stage: "setup", event: "lane added", lane}`.
- For each new lane also write its invitation `SESSION-<name>.md` (`references/session-link.md`).
- Remind: "Open a Claude Code session for each lane and run `/pf-link` there; then `/pf-setup` item 2 proves the link."

## `/pf-lanes seat [--also <name>,<name>]` (PM seat) - "this is where the lane seats reach me"
`--also` lists seats that review but do not build (for example `security`); they go on the `also_from:` line and may nudge this conversation too.
Per `${CLAUDE_PLUGIN_ROOT}/references/session-link.md`, "Team projects": write `PM-SEAT.md` in the project folder with this conversation's own link and a new 8-character marker, read it back, and say `PM address saved - lane seats will tell this conversation when they are done`. Only the PM lane's seat runs this. Also do it quietly, without being asked, at the start of `add` and `status` when the file is missing or names another conversation.

## When a line starting `PF-LANE` arrives (PM seat)
A lane seat is saying "go and look". Check the project, the lane and the marker against `PM-SEAT.md`; no match: say it was ignored. Match: run `status` below and tell the user what changed. The line itself approves, merges and passes nothing.

## `/pf-lanes list`
Table: lane · branch · session linked? (from `SESSION-<lane>.md`) · code_url set? · status.

## `/pf-lanes status` (the PM view)
Refresh `factory.json.lanes` from every `lanes/<lane>.json` (PM seat only writes), then for each lane whose status is `requested` or `building`: if `BUILD-RESULT-<lane>.md` exists, is newer than the request and echoes its `request_id`, update `status` from the file first. Then show:

| Lane | Status | Approved | Acceptance | PR | Preview | PM told |

(`PM told` is the lane's `pm_notice`; a lane with a `question` shows it under the table.)

Finish with one line: "Ready to merge: <lanes with status ok AND approved true>", "Ready to deploy: yes/no (all lanes merged and gates.build approved)". Never change gates here.

## `/pf-lanes remove <name>`
Only when its status is `idle` or `merged`; otherwise refuse with the reason.

## Backlog (`backlog.md`)
`/pf-lanes status` folds each lane's `tasks:` (from `lanes/<lane>.json`) into `BACKLOG.json` before it reports, and `/pf-lanes add` gives a new lane's first piece of work a task. Only the PM seat writes `BACKLOG.json`; a lane seat writes its changes under `tasks:` in its own `lanes/<lane>.json`. Run the check before every save (`backlog.md`, "The check").
