# Verification — the gates travel with the repo

Added in 0.3.0 (18 Nov 2026). a product the factory builds must be checkable by **anyone, on any machine, without the factory** — a client's developer, a new lane, a maintenance run. Until now the gates lived in the builder's session: the moment a human pushed a change, nothing re-ran them. This contract puts the correctness and safety gates **in the repo itself**, as one command, wired to run before every push. Stack-neutral, free, and it replaces nothing: performance, SEO and design stay measured by the build, `/pf-harden` and `/pf-maintain` (they need a running site and a browser lab); this is the part that must hold on every commit.

## A. One command: `verify`
Every repo has a single entry point — `npm run verify` on a Node stack; the same name through the stack's own runner elsewhere (`make verify`, `just verify`, a `scripts/verify` file). It runs, in this order, and stops at the first failure with a non-zero exit:
1. **lint** (with the complexity rules from `code-simplicity.md`) and the formatter in check mode;
2. **types** (`tsc --noEmit`, or the stack's type checker) — skipped only where the language has none;
3. **build** — the production build;
4. **tests** — unit tests plus the access-isolation tests from `security.md` section B;
5. **end-to-end** — section B below;
6. **dependency audit** at high severity (`npm audit --audit-level=high` or the stack's equivalent);
7. **secret scan** of the working tree and the commits being pushed (`gitleaks`).
The end-to-end step is also runnable on its own — `npm run e2e` (or the stack's equivalent) — which is what the deploy stage calls against a preview. It needs no production secret: only the test environment (`.env.example` names, test database, test user). A step that cannot run because a tool is missing **fails** with the install line — it never skips silently. The builder's own verify step (`pf-build-from-spec` §6) runs this same command, so "what the builder checked" and "what anyone can re-run" are the same thing.

## B. End-to-end tests come from the diagrams
Every page and feature is already diagrammed before it is built (`spec-format.md` `## Diagrams`), and a flow diagram is a test plan. So:
- **One test file per diagram** — `e2e/<id>.spec.ts` (Playwright on a web stack; the stack's standard e2e runner otherwise) for every `page-<slug>` and `feature-<slug>` id. The file's first line names its source: `// diagram: <id>`. `app-architecture` and `app-journey` get no file of their own; `app-journey` is covered by one `e2e/app-journey.spec.ts` that walks the primary journey start to finish.
- **A `page-` test** follows the arrows: arrive the way the diagram says, do each action a user can do, land where each one leads. Assert on the verbatim `Copy:` from the SPEC, never on CSS classes.
- **A `feature-` test** follows the sequence, **and its failure path** — the diagram is required to draw one, so the test is required to take it (bad input rejected, signed-out request refused, another user's row not readable).
- **Coverage is exact, both ways.** A `page-`/`feature-` id with no test file fails `verify`; a test file whose `// diagram:` id is no longer in the SPEC is deleted, exactly as the rendered diagram is. The folder always equals the SPEC.
- **Where it runs.** Against the local production build by default; against any deployment by setting `E2E_BASE_URL` (the deploy stage does this for the preview — `deploy-rule.md` "Preview first"). Tests that write data use the **test** database only (`migrations.md` A) and clean up after themselves; they never run against production data.
- **Budget.** Headless, one browser (Chromium) by default, the whole suite under ~5 minutes on a small app; a second engine (WebKit/Firefox) is added only when the Brief names those users. E2E does not re-test what a unit test already proves.

## C. Wired to run before every push — free, no CI minutes
- **Pre-push hook, always.** The repo carries `.githooks/pre-push`, which runs `verify`; the builder sets `git config core.hooksPath .githooks` in its checkout, and the README's first setup line tells any other clone to do the same (a hooks path is local config — it is not cloned). This is the default gate: it costs nothing, needs no runner, and stops a broken push at the source. A hook can be bypassed with `--no-verify`; that is why B and D exist for projects where it matters.
- **Recorded proof.** The build result carries `verify: pass (<n> e2e, <m> unit)`; a failed `verify` is a failed build.

## D. CI mode — `factory.json.ci` (set at plan or setup; default `hook`)
| Mode | What the builder writes | When |
|---|---|---|
| `hook` | the pre-push hook only | default — solo and low-stakes projects |
| `self-hosted` | hook **and** `.github/workflows/verify.yml` with `runs-on: self-hosted`, on `pull_request` and pushes to `main` | team projects and every `data_sensitivity: high` project, once a runner is registered (`/pf-setup ci`) — $0 on your own hardware (`cost-posture.md`) |
| `hosted` | hook **and** the same workflow with `runs-on: ubuntu-latest` | public repos (free), or a private repo on an explicit yes to spend the monthly free allowance (`cost-posture.md`) |
The workflow does exactly one thing: check out, install, run `verify`. It never deploys and never holds a production secret — deploys stay local-build (`deploy-rule.md`). A `self-hosted` workflow is never written before a runner exists (a workflow with no runner leaves every PR "pending" forever). When a workflow exists, `/pf-setup ci` walks the user through requiring the `verify` check on `main` (branch protection is a repo setting: Claude opens the page, he clicks).

## E. Checks (the builder's gate)
`verify` exists and exits 0 on a clean checkout; every `page-`/`feature-` id has its `e2e/<id>.spec.*` and no orphan test exists; every `feature-` test contains its failure path; `.githooks/pre-push` exists and is executable and `core.hooksPath` is set; the workflow file matches `ci` (absent for `hook`). Any miss → fix, up to 3 attempts, then `status: failed`, `failures: verify: <check>`.
