---
name: pf-deliver
description: "Final stage: hands a finished Atelier product to its owner or client. Checks the repo's own docs (architecture with every diagram, runbook with the incident first-response list, admin guide, changelog), assembles a delivery pack from the recorded proof (acceptance, verify + e2e, contract results, pentest, monitoring, backups and the last restore drill, costs, open items), walks the ownership transfer of repo, hosting, database, domain and monitoring with secrets rotated afterwards, and records the recipient's acceptance. Use when the user says /pf-deliver, 'hand it over', 'deliver to the client', 'client handover', 'prepare the handover pack', or 'transfer the project'. Supports --check and --dry-run. Never transfers or changes access on any account itself, and never marks a product delivered without the recipient's acceptance."
---

# /pf-deliver [slug] [--check] [--dry-run]

Turn a live, hardened, monitored product into something its owner can run, change and recover **without the factory**. Read first:
- `${CLAUDE_PLUGIN_ROOT}/references/state-schema.md`
- `${CLAUDE_PLUGIN_ROOT}/references/delivery.md` (this stage's contract — follow it)

## 0. Flags
`--check`: print the delivery status (docs present, pack link, each transfer line, accepted or not) from `factory.json` and stop — read only `state-schema.md`. `--dry-run`: run steps 1–3 in memory, print the pack outline and the transfer checklist, write nothing, stop. PM seat only (`--lane` must equal `factory.json.pm_lane`).

## 1. Gate — is it ready to hand over?
Locate the project (the one the user names, else the only one; if several and none named, ask with AskUserQuestion). Read `factory.json`. Stop, naming exactly what is missing, unless all of these hold:
- `gates.deploy == "approved"` and `deploy.live_url` is set.
- The latest build result carries `verify: pass` (`references/verification.md`).
- `harden.status == "ok"`, or the user says in words to deliver without hardening (record that in Open items).
- `monitoring.uptime` is set, or the same explicit waiver.
- When the product holds data: `maintenance.restore_tested` records a successful restore drill. No waiver — a product nobody has proven can be restored is not delivered.
- When `brief.data_sensitivity == "high"`: `security_testing.status == "ok"` with `critical_high_open == 0`. No waiver.

## 2. Docs — check, never write here
Read the repo with the project's **scoped token** (fail closed — `security.md` 16): `docs/ARCHITECTURE.md`, `docs/RUNBOOK.md`, `docs/ADMIN-GUIDE.md`, `CHANGELOG.md` and `docs/diagrams/` must exist, and the runbook must contain its "When something breaks" section. The builder writes these on every build (`pf-build-from-spec` §6b). If any is missing or names something that no longer exists — a project built before 0.3.0, usually — do not write them yourself: say "The repo's docs need a refresh — run `/pf-build --lane <pm_lane>` with the note `refresh docs`", and stop.

## 3. Recipient and terms — asked, never assumed
With AskUserQuestion, a few at a time, skipping what `factory.json.delivery` or the plan already holds: who receives it (a name or organization — **no contact details are stored**); for each of code, hosting, database, domain and monitoring, whether it is **transferred** to the recipient or the recipient is **added as owner**; whether the factory's access **ends** or is **retained** for maintenance, and with what scope; and the support terms in the user's own words. Never invent a price, an SLA, a warranty or a legal assurance. For an internal product the user is the recipient: the transfer section reads "owner unchanged".

## 4. The delivery pack
Assemble the pack per `delivery.md` section B as a **living doc** (Claude Docs), strictly from recorded facts — `factory.json`, the latest `BUILD-RESULT`, `HARDEN-RESULT`, `PENTEST-RESULT` and `DEPLOY-RESULT`, the repo docs and `maintenance`: what you are getting · what was built (each screen and feature linked to its diagram) · proof (numbers and dates) · how it runs (target, cost forecast vs actual, monitoring, backups, last restore drill) · ownership and transfer checklist · open items (or "None") · support. No secret value, no customer record, no personal contact detail — env var **names** only. Record the link as `delivery.pack_url`. Show it and ask the user to read it before it goes anywhere; **sharing it with the recipient is his action**, not yours.

## 5. Ownership transfer — guided, one item at a time
Per `delivery.md` section C and the `/pf-setup` hard rules: for each line of the checklist, open the exact page in Chrome, say what to do, pre-fill only non-secret fields, and stop — "Your turn: check it and click <button>." Never click Transfer, Invite, Remove, Save or Delete; never type a password, token or code. Order: (1) review the repo's diagrams and docs like code before the repo leaves; (2) code; (3) hosting; (4) database; (5) domain; (6) monitoring and alert recipients; (7) **rotate every secret the factory held**, by the new owner, per `maintenance.md` E — and remove the factory's copies from the build machine's env (give the user the exact names to delete); (8) end or scope the factory's access as agreed. After each, confirm with AskUserQuestion and write the status into `delivery.transfer` (`done` / `pending — <who>` / `not applicable`). A transfer with secrets not yet rotated is recorded as incomplete.

## 6. The gate — recipient's acceptance
When the pack has been shared and no transfer line the recipient needs is unresolved, ask with AskUserQuestion: **"Has the recipient accepted the delivery?"** Flip `gates.delivery = "approved"` only on an approval word (`state-schema.md`), then record `delivery.accepted` (date) and `delivery.access_after`, and append `log {stage: "deliver", event: "accepted"}`. Anything else leaves it `pending`; re-running `/pf-deliver` resumes from the first unresolved line. If the factory's access is retained, point to `/pf-maintain --schedule`; if it ended, say plainly that `/pf-maintain`, `/pf-grow` and `/pf-monitor` no longer reach this product.

## Never
- Mark a product delivered without the recipient's acceptance, or past a failed check in step 1.
- Transfer, invite, remove, or change access on any account — every such step is the owner's click.
- Write or patch the repo's docs from this seat, or fill a gap in the proof with an estimate.
- Put a secret value, customer data or personal contact details in the pack, `factory.json` or a message.
- Promise support terms, prices or legal assurances the user has not stated.
