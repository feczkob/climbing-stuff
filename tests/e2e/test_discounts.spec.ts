import { test, expect } from '@playwright/test';

// Helper to select a category and wait for products to load
const eachCategory = [
  { value: 'ropes', expectedDiscounts: 112 },
  { value: 'friends-nuts', expectedDiscounts: 64 },
  { value: 'slings', expectedDiscounts: 103 },
  { value: 'carabiners-quickdraws', expectedDiscounts: 117 },
];

test.describe('Discounts E2E (mock mode)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should show the main page and category select', async ({ page }) => {
    await expect(page.locator('h1')).toHaveText(/Climbing stuff discounts/i);
    await expect(page.locator('#category-select')).toBeVisible();
  });

  for (const { value, expectedDiscounts } of eachCategory) {
    test(`should show correct discounts for category: ${value}`, async ({ page }) => {
      await page.selectOption('#category-select', value);
      // Wait for products to load
      await page.waitForTimeout(500); // or use a better wait if you have a loading indicator
      const products = await page.locator('.product');
      await expect(products).toHaveCount(expectedDiscounts);
      if (expectedDiscounts > 0) {
        // Check that discount percent is rendered and in the correct format
        const discountPercents = await page.locator('.discount-percent').allTextContents();
        for (const percent of discountPercents) {
          expect(percent).toMatch(/^\-\d+%$/);
        }
      }
    });
  }

  test('should show product details for ropes', async ({ page }) => {
    await page.selectOption('#category-select', 'ropes');
    await page.waitForTimeout(500);
    const firstProduct = page.locator('.product').first();
    await expect(firstProduct.locator('.product-name')).toBeVisible();
    await expect(firstProduct.locator('.orig-price')).toBeVisible();
    await expect(firstProduct.locator('.disc-price')).toBeVisible();
    await expect(firstProduct.locator('.discount-percent')).toBeVisible();
    // Check that the discount percent is in the correct format
    const percent = await firstProduct.locator('.discount-percent').textContent();
    expect(percent).toMatch(/^\-\d+%$/);
  });
}); 