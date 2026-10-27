#!/usr/bin/env bash
# Structural validator for the atelier plugins. Reports every failure; exits non-zero if any.
set -u
cd "$(dirname "$0")/.."
fail=0
ok(){ echo "PASS $1"; }
bad(){ echo "FAIL $1"; fail=1; }
need_file(){ [ -f "$1" ] && ok "$1 exists" || bad "$1 missing"; }
need_grep(){ grep -qE "$2" "$1" 2>/dev/null && ok "$1 contains /$2/" || bad "$1 lacks /$2/"; }
json_ok(){ python3 -I -c "import json,sys;json.load(open(sys.argv[1]))" "$1" 2>/dev/null && ok "$1 valid JSON" || bad "$1 invalid JSON"; }

# --- Task 2: Cowork plugin scaffold
P=atelier
need_file $P/.claude-plugin/plugin.json; json_ok $P/.claude-plugin/plugin.json
need_grep $P/.claude-plugin/plugin.json '"name": *"atelier"'
need_file $P/README.md
for r in state-schema spec-format bridge deploy-rule; do need_file $P/references/$r.md; done
need_grep $P/references/state-schema.md '"gates"'
need_grep $P/references/state-schema.md '"code_path"'
for h in "## Brief" "## Stack" "## Screens" "## Tokens" "## Components" "## Data model" "## Routes / API" "## Acceptance checks"; do need_grep $P/references/spec-format.md "^$h"; done
for m in "PF-BUILD v1" "PF-BUILD-RESULT v1" "PF-DEPLOY v1" "PF-DEPLOY-RESULT v1"; do need_grep $P/references/bridge.md "$m"; done
need_grep $P/references/bridge.md 'mode: continue'
need_grep $P/references/deploy-rule.md 'vercel'; need_grep $P/references/deploy-rule.md 'azure-container-apps'
need_grep $P/references/targets/vercel.md 'VERCEL_TOKEN'


# --- Tasks 3-5: skills (checked when present; required once STAGE>=3)
STAGE=${STAGE:-13}
check_skill(){ # name stage
  [ "$STAGE" -ge "$2" ] || return 0
  local f=$P/skills/$1/SKILL.md
  need_file $f
  need_grep $f "^name: $1$"
  need_grep $f '^description: '
  need_grep $f 'factory.json'
  need_grep $f 'gates'
  need_grep $f 'AskUserQuestion'
  [ "$(wc -w < $f 2>/dev/null || echo 0)" -lt 3000 ] && ok "$f under 3000 words" || bad "$f over 3000 words"
  need_file $P/tests/$1.md
}
check_skill pf-design 3
[ "$STAGE" -ge 3 ] && { need_file $P/skills/pf-design/references/brief-template.md; need_grep $P/skills/pf-design/SKILL.md 'pf-design-system'; need_grep $P/skills/pf-design/SKILL.md 'kebab'; need_grep $P/skills/pf-design/references/brief-template.md 'Next.js \+ Tailwind \+ shadcn/ui'; }
check_skill pf-build 4
[ "$STAGE" -ge 4 ] && { need_grep $P/skills/pf-build/SKILL.md 'dry-run'; need_grep $P/skills/pf-build/SKILL.md 'PF-BUILD-RESULT v1'; need_grep $P/skills/pf-build/SKILL.md 'mode: continue'; need_grep $P/skills/pf-build/SKILL.md '<code root>'; need_grep $P/skills/pf-build/SKILL.md 'eight headings'; }
check_skill pf-deploy 5
[ "$STAGE" -ge 5 ] && { need_grep $P/skills/pf-deploy/SKILL.md 'PF-DEPLOY-RESULT v1'; need_grep $P/skills/pf-deploy/SKILL.md '[Dd]eploy now'; need_grep $P/skills/pf-deploy/SKILL.md '200'; need_grep $P/skills/pf-deploy/SKILL.md '5 minutes'; need_grep $P/skills/pf-deploy/SKILL.md 'deploy-rule'; }

# --- Task 6: Claude Code builder plugin
if [ "$STAGE" -ge 6 ]; then
  B=atelier-builder
  need_file $B/.claude-plugin/plugin.json; json_ok $B/.claude-plugin/plugin.json
  need_grep $B/.claude-plugin/plugin.json '"name": *"atelier-builder"'
  need_file $B/README.md
  for s in pf-build-from-spec pf-deploy-from-spec; do need_file $B/skills/$s/SKILL.md; need_grep $B/skills/$s/SKILL.md "^name: $s$"; done
  need_grep $B/skills/pf-build-from-spec/SKILL.md 'PF-BUILD-RESULT v1'
  need_grep $B/skills/pf-build-from-spec/SKILL.md 'mode: continue'
  need_grep $B/skills/pf-build-from-spec/SKILL.md 'gh repo create'
  need_grep $B/skills/pf-build-from-spec/SKILL.md 'create-next-app'
  need_grep $B/skills/pf-deploy-from-spec/SKILL.md 'PF-DEPLOY-RESULT v1'
  need_grep $B/references/targets/vercel.md 'VERCEL_TOKEN'
  need_grep $B/skills/pf-deploy-from-spec/SKILL.md 'http_status'
  for f in landing app; do need_file $B/tests/fixtures/$f/SPEC.md; for h in "## Brief" "## Stack" "## Screens" "## Tokens" "## Components" "## Data model" "## Routes / API" "## Acceptance checks"; do need_grep $B/tests/fixtures/$f/SPEC.md "^$h"; done; done
  need_grep $B/tests/fixtures/app/SPEC.md 'notes'
  # secrets never appear as values anywhere in either plugin
  if grep -rEn '(sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{36}|eyJ[A-Za-z0-9_-]{30,}\.[A-Za-z0-9_-]{10,})' $P $B >/dev/null 2>&1; then bad "secret-looking value found"; else ok "no secret-looking values"; fi
fi


