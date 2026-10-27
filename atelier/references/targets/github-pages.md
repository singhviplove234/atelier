# Target: github-pages

## Fits
Pure static sites only (no API routes, no forms needing a server). Free via `gh`. Requires a **public** repo on a free GitHub account — the builder creates repos private, so pick this only when the project may be public (the deploy step will offer to flip visibility).

## Env vars
Required: (none)
Optional: —
Checks: `gh auth status` succeeds

## Deploy steps
1. **Local build** to static: `next build` with `output: 'export'` and `basePath: '/<slug>'` in `next.config` → `./out`. Commit the config change before deploying so the tree stays clean.
2. Push `./out` to branch `gh-pages`: `npx gh-pages -d out` (or `git subtree push`).
3. `gh api -X POST repos/<owner>/<slug>/pages -f source[branch]=gh-pages -f source[path]=/` (first run).
4. `live_url` = `https://<owner>.github.io/<slug>/`.

## Health check
`curl` the live URL → 200 (may take a minute on first publish).

## Custom domain
Add a `CNAME` file with the domain to `./out`, set the DNS records GitHub documents, then `gh api -X PUT repos/<owner>/<slug>/pages -f cname=<domain>`. Claude prepares; The user confirms.
