import { test, expect } from '@playwright/test';

test('login page shows form', async ({ page }) => {
  await page.goto('http://localhost:3000/auth/login');
  await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible();
  await expect(page.getByLabel('Email')).toBeVisible();
  await expect(page.getByLabel('Password')).toBeVisible();
});
