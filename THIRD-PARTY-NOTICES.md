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
| `atelier-builder/skills/security-audit` | MIT | © 2025–2026 Cloudflare, Inc. | `cloudflare/security-audit-skill`; license in folder |

Full license text for each lives in that skill's directory (`LICENSE`). If you
redistribute Atelier, keep those files in place.

## Nothing else is installed or fetched

Atelier is self-contained. Apart from the three skills above, every method it
uses (planning audit, design craft, diagram rendering, the launch-video
renderer, all contracts) was written for Atelier and is covered by Atelier's
MIT licence. It does not copy, adapt or download any other skill or plugin,
and it does not ask you to install one.

At run time the builder uses ordinary open-source programs on your machine —
Node, Git, the GitHub CLI, Playwright, the Mermaid command-line tool
(`@mermaid-js/mermaid-cli`, MIT, run through `npx`), `gitleaks` and, for the
optional launch video, `ffmpeg`. These are not redistributed in this
repository; each is installed from its own source under its own licence.
