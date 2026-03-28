---
name: incident-diagnosis
version: "1.0.0"
description: >
  Structured root cause analysis (RCA) skill for SF diagnostic agents.
  Covers the full investigation workflow: collect symptoms → correlate →
  hypothesise → confirm → recommend fix. Activate when: something is broken
  or slow, auto-heal hasn't triggered, or the TMA needs a root cause before acting.

eval_cases:
  - input: "The dashboard is taking 8 seconds to load"
    checks:
      - "regex:latency|slow|query|hypothesis|root.?cause|index"
      - "length_min:80"
      - "no_placeholder"
    expect:
      - Runs diag_endpoint_latency on dashboard URL
      - Runs diag_logs to find slow query or error
      - Runs diag_db_stats to check for missing indexes or fragmentation
      - Runs diag_correlate with all findings
      - Produces ranked hypotheses with confidence levels
  - input: "Agents are stuck, missions not progressing"
    checks:
      - "regex:queue|mission|stuck|stall|memory|error"
      - "length_min:80"
      - "no_placeholder"
    expect:
      - Runs diag_queue_depth first
      - Checks for stalled missions (>30min no update)
      - Runs diag_process_stats to check memory/CPU
      - Runs diag_logs on platform container filtering for errors
      - Identifies if it's a queue, memory, or error loop issue
  - input: "Memory is growing over time, suspecting a leak"
    checks:
      - "regex:leak|memory|RSS|tracemalloc|OOM|GC"
      - "length_min:80"
      - "no_placeholder"
    expect:
      - Runs diag_process_stats with include_children=true
      - Notes RSS trend over multiple calls
      - Runs diag_logs filtering for OOM or GC pressure
      - Runs diag_queue_depth to check if backlog is growing
      - Recommends tracemalloc profiling if leak confirmed
  - input: "API is returning 503s intermittently, about 1 in 10 requests fails"
    checks:
      - "regex:503|pool|connection|exhaust|race.condition|timeout|config"
      - "length_min:80"
      - "no_placeholder"
    expect:
      - Runs diag_endpoint_latency to identify 503 pattern
      - Runs diag_db_stats to check connection pool utilization
      - Runs diag_process_stats to check for saturation
      - Runs diag_logs filtering for connection errors or pool full messages
      - Identifies connection pool exhaustion as top hypothesis
      - Recommends increasing pool size or investigating connection leak
  - input: "The notification service is failing, but users report checkout also broke"
    checks:
      - "regex:cascad|downstream|dependency|propagat|fallback|circuit.breaker|notify"
      - "length_min:80"
      - "no_placeholder"
    expect:
      - Runs diag_logs on notification service first
      - Runs diag_endpoint_latency on checkout endpoint
      - Runs diag_logs on checkout service to find dependency errors
      - Identifies cascading failure pattern (notification outage causing checkout failure)
      - Recommends adding circuit breakers or fallback behavior
      - Notes the root cause is the notification service, not checkout
  - input: "Some users see correct data, others see stale or missing data — no errors in logs"
    checks:
      - "regex:stale|cache|inconsist|replication|lag|missing|partial|read.replica"
      - "length_min:80"
      - "no_placeholder"
    expect:
      - Runs diag_db_stats to check replication lag
      - Runs diag_logs with no error filter to look for cache events
      - Runs diag_endpoint_latency on affected endpoint
      - Hypothesizes read replica lag or cache inconsistency
      - Recommends checking replication status or cache TTL settings
      - Notes no errors in logs is consistent with eventual consistency issues
  - input: "Containers are restarting randomly with no OOM in the logs"
    checks:
      - "regex:disk|space|full|no.*OOM|log.rotate|snapshot|volume|container"
      - "length_min:80"
      - "no_placeholder"
    expect:
      - Runs diag_process_stats to check disk utilization
      - Runs diag_logs filtering for disk or volume messages
      - Runs diag_logs with no error filter for restart signals
      - Identifies disk space exhaustion (not OOM) as root cause
      - Recommends log rotation, volume expansion, or snapshot cleanup
      - Notes containers restart when disk is full even without memory pressure
  - input: "Error rate jumped 4x at 14:23 — a deploy happened at 14:20"
    checks:
      - "regex:14:23|deploy|regression|git|diff|rollback|blast.radius|recent"
      - "length_min:80"
      - "no_placeholder"
    expect:
      - Runs diag_logs at the 14:23 timestamp window
      - Runs diag_correlate with deploy context (PR, diff, migration)
      - Identifies the deploy as the likely cause (4x error spike within minutes of deploy)
      - Recommends rollback or git bisect to identify the offending commit
      - Notes the blast radius to narrow scope
      - Produces ranked hypotheses with deploy as #1
  - input: "Database queries that normally take 10ms are now taking 800ms. No schema changes were made."
    checks:
      - "regex:lock|contention|transaction|serialize|wait|deadlock|isolation"
      - "length_min:80"
      - "no_placeholder"
    expect:
      - Runs diag_db_stats to check for lock waits or table-level locking
      - Runs diag_logs filtering for lock timeout or deadlock messages
      - Runs diag_process_stats to check for long-running transactions
      - Identifies lock contention as the root cause
      - Recommends reviewing open transactions and lock timeout settings
      - Notes this is a classic sign of a long transaction holding locks
  - input: "A critical error was supposed to be logged but the ops team says they never saw it — logs look clean"
    checks:
      - "regex:log|saturat|buffer|drop|overflow|missing|filter|level|stderr"
      - "length_min:80"
      - "no_placeholder"
    expect:
      - Runs diag_logs with no error filter and high line count
      - Runs diag_process_stats to check log buffer status
      - Hypothesizes log buffer overflow or log level filtering suppressing the error
      - Recommends checking log daemon buffer size and log level configuration
      - Notes clean logs do not mean no error — could be log saturation
  - input: "API is returning 429 Too Many Requests on about 5% of calls — not 503"
    checks:
      - "regex:429|rate.limit|throttle|quota|RPS|too.many|backoff|retry"
      - "length_min:80"
      - "no_placeholder"
    expect:
      - Runs diag_endpoint_latency to identify 429 pattern
      - Runs diag_logs filtering for 429 or rate limit messages
      - Runs diag_process_stats to check if service is hitting external quota
      - Identifies rate limiting as the cause, not a server crash
      - Recommends implementing exponential backoff or requesting quota increase
      - Notes 429 is not a crash — it's a signal to slow down or batch requests
  - input: "One microservice is unable to reach another — curl returns 'Could not resolve host'"
    checks:
      - "regex:DNS|resolve|host|nslookup|dig|resolv|/etc/hosts|container"
      - "length_min:80"
      - "no_placeholder"
    expect:
      - Runs diag_process_stats on affected service to check container networking
      - Runs diag_logs filtering for DNS, resolution, or network errors
      - Identifies DNS resolution failure as the root cause
      - Recommends checking container DNS config, /etc/hosts, or coredns issues
      - Notes this is a common cause of microservice interconnection failures
  - input: "A small number of users (~0.1%) are seeing completely wrong data — most users are fine"
    checks:
      - "regex:corruption|wrong.data|0\\.1|inconsist|ghost|phantom|cache.poison|stale"
      - "length_min:80"
      - "no_placeholder"
    expect:
      - Runs diag_db_stats to check for data integrity issues
      - Runs diag_logs filtering for corruption, inconsistency, or cache errors
      - Runs diag_endpoint_latency on affected endpoints
      - Hypothesizes cache poisoning, ghost reads, or race condition in read path
      - Recommends checking cache invalidation logic and DB replication integrity
      - Notes this is low prevalence but high severity
  - input: "API response times are erratic — sometimes 50ms, sometimes 5000ms, no pattern in the logs"
    checks:
      - "regex:CPU|throttl|governor|spike|burst|erratic|schedule|container|noisy"
      - "length_min:80"
      - "no_placeholder"
    expect:
      - Runs diag_process_stats with CPU metrics over time
      - Runs diag_logs to find CPU throttling messages
      - Runs diag_correlate with evidence of erratic latency spikes
      - Identifies CPU throttling or CFS scheduler contention as root cause
      - Recommends checking CPU limits, CPU governor settings, or noisy neighbor
      - Notes erratic latency with no error log is classic throttling signature
  - input: "Service A can reach the database but Service B gets connection timeouts to the same database"
    checks:
      - "regex:network|partition|timeout|firewall|security.group|route|Service.B|connectivity"
      - "length_min:80"
      - "no_placeholder"
    expect:
      - Runs diag_process_stats on Service B to check network interface
      - Runs diag_logs on both services with connectivity filter
      - Runs diag_logs filtering for timeout or connection refused errors
      - Hypothesizes network partition or firewall rule blocking Service B specifically
      - Recommends checking security group rules, VPC routes, or DNS resolution
      - Notes that Service A working rules out database as the root cause
