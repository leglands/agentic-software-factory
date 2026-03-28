---
name: skill-creator
version: "1.1.0"
description: >
  Creates and improves SF agent skills. Follows a draft → eval → grade → iterate
  quality loop: write the skill, define eval_cases, run them via skill-eval workflow,
  grade with skill-grader, and refine. Every new skill gets eval_cases.
metadata:
  category: meta
  scope: "SF platform skills (skills/*.md)"
  triggers:
    - "when creating a new skill"
    - "when a user asks to add agent capability"
    - "when improving or updating an existing skill"
    - "when a skill produces poor or inconsistent outputs"
  source: >
    Anthropic skill-creator pattern (MIT) — adapted for SF YAML/markdown format.
    Ref: https://github.com/anthropics/skills/tree/main/skills/skill-creator
    Adaptations: no .skill packaging, no claude -p CLI, eval_cases embedded in
    frontmatter (not evals.json), grading via skill-grader skill,
    loop via skill-eval workflow (platform/workflows/definitions/skill-eval.yaml).
eval_cases:
  - id: create-basic-skill
    prompt: "Create a skill for generating database migration scripts"
    checks:
      - "regex:name:|version:|eval_cases:|triggers:"
      - "length_min:200"
      - "no_placeholder"
    expectations:
      - "skill has valid YAML frontmatter with name, version, description"
      - "frontmatter includes metadata.triggers with 3+ entries"
      - "frontmatter includes eval_cases with 2+ test cases"
      - "skill body defines concrete rules not vague guidelines"
      - "at least one rule has a bad/good example"
    tags: ["basic", "creation"]
  - id: improve-existing-skill
    prompt: "The tdd skill produces test stubs without assertions — write the complete improved skill .md file"
    checks:
      - "regex:NEVER|MUST|PROHIBITED|assertion|version:"
      - "length_min:200"
      - "no_placeholder"
    expectations:
      - "outputs a complete .md skill file with YAML frontmatter (name/version/eval_cases)"
      - "adds explicit prohibition against stubs using NEVER or MUST keyword"
      - "increments version in the frontmatter (e.g. 1.0.0 → 1.1.0)"
      - "adds at least one eval_case targeting the stub anti-pattern"
    tags: ["improvement", "anti-slop"]
  - id: weak-assertion-detection
    prompt: "Write eval_cases for a skill that formats JSON output"
    checks:
      - "not_regex:output is non-empty|output exists"
      - "regex:key|field|schema|structure|specific|format"
      - "length_min:100"
      - "no_placeholder"
    expectations:
      - "does NOT include 'output is non-empty' as an expectation"
      - "does NOT include 'output exists' as an expectation"
      - "expectations reference specific JSON keys or structure"
    tags: ["meta-eval", "assertion-quality"]
  - id: anti-slop-detection
    prompt: "Write a skill that extracts data from JSON APIs. The skill must ensure agents never hardcode or mock API responses."
    checks:
      - "regex:NEVER|MUST|avoid|slop|mock|stub|fake|hardcode|real"
      - "regex:name:|version:|eval_cases:|triggers:"
      - "length_min:200"
      - "no_placeholder"
    expectations:
      - "skill body contains explicit anti-slop rules (NEVER mock data, NEVER hardcode responses)"
      - "has a bad/good example pair showing the difference between real and fake API handling"
      - "includes an eval_case that tests the agent won't mock the API response"
      - "frontmatter is valid YAML with name, version, description, eval_cases, triggers"
    tags: ["anti-slop", "api"]
  - id: multi-agent-handoff
    prompt: "Write a skill for the handoff moment when a QA agent finishes testing and a dev agent needs to fix the bugs"
    checks:
      - "regex:handoff|transition|context|pass|badge|evidence|bug.list|quality"
      - "length_min:200"
      - "no_placeholder"
    expectations:
      - "skill defines clear boundary between QA phase output and dev phase input"
      - "includes format for passing test evidence (screenshots, error logs, reproduction steps)"
      - "has a rule preventing the dev agent from re-running QA without closing the loop"
      - "includes an eval_case where handoff is done correctly with bug list and evidence"
      - "frontmatter has at least 3 triggers covering the handoff context"
    tags: ["multi-agent", "handoff"]
  - id: security-skill-constraints
    prompt: "Write a skill that helps agents handle secrets and credentials — it must never log or expose secrets"
    checks:
      - "regex:secret|credential|token|log|expos|mask|NEVER|MUST|redact|env"
      - "length_min:200"
      - "no_placeholder"
    expectations:
      - "has explicit NEVER rule against logging or displaying secrets"
      - "has a MUST rule about masking secrets in output (e.g., *** for last 4 chars)"
      - "has a bad/good example showing secret handling in error messages"
      - "includes an eval_case that tests an agent trying to log a secret — must fail or mask it"
    tags: ["security", "secrets"]
  - id: skill-with-missing-version-bump
    prompt: "The existing skill 'tdd.md' was updated to add a new rule, but the version was not bumped. Write the correct version of the skill frontmatter."
    checks:
      - "regex:version.*1\\.1\\.0|version.*minor|patch|increas|changelog"
      - "length_min:100"
      - "no_placeholder"
    expectations:
      - "bumps version from prior version to a higher minor/patch version"
      - "includes a changelog or notes section documenting what changed"
      - "adds an eval_case for the new rule that was introduced"
      - "does NOT leave version unchanged when a rule was added"
      - "does NOT output the full skill body — only the corrected frontmatter"
    tags: ["versioning", "discipline"]
  - id: skill-trigger-misalignment
    prompt: "Write a skill for writing Bash scripts. The skill triggers list says 'when reviewing a PR' and 'when checking code quality' but never 'when writing a script'. What is wrong and fix it?"
    checks:
      - "regex:triggers|script|bash|write|when.doing|context|exact"
      - "length_min:100"
      - "no_placeholder"
    expectations:
      - "identifies that triggers are misaligned with the skill's actual purpose"
      - "fixes triggers to include 'when writing a bash script' and 'when creating a shell script'"
      - "removes misleading triggers about PR review that belong in a code-review skill"
      - "adds at least one eval_case with a prompt that matches the corrected triggers"
    tags: ["triggers", "alignment"]
  - id: ux-skill-constraints
    prompt: "Write a skill for creating UI components. The skill must ensure agents never hardcode colors or pixel values — use design tokens only."
    checks:
      - "regex:design.token|token|color|px|pixel|hardcode|NEVER|MUST|variable|theme"
      - "length_min:200"
      - "no_placeholder"
    expectations:
      - "has explicit NEVER rule against hardcoding colors (e.g. #ff0000) or pixel values"
      - "has a MUST rule to use design tokens from the theme system"
      - "includes a bad/good example: hardcoded #fff vs token(text.primary)"
      - "includes an eval_case that tests an agent trying to use hardcoded pixel values — must fail"
    tags: ["ux", "design-tokens"]
  - id: idempotent-skill-rule
    prompt: "Write a skill for running database migrations. The skill must ensure agents never run a migration twice in production."
    checks:
      - "regex:idempotent|once|only|run.once|duplicate|migration|NEVER|guard|check"
      - "length_min:150"
      - "no_placeholder"
    expectations:
      - "has explicit NEVER rule against running the same migration twice"
      - "has a MUST rule to check migration status before running"
      - "includes a bad/good example: running without check vs checking migrations table first"
      - "includes an eval_case testing that the agent won't run a migration twice"
    tags: ["database", "safety"]
  - id: escalation-skill
    prompt: "Write a skill for when a human engineer must be called in — the agent should never pretend it can fix something beyond its capability."
    checks:
      - "regex:escalat|human|engineer|never.fake|capability|boundary|SAFE|STOP|call"
      - "length_min:150"
      - "no_placeholder"
    expectations:
      - "has a MUST rule to escalate when the agent cannot safely resolve the issue"
      - "has a NEVER rule against pretending to fix something beyond capability"
      - "includes a concrete escalation trigger (e.g., production data loss, security breach)"
      - "includes an eval_case where the agent correctly escalates instead of faking a fix"
    tags: ["safety", "escalation"]
  - id: multi-file-output
    prompt: "Write a skill for generating a full project scaffold (multiple files: package.json, tsconfig.json, README.md, src/index.ts). Output must be complete files, not descriptions."
    checks:
      - "regex:file:|package\\.json|tsconfig|README|scaffold|NEVER|description|complete"
      - "length_min:150"
      - "no_placeholder"
    expectations:
      - "has a NEVER rule against outputting file descriptions instead of actual file content"
      - "has a MUST rule to output complete, syntactically valid file content for each file"
      - "includes an eval_case with a multi-file prompt — each file must be complete"
      - "does NOT output 'package.json would contain...' — must output the actual file"
    tags: ["output", "completeness"]
  - id: test-coverage-requirements
    prompt: "Write a skill that ensures test cases cover happy path AND edge cases. The skill must reject a test suite that only tests the happy path."
    checks:
      - "regex:edge|corner|edge.case|happy.path|coverage|test|NEVER|MUST|reject"
      - "length_min:150"
      - "no_placeholder"
    expectations:
      - "has a NEVER rule against accepting a test suite with only happy path tests"
      - "has a MUST rule requiring at least one edge case test per feature"
      - "includes a bad/good example: only happy path tests vs happy + edge tests"
      - "includes an eval_case testing an agent submitting only happy path — must fail or be rejected"
    tags: ["testing", "coverage"]
  - id: error-handling-constraints
    prompt: "Write a skill for API endpoint handlers. The skill must ensure agents handle errors explicitly — never let exceptions propagate raw to the caller."
    checks:
      - "regex:error|except|catch|raise|propagat|raw|NEVER|MUST|try.except|finally"
      - "length_min:150"
      - "no_placeholder"
    expectations:
      - "has a NEVER rule against letting exceptions propagate unhandled"
      - "has a MUST rule to catch and transform exceptions into structured error responses"
      - "includes a bad/good example: raw exception vs caught and transformed error"
      - "includes an eval_case testing an agent that lets an exception propagate — must fail"
    tags: ["error-handling", "api"]
  - id: version-semver-discipline
    prompt: "Write a skill for API design. You must follow semver. If you add a breaking change without bumping the major version, the skill should fail."
    checks:
      - "regex:semver|version|major|minor|patch|breaking|changelog|NEVER"
      - "length_min:200"
      - "no_placeholder"
    expectations:
      - "has a rule that breaking changes MUST bump major version (X+1.0.0)"
      - "has a NEVER rule against adding breaking changes without version bump"
      - "includes an eval_case with a breaking change — must bump major or fail"
      - "frontmatter version is set appropriately"
    tags: ["versioning", "semver"]
