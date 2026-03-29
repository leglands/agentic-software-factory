---
name: e2e-testing-patterns
version: 1.0.0
description: E2E testing patterns. Playwright + Vitest. POM, fixtures, API-first setup, visual regression, network interception, mobile, a11y, CI/CD, cleanup, smoke vs regression.
metadata:
  category: qa
  triggers:
  - implementing e2e tests
  - debugging flaky tests
  - e2e testing patterns
  - page object model
  - playwright patterns
  - vitest e2e
eval_cases:
- id: e2e-pom-pattern
  prompt: How do I implement Page Object Model for E2E tests?
  should_trigger: true
  checks:
  - length_min:200
  - no_placeholder
  expectations:
  - Shows BasePage class + concrete page class example
  - Selector priority: data-testid > role+name > aria-label > css
  tags:
  - e2e
  - pom
- id: e2e-fixtures
  prompt: How to set up test fixtures for authenticated users in E2E?
  should_trigger: true
  checks:
  - length_min:150
  - no_placeholder
  expectations:
  - Shows Vitest fixture with authenticated user reuse
  tags:
  - e2e
  - fixtures
- id: e2e-api-seed
  prompt: How to seed test data via API instead of UI clicks?
  should_trigger: true
  checks:
  - length_min:150
  - no_placeholder
  expectations:
  - Shows seedUser() and cleanupTestData() helpers
  - Explains API-first vs UI-click setup
  tags:
  - e2e
  - api-first
- id: e2e-visual-regression
  prompt: How to implement visual regression testing with screenshots?
  should_trigger: true
  checks:
  - length_min:150
  - no_placeholder
  expectations:
  - Shows assertScreenshot helper with threshold
  - Shows UPDATE_SCREENSHOTS env var pattern
  tags:
  - e2e
  - visual-regression
- id: e2e-network-interception
  prompt: How to mock external APIs in E2E tests?
  should_trigger: true
  checks:
  - length_min:150
  - no_placeholder
  expectations:
  - Shows page.route() for mocking + mockNetworkError helper
  tags:
  - e2e
  - network-interception
- id: e2e-mobile-responsive
  prompt: How to test responsive design across breakpoints in E2E?
  should_trigger: true
  checks:
  - length_min:120
  - no_placeholder
  expectations:
  - Shows setViewportSize loop over 3 breakpoints
  tags:
  - e2e
  - mobile
- id: e2e-accessibility
  prompt: How to integrate axe-core accessibility audits in E2E?
  should_trigger: true
  checks:
  - length_min:120
  - no_placeholder
  expectations:
  - Shows runAxeAudit helper + common violations checklist
  tags:
  - e2e
  - a11y
- id: e2e-cicd
  prompt: How to configure E2E tests for CI/CD with retries and parallel shards?
  should_trigger: true
  checks:
  - length_min:150
  - no_placeholder
  expectations:
  - Shows playwright config: retries, workers, shard, max-failures
  - Shows GitHub Actions matrix for 3 shards
  tags:
  - e2e
  - cicd
- id: e2e-cleanup
  prompt: How to clean up test data after E2E tests?
  should_trigger: true
  checks:
  - length_min:120
  - no_placeholder
  expectations:
  - Shows beforeEach/afterEach hooks
  - Shows isolated DB per test pattern
  tags:
  - e2e
  - cleanup
- id: e2e-smoke-regression
  prompt: How to tag E2E tests as smoke vs regression and run selectively?
  should_trigger: true
  checks:
  - length_min:120
  - no_placeholder
  expectations:
  - Shows @smoke @regression @slow tags
  - Shows --grep commands for selective runs
  tags:
  - e2e
  - tagging
- id: e2e-full-checkout-flow
  prompt: Write a complete E2E test for a checkout flow with mocked Stripe
  should_trigger: true
  checks:
  - length_min:200
  - no_placeholder
  expectations:
  - Uses API seed, mock Stripe, asserts confirmation
  tags:
  - e2e
  - checkout
- id: e2e-role-based-access
  prompt: How to test role-based access control in E2E?
  should_trigger: true
  checks:
  - length_min:120
  - no_placeholder
  expectations:
  - Shows admin vs member user fixtures
  - Tests 403 for unauthorized role
  tags:
  - e2e
  - rbac
- id: e2e-session-expiry
  prompt: How to test session expiry and redirect in E2E?
  should_trigger: true
  checks:
  - length_min:100
  - no_placeholder
  expectations:
  - Uses clock mocking to expire JWT
  - Asserts returnTo redirect param
  tags:
  - e2e
  - auth
---

# E2E Testing Patterns

## 1. Page Object Model (POM)

### Base Class
```typescript
export class BasePage {
  constructor(protected page: Page) {}

  async goto(path: string): Promise<void> {
    await this.page.goto(path, { waitUntil: 'networkidle' });
  }

  async isVisible(selector: string): Promise<boolean> {
    return this.page.locator(selector).isVisible();
  }
}
```

### Concrete Page Class
```typescript
export class DashboardPage extends BasePage {
  readonly heading = this.page.locator('h1[data-testid="dashboard-heading"]');
  readonly newUserBtn = this.page.getByRole('button', { name: 'Add User' });
  readonly userTable = this.page.locator('[data-testid="user-table"]');

  async clickNewUser(): Promise<UserModalPage> {
    await this.newUserBtn.click();
    return new UserModalPage(this.page);
  }
}
```

### Selector Priority
1. `data-testid` — stable, owned by tests
2. `role + name` — semantic, accessible
3. `aria-label` — contextual
4. CSS selectors — last resort

---

## 2. Test Fixtures

