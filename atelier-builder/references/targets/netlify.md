# Target: netlify

## Fits
Static sites and Next.js apps; similar to Vercel. Free: 100 GB/month, 300 build minutes (unused here — we upload prebuilt).

## Env vars
Required: `NETLIFY_AUTH_TOKEN`
Optional: —
Checks: `npx netlify --version` runs. The site id is created on first deploy and stored in `factory.json.deploy.netlify_site_id` (not a secret)

## Deploy steps
1. **Local build**: `npm run build`.
2. First run: `npx netlify sites:create --name <slug>` → record site id as `NETLIFY_SITE_ID` (env, never printed).
3. `npx netlify deploy --prod --dir <outdir> --site "$NETLIFY_SITE_ID" --auth "$NETLIFY_AUTH_TOKEN"` — uploads the built folder; no remote build.
4. `live_url` = the printed Website URL.

## Health check
`curl` the live URL → 200.

## Custom domain
Netlify → Site → Domain management → Add domain; set the CNAME/ALIAS shown at the registrar. Claude pre-fills; The user confirms.
