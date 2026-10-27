---
name: pf-build
description: "Builds an approved Atelier design for one lane (solo by default): writes SPEC.md and BUILD-REQUEST-LANE.md, then hands off by the chosen mode (A, default: build on the user's machine and wake on the GitHub event; B: build in the cloud, result inline), and presents the repo, PR and preview for approval. Use when the user says /pf-build, /pf-build --check, 'build the product', 'build it', or 'turn the design into code'. Supports --handoff event|cloud, --dry-run and --validate-only."
---

# /pf-build [--lane <name>] [--handoff event|cloud] [--dry-run] [--validate-only] [--check]

`--lane <name>` names this seat's lane; omitted = `solo`. The lane must exist in `factory.json.lanes`; otherwise say "Unknown lane — run `/pf-lanes list`." and stop. All request/result files below are lane-suffixed: `BUILD-REQUEST-<lane>.md`, `BUILD-RESULT-<lane>.md`.

Turn an approved design into a repo and a preview, then stop for approval. Read these first:
- `${CLAUDE_PLUGIN_ROOT}/references/state-schema.md`
- `${CLAUDE_PLUGIN_ROOT}/references/spec-format.md`
- `${CLAUDE_PLUGIN_ROOT}/references/bridge.md`
- `${CLAUDE_PLUGIN_ROOT}/references/handoff.md`

## 0. Flags first

Before reading or writing anything: `--check` → go straight to the check paragraph in step 4; `--validate-only` → only run the eight-heading check on the existing `SPEC-<lane>.md` and stop (do not regenerate it); `--dry-run` → do steps 1–2 in memory, print what `BUILD-REQUEST-<lane>.md` would contain, write nothing, stop. Seat identity = the `--lane` given (default `solo`).

## 1. Gate

Locate the project: the one the user names, else the only `factory.json` under the connected `Atelier` folder. If there is more than one project and none was named, ask with AskUserQuestion which one. Read it. If `gates.design != "approved"`, say exactly: "Design isn't approved yet — run /pf-design and approve it first." and stop. Write nothing.

## 2. SPEC-<lane>.md

**PM lane builds first.** If this lane is not `pm_lane` and `factory.json.repo_url` is empty, say "The PM lane builds first (it scaffolds the repo); wait for it, then run this again." and stop.

Write `<folder>/SPEC-<lane>.md` per `spec-format.md`, plus a `## Scope` section as the first heading after the title: `all` for solo, otherwise this lane's screens/routes from `lanes[<lane>].scope`. Screens/Routes/Acceptance sections list **only** items in scope; other lanes' items appear one line each under `## Scope` as "owned by lane <x>" so the builder knows what not to touch. Content:
- Brief and Stack from `factory.json.brief` (stack verbatim — it is locked). **The Brief must include the SEO inputs from `references/seo-ai-visibility.md` section A** (`Entity:`, `Audience + locale:`, `Primary keywords:`, `Questions:`, `Pages that must rank:`); if the design brief lacks any, ask the user with AskUserQuestion before writing the SPEC — never invent company facts.
- Screens: read the Design artifact (`artifacts.design_url`, Artifact `read`); one `### <Screen>` per artboard in canvas order with `Route:`, `Purpose:`, `Copy:` (verbatim text from the artboard), `Components:`.
- Tokens: read `artifacts.design_system_url`; emit CSS custom properties for light and dark colours, type scale, spacing, radius.
- Components: inventory from the artboards with a props sketch each.
- Data model and Routes / API: from `brief.backend` and `brief.data`; `None` when no backend.
- Acceptance checks: at least one per screen (renders + headline present) and one per route; numbered. Always end with the standing check: `Performance budget met on every screen (references/performance-budget.md: mobile score >= 90, LCP <= 2.5 s, INP <= 200 ms, CLS <= 0.1, route JS <= 200 KB)` and `SEO + AI visibility met on every screen (references/seo-ai-visibility.md: Lighthouse SEO 100, A11y >= 95, robots/sitemap/llms.txt live, 4/4 AI crawlers fetch content, valid JSON-LD)` and `Security met on every screen (references/security.md: RLS on all tables with passing isolation tests, auth walls, input validation, security headers, npm audit and secret scan clean)` and `Code is simple and handoff-ready (references/code-simplicity.md: no unused code or deps, lint-complexity clean, duplication under threshold, reuse over reinvention, idiomatic and readable — without lowering quality)` and `Design standard met on every screen (references/design-standard.md: tokens-only styling, Inter + open icons (no Apple fonts/symbols), clear hierarchy, visible focus + AA contrast, reduced-motion honoured, and the chosen design_direction is expressed with motion in proportion — GPU-only, no CLS, within the perf budget)` and `Legal/compliance checklist met (references/compliance.md: dependency licences permissive or flagged, privacy + cookie consent when personal data is collected, terms + data-deletion for account apps, nothing copied, legal sign-off items flagged)` and `Adversarial edge-case tests pass on every key flow (references/security.md B: 5 break-it tests per flow, idempotent money writes)` and `Official /code-review and /security-review run and Critical/High findings fixed`.

Validate: all eight headings present in order. If any is missing say "SPEC-<lane>.md is missing: <heading>" and stop.

`lanes[<lane>].code_path` = `<code root>/<slug>` for solo / the PM lane, else `<code root>/<slug>--<lane>`. Append `log {stage: "build", lane, event: "spec written"}`.

## 3. (flags handled in step 0)

## 4. Hand-off (see `handoff.md` for the two modes)

