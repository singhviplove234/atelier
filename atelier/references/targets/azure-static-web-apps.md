# Target: azure-static-web-apps

## Fits
Static sites and Next.js apps (static export or SWA hybrid) when everything should stay in Azure. Free tier: 100 GB/month, custom domains, SSL. Needs `az login`.

## Env vars
Required: (none — the deployment token is fetched per run into a shell variable, never written anywhere)
Optional: `SUPABASE_URL`, `SUPABASE_ANON_KEY`
Checks: `az account show` succeeds

## Deploy steps
1. `az staticwebapp create --name <slug> --resource-group pf-<slug> --location <region> --sku Free` (create the RG first if missing). Hold the deployment token in a shell variable for this command only — `SWA_TOKEN=$(az staticwebapp secrets list --name <slug> --query properties.apiKey -o tsv)` — never write it to a file or print it.
2. **Local build**: `npm run build` (for static export set `output: 'export'` in `next.config` → `./out`).
3. `npx @azure/static-web-apps-cli deploy ./out --deployment-token "$SWA_TOKEN" --env production` (or `.next` per SWA Next.js guidance).
4. `live_url` = `https://` + `az staticwebapp show --name <slug> --query defaultHostname -o tsv`.

## Health check
`curl` the live URL → 200.

## Custom domain
`az staticwebapp hostname set --name <slug> --hostname <domain>` after the user adds the CNAME shown by `az staticwebapp hostname show`. Claude prepares the command; The user confirms.