---

# Incident Diagnosis Skill

Structured root cause analysis for production incidents. Use this skill
when something is broken or slow and you need to find *why* before fixing.

**This skill is NOT:**
- Error clustering (use `error-monitoring` skill)
- Auto-healing (use `ops/auto_heal.py`)
- Browser perf audits (use `perf-audit` skill)

**This skill IS:** the investigation phase that precedes all of the above.

---

## Investigation workflow

```
1. COLLECT    → Run diag tools to gather raw evidence
2. CORRELATE  → Feed all evidence into diag_correlate
3. HYPOTHESISE → Ranked root cause hypotheses with confidence
4. CONFIRM    → Quick test of top hypothesis (one targeted check)
5. RECOMMEND  → Fix + monitoring gap
```

Always go in this order. Don't skip to step 5 without evidence.

---

## Step 1 — Collect symptoms

Run all relevant diag tools for the incident type:

### Incident: "page/endpoint is slow"
```
diag_endpoint_latency(url, n=20)        → P50/P95/P99 baseline
diag_logs(source, lines=200, level="error")  → any errors during slow period
diag_db_stats()                          → missing indexes, fragmentation
diag_process_stats()                     → CPU/memory pressure
```

### Incident: "agents stuck / missions not progressing"
```
diag_queue_depth()                       → backlog, stalled missions count
diag_process_stats()                     → memory/thread saturation
diag_logs(source="platform", lines=200, level="error")  → error loop
diag_db_stats()                          → lock waits, table bloat
```

