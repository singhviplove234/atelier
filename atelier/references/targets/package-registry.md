# Target: package-registry

## Fits
Command-line tools and libraries that other people install from a public package registry (npm for JavaScript and TypeScript, PyPI for Python). Not a web host. Read `references/product-types.md` ("Command-line tool or library") first. A published version can never be changed and a name can rarely be taken back, so publishing is always the owner's action.

## Env vars
Required: none for building and testing
Optional: none. Publishing uses the owner's own registry login with two-factor confirmation, or the registry's trusted-publisher link to the repository — never a long-lived token typed or stored by Claude.
Checks: `npm view <name> version` (or the registry's page) shows the name is free or already the owner's, and the new version is higher; `npm pack --dry-run` lists a licence file and only the intended files; the package declares no install-time script

## Preview
The packed file is the preview. `npm pack` (or `python -m build`) produces exactly what would be published; install that file into an empty temporary folder and run the e2e suite against the installed tool. `preview_url` = the path of the packed file. A pre-release under the `next` tag is the owner's choice, not a default.

## Deploy steps
1. Build and pack locally; list the files in the pack and confirm nothing private is inside (no `.env`, no test data with real names, no source maps that were not intended).
2. Run the e2e suite against the packed file installed in a clean folder.
3. Tag the commit `v<version>` and update the changelog.
4. **Stop.** Hand the owner the one line to run — `npm publish` (or `python -m twine upload dist/*`) — or, when a trusted publisher is configured, the release they create to trigger it. Never run a command that releases to production.

## Health check
After the owner publishes: `npm view <name>@<version> version` (or the registry's JSON page for that version) returns the version, and a fresh install in an empty folder runs `--version` correctly. Record `http_status: n/a`.

## Custom domain
Not applicable. Documentation, if it has its own site, is deployed through a web target.
