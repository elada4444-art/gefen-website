const { chromium } = require('playwright-core');
const path = require('path');

// Point this at the Chromium that ships with the environment.
const EXECUTABLE = process.env.CHROMIUM || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const HTML = 'file://' + path.join(__dirname, 'bubbles.html');

const CARDS = [
  { id: 'amit', tail: '' },
  { id: 'michal', tail: 'tail-left' },
  { id: 'noam', tail: 'tail-right' },
  { id: 'dan', tail: '' },
  { id: 'dan-truth', tail: '' },
];

(async () => {
  const browser = await chromium.launch({ executablePath: EXECUTABLE });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  for (const { id, tail } of CARDS) {
    await page.goto(`${HTML}?id=${id}&tail=${encodeURIComponent(tail)}`);
    await page.waitForTimeout(150);
    const el = page.locator('#' + id);
    const box = await el.boundingBox();
    // include the bubble tail (extra 34px below) in the transparent screenshot
    await page.screenshot({
      path: path.join(__dirname, `${id}.png`),
      omitBackground: true,
      clip: { x: box.x - 4, y: box.y - 4, width: box.width + 8, height: box.height + 34 },
    });
    console.log('rendered', id);
  }
  await browser.close();
})();
