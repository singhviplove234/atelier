# Recommending tools & options — always pros, cons and cost

Standing requirement: whenever the factory recommends a tool, service, platform, library, tier or option — a host, a database, a monitoring stack, a pentest version, a handoff mode, a design direction, a paid upgrade — it presents **pros, cons and cost** for each choice, never the upside alone, so the user decides informed.

## The rule
- State **one** recommendation marked "(Recommended)" with the reason, then the real alternatives — each a short line with its **pros, cons and cost**.
- **Never sell a tool on its pros alone, and never hide a con:** a free tier that sleeps or pauses, a cost per run, vendor lock-in, upkeep you own, non-determinism, a signup/account to manage, a learning curve. If a choice has a real downside, it is named.
- **Cost is always stated**, free-first per `cost-posture.md`. A con is not a reason to avoid the right tool — it is there so the choice is made with open eyes.
- Keep it short and plain: a one-line recommendation + 2–3 alternatives, not a spec sheet. Use AskUserQuestion where the user should pick.

## Never trade away the project's quality or security
Free-first, pros/cons and convenience **never** override what the project *requires*. Every suggestion must still meet the project's **quality bar and its security/compliance needs** (`security.md`, `security-testing.md`, `compliance.md`, and `cost-posture.md` "Quality is the bar, not cost"). Never recommend a cheaper or simpler option that fails a real requirement — a free tier that can't hold the uptime a client service needs, a host that can't meet the data-residency/compliance a data-sensitive project needs, a shortcut that weakens RLS, auth, input validation, headers or secret handling. The cheapest option is chosen **from those that clear the bar**, never from below it. When the only option that meets the required quality or security costs money, **recommend it** (with the price, on a yes) — that is correct, not a failure. Security and the project's required quality are fixed **first**; cost and convenience are chosen under them.

## Where it applies (every choice the factory offers)
`platform-selection.md` (hosts/DBs/providers), `monitoring.md` (the monitoring stack), `security-testing.md` (scanners / agent / both), `handoff.md` (mode A / B), `cost-posture.md` (any paid tier), design directions (`design-standard.md`), context tooling (`pf-setup`), and anything else the factory suggests. Each of those already carries its pros/cons; this file is the standing rule they follow, so a new choice added anywhere does the same.
