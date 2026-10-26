const { test, expect } = require('@playwright/test');
const base = process.env.BASE_URL || 'http://127.0.0.1:8080';

test('static production UI browses, personalizes, quotes and submits real orders', async ({ page }) => {
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto(base);
  await expect(page.locator('.product-card')).toHaveCount(8);
  // CSP allows the existing Arabic font and dynamic preview style.
  const sticker = page.locator('.product-card').filter({ hasText: 'Personalized Arabic HTV sticker' });
  await sticker.getByRole('button', { name: 'Customize' }).click();
  await page.getByLabel('Arabic text or name').fill('Latin');
  await expect(page.getByRole('alert')).toContainText('Arabic letters');
  await page.getByLabel('Arabic text or name').fill('علي');
  await expect(page.locator('.preview-text')).toHaveAttribute('dir', 'rtl');
  await expect(page.locator('.preview-text')).toHaveText('علي');
  await page.getByRole('combobox').first().selectOption('Cairo');
  await page.getByLabel('Sticker size').selectOption('9x4');
  await page.getByLabel('Gold', { exact: true }).check();
  await expect(page.locator('.preview-text')).toHaveCSS('color', 'rgb(216, 186, 57)');
  await expect(page.locator('.quote')).toContainText('£9.00');
  await page.getByLabel('Your name').fill('Production smoke synthetic');
  await page.getByLabel('Email or phone').fill('smoke@example.invalid');
  const submitted = page.waitForResponse(r => r.url().endsWith('/api/orders') && r.request().method() === 'POST');
  await page.getByRole('button', { name: 'Send order request', exact: true }).click();
  const response = await submitted;
  expect(response.status()).toBe(201);
  expect(await response.json()).toMatchObject({ total_price_pence: 900, status: 'new' });
  await expect(page.locator('.order-form')).toContainText('sent.');
  await page.getByRole('button', { name: 'Close', exact: true }).click();
  const fixed = page.locator('.product-card').filter({ hasText: 'Small Be Seen tag' });
  await fixed.getByRole('button', { name: 'View details' }).click();
  await expect(page.locator('.quote')).toContainText('£5.00');
  const fixedResponse = page.waitForResponse(r => r.url().endsWith('/api/orders') && r.request().method() === 'POST');
  await page.getByRole('button', { name: 'Send order request', exact: true }).click();
  expect((await fixedResponse).status()).toBe(201);
  expect(errors).toEqual([]);
});

test('reverse proxy protects API, rejects foreign origins and serves security headers', async ({ request }) => {
  const catalogue = await request.get(`${base}/api/products`);
  expect(catalogue.status()).toBe(200);
  const products = await catalogue.json();
  const letter = products.find(p => p.slug === 'small-arabic-letter-tag');
  const quote = await request.post(`${base}/api/products/${letter.id}/price`, {
    data: { options: { text: 'ب', font: 'Amiri' }, quantity: 3 },
  });
  expect((await quote.json()).total_price_pence).toBe(1350);
  expect((await request.post(`${base}/api/orders`, { headers: { Origin: 'https://evil.example.invalid' }, data: {} })).status()).toBe(403);
  expect((await request.get(`${base}/api/products`, { headers: { Host: 'evil.example.invalid' } })).status()).toBe(400);
  expect((await request.get(`${base}/api/missing`)).status()).toBe(404);
  const index = await request.get(base);
  expect(index.headers()['content-security-policy']).toContain("script-src 'self'");
  expect(index.headers()['x-content-type-options']).toBe('nosniff');
  expect(await index.text()).not.toContain('/@vite/client');
  expect((await request.get(`${base}/health/db`)).status()).toBe(200);
});
