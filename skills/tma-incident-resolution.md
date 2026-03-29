# TMA INCIDENT RESOLUTION SKILL

## META
- name: tma-incident-resolution
- version: 1.0.0
- trigger: production_incident, degraded_service, p1_critical, p2_high, p3_medium, p4_low
- timeout: 30min default, 5min for P1

## INCIDENT CLASSIFICATION P1-P4

| P | Label | RTO | RPO | Response | Examples |
|---|-------|-----|-----|----------|----------|
| P1 | CRITICAL | 15min | 0min | Immediate all-hands | Data breach, full outage, data loss |
| P2 | HIGH | 1hr | 15min | 15min lead time | Partial outage, performance degradation |
| P3 | MEDIUM | 4hr | 1hr | 1hr business hours | Non-critical bug, feature broken |
| P4 | LOW | 24hr | 24hr | Next sprint | Cosmetic, minor UX issue |

## TRIAGE WORKFLOW

```
1. DETECT → acknowledge incident channel
2. CLASSIFY → assign P1-P4 within 2min
3. COMMUNICATE → post initial status, update every 15min (P1/P2)
4. MITIGATE → apply fastest containment first
5. DIAGNOSE → root cause within SLA
6. RESOLVE → deploy fix or rollback
7. VALIDATE → confirm service restored
8. ESCALATE → if SLA breached or resources insufficient
```

## ROOT CAUSE ANALYSIS: 5 WHYS

```
SYMPTOM: [observed failure]

WHY? #1 → [immediate cause]
WHY? #2 → [contributing factor]
WHY? #3 → [systemic cause]
WHY? #4 → [process gap]
WHY? #5 → [root cause]

ROOT CAUSE CATEGORY:
- [ ] CODE: bug in source, logic error
- [ ] CONFIG: misconfigured env, feature flag
- [ ] INFRA: network, compute, storage failure
- [ ] DATA: corruption, migration error, volume spike
- [ ] DEPENDENCY: upstream API, library, service
- [ ] PROCESS: missing guardrail, insufficient testing

REMEDIATION:
- Immediate: [containment action]
- Short-term: [fix within 1 sprint]
- Long-term: [prevent recurrence]
```

## HOTFIX TDD SEQUENCE

### PHASE 1: RED (Reproduce)
```
- Write MINIMAL failing test reproducing bug
- Test MUST fail before any fix
- Commit with msg: "RED: reproduce incident #INC-XXX"
```

### PHASE 2: GREEN (Minimal Fix)
```
- Implement SMALLEST fix passing test
- NO refactoring, NO feature additions
- Commit with msg: "GREEN: minimal fix #INC-XXX"
```

### PHASE 3: VERIFY (Regression)
```
- Run full test suite
- Check no new failures introduced
- Deploy to staging, validate behavior
- Commit with msg: "VERIFY: regression check #INC-XXX"
```

### HOTFIX RULES
- Branch: `hotfix/INC-XXX-brief-desc`
- Review: expedited 2-approval
- Deploy: immediate after CI green
- Monitor: 30min post-deploy dashboard

## ROLLBACK DECISION MATRIX

| Condition | Action |
|-----------|--------|
| Fix deploy >15min and P1 | IMMEDIATE rollback |
| New error rate > baseline 2x | Rollback + halt |
| Feature flag available | Toggle off, investigate |
| DB migration irreversible | STOP, escalate to architect |
| Multi-region partial failure | Isolate region, continue fix |
| Rollback fails | Escalate to on-call SRE |

### ROLLBACK PROCEDURE
```
1. STOP traffic to affected version
2. Revert to last known good deployment
3. Validate health checks pass
4. Confirm error rate returns to baseline
5. Notify incident channel
6. Document rollback reason
```

## POST-MORTEM TEMPLATE