**Pick the handoff mode first.** Read `handoff.mode` from `factory.json`. If `--handoff event|cloud` was passed, use it for this run (and, on `/pf-build --handoff …` with no build, record it as the new default and stop). If `handoff.mode` is unset and this is the project's first build, present **both modes** with AskUserQuestion using the pros/cons/**cost** from `handoff.md` — **"A — Local build + event wake (Recommended)"** first, then **"B — Cloud build"** — and record the answer as `handoff.mode` (`event`|`cloud`), `log {stage:"build", event:"handoff mode = <mode>"}`. **Guardrail:** if `brief.data_sensitivity == "high"`, do **not** offer B by default — default to `event`; only if the user explicitly asks for `cloud`, warn per `handoff.md` (client-data path stays local; needs Key Vault + the Phase-2 safety net) and confirm once more before recording it. The pentest step is always `event` regardless.

Make `request_id` = `<slug>-<lane>-<yyyymmddHHMM>`. Write `<folder>/BUILD-REQUEST-<lane>.md` exactly per `bridge.md` with `request_id`, `project: <slug>`, `spec: SPEC-<lane>.md`, `code_path` (the lane's), `lane`, `branch`, `mode: continue` **only** when `factory.json.repo_url` is non-empty, and `notes:` only on a fix re-run. Delete any stale `BUILD-RESULT-<lane>.md`. Write the lane state to `<folder>/lanes/<lane>.json` (`status = requested`, `request_id`, `request`, `approved = false`); if this seat is the PM, also mirror into `factory.json.lanes` and set `gates.build = pending`. Append `log {stage: "build", lane, event: "request written"}`.

### Mode A (event) — build on your machine
**Drive Claude Code through Chrome** per `bridge.md` → "Chrome hand-off": verify the page is this project's Code session, type `/pf-next <slug> build --lane <lane> --go`, Enter, confirm, close the tab, set `status = building`. If `code_url` is empty, the page is a sign-in/unknown session, or Chrome fails twice: fall back to the exact line **without `--go`** (`/pf-next <slug> build --lane <lane>`) and name the window ("your Claude Code session for lane `<lane>`"). Only after the confirmation step say "sent".

Then tell the user:

> Build request written and sent to your Claude Code session (lane `<lane>`). I'll pick up the result here automatically.

(Fallback wording when Chrome could not type it: "Build request written. In your Claude Code session for lane `<lane>`, type **`/pf-next <slug> build --lane <lane>`** and confirm. I'll pick up the result here automatically.")

Then **wake on the event** (not a blind timer): subscribe to the repo's pull-request activity (and `main` pushes for solo). When the builder opens the PR / pushes, that notification wakes you — read `<folder>/BUILD-RESULT-<lane>.md` whose first line is exactly `PF-BUILD-RESULT v1` and whose mtime is newer than `BUILD-REQUEST-<lane>.md`. Only if no event arrives, fall back to a slow poll (~every 15 min) up to 90 minutes. Each check is quiet — say nothing unless the result arrived or the 90 minutes ran out ("Still no result after 90 minutes — run `/pf-build --check` after the build finishes; re-running the hand-off is safe, the builder continues rather than restarting."). Any file that does not start with the exact header is "no result yet".

**`/pf-build --check`** (manual fallback): do the same single check once and continue or report "No result yet".

### Mode B (cloud) — build in the cloud, result inline
Used when `handoff.mode == "cloud"` (or `--handoff cloud`), and never for `data_sensitivity: high` without the warned yes in step 4. There is no Chrome hand-off and no polling: the PM runs the builder itself in its own cloud session — clone the repo from GitHub, run the same from-spec build to every contract, push `lane/<lane>` (or `main` for solo), open the PR, and write `BUILD-RESULT-<lane>.md` into the project folder and commit it — then read that result inline and go to step 5. Requires GitHub clone/push and the target's deploy access reachable from the cloud per `/pf-setup handoff` (Key Vault / short-lived token, never a stored long-lived secret). If that access is not set up, say so and fall back to mode A for this run.

## 5. Record and stop

From the result file (its `request_id` must equal the lane's; otherwise it is stale — "no result yet"): write `repo_url` (never overwrite a non-empty `repo_url` with an empty one), and in `lanes/<lane>.json` `pr_url`, `preview_url`, `result`, `status = ok|failed`; PM mirrors into `factory.json`. Append `log {stage: "build", lane, event: "<status>: acceptance <n/m>"}`. `gates.build` stays `pending` here.

If `status: failed`, show `failures:` verbatim, keep the gate `pending`, and stop.

Otherwise show: repo link, preview link, a screenshot of the preview if a browser tool is available, and the acceptance table. Say: "Say **yes** to approve the build, or tell me what to fix." Stop.

## 6. Approval handling

On an approval word (per "Approval words" in `state-schema.md`): set `lanes[<lane>].approved = true`. If `lanes[<lane>].branch == "main"` (direct push, i.e. solo) → the code is already on `main`: set `status = "merged"` and, if every lane is merged, `gates.build = "approved"`. Otherwise (PR lane) → say "Approved. The PM seat merges it with `/pf-merge --lane <lane>`." A "yes, but …" with a change is a fix request; on vague positives ask with AskUserQuestion "Approve the build? (yes/no)". Fix requests → re-run step 4 with a new `request_id`, `mode: continue` and a `notes:` line describing the fix; the Chrome hand-off runs again; polling as before. On approval append `log {stage: "build", lane, event: "approved"}`; for solo say "Build approved. Run `/pf-deploy` when ready."

## Never
- Send a spec with a missing heading.
- Put a secret value in `SPEC.md`, `factory.json`, or the message.
- Re-scaffold a project that already has `repo_url` — always `mode: continue`.
- Write `factory.json` from a non-PM seat (write `lanes/<lane>.json` instead).
