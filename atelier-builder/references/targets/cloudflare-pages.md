# Target: cloudflare-pages

## Fits
Static sites and Next.js apps (via `@cloudflare/next-on-pages`) with very high traffic expectations. Free: unlimited bandwidth, 500 builds/month, custom domains, SSL.

## Env vars
Required: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`
Optional: —
Checks: `npx wrangler --version` runs

## Deploy steps
1. **Local build**: `npm run build` (Next.js: `npx @cloudflare/next-on-pages`).
2. `npx wrangler pages project create <slug> --production-branch main` (first run).
3. `npx wrangler pages deploy <outdir> --project-name <slug> --branch main` — direct upload; no remote build.
4. `live_url` = `https://<slug>.pages.dev`.

## Health check
`curl` the live URL → 200.

## Custom domain
Cloudflare dashboard → Pages → <slug> → Custom domains → Set up. If the domain's DNS is on Cloudflare it is one click; otherwise add the CNAME shown. Claude opens the page and pre-fills the domain; The user clicks.
