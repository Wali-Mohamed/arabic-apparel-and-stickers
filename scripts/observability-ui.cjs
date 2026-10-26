// Local-only browser review; no external services or customer records.
const { chromium, expect } = require('@playwright/test');
(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage();
    // Collector/application readiness does not imply Grafana HTTP readiness.
    await expect.poll(async () => {
      try { return (await page.request.get('http://lgtm:3000/api/health')).ok(); }
      catch { return false; }
    }, { timeout: 120000 }).toBe(true);
    await page.goto('http://lgtm:3000/d/apparel-local', { waitUntil: 'domcontentloaded' });
    if (new URL(page.url()).pathname === '/login') {
      await page.getByPlaceholder('Email or username').fill('admin');
      await page.getByPlaceholder('Password').fill('admin');
      await page.getByRole('button', { name: 'Log in', exact: true }).click();
      const skip = page.getByRole('button', { name: 'Skip' });
      if (await skip.isVisible()) await skip.click();
      await page.goto('http://lgtm:3000/d/apparel-local');
    }
    for (const title of ['Requests by route and status', 'Errors (4xx and 5xx)',
      'Request p95 seconds', 'Sanitized completion logs (expand TraceID link)']) {
      await expect(page.getByText(title, { exact: true }).first()).toBeVisible({ timeout: 60000 });
    }
    console.log('PASS: actual Chromium loaded all four provisioned Grafana panels');
    console.log('LIMIT: metric exemplar click-through and trace Explore UI are not asserted here');
  } finally { await browser.close(); }
})().catch(() => { console.error('Grafana browser verification failed'); process.exitCode = 1; });
