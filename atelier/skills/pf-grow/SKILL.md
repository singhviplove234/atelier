---
name: pf-grow
description: "Phase-3 growth loop: reads the live site's own data — Google Search Console, GA4, Microsoft Clarity — and proposes a prioritized list of the next SEO, content, conversion and AI-visibility fixes, each with the signal behind it. Recommend-only: it proposes, the user picks, and each chosen item goes through the normal build/harden flow. Use when the user says /pf-grow, 'how do I grow this', 'what should I improve', 'read my analytics', 'SEO next steps', 'why is traffic flat', or 'what should I write next'. Supports --schedule and --dry-run. Changes nothing on its own."
---

# /pf-grow <slug> [--schedule monthly] [--dry-run]

Turn the measurement foundation into the next move. Read first:
- `${CLAUDE_PLUGIN_ROOT}/references/growth.md` (this stage's contract)
- `${CLAUDE_PLUGIN_ROOT}/references/seo-ai-visibility.md`, `performance-budget.md`
- `${CLAUDE_PLUGIN_ROOT}/references/state-schema.md`

## 0. Flags
`--schedule monthly`: set a recurring "what to do next" and stop. `--dry-run`: print the sources it would read; read nothing; stop.

## 1. Gate
Locate the project; read `factory.json`. Require `deploy.live_url` and that the measurement foundation is set up (`seo-ai-visibility.md` F / `monitoring.md`). If GA4 / Search Console are not connected, say so and point to `/pf-setup seo` (and `/pf-setup monitor`), then offer to work from whatever is available.

## 2. Read (free sources, per `growth.md`)
Search Console (queries, impressions/clicks/CTR, position, coverage), GA4 (traffic, top/underperforming pages, drop-off, conversions), Clarity (if set up), and the site's current SEO / Core Web Vitals. Guide any auth the `/pf-setup` way; use the connectors/APIs where available.

## 3. Propose (prioritized, per `growth.md`)
A ranked list as a living doc (or rows on the dashboard), each item = the signal + the fix + the expected gain, across SEO, content, conversion/UX and AI visibility. **Nothing is changed.**

## 4. Hand picked items to the pipeline
The user picks; each chosen item becomes a normal `/pf-build` fix or `/pf-harden` pass, so it still goes through the contracts and gates. Record `factory.json.growth` (`last_run`, `report_url`); log it.

## Never
- Change the live site, its content or settings on its own — it proposes; The user picks; the normal flow builds it.
- Require or recommend a paid SEO tool — the free sources suffice; paid only on an explicit ask.
