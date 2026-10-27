# Atelier skill catalog — which skill, when to use it, how the factory uses it

This is the full map of every skill Atelier leans on, how it arrives, and
exactly where in the pipeline it earns its place. Three standing rules apply
to all of them (`recommendations.md`):

1. **A skill never overrides a contract or a gate.** The contracts
   (performance, security, SEO, compliance, simplicity, design, cost) and the
   approval gates always win on any conflict — a skill polishes *how* a stage
   is done, never *whether* a gate is met.
2. **Atelier redistributes only the three bundled skills** (their licenses
   allow it). Everything else is **installed from its own official source** by
   `/pf-bootstrap` on first run, never copied into this repo
   (`THIRD-PARTY-NOTICES.md`).
3. **Use a skill only when it beats hand-rolled instructions**, and recommend
   any optional one with pros, cons and cost.

How each skill arrives:
- **Bundled** — ships inside Atelier, always present.
- **Built-in** — already part of Claude; nothing to install.
- **First-run** — installed from its official source by `/pf-bootstrap`.

---

## Always present

### Bundled with Atelier
- **find-skill** *(MIT © fockus — bundled)* — searches a catalogue of ~17,800 skills and installs the one you pick. **When:** on first run (`/pf-bootstrap` uses it to fetch the first-run skills below), and any time you want a skill for an ad-hoc need the `pf-*` flow doesn't already cover. **How:** discovery + install engine; it never installs without your explicit choice.
- **humanizer** *(MIT © Siqi Chen — bundled)* — makes copy read like a person, not a model. **When:** `/pf-build` (and `/pf-grow` content), on user-facing copy before it ships. **How:** a polish pass over headlines/body already written to the SPEC — never to fake reviews or deceive (`compliance.md`).
- **design-md** *(MIT © VoltAgent — bundled)* — a library of real-brand design systems (type, color, spacing, motion patterns). **When:** `/pf-design`, when picking or pressure-testing a visual direction for `brief.design_direction`. **How:** reference to choose a direction fast and set the `pf-design-system` tokens; `design-standard.md` still governs the actual tokens, AA contrast and licensed fonts/icons.

### Built into Claude (nothing to install)
- **/code-review + /security-review** — **When:** every `/pf-build`, mandatory. **How:** the builder runs both and fixes Critical/High before a lane can pass.
- **docs** — **When:** `/pf-plan` writes the PRD / architecture / MVP / stack / budget as living docs. **How:** the document surface for planning artifacts.
- **docx / pdf / pptx** — **When:** only when the user asks for a Word/PDF/PowerPoint export of a planning doc. **How:** format skills, opened after the content is settled (research first, then format).

---

## Installed on first run (`/pf-bootstrap`)

These are fetched from their official sources onto your account the first time
you set Atelier up. Grouped by the stage that calls them.

### Planning & audit — `/pf-plan`
- **swot-analysis** — **When:** at discovery, as soon as the idea is understood, *before* committing effort. **How:** pressure-tests the idea (strengths/weaknesses/opportunities/threats + a verdict) so weak ideas are caught early.
- **tech-doc-audit** — **When:** at plan sign-off (`/pf-plan` §7), the real pre-build gate. **How:** audits the architecture + requirements through 11 expert lenses (director, PO, dev, architect, security, UI/UX, SRE, DevOps, DevSecOps, AI/ML, data/compliance); the gaps it finds are folded in before a line is built.
- **llmcouncil** — **When:** only for a genuinely hard fork (platform choice, go/no-go) — not routinely. **How:** a multi-adviser council for one big decision.

### Design & motion — `/pf-design` and `/pf-build`
- **impeccable** — **When:** `/pf-design` / `/pf-build`, for award-grade frontend craft. **How:** sharpens hierarchy, IA, a11y, motion, copy and tokens to a higher bar on top of the design system.
- **emil-design-eng** — **When:** `/pf-design` polish. **How:** the invisible UI details (timing, easing, focus, spacing) that separate good from great.
- **design-taste-frontend / high-end-visual-design / minimalist-ui / industrial-brutalist-ui / gpt-taste / stitch-design-taste** — **When:** `/pf-design` / `/pf-build`, to execute `brief.design_direction` to a non-templated bar. **How:** direction-specific taste; pick the one matching the chosen direction.
- **animate / improve-animations / animation-performance / animated-ui-libraries** — **When:** `/pf-design` / `/pf-build` for the motion layer, especially a `brand` direction. **How:** build and tune motion that stays GPU-only, causes no CLS and fits the performance budget.
- **redesign-existing-projects** — **When:** `/pf-harden` or maintenance, upgrading an existing site to premium quality. **How:** a structured redesign pass within the contracts.
- *Caveat (all design/motion skills):* `design-standard.md` governs tokens, WCAG AA, licensed fonts/icons and the perf/motion budgets — these skills polish, they never override the contract or the budget.

### Copy & brand
- **remove-ai-marks** — **When:** `/pf-build` / `/pf-grow`, before delivering copy. **How:** strips AI-provenance tells from site copy (honest polish, never to deceive).
- **brandkit** — **When:** a `brand`-direction project needing a fuller brand kit. **How:** assembles brand assets/boards; the design and compliance contracts still bind.

### Build discipline (Claude Code, optional)
- **superpowers** — **When:** on the Code session during `/pf-build`. **How:** reinforces plan-first + self-verification + TDD + systematic debugging as the builder works, so mistakes are caught before Atelier's gates. Overlaps what the factory already enforces, so it's polish on *how* the Code session works, not a new capability; separately owned, so it's installed from its own marketplace, never bundled.

---

## Out of scope
Content, social-media, brand-marketing and media-production skills are a
separate domain — Atelier builds software products, so it leaves those alone
unless one is genuinely needed for a project's own site copy (and then only the
copy skills above, never to deceive). See `skills.md` for the short version of
these rules and the team-lane standard.
