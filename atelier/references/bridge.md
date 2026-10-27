# Cowork ⇄ Claude Code bridge (v2) — files + Chrome

Sessions cannot message each other (verified 2026-10-16), so the bridge is: **request/result files in the project folder**, and the Cowork seat **typing the command into the Code session through Chrome**. No ListAgents / SendMessage. No auto-trigger from files: the only thing that starts a build is a `/pf-next` typed into the Code session — by the user, or by the Cowork seat on the user's behalf through Chrome.

**Handoff mode decides the completion signal — see `references/handoff.md`.** This file describes **mode A** (local build on the user's machine, the default): Chrome starts the job, and the PM then **wakes on the GitHub PR/push event** (poll only as a fallback), not a blind timer. **Mode B** (cloud build) does not use this Chrome path at all — the PM runs the build inline in its own cloud session and gets the result directly; see `handoff.md`.

## Files (lane-suffixed)

`BUILD-REQUEST-<lane>.md` / `BUILD-RESULT-<lane>.md`, `MERGE-REQUEST-<lane>.md` / `MERGE-RESULT-<lane>.md`, `DEPLOY-REQUEST.md` / `DEPLOY-RESULT.md`, `HARDEN-REQUEST.md` / `HARDEN-RESULT.md`, `PENTEST-REQUEST.md` / `PENTEST-RESULT.md` in the project folder. The pentest never auto-runs and `--go` is ignored for it. `/pf-harden` works on a `harden/<yyyymmdd>` branch and merges it through the normal merge files with lane name `harden`. Solo projects use lane `solo`. Deploy has no lane: it deploys `main`. Every request carries a `request_id`; the typed command names the exact request, so a stale or foreign request can never run by accident.

A result is valid only if its first line is exactly the expected header and its mtime is newer than the request. Anything else is "no result yet".

## Chrome hand-off (what `/pf-build` and `/pf-deploy` do after writing a request)

Needs: the lane's `code_url` in `factory.json` (from `/pf-setup`), the Claude-in-Chrome tools, and the extension allowed on claude.ai.

1. `tabs_context_mcp` (createIfEmpty) → `tabs_create_mcp` → `navigate` to `code_url`.
2. **Verify the session before typing**: `get_page_text`; the page must show this project's Code session — its title contains `lane <lane>` and the project slug (set by the first message `/pf-setup` asks for) and a line says it is connected to the user's computer — and must not be a sign-in page or a "session ended" notice. If it is a sign-in page, an unknown session, or shows no prompt box → **fall back immediately** (do not retry).
3. `find` "the prompt / message box"; `left_click` it; `type` exactly `/pf-next <slug> build --lane <lane> --go` (merge: `/pf-next <slug> merge --lane <lane> --go`; deploy: `/pf-next <slug> deploy --go`; harden: `/pf-next <slug> harden --go`; pentest: `/pf-next <slug> pentest` **with no --go**); `key` Enter.
4. Wait 5 s; `screenshot` once; confirm the command was accepted (prompt cleared or a reply started). Set `lanes[<lane>].status = building`, log `{stage: build, lane, event: "pf-next typed via Chrome"}`.
5. `tabs_close_mcp`.
6. **Wake on the event (mode A), poll only as fallback.** Subscribe to the repo's pull-request activity (and `main` pushes for solo); when the builder opens the PR / pushes, that GitHub notification wakes the PM, which reads the validated result file at once. If no event arrives, fall back to a slow poll (~every 15 min) up to the stage timeout: build 90 min, deploy 60, harden 120, pentest 180. (The old 3-minute blind poll is gone as the primary path; see `handoff.md`.)

If steps 1, 3 or 4 fail twice (no tab, prompt box not found, extension missing), or step 2 fails once, **fall back**: tell the user exactly which window ("your Claude Code session for lane `<lane>`") and the exact line to type **without `--go`** so the user sees the confirm — `/pf-next <slug> build --lane <lane>` — and keep polling. Never retry Chrome more than twice per request. After the desktop app restarts, `code_url` is stale: `/pf-setup` item 2 again.

Deploy and merge use the PM lane's Code session (`lanes[<pm_lane>].code_url`).

## File shapes (verbatim)

`BUILD-REQUEST-<lane>.md`
```
PF-BUILD v1
request_id: <slug>-<lane>-<yyyymmddHHMM>
project: <slug>                      ← the builder resolves <watch dir>/<slug>; no absolute path
spec: SPEC-<lane>.md                 ← relative to the project folder
code_path: <code root>/<slug> | <code root>/<slug>--<lane>
lane: <lane>
branch: main | lane/<lane>
mode: continue        ← optional hint; the builder decides by what is on disk/GitHub
notes: <fix request>  ← optional; on a re-run after "tell me what to fix"
```

`BUILD-RESULT-<lane>.md`
```
PF-BUILD-RESULT v1
request_id: <echoed>
status: ok|failed
lane: <lane>
repo_url: <url or empty>
pr_url: <url or empty>        ← empty for solo (pushed to main)
preview_url: <url or empty>
acceptance: <n passed>/<n total>
failures: <one line per failed check, or none>
notes: <short free text>
```

`MERGE-REQUEST-<lane>.md`
```
PF-MERGE v1
request_id: <slug>-merge-<lane>-<yyyymmddHHMM>
project: <slug>
repo: <owner>/<slug>
pr_url: <url>
strategy: squash
```

`MERGE-RESULT-<lane>.md`
```
PF-MERGE-RESULT v1
request_id: <echoed>
status: ok|failed
notes: <short; on a conflict: "conflict with main — lane must rebase and rebuild">
```

`DEPLOY-REQUEST.md`
```
PF-DEPLOY v1
request_id: <slug>-deploy-<yyyymmddHHMM>
project: <slug>
code_path: <code root>/<slug>
target: <name from references/targets/>
```

`DEPLOY-RESULT.md`
```
PF-DEPLOY-RESULT v1
request_id: <echoed>
status: ok|failed
live_url: <url or empty>
http_status: <code or empty>
notes: <short free text>
```

`HARDEN-REQUEST.md`
```
PF-HARDEN v1
request_id: <slug>-harden-<yyyymmddHHMM>
project: <slug>
code_path: <code root>/<slug>
live_url: <url or empty>
target: <name from references/targets/>
passes: safety,perf,seo,security,compliance,indexes,caching,load,limits
```

`HARDEN-RESULT.md`
```
PF-HARDEN-RESULT v1
request_id: <echoed>
status: ok|failed
branch: harden/<yyyymmdd>
pr_url: <url>
perf_before / perf_after / budget_met / indexes_added / caching / load / limits / reverted / needs_decision / notes  ← see pf-harden-from-spec
```

Rules: plain text; first line is the version header; secrets never appear (env var names only); the builder deletes nothing.
