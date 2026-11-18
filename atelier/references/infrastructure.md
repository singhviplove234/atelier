# Infrastructure as code — when the cloud setup is more than one command

Added in 0.4.0. A static site on a free host needs no infrastructure code: the target file's few CLI steps *are* the setup, and adding more would only be weight (`code-simplicity.md`). But once a product is several cloud resources wired together — a container app, a database server, a queue, storage, a vault, networking — clicking or typing them by hand cannot be reviewed, repeated or handed over. Then the infrastructure is written down as code, in the repo.

## A. When it applies — `factory.json.infra` (decided at plan time)
| Value | When | Tool |
|---|---|---|
| `none` (default) | static and single-service setups: `github-pages`, `cloudflare-pages`, `netlify`, `vercel`, `azure-static-web-apps`, `aws-amplify`, `render`, `fly-io`, a lone `azure-container-apps` or `gcp-cloud-run` service, and the store targets `expo-eas` / `flutter-stores` — with or without a managed database such as Supabase | the target file's steps |
| `bicep` | Azure with more than one resource (`azure-container-apps` plus anything else) | Bicep |
| `opentofu` | AWS, GCP or a multi-cloud setup with more than one resource | OpenTofu (the open-source Terraform — free, same language) |
| `compose` | a self-hosted box (`oracle`) | a `docker-compose.yml` plus the Caddy config |
Required (not optional) whenever the project has cloud resources of its own beyond that first row **and** is `data_sensitivity: high`, has more than three such resources, or will be delivered to a client — a client cannot own what exists only as click history. A project that fits the first row stays `none` whatever its sensitivity: there is nothing to codify.

## B. How it is written
0. **The code is the SPEC's `app-architecture` diagram, made real.** Every resource in `infra/` appears in that diagram and every box in the diagram that is a cloud resource appears in `infra/`; a resource in neither is not created.
1. Everything lives in `infra/` in the product repo, with one short `infra/README.md`: what each resource is for, what it costs, how to preview and apply.
2. **No secret in the code or in its state.** Secrets are references (a Key Vault / secret-manager entry, an environment value supplied at apply time) — names only (`security.md`). OpenTofu state holds real values, so it lives in a private remote backend with locking (the cloud's own storage — free or a few cents a month at this size, stated in the budget), **never in the repo**; Bicep keeps no state file.
3. **Least privilege and the free tier by default.** Every resource is the smallest/free SKU that meets the SPEC, scale-to-zero where it exists; identities get only the roles they need; nothing public that does not have to be. Every resource carries tags `project=<slug>` and `managed-by=iac`.
4. **Small and flat.** One file per concern, no home-made module framework, no resource the SPEC does not need.

## C. How it is checked (part of `verify`, `verification.md`)
The tool's own build and lint (`bicep build` + linter, or `tofu validate` + `tflint`), plus a free misconfiguration scan (`checkov` or `trivy config`) with no High finding; and a test that the compiled template contains no literal secret and no paid SKU the plan did not approve.

## D. How it is applied — at deploy only, previewed first
- **Preview stage:** run the tool's dry run (`az deployment group what-if`, `tofu plan`) and put its summary in the result: resources to create / change / **delete**, and any that bill.
- **Go-live question:** `/pf-deploy` shows that summary. Anything that would be **deleted or replaced**, and anything **billable**, is named in plain words and needs its own yes — exactly like a destructive migration (`migrations.md` D).
- **`infra/` replaces the target file's resource-creation steps.** When it exists, the deployer does not run the target's create commands (`az containerapp up`, `gcloud run deploy` creating a service, and the like) — the resources come from the code; the target file's steps are used only to build, push and roll out the app version, and for its health check.
- **Live stage:** apply, then migrations, then the app. A failed apply stops the deploy; the previous version stays live.
- **Never automated:** `destroy`, deleting a resource group, or any apply on a schedule.
- **Drift:** `/pf-maintain` runs the dry run on each pass; a difference between the code and what is live is reported, not auto-corrected.

## E. Result lines
`infra: <tool>, <n> resources, lint clean` on a build; `infra_plan: +<a> ~<c> -<d>, billable: <list or none>` on a deploy.
