#!/usr/bin/env node
// Security checker: four mechanical checks a program can decide the same way every time.
// Read-only. It changes nothing, installs nothing and makes no network call.
//   node sec-check.mjs <project folder> [--json]
// Exit 0 = nothing found, 1 = at least one failure, 2 = could not run (never a pass).
// Sources for each rule: references/attack-checks.md.
import fs from 'node:fs';
import path from 'node:path';

const SKIP_DIRS = new Set(['node_modules', '.git', 'dist', 'build', '.next', 'out', 'coverage', '.vercel', '.turbo', 'vendor']);
const CODE = /\.(m?[jt]sx?|cjs)$/;
const TESTISH = /(^|[\\/])(tests?|__tests__|e2e|fixtures?|mocks?|stories)([\\/]|$)|\.(test|spec|stories)\.[^.]+$/i;
const SECURITY_WORD = /token|secret|passw|otp|session|invite|reset|nonce|api[_-]?key|verif|coupon|csrf|salt|magic[_-]?link/i;

function walk(root) {
  const out = [];
  (function go(dir, depth) {
    if (depth > 12) return;
    let ents; try { ents = fs.readdirSync(dir, { withFileTypes: true }); } catch { return; }
    for (const e of ents) {
      if (e.isSymbolicLink()) continue;
      const p = path.join(dir, e.name);
      if (e.isDirectory()) { if (!SKIP_DIRS.has(e.name)) go(p, depth + 1); }
      else if (e.isFile() && (CODE.test(e.name) || /\.sql$/i.test(e.name))) out.push(p);
    }
  })(root, 0);
  return out;
}
const lineOf = (text, idx) => text.slice(0, idx).split('\n').length;
const stripSqlComments = (s) => s.replace(/--[^\n]*/g, (m) => ' '.repeat(m.length)).replace(/\/\*[\s\S]*?\*\//g, (m) => m.replace(/[^\n]/g, ' '));
const stripJsComments = (s) => s.replace(/\/\*[\s\S]*?\*\//g, (m) => m.replace(/[^\n]/g, ' ')).replace(/(^|[^:'"`\\])\/\/[^\n]*/g, (m, a) => a + ' '.repeat(m.length - a.length));

// 1. A database view in an exposed schema must run with the caller's rights (security_invoker).
function checkViews(sqlFiles, rel) {
  const views = new Map();
  for (const f of sqlFiles.sort()) {
    const text = stripSqlComments(fs.readFileSync(f, 'utf8'));
    const re = /\bcreate\s+(?:or\s+replace\s+)?(?:temp(?:orary)?\s+)?(recursive\s+)?view\s+(?:if\s+not\s+exists\s+)?("?[\w.]+"?(?:\."?[\w]+"?)?)([\s\S]*?)\bas\b/gi;
    let m;
    while ((m = re.exec(text))) {
      const name = m[2].replace(/"/g, '').toLowerCase();
      const ok = /security_invoker\s*(=\s*(true|on|1)\b|\s*[,)])/i.test(m[3]);
      views.set(name, { file: rel(f), line: lineOf(text, m.index), ok });
    }
    const alt = /\balter\s+view\s+(?:if\s+exists\s+)?("?[\w.]+"?(?:\."?[\w]+"?)?)\s+set\s*\(([^)]*)\)/gi;
    while ((m = alt.exec(text))) {
      const name = m[1].replace(/"/g, '').toLowerCase();
      if (views.has(name) && /security_invoker\s*=\s*(true|on|1)\b/i.test(m[2])) views.get(name).ok = true;
    }
    const drop = /\bdrop\s+view\s+(?:if\s+exists\s+)?("?[\w.]+"?(?:\."?[\w]+"?)?)/gi;
    while ((m = drop.exec(text))) views.delete(m[1].replace(/"/g, '').toLowerCase());
  }
  const out = [];
  for (const [name, v] of views) {
    const schema = name.includes('.') ? name.split('.')[0] : 'public';
    if (schema !== 'public' || v.ok) continue;
    out.push({ rule: 'view-security', level: 'fail', file: v.file, line: v.line, text: `View ${name} is in the exposed schema without security_invoker = true, so it can show rows that row level security should hide.` });
  }
  return out;
}
// 2. Math.random() must not make anything that guards access.
function checkRandom(file, text, rel) {
  const out = []; const lines = text.split('\n'); const re = /\bMath\s*\.\s*random\s*\(/g; let m;
  while ((m = re.exec(text))) {
    const ln = lineOf(text, m.index);
    if (/sec-check:\s*not-security/i.test(lines.slice(Math.max(0, ln - 2), ln).join('\n'))) continue;
    const sec = SECURITY_WORD.test(lines[ln - 1] || '');                 // the same line only: a nearby line is not evidence
    out.push({ rule: 'weak-random', level: sec ? 'fail' : 'note', file: rel(file), line: ln, text: sec ? 'Math.random() makes something that guards access on this line. Use crypto.getRandomValues or crypto.randomBytes.' : 'Math.random() is used here. Fine for visuals; never for a token, code or id that guards something.' });
  }
  return out;
}
// 3. Proxy trust must not be left wide open.
function checkTrustProxy(file, text, rel) {
  const out = []; const re = /(['"`]trust proxy['"`]\s*,\s*true\b)|(\btrustProxy\s*:\s*true\b)/g; let m;
  while ((m = re.exec(text))) out.push({ rule: 'trust-proxy', level: 'fail', file: rel(file), line: lineOf(text, m.index), text: 'Proxy trust is set to true, so a visitor can claim any address and dodge a per-address limit. Set the exact number of proxies or their addresses.' });
  return out;
}
// 4. A login token must be verified with a fixed algorithm, never the one the token names.
function argsOf(text, openIdx) {
  let depth = 0;
  for (let i = openIdx; i < Math.min(text.length, openIdx + 1500); i++) {
    const c = text[i];
    if (c === '(') depth++;
    else if (c === ')') { depth--; if (depth === 0) return text.slice(openIdx + 1, i); }
  }
  return null;
}
function checkJwt(file, text, rel) {
  const out = [];
  const usesJsonwebtoken = /['"`]jsonwebtoken['"`]/.test(text);
  const usesJose = /['"`]jose['"`]/.test(text);
  const scan = (re, lib) => { let m; while ((m = re.exec(text))) {
    const args = argsOf(text, m.index + m[0].length - 1);
    if (args === null || /\balgorithms\s*:/.test(args)) continue;
    out.push({ rule: 'jwt-algorithm', level: 'fail', file: rel(file), line: lineOf(text, m.index), text: `A ${lib} token is verified without a fixed "algorithms" list, so the token can choose its own algorithm.` });
  } };
  if (usesJsonwebtoken) scan(/\b(?:jwt|jsonwebtoken|JWT)\s*\.\s*verify\s*\(/g, 'jsonwebtoken');
  if (usesJose) scan(/\bjwtVerify\s*\(/g, 'jose');
  return out;
}

export function run(root) {
  const rel = (f) => path.relative(root, f).split(path.sep).join('/');
  const files = walk(root);
  const skipped = [];
  const findings = checkViews(files.filter((f) => /\.sql$/i.test(f)), rel);
  for (const f of files.filter((x) => CODE.test(x) && !TESTISH.test(rel(x)))) {
    let raw; try { raw = fs.readFileSync(f, 'utf8'); } catch { continue; }
    if (raw.length > 2_000_000 || /[^\n]{5000}/.test(raw)) { skipped.push(rel(f)); continue; }   // a bundled or minified file is someone else's built code: named, not judged
    const text = stripJsComments(raw);
    findings.push(...checkRandom(f, raw, rel), ...checkTrustProxy(f, text, rel), ...checkJwt(f, text, rel));
  }
  return { files: files.length, findings, skipped };
}

const isMain = process.argv[1] && path.resolve(process.argv[1]) === path.resolve(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1'));
if (isMain) {
  const args = process.argv.slice(2); const json = args.includes('--json'); const root = args.find((a) => !a.startsWith('--'));
  if (!root || !fs.existsSync(root) || !fs.statSync(root).isDirectory()) { console.log('sec-check: not run - give the project folder: node sec-check.mjs <folder>'); process.exit(2); }
  let res; try { res = run(path.resolve(root)); } catch (e) { console.log(`sec-check: not run - ${e.message}`); process.exit(2); }
  const fails = res.findings.filter((x) => x.level === 'fail'); const notes = res.findings.filter((x) => x.level === 'note');
  if (json) console.log(JSON.stringify({ format: 'PF-SEC-CHECK v1', files: res.files, fails: fails.length, notes: notes.length, skipped: res.skipped, findings: res.findings }, null, 2));
  else {
    for (const x of res.findings) console.log(`${x.level === 'fail' ? 'FAIL' : 'note'} ${x.rule} ${x.file}:${x.line} - ${x.text}`);
    for (const s of res.skipped) console.log(`skipped ${s} - a bundled or minified file, not checked`);
    console.log(`sec-check: ${fails.length ? 'FAIL' : 'pass'} - ${res.files} files read, ${fails.length} failure${fails.length === 1 ? '' : 's'}, ${notes.length} note${notes.length === 1 ? '' : 's'}${res.skipped.length ? `, ${res.skipped.length} bundled file${res.skipped.length === 1 ? '' : 's'} skipped` : ''}`);
  }
  process.exit(fails.length ? 1 : 0);
}