```typescript
export interface AuthUser {
  id: string;
  email: string;
  token: string;
  role: 'admin' | 'member';
}

export const authenticatedUser = async ({ page }, use) => {
  const user = await seedUser({ role: 'admin' });
  const token = await generateTestToken(user);
  await page.goto('/login');
  await page.fill('[name="email"]', user.email);
  await page.fill('[name="password"]', 'TestPass123!');
  await page.click('[type="submit"]');
  await page.waitForURL('**/dashboard');
  await use({ ...user, token });
  await logout(page);
};

export const cleanState = async ({ page }, use) => {
  await use();
  await cleanupTestData();
};
```

---

## 3. API-First Setup

```typescript
export async function seedUser(overrides: Partial<User> = {}): Promise<User> {
  const res = await apiClient.post('/test/users', {
    body: {
      email: `test-${Date.now()}@example.com`,
      role: 'member',
      ...overrides,
    },
  });
  return res.json();
}

export async function seedProject(ownerId: string): Promise<Project> {
  return apiClient.post('/test/projects', {
    body: { name: 'Test Project', ownerId, visibility: 'private' },
  }).json();
}

export async function cleanupTestData(): Promise<void> {
  await apiClient.delete('/test/cleanup');
}
```

---

## 4. Visual Regression

```typescript
export async function assertScreenshot(
  page: Page,
  name: string,
  options: { threshold?: number; fullPage?: boolean } = {}
): Promise<void> {
  const threshold = options.threshold ?? 0.3;
  const screenshot = await page.screenshot({ fullPage: options.fullPage ?? false });
  const result = await imageComparison(screenshot, `screenshots/${name}.png`);
  expect(result).toBeLessThan(threshold);
}
```

```bash
UPDATE_SCREENSHOTS=true npx playwright test
```

---

## 5. Network Interception

```typescript
export function mockExternalAPI(page: Page): void {
  page.route('https://api.stripe.com/**', (route) => {
    route.fulfill({
      status: 200,
      body: JSON.stringify({ id: 'mock_sub_123', status: 'active' }),
    });
  });
}

export function mockNetworkError(page: Page, urlPattern: string): void {
  page.route(urlPattern, (route) => route.abort('failed'));
}
```

---

## 6. Mobile Responsive Testing

```typescript
const devices = [
  { name: 'iPhone 12', width: 390, height: 844 },
  { name: 'iPad Pro', width: 1024, height: 1366 },
  { name: 'Desktop HD', width: 1920, height: 1080 },
];

for (const device of devices) {
  test(`responsive layout ${device.name}`, async ({ page }) => {
    await page.setViewportSize({ width: device.width, height: device.height });
    await page.goto('/dashboard');
    await expect(page.locator('nav')).toBeVisible();
    if (device.width < 768) {
      await page.click('[aria-label="Open menu"]');
    }
  });
}
```

---

## 7. Accessibility Audits

```typescript
export async function runAxeAudit(page: Page, context: string): Promise<void> {
  const results = await new AxeBuilder({ page }).analyze();
  if (results.violations.length > 0) {
    const critical = results.violations.filter(v => v.impact === 'critical');
    expect(critical, `${context} a11y violations: ${JSON.stringify(results.violations)}`).toHaveLength(0);
  }
}
```

### Common Violations Checklist
- Missing alt on img
- Missing aria-label on icon-only buttons
- Color contrast < 4.5:1
- Missing form labels
- Focus trap not working in modals

---

## 8. CI/CD Integration

### Playwright Config
```json
{
  "reporter": [["github-actions"], ["html"]],
  "retries": 2,
  "workers": 4,
  "timeout": 30000,
  "max-failures": 1,
  " shard": ["1/3", "2/3", "3/3"]
}
```

### GitHub Actions
```yaml
- name: E2E Tests
  run: npx playwright test --shard=${{ matrix.shard }}
  matrix:
    shard: [1/3, 2/3, 3/3]
  env:
    CI: true
    MAX_FAILURES: 1
```

### Retry Flaky
```typescript
test.describe.configure({ retries: 2, mode: 'parallel' });
```

---

## 9. Test Data Cleanup

```typescript
let testUserId: string;

test.beforeEach(async () => {
  const user = await seedUser();
  testUserId = user.id;
});

test.afterEach(async () => {
  await deleteUser(testUserId);
  await cleanupOrphanedProjects();
});
```

### Isolated DB per Test
```typescript
test.describe.serial('user management', () => {
  const db = createFreshDB();

  test.beforeAll(async () => {
    await db.migrate();
    await db.seed();
  });

  test.afterAll(async () => {
    await db.drop();
  });
});
```

---

## 10. Tagging Strategy

```typescript
test.describe('@smoke', () => {
  test('login works', async ({ page }) => { /* ... */ });
});

test.describe('@regression', () => {
  test('all features work', async ({ page }) => { /* ... */ });
});

test.describe('@slow', () => {
  test('export 10k rows to CSV', async ({ page }) => { /* ... */ });
});
```

```bash
npx playwright test --grep "@smoke"
npx playwright test --grep "@regression"
npx playwright test --grep "@smoke|@slow"
```

---

## Quick Reference

```bash
npx playwright test
npx playwright test --grep "@smoke"
npx playwright test --headed
npx playwright test --trace=on
UPDATE_SCREENSHOTS=true npx playwright test
npx playwright show-report
```

---

## Checklist

- [ ] POM: one class per page, no selectors in tests
- [ ] Fixtures: reuse authenticated user across tests
- [ ] Seed: API-first, never UI-clicks for setup
- [ ] Visual: baseline screenshots in VCS
- [ ] Network: mock all external services
- [ ] Mobile: test 375px, 768px, 1920px
- [ ] A11y: axe-core on every major page
- [ ] CI: retries=2, shards, max-failures=1
- [ ] Cleanup: before/after hooks, isolated DB
- [ ] Tags: @smoke @regression @slow
