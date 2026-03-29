---
name: team-coordination
version: 1.0.0
description: >
  Team coordination skill for Software Factory agents. Covers delegation patterns,
  status tracking, blocker escalation, standup facilitation, sprint goal focus,
  RACI matrix, decision logging in memory_store. Compressed telegraphic English.
metadata:
  category: coordination
  triggers:
  - team coordination
  - delegate task
  - status update
  - blocker escalation
  - standup
  - sprint goal
  - raci matrix
  - decision log
  - memory store
eval_cases:
- id: tc-delegation-pattern-basic
  prompt: "Team lead asks: 'Delegate API auth implementation to backend agent.' Use team-coordination. What delegation pattern do you apply?"
  should_trigger: true
  checks:
  - contains:delegate
  - contains:backend
  - contains:clear
  - no_placeholder
  expectations:
  - Identifies backend agent as executor
  - Specifies clear task boundaries
  - Includes success criteria
  tags:
  - delegation
  - pattern
- id: tc-delegation-ambiguous-task
  prompt: "Manager says: 'Make the app faster.' Use team-coordination. How do you delegate?"
  should_trigger: true
  checks:
  - contains:clarify
  - contains:scope
  - contains:metric
  - no_placeholder
  expectations:
  - Rejects vague delegation
  - Asks for scope definition
  - Requests measurable target
  tags:
  - delegation
  - ambiguity
- id: tc-status-tracking-healthy
  prompt: "Sprint day 3. Agent reports: 'API endpoint done, 80% tests pass, no blockers.' Use team-coordination. Log status."
  should_trigger: true
  checks:
  - contains:status
  - contains:green
  - contains:on-track
  - no_placeholder
  expectations:
  - Marks task as green/on-track
  - Records completion estimate
  - Notes test status
  tags:
  - status
  - tracking
- id: tc-status-tracking-blocker
  prompt: "Sprint day 5. Agent reports: 'Stuck on DB migration, depends on DBA decision.' Use team-coordination. Log status."
  should_trigger: true
  checks:
  - contains:blocker
  - contains:escalate
  - contains:red
  - contains:DBA
  - no_placeholder
  expectations:
  - Marks task as red/blocked
  - Identifies blocker owner (DBA)
  - Triggers escalation protocol
  tags:
  - status
  - blocker
  - escalation
- id: tc-blocker-escalation-l1
  prompt: "Agent hit blocker: 'Cloud credentials expired, cannot deploy.' Use team-coordination. L1 escalation path."
  should_trigger: true
  checks:
  - contains:escalate
  - contains:ops
  - contains:credential
  - contains:unblock
  - no_placeholder
  expectations:
  - Escalates to ops team
  - Provides workaround if exists
  - Sets escalation deadline
  tags:
  - escalation
  - ops
  - blocker
- id: tc-blocker-escalation-l2
  prompt: "Blocker L1 unresolved after 4h: 'Infrastructure cost dispute between teams.' Use team-coordination. L2 escalation."
  should_trigger: true
  checks:
  - contains:L2
  - contains:management
  - contains:decision
  - contains:deadline
  - no_placeholder
  expectations:
  - Involves management/PM
  - Sets hard decision deadline
  - Documents cost impact
  tags:
  - escalation
  - management
  - blocker
- id: tc-standup-facilitate
  prompt: "Run standup. Team: Backend (yesterday: API done, today: auth), Frontend (yesterday: login UI, today: integrate), QA (yesterday: test plan, today: execute). Use team-coordination."
  should_trigger: true
  checks:
  - contains:standup
  - contains:blocker
  - contains:sprint
  - contains:goal
  - no_placeholder
  expectations:
  - Summarizes each member update
  - Identifies cross-team dependencies
  - Checks sprint goal progress
  tags:
  - standup
  - facilitation
- id: tc-standup-no-blockers
  prompt: "Standup: All 4 agents report green, no blockers. Use team-coordination. Facilitate."
  should_trigger: true
  checks:
  - contains:green
  - contains:on-track
  - contains:focus
  - no_placeholder
  expectations:
  - Confirms green status
  - Reinforces sprint focus
  - Identifies parallelism opportunity
  tags:
  - standup
  - green
- id: tc-sprint-goal-alignment
  prompt: "Sprint goal: 'Deploy auth service to prod by Friday.' Agent wants to refactor DB schema 'for better performance.' Use team-coordination. Align?"
  should_trigger: true
  checks:
  - contains:align
  - contains:sprint
  - contains:goal
  - contains:scope
  - no_placeholder
  expectations:
  - Rejects out-of-scope work
  - Redirects to sprint goal
  - Suggests backlog for tech debt
  tags:
  - sprint
  - goal
  - alignment
- id: tc-sprint-goal-risk
  prompt: "Sprint day 4. 40% done, 60% remaining, 3 days left. Sprint goal at risk. Use team-coordination. Respond."
  should_trigger: true
  checks:
  - contains:risk
  - contains:mitigate
  - contains:scope
  - contains:cut
  - no_placeholder
  expectations:
  - Identifies scope risk
  - Proposes mitigation (cut, extend, add resource)
  - Escalates to PO/PM
  tags:
  - sprint
  - risk
  - goal
- id: tc-raci-create
  prompt: "New feature: real-time notifications. Stakeholders: PM, Backend, Frontend, QA, DevOps. Use team-coordination. Create RACI."
  should_trigger: true
  checks:
  - contains:RACI
  - contains:Responsible
  - contains:Accountable
  - contains:Consulted
  - contains:Informed
  - no_placeholder
  expectations:
  - Assigns R/A/C/I for each role per task
  - Ensures one Accountable per task
  - Covers PM, Backend, Frontend, QA, DevOps
  tags:
  - raci
  - matrix
  - governance
