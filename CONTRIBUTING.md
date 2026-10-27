# Contributing to Atelier

Thanks for your interest in improving Atelier. It's two Claude plugins — `atelier` (Cowork) and `atelier-builder` (Claude Code) — plus a validator.

## Ground rules

- **Keep the safety model intact.** Atelier never types or stores secrets, never deploys/publishes/spends without an explicit human yes, and never runs the pentest against production, real data, or on a schedule. Changes must preserve these.
- **Quality and security are gates, not suggestions.** The build contracts (performance, security, SEO, accessibility, simplicity, compliance) are hard gates. Don't weaken a gate to make something pass.
- **Free-first, provider-agnostic.** Don't add a paid default or lock a step to one cloud.
- **The two plugins share reference files.** Several files under `references/` are kept **byte-identical** between `atelier/` and `atelier-builder/` (the validator enforces it). Edit the `atelier/` copy, then mirror it to `atelier-builder/`.

## Before you open a PR

Run the validator from the repo root and keep it green:

```
bash tests/check.sh
```

It checks plugin structure, required content, the mirrored-file identity, the target registry, and that no personal/private data or secret-looking values are present. If you add a new guarantee, add a check for it.

## Making changes

- **A new hosting target:** add `references/targets/<name>.md` (with `## Required`, `## Checks`, `## Fits`, `## Deploy steps`, `## Health check`) in both plugins, keep them identical, and list it in `references/platform-selection.md` and `references/deploy-rule.md`.
- **A new skill or command:** follow the shape of the existing `pf-*` skills; keep descriptions tag-free; wire any contract it relies on.
- **Docs:** update the top-level `README.md` and the per-plugin READMEs so they stay a true map.

## Reporting issues

Open a GitHub issue with what you expected, what happened, and the steps. For anything security-sensitive, please note it clearly in the issue title.

By contributing, you agree your contributions are licensed under the repository's [MIT License](LICENSE).