# --- Final review fix pass (C1, I1–I6, safety)
if [ "$STAGE" -ge 7 ]; then
  BB=atelier-builder/skills/pf-build-from-spec/SKILL.md; BD=atelier-builder/skills/pf-deploy-from-spec/SKILL.md
  need_grep $BB 'gh repo clone'                       # C1: decide by disk/remote, not flag
  need_grep $BB '\.git'                               # C1
  need_grep $P/skills/pf-build/SKILL.md 'non-empty `repo_url`'   # C1: never blank a good repo_url
  need_grep $P/references/bridge.md '^notes:'         # I1: notes in PF-BUILD shape
  need_grep $BB '## Stack'                            # I2
  need_grep $BB 'unsupported stack'                   # I2
  need_grep $BD 'gh repo clone'                       # I3
  need_grep $BB 'supabase db push'                    # I4
  need_grep $BB 'TEST_USER_EMAIL'                     # I4
  need_grep atelier-builder/README.md 'TEST_USER_EMAIL'
  need_grep $BB '@theme'                              # I5: Tailwind v4
  need_grep $P/skills/pf-build/SKILL.md 'continues rather than restart'  # I6
  need_grep $BB '[Mm]ask'                             # safety: mask secret values in replies
  need_grep $P/skills/pf-deploy/SKILL.md '[Mm]ask'
  need_grep $BD 'uncommitted'                         # safety: no auto-push
  need_grep $BD 'status: failed`, `notes: uncommitted'
fi

# --- Deferred minors pass
if [ "$STAGE" -ge 8 ]; then
  need_grep $P/references/deploy-rule.md 'any trigger'                       # precedence explicit
  need_grep $P/references/deploy-rule.md 'Stack, Data model, Routes'       # scan all three
  if grep -qE '`socket`' $P/references/deploy-rule.md; then bad "deploy-rule still has bare socket trigger"; else ok "no bare socket trigger"; fi
  need_grep $P/references/deploy-rule.md 'Supabase Edge Functions'            # false-trigger exclusion
  need_grep $P/references/state-schema.md 'Approval words'                    # shared yes-list
  need_grep $P/skills/pf-design/SKILL.md 'yes, but'                           # mixed reply = change request
  need_grep $P/skills/pf-build/SKILL.md 'Approval words'
  if grep -q "'ship it'" $P/skills/pf-deploy/SKILL.md; then bad "ship it still a pf-deploy trigger"; else ok "ship it removed from triggers"; fi
  need_grep $P/skills/pf-design/SKILL.md '\[a-z0-9\]'                        # slug charset
  need_grep $P/skills/pf-design/SKILL.md '100 characters'
  need_grep $P/skills/pf-design/SKILL.md 'slug is empty'
  need_grep $P/skills/pf-build/SKILL.md 'more than one project'               # ask which project
  need_grep $P/skills/pf-deploy/SKILL.md 'more than one project'
  need_grep atelier-builder/skills/pf-deploy-from-spec/SKILL.md 'gates.build'   # builder re-checks gate
  need_grep $P/references/state-schema.md '[Dd]eploy exception'                  # gate wording
  need_grep $P/references/state-schema.md 'creating a new project'
  need_grep $P/references/state-schema.md '"goal"'                            # brief.goal
  need_grep $P/skills/pf-design/references/brief-template.md 'Goal'
  need_grep atelier-builder/.claude-plugin/plugin.json 'RESULT'
  need_grep $P/skills/pf-deploy/SKILL.md 'Flags first'                    # dry-run before write
  need_grep $P/tests/pf-build.md 'validate-only'                              # reachable case 3
  need_grep $P/tests/pf-build.md 'fails.*re-run'                              # focus (c) case
  need_grep atelier-builder/tests/fixtures/landing/SPEC.md 'GET /contact'
  need_grep $P/skills/pf-build/SKILL.md 'Mode A'                              # default local path (event wake)
  need_grep $P/skills/pf-build/SKILL.md 'data_sensitivity'                    # cloud guardrail for data-sensitive projects
  # heading order check in spec-format and fixtures
  for f in $P/references/spec-format.md atelier-builder/tests/fixtures/landing/SPEC.md atelier-builder/tests/fixtures/app/SPEC.md; do
    order=$(grep -E '^## ' "$f" | head -8 | tr '\n' '|')
    [ "$order" = "## Brief|## Stack|## Screens|## Tokens|## Components|## Data model|## Routes / API|## Acceptance checks|" ] && ok "$f heading order" || bad "$f heading order: $order"
  done
fi

# --- File hand-off bridge (replaces peer messaging)
if [ "$STAGE" -ge 9 ]; then
  need_grep $P/references/bridge.md 'BUILD-REQUEST-<lane>.md'
  need_grep $P/references/bridge.md 'BUILD-RESULT-<lane>.md'
  need_grep $P/references/bridge.md 'DEPLOY-REQUEST.md'
  need_grep $P/references/bridge.md 'DEPLOY-RESULT.md'
  need_grep $P/references/bridge.md 'Chrome hand-off'
  if grep -q 'ListAgents' $P/skills/pf-build/SKILL.md; then bad "pf-build still uses ListAgents"; else ok "pf-build no ListAgents"; fi
  if grep -q 'ListAgents' $P/skills/pf-deploy/SKILL.md; then bad "pf-deploy still uses ListAgents"; else ok "pf-deploy no ListAgents"; fi
  need_grep $P/skills/pf-build/SKILL.md 'BUILD-REQUEST-<lane>.md'
  need_grep $P/skills/pf-build/SKILL.md 'BUILD-RESULT-<lane>.md'
  need_grep $P/skills/pf-build/SKILL.md 'pf-build --check'
  need_grep $P/skills/pf-deploy/SKILL.md 'DEPLOY-REQUEST.md'
  need_grep $P/skills/pf-deploy/SKILL.md 'DEPLOY-RESULT.md'
  need_grep $P/skills/pf-deploy/SKILL.md 'pf-deploy --check'
  need_grep atelier-builder/skills/pf-build-from-spec/SKILL.md 'BUILD-RESULT-<lane>.md'
  need_grep atelier-builder/skills/pf-build-from-spec/SKILL.md 'BUILD-REQUEST-<lane>.md'
  need_grep atelier-builder/skills/pf-deploy-from-spec/SKILL.md 'DEPLOY-RESULT.md'
  need_grep atelier-builder/skills/pf-deploy-from-spec/SKILL.md 'DEPLOY-REQUEST.md'
  need_grep $P/README.md 'Chrome'
  need_grep $P/tests/pf-build.md 'BUILD-RESULT-<lane>.md'
fi

