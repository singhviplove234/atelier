# Target: flutter-stores

## Fits
Mobile apps built with Flutter, released to Google Play and the Apple App Store with `fastlane`. Not a web host. Read `references/mobile-release.md` first: the store developer accounts carry fees and are the owner's; a public release is always the owner's click. The same lanes release a fully native app (Gradle / Xcode builds in place of the `flutter build` lines). **iOS needs a Mac:** an iOS binary cannot be built on Windows or Linux — it is built on a Mac the owner has, or on a cloud builder's macOS machine inside its free allowance (the allowed remote-build exception; check the current allowance on the provider's pricing page, and ask before anything bills).

## Env vars
Required (Android): `ANDROID_KEYSTORE_PATH`, `ANDROID_KEYSTORE_PASSWORD`, `ANDROID_KEY_ALIAS`, `ANDROID_KEY_PASSWORD` (the upload keystore is created and kept by the owner — never committed), `PLAY_JSON_KEY_PATH` (path to the Play service-account key file)
Optional: `APP_STORE_CONNECT_API_KEY_PATH` (path to the App Store Connect API key file — needed only for the iOS step, on the Mac or cloud builder; its absence skips iOS, it does not fail the Android release)
Checks: `flutter --version` runs; `flutter doctor` shows the Android toolchain ready; `fastlane --version` runs

## Preview
The store test tracks are the preview. Android: `flutter build apk --release` produces an installable build for the team's own devices. `preview_url` = empty (there is no URL; record the artifact path in `notes:`).

## Deploy steps
1. Android: `flutter build appbundle --release` (local build, signed with the owner's upload keystore through the env vars above).
2. Android upload: `fastlane supply --aab build/app/outputs/bundle/release/app-release.aab --track internal --json_key "$PLAY_JSON_KEY_PATH"` → the Play **internal testing** track. The very first upload of a new app must be done by the owner in the Play Console; fastlane can upload from the second one on.
3. iOS (on macOS only): `flutter build ipa --release`, then `fastlane pilot upload --ipa build/ios/ipa/*.ipa --api_key_path "$APP_STORE_CONNECT_API_KEY_PATH"` → **TestFlight**. If this machine is not a Mac and no cloud builder is set up, stop with `notes: iOS build needs macOS — Android shipped to internal testing; iOS pending` rather than failing the Android release.
4. **Stop.** `live_url` = the Play internal-testing / TestFlight link. Promotion to review and production is the owner's click in Play Console / App Store Connect — never run a command that releases to production.

## Health check
The upload commands exit 0 and the build appears on the test track. (There is no HTTP 200 for a store build; record `http_status: n/a`.)

## Custom domain
Not applicable. The app's privacy-policy and support URLs point at the product's website, deployed through a web target.
