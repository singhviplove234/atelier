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
