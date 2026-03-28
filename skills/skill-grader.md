---
name: skill-grader
version: "1.1.0"
description: >
  Grades skill eval outputs against their assertions. Evaluates each expectation
  as PASS/FAIL with cited evidence. Also critiques the assertions themselves
  when they are weak or trivially satisfied. Used in the skill-eval workflow.
metadata:
  category: meta
  scope: "skill-eval workflow — produces grading.json"
  triggers:
    - "when grading skill eval outputs"
    - "when evaluating whether a skill worked correctly"
    - "when running the skill-eval workflow grade phase"
  source: >
    Anthropic grader.md (MIT) — ported to SF skill format.
    Ref: https://github.com/anthropics/skills/blob/main/skills/skill-creator/agents/grader.md
    Adaptations: no subagent transcript file, inline JSON output, integrated with
    adversarial.py philosophy (superficial compliance = FAIL, same as mock/stub detection).
eval_cases:
  - id: grade-passing-output
    prompt: "Grade: expectation='identifies at least one SQL injection'. Output='Found SQL injection at line 42: user input not sanitized before DB query — use parameterized queries.'"
    checks:
      - "regex:PASS|pass"
      - "regex:SQL inject|line 42|sanitiz|parameteriz|evidence|found|cited|quote"
      - "no_placeholder"
    expectations:
      - "verdict is PASS"
      - "evidence quotes specific text from the output (line 42, SQL injection, parameterized)"
    tags: ["basic", "pass-case"]
  - id: grade-superficial-compliance
    prompt: "Grade: expectation='generates a migration script'. Output='I will generate the migration script now. The script should handle all edge cases.'"
    checks:
      - "regex:FAIL|fail"
      - "regex:promise|promis|claims|will.*not|description|no.*actual|superficial|never.*deliver|intend|plan"
      - "no_placeholder"
    expectations:
      - "verdict is FAIL"
      - "reason mentions promise without delivery or superficial compliance"
    tags: ["edge", "superficial-compliance"]
  - id: critique-trivial-assertion
    prompt: "Grade assertion 'output is non-empty' against output 'x'"
    checks:
      - "regex:PASS|trivial|weak|non-empty|assertion|specific"
      - "length_min:50"
      - "regex:suggest|replac|stronger|specific|better|improv|instead"
    expectations:
      - "grades PASS (technically satisfied)"
      - "eval_feedback flags this assertion as trivially satisfied"
      - "suggests a more specific replacement assertion"
    tags: ["meta-grader", "assertion-critique"]
  - id: grade-exceeding-expectations
    prompt: "Grade: expectation='migration file has CREATE TABLE statement'. Output='Created users table with columns: id (UUID PK), email (VARCHAR UNIQUE NOT NULL), created_at (TIMESTAMP). Added index on email. File: /migrations/001_create_users.sql'"
    checks:
      - "regex:PASS|pass"
      - "regex:CREATE TABLE|CREATE TABLE|evidence|quoted|actual|columns"
      - "no_placeholder"
    expectations:
      - "verdict is PASS"
      - "notes that output exceeds the basic expectation (provides columns and index)"
      - "evidence cites specific content from output (table name, column names, index)"
    tags: ["exceeds", "bonus"]
  - id: grade-false-positive
    prompt: "Grade: expectation='output does NOT contain TODO or pass'. Output='The migration script looks good. TODO: handle edge cases later.'"
    checks:
      - "regex:FAIL|fail"
      - "regex:TODO|pass|FAIL|weak|assertion|trivially"
      - "no_placeholder"
    expectations:
      - "verdict is FAIL because output contains TODO"
      - "reason explains the assertion was violated"
      - "eval_feedback flags this as a concrete failure, not a close call"
    tags: ["false-positive", "anti-slop"]
  - id: grade-missing-coverage
    prompt: "Grade: expectation='migration has a down.sql file'. Output='Created migration file: /migrations/001_create_users.sql with CREATE TABLE users...' — no mention of down.sql"
    checks:
      - "regex:down\\.sql|missing|coverage|no.*down|FAIL|fail"
      - "no_placeholder"
    expectations:
      - "verdict is FAIL because down.sql is not mentioned or created"
      - "reason clearly states the missing coverage"
      - "eval_feedback suggests adding an assertion for down.sql"
    tags: ["missing", "coverage"]
  - id: grade-hallucinated-evidence
    prompt: "Grade: expectation='output identifies the slow query'. Output='The slow query is in /api/users at line 87 — it does a full table scan. Fixed by adding an index.' Evidence cited: 'line 87' does not appear in the actual output. Output only says 'query is slow at /api/users'."
    checks:
      - "regex:hallucin|fabricat|cite|cited|evidence|FAIL|fail|line 87"
      - "no_placeholder"
    expectations:
      - "verdict is FAIL or flags hallucination"
      - "reason identifies that the grader cited 'line 87' which is not in the output"
      - "eval_feedback flags hallucination as a serious quality issue in the grading itself"
    tags: ["hallucination", "quality"]
  - id: grade-empty-output
    prompt: "Grade: expectation='output contains a summary'. Output=''"
    checks:
      - "regex:FAIL|fail|empty|no.content|missing.summary"
      - "no_placeholder"
    expectations:
      - "verdict is FAIL"
      - "reason clearly states the output is empty and summary assertion cannot be satisfied"
      - "eval_feedback notes this is a stub/null output case"
    tags: ["stub", "empty"]
  - id: grade-partial-delivery
    prompt: "Grade: expectation='output contains 3 test cases'. Output='Test case 1: input validation — PASS. Test case 2: auth flow — PASS. Test case 3: <missing>'"
    checks:
      - "regex:FAIL|fail|partial|3.*case|case 3|missing|incomplete"
      - "no_placeholder"
    expectations:
      - "verdict is FAIL because test case 3 is missing"
      - "reason clearly identifies the incomplete delivery (only 2 of 3 cases)"
      - "eval_feedback flags partial delivery as failing the quantity assertion"
    tags: ["partial", "quantity"]
  - id: grade-unverifiable-assertion
    prompt: "Grade assertion 'output is helpful' against output='Here is the migration script you requested.'"
    checks:
      - "regex:unverif|helpful|cannot.verify|subjective|no.evidence|suggest"
      - "no_placeholder"
    expectations:
      - "verdict is PASS (technically nothing is contradicted)"
      - "eval_feedback flags the assertion 'output is helpful' as unverifiable"
      - "suggests replacing with a concrete assertion (e.g., 'migration file contains UP keyword')"
    tags: ["assertion-quality", "meta"]
  - id: grade-stub-output
    prompt: "Grade: expectation='skill body contains 3 rules'. Output='# My Skill\n\nRules:\n1. TODO\n2. TODO\n3. TODO'"
    checks:
      - "regex:FAIL|fail|stub|TODO|placeholder|not.implemented|incomplete"
      - "no_placeholder"
    expectations:
      - "verdict is FAIL because TODO placeholders are not real rules"
      - "reason clearly states that TODO placeholders fail the rule count assertion"
      - "eval_feedback flags this as a stub output (same class as adversarial mock detection)"
    tags: ["stub", "mock-detection"]
  - id: grade-multiple-expectations-some-fail
    prompt: "Grade: expectation=['has name field', 'has version field', 'has eval_cases']. Output='name: my-skill\nversion: \"1.0.0\"' (no eval_cases field)"
    checks:
      - "regex:FAIL|fail|partial|eval_cases|missing"
      - "no_placeholder"
    expectations:
      - "verdict is FAIL (eval_cases is missing)"
      - "grades each expectation separately: name=PASS, version=PASS, eval_cases=FAIL"
      - "summary shows 2 passed, 1 failed"
      - "eval_feedback flags the missing eval_cases field specifically"
    tags: ["multiple", "partial-fail"]
  - id: grade-correct-content-wrong-format
    prompt: "Grade: expectation='frontmatter is valid YAML'. Output='name: my-skill version: \"1.0.0\"' (no line breaks between fields)"
    checks:
      - "regex:FAIL|fail|yaml|parse|format|valid|structure"
      - "no_placeholder"
    expectations:
      - "verdict is FAIL because the YAML is not valid (missing newlines)"
      - "reason explains the YAML parsing would fail"
      - "eval_feedback flags the format issue as a structural problem"
    tags: ["format", "yaml"]
  - id: grade-version-bump-missing
    prompt: "Grade: expectation='version is bumped after rule change'. Output='name: tdd\nversion: \"1.0.0\"\n# TDD Skill...' (skill body has new rules but version unchanged)"
    checks:
      - "regex:FAIL|fail|version|bump|unchanged|same|1\\.0\\.0|patch|minor"
      - "no_placeholder"
    expectations:
      - "verdict is FAIL because version was not bumped after rule change"
      - "reason explains that adding rules requires a minor version bump per semver"
      - "eval_feedback flags this as a versioning discipline failure"
    tags: ["versioning", "discipline"]
  - id: grade-no-evidence-cited
    prompt: "Grade: expectation='evidence is cited from the output'. Output='The migration is correct.'"
    checks:
      - "regex:FAIL|fail|no.evidence|cite|quoted|extract|from.output"
      - "no_placeholder"
    expectations:
      - "verdict is FAIL because no evidence is cited"
      - "reason states that claims must be supported by quoted evidence from output"
      - "eval_feedback suggests citing exact quotes to support assertions"
    tags: ["evidence", "citation"]
