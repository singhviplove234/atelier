# Deploy target rule (v2 — registry based)

Targets live in `references/targets/<name>.md`, one file each (Fits, Env vars, Deploy steps, Health check, Custom domain). Adding a tool = adding a file; no skill changes.

Shipping targets: `vercel`, `azure-static-web-apps`, `azure-container-apps`, `cloudflare-pages`, `netlify`, `github-pages`, `aws-amplify`, `gcp-cloud-run`, `render`, `fly-io`, `oracle`. The registry is extensible — a provider not listed gets a new target file (see `platform-selection.md`).

## How `/pf-deploy` picks

1. **Hint wins.** If `factory.json.brief.deploy_hint` names a target that exists in `targets/`, use it (`chosen_by: hint`).
2. **Otherwise recommend by fit** — use `references/platform-selection.md` (provider-agnostic, free-first), not an Azure default. Classify the project's needs from `SPEC.md` (Stack, Data model, Routes / API) and match the cheapest option that clears the bar across **all** providers:
   - Static export, no routes → a free static host: `github-pages` (public repo), `cloudflare-pages`, `netlify`, or `azure-static-web-apps` — pick by the user's accounts + simplicity.
   - Next.js / Supabase-only → `azure-static-web-apps` Free (when you hold Azure credits) **or** `cloudflare-pages`/`netlify`/`vercel` (Hobby, non-commercial) — all $0 at small scale.
   - A server / container / background work → a scale-to-zero host: `azure-container-apps`, `gcp-cloud-run`, `fly-io`, `render`, or `aws-amplify` — the best free fit for the runtime.
   - An always-on box / self-hosted open-source → `oracle` (Always Free ARM).
   State **one** recommendation with the reason + cost, then offer 2–3 real alternatives (including an open-source/self-host option when it fits). Azure is a strong option, never the automatic one.
3. **Ask** with AskUserQuestion: the recommendation first, marked "(Recommended)", then the alternatives, each with one line from its `## Fits`. Record `chosen_by: user` (or `rule` if the user accepts the recommendation).

Infra triggers (whole words, case-insensitive): `cron`, `scheduled job`, `schedule`, `queue`, `worker`, `websocket`, `Postgres server`, `SQL Server`, `Cosmos`, `Redis`, `Service Bus`, `Azure Functions`, `Container Apps`, `long-running`, `Temporal`, `Docker`. Not triggers: `Supabase Edge Functions`, `Supabase Realtime`. Precedence: any trigger wins, even alongside Supabase.

## Cost posture (all targets)

**Standing decision: aim for zero recurring fees**. **Platform is chosen by project fit** (`platform-selection.md`), not Azure by default — Azure is the default only where it is the best free fit and you hold credits; the zero-recurring-fee posture holds on whatever platform is chosen. Defaults: Static Web Apps **Free** plan (not Standard), Container Apps with consumption billing and `--min-replicas 0`, no Redis / managed cache, no paid add-ons. Before any step that creates a billed resource (SWA Standard, a Redis cache, a database server, a paid plan upgrade) the deployer must stop and ask with the monthly price shown.

Full free-first rule and the free-tier/credit inventory: `references/cost-posture.md` (try free tiers, then credits you already hold (a cloud startup grant, or a trial such as Oracle's ~$300), then another free tier, paid only on an explicit yes). Build locally; upload output or a locally built image. No remote build services (`vercel --prod` without `--prebuilt`, `az acr build`, Netlify/Cloudflare git builds) and no **GitHub-hosted** build/deploy runners (those bill minutes). A GitHub Actions workflow on a **self-hosted** runner (own hardware, $0 today) for CI — tests and the security gate on every push — is allowed and encouraged for data-sensitive projects; see `cost-posture.md`. The deploy itself still happens from a locally built artifact, not a hosted build.

## Auto-rollback (a bad deploy heals itself — see `references/monitoring.md` D)

Every deploy keeps the **last known-good version** before shipping the new one (the prior built artifact we uploaded, or for `azure-container-apps` the previous **revision**). After deploying, run the target's health check, then watch `/api/health` + availability/error-rate for a short **bake window** (~5–10 min). If the health check fails or the bake window shows a clear regression, **roll back automatically** to that last known-good version (redeploy the prior artifact, or shift 100% traffic to the previous healthy revision) and alert the user. A healthy deploy is left live. **Never auto-revert the database** — a broken migration is flagged for a human, not rolled back; prefer backward-compatible (expand-then-contract) migrations so an app rollback stays compatible. Auto-rollback needs no new approval — it is a safety reaction to a deploy the user already approved; a fresh forward deploy still needs the go-live yes.

## The question, always

`Target: <name> — <one-line reason>. Deploy now?` with Yes / No. Deploy never starts on anything but Yes.
