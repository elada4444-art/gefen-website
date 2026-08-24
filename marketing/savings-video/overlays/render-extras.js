const { chromium } = require('playwright-core');
const path = require('path');
const fs = require('fs');

const EXECUTABLE = process.env.CHROMIUM || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const HTML = 'file://' + path.join(__dirname, 'extras.html');
const OUTDIR = path.join(__dirname, 'extras');
fs.mkdirSync(OUTDIR, { recursive: true });

const INTRO_TEXT = 'שיחה נפוצה בין חברים בשנת 2026…';
const TYPE_FPS = 10;      // the intro sequence is played back at this fps in compose.sh
const HOLD_FRAMES = 20;   // full-text frames held after typing (2s at 10fps)

(async () => {
  const browser = await chromium.launch({ executablePath: EXECUTABLE });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });

  // disclaimer (static, full-frame, transparent)
  await page.goto(`${HTML}?el=disc`);
  await page.waitForTimeout(120);
  await page.screenshot({ path: path.join(OUTDIR, 'disc.png'), omitBackground: true });

  // intro typewriter frames (one cumulative frame per character, then a hold)
  await page.goto(`${HTML}?el=intro`);
  await page.waitForTimeout(120);
  const chars = Array.from(INTRO_TEXT);
  let idx = 1;
  for (let k = 1; k <= chars.length; k++) {
    await page.evaluate((t) => { document.getElementById('intro').textContent = t; }, chars.slice(0, k).join(''));
    await page.waitForTimeout(30);
    await page.screenshot({ path: path.join(OUTDIR, `intro_${String(idx++).padStart(3, '0')}.png`), omitBackground: true });
  }
  await page.evaluate((t) => { document.getElementById('intro').textContent = t; }, INTRO_TEXT);
  for (let h = 0; h < HOLD_FRAMES; h++) {
    await page.screenshot({ path: path.join(OUTDIR, `intro_${String(idx++).padStart(3, '0')}.png`), omitBackground: true });
  }
  console.log('intro frames:', idx - 1, '@', TYPE_FPS, 'fps =', ((idx - 1) / TYPE_FPS).toFixed(2), 's');
  await browser.close();
})();
