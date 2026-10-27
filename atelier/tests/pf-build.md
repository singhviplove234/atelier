# Manual test script — /pf-build

Prereq: a project from `tests/pf-design.md`; `/pf-setup` done so `lanes.solo.code_url` is set; a Code session open. File names are lane-suffixed (`BUILD-REQUEST-solo.md`, `BUILD-RESULT-solo.md`). For result-shape cases you can write the result file by hand.

| # | Setup | Do | Expected |
|---|---|---|---|
| 1 | `gates.design == pending` | `/pf-build` | Refuses: "Design isn't approved yet — run /pf-design and approve it first." Nothing written. |
| 2 | design approved | `/pf-build --dry-run` | `SPEC.md` written with all eight headings in order; `BUILD-REQUEST-<lane>.md` content printed starting `PF-BUILD v1`; no request file written; `factory.json` unchanged except a `log` entry. |
| 3 | delete the `## Tokens` heading from `SPEC.md` by hand | `/pf-build --validate-only` | Refuses naming the missing heading: "SPEC.md is missing: ## Tokens"; `SPEC.md` not regenerated. |
| 3b | a build that fails before `gh repo create` (e.g. kill the builder mid-way) | re-run `/pf-build` | Builder continues from the existing `<code root>/<slug>` checkout — no second `create-next-app`; `repo_url` not blanked. |
| 4 | design approved | `/pf-build` | Writes `BUILD-REQUEST-<lane>.md`; asks you to run `/pf-next`; starts polling. `/pf-build --check` before running /pf-next → "No result yet". |
| 5 | wait for `BUILD-RESULT-solo.md` with `status: ok … acceptance: 4/4` | wait for the poll (or `/pf-build --check`) | Fields recorded; gate `pending`; acceptance table shown; asks for approval. |
| 6 | write a `BUILD-RESULT-<lane>.md` by hand with free text and no version line | `/pf-build --check` (or let the poll see it) | Treated as no result ("No result yet"); gate unchanged. |
| 7 | `repo_url` already set | `/pf-build --dry-run` | Printed request includes `mode: continue`. |
| 8 | after case 5 (solo) | reply `yes` | `lanes.solo.status == merged`; `gates.build == approved`; "Run /pf-deploy when ready." |
| 9 | team lane `frontend`, result ok with `pr_url` | reply `yes` | gate unchanged; "The PM seat merges it with `/pf-merge --lane frontend`." |
