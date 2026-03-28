---
name: tdd-mastery
description: 'Guides the agent through strict Test-Driven Development using the Red-Green-Refactor
  cycle. Use this skill whenever writing new features, fixing bugs, or refactoring
  code that requires test coverage. The agent writes failing tests FIRST, then implements
  minimal code to pass, then refactors while keeping tests green.

  '
metadata:
  category: testing
  triggers:
  - when user asks to write tests before code
  - when user asks to implement a feature with TDD
  - when user asks to fix a bug and wants a regression test
  - when user mentions red-green-refactor
  - when test coverage needs to increase
version: 1.3.0
eval_cases:
- id: tdd-new-feature
  prompt: "TDD RED phase is done. Here is the failing test:\n\n```python\nimport pytest\n\
    from finance import compound_interest\n\ndef test_compound_interest_basic():\n\
    \    result = compound_interest(principal=1000, rate=0.05, years=3)\n    assert\
    \ abs(result - 1157.625) < 0.01  # 1000 * (1.05)^3\n\ndef test_compound_interest_zero_years():\n\
    \    assert compound_interest(principal=500, rate=0.1, years=0) == 500.0\n```\n\
    \nThis test FAILS because `compound_interest` doesn't exist yet.\nNow show the\
    \ GREEN phase (write the minimal implementation to pass both tests)\nand then\
    \ the REFACTOR phase (improve code while keeping tests green).\nDo NOT rewrite\
    \ the tests — just write the implementation.\n"
  should_trigger: true
  checks:
  - regex:def compound_interest|def calculate_compound
  - regex:return.*principal|return.*rate|return.*\*\*|\(1.*rate\)
  - regex:refactor|REFACTOR|clean|improve|docstring|type hint
  - length_min:100
  expectations:
  - 'Shows GREEN phase: writes minimal compound_interest() with actual formula (principal
    * (1+rate)**years)'
  - Does NOT rewrite the tests — just implements the function
  - 'Shows REFACTOR phase: adds type hints, docstring, or error handling'
  tags:
  - basic
  - python
- id: tdd-bug-regression
  prompt: 'There''s a bug: get_user(0) returns None instead of raising ValueError.
    Fix it with TDD.

    Show: RED phase (failing test), GREEN phase (minimal fix), result.

    Do NOT use pass or TODO anywhere — write the actual implementation.

    '
  should_trigger: true
  checks:
  - regex:def test_.*user|class Test.*User|test_get_user
  - regex:ValueError|raises
  - regex:get_user
  - regex:raise ValueError|pytest.raises
  expectations:
  - Writes a failing test reproducing the bug FIRST (test_get_user_raises_for_zero
    or similar)
  - Test uses pytest.raises(ValueError) or assertRaises(ValueError)
  - Implementation uses 'raise ValueError' for id=0 — actual code, not a stub
  tags:
  - bug
  - regression
- id: tdd-no-trigger-doc
  prompt: Write documentation for a REST API endpoint that returns a list of users.
  should_trigger: false
  checks: []
  expectations:
  - produces API documentation without forcing Red-Green-Refactor cycle
  tags:
  - negative
