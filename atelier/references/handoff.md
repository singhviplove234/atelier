# Handoff modes — how the PM (Cowork) hands a job to the builder and learns it is done

Standing decision: the factory supports **two** handoff modes and lets the user **choose per project**, defaulting to **A**. Before a project's first build the PM explains both — pros, cons and **cost** — records the choice, and does not re-ask every build. The choice can be changed per project or overridden on a single run. Both modes keep every human approval gate exactly where it is.

This replaces the old poll-only completion signal in `bridge.md`: mode A wakes on a GitHub event (no more blind 3-minute timer as the primary path), mode B returns the result inline (no waiting at all).

## The two modes

### A — Local build + event wake  (DEFAULT)
The builder (Claude Code) runs on **the user's own computer**, started the existing way (the Chrome hand-off in `bridge.md`, or typed by the user). The change from before: the PM does **not** poll on a timer to learn it finished. It **subscribes to the project's GitHub repo** and **wakes on the event** — the builder opens the pull request (lane builds) or pushes to `main` (solo) when done, and that GitHub notification reaches the PM the moment it happens. The `*-RESULT-*.md` file stays the durable record; a slow poll (every ~15 min) remains only as a guaranteed fallback if no event arrives within the stage timeout.
- **Pros:** builds on hardware you already pay for (your PC); you can open Claude Code and watch or step in; **no secrets ever leave your machine**; nothing new to run. This removes the polling wait.
- **Cons:** your computer must be on with the Code session running for a build to happen; the PM waits on your machine's pace.
- **Cost: $0.** Your CPU and power (already paid for), GitHub free, the event notification free. It does **not** draw on your Claude plan usage while it waits.

### B — Cloud build  (opt-in, PC-independent)
The build runs **in the cloud where the PM runs**: it clones the repo from GitHub, builds and tests, pushes the branch/PR, and deploys to the free Azure target — **blocking**, so the PM gets the result directly with **no polling and no waiting on your PC**.
- **Pros:** your computer does not need to be on; the natural home for scheduled / unattended runs; fully hands-off between the approval gates.
- **Cons:** the **cloud** Claude does the building, not your desktop Claude Code, so you cannot watch it live the same way; your GitHub + Azure credentials must be **reachable from the cloud** (a real security surface — mitigated with Azure Key Vault + short-lived tokens, never a long-lived secret in the cloud); it cannot reach anything private to your machine or LAN; a bad run can reach a PR or a deploy before you see it, so it wants the Phase-2 safety net (monitoring + auto-rollback) in place first.
- **Cost:** **no new vendor bill** (GitHub free, Azure unchanged, and because the build runs in the Claude cloud — not GitHub-hosted runners — there are no CI minutes to pay for), **but the build work draws on your Claude plan usage** — every build, especially a scheduled one, spends usage that mode A spends on your free local CPU. Optional Azure Key Vault for secrets is pennies (effectively free at low volume).

## Choosing (the PM explains both, then records)
- Default is **A**. Before a project's first build, `/pf-build` presents **both** modes with the pros/cons/cost above (AskUserQuestion, **A marked "(Recommended)"**) and records the choice in `factory.json.handoff.mode` (`event` | `cloud`). It is **not** re-asked each build.
- **Per-run override:** `--handoff event|cloud` on `/pf-build`, `/pf-deploy` or `/pf-harden` uses that mode for the one run without changing the project default.
- **Change the default:** `/pf-build --handoff event|cloud` (records it), or edit `factory.json.handoff.mode`.
- **Data-sensitivity guardrail (hard):** when `brief.data_sensitivity: high` (data-sensitive — client, financial or personal data), the default stays **A** and **B is not offered by default**. If the user explicitly asks for B on such a project, the PM warns plainly that the client-data path should stay on the local/watched mode, requires the secret-handling (Azure Key Vault, no long-lived secret in the cloud) and the Phase-2 safety net, and confirms once more. **Client data never builds in the cloud without that explicit, warned yes.** The pentest step is **always mode A** (own pre-production host, watched, never cloud, never scheduled).

## How each mode signals completion (replaces poll-only)
- **A (event):** right after the hand-off, the PM subscribes to the repo's pull-request activity (and `main` pushes for solo). It waits on the GitHub event; on the PR-opened / push notification it reads the matching `*-RESULT-*.md` (validated by exact header + mtime newer than the request) and proceeds. It falls back to a slow poll only if no event arrives within the stage timeout. Requires the repo on GitHub and PR notifications enabled (`/pf-setup handoff`).
- **B (cloud):** the PM runs the build in its own cloud session and gets the result **inline** — there is nothing to wait on. The `*-RESULT-*.md` is still written to the project folder and committed to the repo as the durable record. The cloud session needs GitHub (clone/push) and the target's deploy credentials reachable per `/pf-setup handoff` (Key Vault / short-lived token), never a stored long-lived secret.

## Unchanged in both modes
The human approval gates do not move: **design sign-off**, **deploy go-live** (always a yes), **pentest scope** (never scheduled, never `--go`), and **client-data go-live**. The contracts (performance, SEO, security, compliance, simplicity, design, cost) are met in full whichever mode builds the code.
