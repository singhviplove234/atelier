# Skills the factory leans on

The factory **uses skills that already exist** where they beat hand-rolled
instructions. A skill **never overrides a contract or a gate** (the contract
wins on any conflict).

**The full map — which skill, when to use it, and how the pipeline uses each —
is `skill-catalog.md`.** This file is the short version plus the rules that
don't fit a per-skill row.

## How skills arrive (Atelier is one-stop)
- **Bundled** (always present): `find-skill`, `humanizer`, `design-md` — the ones whose licenses allow redistribution (`THIRD-PARTY-NOTICES.md`).
- **Built-in**: `/code-review`, `/security-review`, and the Claude document skills (`docs`, `docx`, `pdf`, `pptx`).
- **Required on the Code session**: `diagram-design` (third-party, MIT © Cathryn Lavery) — the one tool a build cannot run without. It renders every diagram the factory makes: the plan's architecture diagram and, before any build, the SPEC's `## Diagrams` (app architecture + journey, one user-flow per page, one sequence per feature — `spec-format.md`); the builder's Diagrams gate refuses to scaffold without it. It is a Claude Code plugin, installed from the author's repo only by `/pf-setup` step 0b2 (`/plugin marketplace add cathrynlavery/diagram-design`, then `/plugin install diagram-design@diagram-design`; check with `/diagram-design:doctor`) — never copied into this repo.
- **Installed on first run**: everything else the factory uses (`tech-doc-audit`, `swot-analysis`, `llmcouncil`, the design-taste and animation skills, `remove-ai-marks`, `brandkit`, and optionally `superpowers`) is installed from its **own official source** by `/pf-bootstrap` on the first run on a Claude account — never copied into this repo. After that, `skill-catalog.md` tells Atelier how and when to use each.

## Team projects — defer to your own lane standard, if you have one
If you maintain your own working standard for team lanes as a skill — session
start, Definition-of-Done, how each lane writes status, the handoffs, the log
entry — the factory **defers to it**: for a team project its lanes run inside
your standard, and your binding team files **win** over the factory's generic
lane steps. If you have no such skill, the factory uses its own built-in
team-lane steps (`pf-lanes`, `pf-build --lane`, `pf-merge`), which are complete
on their own. Either way the factory orchestrates; your standard, where
present, governs the lane.

## The rules
- A skill never overrides a contract or a gate.
- Atelier redistributes only the three bundled skills; all others install from their own official source (licensing — some skills are proprietary or unlicensed and must not be copied).
- Use a skill only where it beats hand-rolled instructions; recommend any optional one with pros, cons and cost per `recommendations.md`.
- Content, social-media and media-production skills are out of scope — the factory builds software products.

## Optional third-party tools behind an option (never bundled — `options.md`)
- **blender-skills** *(third-party, MIT — `EL4CTEO/blender-skills`)* — Blender workflows as agent skills, used only when a project's 3D scene is of kind `model` and the file is made in Blender on the Code machine (`scene-3d.md`). Installed from its own repository via `/pf-setup options`; needs Blender installed.
- **Motion Design** *(third-party, no licence stated — by Mr. Pynk, on work credited to Rourke Heath)* — the default tool for the optional launch video (`launch-video.md`). A folder the user downloads from the author's page and runs on their own computer; the factory only writes a brief pack for it and never copies or redistributes it.
