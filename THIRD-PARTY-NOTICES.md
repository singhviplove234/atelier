# Third-party notices

Atelier's own code and documentation are MIT-licensed (see `LICENSE`). In
addition, Atelier **bundles** the following third-party skills so the factory
works out of the box. Each is redistributed under its own license, which is
kept intact in the skill's folder. These skills are **not** covered by
Atelier's MIT license — their own terms govern, and copyright remains with
their respective authors.

| Skill (path) | License | Copyright | Source |
|---|---|---|---|
| `atelier/skills/humanizer` | MIT | © 2025 Siqi Chen | bundled, license in folder |
| `atelier/skills/design-md` | MIT | © 2026 VoltAgent | bundled, license in folder |
| `atelier/skills/find-skill` | MIT | © 2026 fockus | adapted from `fockus/claude-skill-find-skill`; license in folder |

Full license text for each lives in that skill's directory (`LICENSE`). If you
redistribute Atelier, keep those files in place.

## Skills Atelier installs on first run (not bundled)

Other skills the factory can use — `tech-doc-audit`, `swot-analysis`,
`llmcouncil`, the design-taste and animation skills, `remove-ai-marks`,
`brandkit`, and others — are **not** redistributed here. Several carry
licenses that do not permit redistribution (for example, Anthropic's own
skills are proprietary and may not be copied or distributed; some skills ship
with no license at all). Instead, on first run Atelier's `/pf-bootstrap` uses
the bundled `find-skill` to locate and install them **from their official
sources** onto your own Claude account, with your go-ahead. Nothing in that
set is copied into this repository.

Anthropic's built-in skills (`docs`, `docx`, `pdf`, `pptx`) and the built-in
`/code-review` and `/security-review` are already present in Claude and are
neither bundled nor installed by Atelier.
