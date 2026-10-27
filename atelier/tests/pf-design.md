# Manual test script — /pf-design

Run in a Cowork session with `atelier` installed and the `Atelier` folder connected. Tick each expected outcome.

| # | Do | Expected |
|---|---|---|
| 1 | `/pf-design "My SaaS Idea!"` | Folder `Atelier/my-saas-idea/` created; `factory.json.name == "my-saas-idea"`; `gates.design == "pending"`; a Design artifact opens with one artboard per screen; the skill stops — nothing is built. |
| 2 | Reply `looks good` | Skill asks "Approve the design? (yes/no)"; gate unchanged. |
| 3 | Reply `yes` | `gates.design == "approved"`; `log` gains an entry with `stage: design`. |
| 4 | Run `/pf-design "My SaaS Idea!"` again | Skill asks "resume or start over?"; `factory.json` is not overwritten silently. |
| 5 | Inspect the brief before approving (fresh project) | Shows `Stack: Next.js + Tailwind + shadcn/ui (TypeScript); Supabase` pre-filled; editing it before approval changes `factory.json.brief.stack`; after approval the skill refuses to change it. |