- id: tdd-typescript-green-phase
  prompt: "TDD RED phase complete. You have this failing test for a TypeScript function:\n\
    \n```typescript\nimport { parseISO, differenceInDays } from \"./date-utils\";\n\
    \ntest(\"differenceInDays returns 0 for same date\", () => {\n  const date1 =\
    \ new Date(\"2024-01-01\");\n  const date2 = new Date(\"2024-01-01\");\n  expect(differenceInDays(date1,\
    \ date2)).toBe(0);\n});\n\ntest(\"differenceInDays returns positive for future\
    \ date\", () => {\n  const date1 = new Date(\"2024-01-01\");\n  const date2 =\
    \ new Date(\"2024-01-10\");\n  expect(differenceInDays(date1, date2)).toBe(9);\n\
    });\n```\n\nNow show GREEN phase: write ONLY the minimal implementation to pass\
    \ these tests.\nDo NOT refactor — just make them pass.\n"
  should_trigger: true
  checks:
  - regex:function differenceInDays|const differenceInDays
  - regex:Math\.abs|Date\.getTime|getTime\(\)
  - not_regex:import.*vitest|describe\(|it\(
  - length_min:60
  expectations:
  - Writes minimal implementation using Date getTime() or similar
  - Does NOT modify the tests
  - Returns absolute difference in days
  tags:
  - green
  - typescript
- id: tdd-go-refactor-phase
  prompt: "GREEN phase done. Current implementation passes all tests:\n\n```go\nfunc\
    \ CalculateArea(width, height float64) float64 {\n    return width * height\n\
    }\n```\n\nNow do the REFACTOR phase: improve this code. Add input validation,\n\
    documentation, and consider edge cases. Keep all tests passing.\nRun tests after\
    \ your changes.\n"
  should_trigger: true
  checks:
  - regex:func CalculateArea|func.*Area
  - regex:width <= 0|height <= 0|if.*<=\s*0|error
  - regex:doc|comment|// |/**
  - length_min:120
  expectations:
  - Adds validation for zero/negative dimensions
  - Adds Godoc comment or similar documentation
  - Returns (float64, error) tuple or panics gracefully
  - Keeps tests passing
  tags:
  - refactor
  - go
- id: tdd-edge-empty-collection
  prompt: 'Implement a sum_of_squares function in Python using strict TDD.

    Show RED phase (failing tests including empty list, single element),

    GREEN phase (minimal implementation), then REFACTOR.


    Empty list should return 0, single element should return element squared.

    '
  should_trigger: true
  checks:
  - regex:test.*empty|test.*single|test.*one
  - regex:return 0|== \[\]|len\(.*\)\s*==\s*0
  - regex:sum|x\*\*2|x \* x
  - length_min:150
  expectations:
  - 'RED: writes tests for empty list, single element, normal case'
  - 'GREEN: minimal implementation handling edge cases'
  - 'REFACTOR: clean implementation with possible list comprehension'
  tags:
  - edge
  - python
  - math
- id: tdd-string-reverse-bug
  prompt: 'There''s a bug: reverse_string("hello") returns "olleh" but reverse_string("")

    crashes with IndexError. Fix this using TDD.


    Show RED phase (failing test for empty string), GREEN phase (fix),

    and verify with REFACTOR.

    '
  should_trigger: true
  checks:
  - regex:test.*empty|test.*edge
  - regex:if.*==\s*["']["']|len\(.*\)\s*==\s*0
  - regex:return ["']|return ""
  - not_regex:TODO|pass\s*$
  expectations:
  - 'RED: writes test that calls reverse_string("")'
  - 'GREEN: adds if not s: return "" or similar guard'
  - Fixes the IndexError without breaking existing functionality
  tags:
  - bug
  - edge
  - python
- id: tdd-typescript-mocking
  prompt: 'TDD RED phase: write a test for a UserService that sends a welcome email

    on registration. Mock the EmailClient using Vitest.


    Test should verify send() is called with correct parameters.

    Do NOT write implementation yet.

    '
  should_trigger: true
  checks:
  - regex:vi\.mock|vi\.fn|mock\(
  - regex:UserService|class UserService
  - regex:expect.*send|toHaveBeenCalled
  - not_regex:export function|export class
  - length_min:100
  expectations:
  - Mocks EmailClient with vi.mock()
  - Test calls service.register() and asserts email sent
  - No implementation code — RED phase only
  tags:
  - red
  - typescript
  - mocking
- id: tdd-python-context-manager
  prompt: 'Implement a FileHandler class in Python using TDD that can be used with
    `with` statement.

    RED: write tests for open, read, close, and exception during read.

    GREEN: implement minimal __enter__ and __exit__.

    REFACTOR: add proper error handling.

    '
  should_trigger: true
  checks:
  - regex:def __enter__|def __exit__
  - regex:with.*FileHandler|with open
  - regex:test.*context|test.*with
  - not_regex:class FileHandler:|pass
  - length_min:150
  expectations:
  - 'RED: tests for successful read and exception handling'
  - 'GREEN: minimal context manager protocol implementation'
  - 'REFACTOR: adds buffering, encoding, or error propagation'
  tags:
  - green
  - python
  - oop
- id: tdd-go-concurrency
  prompt: 'Write a Go function `IncrementCounter(counter *int64, wg *sync.WaitGroup)`
    using TDD.

    RED: write tests for concurrent access (launch goroutines, increment, verify final
    value).

    GREEN: implement with proper synchronization.

    Do NOT use mutex yet — just show the data race problem first.

    '
  should_trigger: true
  checks:
  - regex:wg\.Add|wg\.Done|wg\.Wait
  - regex:go func|increment
  - regex:\*int64|atomic\.
  - not_regex:fmt\.Print|log\.Print
  - length_min:120
  expectations:
  - 'RED: writes test launching multiple goroutines'
  - 'GREEN: uses atomic.AddInt64 or sync.Mutex'
  - Demonstrates understanding of concurrency testing
  tags:
  - green
  - go
  - concurrency
- id: tdd-rust-generics
  prompt: 'Write a Rust function `largest<T: PartialOrd>(list: &[T]) -> T` using TDD.

    RED: write tests with i32 slice and f64 slice.

    GREEN: minimal generic implementation.

    REFACTOR: use std::cmp::Ordering or Iterator.

    '
  should_trigger: true
  checks:
  - regex:fn largest|fn largest<T>
  - 'regex:T: PartialOrd|where T:'
  - regex:test.*i32|test.*f64|test.*generic
  - not_regex:fn largest\(\s*\)\s*\{
  - length_min:130
  expectations:
  - 'RED: separate tests for integer and float slices'
  - 'GREEN: generic function using PartialOrd bound'
  - 'REFACTOR: clean implementation, possibly with Iterator'
  tags:
  - green
  - rust
  - generics
- id: tdd-negative-pure-design
  prompt: Draw an ER diagram for a blog database schema with users, posts, and comments.
  should_trigger: false
  checks: []
  expectations:
  - Produces ER diagram without TDD phases
  - No test code written
  tags:
  - negative
  - database
- id: tdd-typescript-async
  prompt: 'Write an async function fetchUserData(userId: string): Promise<User>

    using TDD. RED: write tests with mocked fetch, test loading state,

    test not-found case (404). GREEN: minimal implementation returning mock data.

    '
  should_trigger: true
  checks:
  - regex:async|await|Promise
  - regex:fetch.*mock|mock.*fetch|global\.fetch
  - regex:test.*404|test.*not.?found
  - not_regex:return user;
  - length_min:120
  expectations:
  - 'RED: mocks globalThis.fetch and tests success/404 cases'
  - 'GREEN: returns Promise resolving to User or throws'
  - Proper async/await usage in tests
  tags:
  - red
  - typescript
  - async
- id: tdd-python-decorator
  prompt: 'Write a Python decorator `retry(max_attempts: int)` using TDD.

    RED: write tests where function fails twice then succeeds, and where it fails
    always.

    GREEN: minimal decorator implementation.

    REFACTOR: add exponential backoff.

    '
  should_trigger: true
  checks:
  - regex:@retry|def retry|decorator
  - regex:test.*retry|test.*attempt
  - 'regex:except|try:'
  - not_regex:pass\s*$
  - length_min:150
  expectations:
  - 'RED: tests verify retry logic and eventual success/failure'
  - 'GREEN: decorator wraps function and retries on exception'
  - 'REFACTOR: adds sleep between retries or exponential backoff'
  tags:
  - green
  - python
  - decorator
- id: tdd-go-slice-filter
  prompt: 'Implement a FilterSlice function in Go that takes a []int and a predicate
    func(int) bool.

    Use TDD. RED: write tests for filtering evens, filtering > 10.

    GREEN: minimal implementation.

    REFACTOR: make it generic with comparable constraint.

    '
  should_trigger: true
  checks:
  - regex:func FilterSlice|func Filter
  - regex:func\(.*int.*bool|func\(i int\)
  - regex:test.*even|test.*filter
  - not_regex:fmt\..*Print
  - length_min:120
  expectations:
  - 'RED: tests check filtered output length and contents'
  - 'GREEN: loops and appends matching elements'
  - 'REFACTOR: uses generics (Go 1.18+)'
  tags:
  - green
  - go
  - generics
- id: tdd-python-property
  prompt: 'Write a Temperature class in Python with celsius/fahrenheit property conversion
    using TDD.

    RED: tests for T(0).celsius == 0, T(32).celsius == 0, T(100).celsius == 37.78
    approx.

    GREEN: minimal class with property getters/setters.

    REFACTOR: add validation for absolute zero.

    '
  should_trigger: true
  checks:
  - regex:class Temperature|@property
  - regex:test.*celsius|test.*fahrenheit
  - regex:-273\.15|absolute.zero|ValueError
  - not_regex:return temp
  - length_min:150
  expectations:
  - 'RED: tests for freezing point (0C/32F), boiling (100C/212F)'
  - 'GREEN: property getters compute conversion formulas'
  - 'REFACTOR: validates -273.15C boundary'
  tags:
  - green
  - python
  - oop
- id: tdd-typescript-union-types
  prompt: 'Write a TypeScript function processInput(input: string | number | null):
    string

    using TDD. RED: write tests for string passthrough, number squared, null returns
    "empty".

    GREEN: minimal implementation with type guards.

    Do NOT use any: type.

    '
  should_trigger: true
  checks:
  - 'regex:string \| number \| null|input: string'
  - regex:typeof|instanceof|if \(
  - regex:test.*null|test.*string|test.*number
  - not_regex:any\b|Any\b
  - length_min:120
  expectations:
  - 'RED: tests cover all three input type branches'
  - 'GREEN: uses typeof or explicit type narrowing'
  - Function signature uses proper union type, not any
  tags:
  - green
  - typescript
---

# TDD Mastery

This skill enables the agent to practice strict Test-Driven Development across TypeScript/Vitest,
Rust, and Python/pytest. The agent never writes implementation code without a failing test first.

## Use this skill when

- Implementing new features or functions
- Fixing bugs (write a failing test that reproduces the bug first)
- Refactoring existing code (ensure tests exist before changing)
- User explicitly asks for TDD or test-first approach
- Increasing test coverage on existing modules

## Do not use this skill when

- Writing quick prototype/spike code explicitly marked as throwaway
- The task is purely configuration (no logic to test)
- Writing documentation only

## Instructions

### The Red-Green-Refactor Cycle

Every feature follows three strict phases:

#### 1. RED — Write a Failing Test

Write the test BEFORE any implementation. The test must:

- Describe the expected behavior clearly in the test name
- Follow Arrange-Act-Assert (AAA) pattern
- Fail for the RIGHT reason (not a syntax error)

```typescript
// TypeScript + Vitest example
import { describe, it, expect } from "vitest";
import { calculateDiscount } from "./pricing";

describe("calculateDiscount", () => {
  it("should apply 10% discount for orders over $100", () => {
    // Arrange
    const orderTotal = 150;
    const discountTier = "standard";

    // Act
    const result = calculateDiscount(orderTotal, discountTier);

    // Assert
    expect(result).toBe(135);
  });

  it("should return original price for orders under $100", () => {
    const result = calculateDiscount(50, "standard");
    expect(result).toBe(50);
  });

  it("should throw for negative amounts", () => {
    expect(() => calculateDiscount(-10, "standard")).toThrow("Amount must be positive");
  });
});
```

```rust
// Rust example
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn calculates_discount_for_large_orders() {
        let result = calculate_discount(150.0, DiscountTier::Standard);
        assert_eq!(result, 135.0);
    }

    #[test]
    #[should_panic(expected = "Amount must be positive")]
    fn rejects_negative_amounts() {
        calculate_discount(-10.0, DiscountTier::Standard);
    }
}
```

```python
# Python + pytest example
import pytest
from pricing import calculate_discount

def test_applies_10_percent_discount_over_100():
    result = calculate_discount(150, "standard")
    assert result == 135

def test_returns_original_price_under_100():
    assert calculate_discount(50, "standard") == 50

def test_rejects_negative_amounts():
    with pytest.raises(ValueError, match="Amount must be positive"):
        calculate_discount(-10, "standard")
```

#### 2. GREEN — Write Minimal Code to Pass

Implement ONLY what's needed to make the failing test pass. No extra features, no premature optimization.

```typescript
export function calculateDiscount(amount: number, tier: string): number {
  if (amount < 0) throw new Error("Amount must be positive");
  if (amount > 100 && tier === "standard") {
    return amount * 0.9;
  }
  return amount;
}
```

#### 3. REFACTOR — Improve Without Changing Behavior

With green tests as safety net, improve:

- Extract constants/enums
- Remove duplication
- Improve naming
- Simplify logic

Run tests after EVERY refactor step. If any test fails, revert immediately.

### Mocking Strategies

Use mocks ONLY when:

- External services (APIs, databases)
- Non-deterministic behavior (dates, random)
- Slow dependencies (file system, network)

```typescript
import { vi, describe, it, expect, beforeEach } from "vitest";
import { UserService } from "./user-service";
import { EmailClient } from "./email-client";

vi.mock("./email-client");

describe("UserService", () => {
  let service: UserService;
  let mockEmailClient: EmailClient;

  beforeEach(() => {
    mockEmailClient = {
      send: vi.fn().mockResolvedValue({ success: true }),
    } as unknown as EmailClient;
    service = new UserService(mockEmailClient);
  });

  it("should send welcome email on registration", async () => {
    await service.register("user@example.com", "password123");

    expect(mockEmailClient.send).toHaveBeenCalledWith({
      to: "user@example.com",
      template: "welcome",
    });
  });
});
```

### Coverage Enforcement

- Target: **80% minimum** line coverage, **70% minimum** branch coverage
- Run coverage after each feature: `vitest run --coverage`
- Never skip edge cases: null, undefined, empty strings, boundary values
- Test error paths as thoroughly as happy paths

### Test Naming Convention

Use descriptive names that read like specifications:

- `it('should reject passwords shorter than 8 characters')`
- `it('returns empty array when no results match filter')`
- `test_raises_permission_error_for_non_admin_users`

## Output Format

When applying TDD, output each phase clearly:

```
## RED Phase
[Test code that fails]
Expected failure: [description]

## GREEN Phase
[Minimal implementation]
All tests passing: ✅

## REFACTOR Phase
[Improved code]
All tests still passing: ✅
Coverage: XX%
```

## Anti-patterns

- **NEVER** write implementation before the test
- **NEVER** write a test that passes immediately (it proves nothing)
- **NEVER** mock everything — prefer real implementations for value objects and pure functions
- **NEVER** skip the refactor phase — technical debt accumulates
- **NEVER** test implementation details (private methods, internal state) — test behavior
- **NEVER** use `test.skip()` or `@pytest.mark.skip` without a linked issue/ticket
- **NEVER** write tests without assertions (test must assert something meaningful)
- **NEVER** copy-paste tests — use parameterized tests for similar cases
