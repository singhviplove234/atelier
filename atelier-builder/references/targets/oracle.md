# Target: oracle

## Fits
An always-on box / self-hosted **open-source** stack on **Oracle Cloud Always Free** (ARM Ampere, up to ~24GB — verify current terms; ARM capacity is scarce). Best when the project wants to own the stack, run open-source (Docker Compose behind Caddy/Coolify), avoid per-service free-tier limits, or needs a persistent server at **$0**. For a simple static site a free static host is simpler.

## Env vars
Required: SSH access to the Always-Free VM — `ORACLE_VM_HOST` (user@ip); the key lives in the local SSH agent, never in the repo
Optional: `SUPABASE_URL`/`SUPABASE_ANON_KEY`, or a self-hosted Postgres on the box
Checks: `ssh "$ORACLE_VM_HOST" 'docker --version'` runs

## Deploy steps
1. Build **locally** (container image or static output): `docker build -t <slug>:<tag> .` — never a remote/paid build.
2. Ship the image to the VM: `docker save <slug>:<tag> | ssh "$ORACLE_VM_HOST" 'docker load'` (or push to a free registry and pull on the VM).
3. On the VM: `docker compose up -d` — the app plus **Caddy** as a reverse proxy that issues HTTPS automatically via Let's Encrypt.
4. `live_url` = `https://<domain-or-vm-ip>`.

## Health check
`curl -s -o /dev/null -w "%{http_code}" <live_url>/api/health` → 200.

## Custom domain
Point the domain's A record at the VM's public IP at the registrar; Caddy issues the certificate automatically on first request. The user adds the DNS record; Claude gives the exact record and stops.
