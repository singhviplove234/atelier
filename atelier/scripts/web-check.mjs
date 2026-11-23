#!/usr/bin/env node
// Web platform checker: eleven outdated or harmful web patterns a program can decide for certain.
// Read-only. It changes nothing, installs nothing and makes no network call.
//   node web-check.mjs <project folder> [--json]
// Exit 0 = nothing found, 1 = at least one failure, 2 = could not run (never a pass).
// The rule behind each check, and the page it was written from: references/web-checks.md.
import fs from 'node:fs';
import path from 'node:path';

const SKIP_DIRS = new Set(['node_modules', '.git', 'dist', 'build', '.next', 'out', 'coverage', '.vercel', '.turbo', 'vendor']);
const SCRIPT = /\.(m?[jt]sx?|cjs|vue|svelte|astro)$/i;
const MARKUP = /\.(html?|[jt]sx|vue|svelte|astro)$/i;
const STYLE = /\.(css|scss|less|vue|svelte|astro|html?)$/i;
const TESTISH = /(^|[\\/])(tests?|__tests__|e2e|fixtures?|mocks?|stories)([\\/]|$)|\.(test|spec|stories)\.[^.]+$/i;

function walk(root) {
  const out = [];
  (function go(dir, depth) {
    if (depth > 12) return;
    let ents; try { ents = fs.readdirSync(dir, { withFileTypes: true }); } catch { return; }
    for (const e of ents) {
      if (e.isSymbolicLink()) continue;
      const p = path.join(dir, e.name);
      if (e.isDirectory()) { if (!SKIP_DIRS.has(e.name)) go(p, depth + 1); }
      else if (e.isFile() && (SCRIPT.test(e.name) || MARKUP.test(e.name) || STYLE.test(e.name))) out.push(p);
    }
  })(root, 0);
  return out;
}
const lineOf = (text, idx) => text.slice(0, idx).split('\n').length;
const blank = (m) => m.replace(/[^\n]/g, ' ');
const stripComments = (s) => s.replace(/\/\*[\s\S]*?\*\//g, blank).replace(/<!--[\s\S]*?-->/g, blank).replace(/(^|[^:'"`\\])\/\/[^\n]*/g, (m, a) => a + ' '.repeat(m.length - a.length));

const SCRIPT_RULES = [
  ['W1', /\bdocument\s*\.\s*write(?:ln)?\s*\(/g, 'document.write() is strongly discouraged. Build the element and add it to the page instead.'],
  ['W2', /addEventListener\s*\(\s*['"`]unload['"`]|\bonunload\s*=/g, 'The unload event should be avoided. Use pagehide or visibilitychange.'],
  ['W3', /\.\s*keyCode\b/g, 'KeyboardEvent.keyCode is deprecated. Use event.key or event.code.'],
  ['W4', /\bdocument\s*\.\s*execCommand\s*\(/g, 'document.execCommand() is deprecated. Use the Clipboard API or direct editing of the page.'],
  ['W5', /\.\s*substr\s*\(/g, 'String.substr() is deprecated. Use slice() or substring().'],
  ['W6', /(^|[^.\w$])escape\s*\(/g, 'escape() is deprecated. Use encodeURIComponent() or encodeURI().'],
  ['W7', /['"`]DOM(?:NodeInserted|NodeRemoved|SubtreeModified|AttrModified|CharacterDataModified|NodeInsertedIntoDocument|NodeRemovedFromDocument)['"`]/g, 'Mutation events are deprecated. Use a MutationObserver.'],
  ['W9', /\buserScalable\s*:\s*false\b|\bmaximumScale\s*:\s*(?:0?\.\d+|1(?:\.0+)?)\b/g, 'The page stops people zooming in. Leave zoom on: people with low vision need it.'],
];
const MARKUP_RULES = [
  ['W8', /<\s*(center|font|marquee)(?=[\s>/])/g, (m) => `The <${m[1]}> element is deprecated. Use CSS.`],
];
function checkViewport(text, push) {
  const re = /<meta\b[^>]*\bname\s*=\s*["']viewport["'][^>]*>/gi; let m;
  while ((m = re.exec(text))) {
    if (/user-scalable\s*=\s*(no|0)\b/i.test(m[0]) || /maximum-scale\s*=\s*(0?\.\d+|1(\.0+)?)(?![\d.])/i.test(m[0])) push('W9', m.index, 'The page stops people zooming in. Leave zoom on: people with low vision need it.');
  }
}
function checkLang(text, push) {
  const re = /<html\b([^>]*)>/gi; let m;
  while ((m = re.exec(text))) if (!/\blang\s*=/.test(m[1])) push('W10', m.index, 'The <html> element has no lang attribute. Say which language the page is in.');
}
function checkOutline(text, push) {
  const re = /([^{}]+)\{([^{}]*)\}/g; let m;
  while ((m = re.exec(text))) {
    const sel = m[1], body = m[2];
    if (!/:focus\b/.test(sel) && !/(^|[\s,}])\*\s*$/.test(sel.trim())) continue;
    if (!/(^|[;\s{])outline\s*:\s*(none|0)\b/i.test(body) || /outline\s*:\s*(?!none|0\b)[^;]+/i.test(body.replace(/outline\s*:\s*(none|0)\b[^;]*;?/i, ''))) continue;
    if (/box-shadow\s*:(?!\s*none)|(^|[;\s])border(-\w+)*\s*:(?!\s*(none|0))|background(-color)?\s*:|text-decoration\s*:(?!\s*none)|outline-(color|style|width)\s*:/i.test(body)) continue;
    push('W11', m.index + m[1].length, 'The focus outline is removed and nothing replaces it. Keyboard users cannot see where they are.');
  }
}

export function run(root) {
  const rel = (f) => path.relative(root, f).split(path.sep).join('/');
  const files = walk(root); const findings = []; const skipped = [];
  for (const f of files) {
    const r = rel(f); if (TESTISH.test(r)) continue;
    let raw; try { raw = fs.readFileSync(f, 'utf8'); } catch { continue; }
    if (raw.length > 2_000_000 || /[^\n]{5000}/.test(raw)) { skipped.push(r); continue; }
    const text = stripComments(raw);
    const push = (rule, idx, msg) => findings.push({ rule, level: 'fail', file: r, line: lineOf(text, idx), text: msg });
    if (SCRIPT.test(f) || /\.html?$/i.test(f)) for (const [rule, re, msg] of SCRIPT_RULES) { re.lastIndex = 0; let m; while ((m = re.exec(text))) push(rule, m.index, msg); }
    if (MARKUP.test(f)) { for (const [rule, re, msg] of MARKUP_RULES) { re.lastIndex = 0; let m; while ((m = re.exec(text))) push(rule, m.index, msg(m)); } checkViewport(text, push); checkLang(text, push); }
    if (STYLE.test(f)) checkOutline(/\.html?$|\.(vue|svelte|astro)$/i.test(f) ? (text.match(/<style\b[^>]*>([\s\S]*?)<\/style>/gi) || []).join('\n') : text, /\.(css|scss|less)$/i.test(f) ? push : (rule, _i, msg) => findings.push({ rule, level: 'fail', file: r, line: 0, text: msg }));
  }
  return { files: files.length, findings, skipped };
}

const isMain = process.argv[1] && path.resolve(process.argv[1]) === path.resolve(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1'));
if (isMain) {
  const args = process.argv.slice(2); const json = args.includes('--json'); const root = args.find((a) => !a.startsWith('--'));
  if (!root || !fs.existsSync(root) || !fs.statSync(root).isDirectory()) { console.log('web-check: not run - give the project folder: node web-check.mjs <folder>'); process.exit(2); }
  let res; try { res = run(path.resolve(root)); } catch (e) { console.log(`web-check: not run - ${e.message}`); process.exit(2); }
  const n = res.findings.length;
  if (json) console.log(JSON.stringify({ format: 'PF-WEB-CHECK v1', files: res.files, fails: n, skipped: res.skipped, findings: res.findings }, null, 2));
  else {
    for (const x of res.findings) console.log(`FAIL ${x.rule} ${x.file}${x.line ? ':' + x.line : ''} - ${x.text}`);
    for (const s of res.skipped) console.log(`skipped ${s} - a bundled or minified file, not checked`);
    console.log(`web-check: ${n ? 'FAIL' : 'pass'} - ${res.files} files read, ${n} failure${n === 1 ? '' : 's'}${res.skipped.length ? `, ${res.skipped.length} bundled file${res.skipped.length === 1 ? '' : 's'} skipped` : ''}`);
  }
  process.exit(n ? 1 : 0);
}