### Incident: "memory growing / suspected leak"
```
diag_process_stats(include_children=true)  → RSS/VMS trend
diag_logs(source, filter="oom|memory|killed")
diag_queue_depth()                         → growing backlog = growing queue
```

### Incident: "service crashed / container restarted"
```
diag_logs(source, lines=500, level="error")   → last error before crash
diag_process_stats()                           → current state
diag_logs(source, filter="exit|signal|killed")
```

### Incident: "errors spiking in production"
```
diag_logs(source, lines=500, level="error")
diag_endpoint_latency(url)               → are errors causing latency too?
diag_db_stats()                          → DB connectivity issues
```

---

## Step 2 — Correlate with diag_correlate

After collecting evidence, call `diag_correlate` with ALL findings:

```
diag_correlate(
  symptoms="<paste ALL diag tool outputs here>",
  context="deploy was done 30min ago, PR #47 merged (new DB query in /api/dashboard)"
)
```

The context field is critical: include what changed recently.

---

## Step 3 — Root cause hypotheses

Structure hypotheses by confidence:

```markdown
### Hypothesis 1 — Missing DB index on missions.status (HIGH confidence)
Evidence:
  - P95 latency jumped from 120ms to 3.8s after PR #47
  - diag_db_stats: missions table has 82,000 rows, no index on status column
  - diag_logs: "full table scan" in SQLite explain output
Fix:
  CREATE INDEX idx_missions_status ON missions(status);
  → Estimated improvement: P95 back to ~150ms
Verify: diag_endpoint_latency(url, n=10) after index creation

### Hypothesis 2 — N+1 query in new dashboard endpoint (MEDIUM confidence)
Evidence:
  - PR #47 adds /api/dashboard/stats with nested loop
  - diag_logs: 47 identical SELECT statements in 200ms window
Fix:
  Refactor loop to single JOIN query
Verify: diag_logs(filter="SELECT", lines=50) after fix
```

---

## Step 4 — Confirm top hypothesis

Do ONE targeted check to confirm before acting:

| Hypothesis type | Confirmation check |
|----------------|-------------------|
| DB index missing | `EXPLAIN QUERY PLAN SELECT ...` via diag_db_stats |
| Memory leak | Run diag_process_stats twice, 60s apart — compare RSS |
| Error loop | diag_logs with filter on specific error pattern |
| CPU saturation | diag_process_stats with 2s CPU interval |
| Queue backup | diag_queue_depth twice, 30s apart — compare stalled count |

---

## Step 5 — Recommend fix + monitoring gap

Every RCA output must include:

```markdown
## Recommended Fix
[specific code change / command / config]

## Monitoring gap
"This issue would have been caught earlier if we had:
- Alert on P95 > 500ms (currently no latency alert)
- Alert on table size > 50,000 rows without index
- Add DB query duration logging to all endpoints"

## Escalation
[if fix requires > 1h or touches production data: create TMA epic via monitoring_create_heal_epic]
```

---

## Common root causes in SF

| Symptom | Most common cause | First check |
|---------|------------------|-------------|
| Slow endpoint | Missing DB index | diag_db_stats |
| Agents stuck | Memory saturation or error loop | diag_queue_depth + diag_process_stats |
| Memory growing | Unbounded cache or queue | diag_queue_depth |
| Container restart | OOM or uncaught exception | diag_logs (last 500 lines before crash) |
| Error spike | Deploy regression | diag_logs + git log --oneline -5 |
| Slow DB | Table fragmentation | diag_db_stats (freelist %) |

---

## Diagnostic tool quick reference

| Tool | Data | Use when |
|------|------|----------|
| `diag_logs` | Container/service logs | First step always |
| `diag_process_stats` | CPU/memory/threads | Suspecting resource saturation |
| `diag_db_stats` | Table sizes, slow queries, indexes | Suspecting DB bottleneck |
| `diag_endpoint_latency` | P50/P95/P99 response times | Endpoint feels slow |
| `diag_queue_depth` | Mission backlog, stalled agents | Platform feels stuck |
| `diag_correlate` | Structured RCA | After collecting all evidence |

---

## Integration with TMA auto-heal

When RCA is complete:
1. If fix is safe (no data migration, < 30min): apply directly
2. If fix is risky or complex: `monitoring_create_heal_epic(cluster_signature, fix_plan)`
3. Always: `monitoring_mark_alerted(signature)` to prevent duplicate alerts
4. Document root cause in mission memory: `memory_store(key="rca", value=...)`
