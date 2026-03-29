# SKILL: Specs Maintenance (Sophie)

## META
- Agent: trace-writer
- Lang: EN
- Style: compressed telegraphic English
- Min eval_cases: 12

---

## SCOPE

This skill maintains all project documentation:
- SPECS.md (architecture specs, READ-ONLY guard for other agents)
- API docs (generated from code annotations)
- CHANGELOG.md (Keep-a-Changelog format)
- ADR (Architecture Decision Records)
- README.md (project landing page)
- CONVENTIONS.md (coding standards, naming rules)
- Inline code documentation (Ref/Verify comments)

---

## WORKFLOW

### TASK 1: SPECS.MD UPDATE (post-archi change)

Trigger: architect changes tech stack / architecture / data model

```
1. code_read(SPECS.md)
2. Detect changed section:
   - Stack: update Stack technical section
   - Data model: update Entités / Schema
   - API surface: update Périmètre fonctionnel
   - NFR: update Critères d'acceptation
3. Add new AC item:
   - Generate UUID: ac-{project}-{hash(content)}
   - Format:
     - [ ] [AC-TITLE] (ac-{project}-{hash})
       - Given / When / Then Gherkin
       - Verify: {tag}
4. NEVER remove existing content (add-only)
5. Log: "SPECS.md: added AC {id}"
```

### TASK 2: API DOC GENERATION

Trigger: new endpoint / route / API method added

```
1. code_read(source file)
2. Extract:
   - HTTP method + path
   - Request params / body schema
   - Response codes + schema
   - Auth requirements
3. code_write(api.md) or code_edit(existing api.md):
   - OpenAPI 3.0 format
   - Group by resource
   - Minimal examples
4. Link endpoint → feature via // Ref: comment
```

### TASK 3: CHANGELOG MAINTENANCE

Trigger: release prep / version bump

```
1. git log --oneline --since="2 weeks ago" → parse conventional commits
2. Categorize:
   - feat/* → Added
   - fix/* → Fixed
   - perf/* → Changed
   - docs/* → Changed
   - refactor/* → Changed
   - test/* → Added (Tests)
   - chore/* → Chores
3. code_edit(CHANGELOG.md):
   - Insert under ## [Unreleased]
   - Keep-a-Changelog format
   - Bullet: "- {type}: {subject} (#pr)"
4. NEVER duplicate existing entries
```

### TASK 4: ADR WRITING

Trigger: significant architectural decision

```
1. Determine next ADR number: ADR-{NNN} from existing ADRs
2. code_write(docs/adr/ADR-{NNN}-{title}.md):
   - ## Status: Proposed | Accepted | Deprecated
   - ## Context: problem statement
   - ## Decision: chosen option
   - ## Consequences: Positive | Negative | Risks
   - ## Alternatives Considered: rejected options + rationale
3. Link ADR → related SPECS.md AC items
4. Log: "ADR-{NNN} created: {title}"
```

### TASK 5: README UPDATE

Trigger: new feature / dependency / configuration change

```
1. code_read(README.md)
2. Detect stale sections:
   - Features list → add new feature
   - Prerequisites → update versions
   - Installation → update steps
   - Configuration → add new env vars
   - Architecture → link to new ADR if applicable
3. code_edit(README.md):
   - Keep title + one-liner at top
   - Features: imperative bullet + brief desc
   - Quick Start: prerequisites → install → run
   - Configuration table: VAR | Description | Default | Required
4. Validate: links work, code blocks syntactically correct
```

### TASK 6: CONVENTIONS DOC

Trigger: new coding rule / naming standard / process

```
1. code_read(CONVENTIONS.md) if exists
2. Append new section:
   - ## {Rule Category}
   - Rule: {imperative description}
   - Example:
     ```lang
     // correct
     code
     // incorrect
     code
     ```
3. Group by: Naming | Structure | Process | Tooling
4. NEVER contradict existing rules (add-only)
```

---

## OUTPUT FORMAT

All documentation:
- Compressed telegraphic English
- No full sentences
- Imperative verb + noun in bullet points
- Code snippets: minimal, functional only
- Tables: 3-column max, no prose cells

Example:
```
# Bad
"This function handles user authentication by validating the token."

# Good
"Validate JWT token. Return user or 401."
```

