# Changelog

## 1.3.0
- **Options index** (`references/options.md`): every optional add-on in one place — when it is offered, where the choice is recorded, the one file that defines it. Off until chosen; offered in one line, once.
- **Advisor model** guidance for the builder: experimental, machine-wide, and measured across builds before it is recommended.
- **3D product scene** (optional): still image first, the 3D loads on interaction, strict size limits, tested fallback.
- **Launch video** (`/pf-promo`, optional): a brief pack for a motion-graphics tool that runs on your own computer; never bundled, never a gate.
- **Growth drafts** (`/pf-grow --draft`, optional): the new title, description and opening written out for pages you pick; still approved before anything changes, measured after 28 days.
- Numbered review notes (D1…, G1…) so feedback can be given by number.

## 1.2.0
- **Looks like the design.** Every screen is screenshotted at phone and desktop size: a visual baseline that fails the build on an unexplained change, and a design check against the approved artboards before the build is approved.
- **Locale-ready.** Dates, numbers and money always go through the locale formatter; full translation machinery when the plan lists more than one locale.
- **Infrastructure as code** for multi-resource cloud setups: dry-run at preview, applied only after a yes.
- **Feature flags and canary rollouts**, only when a release needs them.
- **Flutter and native store releases** (`flutter-stores` target).
- **Status page and customer notices**; a version-mismatch notice on the control panel.
- Fixed: the SPEC contract had lost its per-heading definitions.

## 1.1.0
- **Diagrams before code.** The SPEC has a ninth heading, `## Diagrams`: the app, every page and every feature is diagrammed before anything is built, and the builder refuses to build otherwise. Rendered with the Diagram Design plugin (required on the Code session).
- **Checks that travel with the repo.** Every product gets one `verify` command wired to a pre-push hook (and an optional CI workflow), with an end-to-end test for every page and feature diagram.
- **Preview first.** Deploys go to a preview and pass the end-to-end suite there before the go-live question; each live release is git-tagged.
- **Data safety.** Separate test and production databases once a product is live; expand-then-contract migrations; a destructive migration needs its own yes and a backup first.
- **`/pf-deliver`.** A handover stage: repo docs (architecture, runbook, admin guide, changelog), a delivery pack built from recorded proof, a guided ownership transfer, and the recipient's acceptance as the final gate.
- **SaaS blueprint and mobile release** (`expo-eas` target) decided at plan time.
- **`/pf-next doctor` and `/pf-setup --check`** verify the whole toolchain in one pass.
- No AI attribution trailers in the repos Atelier builds; optional `apple-look` skill for mobile UI; search-question mining in the growth loop.
