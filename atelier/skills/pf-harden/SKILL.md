---
name: pf-harden
description: "PM step after a deploy: makes the live product fast, findable and able to take a traffic spike — safety-net tests, performance budget on the live site, SEO + AI-engine visibility (Google, Bing, ChatGPT, Claude, Perplexity), a defensive security review (RLS, auth, input, headers, secret and dependency scan — own site only), database indexes, free-layer caching, a local k6 load test and a hosting-limits check — by writing HARDEN-REQUEST.md, driving Claude Code through Chrome to run /pf-next harden, polling for HARDEN-RESULT.md, then offering merge + redeploy. Use when the user says /pf-harden, 'harden the site', 'make it faster', 'will it survive traffic', 'survive going viral', 'fix the SEO', 'make ChatGPT find us', 'is it secure', or 'lock it down'. Supports --dry-run and --passes."
---

# /pf-harden [--passes safety,perf,seo,security,compliance,indexes,caching,load,limits] [--dry-run]

Post-launch hardening. Read first: `${CLAUDE_PLUGIN_ROOT}/references/performance-budget.md`, `seo-ai-visibility.md`, `security.md`, `deploy-rule.md` (cost posture), `bridge.md`, `handoff.md`.

## 0. Flags first
`--dry-run` → print the `HARDEN-REQUEST.md` that would be written, write nothing, ask nothing, stop. Seat identity = `--lane` (default `solo`); must equal `factory.json.pm_lane`, else "Only the PM lane (`<pm_lane>`) hardens." and stop. `--passes` defaults to all nine; `safety` is always included even if omitted.

## 1. Gate
Locate the project (named, else the only one, else ask). Read `factory.json`. Require `gates.build == "approved"`. Prefer a live site: use `deploy.live_url` when `deploy.status == ok`; otherwise say "No live deploy yet — hardening will measure a local copy instead; results are indicative" and continue with `live_url` empty. Never run on a project whose last build failed.

## 2. Explain and ask — always
Show in one short block what will happen, in the user's words: tests first so nothing breaks; speed check against the budget (score >= 90, loads under 2.5 s, no lag, no jumping); SEO and AI-visibility check (Google + Bing + ChatGPT, Claude, Perplexity crawlers can read every page, structured data, llms.txt, FAQ blocks); a defensive security review of your own site only (data-access rules, logins, input checks, security headers, secret and dependency scan) — read-only, no attack tools, no other sites; a legal/compliance check (dependency licences, privacy/terms/consent, data-deletion) that flags anything a lawyer should see — not legal advice; database indexes; free caching only (no Redis); a fake-traffic test on a local copy only, never the live site; a list of what would break first at 10x traffic with prices, **recommend only — nothing paid gets created**. Then AskUserQuestion: `Harden <slug> now? (passes: <list>)` Yes / No. Only Yes proceeds.

## 3. Hand-off (file-based — see `bridge.md`)
`request_id = <slug>-harden-<yyyymmddHHMM>`. Write `<folder>/HARDEN-REQUEST.md`:
```
PF-HARDEN v1
request_id: <id>
project: <slug>
code_path: <code root>/<slug>
live_url: <deploy.live_url or empty>
target: <deploy.target>
passes: <list>
```
Delete any stale `HARDEN-RESULT.md`. Store `harden.request_id`, `harden.status = requested`; log `{stage: "harden", event: "request written"}`. Hand off per `handoff.md`. **Mode A (event, default):** drive Chrome per `bridge.md` on `lanes[<pm_lane>].code_url` with `/pf-next <slug> harden --go` (fallback: "In your Claude Code session (lane `<pm_lane>`) type **`/pf-next <slug> harden`** and confirm."), then wake on the GitHub PR event; fall back to a slow poll (~every 15 min) for `HARDEN-RESULT.md` (first line exactly `PF-HARDEN-RESULT v1`, same `request_id`) up to 120 minutes. **Mode B (cloud):** run the harden passes inline in the cloud per `handoff.md` and read the result directly (load tests still run against a local copy with a test database, never the live URL). `--handoff event|cloud` overrides for this run.

## 4. Present
Record `harden.status`, `harden.pr_url`, `harden.branch`; log `{stage: "harden", event: "<status>: budget_met <yes/no>"}`. Show: the before/after speed table (route | score | LCP | INP | CLS | JS KB), the SEO table (route | title | description | schema | SEO score | crawlers 4/4), the security table (check | result | fixed/needs-you), indexes added, caching applied, load summary in plain words, the limits list with monthly costs, anything reverted, and `needs_decision` items as a separate "Paid — your call" list. Say plainly whether the site now meets the budget.

## 5. Merge and redeploy (ask)
If `status: ok`: AskUserQuestion `Merge the hardening PR into main and redeploy? Yes / No`. On Yes: write `MERGE-REQUEST-harden.md` per `bridge.md` (`repo`, `pr_url`, `strategy: squash`), drive `/pf-next <slug> merge --lane harden --go`, poll `MERGE-RESULT-harden.md` (20 min), then run the `/pf-deploy` flow from its step 4 (it asks "Deploy now?" itself). On No: "PR is open at <pr_url>; run /pf-harden again or merge later." If `status: failed`: show `notes`/`failures` and offer "run again with fewer passes" or "tell me what to fix".

Never: load-test a live URL, add Redis or any paid resource, upgrade a plan, push to `main` directly, or run without the Yes in step 2.
