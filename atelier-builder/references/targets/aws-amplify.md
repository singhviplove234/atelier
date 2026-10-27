# Target: aws-amplify

## Fits
Static sites and Next.js (SSR supported) on **AWS**. Free tier is generous for the first 12 months, then low pay-as-you-go. Best when the project is already on AWS or needs AWS services. For a tiny static site a pure free static host is cheaper/simpler.

## Env vars
Required: AWS credentials via `aws configure`/SSO (short-lived — never a long-lived key in the repo); `AMPLIFY_APP_ID`
Optional: `SUPABASE_URL`, `SUPABASE_ANON_KEY`
Checks: `aws --version` and `aws amplify list-apps` run

## Deploy steps
1. Build locally: `npm ci && npm run build` (static export or Next build) — **local build**, never an Amplify-hosted build.
2. Create/confirm the app (first run): `aws amplify create-app --name <slug>` → `AMPLIFY_APP_ID`; create a branch `aws amplify create-branch --app-id "$AMPLIFY_APP_ID" --branch-name main`.
3. Deploy the prebuilt output via a manual deployment: `aws amplify create-deployment` then upload the zipped build output to the returned URL, then `aws amplify start-deployment`. Uploads the local artifact only.
4. `live_url` = `https://main.<AMPLIFY_APP_ID>.amplifyapp.com`.

## Health check
`curl -s -o /dev/null -w "%{http_code}" <live_url>` → 200.

## Custom domain
Amplify console → Domain management → Add domain; it shows the DNS records (CNAME/ANAME). The user adds them at the registrar; Claude pre-fills the domain field and stops before Save.
