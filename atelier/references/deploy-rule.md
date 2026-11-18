# Deploy target rule (v2 — registry based)

Targets live in `references/targets/<name>.md`, one file each (Fits, Env vars, Preview, Deploy steps, Health check, Custom domain). Adding a tool = adding a file; no skill changes.

Shipping targets: `vercel`, `azure-static-web-apps`, `azure-container-apps`, `cloudflare-pages`, `netlify`, `github-pages`, `aws-amplify`, `gcp-cloud-run`, `render`, `fly-io`, `oracle` for the web, and `expo-eas` (React Native + Expo) and `flutter-stores` (Flutter and native) for mobile apps released to the App Store and Google Play (`mobile-release.md` — a store release has its own fees, review and owner-only publish step). The registry is extensible — a provider not listed gets a new target file (see `platform-selection.md`).

## How `/pf-deploy` picks

1. **Hint wins.** If `factory.json.brief.deploy_hint` names a target that exists in `targets/`, use it (`chosen_by: hint`).
2. **Otherwise recommend by fit** — use `references/platform-selection.md` (provider-agnostic, free-first), not an Azure default. Classify the project's needs from `SPEC.md` (Stack, Data model, Routes / API) and match the cheapest option that clears the bar across **all** providers:
   - Static export, no routes → a free static host: `github-pages` (public repo), `cloudflare-pages`, `netlify`, or `azure-static-web-apps` — pick by the user's accounts + simplicity.
   - Next.js / Supabase-only → `azure-static-web-apps` Free (when you hold Azure credits) **or** `cloudflare-pages`/`netlify`/`vercel` (Hobby, non-commercial) — all $0 at small scale.
   - A server / container / background work → a scale-to-zero host: `azure-container-apps`, `gcp-cloud-run`, `fly-io`, `render`, or `aws-amplify` — the best free fit for the runtime.
   - An always-on box / self-hosted open-source → `oracle` (Always Free ARM).
   - A mobile app → `expo-eas` (React Native + Expo) or `flutter-stores` (Flutter / native); its companion website (privacy policy, support page) deploys separately through a web target.
   State **one** recommendation with the reason + cost, then offer 2–3 real alternatives (including an open-source/self-host option when it fits). Azure is a strong option, never the automatic one.
3. **Ask** with AskUserQuestion: the recommendation first, marked "(Recommended)", then the alternatives, each with one line from its `## Fits`. Record `chosen_by: user` (or `rule` if the user accepts the recommendation).

Infra triggers (whole words, case-insensitive): `cron`, `scheduled job`, `schedule`, `queue`, `worker`, `websocket`, `Postgres server`, `SQL Server`, `Cosmos`, `Redis`, `Service Bus`, `Azure Functions`, `Container Apps`, `long-running`, `Temporal`, `Docker`. Not triggers: `Supabase Edge Functions`, `Supabase Realtime`. Precedence: any trigger wins, even alongside Supabase.

## Cost posture (all targets)

**Standing decision: aim for zero recurring fees**. **Platform is chosen by project fit** (`platform-selection.md`), not Azure by default — Azure is the default only where it is the best free fit and you hold credits; the zero-recurring-fee posture holds on whatever platform is chosen. Defaults: Static Web Apps **Free** plan (not Standard), Container Apps with consumption billing and `--min-replicas 0`, no Redis / managed cache, no paid add-ons. Before any step that creates a billed resource (SWA Standard, a Redis cache, a database server, a paid plan upgrade) the deployer must stop and ask with the monthly price shown.

Full free-first rule and the free-tier/credit inventory: `references/cost-posture.md` (try free tiers, then credits you already hold (a cloud startup grant, or a trial such as Oracle's ~$300), then another free tier, paid only on an explicit yes). Build locally; upload output or a locally built image. No remote build services (`vercel --prod` without `--prebuilt`, `az acr build`, Netlify/Cloudflare git builds) and no **GitHub-hosted** build/deploy runners (those bill minutes). A GitHub Actions workflow on a **self-hosted** runner (own hardware, $0 today) for CI — tests and the security gate on every push — is allowed and encouraged for data-sensitive projects; see `cost-posture.md`. The deploy itself still happens from a locally built artifact, not a hosted build. Which CI a project gets (`hook` / `self-hosted` / `hosted`) and what the workflow may do is defined in `verification.md` D. One stated exception to local builds: an iOS binary built from a non-Apple machine (`mobile-release.md` A).

## Preview first (every project, wherever the target has one)

Nothing goes live unseen and untested. When the chosen target's `## Preview` is not `None`, a deploy runs in **two stages**, each its own request (`stage: preview`, then `stage: live`):
1. **Preview** — the built output goes to the target's preview slot: a real URL on the real host, production untouched. The deployer runs the target's health check on it and the full **e2e suite against it** (`E2E_BASE_URL=<preview_url>`, `verification.md` B). A preview is never indexed (`X-Robots-Tag: noindex` where the host does not add it), never applies a migration, and — when the project has a Data model — uses the **test** database, never production data (`migrations.md` A). A failed preview stops the deploy; nothing live has changed.
2. **Live** — only after the go-live yes, which now shows the preview link and the e2e count. The live stage **promotes what was previewed** (the target's *Promote* line) rather than building something new, applies pending migrations first (`migrations.md` D), and tags the deployed commit `live-<yyyymmdd-HHMM>` — the marker the next rollback and the changelog use.
A target whose Preview is `None` (and the first-ever deploy on targets that need an existing service) skips stage 1: the same health check and e2e suite run against the **local production build** instead, and the go-live question says so. `streamlined` projects (`pf-ship`) run the preview without asking and pause once, at go-live; `guarded` projects are asked before the preview too.

## Infrastructure and gradual rollout (only where the plan set them)
When `factory.json.infra` is not `none`, the cloud resources are code in the repo's `infra/` and are previewed, approved and applied by the deploy exactly as `infrastructure.md` D says — a deletion, a replacement or a billable resource needs its own yes. When the deploy request says `rollout: canary`, the live stage sends 10% of traffic to the new version, bakes, then 100% (`rollout.md` B); otherwise it is `full`.

## Auto-rollback (a bad deploy heals itself — see `references/monitoring.md` D)

Every deploy keeps the **last known-good version** before shipping the new one (the prior built artifact we uploaded, or for `azure-container-apps` the previous **revision**). After deploying, run the target's health check, then watch `/api/health` + availability/error-rate for a short **bake window** (~5–10 min). If the health check fails or the bake window shows a clear regression, **roll back automatically** to that last known-good version (redeploy the prior artifact, or shift 100% traffic to the previous healthy revision) and alert the user. A healthy deploy is left live. **Never auto-revert the database** — a broken migration is flagged for a human, not rolled back; expand-then-contract migrations are **required** (`migrations.md` B) precisely so an app rollback always stays compatible; the last known-good version is the commit under the previous `live-` tag. Auto-rollback needs no new approval — it is a safety reaction to a deploy the user already approved; a fresh forward deploy still needs the go-live yes.

## The question, always

`Target: <name> — <one-line reason>. Deploy now?` with Yes / No. Deploy never starts on anything but Yes.
