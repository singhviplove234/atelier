# Data safety — two databases and migrations that cannot lose data

Once a product holds real data, a build, a test or a preview must never be able to touch it, and a schema change must never be able to destroy it. Stack-neutral: the names below are the Supabase/Postgres defaults; another database uses its own equivalents and the same rules.

## A. Two databases once data is real
- **Test database** — what builds, tests, e2e, previews and restore drills use. Synthetic/seed data only. On the build machine it is the **unprefixed** env names (`SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_DB_URL`, `SUPABASE_SERVICE_ROLE_KEY`, or `DATABASE_URL`).
- **Production database** — what the live site uses, and nothing else. On the build machine it is the same names with a **`PROD_` prefix** (`PROD_SUPABASE_URL`, …); the live deploy feeds the host's env from the `PROD_` values (unprefixed on the host), and is the only step that ever connects to it.
- **When the split is required.** A `data_sensitivity: high` project: from the first build. Every other project with a Data model: from the first build **after** go-live. Before go-live a single database is fine — it holds only seed data, and at the first live deploy it becomes production. From then on a build that would apply a migration or seed refuses until the split exists: `failures: project is live on a single database — run /pf-setup database to split test from production`. `/pf-setup database` does the split with the user (the current values become `PROD_…`; a new free project becomes the unprefixed test database). Recorded as `factory.json.database: single|split` — names only, never a value.
- **Free-first.** A second free-tier database project costs nothing; a paid tier is never the reason for a split.

## B. How a migration is written
1. **Forward-only and immutable.** One timestamped file per change; a migration that has been applied anywhere is never edited or deleted — a fix is a new migration.
2. **Expand, then contract — required, not preferred.** A change that removes or narrows something (drop a column or table, rename, tighten a type, add `NOT NULL` without a default) is split across **two releases**: release 1 *expands* (add the new column/table, write to both, backfill); release 2 *contracts* (remove the old one), and only after release 1 is live and healthy. So the previous app version always runs against the new schema, and auto-rollback of the app (`deploy-rule.md`) is always safe.
3. **Destructive migrations are labelled.** Any migration containing `DROP`, `TRUNCATE`, `DELETE` without a key, `ALTER … TYPE`, or a rename starts with `-- destructive: <what and why>`. An unlabelled destructive statement fails the gate.
4. **Idempotent and bounded.** `IF NOT EXISTS` / `IF EXISTS` where the engine allows; indexes built without locking writes (`CONCURRENTLY`); a backfill over a large table runs in batches, not one transaction.
5. **Access rules ship with the table.** A new table's row-level policy is in the same migration (`security.md` A) — never a release behind.

## C. How a migration is tested (the builder's gate)
On the **test** database, every build that adds a migration: (1) apply all migrations from empty — must succeed; (2) apply only the new ones on top of the schema as of `main` — must succeed; (3) run the previous release's e2e suite against the new schema when a previous release exists (`git stash`/worktree of the last `live-` tag) — proves the expand step is backward-compatible; (4) scan for unlabelled destructive statements. Any miss → `status: failed`, `failures: migrations: <check>`. The result carries `migrations: <n> new, <k> destructive`.

## D. How a migration reaches production (deploy only, never build)
- Pending migrations are applied by the **live deploy**, to the production database, **before** the app is switched — never by a build, a preview or a test.
- **Backup first.** Before applying, take (or confirm, within the last hour) a backup per `maintenance.md` C; no backup → no migration.
- **A destructive migration needs its own yes.** `/pf-deploy` lists every `-- destructive:` line in the go-live question; without a clear yes to that line the deploy stops. It is never covered by a standing or scheduled approval.
- **Failure.** A migration that fails is not retried and not auto-reverted: the app switch does not happen, the previous version stays live, and the result carries `needs_decision: migration <name> failed at <statement>` for the user. The database is never rolled back automatically (`monitoring.md` D).
