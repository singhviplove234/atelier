# Target: desktop-release

## Fits
Installed desktop apps for Windows, macOS and Linux, distributed as installers attached to a release on the project's own code host. Not a web host. Read `references/product-types.md` ("Desktop app") first: code signing certificates and Apple's developer programme are paid and belong to the owner — read the current prices on their pages; an unsigned build is for testers only and shows security warnings. A macOS build needs a Mac.

## Env vars
Required: none beyond the code host's command-line login already used by the factory (`gh auth status` succeeds)
Optional: none. Signing identities live in the operating system's own certificate store or keychain on the build machine, put there by the owner — never as env vars, never typed by Claude.
Checks: `gh auth status` succeeds; the shell's build tool prints its version (`npx tauri --version` or `npx electron-builder --version`); for a signed build, the platform's signing tool lists the owner's identity

## Preview
A **draft pre-release**: installers built locally and attached to a draft release that only collaborators can see. The e2e suite runs against the built app (or the web layer plus a packaged-app smoke test, `product-types.md`). `preview_url` = the draft release URL.

## Deploy steps
1. Build the installer locally on each operating system being released: one build per system, on that system. Sign and (on macOS) notarize only when the owner has installed their identity; otherwise mark the release notes "unsigned — testers only".
2. Write `SHA256SUMS.txt` for every installer.
3. `gh release create v<version> --draft --title "<name> <version>" --notes-file CHANGELOG-<version>.md <installers> SHA256SUMS.txt`
4. If the app updates itself, add the signed update manifest to the same draft.
5. **Stop.** `live_url` = the release page. Publishing the draft is the owner's click — never run a command that releases to production.

## Health check
`gh release view v<version> --json assets` lists every installer and the checksum file with non-zero sizes; a downloaded installer's hash matches `SHA256SUMS.txt`; the installed app prints the right `--version`. Record `http_status: n/a`.

## Custom domain
Not applicable. The download page lives on the product's website, deployed through a web target, and links to the published release.