---

# Skill Creator

Creates and evolves SF agent skills via the eval loop:
**Draft → Eval Cases → Execute → Grade → Iterate**.

Source: Anthropic skill-creator (MIT) — adapted for SF.

---

## STEP 1 — Understand the Skill

Before writing, answer:
- **What task does this skill guide?** (concrete, not abstract)
- **What triggers it?** (which LLM tasks, keywords, contexts)
- **What failure modes should it prevent?** (slop, fake data, bad patterns)
- **Who are the consumers?** (which agents, which workflows)

---

## STEP 2 — Write the Skill

### Frontmatter schema

```yaml
name: my-skill
version: "1.0.0"
description: >
  One clear sentence. What the skill does, when to use it.
metadata:
  category: dev | ux | security | ops | meta
  scope: "target files / languages / contexts"
  triggers:
    - "when doing X"
    - "when the task involves Y"
    - "always for Z type of output"
  source: "origin if ported/inspired from external"  # optional
eval_cases:
  - id: happy-path
    prompt: "Ask that triggers the skill naturally"
    expectations:
      - "output contains X"
      - "output does NOT contain Y"
      - "format matches Z"
    tags: ["basic"]
  - id: anti-pattern
    prompt: "Input likely to produce the wrong output"
    expectations:
      - "skill prevents the anti-pattern"
      - "output follows rule X instead"
    tags: ["edge", "anti-pattern"]
```