# --- /pf-next + Cowork-side polling
if [ "$STAGE" -ge 10 ]; then
  need_file atelier-builder/skills/pf-next/SKILL.md
  need_grep atelier-builder/skills/pf-next/SKILL.md '^name: pf-next$'
  need_grep atelier-builder/skills/pf-next/SKILL.md 'BUILD-REQUEST-<lane>.md'
  need_grep atelier-builder/skills/pf-next/SKILL.md 'DEPLOY-REQUEST.md'
  need_grep atelier-builder/skills/pf-next/SKILL.md 'pending'
  need_grep atelier-builder/skills/pf-next/SKILL.md 'PF_WATCH_DIR'
  need_grep atelier-builder/skills/pf-next/SKILL.md 'confirm'
  need_grep $P/skills/pf-build/SKILL.md 'poll'
  need_grep $P/skills/pf-build/SKILL.md 'pf-next'
  need_grep $P/skills/pf-deploy/SKILL.md 'poll'
  need_grep $P/skills/pf-deploy/SKILL.md 'pf-next'
  need_grep $P/references/bridge.md 'pf-next'
  need_grep $P/README.md 'pf-next'
  need_grep atelier-builder/README.md 'pf-next'
  if [ -d atelier-builder/hooks ]; then bad "builder must not ship a hooks module"; else ok "builder ships no hooks module"; fi
fi
  need_grep atelier-builder/references/targets/vercel.md 'prebuilt'

# --- v2: lanes, PM, Chrome hand-off, target registry, /pf-setup
if [ "$STAGE" -ge 11 ]; then
  for t in vercel azure-static-web-apps azure-container-apps cloudflare-pages netlify github-pages aws-amplify gcp-cloud-run render fly-io oracle; do
    f=$P/references/targets/$t.md; need_file $f
    for h in "## Fits" "## Env vars" "## Deploy steps" "## Health check" "## Custom domain"; do need_grep $f "^$h"; done
  done
  need_grep $P/references/targets/azure-container-apps.md 'docker build'
  need_grep $P/references/targets/vercel.md 'prebuilt'
  need_grep $P/references/deploy-rule.md 'targets/'
  need_grep $P/references/deploy-rule.md 'deploy_hint'
  need_grep $P/references/state-schema.md '"lanes"'
  need_grep $P/references/state-schema.md '"code_url"'
  need_grep $P/references/state-schema.md 'requested'
  need_grep $P/references/bridge.md 'BUILD-REQUEST-<lane>.md'
  need_grep $P/references/bridge.md 'pf-next <slug> build --lane'
  need_grep $P/references/bridge.md 'tabs_context_mcp'
  need_grep $P/references/bridge.md 'fall back'
  for s in pf-lanes pf-merge pf-setup; do need_file $P/skills/$s/SKILL.md; need_grep $P/skills/$s/SKILL.md "^name: $s$"; need_file $P/tests/$s.md; done
  need_grep $P/skills/pf-setup/SKILL.md '[Nn]ever type'
  need_grep $P/skills/pf-setup/SKILL.md 'Remote Control'
  need_grep $P/skills/pf-setup/SKILL.md 'code_url'
  need_grep $P/skills/pf-build/SKILL.md 'lane <name>'
  need_grep $P/skills/pf-build/SKILL.md 'Chrome'
  need_grep $P/skills/pf-build/SKILL.md 'BUILD-REQUEST-'
  need_grep $P/skills/pf-deploy/SKILL.md 'targets/'
  need_grep $P/skills/pf-deploy/SKILL.md 'all lanes'
  need_grep $P/skills/pf-deploy/SKILL.md 'Chrome'
  need_grep $P/skills/pf-design/SKILL.md 'Lanes'
  need_grep atelier-builder/skills/pf-next/SKILL.md 'gh pr merge'
  need_grep atelier-builder/skills/pf-next/SKILL.md 'skip the confirm'
  need_grep atelier-builder/skills/pf-next/SKILL.md 'lane'
  need_grep atelier-builder/skills/pf-build-from-spec/SKILL.md 'lane/'
  need_grep atelier-builder/skills/pf-build-from-spec/SKILL.md 'gh pr create'
  need_grep atelier-builder/skills/pf-deploy-from-spec/SKILL.md 'targets/'
  need_grep $P/README.md 'PM'
  need_grep $P/README.md 'pf-setup'
fi


