---
name: write-e2e-test
description: Write REAL Playwright E2E tests for Popinz. Use when asked to write tests, create test files, implement user journeys, or test a feature. Triggers on keywords like "test", "e2e", "playwright", "user journey", "ihm", "spec".
argument-hint: "[feature-name] e.g. dashboard, persons, calls, planning, groups, documents, evaluations, search, settings, registrations, login"
---

# Write REAL Playwright E2E Tests for Popinz

You are writing **real** end-to-end Playwright tests for the Popinz school management SaaS.

**Target**: `$ARGUMENTS` (the feature or page to test)

## ABSOLUTE RULES

1. **NEVER `console.log('TDD RED:...'); return;`** — a test that always passes is WORSE than no test
2. **NEVER `testInfo.skip()` or `test.skip()`**
3. **Every test MUST have `expect()` assertions that ACTUALLY EXECUTE on every run**
4. **If a page returns an error, the test MUST FAIL**
5. **Test REAL user behavior**: goto, click, fill, navigate, verify visible content
6. **Check 3 layers on EVERY test**: content (visible text/elements), console (0 JS errors), network (0 HTTP 5xx)
7. **Use Page Object Model** — one class per page, selectors centralized
8. **Run the test on staging** before considering it done

## STEP 1: Read Existing Code

Before writing anything:
1. Read `e2e/helpers/test-config.ts` for TestConfig, getUserCredentials, login
2. Read `e2e/helpers/auth.ts` for loginAs, apiLoginAs
3. Read `e2e/base.fixture.ts` if it exists
4. Check `e2e/pages/` for existing Page Objects
5. Check `e2e/helpers/error-tracker.ts` for the ErrorTracker class

If any of these don't exist yet, CREATE them first.

## STEP 2: Create/Update Page Objects

Each page needs a Page Object in `e2e/pages/`. Use REAL selectors from the reference below.

```typescript
// e2e/pages/ExamplePage.ts
import { type Page, type Locator, expect } from '@playwright/test';

export class ExamplePage {
  readonly page: Page;
  // Define locators from REAL HTML selectors
  readonly heading: Locator;
  readonly someButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.heading = page.locator('h1, h2, .page-title').first();
    this.someButton = page.locator('#real-button-id');
  }

  async goto() {
    await this.page.goto('/fr/some-route');
    await this.page.waitForLoadState('domcontentloaded');
  }

  async expectLoaded() {
    await expect(this.page).not.toHaveURL(/login/);
    await expect(this.heading).toBeVisible({ timeout: 10000 });
  }
}
```

## STEP 3: Write Tests

Every test file follows this structure:

```typescript
import { test, expect } from '@playwright/test';
import { TestConfig } from '../helpers/test-config';
import { loginAs } from '../helpers/auth';
import { ErrorTracker } from '../helpers/error-tracker';
import { SomePage } from '../pages/SomePage';

test.describe('Feature Name - Complete User Journey', () => {
  let errors: ErrorTracker;

  test.beforeEach(async ({ page, context }) => {
    errors = new ErrorTracker(page);
    await context.clearCookies();
    // Dismiss cookie consent
    const accept = page.locator('button:has-text("Accepter"), button:has-text("Accept")');
    await page.goto(`${TestConfig.baseUrl}/fr/login`);
    if (await accept.isVisible().catch(() => false)) {
      await accept.click();
      await page.waitForTimeout(300);
    }
  });

  test.afterEach(async () => {
    await errors.expectNoErrors();
  });

  test('descriptive name of what user does', async ({ page }) => {
    // 1. LOGIN as specific role
    await loginAs(page, 'owner');

    // 2. NAVIGATE to the feature page
    const somePage = new SomePage(page);
    await somePage.goto();

    // 3. ASSERT the page loaded correctly (content visible)
    await somePage.expectLoaded();
    await expect(somePage.heading).toContainText(/expected text/i);

    // 4. INTERACT with the page (click, fill, submit)
    await somePage.someButton.click();

    // 5. ASSERT the result
    await expect(page.locator('.result')).toBeVisible();

    // ErrorTracker.expectNoErrors() runs in afterEach
  });
});
```

## STEP 4: Run on Staging

After writing tests, run them:
```bash
ssh debian@51.38.224.228 "cd /opt/docker/staging/code/popinz-tests && sudo -u www-data-staging bash -c 'TEST_ENV=staging npx playwright test --config=playwright.staging-full.config.ts e2e/path/to/test.spec.ts --reporter=line 2>&1'"
```

## SELECTORS REFERENCE (from actual HTML)

See [selectors.md](selectors.md) for complete reference.

## ROUTES REFERENCE

See [routes.md](routes.md) for complete route mapping.

## ANTI-PATTERNS TO AVOID

```typescript
// BAD: Test that always passes
test('my test', async ({ page }) => {
  const response = await page.goto('/fr/some-page');
  if (response?.status() !== 200) {
    console.log('TDD RED: page not available');
    return; // ← TEST PASSES EVEN WHEN SITE IS BROKEN
  }
  await expect(something).toBeVisible();
});

// GOOD: Test that fails when page is broken
test('my test', async ({ page }) => {
  await loginAs(page, 'owner');
  await page.goto(`${TestConfig.baseUrl}/fr/some-page`);
  await expect(page).not.toHaveURL(/login/); // Not redirected
  const heading = page.locator('h1, h2, .page-title').first();
  await expect(heading).toBeVisible(); // Page has content
  // ErrorTracker catches console/network errors in afterEach
});
```

```typescript
// BAD: Guessed selectors
page.locator('.some-class-i-think-exists');

// GOOD: Selectors from actual HTML
page.locator('#frm_email');  // From login view
page.locator('#absenceSearchInput');  // From dashboard view
page.locator('.btn_present_ctn');  // From calls view
```
