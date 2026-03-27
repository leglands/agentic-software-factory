---
name: pm-workflow-playbook
version: "1.0"
description: >
  PM decision playbook: which workflow to launch, when, and why.
  Covers all available briques (phases/workflows) and their triggers.
eval_cases:
  - id: post-sprint-decision
    prompt: "Sprint 3 just completed. Tests pass but code quality score is 72%. What do you launch?"
    checks:
      - "has_keyword:refactoring-sprint"
    expectations:
      - "Recommends refactoring-sprint because quality < 85%"
      - "Does NOT suggest another feature sprint before cleanup"
  - id: security-trigger
    prompt: "A new dependency was added. When should security scan run?"
    checks:
      - "has_keyword:sast-continuous"
    expectations:
      - "Triggers after any dependency change, not just at release"
  - id: new-feature-flow
    prompt: "Client requests a new feature. What's the workflow?"
    checks:
      - "has_keyword:feature-sprint"
      - "has_keyword:epic-decompose"
    expectations:
      - "Uses epic-decompose if complex (>5 files), feature-sprint if simple"
  - id: release-readiness
    prompt: "We want to release next week. What should we run first?"
    checks:
      - "has_keyword:performance-testing"
      - "has_keyword:documentation"
    expectations:
      - "Performance testing + documentation pipeline + security scan before release"
---

# PM Workflow Playbook — Which Brique, When, Why

## Decision Tree

```
New feature request?
  → Simple (<5 files) → feature-sprint
  → Complex (system) → epic-decompose → N x feature-sprint

Sprint completed?
  → Every sprint → code-simplify (automatic, diff-based)
  → Every 3 sprints OR quality < 85% → refactoring-sprint (full hardening)
  → Before release → performance-testing + documentation-pipeline

Quality issue detected?
  → Score < 85% → hardening-sprint (targeted 3 dimensions)
  → Score < 70% → refactoring-sprint (full 6-phase)
  → Security vuln → sast-continuous (immediate)

Maintenance request?
  → Bug fix → tma-maintenance
  → Auto-detected issue → tma-autoheal
  → Tech debt > threshold → tech-debt-reduction

Design change?
  → New component → design-system-component
  → DS audit → refactoring-sprint phase 1 only

Release prep?
  → documentation-pipeline → performance-testing → sast-continuous → canary-deployment
```

## Available Briques (Workflows)

### Feature Development
| Workflow | When | Duration | Agents |
|---|---|---|---|
| `feature-sprint` | Single feature, <5 files | 1-4h | lead+dev+qa+devops |
| `feature-request` | Client/business request | 2-6h | PM+lead+dev+qa |
| `epic-decompose` | Complex system (>5 files) | 30min decompose + N sprints | architect+PM → teams |

### Quality & Refactoring
| Workflow | When | Duration | Agents |
|---|---|---|---|
| `refactoring-sprint` | Every 3 sprints OR quality <85% | 2-4h | 4 audit agents + dev + qa |
| `hardening-sprint` | AC score <85%, targeted | 1-2h | qa+architect+lead |
| `code-simplify` | After each sprint (automatic) | 30min | code-reviewer+lead+qa |
| `tech-debt-reduction` | Debt score > threshold | 2-4h | lead+dev |

### Security
| Workflow | When | Duration | Agents |
|---|---|---|---|
| `sast-continuous` | After dep changes, before release | 1h | securite+devsecops |
| `security-hacking` | Quarterly, before major release | 4-8h | pentest team (8 agents) |

### Testing & Performance
| Workflow | When | Duration | Agents |
|---|---|---|---|
| `performance-testing` | Before release, after perf regression | 2-4h | perf_engineer+sre |
| `test-campaign` | Before release, after major feature | 2-4h | qa_lead+testeur+automation |

### Documentation & Compliance
| Workflow | When | Duration | Agents |
|---|---|---|---|
| `documentation-pipeline` | Before release, after API changes | 1-2h | tech_writer+dev |
| `rse-compliance` | Quarterly, regulatory audit | 2-4h | RSE team |
| `license-compliance` | Before release | 1h | compliance+legal |

### Deployment
| Workflow | When | Duration | Agents |
|---|---|---|---|
| `cicd-pipeline` | Standard deploy | 30min | devops+sre |
| `canary-deployment` | Production deploy (1%→10%→50%→100%) | 2h | devops+sre+qa |

### Mobile
| Workflow | When | Duration | Agents |
|---|---|---|---|
| `mobile-ios-epic` | iOS feature/release | 4-8h | iOS team |
| `mobile-android-epic` | Android feature/release | 4-8h | Android team |

## Automatic Triggers (PM doesn't need to launch)

These run automatically:
- `code-simplify` → after each `feature-sprint` completion (`on_complete`)
- `documentation-pipeline` → after each `feature-sprint` completion (`on_complete`)
- `tma-autoheal` → when watchdog detects issues
- `hardening-sprint` → when AC score drops below 85%

## PM Commands

To launch any workflow:
```
create_mission(name="Refactoring Sprint Q1", goal="Quality hardening", project_id="popinz", workflow_id="refactoring-sprint")
```

To check status:
```
check_run_status(project_id="popinz")
```

## Sprint Cadence Recommendation

```
Sprint 1: feature-sprint → code-simplify (auto)
Sprint 2: feature-sprint → code-simplify (auto)
Sprint 3: feature-sprint → code-simplify (auto) → refactoring-sprint
Sprint 4: feature-sprint → code-simplify (auto)
Sprint 5: feature-sprint → code-simplify (auto)
Sprint 6: feature-sprint → code-simplify (auto) → refactoring-sprint → performance-testing
Release: documentation-pipeline → sast-continuous → canary-deployment
```
