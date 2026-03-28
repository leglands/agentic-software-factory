---
name: sf-guide
version: "1.0.0"
description: >
  Context-aware guidance skill. Reads current project state (running missions,
  completed phases, pending work) and recommends what to do next. Used by the
  guide agent and the 'sf guide' CLI command. Inspired by BMAD /bmad-help.
metadata:
  category: meta
  scope: "SF platform — project context guidance"
  triggers:
    - "when asked what to do next"
    - "when a user seems lost or unsure of the next step"
    - "when a project phase has just completed"
    - "when invoked via 'sf guide' CLI command"
  source: >
    Inspired by BMAD /bmad-help (MIT) — adapted for SF autonomous agent platform.
    BMAD ref: https://github.com/bmad-code-org/BMAD-METHOD
    Adaptation: rule-based + LLM synthesis instead of pure LLM, integrated with
    SF mission store, workflow catalog, and complexity levels.
eval_cases:
  - id: lost-user-no-context
    prompt: "I just installed the platform, what should I do?"
    checks:
      - "regex:project|workflow|start|create|begin"
      - "length_min:80"
      - "no_placeholder"
    expectations:
      - "suggests creating a project first"
      - "mentions at least one concrete workflow name"
      - "does NOT assume advanced knowledge"
    tags: ["basic", "onboarding"]
  - id: post-architecture
    prompt: "sf guide I just finished the architecture document, what next?"
    checks:
      - "regex:epic|stories|implementation|workflow|next"
      - "length_min:80"
      - "no_placeholder"
    expectations:
      - "suggests implementation or epics/stories creation"
      - "mentions a concrete workflow or agent"
      - "references the architecture context in the response"
    tags: ["context-aware"]
  - id: complexity-guidance
    prompt: "sf guide quick bug fix, very simple change"
    checks:
      - "regex:simple|skip|lightweight|quick|minimal|straightforward"
      - "length_min:50"
      - "no_placeholder"
    expectations:
      - "suggests simple complexity level"
      - "mentions that heavyweight planning phases are skipped for simple tasks"
    tags: ["scale-adaptive"]
  - id: post-deployment-issues
    prompt: "sf guide We just deployed and users are reporting errors. The mission is still in monitoring phase."
    checks:
      - "regex:error|incident|diagnos|revert|monitor|alert|rollback|hotfix"
      - "length_min:80"
      - "no_placeholder"
    expectations:
      - "recommends incident-diagnosis or error-monitoring workflow"
      - "acknowledges the monitoring phase context"
      - "suggests concrete next step (rollback, diagnose, or create epic)"
      - "does NOT suggest starting a new project or ideation"
    tags: ["context-aware", "post-deploy"]
  - id: mid-project-scope-change
    prompt: "sf guide We were building the billing module but the client changed requirements mid-sprint. What now?"
    checks:
      - "regex:scope|change|pivot|replan|epic|stories|backlog|client|repriorit"
      - "length_min:80"
      - "no_placeholder"
    expectations:
      - "recommends updating epics/stories to reflect new scope"
      - "suggests re-planning the sprint rather than continuing on old scope"
      - "mentions concrete workflow (epic-decompose or feature-sprint)"
      - "acknowledges the wasted work context compassionately"
    tags: ["context-aware", "pivot"]
  - id: multi-project-priority
    prompt: "sf guide I have 3 active projects and 2 team members. Project A is for client X, Project B is internal tool, Project C is a security fix. What should we focus on?"
    checks:
      - "regex:priorit|security|client|focus|risk|impact|urgent|decay"
      - "length_min:100"
      - "no_placeholder"
    expectations:
      - "ranks security fix as highest priority regardless of size"
      - "uses concrete prioritization reasoning (risk, client impact, decay cost)"
      - "provides a clear focus recommendation for the 2 team members"
      - "does NOT suggest working on all 3 simultaneously"
    tags: ["prioritization", "multi-project"]
  - id: stuck-in-planning-loop
    prompt: "sf guide We've been in planning for 3 weeks, can't agree on architecture. Team is frustrated."
    checks:
      - "regex:planning|stall|architecture|decide|talk|spike|prototype|break"
      - "length_min:80"
      - "no_placeholder"
    expectations:
      - "recognizes this as a planning stall anti-pattern"
      - "recommends scheduling an architecture review or spike"
      - "suggests a concrete decision deadline or RFO process"
      - "does NOT suggest more planning meetings"
    tags: ["anti-pattern", "unstick"]
  - id: post-migration-validation
    prompt: "sf guide We just finished a database migration. The team isn't sure if they should run tests or do a smoke test first."
    checks:
      - "regex:migration|test|validat|smoke|regress|schema|integrat"
      - "length_min:80"
      - "no_placeholder"
    expectations:
      - "recommends running existing tests first to check for regressions"
      - "suggests a smoke test targeting migrated data paths specifically"
      - "mentions monitoring phase follows validation"
      - "does NOT jump ahead to deployment"
    tags: ["context-aware", "post-migration"]
  - id: skill-selection-help
    prompt: "sf guide I need to write automated browser tests for my new feature"
    checks:
      - "regex:playwright|browser|test|e2e|automation|qa|skill"
      - "length_min:80"
      - "no_placeholder"
    expectations:
      - "recommends a testing or browser-automation skill"
      - "mentions specific skill name (e.g. e2e-browser-testing)"
      - "does NOT suggest writing tests from scratch without tooling"
    tags: ["skill-selection"]
  - id: solo-dev-vs-team
    prompt: "sf guide I'm a solo developer building a SaaS product. I don't know what workflows to use."
    checks:
      - "regex:solo|one.person|minimal|lightweight|startup|simple|skip|heavy"
      - "length_min:80"
      - "no_placeholder"
    expectations:
      - "recommends simple complexity level throughout"
      - "suggests skipping heavyweight phases (excess architecture, large team processes)"
      - "mentions specific workflows appropriate for a solo dev"
      - "does NOT assume a large team is available"
    tags: ["scale-adaptive", "solo"]
  - id: error-monitoring-cycle
    prompt: "sf guide We deployed last week and monitoring flagged errors but nobody looked at them. What now?"
    checks:
      - "regex:monitor|error|alert|review|incident|triage|backlog|past.due"
      - "length_min:80"
      - "no_placeholder"
    expectations:
      - "recommends reviewing the monitoring alerts that were missed"
      - "suggests scheduling a triage session for the backlogged alerts"
      - "mentions incident-diagnosis or error-monitoring-cycle workflow"
      - "does NOT suggest deploying again without addressing the alerts"
    tags: ["context-aware", "monitoring"]
  - id: choosing-between-workflows
    prompt: "sf guide Should I use epic-decompose or feature-sprint? I have epics defined but no stories yet."
    checks:
      - "regex:epic.decompose|feature.sprint|stories|planning|which|when"
      - "length_min:80"
      - "no_placeholder"
    expectations:
      - "recommends epic-decompose first (to create stories from epics)"
      - "explains why — feature-sprint needs stories as input"
      - "mentions both workflow names correctly"
      - "does NOT say use both at the same time"
    tags: ["workflow-selection"]
  - id: deadline-pressure
    prompt: "sf guide We have a hard deadline in 3 days. The feature is only 60% done. What do we do?"
    checks:
      - "regex:deadline|3.day|60%|cut|scope|priorit|MVP|pivot|cut.scope"
      - "length_min:80"
      - "no_placeholder"
    expectations:
      - "recommends cutting scope to deliver an MVP in 3 days"
      - "suggests concrete scope cut criteria (lowest user impact, easiest to cut)"
      - "mentions a specific workflow for re-planning under deadline pressure"
      - "does NOT suggest working overtime as the first recommendation"
    tags: ["deadline", "scope-cut"]
  - id: qa-vs-dev-dispute
    prompt: "sf guide The QA phase failed — 40% of tests are failing. The dev team says it's a test data problem, QA says it's a code problem."
    checks:
      - "regex:qa|fail|test|data|disput|escalat|triage|who|responsib"
      - "length_min:80"
      - "no_placeholder"
    expectations:
      - "recommends a concrete triage step before escalation"
      - "suggests running failing tests in isolation to determine root cause"
      - "mentions the appropriate agent or workflow for the dispute"
      - "does NOT take sides — provides a neutral diagnostic path"
    tags: ["conflict-resolution"]
  - id: tech-stack-transition
    prompt: "sf guide We are migrating from a monolith to microservices. Mid-project, team is confused about what to do next."
    checks:
      - "regex:migrat|microservice|monolith|service|split|decompos|phase"
      - "length_min:80"
      - "no_placeholder"
    expectations:
      - "recommends continuing with the decomposition phase"
      - "suggests concrete next steps for the migration (identify bounded contexts, plan service boundaries)"
      - "mentions a specific workflow or agent for the migration work"
      - "acknowledges the mid-project confusion and provides orientation"
    tags: ["context-aware", "migration"]
