# Target: chrome-web-store

## Fits
Browser extensions (Manifest V3) for Chrome, and for Edge and other Chromium browsers that install from the same store. Not a web host. Read `references/product-types.md` ("Browser extension") first. The developer account and its one-time registration fee are the owner's — read the current fee on the store's page. Every release is reviewed by the store and can be rejected; a public release is always the owner's click. Firefox and Safari have their own stores and are not covered by this target.

## Env vars
Required: `CWS_EXTENSION_ID` (the item's ID, known after the owner's first upload)
Optional: `CWS_CLIENT_ID`, `CWS_CLIENT_SECRET`, `CWS_REFRESH_TOKEN` (the store's API credentials, created by the owner in their own developer console — only for uploading a draft from the command line; without them the owner uploads the zip in the dashboard)
Checks: `node -v` reports version 20 or newer; after a build, `dist/manifest.json` exists, its `manifest_version` is 3 and its `version` is higher than the last uploaded one

## Preview
The unpacked build is the preview. Build to `dist/`, load it in a Chromium persistent context and run the full e2e suite against it. For testers outside the machine, the store's *trusted testers* visibility is the preview channel — set by the owner in the dashboard. `preview_url` = the path of the built zip.

## Deploy steps
1. Build and zip locally: `npm run build`, then zip the contents of `dist/` (not the folder) to `release/<name>-<version>.zip`.
2. **First release:** stop. The owner creates the item in the developer dashboard, uploads this zip, fills in the listing, the privacy-policy URL and the data-use disclosure, and copies the item ID into `CWS_EXTENSION_ID`.
3. **Later releases, when the API credentials are set:** upload the zip as a **draft** with the store's publish API or its command-line uploader (run it with `--help` first and use the flags it lists; never pass a flag that publishes).
4. **Stop.** `live_url` = the item's store URL. Submitting for review and publishing are the owner's clicks — never run a command that releases to production.

## Health check
The upload response reports success and the dashboard shows the new version as a draft. After the owner publishes and review passes: the store page shows the new version number. There is no HTTP 200 for a store item; record `http_status: n/a`.

## Custom domain
Not applicable. The extension's home page, privacy policy and support URLs point at the product's website, deployed through a web target.
