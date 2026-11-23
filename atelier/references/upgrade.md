# Upgrade path — bringing an older project up to today's factory

Added in 2.2.0. A project built with an earlier version of the factory keeps working, but it lacks what later versions added. `/pf-upgrade` finds what is missing and adds it safely. `factory.json.factory_version` records the plugin version that created or last upgraded a project; it is empty on projects older than this field, which simply means "check everything".

## The principle
**An upgrade changes how well the project is protected and documented, not what the product does.** Its test is simple: the e2e suite gives the same result before and after. Anything that would change behaviour, data or cost is not part of the upgrade — it is listed separately and becomes its own normal build.

## What is checked (present / missing / not applicable — with the evidence)
| # | Capability | Present when | Adding it | Kind |
|---|---|---|---|---|
| U1 | State file is current | `factory.json` has every field in `state-schema.md` | add missing fields with their documented defaults; never overwrite a value; keep a dated copy first | state |
| U2 | Diagrams in the SPEC | `SPEC.md` has `## Diagrams` with one per page and flow | drawn from the code as built, confirmed by the owner | docs |
| U3 | Flow diagrams in the plan | the user journey and the screen map exist (`planning.md`) | drawn from the product as built | docs |
| U4 | One-command verify and the pre-push hook | a `verify` script and `.githooks/pre-push` (`verification.md` A) | added | code |
| U5 | e2e from the diagrams, with failure paths | `e2e/` has a spec per diagram | written for the product as it is today | code |
| U6 | Visual baseline | screenshot baselines exist (`verification.md` F) | captured from the current, approved look | code |
| U7 | The docs set | architecture, runbook, admin guide, changelog (`delivery.md`) | written from the code | docs |
| U8 | Secret scan and security headers | `security.md` items pass | fixed, one commit each | code |
| U9 | Live tag and a known last-good version | a `live-` tag on the deployed commit | tag the commit that is verifiably live | state |
| U10 | Test and production data are separate | `database` is `split` for a live product (`migrations.md` A) | planned with the owner; **its own build**, never bundled | data |
| U11 | Migrations are expand-then-contract | a migrations folder following `migrations.md` B | convention added; old migrations are left alone | code |
| U12 | Monitoring, alerts and rollback | `monitoring.*` is filled | `/pf-monitor` | account |
| U13 | Backups and a tested restore | `maintenance.backups`, `restore_tested` | `/pf-maintain` | account |
| U14 | Locale-ready basics | `i18n.md` A holds | fixed where cheap; listed where not | code |
| U15 | Search foundation | sitemap, no orphan pages, one-hop redirects (`seo-ai-visibility.md`) | `/pf-harden` | code |
| U16 | Dependencies and runtime are supported versions | `/pf-maintain` reports none end-of-life | `/pf-maintain` — not repeated here | code |
| U17 | Hand-offs go only to the authorized session | every lane that has a `code_url` has a `SESSION-<lane>.md` with `status: linked` (`session-link.md`) | invitations written; the user runs `/pf-link` once in each lane's Code session | account |
| U18 | The live tracker has something to read | `BACKLOG.json` is in the project folder and passes its check; each lane's checkout has `.pf-activity.json` | write `BACKLOG.json` from the plan and the lane files (`backlog.md`); the user runs `/pf-link` once more in each lane's Code session | state |
| U19 | The code passes the attack checks | the last build or harden result has `sec-check: pass` (`attack-checks.md`) and, for a web product, `web-check: pass` (`web-checks.md`) | run both checkers read-only, fix each `FAIL` as its own commit through the normal build path | code |
A capability that an option controls (a status page, infrastructure as code, a canary) is not "missing" on a project that never chose it (`options.md`).

## The order — safety nets first
1. **Assess, read-only.** Report U1–U19 with evidence, effort (small / medium / large) and risk. Nothing is changed.
2. **The owner picks** by number.
3. **State and docs** items first (U1–U3, U7, U9, U18): no code risk.
4. **Then the nets** (U4, U5, U6): so that every later change is checked by them. If e2e written for the current product fails, that is a real bug found — it is reported and fixed as its own build, not hidden inside the upgrade.
5. **Then the code items**, one commit each, through the normal build path, with a preview before anything is live: on a team project a PR lane named `upgrade` (`/pf-build` → review → `/pf-merge` → `/pf-deploy`); on a solo project a `/pf-build` change request on its `solo` lane, deployed preview-first as always.
6. **Account items** are handed to the stage that owns them (`/pf-monitor`, `/pf-maintain`, `/pf-harden`); `/pf-upgrade` only lists them.
7. Set `factory_version` to the current plugin version and record `upgraded: { date, from, items }`.

## Adopting a project the factory did not build
`/pf-upgrade <slug> --adopt <repository>`: read the repository first, change nothing. Write `factory.json` and a `SPEC.md` that describes the product **as it is**, and get the owner's yes to that description before anything else — a wrong SPEC would make every later check wrong. Then the same assessment and order as above. Stacks the factory has no target or contract for are named as such; they are not forced into one.

## Never
Change behaviour inside an upgrade. Touch production data. Overwrite a value in `factory.json`. Re-baseline screenshots to make a difference disappear. Skip the preview. Mark a capability present without the evidence.