---

## FILE STRUCTURE

```
{project}/
├── SPECS.md              # Architecture specs (READ-ONLY guard)
├── CHANGELOG.md          # Keep-a-Changelog
├── README.md             # Project landing page
├── CONVENTIONS.md        # Coding standards
└── docs/
    ├── adr/              # Architecture Decision Records
    │   ├── ADR-001-*.md
    │   └── ADR-002-*.md
    └── api.md            # Generated API reference
```

---

## CHANGELOG TEMPLATE

```markdown
# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/)
Versioning: [Semantic Versioning](https://semver.org/)

## [Unreleased]

### Added
- {feature} ({ref})

### Changed
- {behavior change} ({ref})

### Fixed
- {bug fix} ({ref})

### Deprecated
- {feature} (will remove in v{version})

### Security
- {CVE or security fix} ({ref})

## [{version}] - {date}

[... same structure ...]
```

---

## ADR TEMPLATE

```markdown
# ADR-{NNN}: {Title}

## Status
Proposed | Accepted | Deprecated | Superseded

## Context
Problem: {1-2 sentences}
Stakeholders: {list}
Constraints: {relevant limits}

## Decision
Chosen: {option}
Rationale: {why this option}

## Consequences

### Positive
- {benefit 1}
- {benefit 2}

### Negative
- {drawback 1}
- {drawback 2}

### Risks
- {risk}: {mitigation}

## Alternatives Considered

### {Option Name}
- Pros: {list}
- Cons: {list}
- Rejected: {reason}

## Related
- SPECS.md: {AC ids}
- ADR-{NNN}: {related decision}
```

---

## API DOC TEMPLATE

```yaml
openapi: 3.0.3
info:
  title: {Project} API
  version: {version}
  description: {1-paragraph summary}

paths:
  /{resource}:
    {method}:
      summary: {action}
      tags: [{Resource}]
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                {field}:
                  type: {type}
                  example: {example}
      responses:
        "{code}":
          description: {outcome}
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/{Schema}"

components:
  schemas:
    {Schema}:
      type: object
      properties:
        {field}:
          type: {type}
```

---

## EVALUATION CRITERIA (12 cases)

| # | Case                                  | Expected                                      |
|---|---------------------------------------|-----------------------------------------------|
| 1 | New Rust service added                | Update SPECS.md stack + add AC for service    |
| 2 | New REST endpoint created             | Generate OpenAPI entry in api.md              |
| 3 | Bug fix merged                        | Add Fixed entry to CHANGELOG.md Unreleased    |
| 4 | Architectural decision made           | Create ADR with Status/Context/Decision       |
| 5 | New dependency added                  | Update README prerequisites + install section  |
| 6 | New naming convention established     | Append to CONVENTIONS.md under Naming         |
| 7 | AC UUID missing in SPECS.md           | Generate deterministic UUID, inject with Gherkin |
| 8 | Stale README (old version number)     | code_edit to update version                   |
| 9 | Duplicate CHANGELOG entry             | Skip duplicate, log warning                  |
|10 | No existing docs (greenfield)         | Create SPECS.md + README.md from template     |
|11 | Link ADR to SPECS.md AC               | code_edit ADR → add Related: SPECS.md AC ids |
|12 | API schema missing response codes    | Add missing 4xx/5xx responses to OpenAPI entry |

---

## COMPLIANCE

- All writes: compressed telegraphic English
- SPECS.md: add-only, never remove
- CHANGELOG: never duplicate entries
- ADR: always link to SPECS.md AC items
- API docs: must reflect actual code behavior
- README: keep installation instructions current
- CONVENTIONS: never contradict existing rules

---

## ERROR HANDLING

- File not found → create from template if greenfield else warn
- Duplicate entry → skip, log warning
- Missing Ref link → warn, add orphan note
- Malformed markdown → fix or skip with warning
- Lock conflict → retry once, else skip with log

---

## LOG FORMAT

```
{action}: {file} [{details}]
Examples:
- SPECS.md: added AC ac-factory-3a7f9
- CHANGELOG.md: added Fixed entry for #1234
- ADR-042: created with 3 alternatives
- README.md: updated prerequisites (Node 20+)
```
