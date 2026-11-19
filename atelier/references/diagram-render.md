# Rendering diagrams — Atelier's own renderer

Every diagram in a SPEC is Mermaid source (`spec-format.md` `## Diagrams`). Atelier renders it itself with the open-source **Mermaid command-line tool** (`@mermaid-js/mermaid-cli`, run as `mmdc` through `npx` — an ordinary npm tool like the linter, not a plugin or a skill), themed from the project's own tokens. Nothing else is installed for diagrams.

## A. The theme comes from the SPEC, never from a website
Write `docs/diagrams/theme.json` from `## Tokens`, mapping: page background → `background`; card/surface colour → `primaryColor`; text colour → `primaryTextColor`; the accent → `primaryBorderColor`; the muted colour → `lineColor`; a tint of the surface → `secondaryColor` and `tertiaryColor`; the body font stack → `fontFamily`. Use Mermaid's `base` theme so every colour is the project's:
```json
{ "theme": "base", "themeVariables": { "background": "#ffffff", "primaryColor": "#ffffff", "primaryTextColor": "#111827", "primaryBorderColor": "#16a34a", "lineColor": "#6b7280", "secondaryColor": "#f3f4f6", "tertiaryColor": "#ffffff", "fontFamily": "Inter, system-ui, sans-serif", "fontSize": "15px" } }
```
The file is regenerated whenever the tokens change; a changed theme re-renders every diagram.

## B. One source file, two outputs, per diagram
For each block, write the source to `docs/diagrams/<id>.mmd` (the `%% id:` and `%% covers:` comment lines stay in — Mermaid ignores them), then:
```
npx -y @mermaid-js/mermaid-cli -i docs/diagrams/<id>.mmd -o docs/diagrams/<id>.svg -c docs/diagrams/theme.json -b "<background>"
npx -y @mermaid-js/mermaid-cli -i docs/diagrams/<id>.mmd -o docs/diagrams/<id>.png -c docs/diagrams/theme.json -b "<background>" -s 2
```
Pin the tool's version in the repo's dev dependencies after the first run, so a later release cannot change how diagrams look. The tool drives a headless Chromium; if it cannot find one, point it at the Chromium that Playwright already installed for the end-to-end tests with a small `-p docs/diagrams/puppeteer.json` file (`{"executablePath": "<path>"}`, the path printed by `node -e "console.log(require('playwright').chromium.executablePath())"`) — never download a second browser when one is present.

## C. When to render, and what to remove
Render an id when its `.mmd` is new or changed, when either output is missing, or when `theme.json` changed. Delete the `.mmd`, `.svg` and `.png` of any id that is no longer in the SPEC. The folder always equals the SPEC.

## D. When a diagram will not render
A syntax error is a defect in the SPEC, not something to draw around: retry once after normalising whitespace, then fail the build with the tool's own message — `failures: diagram <id>: <reason>` — so the PM fixes the source. Never replace a diagram with a hand-made picture, and never skip one.

## E. Check
`npx -y @mermaid-js/mermaid-cli --version` runs; every id in the SPEC has its three files; no file exists for an id that is not in the SPEC; each `.svg` is non-empty and contains the diagram's own labels.