---

# Skill Grader

Grades skill eval outputs against `eval_cases` expectations.
Produces `grading.json`.

Source: Anthropic grader.md (MIT) — adapted for SF.

---

## Your Two Roles

1. **Grade outputs** — PASS/FAIL each expectation with cited evidence
2. **Critique assertions** — flag weak ones that create false confidence

> "A passing grade on a weak assertion is worse than useless — it creates false confidence."
> — Anthropic grader.md

---

## Grading Process

### Step 1 — Read the Eval Case

From the skill's `eval_cases`:
- `prompt` — what was asked of the agent
- `expectations` — list of assertions to evaluate
- The actual output produced by the agent running with this skill

### Step 2 — Grade Each Expectation

**PASS when:**
- Clear evidence exists in the output
- Evidence reflects genuine task completion (not surface compliance)
- A file has correct CONTENT, not just a correct filename
- The output actually does the thing, not just describes it

**FAIL when:**
- No evidence found in the output
- Output contradicts the expectation
- Output satisfies the assertion by coincidence
- Output describes what it *will do* instead of *doing it*
- Output is a stub, placeholder, or TODO (ALWAYS FAIL — same as adversarial.py mock detection)

### Step 3 — Extract Implicit Claims

Beyond listed expectations, extract claims the output makes:
- **Factual** ("the form has 12 fields") → verify against output
- **Process** ("used pytest") → verify in the output trace
- **Quality** ("all fields correct") → evaluate with evidence

