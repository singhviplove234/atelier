---
name: pf-design
description: "Starts an Atelier project: scopes an idea, writes a brief, and creates a Claude Design artifact with one artboard per screen from the shared pf-design-system, then waits for approval. Use when the user says /pf-design, 'design a product', 'start a new product', 'new product idea', or wants mockups before any code is written."
---

# /pf-design

Turn an idea into an approved design. Stop after presenting the design — never build code here.

Read `${CLAUDE_PLUGIN_ROOT}/references/state-schema.md` before writing `factory.json`.

## 1. Slug and folder

1. Take the idea text after `/pf-design`. If empty, ask for it in one sentence.
2. Derive the slug: lowercase; keep only `[a-z0-9]`, replacing every other run of characters with `-`; trim leading/trailing `-`; truncate to 100 characters. (`"My SaaS Idea!"` → `my-saas-idea`). If the slug is empty (all punctuation or non-Latin text), ask for a short English project name and derive again. This kebab-case slug is the folder name, `code_path` leaf and GitHub repo name.
3. Project folder = `<connected Atelier folder>/<slug>/`. Find it with `device_list_dir` among the connected folders: prefer the one whose leaf name is `Atelier` (the recommended name, or wherever `PF_WATCH_DIR` points). If exactly one folder is connected, use it; if several are and none is named `Atelier`, ask which to use with AskUserQuestion; if none is connected, stop and ask the user to create and connect an `Atelier` folder (the README explains it).
4. If `<folder>/factory.json` already exists, ask with AskUserQuestion: **Resume** (continue from the current gate) or **Start over** (move the old folder to `<slug>-old-<yyyymmdd>` first). Never overwrite silently.

## 2. Scope (at most two questions)

**If an approved plan already exists** (`factory.json.gates.plan == "approved"`, from `/pf-plan`): skip scoping — use that brief, lanes and methodology as given, keep `gates.plan` as-is, and go straight to the Design System step. Planning already gathered the requirement.

Otherwise ask with AskUserQuestion, one at a time, only what the idea text does not already answer:
- Which screens/pages? Offer 2–3 sensible sets for the idea (e.g. landing: Home, Pricing, Contact; app: Login, Dashboard, Settings).
- Backend needed? Options: no; yes — simple data (name the entities); yes — accounts + data.

## 3. Brief

Fill `${CLAUDE_PLUGIN_ROOT}/skills/pf-design/references/brief-template.md` (Name, One-liner, Audience, Goal, Screens, Backend, Stack, Deploy hint, Lanes). **Lanes** defaults to `solo`; a team project lists its lanes (e.g. `frontend, backend`). Deploy hint may name a target from `references/targets/` (`vercel`, `azure-static-web-apps`, `azure-container-apps`, `cloudflare-pages`, `netlify`, `github-pages`) or stay blank for the rule to recommend. **Free-first (read `references/cost-posture.md`):** pick the free, secure stack for this project and say the plan in one plain line (e.g. "Azure Static Web Apps + Supabase — $0/month"); only mention paid if a free option genuinely can't meet a stated need, with the price, and ask. Keep it to one host + one database unless the project needs more. **Design direction:** read `${CLAUDE_PLUGIN_ROOT}/references/design-standard.md` and set `brief.design_direction` to the best fit — `brand` (premium/luxury/lifestyle/D2C/portfolio — cinematic, motion-led), `product` (SaaS/dashboard/tool — clean, dense, minimal), `editorial` (blog/docs/media — typography-first), or `marketing` (landing/conversion — bold hero + one CTA). State the chosen direction in one line; ask one short question only if two directions genuinely fit. The design-system and build execute that direction on the shared foundation (tokens, accessibility, licensed fonts/icons). **Size estimate:** judge the project's size now (screens + routes + data model) and whether it is likely to grow large (a platform/multi-module product): set `brief.size` to `small` or `large` — `large` when it already has many screens/entities **or** is the kind of product whose codebase will get big. When `large`, set `brief.context_tooling: recommended` and tell the user in one line that a free context tool (claude-mem / Graphify) will be suggested at setup so big builds stay fast and cheap. Stack is pre-filled with the default `Next.js + Tailwind + shadcn/ui (TypeScript); Supabase`; drop `; Supabase` when backend is no. Show the brief and say: "Edit any line now — the stack locks when you approve the design." Apply any edits.

