# Target: expo-eas

## Fits
Mobile apps built with React Native + Expo, released to the Apple App Store and Google Play through Expo Application Services (EAS). Not a web host. Read `references/mobile-release.md` first: the store developer accounts carry fees and are the owner's; a public release is always the owner's click. EAS has a monthly free build allowance — check the current number on Expo's pricing page; anything beyond it asks first.

## Env vars
Required: `EXPO_TOKEN` (an Expo access token for non-interactive builds)
Optional: none for the build. Store credentials (the Apple API key, the Google Play service-account key) are added by the owner to EAS's own credential store with `eas credentials` — never as env vars, never typed by Claude.
Checks: `npx eas-cli --version` runs; `npx eas-cli whoami` succeeds

## Preview
The store test tracks are the preview. `npx eas-cli build --platform all --profile preview --non-interactive` produces installable internal builds (Android APK; iOS ad-hoc for registered devices). `preview_url` = the build page URL EAS prints.

## Deploy steps
1. `npx eas-cli build --platform <ios|android|all> --profile production --non-interactive` — Android may build locally with `--local` on macOS, Linux or WSL; iOS from Windows uses the EAS cloud builder (the allowed remote-build exception, `mobile-release.md` A).
2. `npx eas-cli submit --platform ios --latest --non-interactive` → uploads to App Store Connect, where it appears in **TestFlight**. `npx eas-cli submit --platform android --latest --non-interactive` → uploads to the Play **internal testing** track (the very first Android upload must be done by the owner in the Play Console; EAS can submit from the second one on).
3. **Stop.** `live_url` = the TestFlight / Play testing link. Promotion to review and production is the owner's click in App Store Connect / Play Console — never run a command that releases to production.

## Health check
`npx eas-cli build:view --json` on the submitted build reports `finished`, and the submission reports success. (There is no HTTP 200 for a store build; record `http_status: n/a`.)

## Custom domain
Not applicable. The app's privacy-policy and support URLs point at the product's website, deployed through a web target.
