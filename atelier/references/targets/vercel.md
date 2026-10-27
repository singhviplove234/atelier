# Target: vercel

## Fits
Static sites and Next.js apps whose only infra is Supabase (DB/auth, Edge Functions). Hobby tier: one person, 100 GB/month bandwidth. Not for apps that need servers you run, queues or cron.

## Env vars
Required: `VERCEL_TOKEN`
Optional: `SUPABASE_URL`, `SUPABASE_ANON_KEY` (only for apps with a backend)
Checks: `npx vercel --version` runs

## Deploy steps
1. `npx vercel pull --yes --environment=production --token "$VERCEL_TOKEN"` (first run links/creates the project named after the repo).
2. Env vars from `.env.example`: `npx vercel env add <NAME> production --token "$VERCEL_TOKEN"` fed from the local env — never typed.
3. `npx vercel build --prod --token "$VERCEL_TOKEN"` — **local build**.
4. `npx vercel deploy --prebuilt --prod --yes --token "$VERCEL_TOKEN"` — uploads output only; no Vercel build minutes. Never plain `vercel --prod`.
5. `live_url` = the printed production URL.

## Health check
`curl -s -o /dev/null -w "%{http_code}" <live_url>` → 200.

## Custom domain
Vercel dashboard → Project → Settings → Domains → Add. It shows the DNS record (CNAME `cname.vercel-dns.com` or A `76.76.21.21`). The user adds it at the registrar; Claude pre-fills the domain field in the dashboard and stops before Save.
