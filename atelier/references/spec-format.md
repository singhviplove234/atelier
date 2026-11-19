# SPEC.md — the build contract

Written by `/pf-build` into the project folder. Exactly these **nine** H2 headings, in this order, every one present (write `None` under a heading that doesn't apply — except `## Diagrams`, which is never `None`). `/pf-build` refuses to send a spec with a missing heading, and the builder refuses to build one. (`/pf-build` also writes a `## Scope` section *before* these nine — it is the lane's scope note, not one of the nine.)

```
# <Project name>

## Brief
## Stack
## Screens
## Tokens
## Components
## Data model
## Routes / API
## Diagrams
## Acceptance checks
```

## Brief
One-liner, audience, and the goal of v1 — three short lines copied from `factory.json.brief`. Plus the SEO inputs (`seo-ai-visibility.md` A), a `Locales:` line (the locale list, source locale first — one entry unless the plan chose more; `i18n.md`), and, when the plan set them, `Flags:` (name, default, owner, remove-by — `rollout.md`), `3D scene:` (`shapes` or `model`, and the screen that carries it — `scene-3d.md`) and the SaaS blueprint decisions.

## Stack
Framework, styling, DB/auth, language. Locked at design approval. Default: `Next.js (App Router) + Tailwind + shadcn/ui, TypeScript; Supabase for DB/auth`.

## Screens
One `### <Screen name>` subsection per artboard in the Design artifact, in canvas order. Each has: `Route:` (e.g. `/pricing`), `Purpose:` (one line), `Copy:` (the exact headline, body and button text from the artboard — verbatim), `Components:` (names from the Components section).

## Tokens
CSS custom properties taken from the `pf-design-system` artifact (built to `references/design-standard.md`): colours for light and dark (`--color-bg`, `--color-fg`, `--color-primary`, …) at WCAG AA, the `Inter` type scale (`--text-xs` … `--text-4xl` with font families), a 4-pt spacing scale, radius scale. Written so they can be pasted into `app/globals.css`. These tokens are the only styling source — no hard-coded hex or arbitrary font px in screens.

## Components
Inventory of reusable components with a one-line props sketch each, e.g. `PricingCard(title, price, features[], cta)`.

## Data model
Tables/collections with fields and types, plus which are user-scoped. `None` when `brief.backend == false`.

## Routes / API
Endpoints as `METHOD /path — input → output`. Include auth requirement per route. `None` when no backend.

## Diagrams
**Every project, page and feature is diagrammed before a line is built — this heading is the gate.** Each diagram is a fenced ` ```mermaid ` block whose first line is an id comment (`%% id: app-architecture`); the id is the filename the builder renders to, so it must be unique and stable across builds. Three groups:
- **App (always two):** `app-architecture` — the stack, the pieces and how they fit, carried over from the plan's architecture overview (`planning.md` §5) and updated to the locked stack; `app-journey` — the sitemap / primary user journey across the screens.
- **One per screen:** `page-<slug>` for every in-scope `### <Screen>` — a user-flow diagram: how the user arrives, what they can do, where each action leads. *Grouping rule:* screens that differ only in the data they show (a list and its detail view, the three tabs of one settings page) may share one diagram — declare it with a second comment line `%% covers: <Screen A>, <Screen B>`; every in-scope screen must appear in exactly one `page-` block's id or `covers:` line.
- **One per feature:** `feature-<slug>` — a sequence or flow diagram: user action → UI → route → data → response, **including the failure path**. The feature set is defined, not guessed: (1) each **route group** under `## Routes / API` — routes sharing the first path segment after `/api/` (`/api/notes` and `/api/notes/:id` are one group); (2) each **user-scoped table** under `## Data model` — any table marked user-scoped, or with an owner/user id column, or under RLS; (3) each **capability the Brief names** — auth/sign-in, payments, search, upload, email/notifications, scheduled jobs, an interactive 3D scene, integrations with a named third party. One `feature-` block may satisfy several of these at once (the notes route group + the notes table + "save notes" is one feature) — declare it with `%% covers: routes /api/notes, table notes, capability notes`. Every route group, user-scoped table and named capability must appear in exactly one `feature-` block's id or `covers:` line.
Mermaid is the editable source of truth. The builder renders every block itself (`diagram-render.md`; the builder's gate: `pf-build-from-spec` §1b) into `docs/diagrams/<id>.mmd|.png|.svg`, in the project's brand from `## Tokens`, and commits them with the build. It refuses to scaffold if any screen or feature is uncovered — and fails the build, rather than carrying on, if a block will not render. A later build re-renders only the blocks that changed and removes the files of ids that no longer exist — the rendered copy never drifts from the source.

## Acceptance checks
Numbered, testable statements the builder must run and report pass/fail on, e.g. `1. GET / returns 200 and contains the Home headline`. At least one per screen; at least one per route.
