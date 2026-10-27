// Read-only local UI check. Screenshot capture/manual review remains separate.
const { chromium, expect } = require('@playwright/test');
(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage();
    await expect.poll(async () => {
      try { return (await page.request.get('http://lgtm:3000/api/health')).ok(); }
      catch { return false; }
    }, { timeout: 120000 }).toBe(true);
    const login = await page.request.post('http://lgtm:3000/login', {
      data: { user: 'admin', password: 'admin' }
    });
    expect(login.ok()).toBe(true); // Local demo session; never print cookies.
    const ruleUrl = 'http://lgtm:3000/alerting/grafana/pricing-unavailable/view';
    await page.goto(ruleUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
    if (new URL(page.url()).pathname === '/login') {
      await page.getByPlaceholder('Email or username').fill('admin');
      await page.getByPlaceholder('Password').fill('admin');
      await page.getByRole('button', { name: 'Log in', exact: true }).click();
      await page.goto(ruleUrl);
    }
    await expect(page.getByText('PricingUnavailable', { exact: true }).first()).toBeVisible({ timeout: 60000 });
    console.log('PASS: actual Grafana Alert rules UI displays PricingUnavailable');
  } finally { await browser.close(); }
})().catch(error => { console.error('Alert UI verification failed: ' + error.message.split('\n')[0]); process.exitCode = 1; });
