# SPEC.md — the build contract

Written by `/pf-build` into the project folder. Exactly these eight H2 headings, in this order, every one present (write `None` under a heading that doesn't apply). `/pf-build` refuses to send a spec with a missing heading.

```
# <Project name>

## Brief
## Stack
## Screens
## Tokens
## Components
## Data model
## Routes / API
## Acceptance checks
```

## Brief
One-liner, audience, and the goal of v1 — three short lines copied from `factory.json.brief`.

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

## Acceptance checks
Numbered, testable statements the builder must run and report pass/fail on, e.g. `1. GET / returns 200 and contains the Home headline`. At least one per screen; at least one per route.
