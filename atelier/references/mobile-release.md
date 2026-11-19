# Mobile release — getting an app into the stores

The factory plans, designs and builds mobile apps (`design-standard.md` "Mobile apps"), so it must also say truthfully how one ships — and never let "build me an app" quietly end at a build. A store release is not a web deploy: it has fees no free tier removes, a review by a third party, and a publish step that cannot be undone. This file is what `/pf-plan` tells the user up front and what `/pf-deploy` follows through the `expo-eas` target.

## A. Said at plan time, before the stack is locked
- **Fees that cannot be avoided** (the one standing exception to zero recurring fees — stated with the price, on a yes): the Apple Developer Program (yearly) for the App Store, and a Google Play developer account (one-time). Read the current prices from Apple's and Google's own pages at plan time; never quote from memory.
- **The accounts are the owner's.** The developer accounts are created by the user or the client in their own name (Apple requires the legal entity that publishes the app); the factory never creates one and never holds its password.
- **Time is not ours.** Each store reviews every release; allow days, not minutes. A new **personal** Google Play account must first run a closed test with a minimum number of testers for a set number of days before production access (currently 12 testers for 14 days — confirm on Google's page). The plan's timeline carries this.
- **iOS builds need Apple hardware or a cloud builder.** From a Windows machine an iOS binary can only be produced by a cloud build service; this is the one case where a remote build is allowed (`deploy-rule.md`), inside its free allowance, and anything billable asks first.
- **Supported paths:** React Native with **Expo**, released through **EAS** (`targets/expo-eas.md`); **Flutter** — and fully native apps through the same lanes — released with `fastlane` (`targets/flutter-stores.md`). Android builds and uploads run from any machine; an iOS build needs a Mac or a cloud macOS builder, and the plan says which the project has **before** the stack is locked — an iOS release with neither is a known gap stated up front, not discovered at ship time.
- **Often the better answer:** if the product needs no device API a browser lacks, a responsive web app (installable as a PWA) ships today on a free host with no store, no fee and no review. `/pf-plan` offers that comparison in one line before a store app is chosen.

## B. What the build adds for a mobile app
Bundle identifiers and app name from the Brief; icons and splash from the design tokens; the permission strings for every device capability the SPEC uses (and none it does not); a privacy policy URL and the store data-safety answers drafted from `compliance.md` (the owner confirms them — the factory never asserts them); `verify` runs lint, types, unit tests and the stack's e2e runner on an emulator/simulator where one is available on the build machine, and says plainly in the result which platforms were not exercised.

## C. Release stages (each is a gate)
1. **Internal build** — install on real devices of the team. No store involved.
2. **Store test track** — TestFlight (iOS) / internal or closed testing (Android). This is the mobile equivalent of the web preview: `/pf-deploy` stops here by default.
3. **Submit for review → public release** — **the owner's click, always.** `/pf-deploy` prepares the listing (name, description, screenshots from the design, the answers above), then stops and says "Your turn: check it and click Submit for review." It never submits, never releases to production, and never changes pricing or availability.
After release: updates follow the same three stages; a JavaScript-only fix may go out as an over-the-air update only where both stores' rules allow it and the change needs no new permission.

## Never
- Create a developer account, accept a store agreement, or type a store password or app-specific password.
- Submit for review or release to production on the user's behalf.
- Quote a fee, a review time or a store rule from memory as current — read the store's page at plan time.