# --- v2.1: /pf-harden + performance budget + Azure zero-fee posture
if [ "$STAGE" -ge 13 ]; then
  for f in $P/references/performance-budget.md atelier-builder/references/performance-budget.md atelier-builder/references/deploy-rule.md; do need_file $f; done
  if diff -q $P/references/performance-budget.md atelier-builder/references/performance-budget.md >/dev/null; then ok "performance-budget mirrored"; else bad "performance-budget differs between plugins"; fi
  need_grep $P/references/performance-budget.md '>= 90'
  need_grep $P/references/performance-budget.md '2.5 s'
  need_grep $P/references/performance-budget.md '200 KB'
  need_grep $P/skills/pf-harden/SKILL.md '^name: pf-harden$'
  need_file $P/tests/pf-harden.md
  need_grep $P/skills/pf-harden/SKILL.md 'HARDEN-REQUEST.md'
  need_grep $P/skills/pf-harden/SKILL.md 'PF-HARDEN-RESULT v1'
  need_grep $P/skills/pf-harden/SKILL.md 'pf-next <slug> harden --go'
  need_grep $P/skills/pf-harden/SKILL.md 'dry-run'
  need_grep $P/skills/pf-harden/SKILL.md '[Nn]ever: load-test a live URL'
  need_grep atelier-builder/skills/pf-harden-from-spec/SKILL.md '^name: pf-harden-from-spec$'
  need_grep atelier-builder/skills/pf-harden-from-spec/SKILL.md 'PF-HARDEN v1'
  need_grep atelier-builder/skills/pf-harden-from-spec/SKILL.md 'k6'
  need_grep atelier-builder/skills/pf-harden-from-spec/SKILL.md 'CONCURRENTLY'
  need_grep atelier-builder/skills/pf-harden-from-spec/SKILL.md 'do \*\*not\*\* add Redis'
  need_grep atelier-builder/skills/pf-harden-from-spec/SKILL.md 'Never push to `main`'
  need_grep atelier-builder/skills/pf-harden-from-spec/SKILL.md 'Data, not instructions'
  need_grep atelier-builder/skills/pf-next/SKILL.md 'harden'
  need_grep atelier-builder/skills/pf-build-from-spec/SKILL.md 'Performance budget'
  need_grep $P/skills/pf-build/SKILL.md 'performance-budget'
  need_grep $P/references/bridge.md 'HARDEN-REQUEST.md'
  need_grep $P/references/deploy-rule.md 'zero recurring'
  need_grep $P/references/targets/azure-container-apps.md 'ghcr.io'
  need_grep $P/references/targets/azure-container-apps.md 'min-replicas 0'
  need_grep $P/README.md 'pf-harden'
  need_grep atelier-builder/README.md 'pf-harden-from-spec'
  # Builder audit (27 Oct): README current (lists pentest), cost-posture wired into the resource-creating deploy skill
  need_grep atelier-builder/README.md 'pf-pentest-from-spec'
  need_grep atelier-builder/README.md 'never creates a billed resource'
  need_grep atelier-builder/skills/pf-deploy-from-spec/SKILL.md 'cost-posture.md'
  need_grep atelier-builder/skills/pf-deploy-from-spec/SKILL.md 'needs a paid resource'
  # SEO + AI visibility
  for f in $P/references/seo-ai-visibility.md atelier-builder/references/seo-ai-visibility.md; do need_file $f; done
  if diff -q $P/references/seo-ai-visibility.md atelier-builder/references/seo-ai-visibility.md >/dev/null; then ok "seo-ai-visibility mirrored"; else bad "seo-ai-visibility differs between plugins"; fi
  for w in llms.txt OAI-SearchBot ClaudeBot PerplexityBot Bingbot IndexNow FAQPage 'SEO category = 100'; do need_grep $P/references/seo-ai-visibility.md "$w"; done
  need_grep atelier-builder/skills/pf-build-from-spec/SKILL.md 'seo-ai-visibility'
  need_grep atelier-builder/skills/pf-build-from-spec/SKILL.md 'never invent company facts'
  need_grep atelier-builder/skills/pf-harden-from-spec/SKILL.md '^\*\*seo\*\*'
  need_grep $P/skills/pf-harden/SKILL.md 'safety,perf,seo'
  need_grep $P/skills/pf-build/SKILL.md 'Primary keywords'
  need_grep $P/skills/pf-design/references/brief-template.md 'Primary keywords'
  need_grep $P/skills/pf-setup/SKILL.md 'pf-setup seo'
  need_grep $P/skills/pf-setup/SKILL.md 'Bing Webmaster'
  need_grep $P/README.md 'llms.txt'
  # SEO items folded from the seotipsbypawan post-launch guide (27 Oct)
  need_grep $P/references/seo-ai-visibility.md 'per service and per area'
  need_grep $P/references/seo-ai-visibility.md 'Microsoft Clarity'
  need_grep $P/references/seo-ai-visibility.md 'Measurement'
  # Refinements reconciled against the guide's actual 10 steps (27 Oct)
  need_grep $P/references/seo-ai-visibility.md 'doorway pages'
  need_grep $P/references/seo-ai-visibility.md 'cannibalise'
  need_grep $P/references/seo-ai-visibility.md 'hub-and-spoke'
  need_grep $P/references/seo-ai-visibility.md 'conversions/key events'
  # Security contract
  for f in $P/references/security.md atelier-builder/references/security.md; do need_file $f; done
  if diff -q $P/references/security.md atelier-builder/references/security.md >/dev/null; then ok "security mirrored"; else bad "security differs between plugins"; fi
  for w in 'Row Level Security' 'Supabase Auth' 'Strict-Transport-Security' 'npm audit' 'defensive' 'human pentester'; do need_grep $P/references/security.md "$w"; done
  need_grep $P/references/security.md 'No attack tooling'
  need_grep atelier-builder/skills/pf-build-from-spec/SKILL.md 'security.md'
  need_grep atelier-builder/skills/pf-build-from-spec/SKILL.md 'Security gate'
  need_grep atelier-builder/skills/pf-harden-from-spec/SKILL.md '^\*\*security\*\*'
  need_grep atelier-builder/skills/pf-harden-from-spec/SKILL.md 'never scan or test any other host'
  need_grep $P/skills/pf-harden/SKILL.md 'seo,security'
  need_grep $P/skills/pf-build/SKILL.md 'Security met on every'
  need_grep $P/README.md 'Secure by default'
  need_grep $P/README.md 'penetration testing'
  # Adversarial security testing (pentest) — gated, own-staging-only
  for f in $P/references/security-testing.md $P/skills/pf-pentest/SKILL.md $P/tests/pf-pentest.md atelier-builder/skills/pf-pentest-from-spec/SKILL.md; do need_file $f; done
  need_grep $P/skills/pf-pentest/SKILL.md '^name: pf-pentest$'
  need_grep atelier-builder/skills/pf-pentest-from-spec/SKILL.md '^name: pf-pentest-from-spec$'
  need_grep $P/references/security-testing.md 'authorized_targets'
  need_grep $P/references/security-testing.md 'synthetic'
  need_grep $P/references/security-testing.md 'stops when the run completes'
  need_grep $P/references/security-testing.md 'What it never does'
  need_grep atelier-builder/skills/pf-pentest-from-spec/SKILL.md 'not in authorized pre-production allowlist'
  need_grep atelier-builder/skills/pf-pentest-from-spec/SKILL.md 'never run it on a schedule'
  need_grep atelier-builder/skills/pf-pentest-from-spec/SKILL.md 'bounded assessment against'
  need_grep atelier-builder/skills/pf-pentest-from-spec/SKILL.md 'does not author exploit payloads'
  need_grep $P/skills/pf-pentest/SKILL.md 'is ignored here by design'
  need_grep $P/skills/pf-pentest/SKILL.md 'synthetic'
  need_grep atelier-builder/skills/pf-next/SKILL.md 'pentest'
  need_grep atelier-builder/skills/pf-next/SKILL.md 'never skips the confirm for pentest'
  need_grep $P/references/bridge.md 'PENTEST-REQUEST.md'
  need_grep $P/references/state-schema.md 'security_testing'
  need_grep $P/references/state-schema.md 'authorized_targets'
  need_grep $P/skills/pf-setup/SKILL.md 'pf-setup pentest'
  need_grep $P/README.md 'pf-pentest'
  # pentest: two versions (scanners / agent / both), recommended + user choice + extra agent guardrail
  need_grep $P/skills/pf-pentest/SKILL.md 'scanners|agent|both'
  need_grep $P/skills/pf-pentest/SKILL.md 'Recommended'
  need_grep $P/skills/pf-pentest/SKILL.md 'Extra guardrail for the agent'
  need_grep $P/skills/pf-pentest/SKILL.md 'second'
  need_grep $P/references/security-testing.md 'Two versions'
  need_grep $P/references/security-testing.md 'Cons:'                         # pros AND cons shown at the choice
  need_grep $P/references/security-testing.md 'LLM cost'                       # the agent's cost con
  need_grep $P/references/security-testing.md 'deterministic'                  # the scanners pro
  need_grep $P/skills/pf-pentest/SKILL.md 'Con:'                               # cons surfaced in the skill's choice
  need_grep atelier-builder/skills/pf-pentest-from-spec/SKILL.md 'mode. is .scanners. or .both'
  need_grep atelier-builder/skills/pf-pentest-from-spec/SKILL.md 'agent mode requested but PentAGI not enabled'
  # Code simplicity & handoff
  for f in $P/references/code-simplicity.md atelier-builder/references/code-simplicity.md; do need_file $f; done
  if diff -q $P/references/code-simplicity.md atelier-builder/references/code-simplicity.md >/dev/null; then ok "code-simplicity mirrored"; else bad "code-simplicity differs between plugins"; fi
  for w in 'simplest correct version' 'No dead or speculative code' 'hard limit' 'knip' 'jscpd'; do need_grep $P/references/code-simplicity.md "$w"; done
  need_grep $P/references/code-simplicity.md 'never picks a worse language'
  need_grep atelier-builder/skills/pf-build-from-spec/SKILL.md 'reuse a maintained library'
  need_grep $P/skills/pf-build/SKILL.md 'handoff-ready'
  need_grep $P/README.md 'handoff-ready code'
  # Apple-grade design standard (web-licensed)
  for f in $P/references/design-standard.md atelier-builder/references/design-standard.md; do need_file $f; done
  if diff -q $P/references/design-standard.md atelier-builder/references/design-standard.md >/dev/null; then ok "design-standard mirrored"; else bad "design-standard differs between plugins"; fi
  for w in 'hierarchy, harmony' 'Inter' 'Lucide' 'never Apple' 'WCAG AA' '4-pt'; do need_grep $P/references/design-standard.md "$w"; done
  need_grep $P/references/design-standard.md 'SF Pro'
  need_grep $P/references/design-standard.md 'prefers-reduced-motion'
  need_grep atelier-builder/skills/pf-build-from-spec/SKILL.md 'Design standard'
  need_grep atelier-builder/skills/pf-build-from-spec/SKILL.md 'never Apple SF Pro'
  need_grep $P/skills/pf-design/SKILL.md 'design-standard.md'
  need_grep $P/skills/pf-build/SKILL.md 'Design standard met'
  # Adaptive design directions + motion-led layer
  need_grep $P/references/design-standard.md 'design direction'
  need_grep $P/references/design-standard.md 'Motion & animation'
  need_grep $P/references/design-standard.md 'scroll-reveal'
  need_grep $P/references/design-standard.md 'prefers-reduced-motion'
  need_grep $P/skills/pf-design/SKILL.md 'brief.design_direction'
  need_grep $P/references/state-schema.md '"design_direction"'
  need_grep atelier-builder/skills/pf-build-from-spec/SKILL.md 'design_direction'
  need_grep $P/README.md 'design direction'
  need_grep $P/README.md 'Apple-grade design'
  # Motion-led learnings folded from a real shipped build (grammar + gotchas + weight budget)
  need_grep $P/references/design-standard.md 'scroll is the clock'
  need_grep $P/references/design-standard.md 'one-shot reveal'
  need_grep $P/references/design-standard.md 'scrub'
  need_grep $P/references/design-standard.md 'GPU-only'
  need_grep $P/references/design-standard.md 'translate'
  need_grep $P/references/design-standard.md 'doubles the offset'
  need_grep $P/references/design-standard.md 'fetchpriority'
  need_grep $P/references/design-standard.md 'ImageBitmap'
  need_grep $P/references/design-standard.md 'warm-cache desktop'
  need_grep $P/references/performance-budget.md 'weight budget'
  need_grep $P/references/performance-budget.md 'weight, not the motion engine'
  need_grep $P/references/performance-budget.md 'cold cache'
  need_grep $P/references/performance-budget.md '50 ms during'
  # Legal/compliance + CLAUDE.md generator + adversarial edge-case tests
  for f in $P/references/compliance.md atelier-builder/references/compliance.md; do need_file $f; done
  if diff -q $P/references/compliance.md atelier-builder/references/compliance.md >/dev/null; then ok "compliance mirrored"; else bad "compliance differs between plugins"; fi
  for w in 'not legal advice' 'Dependency licences' 'Privacy policy' 'Data-subject rights' 'needs legal review'; do need_grep $P/references/compliance.md "$w"; done
  # Compliance items folded from the itsrishi.ai legal-checklist reel (27 Oct)
  need_grep $P/references/compliance.md 'consent checkbox'
  need_grep $P/references/compliance.md 'access and rectification'
  need_grep $P/references/compliance.md 'Third-party API . service terms'
  need_grep $P/references/compliance.md 'THIRD-PARTY-NOTICES'
  need_grep $P/references/compliance.md 'provenance'
  need_grep atelier-builder/skills/pf-build-from-spec/SKILL.md 'Compliance gate'
  need_grep atelier-builder/skills/pf-build-from-spec/SKILL.md 'CLAUDE.md'
  need_grep atelier-builder/skills/pf-build-from-spec/SKILL.md 'skip preambles'
  need_grep atelier-builder/skills/pf-harden-from-spec/SKILL.md '^\*\*compliance\*\*'
  need_grep $P/skills/pf-harden/SKILL.md 'security,compliance'
  need_grep $P/references/security.md 'Adversarial edge cases'
  need_grep $P/skills/pf-build/SKILL.md 'Legal/compliance checklist met'
  need_grep $P/skills/pf-build/SKILL.md 'Adversarial edge-case tests pass'
  need_grep $P/README.md 'project CLAUDE.md'
  # Official in-session review + claude-mem recommendation
  need_grep atelier-builder/skills/pf-build-from-spec/SKILL.md '/code-review'
  need_grep atelier-builder/skills/pf-build-from-spec/SKILL.md 'Official review'
  need_grep atelier-builder/skills/pf-harden-from-spec/SKILL.md '/security-review'
  need_grep $P/skills/pf-setup/SKILL.md 'claude-mem'
  need_grep $P/skills/pf-setup/SKILL.md 'built into Claude Code'
  need_grep $P/README.md 'built-in'
  need_grep $P/skills/pf-build/SKILL.md 'Official /code-review'
  # Free-first cost posture + project size / context-tool trigger
  for f in $P/references/cost-posture.md atelier-builder/references/cost-posture.md; do need_file $f; done
  if diff -q $P/references/cost-posture.md atelier-builder/references/cost-posture.md >/dev/null; then ok "cost-posture mirrored"; else bad "cost-posture differs between plugins"; fi
  for w in 'Free-first' 'credits you already hold' 'Oracle Cloud Always Free' 'minimal' 'Quality is the bar' 'Evaluate the project first' 'never overrides them'; do need_grep $P/references/cost-posture.md "$w"; done
  need_grep $P/references/deploy-rule.md 'cost-posture.md'
  # Self-hosted CI clarification: self-hosted Actions $0 and allowed; only hosted minutes billed
  need_grep $P/references/cost-posture.md 'self-hosted'
  need_grep $P/references/cost-posture.md 'postponed'
  need_grep $P/references/cost-posture.md 'free tier used within its limit'
  need_grep $P/references/cost-posture.md 'billed overage'
  need_grep $P/references/deploy-rule.md 'self-hosted'
  need_grep $P/references/deploy-rule.md 'GitHub-hosted'
  need_grep $P/references/security.md 'Gated checks before merge'
  need_grep $P/references/security.md 'self-hosted'
  need_grep $P/skills/pf-design/SKILL.md 'cost-posture.md'
  need_grep $P/skills/pf-design/SKILL.md 'brief.context_tooling'
  need_grep $P/references/state-schema.md '"context_tooling"'
  need_grep $P/skills/pf-setup/SKILL.md 'Graphify'
  need_grep atelier-builder/skills/pf-build-from-spec/SKILL.md 'Context-speed note'
  need_grep $P/README.md 'Free-first'
  # Handoff modes A/B (27 Oct): both built, A default, user chooses with pros/cons/cost
  need_file $P/references/handoff.md
  need_grep $P/references/handoff.md 'event wake'
  need_grep $P/references/handoff.md 'Cloud build'
  need_grep $P/references/handoff.md 'draws on your Claude plan usage'
  need_grep $P/references/handoff.md 'data_sensitivity'
  need_grep $P/references/handoff.md 'Key Vault'
  need_grep $P/references/state-schema.md '"data_sensitivity"'
  need_grep $P/references/state-schema.md '"handoff"'
  need_grep $P/references/bridge.md 'handoff.md'
  need_grep $P/references/bridge.md 'Wake on the event'
  need_grep $P/skills/pf-build/SKILL.md 'handoff.md'
  need_grep $P/skills/pf-build/SKILL.md '\-\-handoff'
  need_grep $P/skills/pf-build/SKILL.md 'Mode B'
  need_grep $P/skills/pf-setup/SKILL.md 'pf-setup handoff'
  need_grep $P/skills/pf-deploy/SKILL.md 'handoff.md'
  need_grep $P/skills/pf-harden/SKILL.md 'handoff.md'
  # pf-ship conductor (27 Oct): runs the whole pipeline, pauses only at human gates
  need_file $P/skills/pf-ship/SKILL.md
  need_grep $P/skills/pf-ship/SKILL.md '^name: pf-ship$'
  need_grep $P/skills/pf-ship/SKILL.md 'design sign-off'
  need_grep $P/skills/pf-ship/SKILL.md 'deploy go-live'
  need_grep $P/skills/pf-ship/SKILL.md 'pentest scope'
  need_grep $P/skills/pf-ship/SKILL.md 'handoff.md'
  need_grep $P/skills/pf-ship/SKILL.md 'never on a schedule'
  # pf-plan PM/BA/PO stage (27 Oct): discovery, budget forecast under cost posture, lanes, methodology, docs, living dashboard
  need_file $P/references/planning.md
  need_grep $P/references/planning.md 'does not unlock paid'            # budget never loosens cost posture
  need_grep $P/references/planning.md 'Solo lane'
  need_grep $P/references/planning.md 'Team lanes'
  need_grep $P/references/planning.md 'methodology'
  need_grep $P/references/planning.md 'shared database'                 # dashboard db, not republish
  need_grep $P/references/planning.md 'without re-asking permission'    # the artifact-update fix
  need_file $P/skills/pf-plan/SKILL.md
  need_grep $P/skills/pf-plan/SKILL.md '^name: pf-plan$'
  need_grep $P/skills/pf-plan/SKILL.md 'planning.md'
  need_grep $P/skills/pf-plan/SKILL.md 'plan sign-off'
  need_grep $P/skills/pf-plan/SKILL.md 'cost-posture.md'
  need_grep $P/references/state-schema.md '"planning"'
  need_grep $P/references/state-schema.md '"plan":'
  need_grep $P/skills/pf-ship/SKILL.md 'Stage 0'
  need_grep $P/skills/pf-design/SKILL.md 'approved plan'
  # Phase 2 (27 Oct): monitoring + alerts + auto-rollback
  for f in $P/references/monitoring.md atelier-builder/references/monitoring.md; do need_file $f; done
  if diff -q $P/references/monitoring.md atelier-builder/references/monitoring.md >/dev/null; then ok "monitoring mirrored"; else bad "monitoring differs between plugins"; fi
  need_grep $P/references/monitoring.md 'Auto-rollback'
  need_grep $P/references/monitoring.md 'last known-good'
  need_grep $P/references/monitoring.md 'Never auto-revert the database'
  need_grep $P/references/monitoring.md 'App Insights'
  need_grep $P/references/monitoring.md 'bake window'
  need_file $P/skills/pf-monitor/SKILL.md
  need_grep $P/skills/pf-monitor/SKILL.md '^name: pf-monitor$'
  need_grep $P/skills/pf-monitor/SKILL.md 'monitoring.md'
  need_grep $P/skills/pf-monitor/SKILL.md 'cost-posture.md'
  need_grep $P/references/deploy-rule.md 'Auto-rollback'
  need_grep $P/references/deploy-rule.md 'last known-good'
  need_grep atelier-builder/skills/pf-deploy-from-spec/SKILL.md 'rolled_back'
  need_grep atelier-builder/skills/pf-deploy-from-spec/SKILL.md 'Never roll back the database'
  need_grep $P/skills/pf-ship/SKILL.md 'pf-monitor'
  need_grep $P/skills/pf-setup/SKILL.md 'pf-setup monitor'
  need_grep $P/references/state-schema.md '"monitoring"'
  # Phase 3 (27 Oct): maintenance loop + backups/restore + growth loop
  need_file $P/references/maintenance.md
  need_grep $P/references/maintenance.md 'Backups & restore'
  need_grep $P/references/maintenance.md 'GitHub .authoritative'
  need_grep $P/references/maintenance.md 'restore drill'
  need_grep $P/references/maintenance.md 'Never back up'
  need_grep $P/references/maintenance.md 'pg_dump'
  need_grep $P/references/maintenance.md 'pentest is never scheduled'
  need_file $P/references/growth.md
  need_grep $P/references/growth.md 'Search Console'
  need_grep $P/references/growth.md 'no paid SEO tool'
  need_file $P/skills/pf-maintain/SKILL.md
  need_grep $P/skills/pf-maintain/SKILL.md '^name: pf-maintain$'
  need_grep $P/skills/pf-maintain/SKILL.md 'maintenance.md'
  need_grep $P/skills/pf-maintain/SKILL.md 'restore drill'
  need_grep $P/skills/pf-maintain/SKILL.md 'Never auto-deploy'
  need_file $P/skills/pf-grow/SKILL.md
  need_grep $P/skills/pf-grow/SKILL.md '^name: pf-grow$'
  need_grep $P/skills/pf-grow/SKILL.md 'growth.md'
  need_grep $P/skills/pf-setup/SKILL.md 'pf-setup backup'
  need_grep $P/references/state-schema.md '"maintenance"'
  need_grep $P/references/state-schema.md '"growth"'
  need_grep $P/skills/pf-ship/SKILL.md 'pf-maintain'
  # Phase-3 gap closers (27 Oct): secret rotation + real-bill spend watch, both recommend-only, secrets never held
  need_grep $P/references/maintenance.md 'Secret hygiene'
  need_grep $P/references/maintenance.md 'rotat'
  need_grep $P/references/maintenance.md 'never sees, types'
  need_grep $P/references/maintenance.md 'real bill'
  need_grep $P/references/maintenance.md 'free-tier limit'
  need_grep $P/references/maintenance.md 'no payment details'
  need_grep $P/skills/pf-maintain/SKILL.md 'secret_rotation'
  need_grep $P/skills/pf-maintain/SKILL.md 'never type'
  need_grep $P/skills/pf-maintain/SKILL.md 'Spend vs forecast'
  need_grep $P/skills/pf-maintain/SKILL.md 'recommendations.md'
  need_grep $P/references/state-schema.md 'secret_rotation'
  need_grep $P/references/state-schema.md '"spend"'
  need_grep $P/references/cost-posture.md 'In maintenance'
  need_grep $P/references/cost-posture.md 'before.*it bills'
  # Phase 4 (27 Oct): the cross-project control panel
  need_file $P/references/control-panel.md
  need_grep $P/references/control-panel.md 'Control panel'
  need_grep $P/references/control-panel.md 'shared database'
  need_grep $P/references/control-panel.md 'never republishes the page'
  need_grep $P/references/control-panel.md 'No secrets, no personal data'
  need_grep $P/references/control-panel.md 'Read-only mirror'
  need_file $P/skills/pf-board/SKILL.md
  need_grep $P/skills/pf-board/SKILL.md '^name: pf-board$'
  need_grep $P/skills/pf-board/SKILL.md 'control-panel.md'
  need_grep $P/skills/pf-board/SKILL.md 'artifact-capabilities'
  need_grep $P/skills/pf-board/SKILL.md 'never republish'
  # Multi-cloud / stack selection (27 Oct): any provider, free-first; + one-time project setup
  need_file $P/references/platform-selection.md
  need_grep $P/references/platform-selection.md 'not locked to Azure'
  need_grep $P/references/platform-selection.md 'provider-agnostic'
  need_grep $P/references/platform-selection.md 'open-source'
  need_grep $P/references/platform-selection.md 'the user picks'
  need_grep $P/references/deploy-rule.md 'platform-selection'
  need_grep $P/references/deploy-rule.md 'gcp-cloud-run'
  need_grep $P/references/cost-posture.md 'provider-agnostic'
  need_grep $P/skills/pf-plan/SKILL.md 'platform-selection.md'
  need_grep $P/skills/pf-plan/SKILL.md 'Platform . stack'
  need_grep $P/skills/pf-setup/SKILL.md 'pf-setup project'
  need_grep $P/skills/pf-setup/SKILL.md 'Superpowers'
  need_grep atelier-builder/skills/pf-build-from-spec/SKILL.md 'Plan-first'
  need_file $P/references/skills.md
  need_grep $P/references/skills.md 'overrides a contract'
  need_grep $P/references/skills.md 'find-skill'
  need_grep $P/references/skills.md 'team-lane'
  need_grep $P/skills/pf-design/SKILL.md 'skills.md'
  need_grep $P/skills/pf-plan/SKILL.md 'tech-doc-audit'
  need_grep $P/skills/pf-plan/SKILL.md 'team-lane'
  # Full skill catalog (which/when/how) is the detailed map
  need_file $P/references/skill-catalog.md
  need_grep $P/references/skill-catalog.md 'tech-doc-audit'
  need_grep $P/references/skill-catalog.md 'swot-analysis'
  need_grep $P/references/skill-catalog.md 'Out of scope'
  need_grep $P/references/skill-catalog.md 'never overrides a contract'
  # One-stop bundling: 3 permissive MIT skills vendored WITH their licenses, others install on first run
  for s in find-skill humanizer design-md; do
    need_file $P/skills/$s/SKILL.md
    if ls $P/skills/$s/LICENSE* >/dev/null 2>&1; then ok "$s ships its LICENSE"; else bad "$s missing its LICENSE"; fi
  done
  # brand-guidelines must NOT be bundled (it is Anthropic's own brand skill — not redistributable)
  if [ -e $P/skills/brand-guidelines ]; then bad "brand-guidelines must not be bundled (Anthropic brand skill)"; else ok "brand-guidelines not bundled"; fi
  need_file THIRD-PARTY-NOTICES.md
  for h in humanizer design-md find-skill; do need_grep THIRD-PARTY-NOTICES.md "$h"; done
  need_grep THIRD-PARTY-NOTICES.md 'MIT'
  # First-run bootstrap installer
  need_file $P/skills/pf-bootstrap/SKILL.md
  need_grep $P/skills/pf-bootstrap/SKILL.md '^name: pf-bootstrap$'
  need_grep $P/skills/pf-bootstrap/SKILL.md 'official source'
  need_grep $P/skills/pf-bootstrap/SKILL.md 'once-per'
  need_grep $P/skills/pf-bootstrap/SKILL.md 'bootstrap.json'
  need_grep $P/skills/pf-setup/SKILL.md 'pf-bootstrap'
  # Standing pros/cons rule + pf-ship autonomy level (27 Oct)
  need_file $P/references/recommendations.md
  need_grep $P/references/recommendations.md 'pros, cons and cost'
  need_grep $P/references/recommendations.md 'never the upside alone'
  need_grep $P/references/recommendations.md 'Never trade away'
  need_grep $P/references/recommendations.md 'clear the bar'
  need_grep $P/references/monitoring.md 'Choosing the monitoring stack'
  need_grep $P/references/monitoring.md 'Cons:'
  need_grep $P/references/platform-selection.md 'pros, cons and cost'
  need_grep $P/skills/pf-ship/SKILL.md 'Autonomy level'
  need_grep $P/skills/pf-ship/SKILL.md 'streamlined'
  need_grep $P/references/state-schema.md '"ship_mode"'
