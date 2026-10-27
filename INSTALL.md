# Installing Atelier — step by step

Atelier is **two plugins for [Claude](https://claude.com)** that work together:

- **`atelier`** runs in **Claude Cowork** — it plans, designs and directs the work, and holds every approval gate.
- **`atelier-builder`** runs in **Claude Code** on your computer — it does the actual building, deploying and testing.

You install both. It takes a few minutes, and you don't need to be a developer — Atelier walks you through the human-only steps once you're set up.

## Before you start

You'll need Claude with access to **Cowork** and **Claude Code** (the plugin system), plus three tools on the computer that will do the building:

- **Node.js 20 or newer** — <https://nodejs.org>
- **Git** — <https://git-scm.com>
- **GitHub CLI (`gh`)**, signed in — <https://cli.github.com>

Not sure whether you have these? Install the plugins first, then run `/pf-setup` (Step 4) — it checks for each one and gives you the exact install command for your operating system (Windows, macOS or Linux).

## Step 1 — Add the Atelier marketplace (once)

In **either** Claude Code or Cowork, type:

```
/plugin marketplace add singhviplove234/atelier
```

This tells Claude where the two Atelier plugins live. Nothing is kept yet — it just registers the source.

## Step 2 — Install the Cowork half

In **Cowork**, type:

```
/plugin install atelier@atelier
```

## Step 3 — Install the builder half

In **Claude Code** (on the computer that will build your product), type:

```
/plugin install atelier-builder@atelier
```

No marketplace? You can also install by file: download `atelier.zip` and `atelier-builder.zip` from this repo's Releases (or zip the `atelier/` and `atelier-builder/` folders yourself), then in the Plugins panel choose **Add → Upload plugin** and pick the matching file.

## Step 4 — One-time setup

In **Cowork**, run:

```
/pf-setup project my-first-idea
```

This is the step that makes Atelier fully equipped. The **first time** you run it, it automatically:

- Installs the recommended helper skills from their own official sources (the three permissively-licensed ones ship with Atelier; the rest are fetched with one confirmation — see `THIRD-PARTY-NOTICES.md` and `atelier/references/skill-catalog.md`).
- Checks you have Node, Git and `gh`, and gives you the exact install command for anything missing.
- Walks you through the human-only bits one at a time: connecting a project folder, signing in to GitHub and your chosen host, and setting up a database if your project needs one.

After the first run, Atelier knows which skill to use when, and later projects skip straight past setup.

## Step 5 — Build your first product

In **Cowork**, describe what you want:

```
/pf-plan a simple landing page for my coffee subscription with an email signup
```

Atelier interviews you for the essentials, forecasts the cost (almost always **$0/month** to start), writes the planning docs, and asks you to approve the plan. Then:

```
/pf-ship
```

runs the whole chain — design, build, deploy, harden — and **pauses at each gate to show you the work and ask for your yes** before moving on. When it's live, `/pf-monitor` adds a free safety net and `/pf-maintain` keeps it patched and backed up.

Prefer to go one step at a time? Run `/pf-design`, review it, then `/pf-build`, `/pf-deploy`, `/pf-harden` yourself.

## Good to know

- **You need both Cowork and Claude Code.** Cowork is where you talk to Atelier; Claude Code (on your own machine) is where the building happens.
- **The first project is the slow one** — that's when setup and the skill install happen. Everything after is quicker.
- **Atelier never spends money or ships anything without asking.** It pre-fills what's safe and hands you the final click on anything that signs in, pays, deploys or publishes.
- **Stuck on a step?** `/pf-setup` can be re-run safely any time — it only does what's still missing.

See the main `README.md` for what Atelier is and the full command list, and `atelier/README.md` for the complete Cowork command map.
