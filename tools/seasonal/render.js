// Renders jobs from a JSON file with headless Chromium (Playwright).
//   node tools/seasonal/render.js jobs.json
// job: {html, pdf, width, height}  -> vector PDF at that page size (CSS units, e.g. "8.5in")
//      {html, image, w, h, scale}  -> JPEG/PNG screenshot of a w x h viewport at deviceScaleFactor scale
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const browser = await chromium.launch();
  const ctxs = {};
  for (const j of jobs) {
    const key = j.pdf ? 'pdf' : `${j.w}x${j.h}@${j.scale || 1}`;
    if (!ctxs[key]) ctxs[key] = await browser.newContext(j.pdf ? {} : { viewport: { width: j.w, height: j.h }, deviceScaleFactor: j.scale || 1 });
    const page = await ctxs[key].newPage();
    await page.goto('file://' + j.html);
    await page.evaluate(() => document.fonts.ready);
    if (j.pdf) {
      await page.pdf({ path: j.pdf, width: j.width, height: j.height, printBackground: true, margin: { top: 0, right: 0, bottom: 0, left: 0 } });
    } else if (j.image.endsWith('.png')) {
      await page.screenshot({ path: j.image, type: 'png', omitBackground: !!j.transparent });
    } else {
      await page.screenshot({ path: j.image, type: 'jpeg', quality: j.quality || 90 });
    }
    await page.close();
  }
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