fi

# --- v2 review fix pass
if [ "$STAGE" -ge 12 ]; then
  BN=atelier-builder/skills/pf-next/SKILL.md; BB=atelier-builder/skills/pf-build-from-spec/SKILL.md; BD=atelier-builder/skills/pf-deploy-from-spec/SKILL.md
  need_grep $BN 'request_id'                                   # C1 exact addressing
  need_grep $BN '/pf-next <slug> <build|merge|deploy>'
  need_grep $P/references/bridge.md 'request_id:'
  need_grep $P/references/bridge.md 'PF-MERGE v1'               # I15 merge shapes in bridge
  need_grep $P/references/bridge.md 'PF-MERGE-RESULT v1'
  need_grep $P/references/bridge.md 'project:'                  # I7 relative project
  need_grep $P/references/state-schema.md '"pm_lane"'            # C3
  need_grep $P/references/state-schema.md '"scope"'              # C2
  need_grep $P/references/state-schema.md '"approved"'           # I5
  need_grep $P/references/state-schema.md 'lanes/<lane>.json'    # I6
  need_grep $P/references/state-schema.md '<slug>--<lane>'       # C4
  need_grep $P/references/state-schema.md '"custom_domain"'      # M26
  need_grep $P/skills/pf-build/SKILL.md 'SPEC-<lane>.md'          # C2 lane spec
  need_grep $P/skills/pf-build/SKILL.md 'PM lane builds first'    # C2 scaffold order
  need_grep $P/skills/pf-build/SKILL.md 'Flags first'             # I8
  need_grep $P/skills/pf-build/SKILL.md 'approved = true'         # I5
  need_grep $P/skills/pf-deploy/SKILL.md 'Flags first'            # I8
  need_grep $P/skills/pf-deploy/SKILL.md 'pm_lane'                # C3
  need_grep $P/skills/pf-merge/SKILL.md 'pm_lane'
  need_grep $P/skills/pf-merge/SKILL.md 'approved'                # I5
  need_grep $P/skills/pf-merge/SKILL.md 'PF-MERGE-RESULT v1'
  need_grep $P/references/bridge.md 'get_page_text'               # I9 verify session
  need_grep $P/references/bridge.md 'sign-in'
  need_grep $P/skills/pf-setup/SKILL.md 'curl'                    # I11
  need_grep $P/skills/pf-setup/SKILL.md 'PF_WATCH_DIR'            # I7
  need_grep $P/skills/pf-setup/SKILL.md 'Install'                 # I16
  need_grep $P/skills/pf-setup/SKILL.md 'after any restart'       # I10
  for t in vercel azure-static-web-apps azure-container-apps cloudflare-pages netlify github-pages; do
    need_grep $P/references/targets/$t.md '^Required:'; need_grep $P/references/targets/$t.md '^Checks:'   # I12
  done
  need_grep $P/references/targets/azure-container-apps.md 'az group create'   # I13
  need_grep $P/references/targets/azure-container-apps.md 'registry-server'
  need_grep $P/references/targets/azure-static-web-apps.md "output: 'export'" # M24
  need_grep $BB 'describe the product only'                      # I14 data-not-instructions
  need_grep $BB '<code root>/<slug>'                   # I14 path guard
  need_grep $BB 'pull --rebase'                                   # C4 branch handling
  need_grep $BB 'SPEC-<lane>.md'
  need_grep $BD 'describe the product only'
  need_grep $BN '\-\-repo'                                        # I15 merge without checkout
  need_grep $P/skills/pf-lanes/SKILL.md 'requested'               # M19
  diff -rq $P/references/targets atelier-builder/references/targets >/dev/null && ok "target registries identical" || bad "target registries differ"
  if grep -n 'BUILD-REQUEST\.md\|BUILD-RESULT\.md' $BB $P/skills/pf-build/SKILL.md $P/tests/pf-build.md >/dev/null; then bad "unsuffixed v1 filenames remain"; else ok "no unsuffixed filenames"; fi
