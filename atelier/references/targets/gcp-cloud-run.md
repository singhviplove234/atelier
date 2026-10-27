# Target: gcp-cloud-run

## Fits
A real server or container (any runtime — Node, Python, Go) that **scales to zero** on **GCP**. Cloud Run's free tier is generous (~2M requests/month). Best when the project needs a server or background work and you want $0 at small scale. Overkill for a pure static site.

## Env vars
Required: `gcloud` auth (`gcloud auth login`, or a service account via Workload Identity — no key file in the repo); `GCP_PROJECT`, `GCP_REGION`
Optional: `SUPABASE_URL`, `SUPABASE_ANON_KEY`
Checks: `gcloud --version` and `gcloud config get-value project` run

## Deploy steps
1. Build the image **locally**: `docker build -t <GCP_REGION>-docker.pkg.dev/<GCP_PROJECT>/pf/<slug>:<tag> .` — never Cloud Build.
2. Auth + push: `gcloud auth configure-docker <GCP_REGION>-docker.pkg.dev` then `docker push <image>` to Artifact Registry.
3. Deploy: `gcloud run deploy <slug> --image <image> --region "$GCP_REGION" --allow-unauthenticated --min-instances 0`.
4. `live_url` = the printed Cloud Run service URL.

## Health check
`curl -s -o /dev/null -w "%{http_code}" <live_url>/api/health` → 200.

## Custom domain
Cloud Run → Manage custom domains (or a load balancer); it shows the DNS records. The user adds them at the registrar; Claude pre-fills and stops before Save.