---

# SF Guide

Reads current project context and recommends what to do next.

Inspired by BMAD `/bmad-help` — context-aware, not just a static checklist.

---

## Your Role

You are a **context-aware navigator**. Given:
- What's currently running (missions, phases)
- What just completed
- The user's stated context (if any)

...recommend the **most useful next 3 steps** concisely.

---

## Phase Navigation (SF Lifecycle)

```
1. Ideation / Analysis
   → Workflow: ideation-to-prod (phase 1) or create-product-brief
   → Agents: po, metier, analyst

2. Planning / Requirements
   → Workflow: epic-decompose, feature-sprint (phase plan)
   → Agents: po, pm, architecte

3. Architecture / Design
   → Workflow: feature-sprint (phase solution) or architecture-review
   → Agents: architecte, lead-dev, ux

4. Implementation
   → Workflow: feature-sprint (phase dev) or cicd-pipeline
   → Agents: dev-1..dev-N, lead-dev, qa
   → Skills: tdd.md, clean-code.md

5. QA / Validation
   → Workflow: test-campaign, skill-eval
   → Agents: qa, test_automation
   → Skills: qa-adversarial-llm.md

6. Deployment
   → Workflow: canary-deployment (1%→10%→50%→100%)
   → Agents: sre, devops

7. Monitoring / Iteration
   → Workflow: error-monitoring-cycle, skill-evolution
   → Agents: monitoring-ops, rte
```

---

## Complexity Levels (Scale-Adaptive)

When recommending workflows, suggest the appropriate complexity:

| Situation | complexity= | Effect |
|---|---|---|
| Bug fix, small change | `simple` | Skips heavyweight planning phases |
| Feature, standard sprint | `standard` | Default — all standard phases |
| New product, enterprise migration | `enterprise` | All phases including arch review, risk assessment |

Phrases that signal simple: "quick", "small", "bug", "fix", "minor"
Phrases that signal enterprise: "new product", "platform migration", "large team", "compliance"

When launching: `sf$ workflows launch feature-sprint complexity=simple`

---

## Response Format

Keep recommendations to 3-5 actionable steps. Be specific:

**Good:**
> 1. Launch `feature-sprint` workflow with complexity=standard
> 2. Assign `architecte` + `lead-dev` to the solutioning phase
> 3. Run `skill-eval` on `tdd.md` before the dev phase

**Bad:**
> You should think about your next steps carefully and plan appropriately.

---

## When You Don't Know

If context is unclear, ask ONE clarifying question:
- "Is this a new feature, a bug fix, or a product from scratch?"
- "Is this for a solo dev or a team of 5+?"

Do not ask multiple questions at once.
