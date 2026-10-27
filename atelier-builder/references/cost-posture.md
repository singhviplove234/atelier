# Free-first, secure-first — how the factory chooses what a project runs on

Standing requirement: for every project the factory evaluates the need and proposes the **free, secure** way first. It only proposes paid when a free option genuinely cannot meet a real requirement, and then it stops and asks with the monthly price and the reason. Free tiers can be **combined**, but the result stays **minimal and easy** — the fewest moving parts that do the job, presented as one simple line, never a menu.

This is **provider-agnostic**: free-first applies the same across every cloud — Azure, AWS, GCP, Oracle, Vercel, Cloudflare, Netlify, Render, Fly.io — and open-source / self-hosted setups alike. The platform is chosen by **project fit** (`platform-selection.md`): the cheapest option that clears the bar, never a default cloud. Azure is preferred only where it is the best free fit **and** you hold credits to absorb overflow.

## Quality is the bar, not cost (never compromised)
Free-first means **free where free genuinely meets what this project needs** — it never means shipping a weaker, slower, flakier or less-secure product to save money. The project's required quality is fixed first; cost is chosen under it, not over it. If a free tier cannot meet that bar, the factory **recommends the paid option it does need** (cheapest that fits, with the price, and asks) rather than degrading the product onto a free tier that throttles, pauses, or can't scale. The other contracts — performance, security, SEO, compliance, design — are met in full at **every** cost tier; "free" never overrides them.

## Evaluate the project first (then pick the tier that clears the bar)
Before recommending anything, judge this project's real requirements and match the cost tier to them:
- **Audience & stakes:** internal/hobby vs client-facing/production; a commercial product cannot run on a non-commercial free tier (e.g. Vercel Hobby).
- **Traffic & bandwidth:** expected visitors and data transfer vs the free tier's limits.
- **Uptime / reliability:** does it need an SLA or always-on? A free tier that sleeps or pauses (e.g. Supabase free pausing when idle) is fine for a demo, not for a live client service — recommend the paid/always-on option there.
- **Data sensitivity & compliance:** client/financial/personal data (data-sensitive) may need a paid tier for region, backups, private networking or an SLA — do not force it onto a bare free tier.
- **Scale & growth:** if it will clearly outgrow the free limits soon, say so now and show the paid step and its cost, rather than a free setup that breaks in a month.

Match the recommendation to that evaluation: a small internal tool → free tier; a demo → free, with the pause caveat stated; a live client product with real users or sensitive data → the tier that actually meets its reliability/compliance bar, free if it clears it, paid (with price, on your yes) if it doesn't.

## The order to try (cheapest option that still clears the bar, first)
1. **Free tier of the obvious tool — when it meets the bar.** Azure Static Web Apps **Free**, Container Apps scaled to zero, Supabase free tier, a tool's own free allowance. Secure defaults always on. Skip a free tier that can't meet this project's reliability/scale/compliance needs (above) and move down the list.
2. **Free credits we already hold**, for what exceeds a free tier: **cloud startup or trial credits you already hold** first; a provider's trial credits (e.g. Oracle's ~$300 / 30 days) second. Credits are finite and expire — use them for the overflow, not as the baseline.
3. **Another provider's free tier**, as a fallback, when it keeps the project free: **Oracle Cloud Always Free** (up to ~24GB ARM, 200GB storage, ~10TB egress, 2 databases — ARM capacity is scarce and 2026 terms tightened, so verify), **Vercel Hobby** (non-commercial only; commercial needs paid Pro), **Cloudflare/Netlify free** tiers.
4. **Paid — when the project needs it.** When no free combination meets the project's real quality bar (commercial licence, bandwidth beyond free, an uptime SLA, always-on database, compliance, scale), name the **cheapest** paid option that **actually meets the bar** (not the cheapest overall), show the **monthly cost** and what it buys, and **ask** before anything billable is created. Recommending paid here is correct, not a failure — cost never beats the quality the project needs. Never auto-upgrade.

## Avoid these paid traps (free equivalents exist)
- **GitHub Actions — avoid the *paid* path, not CI itself.** The cost trap is **GitHub-hosted** runner minutes beyond the monthly free allowance (private repos get a free tier, then it's billed) used to **build or deploy** — don't run remote builds there; build locally and **push the result straight to the host** (Azure / prebuilt upload). But **CI on a *self-hosted* runner (your own PC / your own box) costs $0 today** and is allowed — and is the right call for a data-sensitive project that wants tests, a secret scan and the security checks gating every push before anything merges. Public repos are free either way. (GitHub floated a $0.002/min self-hosted charge for March 2026 but **postponed** it after backlash; if that charge ever lands, revisit this and move the gate to local pre-push hooks.)
  - **The free hosted allowance is itself a free tier — usable as a last resort.** If a step genuinely needs a GitHub-**hosted** runner and there is no self-hosted or local way to do it, the monthly free allowance (2,000 min on Free, 3,000 on Pro — GitHub-hosted, resets each cycle) may be used for it, because a free tier used within its limit is still $0. Two conditions, always: (1) prefer self-hosted/local first — those are unlimited and burn no quota; (2) usage must stay comfortably inside the allowance — the moment a need would spill into **billed overage**, stop and ask with the monthly cost (free-first, never a silent overage, never an auto-upgrade). Deploy builds still run locally and push a prebuilt artifact regardless; the free minutes are not a licence to remote-build.
- **Remote build minutes** (`vercel --prod` without `--prebuilt`, `az acr build`, git-triggered host builds) → build locally, upload the artifact/image.
- **Managed Redis / caches / paid add-ons** → the free caching layer (CDN, framework cache, headers) first; a paid cache only on an explicit yes.

## Keep it minimal (the part that matters most)
- Default is **one host + one database** (Azure SWA/Container Apps + Supabase). Add a second free service only when the project genuinely needs it — never stitch five free tiers together to save a dollar if one tool does the job.
- Present the choice as **one plain line**: e.g. "Free plan: Azure Static Web Apps hosts it, Supabase is the database — **$0/month**." Not a comparison table, not options to pick from, unless the user asks.
- The user is not technical: no juggling of dashboards. If a free tier needs a human step (a sign-up, a credit application), `/pf-setup` walks them through it one step at a time.

## When the factory re-checks cost
- **At design/scope** (`/pf-design`): pick the free stack for the project's real size and likely growth.
- **At deploy** (`/pf-deploy`, with `deploy-rule.md`): confirm the free target still fits; flag any billable step.
- **At harden** (`/pf-harden` limits pass): list what would force a paid tier at 10x traffic, with the monthly cost — recommend only, create nothing.
- **In maintenance** (`/pf-maintain`, `maintenance.md` F): read the **real** month-to-date bill / free-tier usage per provider (Azure cost tools where available, else the provider's billing page), compare it to the forecast, to $0, and to each free-tier limit, and alert on drift toward billable **before** it bills — recommend-only, never a downgrade of the product and never an auto-change.

The rule in one sentence: **meet the quality the project needs, and within that pick the cheapest secure option — free when it clears the bar, our credits for the overflow, paid (with price, on your yes) when free can't do the job; kept minimal.**
