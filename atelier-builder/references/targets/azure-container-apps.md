# Target: azure-container-apps

## Fits
Full apps: databases you run, workers, queues, cron, websockets, multi-service platforms. Consumption plan has a monthly free grant that covers a low-traffic app when it scales to zero. **Zero-fee posture:** image registry is GitHub Container Registry (`ghcr.io`, free with the project's GitHub account) — Azure Container Registry Basic costs ~US$5/month and is used only if the user says yes to that fee. Needs `az login`, `gh auth`, and Docker Desktop.

## Env vars
Required: `GHCR_TOKEN` (GitHub token with write:packages, for ghcr.io) plus the app's own: `SUPABASE_*`, `DATABASE_URL`, `CRON_SECRET` as the SPEC needs
Optional: —
Checks: `az account show` succeeds; `docker info` succeeds

## Preview
Set the app to multiple-revision mode once (`az containerapp revision set-mode --name <slug> --resource-group pf-<slug> --mode multiple`), then deploy the new image as a revision that takes **no traffic**: `az containerapp update --name <slug> --resource-group pf-<slug> --image <registry>/<slug>:<gitsha> --revision-suffix <gitsha>` followed by `az containerapp ingress traffic set --name <slug> --resource-group pf-<slug> --revision-weight <previous revision>=100`, and give it a label URL: `az containerapp revision label add --name <slug> --resource-group pf-<slug> --label preview --revision <slug>--<gitsha>`. `preview_url` = the label's URL. **Promote:** `az containerapp ingress traffic set … --revision-weight <slug>--<gitsha>=100` — the same image, no rebuild. First deploy of a project has no previous revision: there is no preview, verify on the local production build.

## Deploy steps
1. `az group create --name pf-<slug> --location <region>` (idempotent). Registry = `ghcr.io/<owner>/<slug>` (login: `echo $GHCR_TOKEN | docker login ghcr.io -u <owner> --password-stdin`, token from env var `GHCR_TOKEN` with `write:packages`; never print it). Only if the user explicitly approves the ~US$5/month: `az acr create --name <acr> --resource-group pf-<slug> --sku Basic`; `az acr login --name <acr>`.
2. **Build locally** — never `az acr build`: `docker build -t <registry>/<slug>:<gitsha> .` (generate a standard Next.js standalone / Python / Go Dockerfile if absent) then `docker push`.
3. First run: `az containerapp up --name <slug> --resource-group pf-<slug> --image <registry>/<slug>:<gitsha> --registry-server <registry host> --registry-username <owner> --registry-password $GHCR_TOKEN --ingress external --target-port <port>` (creates the environment and the app), then `az containerapp update --name <slug> --resource-group pf-<slug> --min-replicas 0 --max-replicas 2` so an idle app costs nothing. Then secrets fed from the local env: `az containerapp secret set --name <slug> --resource-group pf-<slug> --secrets name=value …` and `az containerapp update --set-env-vars NAME=secretref:name …`.
4. Later runs: `az containerapp update --name <slug> --resource-group pf-<slug> --image <registry>/<slug>:<gitsha>`.
5. Cron from the spec: `az containerapp job create --trigger-type Schedule --cron-expression "<expr>"` calling the route with `CRON_SECRET`.
6. `live_url` = `https://` + `az containerapp show --query properties.configuration.ingress.fqdn -o tsv`.

## Health check
`curl` the live URL → 200 within 5 minutes (cold start allowed).

## Custom domain
`az containerapp hostname add` + `hostname bind` with a managed certificate after the user sets the CNAME/TXT shown by `az containerapp hostname list`. Claude prepares; The user confirms.
