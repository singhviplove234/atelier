# Handoff modes — how the PM (Cowork) hands a job to the builder and learns it is done

Standing decision: the factory supports **two** handoff modes and lets the user **choose per project**, defaulting to **A**. Before a project's first build the PM explains both — pros, cons and **cost** — records the choice, and does not re-ask every build. The choice can be changed per project or overridden on a single run. Both modes keep every human approval gate exactly where it is.

This improves on the old blind 3-minute timer in `bridge.md`: mode A is **woken by the PR** (not polling) as its completion signal, mode B returns the result inline (no waiting at all). Honest framing: a Cowork session **cannot be pushed to** from outside — nothing but a scheduled check-in it sets, a delivered notification for a subscribed PR (where the surface supports it), or the user can wake it. "Event-wake" means *the notification pipeline delivering the real PR event*, not a live push.

## The two modes

### A — Local build + PR-event wake  (DEFAULT)
The builder (Claude Code) runs on **the user's own computer**, started the existing way (the Chrome hand-off in `bridge.md`, or typed by the user).

**The PM is woken by the PR, it does not poll.** A Cowork session can't receive a raw webhook, but the notification pipeline (`ReadNotifications`) carries **GitHub activity on subscribed PRs** — so the autonomy path is:
1. **At setup, the repo's PR activity is subscribed** (`/pf-setup handoff`), so its events are delivered to this session as notifications.
2. **The builder opens a draft PR at the start of a lane build** (`main`-push for solo), giving the PM something to be woken by immediately. Every later event on it is a wake: **done** → the builder marks the PR ready for review (and writes `*-RESULT-*.md`); **blocked on a question** → the builder adds a `needs-input` label (and writes `NEEDS-INPUT-<lane>.md`). Both "done" and "blocked" are PR activity, so **both wake the PM through the same channel — nothing is polled.**
3. On each wake the PM calls `ReadNotifications`, then reads GitHub with the project's **scoped lane token (fails closed if missing — never a personal login, `security.md` 16)** and acts on the matching result or question.

A **scheduled check-in is only a rare backstop** — a single long timer at the stage timeout (build 90 min, etc.), used **only if** notifications aren't being delivered on this surface (then it degrades gracefully to a paced check). It is not the primary signal and does not run on a fast loop.

**Chrome stays needed** for exactly two things with no other path: typing the one `/pf-next` command to *start* the build, and (when a question arrives) reading/answering it on the Code page.
- **Pros:** builds on hardware you already pay for (your PC); you can watch or step in; **no secrets ever leave your machine**; and the PM is **woken by the PR event**, so it truly waits idle instead of polling.
- **Cons:** your computer must be on with the Code session running; the autonomy depends on the GitHub-notification subscription being delivered to the session (set up at `/pf-setup handoff`) — where a surface doesn't deliver it, the backstop check covers it, slower.
- **Cost: $0.** Your CPU and power (already paid for); and every GitHub piece of the wake route is a **free** feature — watching/subscribing to PRs, PR notifications, draft PRs and labels — with **no GitHub Actions minutes** used (CI, if any, runs self-hosted/local per `cost-posture.md`). The notification is free, and waiting idle draws **no** Claude plan usage. Chrome (the start command + answering a question) is also free.

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
- **A (woken by the PR event):** the PM subscribes to the repo's pull-request activity at setup, then **waits idle until a notification arrives** (`ReadNotifications` carries GitHub activity on subscribed PRs). The builder opens a draft PR at build start; it marking the PR **ready** (done) or adding a **`needs-input`** label (blocked) each delivers a notification that wakes the PM, which then reads GitHub with the scoped token (fail-closed, never a personal login) and reads the matching `*-RESULT-*.md` (validated by exact header + mtime) or opens the Code page for the question. **No polling** on the happy path. A single long **backstop check** at the stage timeout covers the case where this surface doesn't deliver GitHub notifications; it is not the primary signal. A Cowork session cannot receive a raw push — this is the notification pipeline delivering the real PR event.
- **B (cloud):** the PM runs the build in its own cloud session and gets the result **inline** — there is nothing to wait on. The `*-RESULT-*.md` is still written to the project folder and committed to the repo as the durable record. The cloud session needs GitHub (clone/push) and the target's deploy credentials reachable per `/pf-setup handoff` (Key Vault / short-lived token), never a stored long-lived secret.

## Unchanged in both modes
The human approval gates do not move: **design sign-off**, **deploy go-live** (always a yes), **pentest scope** (never scheduled, never `--go`), and **client-data go-live**. The contracts (performance, SEO, security, compliance, simplicity, design, cost) are met in full whichever mode builds the code.