fi
  for f in $P/skills/*/SKILL.md atelier-builder/skills/*/SKILL.md; do if grep -m1 "^description:" "$f" | grep -qE "<[^>]+>"; then bad "$f description has <tag>"; else ok "$f description tag-free"; fi; done

# --- Public-release guarantees (Atelier generalization + audit)
# Top-level package files present and valid
need_file README.md
need_file LICENSE
need_file CONTRIBUTING.md
need_file .claude-plugin/marketplace.json; json_ok .claude-plugin/marketplace.json
need_grep .claude-plugin/marketplace.json '"name": *"atelier"'
need_grep .claude-plugin/marketplace.json '"source": *"\./atelier"'
need_grep .claude-plugin/marketplace.json '"source": *"\./atelier-builder"'
need_grep LICENSE 'MIT License'
need_grep README.md 'plugin install atelier@atelier'
need_grep README.md 'plugin install atelier-builder@atelier'
# Plugin manifests carry the new names
need_grep $P/.claude-plugin/plugin.json '"name": *"atelier"'
need_grep atelier-builder/.claude-plugin/plugin.json '"name": *"atelier-builder"'
# Generic hygiene: no machine-specific cloud-sync paths leaked into the plugins
if grep -rnE 'OneDrive|Claude AI' atelier atelier-builder --include='*.md' >/dev/null 2>&1; then bad "machine-specific path remains in a plugin"; else ok "plugins free of machine-specific paths"; fi
# Cross-platform: no Windows-only hardcoded code path
if grep -rnE 'C:..dev..pf' atelier atelier-builder --include='*.md' >/dev/null 2>&1; then bad "hardcoded C:\\dev\\pf remains"; else ok "code path is cross-platform"; fi
# No leftover old plugin-name references in content
if grep -rn 'product-factory' atelier atelier-builder --include='*.md' >/dev/null 2>&1; then bad "old plugin name product-factory remains"; else ok "no old plugin-name references"; fi

[ $fail -eq 0 ] && echo "ALL PASS" || { echo "FAILURES"; exit 1; }
