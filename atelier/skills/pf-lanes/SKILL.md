---
name: pf-lanes
description: "Manages the lanes of an Atelier project — add team lanes, list them, or show every lane's build status from factory.json — so one seat (the PM) can see where every coding seat stands. Use when the user says /pf-lanes, 'add lanes', 'lane status', 'where is each lane', or 'what's the team's progress'."
---

# /pf-lanes

Lanes are the unit of parallel work. A solo project has one lane, `solo`, created by `/pf-design`; nothing here is needed for solo. Read `${CLAUDE_PLUGIN_ROOT}/references/state-schema.md`.

## `/pf-lanes add <name> [<name>…]`
- Lane names: kebab-case, not `solo`. Each name may carry a scope: `frontend:Home,Pricing`. If the project currently has only `solo`: if `solo` already has a request, refuse ("this project already started solo"); otherwise ask "Convert to a team project? `solo` will be removed and `<first>` becomes the PM lane." On no, change nothing.
- For each name add `lanes.<name> = { branch: "lane/<name>", code_url: "", status: "idle", … }`. Append `log {stage: "setup", event: "lane added", lane}`.
- Remind: "Run `/pf-setup` on each lane's seat to record its Code session URL."

## `/pf-lanes list`
Table: lane · branch · code_url set? · status.

## `/pf-lanes status` (the PM view)
Refresh `factory.json.lanes` from every `lanes/<lane>.json` (PM seat only writes), then for each lane whose status is `requested` or `building`: if `BUILD-RESULT-<lane>.md` exists, is newer than the request and echoes its `request_id`, update `status` from the file first. Then show:

| Lane | Status | Approved | Acceptance | PR | Preview |

Finish with one line: "Ready to merge: <lanes with status ok AND approved true>", "Ready to deploy: yes/no (all lanes merged and gates.build approved)". Never change gates here.

## `/pf-lanes remove <name>`
Only when its status is `idle` or `merged`; otherwise refuse with the reason.
