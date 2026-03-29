# Testing Strategy — code-critic

role: code-critic
scope: test quality, coverage, reliability

---

## TEST PYRAMID

- BASE: unit tests — fast, isolated, 70-80% coverage target
- MID: integration tests — real DB or test containers, 50-60% coverage
- TOP: e2e tests — slow, brittle, minimum viable, 10-20% coverage
- RATIO: 70/20/10 per test type distribution
- each upper layer: fewer tests, higher cost, greater confidence

---

## TDD RED-GREEN-REFACTOR

### RED
- write failing test before any implementation code
- test names: describe behavior, not implementation
- assertion error expected — no production code exists yet

### GREEN
- minimal code to pass the test
- no optimization, no abstraction — just make it work
- all previous tests still pass

### REFACTOR
- clean up code, extract duplication
- tests remain unchanged
- verify all tests green after refactor

### LOOP
- RED: fail -> GREEN: pass -> REFACTOR: improve
- max 5-10 min per cycle
- never skip refactor phase

---

## COVERAGE THRESHOLDS

- UNIT: 80% line coverage minimum, 90% for critical paths
- INTEGRATION: 60% line coverage minimum
- E2E: functional coverage, not line coverage
- BRANCH: 75% minimum for unit tests
- FUNCTION: 100% for public APIs
- CYCLE: enforce via CI gate — fail if below threshold
- EXCEPTION: generated code, one-liners — document why excluded

---

## TEST NAMING CONVENTIONS

### pattern: `describeBehavior_Scenario_ExpectedResult`

```
describeUserAuth
  .whenCredentialsInvalid
    .shouldReturn401

describeOrderTotal
  .whenDiscountApplied
    .shouldCalculateCorrectly
```

### rules
- names: sentence case, no underscores in Describe
- scenario: when/given prefix
- assertion: should/expect prefix
- one concept per test
- no "test" or "it" prefixes — describe framework handles this

### BAD
```
test1, testUser, testOrderTotal1
```

### GOOD
```
describePaymentProcessor
  .whenCardDeclined
    .shouldNotDeductBalance
```

---

## MOCK VS REAL DB

### use MOCK when
- testing business logic, no DB interaction
- need fast feedback, <10ms per test
- testing edge cases, errors that real DB cannot produce
- DB is external service, network-dependent

### use REAL DB (testcontainers, sqlite, h2) when
- testing queries, migrations, schema constraints
- testing ORM behavior, lazy loading, transactions
- integration points with real DB features (triggers, cascades)
- need confidence in actual SQL generated

### guidelines
- MOCK ratio: 80% of unit tests
- REAL DB: only for integration layer
- NEVER mock data access layer in integration tests
- use testcontainers for postgres/mysql/redis in CI
- reset DB state between tests via transactions or fixtures

---

## FIXTURE PATTERNS

### inline fixtures
- small, simple objects
- no dependencies
- directly in test file

### factory fixtures
- parameterized creation
- default values + override capability
- `UserFactory.withName("alice")`

### shared fixtures
- expensive setup, reused across tests
- class or module level
- document thread-safety

### fixture composition
- build complex objects from simple ones
- `OrderFactory.withStandardItems()` -> builds items + user + address

### lifecycle
- setup before test
- teardown after test
- never leak state between tests

### antipatterns
- shared mutable state across tests
- fixtures calling other fixtures with hidden deps
- "god fixtures" doing too much

---

## PROPERTY-BASED TESTING

### concept
- generate random inputs, verify invariants hold
- test hundreds of cases in ms
- discover edge cases humans miss

### when to use
- pure functions with mathematical properties
- serialization/deserialization
- protocol handlers, parsers
- cryptographic operations
- any function with complex input domain

### properties to test
- commutativity: f(a,b) == f(b,a)
- associativity: f(f(a,b),c) == f(a,f(b,c))
- identity: f(a, identity) == a
- idempotence: f(f(a)) == f(a)
- roundtrip: decode(encode(x)) == x
- bounds: output always in expected range

### tools
- JS/TS: fast-check, jsverify
- Python: hypothesis
- Rust: proptest, quickcheck
- Go: testing/quick

