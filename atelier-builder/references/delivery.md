# Delivery — handing a finished product to its owner

Added in 1.1.0 (18 Nov 2026). "live and tested" is not "delivered". A client (or your own future self) must be able to **run, change and recover the product without the factory**. Delivery is the last stage, run by `/pf-deliver` after deploy, harden and monitor — and for a `data_sensitivity: high` project after a clean pentest. It is a human gate: the product is delivered when the recipient accepts it, never when Claude says so. (Not to be confused with `handoff.md`, which is the *seat* handoff between Cowork and Claude Code during a build.)

## A. What is in the repo (written by every build, so it never drifts)
The builder keeps four documents current on every build (`pf-build-from-spec` §6b) — delivery only checks they exist and are current:
- **`docs/ARCHITECTURE.md`** — one page: what the product is, the stack and why, the folder map, and every rendered diagram from `docs/diagrams/` embedded in order (app → pages → features). The diagrams are the architecture; this page is their table of contents.
- **`docs/RUNBOOK.md`** — for whoever operates it: run locally, run `verify`, deploy, roll back, apply a migration, restore from backup (the tested step from `maintenance.md` C), rotate each secret (names only), where logs and alerts are, and **"when something breaks"** — a short first-response list per failure the monitoring can raise (site down, error spike, expired certificate, database full, a third-party key expired or rate-limited): what to check first, the command, and when to roll back; plus the three ready customer notices (*investigating*, *identified*, *resolved* — `monitoring.md` F) and every kill switch with the config name that flips it (`rollout.md` A4).
- **`docs/ADMIN-GUIDE.md`** — for the non-technical owner, in plain language: how to sign in as admin, every task they will do themselves (add content, manage users, read the numbers), what each alert email means, and who to call. No commands.
- **`CHANGELOG.md`** — one dated entry per build under the user-visible change, newest first; each live deploy is marked by a `live-<yyyymmdd-HHMM>` git tag on the deployed commit.

## B. The delivery pack (assembled by `/pf-deliver`, a living doc)
One document for the recipient, built from `factory.json`, the result files and the repo — nothing invented:
1. **What you are getting** — the product in two sentences, the live URL, the repo, the date, and the launch video if one was recorded (`promo.video`).
2. **What was built** — the screens and features, each linked to its diagram.
3. **Proof** — acceptance checks passed (n/n), `verify` result and e2e count, the contract results (performance, SEO + AI visibility, security, accessibility, simplicity, compliance) from the latest build and harden, and for a data-sensitive project the pentest outcome. Numbers and dates, not adjectives.
4. **How it runs** — hosting target and plan, monthly cost forecast vs actual (`maintenance.spend`), monitoring and alerts in place, backup location and the date of the last successful restore drill.
5. **What you own and how it transfers** — section C, as a checklist with a status per line.
6. **Open items** — every `needs_decision`, held major upgrade, "needs legal review" flag and known limitation, stated plainly. An empty list is written as "None".
7. **Support** — what happens after today: the maintenance schedule if one is agreed, what is and is not covered, how to request a change. Terms come from the user; the pack never invents a price, an SLA or a warranty.
The pack contains **no secret, no personal data and no customer record** — names of env vars only.

## C. Ownership transfer (guided; the owner clicks — Claude never does)
Every item is an account or settings change, so `/pf-deliver` opens the page, says exactly what to do, and stops (`pf-setup` hard rules):
- **Code** — transfer the GitHub repo to the client's organization, or add them as owner/collaborator. Before the repo leaves, the diagrams and docs are reviewed like code (they map routes, tables and auth walls).
- **Hosting, database, domain, monitoring** — move each resource to the client's account, or add the client as owner and remove the factory's access afterwards. The DNS registrar account stays the client's from the start wherever possible.
- **Secrets — rotate after transfer, always.** Every credential the factory ever held for the project (deploy tokens, database keys, API keys) is rotated by the new owner once they have access, per `maintenance.md` E, and the factory's copies are removed from the build machine's env. A transfer without rotation is not complete.
- **Factory access** — decide and record: ended, or retained for an agreed maintenance period with its scope.

## D. The gate
`gates.delivery`: `pending` → `approved` only on an approval word (`state-schema.md`) to **"Has the recipient accepted the delivery?"** — after the pack is shared and the transfer checklist shows no unresolved line the recipient needs. Recorded in `factory.json.delivery` (`recipient` — a name or organization, no contact details; `pack_url`; `transfer` — per-item status; `accepted` date; `access_after` — `ended` or the retained scope). An internal product (the user is the owner) still gets the docs and the pack; the transfer section reads "owner unchanged" and the gate is his own yes.

## Never
- Mark a product delivered without the recipient's acceptance, or with a failing `verify`, an open Critical/High security finding, or no successful restore drill on a product that holds data.
- Put a secret value, a customer record or personal contact details in the pack or the repo docs.
- Transfer, share or change access on any account yourself — every such step is the owner's click.
- Promise support terms, prices or legal assurances the user has not stated.
