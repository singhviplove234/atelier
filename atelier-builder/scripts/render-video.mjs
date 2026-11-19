#!/usr/bin/env node
// Atelier's own renderer for the optional launch video (references/launch-video.md).
// It opens a local animation page in headless Chromium (Playwright, already an Atelier requirement),
// asks the page to draw each moment in time, screenshots it, and pipes the frames to ffmpeg.
// No graphics card, no network, no third-party tool.
//
//   node render-video.mjs stills <page.html> <outDir> <t1> <t2> ...          [--portrait]
//   node render-video.mjs video  <page.html> <out.mp4> [--fps 30] [--scale 1|2] [--portrait]
//
// Page contract: window.TOTAL (seconds) and window.renderAt(t) (may return a promise) —
// renderAt must draw the frame for time t from scratch, so any frame can be made in any order.
//   --scale 2  renders at twice the pixel density (1920x1080 -> 3840x2160)
//   --portrait 1080x1920 instead of 1920x1080
import { spawn } from 'node:child_process';
import { mkdirSync, existsSync } from 'node:fs';
import { resolve, dirname, join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';

const argv = process.argv.slice(2);
const take = (name) => { const i = argv.indexOf(name); if (i < 0) return null; const v = argv[i + 1]; argv.splice(i, 2); return v; };
const has = (name) => { const i = argv.indexOf(name); if (i < 0) return false; argv.splice(i, 1); return true; };
const fps = Number(take('--fps') || 30), scale = Number(take('--scale') || 1), portrait = has('--portrait');
const [mode, pageArg, out, ...times] = argv;
const usage = () => { console.error('usage: render-video.mjs stills|video <page.html> <out> [times...] [--fps n] [--scale 1|2] [--portrait]'); process.exit(2); };
if (!['stills', 'video'].includes(mode) || !pageArg || !out) usage();
if (!(fps >= 1 && fps <= 60) || ![1, 2].includes(scale)) usage();
const pagePath = resolve(pageArg);
if (!existsSync(pagePath)) { console.error(`page not found: ${pagePath}`); process.exit(2); }

// This script lives in the plugin, but Playwright lives in the product repo it is run from — so resolve it from the
// current folder first (the repo's node_modules), then from this script's own location.
let chromium;
try { ({ chromium } = createRequire(join(process.cwd(), 'package.json'))('playwright')); }
catch {
  try { ({ chromium } = await import('playwright')); }
  catch { console.error('Playwright is not installed in this folder. From the product repo run: npm i -D playwright && npx playwright install chromium'); process.exit(3); }
}

const size = portrait ? { width: 1080, height: 1920 } : { width: 1920, height: 1080 };
const browser = await chromium.launch();
let code = 0;
try {
  const context = await browser.newContext({ viewport: size, deviceScaleFactor: scale, offline: true });
  const page = await context.newPage();
  page.on('pageerror', (e) => console.error('page error:', e.message));
  await page.goto(pathToFileURL(pagePath).href);
  await page.waitForFunction(() => typeof window.renderAt === 'function' && Number.isFinite(window.TOTAL), null, { timeout: 15000 });
  await page.evaluate(() => document.fonts.ready.then(() => true));
  const draw = (t) => page.evaluate((time) => Promise.resolve(window.renderAt(time)).then(() => new Promise((r) => requestAnimationFrame(() => r(true)))), t);

  if (mode === 'stills') {
    mkdirSync(out, { recursive: true });
    for (const t of times.map(Number)) { await draw(t); await page.screenshot({ path: join(out, `${t.toFixed(2)}s.png`) }); }
    console.log(`stills: ${times.length} -> ${out}`);
  } else {
    const total = await page.evaluate(() => window.TOTAL);
    if (!(total > 0 && total <= 60)) throw new Error(`window.TOTAL must be between 0 and 60 seconds (got ${total})`);
    const frames = Math.round(total * fps);
    mkdirSync(dirname(resolve(out)), { recursive: true });
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'png', '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', resolve(out)], { stdio: ['pipe', 'ignore', 'pipe'] });
    let err = ''; ff.stderr.on('data', (d) => { err += d; });
    const done = new Promise((ok, no) => { ff.on('error', () => no(new Error('ffmpeg not found on PATH'))); ff.on('close', (c) => (c === 0 ? ok() : no(new Error(err || 'ffmpeg failed')))); });
    for (let f = 0; f < frames; f++) {
      await draw(f / fps);
      const png = await page.screenshot({ type: 'png' });
      if (!ff.stdin.write(png)) await new Promise((r) => ff.stdin.once('drain', r));
      if (f % fps === 0) process.stdout.write(`\r${f}/${frames} frames`);
    }
    ff.stdin.end(); await done;
    console.log(`\nvideo: ${out} (${frames} frames, ${fps} fps, ${size.width * scale}x${size.height * scale})`);
  }
} catch (e) { console.error('FAILED:', e.message); code = 1; }
finally { await browser.close(); }
process.exit(code);