### example
```
property("sort is idempotent", () => {
  const arr = arbitrary.array(arbitrary.integer());
  assert.deepEqual(sort(sort(arr)), sort(arr));
});
```

---

## SNAPSHOT TESTING ANTI-PATTERNS

### problems
- tests fail on intentional changes (UI, formatting)
- snapshots become dumping grounds for any output
- no specification of what "correct" means
- easy to update all snapshots with single keystroke
- often mask real bugs

### when snapshot OK
- stable output formats from external APIs
- complex data structures that change rarely
- one-off debugging, not permanent tests

### better alternatives
- semantic assertions: `expect(price).toBe(9.99)` not snapshot
- schema validation: ajv/zod for data shape
- targeted property tests

### if using snapshots
- git blame each snapshot line
- require PR approval for snapshot changes
- keep snapshots small (<50 lines)
- separate snapshot directory per component

---

## FLAKY TEST DETECTION

### symptoms
- tests pass locally, fail CI
- tests fail randomly with no code changes
- tests pass on rerun
- tests related to time, async, or external services

### root causes
- async race conditions
- test order dependencies
- shared mutable state
- network timeouts not configured
- sleep instead of proper wait
- hardcoded timestamps
- random data colliding

### detection strategies
- repeat tests N times (5-10) — if fails once, flaky
- run tests in random order — detect order deps
- monitor pass rate per test over time
- log flaky tests to metrics

### fixes
- async: use proper synchronization, not sleep
- order deps: use test isolation, cleanup in afterEach
- time: freeze system time, use test clocks
- network: configure timeouts, use recorded responses
- shared state: each test creates own data

### CI configuration
```
flaky_tests:
  retry: 3
  tracking: per-test pass rate
  quarantine: >20% failure rate after fixes
```

---

## EVAL_CASES

### eval:1 — pyramid compliance
```
code: calculates discount, DB call hidden in service layer
ask: how to test discount calculation
expect: mock DB, pure unit test, pyramid correct
```

### eval:2 — TDD cycle
```
code: empty module, requirement: add(a,b) returns sum
ask: write test first
expect: RED phase, minimal test, name convention correct
```

### eval:3 — coverage gate
```
code: 60% unit coverage on new module
ask: is this acceptable
expect: reject, need 80% minimum, specific uncovered areas
```

### eval:4 — naming
```
code: test("test1") { ... }
ask: improve naming
expect: describe-behavior pattern, semantic name
```

### eval:5 — mock vs real
```
code: mock entire repository for unit test
ask: is this correct
expect: yes for unit, but integration test must use real DB
```

### eval:6 — fixture quality
```
code: one fixture builds entire order graph
ask: critique
expect: too large, break into factory composition
```

### eval:7 — property testing need
```
code: URL parser with 50 specific test cases
ask: how to reduce test count
expect: property-based testing, test invariants
```

### eval:8 — snapshot antipattern
```
code: snapshot tests for entire API response JSON
ask: is this good
expect: no, semantic assertions, snapshot only if truly stable
```

### eval:9 — flaky diagnosis
```
code: test sometimes fails on CI, passes locally
ask: root cause and fix
expect: race condition, async issue, or shared state
```

### eval:10 — integration test DB
```
code: unit tests use real postgres via testcontainer
ask: is this appropriate
expect: no, unit tests should use mocks, real DB for integration only
```

### eval:11 — refactor phase skip
```
code: all tests pass but code is messy
ask: next step
expect: refactor phase, tests unchanged, code improved
```

### eval:12 — property roundtrip
```
code: serialize/deserialize for JSON, XML, protobuf
ask: what to property test
expect: roundtrip: decode(encode(x)) == x for all inputs
```

---

## IMPLEMENTATION CHECKLIST

- [ ] CI gate enforces coverage thresholds
- [ ] unit tests use mocks, not real DB
- [ ] integration tests use testcontainers or sqlite/h2
- [ ] test naming follows describe-behaviour pattern
- [ ] TDD cycle documented in team runbook
- [ ] flaky test tracking enabled
- [ ] snapshot tests reviewed, minimal usage
- [ ] property-based tests for pure function modules
- [ ] fixture factories documented and isolated
- [ ] test isolation verified via random order runs