## 4. Design System

Find the shared Design System: Artifact `list` with `type: "Design System"`, look for title `pf-design-system`. If absent, create it from the Design System type (title `pf-design-system`) **to `${CLAUDE_PLUGIN_ROOT}/references/design-standard.md`** (Apple-grade polish, web-licensed assets): one accent colour over a neutral ramp in light and dark (WCAG AA), the `Inter` type scale, a 4-pt spacing grid, 2–3 radii, soft sparing elevation, and components Button/Card/Input/Nav/Hero/Footer each with hover/focus/active/disabled states and a visible focus ring; icons from an open set (Lucide/Heroicons); optional tasteful frosted-glass surface, and a motion layer (scroll-reveal, micro-interactions, hero/section transitions) applied in proportion to `brief.design_direction` — rich for `brand`, minimal for `product`. Never Apple SF Pro/New York or SF Symbols. Record its URL as `artifacts.design_system_url`. Reuse it for every project; only change it when the user asks.

## 5. Design artifact

Create a Design artifact from the Design type, title `<slug> — design`, following the type's instructions. One artboard per screen in brief order, desktop size, using the Design System tokens and components. When the session has the official design skills (design-taste-frontend / high-end-visual-design / minimalist-ui, and animation-performance for the motion layer), use them to execute `brief.design_direction` to a higher bar — see `references/skills.md`; `design-standard.md` still governs tokens, AA contrast, licensed fonts/icons and the perf/motion budgets (the contract wins on any conflict). Put real, specific copy on every artboard (headline, body, button text) — the build step copies it verbatim into `SPEC.md`. Record the URL as `artifacts.design_url`.

## 6. Write state and stop

Write `factory.json` exactly per `state-schema.md`: `name`, `created` (now, with offset), the brief fields, both artifact URLs, `gates.design`/`gates.build`/`gates.deploy` = `pending` (leave `gates.plan` as-is — `approved` if `/pf-plan` set it, else `pending`), `code_path` = `<code root>/<slug>`, empty `repo_url`/`deploy`, `pm_lane` = the first lane in the brief (`solo` on solo), and `lanes`: one entry per lane — `solo` → `{branch: "main", scope: "all", code_path: <code root>/<slug>}`; the PM lane of a team → `{branch: "lane/<name>", code_path: <code root>/<slug>}`; every other lane → `{branch: "lane/<name>", code_path: <code root>/<slug>--<name>}`; `scope` from the brief's Lanes line (`frontend: Home, Pricing; backend: /api/*`) — every screen and route must belong to exactly one lane, else ask; each with `code_url: ""`, `status: "idle"`, `approved: false`; plus one `log` entry `{stage: "design", event: "created"}`. If any lane has no `code_url`, add: "Run `/pf-setup` to connect each lane's Code session." Open the Design artifact for the user, show the brief, and say: "Review the artboards. Say **yes** to approve the design, or tell me what to change." Then stop.

## 7. Approval handling

- Flip `gates.design` to `approved` **only** per "Approval words" in `state-schema.md` (`yes`, `approve`, `approved`, `go ahead`). A "yes, but …" that carries a change is a change request — apply the change and re-present; do not flip. On anything else that sounds positive (`looks good`, `nice`, `ok`), ask with AskUserQuestion: "Approve the design? (yes/no)". Do not flip on `ok` alone.
- On change requests: revise the artboards (republish the same artifact URL), update the brief if screens changed, append a `log` entry `{stage: "design", event: "revised: <summary>"}`, re-present.
- On approval: set the gate, append `{stage: "design", event: "approved"}`, and say: "Design approved. Run `/pf-build` when you're ready."
- After approval, refuse any change to `brief.stack` ("Stack is locked after design approval — start over to change it").

## Never
- Build, scaffold or write code here.
- Store any secret in `factory.json` or the brief.
- Create a second Design System unless asked.
