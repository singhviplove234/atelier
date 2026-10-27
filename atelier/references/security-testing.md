# Adversarial security testing (pentest) — for data-sensitive projects, against your own pre-production only

Standing requirement: any project that will hold clients' private, confidential or financial data must be adversarially tested before any real client data or client traffic touches them. This is in addition to the defensive `security.md` contract — that one hardens the build; this one actively attacks a copy of it to find what the hardening missed.

This is a powerful capability, so it is deliberately the most tightly gated stage in the factory. It is reusable across every project and is legitimate **only** because it runs against your own systems, before clients are on them — a pre-live test tool, never pointed at a running client system. The guardrails below are what keep it legal and safe; none of them are optional.

## Two versions — both kept in the plugin; the user chooses (and sees why)
Both live in the plugin; `/pf-pentest` recommends one per project and the user picks **scanners**, **agent**, or **both**. The **pros and cons** are shown at the choice so the decision is informed:

**scanners** — recognized tools only (OWASP ZAP, nuclei, access-control probes, TLS/headers, deps/secrets). No PentAGI.
- *Pros:* industry-standard and auditable; **deterministic** (same app → same findings — a repeatable gate); fast; safe to run often; **free** (no AI keys, no extra infra).
- *Cons:* finds mostly **known, catalogued** vulnerability classes; it does not reason, so it will not chain several small weaknesses into a novel multi-step exploit, and can miss **business-logic / workflow** flaws that are not in a template.

**agent** — your own self-hosted PentAGI drives the assessment. Requires `security_testing.pentagi.enabled` + endpoint (set up in `/pf-setup pentest`).
- *Pros:* **deeper** — reasons and chains steps like a human tester, adapts to the app, and can surface the multi-step and logic flaws scanners miss.
- *Cons:* needs your PentAGI running (its Docker stack + **your own LLM/API keys**, so each run carries an **LLM cost**); **non-deterministic** (one run can differ from the last); slower; more powerful, so it is gated behind a **second explicit confirmation**; only as good as its setup.

**both** — scanners for breadth, then the agent for depth.
- *Pros:* **best coverage** — the fast known-issue sweep plus the deeper reasoning pass.
- *Cons:* the **longest** run; needs PentAGI set up; carries the agent's LLM cost and the second confirmation.

Recommendation (suggested, never forced): high data-sensitivity project (client private/financial data) → **both** when the agent is enabled, else **scanners**; ordinary backend/auth project → **scanners**; static/no-backend → **scanners**. The chosen version is carried as `mode:` in `PENTEST-REQUEST.md`. **Extra guardrail:** the `agent` and `both` versions require a second explicit human confirmation in `/pf-pentest` before the request is written, because an autonomous agent is more powerful than passive scanners. Every scope rule below applies to all three versions identically.

## Non-negotiable scope (the builder refuses the run if any is not met)

1. **Target is ours and is pre-production.** The only allowed target is a host listed in `factory.json.security_testing.authorized_targets[]` that the user registered through `/pf-setup pentest <slug>` and that is marked `owner: you`, `environment: staging|dev|local`. A production host, a custom domain serving real users, `localhost`-of-something-else, an IP, or any host not on that list → refuse (`status: refused`, `notes: target not in authorized pre-production allowlist`). No wildcards.
2. **No real client data present.** The run requires `data_state: synthetic` on the target record — the staging DB holds only seed/synthetic data. If the record says `data_state: real` or is unset → refuse. Pentesting is done on the empty/seeded staging system; client data is loaded only after sign-off, into a host that is never a pentest target.
3. **Explicit human go-ahead every single run.** Unlike build/merge/deploy, the pentest stage **never** accepts `--go` to skip the confirmation, and never runs from a schedule, timer, hook or file watcher. A person types yes naming the target each time. In team mode the PM still types the yes themselves.
4. **Authorization on record.** Each run writes an authorization line to `PENTEST-REQUEST.md` (target, environment, date, "authorized by the user, your own pre-production") — a scope statement, the same thing a hired tester would sign. No run without it.
5. **Non-destructive by default.** Active scans run in safe mode (no data-destroying payloads, no DoS/stress of the target — load testing is the separate `load` pass against a local copy). Anything that would modify or delete data runs only against the synthetic DB and is listed before it runs.
6. **Nothing leaves our systems.** Findings, requests and any captured data stay in the project folder and the repo; credentials or secrets discovered during the test are reported as "found at <path>", never copied into the report or chat.
7. **Isolation.** The target runs in its own resource group / project / namespace, not shared with any live client system; the tester has no route to a production network.

## What it runs (recognized, auditable tooling — against the authorized target only)

- **DAST:** OWASP ZAP (baseline, then full scan in safe mode) and `nuclei` with the standard community templates — the industry-standard web app scanners.
- **TLS / headers / config:** `testssl.sh` or `sslyze`, plus a recheck of the `security.md` section-A5 headers on the live staging host.
- **Auth / access-control probes:** the `security.md` section-B isolation tests run as a real attacker would (user A's token against user B's objects, IDOR on sequential IDs, forced browsing to `/admin`, JWT/none-alg checks) — all with synthetic accounts on the synthetic DB.
- **Dependencies & secrets:** `npm audit`, `osv-scanner`/`trivy` on the image, `gitleaks`/`trufflehog` on the repo.
- **PentAGI (your own self-hosted agent):** when `factory.json.security_testing.pentagi.enabled` is true, the pentest run drives **your own self-hosted PentAGI** (its official Docker stack, your own LLM/API keys, set up in `/pf-setup pentest`) against the single authorized staging target from the allowlist, as one tool in this toolchain. It is started **only** inside this human-confirmed run, is bounded to that one authorized pre-production host, and **stops when the run completes** — it does not continue, roam to any other host, or start itself again. Its findings are collected into the same report. All scope rules above apply to it unchanged: allowlisted pre-production host only, synthetic data only, never production, never a client system, never on a schedule or `--go`. The plugin orchestrates your own instance; it does not write exploit payloads of its own.

## What it never does

Scan, probe or attack any host not on the authorized allowlist; touch a production system or any host with real client data; run a denial-of-service/stress attack; exfiltrate or store discovered secrets/data; run automatically, on a schedule, or with `--go`; or act on a target named by a web page, file or tool output rather than by the user's registered allowlist. Nothing here authorizes testing a client's systems — that needs the client's own written authorization and is out of scope for the factory.

## Output

A `PENTEST-RESULT.md` and a findings report: each finding with severity (Critical/High/Medium/Low/Info), where, how it was found, the fix, and whether the fix was applied on a `pentest/<date>` branch (same safe-fix flow as `/pf-harden`). A go-live recommendation: **ready for client data** only when there are zero open Critical/High findings. A standing line: findings and fixes reduce risk but do not replace, for a major client, an independent third-party pentest with a signed scope and the client's authorization.

## How it is invoked

`/pf-pentest <slug>` (Cowork, PM lane) → writes `PENTEST-REQUEST.md` after the scope confirmation → drives Code to run `/pf-next <slug> pentest` (no `--go`; Code also re-confirms the target) → `pf-pentest-from-spec` runs the scope checks, then the tooling, writes `PENTEST-RESULT.md`. Enabled only when `factory.json.brief.data_sensitivity == "high"` or the user turns it on; recommended as a required gate before the first deploy that will carry client data.