### Skill body rules

- **Rules, not guidelines** — "NEVER do X" beats "try to avoid X"
- **Concrete bad/good examples** for each rule
- **Explicit rejection criteria** — what output should trigger a retry
- **No meta-commentary** — the skill is read by an LLM agent, not a human
- **Short sections** — max 10 rules, each ≤5 lines

---

## STEP 3 — Write Eval Cases

For each skill, define at minimum:
1. **Happy path** — typical trigger, verifiable output
2. **Anti-pattern case** — input likely to produce the wrong output
3. **Edge case** — boundary condition, ambiguous input (optional but recommended)

### Good expectations (specific, verifiable, discriminating)

| Good | Bad |
|---|---|
| "output contains a SQL injection warning at line 42" | "output identifies a security issue" |
| "migration file starts with `-- Migration:` header" | "migration file is correct" |
| "all 3 required fields are populated with non-empty values" | "fields are populated" |
| "output does NOT contain `TODO` or `pass`" | "output has no stubs" |

An expectation is **discriminating** when:
- A correct output passes it
- An incorrect output fails it
- A trivially empty or placeholder output fails it

An expectation is **trivially satisfied** (don't write these) when:
- Any non-empty output passes it (`output is non-empty`, `response exists`)
- A stub or placeholder passes it (`output mentions the topic`)

---

## OUTPUT RULE — ALWAYS OUTPUT THE COMPLETE FILE

**NEVER** describe changes or list what to fix. **ALWAYS** output the complete `.md` file.

| Mode | WRONG ❌ | RIGHT ✓ |
|---|---|---|
| Creating | "Here's how I'd structure a skill for X..." | Full `---\nname: x\n...---\n# X\n...` |
| Improving | "Add a NEVER rule and bump version to 1.1.0" | Complete improved `.md` with the rule already applied |

When improving a skill you don't have access to: **infer a plausible minimal version** then apply the fix. The output must be a real, runnable `.md` skill file.

---

## STEP 4 — Grade and Iterate

1. Run `skill-eval` workflow with your skill
2. Review `grading.json` — check PASS/FAIL + evidence
3. Read `eval_feedback.suggestions` — grader flags weak assertions
4. Fix failing cases OR tighten assertions if they were wrong
5. Repeat until all eval_cases pass
6. Bump `version` (semver: breaking→major, rule change→minor, typo/fix→patch)

---

## STEP 5 — Commit

```bash
git commit -m "feat(skills): add <name> skill v1.0.0

- triggers: <list main triggers>
- eval_cases: N test cases
- source: <if applicable>

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## Quality Checklist

Before shipping:
- [ ] YAML frontmatter parses without error
- [ ] `eval_cases` has ≥2 test cases
- [ ] Each expectation is specific and verifiable (not trivially satisfied)
- [ ] Skill body has ≥3 rules with at least one concrete bad/good example
- [ ] Version bumped if updating existing skill
- [ ] No meta-commentary in skill body
