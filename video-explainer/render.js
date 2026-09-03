// Frame-by-frame renderer: drives anim.html deterministically and pipes PNG frames into ffmpeg.
// usage: node render.js --html anim.html --timeline timeline.json --audio mix.wav --out final.mp4 [--fps 30] [--preview N]
const { chromium } = require('playwright-core');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const args = Object.fromEntries(process.argv.slice(2).map((a, i, arr) => a.startsWith('--') ? [a.slice(2), arr[i + 1]] : []).filter(Boolean));
const FPS = parseInt(args.fps || '30', 10);
const W = 1080, H = 1920;
const FFMPEG = '/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2';
const here = __dirname;

(async () => {
  const fontsCss = fs.readFileSync(path.join(here, '..', 'fonts', 'heebo-local.css'), 'utf8')
    .replace(/url\(([^)]+)\)/g, (m, f) => `url(file://${path.join(here, '..', 'fonts', f)})`);
  const logoB64 = fs.readFileSync('/home/user/gefen-website/assets/logo.png').toString('base64');
  let html = fs.readFileSync(args.html, 'utf8')
    .replace('/* __FONTS__ */', fontsCss)
    .split('__LOGO__').join('data:image/png;base64,' + logoB64);
  const timeline = args.timeline ? JSON.parse(fs.readFileSync(args.timeline, 'utf8')) : null;
  if (timeline) html = html.replace('window.TIMELINE = window.TIMELINE ||', 'window.TIMELINE = ' + JSON.stringify(timeline) + ' ||');
  html = html.replace('<script>', '<script>window.__RENDER_MODE__=true;');
  const tmpHtml = path.join(here, '_render.html');
  fs.writeFileSync(tmpHtml, html);

  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--no-sandbox', '--font-render-hinting=none'] });
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  await page.goto('file://' + tmpHtml);
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() => new Promise(r => setTimeout(r, 300)));
  const total = await page.evaluate(() => window.TIMELINE.total);
  console.error(`total ${total.toFixed(2)}s, ${Math.ceil(total * FPS)} frames @${FPS}fps`);

  if (args.preview) {
    // dump N evenly spaced frames as PNG for visual QA
    const n = parseInt(args.preview, 10);
    const dir = path.join(here, 'preview'); fs.mkdirSync(dir, { recursive: true });
    const times = args.times ? args.times.split(',').map(Number) : Array.from({ length: n }, (_, i) => (i + 0.5) * total / n);
    for (const t of times) {
      await page.evaluate(t => window.render(t), t);
      await page.screenshot({ path: path.join(dir, `t${t.toFixed(1).padStart(6, '0')}.png`), type: 'png' });
    }
    await browser.close(); console.error('preview done'); return;
  }

  const nFrames = Math.ceil(total * FPS);
  const ffArgs = ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', '-'];
  if (args.audio) ffArgs.push('-i', args.audio);
  ffArgs.push('-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', String(FPS), '-movflags', '+faststart');
  if (args.audio) ffArgs.push('-c:a', 'aac', '-b:a', '160k', '-shortest');
  ffArgs.push(args.out || 'final.mp4');
  const ff = spawn(FFMPEG, ffArgs, { stdio: ['pipe', 'inherit', 'inherit'] });
  const write = buf => new Promise(res => { if (!ff.stdin.write(buf)) ff.stdin.once('drain', res); else res(); });
  const t0 = Date.now();
  for (let i = 0; i < nFrames; i++) {
    const t = i / FPS;
    await page.evaluate(t => window.render(t), t);
    const buf = await page.screenshot({ type: 'png' });
    await write(buf);
    if (i % 150 === 0) console.error(`frame ${i}/${nFrames} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
  }
  ff.stdin.end();
  await new Promise((res, rej) => ff.on('close', c => c === 0 ? res() : rej(new Error('ffmpeg exit ' + c))));
  await browser.close();
  console.error('done in', ((Date.now() - t0) / 1000).toFixed(0), 's');
})().catch(e => { console.error(e); process.exit(1); });