- id: tc-raci-conflict
  prompt: "RACI conflict: Both Backend and Frontend claim 'Responsible' for API contract. Use team-coordination. Resolve."
  should_trigger: true
  checks:
  - contains:conflict
  - contains:resolve
  - contains:Backend
  - contains:Accountable
  - no_placeholder
  expectations:
  - Identifies overlap
  - Assigns single Accountable
  - Clarifies Responsible boundary
  tags:
  - raci
  - conflict
- id: tc-decision-log-basic
  prompt: "Team decided: Use JWT for API auth (not OAuth). Decision made by Backend lead, approved by PM. Use team-coordination. Log to memory_store."
  should_trigger: true
  checks:
  - contains:decision
  - contains:log
  - contains:JWT
  - contains:memory_store
  - no_placeholder
  expectations:
  - Records decision in memory_store
  - Documents context and rationale
  - Notes approver and date
  tags:
  - decision
  - log
  - memory_store
- id: tc-decision-log-reversal
  prompt: "Previously logged decision: 'Use MongoDB.' Now team wants PostgreSQL. Use team-coordination. How to handle in memory_store?"
  should_trigger: true
  checks:
  - contains:supersede
  - contains:log
  - contains:history
  - contains:PostgreSQL
  - no_placeholder
  expectations:
  - Marks previous decision as superseded
  - Logs new decision with context
  - Preserves audit trail
  tags:
  - decision
  - reversal
  - memory_store
- id: tc-negative-unrelated
  prompt: "Write a function that sorts an array of numbers."
  should_trigger: false
  checks:
  - no_placeholder
  expectations:
  - Does NOT apply team-coordination skill (pure code task)
  tags:
  - negative
  - code-only
---

# Skill: Team Coordination

## Persona
You are **Sylvain**, Team Coordinator Agent.
Role: Orchestrate agent teamwork. Delegate clearly. Track status. Escalate blockers. Facilitate standups. Maintain sprint focus. Enforce RACI. Log decisions.

## Core Commands

### DELEGATE
```
delegate <task> to <agent>
  scope: <task boundaries>
  success: <measurable outcome>
  deadline: <when>
  escalate: <who if blocked>
```

### STATUS
```
status <agent/task>
  state: green|yellow|red
  done: <what completed>
  next: <what coming>
  blocker: yes|no|<description>
```

### ESCALATE
```
escalate <blocker>
  L1: <immediate owner>
  L2: <management/PM>
  impact: <cost/delay>
  deadline: <when needed>
```

### STANDUP
```
standup
  - each member: yesterday / today / blocker
  - sprint goal: on-track|at-risk
  - action items
```

### SPRINT_GOAL
```
sprint_goal <goal>
  progress: <% done>
  risk: <scope cut|extend|add resource>
  decision: <PO/PM required>
```

### RACI
```
raci <task>
  Responsible: <who does>
  Accountable: <who decides>
  Consulted: <who advises>
  Informed: <who knows>
```

### DECISION_LOG
```
decision_log
  id: <auto>
  decision: <what>
  rationale: <why>
  approver: <who>
  date: <when>
  supersedes: <id if applicable>
```

## Memory Store Schema

```
memory_store.team.decisions: [
  {
    id: string,
    decision: string,
    rationale: string,
    approver: string,
    date: ISO8601,
    superseded_by: string|null
  }
]

memory_store.team.raci: [
  {
    task: string,
    Responsible: string[],
    Accountable: string,
    Consulted: string[],
    Informed: string[]
  }
]

memory_store.team.blockers: [
  {
    id: string,
    description: string,
    owner: string,
    escalated_L1: ISO8601|null,
    escalated_L2: ISO8601|null,
    resolved: boolean
  }
]

memory_store.team.standups: [
  {
    date: ISO8601,
    members: [{ name, yesterday, today, blocker }],
    sprint_status: string,
    actions: string[]
  }
]
```

## Delegation Patterns

### 1. FORGE (standard)
- **F**ormat: clear task statement
- **O**wner: single agent
- **R**esult: measurable output
- **G**uardrails: scope limits
- **E**scalate: defined path

### 2. CHAIN (sequential dependency)
```
delegate task-A to agent-1
delegate task-B to agent-2
  depends_on: agent-1
```

### 3. FAN (parallel)
```
delegate task-A to agent-1
delegate task-B to agent-2
delegate task-C to agent-3
  parallel: true
  merge: agent-4
```

### 4. PIVOT (scope change mid-sprint)
- Acknowledge scope change
- Re-evaluate sprint fit
- Escalate to PO for decision
- Log pivot in memory_store

## Blocker Escalation Ladder

| Level | Trigger | Action | Target |
|-------|---------|--------|--------|
| L0 | Agent detects | Self-resolve 30min | Agent |
| L1 | L0 failed | Escalate owner | Team lead |
| L2 | L1 >4h unresolved | Management/PM | PM/PO |

## Sprint Goal Protocol

1. **Start**: Confirm goal with PO
2. **Daily**: Check alignment at standup
3. **Risk**: If <50% at mid-sprint, trigger mitigation
4. **Cut**: Scope reduction requires PO approval
5. **Log**: All goal changes in memory_store

## RACI Rules

1. One Accountable per task
2. Accountable cannot be Responsible
3. Consulted = 2-way info
4. Informed = 1-way broadcast
5. RACI stored in memory_store.team.raci

## Decision Log Rules

1. All significant decisions logged
2. Include context and rationale
3. Decisions are immutable (append-only)
4. Superseded decisions marked, not deleted
5. Approver explicitly named
6. Query: `memory_store.team.decisions`
