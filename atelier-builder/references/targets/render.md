# Target: render

## Fits
A full-stack web service, static site, or container on **Render** — a simple PaaS. Free tier: a web service (spins down when idle → cold start on wake) and static sites. Best for a single service deployed with minimal setup. The free service sleeping makes it a demo/low-traffic fit, not always-on client production — recommend a paid always-on tier (with the price, on a yes) for a live client service.

## Env vars
Required: `RENDER_API_KEY`; `RENDER_SERVICE_ID` (after first create)
Optional: `SUPABASE_URL`, `SUPABASE_ANON_KEY`
Checks: `curl -s -H "Authorization: Bearer $RENDER_API_KEY" https://api.render.com/v1/services` returns 200

## Deploy steps
1. Build locally (static output, or a Docker image pushed to a free registry).
2. Static site → upload the built output; service → point Render at the prebuilt image, or let Render build from the repo (its build is **included free** on the free tier — acceptable here since it is not separately metered like GitHub Actions). Create via `POST /v1/services` (first run), then `POST /v1/services/<id>/deploys`.
3. `live_url` = the printed `onrender.com` URL.

## Health check
`curl -s -o /dev/null -w "%{http_code}" <live_url>/api/health` → 200.

## Custom domain
Render dashboard → Settings → Custom Domains → Add; it shows the DNS record. The user adds it at the registrar; Claude pre-fills and stops.
