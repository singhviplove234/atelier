---
name: pf-merge
description: "PM step for team projects: merges an approved lane's PR into main after the user's yes, updates the lane to merged, and flips gates.build when every lane is merged. Use when the user says /pf-merge, 'merge the LANE lane', or 'merge what's ready'."
---

# /pf-merge --lane <name>   (or `/pf-merge --all-ready`)

Seat identity = `--lane` (default `solo`); it must equal `factory.json.pm_lane`, else "Only the PM lane (`<pm_lane>`) merges." and stop. Lanes whose `branch == main` (solo) never need this. First refresh `factory.json.lanes` from every `lanes/<lane>.json`.

## 1. Preconditions
Lane exists; `lanes[<lane>].status == "ok"`; `lanes[<lane>].approved == true` (its owner said yes in `/pf-build`); `pr_url` non-empty. Otherwise explain which is missing and stop.

## 2. Show and ask (or a bounded standing yes)
Show the PR link, acceptance count, and the preview link. Default: ask with AskUserQuestion "Merge `lane/<name>` into main? (yes/no)" — only an approval word proceeds.

**Standing-yes merge (opt-in, per project).** If `factory.json.merge_policy == "standing-yes"` (a deliberate choice the user set), skip the per-merge ask **only when all guardrails hold**: `lanes[<lane>].approved == true`, every required lane/reviewer approval for this PR is present at the current commit, and CI is **green on that commit**. Then merge and log `{event: "merged under standing-yes"}`. If any guardrail is not met, fall back to the explicit ask — the standing yes never force-merges an unapproved, un-reviewed or red PR. The standing yes covers **merges only**: deploy/go-live, the pentest scope, and client-data go-live **always** ask, on every project, regardless of `merge_policy`. Record the reads that satisfied the guardrails (approvals, CI commit) using the project's scoped token, failing closed if it is missing (`security.md` 16).

## 3. Merge
Write `<folder>/MERGE-REQUEST-<lane>.md` exactly per `bridge.md` (`PF-MERGE v1`, `request_id = <slug>-merge-<lane>-<yyyymmddHHMM>`, `project`, `repo: <owner>/<slug>`, `pr_url`, `strategy: squash`). Drive Chrome per `bridge.md` on `lanes[<pm_lane>].code_url` with `/pf-next <slug> merge --lane <lane> --go`. Poll every 3 minutes for `MERGE-RESULT-<lane>.md` with first line exactly `PF-MERGE-RESULT v1` and the same `request_id`, up to 20 minutes. Fallback (empty `code_url`, sign-in page, or Chrome failed twice): "In your Claude Code session (lane `<pm_lane>`) type **`/pf-next <slug> merge --lane <lane>`** and confirm."

## 4. Record
On `ok`: `lanes[<lane>].status = "merged"`, log `{stage: "merge", lane, event: "merged"}`. On `failed` with a conflict note: tell the lane's owner to run `/pf-build --lane <lane>` again (the builder rebases on `main`), and leave status `ok` → it will be re-set by the rebuild. If **every** declared lane is now `merged`, set `gates.build = "approved"`, log it, and say "All lanes merged — run `/pf-deploy` when ready." Otherwise list the lanes still open.

`--all-ready`: run the above for each lane with status `ok`, asking once per lane.