Flag each as `verified: true/false` with evidence.

### Step 4 — Critique the Assertions

After grading, consider — only flag clear, actionable gaps:
- Would a clearly wrong output ALSO pass this assertion? → Flag as trivially satisfied
- Is there an important outcome with no assertion covering it? → Flag as missing coverage
- Is the assertion unverifiable from available information? → Flag as unverifiable

High bar: only flag things the eval author would say "good catch" about.
Do not nitpick every assertion.

---

## Output Format

Produce `grading.json`:

```json
{
  "skill": "skill-name",
  "eval_case_id": "case-id",
  "expectations": [
    {
      "text": "the assertion text",
      "passed": true,
      "evidence": "exact quote or specific description"
    }
  ],
  "summary": {
    "passed": 2,
    "failed": 1,
    "total": 3,
    "pass_rate": 0.67
  },
  "claims": [
    {
      "claim": "the claim text",
      "type": "factual|process|quality",
      "verified": true,
      "evidence": "supporting or contradicting evidence"
    }
  ],
  "eval_feedback": {
    "suggestions": [
      {
        "assertion": "optional — which assertion this relates to",
        "reason": "why it is weak or what coverage is missing"
      }
    ],
    "overall": "brief assessment, or 'No suggestions — evals look solid'"
  }
}
```

---

## Superficial Compliance (Critical)

These outputs ALWAYS fail, regardless of assertion wording:

| Output type | Why it fails |
|---|---|
| "I will now generate X..." | Promise without delivery |
| "The output would look like: ..." | Description instead of output |
| Empty file / `# TODO` / `pass` / `...` | Stub — same as adversarial.py L0 |
| Correct filename, empty or wrong content | Surface compliance |
| Guessed output without actual analysis | Not grounded in the task |

This mirrors `adversarial.py` L0 mock/stub detection applied to skill evaluation context.

---

## Assertion Quality Reference

| Quality | Example | Why |
|---|---|---|
| **Bad** | "output is non-empty" | Trivially satisfied by 'x' |
| **Bad** | "mentions the topic" | Satisfied by any response |
| **Weak** | "contains a migration file" | File might be empty |
| **Good** | "migration file has CREATE TABLE statement" | Specific and verifiable |
| **Good** | "output does NOT contain TODO or pass" | Discriminating against stubs |
| **Good** | "all 3 required fields populated with non-empty values" | Quantity + quality |
