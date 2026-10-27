# Atelier

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE) [![Release](https://img.shields.io/github/v/release/singhviplove234/atelier?sort=semver)](https://github.com/singhviplove234/atelier/releases) [![Made for Claude](https://img.shields.io/badge/made%20for-Claude-8A2BE2)](https://claude.com)

> **New to Atelier? [INSTALL.md](INSTALL.md) is a plain, step-by-step install guide anyone can follow.**

**Describe an idea. Atelier plans it, designs it, builds it, ships it, and keeps it running — pausing only when it needs your yes.**

Atelier is a pair of plugins for [Claude](https://claude.com) that turn a plain-language idea into a real, live web product and then look after it. You don't need to be a developer. You describe what you want; Atelier acts as your product manager, designer, engineer and operator, and stops at every important decision to show you the work and ask before it does anything that matters.

It is **free-first** (it reaches for the free, secure way to build and host before anything paid, and never spends money without asking), **secure and quality-gated by default** (every build must pass performance, security, SEO, accessibility, simplicity and legal checks before it ships), and **provider-agnostic** (it picks the best-fit host across Azure, AWS, GCP, Oracle, Vercel, Cloudflare, Netlify, Render, Fly.io or a free static host — never locked to one cloud).

> Atelier builds software products. It is not a website-content or social-media tool.

---

## Who it's for

- **Non-technical founders and operators** — you have an idea for a site, tool or small app. Atelier handles the technical work in plain language and walks you through the few steps only a human can do (clicking "sign up", pasting a key), one at a time.
- **Developers and teams** — a repeatable, gated pipeline with real engineering contracts, team "lanes" that build in parallel, monitoring, auto-rollback, maintenance and a security pentest stage. Bring your own standards; Atelier defers to them where you have them.

---

## How it works

Atelier is two plugins that talk to each other:

| Plugin | Runs in | Role |
|---|---|---|
| **`atelier`** | Claude **Cowork** | The **PM / orchestrator.** Plans, designs, drives the build, deploys, monitors, maintains and grows — and holds every approval gate. |
| **`atelier-builder`** | **Claude Code** | The **builder.** Runs one build / deploy / harden / pentest request at a time on your machine and writes the result back. |

The Cowork side writes a request file into a shared project folder and triggers Claude Code (through Chrome, or you paste one command); Claude Code does the heavy lifting locally and writes a result back. You stay in Cowork the whole time.

### The pipeline

```
/pf-plan → /pf-design → /pf-build → /pf-deploy → /pf-harden → /pf-monitor → /pf-maintain → /pf-grow
  (PM/BA)    (design)     (code)      (go live)    (fast+found)  (safety net)  (keep healthy)  (grow)
```

`/pf-ship` runs the whole chain for you and pauses only at your gates. `/pf-board` shows every project's status on one live dashboard. A data-sensitive project also gets `/pf-pentest` (an authorized security attack-test of your own pre-production, before any real data).

Each arrow is a gate: Atelier shows you the result and waits for your **yes** before moving on.

---

## Install

Atelier is a marketplace with two plugins. Add the marketplace once, then install each half where it belongs.

**1. Add the marketplace** (in either Claude Code or Cowork):

```
/plugin marketplace add singhviplove234/atelier
```

**2. Install the Cowork half** (in **Cowork**):

```
/plugin install atelier@atelier
```

**3. Install the builder half** (in **Claude Code**, on the computer that will build):

```
/plugin install atelier-builder@atelier
```

You can also install from a downloaded release: in the Plugins panel choose **Add → Upload plugin** and pick `atelier.zip` (Cowork) or `atelier-builder.zip` (Claude Code).

**4. One-time setup** — in Cowork, run:

```
/pf-setup project my-first-idea
```

It stands up everything a project needs (a connected projects folder, GitHub, the chosen host's CLI and sign-in, a database if needed, monitoring, backups) and walks you through each human step. On the **very first run** it also runs `/pf-bootstrap` once, which installs Atelier's recommended helper skills from their official sources so the factory is fully equipped (Atelier bundles the three it may redistribute; the rest install on first run — see `THIRD-PARTY-NOTICES.md` and `atelier/references/skill-catalog.md`). See **Requirements** below for what to have installed first.

---

## Quickstart — your first product

In a **Cowork** session with the `atelier` plugin:

```
/pf-plan a simple landing page for my coffee subscription, with an email signup
```

Atelier interviews you for the essentials, forecasts the cost (almost always **$0/month** to start), picks a methodology, writes the planning docs, and asks you to approve the plan. Then:

```
/pf-ship
```

runs design → build → deploy → harden, pausing to show you the design, the built preview, and to ask "deploy now?" before it goes live. When it's up, `/pf-monitor` adds a free safety net and `/pf-maintain` keeps it patched, backed up, key-rotated and within budget.

Prefer one step at a time? Run `/pf-design`, review, then `/pf-build`, `/pf-deploy`, `/pf-harden` yourself.

---

## What Atelier will never do

- Type your passwords, tokens or card numbers, or click the final submit on sign-up, payment or DNS pages — it pre-fills what's safe and hands those steps to you.
- Store a secret anywhere (it knows env-var **names** only, never values).
- Deploy, publish, merge or spend money without your explicit yes.
- Run the security pentest on a schedule, against production, or against anything with real data.
- Build remotely on paid CI, or create a billed resource without stopping to show you the price.
- Redistribute a skill whose license forbids it — the three bundled skills ship under their own permissive licenses (`THIRD-PARTY-NOTICES.md`) and everything else installs from its own official source; downgrade quality or security to save money.

## The contracts (what every build must pass)

Speed (mobile Lighthouse ≥ 90), security (secure by default — data-access rules, auth, input validation, headers, secret & dependency scans, defensive and self-only), SEO + AI-engine visibility (Google, Bing, ChatGPT, Claude, Perplexity), simple hand-off-ready code, the right design for the project at an Apple-grade bar, legal & compliance, and free-first cost — each a hard gate at build, re-checked live at harden. Quality and security are fixed first; cost is chosen under them, never over them.

---

## Requirements

On the machine that runs **Claude Code** (the builder):

- **Node 20+** and **Git**, and **GitHub CLI** (`gh`) signed in.
- Per chosen host, its CLI: `vercel`, Azure `az`, Docker Desktop, `wrangler` (Cloudflare), `netlify`, `gcloud`, or `flyctl`.
- A free **Supabase** account if the project needs a database.
- Remote Control on in Claude Code (`/remote-control`) so Cowork can drive it, or you paste the one `/pf-next` command when asked.

`/pf-setup` checks for these and gives you the exact install command for your OS (Windows / macOS / Linux). Atelier is cross-platform.

### Paths

- **Projects folder** — a folder you connect to the Cowork task; default `~/Atelier` (`%USERPROFILE%\Atelier` on Windows), or set `PF_WATCH_DIR`.
- **Code checkouts** — default `~/dev/atelier/<project>` (`%USERPROFILE%\dev\atelier\<project>` on Windows), or set `PF_CODE_DIR`.

---

## Documentation

- [`atelier/README.md`](atelier/README.md) — the full Cowork command map and how the pieces fit.
- [`atelier-builder/README.md`](atelier-builder/README.md) — the builder's skills and machine requirements.
- `atelier/references/` — the contracts (performance, security, SEO, compliance, cost, design) and how the pipeline works.

## Contributing

Issues and pull requests are welcome — see [`CONTRIBUTING.md`](CONTRIBUTING.md). A validator (`tests/check.sh`) checks the plugins' structure and guarantees; please keep it green.

## Disclaimer

Atelier automates software delivery but does not replace professional judgment. It flags legal, security and financial matters for a human (and, where it matters, a lawyer) rather than deciding them. You are responsible for what you ship. The compliance and security checks are aids, not guarantees of legal compliance.

## License

[MIT](LICENSE) © 2026 The Atelier Authors