```markdown
# Incident Post-Mortem: INC-XXX

## SUMMARY
- Date: YYYY-MM-DD HH:MM-HH:MM UTC
- Duration: Xh Ym
- P-Level: P1
- Impact: [user count, revenue, SLA breach]

## TIMELINE
| Time | Event |
|------|-------|
| HH:MM | Alert fired |
| HH:MM | Incident acknowledged |
| HH:MM | Root cause identified |
| HH:MM | Fix deployed |
| HH:MM | Service restored |

## ROOT CAUSE
[5 whys analysis]

## CONTRIBUTING FACTORS
- Factor 1
- Factor 2

## REMEDIATION
| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|
| Fix code | @dev | YYYY-MM-DD | DONE |
| Add test | @qa | YYYY-MM-DD | DONE |
| Update runbook | @sre | YYYY-MM-DD | DONE |

## WHAT WENT WELL
- Bullet points

## WHAT WENT POORLY
- Bullet points

## ACTION ITEMS
- [ ] Action 1
- [ ] Action 2

## SIGN-OFF
- @lead
- @reviewer
- Date: YYYY-MM-DD
```

## SLA TRACKING

### RESPONSE SLA
| P | Acknowledge | Escalate If |
|---|------------|-------------|
| P1 | 5min | 10min no ack |
| P2 | 15min | 30min no ack |
| P3 | 1hr | 4hr no ack |
| P4 | 24hr | 48hr no ack |

### RESOLUTION SLA
| P | Target | Hard Deadline |
|---|--------|---------------|
| P1 | 1hr | 4hr |
| P2 | 4hr | 24hr |
| P3 | 48hr | 7d |
| P4 | 7d | 30d |

### ESCALATION PATH
```
P1: On-call → Team Lead → VP Eng → CTO (15min intervals)
P2: On-call → Team Lead → Engineering Manager
P3: Team Lead → EM (SLA+50%)
P4: Next sprint planning
```

## AUTO-HEAL PATTERNS

### PATTERN 1: Circuit Breaker
```
TRIGGER: Error rate >5% in 2min OR latency p99 >2s
ACTION: Open circuit, return cached fallback
RECOVERY: 30s probe, 10% traffic, scale to 100%
```

### PATTERN 2: Auto-Scale Restart
```
TRIGGER: Memory >85% OR CPU >90% for 3min
ACTION: Graceful restart of affected pods
RECOVERY: Confirm health check pass within 5min
```

### PATTERN 3: DB Connection Pool Reset
```
TRIGGER: Connection errors >10 in 1min
ACTION: Flush pool, reconnect with backoff
RECOVERY: Validate with probe query
```

### PATTERN 4: Feature Flag Rollback
```
TRIGGER: Error rate spike correlated with flag change
ACTION: Disable feature flag immediately
RECOVERY: Validate error rate returns to baseline
```

### PATTERN 5: Cached Response Fallback
```
TRIGGER: Upstream API timeout >5s
ACTION: Serve stale cache with warning header
RECOVERY: Background refresh, alert if cache miss
```

### AUTO-HEAL GUARDRAILS
- Max 3 auto-heal attempts per incident
- Auto-heal disabled during active incident channel
- All auto-heal events logged and visible in dashboard
- Post-incident review for every auto-heal trigger

## INCIDENT CHANNELS

| Environment | Channel | Bridge |
|-------------|---------|--------|
| Production | #incidents-production | PagerDuty |
| Staging | #incidents-staging | Slack |
| Security | #incidents-security | PagerDuty +加密 |

## EVAL CASES

### EVAL 1: P1 Database Outage
```
SCENARIO: Primary DB instance unreachable, replication lag 0
TRIAGE: P1 confirmed
EXPECTED: Immediate failover to replica, investigate primary
AUTO-HEAL: Circuit breaker returns cached data
```

### EVAL 2: P2 API Latency Spike
```
SCENARIO: p99 latency >5s, error rate 3%
TRIAGE: P2 confirmed
EXPECTED: Identify slow queries, scale horizontally
HOTFIX: Add query index, deploy via TDD RED-GREEN-VERIFY
```

