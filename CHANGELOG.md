# Changelog

## 2.0.1 — audit fixes
- Version numbers in the guides now match Atelier's own releases; the "added in" notes are gone.
- The launch-video result file uses one field per line, as the bridge documents; a non-Node product (Flutter, native) can still get a launch video.
- The top-level README now mentions lanes, delivery and the launch video; the builder README lists the bundled security audit.
- The bundled `humanizer` ships without its upstream packaging script.
- The validator's private-wording check stores hashes instead of words.

## 2.0.0 — one bundle
Atelier no longer asks you to install, and no longer fetches, any other skill or plugin. Everything it uses is inside its two plugins.
- **Removed:** the first-run installer (`/pf-bootstrap`), the bundled skill finder (`find-skill`) and the outside-skill catalogue; every "install this plugin" step in setup.
- **Planning audit is Atelier's own** (`references/plan-audit.md`): the idea-stage SWOT, the eleven-role audit and a hard-decision council.
- **Design craft is Atelier's own** (`references/design-craft.md`): direction playbooks, detail, motion, redesigns, brand kits.
- **Diagrams are rendered by Atelier** (`references/diagram-render.md`) with the open-source Mermaid command-line tool, in the project's own colours. The Diagram Design plugin is no longer needed.
- **Launch video is made by Atelier** (`/pf-promo` → `/pf-next <slug> promo`): storyboard you approve, review stills, then a render on your build machine with the bundled renderer (browser + ffmpeg; no graphics card, no outside tool).
- **Reviews are built in:** every build gets a code review and a security review whether or not the session has a review command.
- Mobile apps follow the platform's published guidelines directly; a 3D `model` scene takes a finished file from any 3D tool.
- Still bundled, under their own licences: `humanizer`, `design-md`, `security-audit`.
- **Upgrading from 1.x:** nothing to migrate. Skills you installed earlier are simply no longer used by Atelier; you may keep or remove them. On the build machine, run `/pf-next doctor` once — it now checks the Mermaid tool (and `ffmpeg` only if you make a launch video).

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
