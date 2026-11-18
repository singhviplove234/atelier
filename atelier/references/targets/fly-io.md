# Target: fly-io

## Fits
A container app at the edge on **Fly.io** — any runtime, deploys a Docker image, runs close to users, scales to zero. The free allowance covers small apps. Good when you want a container near users at $0 small-scale. Overkill for a pure static site.

## Env vars
Required: `FLY_API_TOKEN`; the app name in `fly.toml`
Optional: `SUPABASE_URL`, `SUPABASE_ANON_KEY`
Checks: `flyctl version` runs; `flyctl auth whoami` with the token succeeds

## Preview
None by default (a second Fly app is a second machine to pay attention to). Verify on the local production image (`docker run`) and run e2e there. If the project needs a standing staging app, that is a plan-time decision with its cost stated.

## Deploy steps
1. Build the image **locally**: `docker build -t <slug> .`.
2. First run: `flyctl launch --no-deploy` to create `fly.toml`. Then `flyctl deploy --local-only --image <slug> --app <slug>` — `--local-only` uses the local image, **no remote builder**.
3. `live_url` = `https://<slug>.fly.dev`.

## Health check
`curl -s -o /dev/null -w "%{http_code}" <live_url>/api/health` → 200.

## Custom domain
`flyctl certs add <domain>`; it prints the DNS records. The user adds them at the registrar; Claude gives the exact records and stops.
