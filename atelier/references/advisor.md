# Advisor model — a stronger model on call for the builder (optional, experimental)

Claude Code can pair the model that does the work (the *main* model) with a stronger one it may consult (the *advisor*). This page is what the factory tells the user about it; it is an option (`options.md`), off by default, and **nothing in the factory depends on it** — every gate applies to whatever model built the code.

## What is true about it (checked against Claude Code's own documentation, November 2026 — re-check before relying on any line; the feature is marked experimental)
- **How it is set:** `/advisor fable` (or `opus`, `sonnet`, `off`) in a Claude Code session, or the `advisorModel` setting. `/advisor` with no argument opens a picker.
- **It is the main model that decides when to consult** — typically before committing to an approach, when an error keeps recurring, and before declaring a task done. The advisor is not a mandatory planning step, and there is no setting to force or cap consultations.
- **The advisor must rank at or above the main model.** A weaker advisor is not attached.
- **Cost:** advisor usage counts toward the plan's usage limits (or is billed at the advisor model's rate on API billing). A Fable advisor may draw on usage credits on some plans and ask for a one-time consent. Anthropic's pages describe a faster main model with a stronger advisor as *typically* costing less than running the stronger model throughout — they publish **no percentage** for that; any figure seen elsewhere is unverified.
- **Scope:** `/advisor` saves to the **user's** settings, so it applies to **every** Claude Code session on that machine — other projects' and other lanes' sessions included — not just this project's. A per-project setting is not documented.
- **Where it works:** the terminal, non-interactive runs, the desktop app and Remote Control (so it works with the factory's hand-off mode A; outside the terminal it needs a recent Claude Code — 2.1.260 or later at the time of checking). In hand-off mode B the build runs in the PM's own cloud session, so this machine setting does not apply there and the `model:` line simply reports what that session used. Not available on third-party cloud platforms; it stays off when telemetry is disabled. It adds little on short tasks.

## The three set-ups the factory describes (one line each, with the con)
| Set-up | Main model | Advisor | For | Con |
|---|---|---|---|---|
| **As you are** (default) | whatever the session uses | none | most projects | none — this is the baseline |
| **Economy** | a faster model (Sonnet) | Fable or Opus | long builds where usage limits bite | the saving is unmeasured; a weaker main model may need more fix rounds |
| **Extra review** | the strongest model you normally use | Fable | a `data_sensitivity: high` or unusually hard build | costs more than the baseline, by design |
A `data_sensitivity: high` project is never moved to **Economy** by the factory's suggestion — only on the user's own words.

## How it is turned on (`/pf-setup advisor`)
The factory explains the table, says plainly that the setting is machine-wide and experimental, and asks. On a yes it gives the two lines to type in the Code session — the main-model choice and `/advisor <name>` — or types them through Chrome only after that yes; it never changes the setting on its own, and `/advisor off` undoes it. The choice is recorded as `options.advisor` (`none`, `economy` or `extra-review`).

## How its value is measured — not assumed
Every build result carries a `model:` line (`model: <main> · advisor: <name, none or unknown>`, `bridge.md`), and `/pf-build` logs it with the fix round (0 for a first attempt, +1 for each re-run after a failed or sent-back build) and the request and result times. `/pf-setup advisor` and `/pf-board` can therefore compare like with like across builds: acceptance pass rate on the first attempt, fix rounds needed, and how long the build took. After two builds on a new set-up the factory reports that comparison in three lines and asks whether to keep it. No claim of saving is made before then.

## Never
- Change the main model or the advisor without the user's yes in that conversation.
- Present an unmeasured saving as a fact, or quote a percentage Anthropic has not published.
- Treat a build as better or worse because of the model that made it — the gates decide.
