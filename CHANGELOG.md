# Changelog

## 1.1.0
- **Diagrams before code.** The SPEC has a ninth heading, `## Diagrams`: the app, every page and every feature is diagrammed before anything is built, and the builder refuses to build otherwise. Rendered with the Diagram Design plugin (required on the Code session).
- **Checks that travel with the repo.** Every product gets one `verify` command wired to a pre-push hook (and an optional CI workflow), with an end-to-end test for every page and feature diagram.
- **Preview first.** Deploys go to a preview and pass the end-to-end suite there before the go-live question; each live release is git-tagged.
- **Data safety.** Separate test and production databases once a product is live; expand-then-contract migrations; a destructive migration needs its own yes and a backup first.
- **`/pf-deliver`.** A handover stage: repo docs (architecture, runbook, admin guide, changelog), a delivery pack built from recorded proof, a guided ownership transfer, and the recipient's acceptance as the final gate.
- **SaaS blueprint and mobile release** (`expo-eas` target) decided at plan time.
- **`/pf-next doctor` and `/pf-setup --check`** verify the whole toolchain in one pass.
- No AI attribution trailers in the repos Atelier builds; optional `apple-look` skill for mobile UI; search-question mining in the growth loop.
