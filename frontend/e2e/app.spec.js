import { test, expect, request } from '@playwright/test';

const apiBase = 'http://127.0.0.1:8000';

async function bootstrapUser(api, role, email) {
  const response = await api.post(`${apiBase}/test/bootstrap-user`, {
    data: {
      email,
      password: 'password123',
      name: role === 'admin' ? 'Admin E2E' : 'User E2E',
      role
    }
  });
  expect(response.ok()).toBeTruthy();
}

async function login(page, email = 'e2e_user@example.com') {
  await page.goto('/#/login');
  await page.getByTestId('email').fill(email);
  await page.getByTestId('password').fill('password123');
  await page.getByTestId('login-submit').click();
  await expect(page).toHaveURL(/.*dashboard/);
}

test.beforeAll(async () => {
  const api = await request.newContext();
  await bootstrapUser(api, 'user', 'e2e_user@example.com');
  await bootstrapUser(api, 'admin', 'e2e_admin@example.com');
  await api.dispose();
});

test('save scheme flow', async ({ page }) => {
  await login(page);
  await page.getByTestId('scheme-query').fill('pm kisan');
  await page.getByTestId('scheme-search').click();
  const saveButton = page.getByTestId('save-toggle-PM Kisan');
  await expect(saveButton).toBeVisible();
  await saveButton.click();
  await expect(saveButton).toContainText('Unsave');
  await saveButton.click();
  await expect(saveButton).toContainText('Save');
});

test('checklist persistence', async ({ page }) => {
  await login(page);
  const firstCheckbox = page.locator('[data-testid^="check-"]').first();
  await expect(firstCheckbox).toBeVisible();
  await firstCheckbox.check();
  await page.reload();
  const firstCheckboxAfterReload = page.locator('[data-testid^="check-"]').first();
  await expect(firstCheckboxAfterReload).toBeChecked();
});

test('compare modal behavior', async ({ page }) => {
  await login(page);
  await page.getByTestId('scheme-query').fill('PM Kisan');
  await page.getByTestId('scheme-search').click();
  await page.getByTestId('compare-PM Kisan').click();
  await page.getByTestId('run-compare').click();
  await expect(page.getByTestId('compare-error')).toContainText('Pick 2 or 3 schemes');
  await page.getByTestId('compare-b').fill('Atal Pension Yojana');
  await page.getByTestId('run-compare').click();
  await expect(page.getByTestId('compare-results')).toBeVisible();
});

test('autosuggest dropdown interaction', async ({ page }) => {
  await login(page);
  await page.getByTestId('scheme-query').fill('PM');
  const dropdown = page.getByTestId('autosuggest-dropdown');
  await expect(dropdown).toBeVisible();
  await page.locator('[data-testid^="autosuggest-item-"]').first().click();
  await expect(page.getByTestId('scheme-query')).toHaveValue(/PM/i);
});

test('alert generation and display', async ({ page, request }) => {
  await login(page);
  const token = await page.evaluate(() => localStorage.getItem('access_token'));
  expect(token).toBeTruthy();

  const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };
  const subResp = await request.post(`${apiBase}/api/v1/alerts/subscriptions`, {
    headers,
    data: {
      scheme_name: 'PM Kisan',
      channel: 'in_app',
      next_deadline: '2026-02-26'
    }
  });
  expect(subResp.ok()).toBeTruthy();

  const dispatchResp = await request.post(`${apiBase}/api/v1/alerts/dispatch`, { headers });
  expect(dispatchResp.ok()).toBeTruthy();

  await page.reload();
  await expect(page.getByTestId('notification-list')).toContainText('Scheme alert');
});
