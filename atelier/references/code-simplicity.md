# Code simplicity & handoff contract — the code a human inherits must be the simplest correct version

Standing requirement: whatever the language, the code must be simple — no unnecessary or duplicated lines, the 2-line way chosen over the 10-line way when they do the same thing — and easy for a human to pick up and keep building after the AI version. If the factory can't build something cleanly itself, it looks for a maintained library, package or skill that does the job rather than hand-rolling it. This never lowers quality and never picks a worse language, framework or approach just to be shorter: simplest **correct** version, not shortest at any cost.

## The rule the builder applies to every file it writes

1. **Fewest lines that stay clear.** If the same result is correct, as readable, and as safe in fewer lines, write the fewer. Use the language's own idioms and standard library (comprehensions, built-ins, map/filter, destructuring, LINQ, stream APIs) instead of long manual equivalents — but never a dense one-liner that a human has to decode. Clarity wins ties, not brevity.
2. **Don't reinvent — reuse.** Before hand-writing non-trivial logic (date math, validation, parsing, auth, HTTP, retries, slugging, currency, PDF, CSV), use a well-known, maintained, appropriately-licensed library or an available skill. Prefer the framework's built-in over a dependency, and a small focused dependency over a large one. If a good library or repo exists, use it and name it; if none fits, write the minimal version. (Record the choice so the human knows why the dependency is there.)
3. **No dead or speculative code.** No unused variables, imports, parameters, files or dependencies; no commented-out blocks; no "might need it later" abstractions, options or config for things the spec doesn't ask for. Build exactly what the SPEC needs. Delete scaffolding the generator leaves behind.
4. **DRY, lightly.** Factor out logic duplicated three+ times into one named helper; do **not** over-abstract two similar lines into a framework. A little repetition beats a wrong abstraction.
5. **Small, named, single-purpose units.** Short functions that do one thing with a name that says what; descriptive variable names over comments; early returns over deep nesting. Comments explain **why** (a non-obvious decision), never restate **what** the code already says.
6. **Boring and consistent.** Match the project's existing patterns and the language's standard style/formatter (Prettier, gofmt, black, rustfmt). No clever metaprogramming, no custom DSLs, no premature performance tricks. The human should recognise ordinary, idiomatic code.
7. **Handoff-ready.** A short README: what it is, how to run it, the main folders, and any non-obvious decision in one place. `.env.example` lists the env vars. Names and structure make the entry points obvious. Nothing a new developer has to reverse-engineer to start.

## The hard limit (quality first — simplicity never overrides these)

Never shorten in a way that removes input validation, error handling, security controls (`security.md`), accessibility, or needed tests; never collapse logic into something unreadable to save lines; never pick a weaker language, framework, type-looseness (`any`, untyped), or architecture just because it's fewer lines. If "simpler" and "correct/secure/right tool" conflict, correct wins and the code stays as long as it must — the goal is the simplest version that is still right, maintainable and the best choice going forward.

## How it is checked (build step 6; a `simplicity` review in `/pf-harden`)

Using existing tooling, no bespoke scanners:
- **Lint with complexity on:** ESLint (`complexity`, `max-depth`, `max-lines-per-function` as warnings), or the language equivalent (golangci-lint, ruff, clippy). Clean before ok.
- **Unused code/deps:** `knip` or `ts-prune` for unused exports/files, `depcheck` for unused dependencies, the compiler's unused-import/var errors on. Zero unused.
- **Duplication:** `jscpd` (or language equivalent) over the source; investigate any clone above the threshold and factor or justify it.
- **Formatter:** the project formatter reports no diff.
- **Dependency sanity:** each added dependency is maintained and actually used; a one-use trivial helper is inlined rather than pulled from a package.
- **Human-handoff self-review:** the builder re-reads each file it wrote and asks, per file, "could a mid-level developer in this language read this top-to-bottom and know what it does, and is any part longer than it needs to be?" — and simplifies what fails, without crossing the hard limit above.

Report a short table in `notes:`: file | lines | longest function | unused found | duplication % | simplified? — before and after any simplification.