### EVAL 3: P1 Data Breach Indicator
```
SCENARIO: Unusual read patterns on user table, no deployment
TRIAGE: P1 confirmed
EXPECTED: Isolate affected service, preserve logs, escalate security
ROLLBACK: Not applicable, forensic investigation first
```

### EVAL 4: P3 Feature Regression
```
SCENARIO: New checkout flow failing for EU users
TRIAGE: P3 confirmed
EXPECTED: Write failing test, minimal fix, verify regression suite
POST-MORTEM: Required within 48hr
```

### EVAL 5: P2 Dependency Failure
```
SCENARIO: Third-party payment API returning 503
TRIAGE: P2 confirmed
EXPECTED: Enable circuit breaker, queue transactions
AUTO-HEAL: Circuit breaker pattern triggers
ROLLBACK: Revert any recent payment code changes
```

### EVAL 6: P1 Rollback Cascade
```
SCENARIO: Hotfix deploy causing 500 errors on 20% of requests
TRIAGE: P1 confirmed
EXPECTED: Immediate rollback decision per matrix
ROLLBACK: Execute rollback procedure, validate health
POST-MORTEM: Root cause in migration script
```

### EVAL 7: P4 Technical Debt
```
SCENARIO: Inconsistent error messages across API
TRIAGE: P4 confirmed
EXPECTED: Schedule in next sprint, no hotfix
POST-MORTEM: Not required for P4
```

### EVAL 8: P2 Migration Failure
```
SCENARIO: Data migration script corrupting 0.1% of records
TRIAGE: P2 confirmed
EXPECTED: STOP migration, assess damage, clean recovery
ROLLBACK: Restore from backup, replay migration fixed
AUTO-HEAL: Not applicable, manual intervention required
```

### EVAL 9: P1 Cascading Failure
```
SCENARIO: Service A fails, triggering Service B timeout, causing full outage
TRIAGE: P1 confirmed
EXPECTED: Isolate Service A, prevent cascade, restore B
5-WHY: Root cause in missing circuit breaker on A
```

### EVAL 10: P3 Configuration Drift
```
SCENARIO: Feature flag misconfigured, affecting 5% of users
TRIAGE: P3 confirmed
EXPECTED: Correct flag, verify fix, document drift source
HOTFIX: Update config management, no code change
```

### EVAL 11: P2 Security Patch Required
```
SCENARIO: Library CVE disclosed, no active exploitation detected
TRIAGE: P2 confirmed (time-bound vulnerability)
EXPECTED: Patch within 24hr, verify no breaking changes
ROLLBACK: Revert patch if breaking, re-patch after fix
```

### EVAL 12: P1 Performance Degradation
```
SCENARIO: System responding but latency 10x normal, SLA breach imminent
TRIAGE: P1 confirmed
EXPECTED: Identify bottleneck (CPU/memory/IO), scale or optimize
AUTO-HEAL: Auto-scale pattern triggers
HOTFIX: Query optimization or caching layer
```

### EVAL 13: P3 User Report Storm
```
SCENARIO: 50+ user reports of login issue, error rate 2%
TRIAGE: P3 (P2 if trending up)
EXPECTED: Validate scope, identify root cause
ROLLBACK: Not triggered, investigate first
```

### EVAL 14: P2 Scheduled Maintenance Window
```
SCENARIO: Maintenance causing 5min expected downtime
TRIAGE: P2 planned
EXPECTED: Pre-communicate, monitor, post-validate
ROLLBACK: Abort maintenance if issues arise
```

### EVAL 15: P1 Cloud Provider Failure
```
SCENARIO: AWS/GCP region outage affecting production
TRIAGE: P1 confirmed
EXPECTED: Failover to alternate region, communicate externally
AUTO-HEAL: Multi-region failover pattern
ROLLBACK: N/A - provider issue, wait for recovery
```
