# What Atelier is made of — everything is inside

Atelier is one bundle. Every method, contract and tool it relies on ships inside its two plugins or is already part of Claude; **it never asks you to install another skill or plugin, and it never fetches one.** This page is the inventory.

## Atelier's own methods (written for Atelier, in `references/`)
- **Planning rigor** — `plan-audit.md`: the idea-stage SWOT, the eleven-lens pre-build audit under different roles, and the hard-decision council. Run by `/pf-plan`.
- **Design craft** — `design-craft.md`: direction playbooks, detail craft, motion, redesigns, brand kits. Used by `/pf-design` and the build, inside the limits of `design-standard.md`.
- **Diagrams** — `diagram-render.md`: every SPEC diagram rendered by Atelier itself from Mermaid source in the project's own colours.
- **Launch video** — `launch-video.md` and the bundled renderer `atelier-builder/scripts/render-video.mjs`: a short product animation built and rendered by Atelier (optional).
- **The contracts** — performance, SEO and AI visibility, security, simplicity, design, compliance, verification, data safety, deploy, delivery — and the options index (`options.md`).

## Bundled open-source skills (shipped inside the plugins, with their licences — `THIRD-PARTY-NOTICES.md`)
- **humanizer** *(MIT © Siqi Chen)* — makes user-facing copy read like a person wrote it. Used on copy before it ships; never to fake a review or mislead.
- **design-md** *(MIT © VoltAgent)* — a reference library of real design systems, for choosing and pressure-testing a direction. Reference only; a brand is never copied.
- **security-audit** *(MIT © Cloudflare — in `atelier-builder`)* — a source-first vulnerability audit used by the hardening and pentest stages on your own code.

## Part of Claude itself (nothing to install)
- The document surface Claude provides for planning documents, and its file formats when you ask for an export.
- Claude Code's own review commands, where the session has them. Atelier does not depend on them: if a review command is not available, the builder performs the same review directly against `security.md` and `code-simplicity.md`.

## Ordinary developer tools on the build machine (programs, not skills or plugins)
Node, Git, the GitHub CLI, the chosen host's CLI, Playwright's Chromium (end-to-end tests, screenshots, the video renderer), the Mermaid command-line tool run through `npx` (diagrams), `gitleaks` (secret scan), and `ffmpeg` (only if you make a launch video). `/pf-next doctor` checks them; `/pf-setup` gives the one line that installs each.

## Team projects — your own lane standard, if you have one
If you already keep your own working standard for team lanes, Atelier defers to it for those lanes. If you do not, Atelier's built-in team-lane steps (`pf-lanes`, `pf-build --lane`, `pf-merge`) are complete on their own.

## The rules
- Nothing here overrides a contract or a gate.
- Atelier ships only what its licence permits and credits it; it does not copy unlicensed or proprietary work, and it does not point you at anything to install in its place — where a capability matters, Atelier has its own.
- If you happen to have other skills installed in Claude, Atelier neither needs nor calls them.
