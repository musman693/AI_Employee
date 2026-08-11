import { test, expect } from '@playwright/test';

test('login page shows form', async ({ page }) => {
  await page.goto('/login');
  await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible();
  await expect(page.getByLabel('Email')).toBeVisible();
  await expect(page.getByLabel('Password')).toBeVisible();
});

test('protected routes redirect to sign in and preserve destination', async ({ page }) => {
  await page.goto('/reports');
  await expect(page).toHaveURL(/\/login\?callbackUrl=%2Freports/);
  await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible();
});

test('root route cannot bypass authentication', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveURL(/\/login\?callbackUrl=%2Finbox/);
});

test('login validates credentials before contacting the backend', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('not-an-email');
  await page.getByLabel('Password').fill('short');
  await page.getByRole('button', { name: 'Continue' }).click();
  await expect(page.getByText('Enter a valid email')).toBeVisible();
  await expect(page.getByText('Password must have at least 8 characters')).toBeVisible();
});

test('account recovery navigation uses real routes', async ({ page }) => {
  await page.goto('/login');
  await page.getByRole('link', { name: 'Forgot password?' }).click();
  await expect(page).toHaveURL(/\/forgot-password$/);
  await page.getByRole('link', { name: 'Back to sign in' }).click();
  await expect(page).toHaveURL(/\/login$/);
});
