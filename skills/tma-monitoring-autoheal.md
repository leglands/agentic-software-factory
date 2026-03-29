name: TMA Monitoring Auto-heal
description: TMA monitoring and auto-heal skill. Covers health checks, alerting, circuit breakers, graceful degradation, MTTR tracking, incident escalation, log analysis, resource exhaustion detection.
trigger: "/tma-mon" or "monitoring,alerting,autoheal,circuit-breaker,graceful-degradation,mttr,incident-escalation,log-analysis,resource-exhaustion"
tools:
  - bash
  - read
  - write
  - edit
  - glob
  - grep
  - task
  - rtk_git_status
  - rtk_git_diff
  - rtk_git_log
  - rtk_ls
  - rtk_read_file
  - rtk_pytest
  - rtk_cargo_test
  - rtk_docker_ps
  - playwright_browser_navigate
  - playwright_browser_snapshot
  - playwright_browser_console_messages
  - playwright_browser_network_requests
  - playwright_browser_wait_for
  - playwright_browser_click
  - playwright_browser_type
  - playwright_browser_evaluate
  - playwright_browser_take_screenshot
  - playwright_browser_install
  - sf-jarvis_jarvis_ask
  - sf-jarvis_jarvis_status
  - sf-jarvis_jarvis_task_list
  - sf-jarvis_jarvis_agent_card
  - question
  - todowrite
  - webfetch
  - skill

## HEALTH CHECK ENDPOINTS

### Standard Endpoints
```
GET /health          → { status, version, uptime, checks[] }
GET /health/live     → liveness probe (process alive)
GET /health/ready    → readiness probe (can serve traffic)
GET /health/deep     → deep check (DB, cache, external deps)
```

### Check Types
- **LIVENESS**: Is process running? Restart if FAIL
- **READINESS**: Can handle traffic? Remove from LB if FAIL
- **STARTUP**: Init complete? Block traffic until PASS

### Implementation Pattern
```typescript
interface HealthCheck {
  name: string;
  status: 'PASS' | 'FAIL' | 'WARN';
  latency_ms?: number;
  message?: string;
  timestamp: string;
}

async function deepHealthCheck(): Promise<HealthCheck[]> {
  return Promise.all([
    checkDb(),
    checkCache(),
    checkExternalDeps(),
    checkDiskSpace(),
    checkMemoryPressure()
  ]);
}
```

## ALERTING THRESHOLDS

### Severity Levels
| Level | Name | Response Time | Example |
|-------|------|---------------|---------|
| P1 | CRITICAL | 0-5 min | Service DOWN |
| P2 | HIGH | 5-15 min | Latency > 500ms |
| P3 | MEDIUM | 15-60 min | Error rate > 1% |
| P4 | LOW | 1-4 hrs | Disk > 70% |

### Threshold Config
```yaml
alerts:
  latency_p99:
    warning: 300ms
    critical: 1000ms
    window: 5m
  error_rate:
    warning: 0.5%
    critical: 2%
    window: 2m
  availability:
    critical: < 99.5%
    window: 1h
  memory_usage:
    warning: 75%
    critical: 90%
    window: 5m
  cpu_usage:
    warning: 70%
    critical: 85%
    window: 5m
```

### Alerting Rules
```yaml
groups:
  - name: service_health
    rules:
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.job }} is down"
          
      - alert: HighLatency
        expr: latency_p99 > 1000
        for: 5m
        labels:
          severity: high
```

## AUTO-RESTART ON FAILURE

### Restart Policy Matrix
| Failure Type | Threshold | Action | Cooldown |
|--------------|-----------|--------|----------|
| Crash Loop | 3x in 5min | Escalate | 30min |
| OOM | any | Restart | 5min |
| Hang | 60s unresponsive | Restart | 10min |
| Deadlock | detected | Restart | 15min |
| Resource exhaustion | threshold hit | Scale/Restart | 5min |

### Auto-Restart Implementation
```typescript
class RestartPolicy {
  private attempts: Map<string, Attempt[]> = new Map();
  
  shouldRestart(serviceId: string, reason: FailureReason): boolean {
    const history = this.attempts.get(serviceId) || [];
    const recent = history.filter(a => 
      Date.now() - a.timestamp < this.windowMs
    );
    
    if (this.isCrashLoop(recent)) {
      this.escalate(serviceId, 'CRASH_LOOP');
      return false;
    }
    
    if (this.cooldownActive(serviceId)) {
      return false;
    }
    
    return true;
  }
  
  private isCrashLoop(attempts: Attempt[]): boolean {
    return attempts.length >= 3 && 
           attempts.every(a => a.reason === 'CRASH');
  }
}
```

### Kubernetes Restart Policy
```yaml
spec:
  restartPolicy: Always
  containers:
  - name: app
    livenessProbe:
      httpGet:
        path: /health/live
        port: 8080
      initialDelaySeconds: 30
      periodSeconds: 10
      failureThreshold: 3
    readinessProbe:
      httpGet:
        path: /health/ready
        port: 8080
      initialDelaySeconds: 5
      periodSeconds: 5
      failureThreshold: 3
```

## CIRCUIT BREAKER PATTERNS

### State Machine
```
CLOSED → (failure threshold) → OPEN
OPEN → (timeout) → HALF_OPEN
HALF_OPEN → (success) → CLOSED
HALF_OPEN → (failure) → OPEN
```

### Circuit Breaker Config
```typescript
interface CircuitBreakerConfig {
  failureThreshold: number;      // failures before open (default: 5)
  successThreshold: number;     // successes in half-open to close (default: 3)
  timeout: number;              // ms before half-open (default: 60000)
  halfOpenMaxCalls: number;     // calls allowed in half-open (default: 3)
  windowDuration: number;       // sliding window ms (default: 10000)
  volumeThreshold: number;      // min calls before CB evaluates (default: 10)
}

class CircuitBreaker {
  private state: 'CLOSED' | 'OPEN' | 'HALF_OPEN' = 'CLOSED';
  private failureCount = 0;
  private successCount = 0;
  private lastFailureTime = 0;
  private callTimestamps: number[] = [];
  
  async call<T>(fn: () => Promise<T>, fallback: T): Promise<T> {
    if (this.state === 'OPEN') {
      if (Date.now() - this.lastFailureTime > this.config.timeout) {
        this.transitionTo('HALF_OPEN');
      } else {
        return fallback;
      }
    }
    
    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      return fallback;
    }
  }
}
```

### Usage Patterns
```typescript
// Decorator
@CircuitBreaker({ failureThreshold: 3, timeout: 30000 })
async function fetchUserData(id: string): Promise<UserData> {
  return externalService.getUser(id);
}

// Manual
const cb = new CircuitBreaker({ 
  failureThreshold: 5,
  fallback: () => defaultUserData 
});
const data = await cb.call(() => getUser(id), defaultUserData);
```

## GRACEFUL DEGRADATION

### Degradation Levels
| Level | Status | Behavior |
|-------|--------|----------|
| 0 | FULL | All features operational |
| 1 | DEGRADED | Non-essential features disabled |
| 2 | MINIMAL | Core features only, caching active |
| 3 | EMERGENCY | Read-only, single instance |
| 4 | DOWN | No service, error page |

### Implementation
```typescript
class GracefulDegradation {
  private level: DegradationLevel = 0;
  private featureFlags: Map<string, boolean> = new Map();
  
  getDegradationLevel(): DegradationLevel {
    return this.level;
  }
  
  setDegradationLevel(level: DegradationLevel): void {
    this.level = level;
    this.updateFeatureFlags();
  }
  
  private updateFeatureFlags(): void {
    switch (this.level) {
      case 0: // Full
        this.featureFlags.set('analytics', true);
        this.featureFlags.set('search', true);
        this.featureFlags.set('recommendations', true);
        break;
      case 1: // Degraded
        this.featureFlags.set('analytics', false);
        this.featureFlags.set('search', true);
        this.featureFlags.set('recommendations', false);
        break;
      case 2: // Minimal
        this.featureFlags.set('analytics', false);
        this.featureFlags.set('search', false);
        this.featureFlags.set('recommendations', false);
        break;
      case 3: // Emergency
        this.featureFlags.set('analytics', false);
        this.featureFlags.set('search', false);
        this.featureFlags.set('recommendations', false);
        this.setReadOnlyMode(true);
        break;
    }
  }
  
  isFeatureEnabled(feature: string): boolean {
    return this.featureFlags.get(feature) ?? false;
  }
}
```

### Fallback Strategies
```typescript
const fallbackStrategies = {
  'user-recommendations': () => defaultRecommendations,
  'search': () => cachedSearchResults,
  'payment-processing': () => queueForLater,
  'analytics': () => bufferedAnalytics,
  'image-resize': () => originalImage,
  'notifications': () => { /* silently drop */ }
};
```

## MTTR TRACKING

### MTTR Metrics
```typescript
interface IncidentRecord {
  id: string;
  startedAt: Date;
  detectedAt: Date;
  resolvedAt?: Date;
  severity: 'P1' | 'P2' | 'P3' | 'P4';
  type: 'performance' | 'outage' | 'degradation' | 'security';
  affectedService: string;
  rootCause?: string;
  resolutionSteps?: string[];
}

interface MTTRStats {
  mttr_minutes: number;
  mttr_target_minutes: number;
  incidents_last_7d: number;
  incidents_last_30d: number;
  availability_percent: number;
  mtbf_hours: number;  // Mean Time Between Failures
}
```

### MTTR Calculation
```typescript
function calculateMTTR(incidents: IncidentRecord[]): number {
  const resolved = incidents.filter(i => i.resolvedAt);
  if (resolved.length === 0) return 0;
  
  const totalMinutes = resolved.reduce((sum, i) => {
    const duration = i.resolvedAt.getTime() - i.detectedAt.getTime();
    return sum + duration / 60000;
  }, 0);
  
  return totalMinutes / resolved.length;
}
```

### MTTR Dashboard Query (Prometheus)
```promql
# Average MTTR
avg_over_time(incident_resolution_time_minutes[7d])

# MTTR by severity
sum by (severity) (incident_resolution_time_minutes) 
  / 
sum by (severity) (count(incident_resolution_time_minutes))

# MTTR trend
rate(incident_resolution_time_minutes_total[1h]) * 60
```

## INCIDENT ESCALATION MATRIX

### Escalation Matrix
| Level | Who | Trigger | Response Time |
|-------|-----|---------|---------------|
| L1 | On-call Engineer | Auto/Manual | 15 min |
| L2 | Team Lead | L1 no resolution | 30 min |
| L3 | Engineering Manager | L2 no resolution | 1 hr |
| L4 | VP Engineering | Business impact | 2 hr |
| L5 | CTO | Major outage | 4 hr |

### Escalation Rules
```yaml
escalation:
  rules:
    - name: p1_escalation
      if:
        severity: P1
        no_resolution_minutes: 15
      then:
        level: L2
        notify: [slack_alerts, pagerduty]
        
    - name: p2_escalation
      if:
        severity: P2
        no_resolution_minutes: 30
      then:
        level: L2
        notify: [slack_alerts]
        
    - name: blast_radius
      if:
        affected_users_percent: > 20
      then:
        level: L3
        notify: [slack_alerts, pagerduty, sms]
```

### Runbook Structure
```markdown
# INCIDENT: [Title]
## Severity: P[N]
## Status: [OPEN|INVESTIGATING|MITIGATED|RESOLVED]

## Timeline
- HH:MM - Event
- HH:MM - Detected
- HH:MM - Action taken
- HH:MM - Resolved

## Impact
- Users affected: N%
- Services impacted: [list]
- Revenue impact: $estimate

## Root Cause
[Description]

## Resolution
[Steps taken]

## Follow-up
- [ ] Task 1
- [ ] Task 2
```

## LOG ANALYSIS PATTERNS

### Error Pattern Detection
```typescript
const errorPatterns = [
  {
    name: 'OOM_KILL',
    regex: /oom_kill|out_of_memory|killed process/gi,
    severity: 'critical',
    action: 'restart_service'
  },
  {
    name: 'CONNECTION_TIMEOUT',
    regex: /connection_timeout|etimedout|ECONNRESET/gi,
    severity: 'warning',
    action: 'check_upstream'
  },
  {
    name: 'AUTH_FAILURE',
    regex: /authentication_failed|unauthorized|401|403/gi,
    severity: 'medium',
    action: 'alert_security'
  },
  {
    name: 'RATE_LIMIT',
    regex: /rate_limit_exceeded|429|too_many_requests/gi,
    severity: 'low',
    action: 'log_only'
  },
  {
    name: 'DB_DEADLOCK',
    regex: /deadlock_detected|lock_wait_timeout/gi,
    severity: 'high',
    action: 'restart_db_connection'
  }
];
```

### Log Aggregation Query Patterns
```yaml
queries:
  error_rate:
    pattern: 'level=ERROR'
    group_by: [service, endpoint]
    window: 5m
    alert_threshold: 10
    
  latency_outliers:
    pattern: 'latency_ms=\d+'
    extract: 'latency_ms'
    group_by: [service, endpoint]
    percentile: p99
    alert_threshold: 1000
    
  crash_loop:
    pattern: ' exited with code \d+'
    group_by: [service, host]
    window: 5m
    alert_threshold: 3
```

### Structured Log Format
```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "level": "ERROR",
  "service": "user-api",
  "version": "1.2.3",
  "trace_id": "abc123",
  "span_id": "def456",
  "message": "Database connection failed",
  "error": {
    "type": "ConnectionError",
    "message": "ECONNREFUSED",
    "stack": "..."
  },
  "context": {
    "db_host": "db.internal",
    "db_port": 5432,
    "query": "SELECT * FROM users"
  }
}
```

## RESOURCE EXHAUSTION DETECTION

### Resource Monitors
```typescript
interface ResourceMetrics {
  cpu: { usage: number; throttled: number; };
  memory: { used: number; cached: number; available: number; oom_kills: number; };
  disk: { used: number; available: number; io_wait: number; };
  network: { connections: number; dropped: number; bandwidth: number; };
  sockets: { open: number; TIME_WAIT: number; orphan: number; };
}

class ResourceMonitor {
  private thresholds = {
    memory: { warning: 75, critical: 90 },
    cpu: { warning: 70, critical: 85 },
    disk: { warning: 80, critical: 95 },
    connections: { warning: 8000, critical: 10000 }
  };
  
  checkResources(): Alert[] {
    const alerts: Alert[] = [];
    const metrics = this.collectMetrics();
    
    if (metrics.memory.usage > this.thresholds.memory.critical) {
      alerts.push({
        severity: 'critical',
        type: 'MEMORY_EXHAUSTION',
        message: `Memory at ${metrics.memory.usage}%`,
        action: 'trigger_gc_or_restart'
      });
    }
    
    if (metrics.memory.oom_kills > 0) {
      alerts.push({
        severity: 'critical',
        type: 'OOM_KILL',
        message: `${metrics.memory.oom_kills} OOM kills detected`,
        action: 'immediate_restart'
      });
    }
    
    if (metrics.connections.open > this.thresholds.connections.critical) {
      alerts.push({
        severity: 'high',
        type: 'CONNECTION_EXHAUSTION',
        message: `${metrics.connections.open} open connections`,
        action: 'scale_out'
      });
    }
    
    return alerts;
  }
}
```

### Container Resource Limits
```yaml
resources:
  limits:
    memory: "512Mi"
    cpu: "500m"
  requests:
    memory: "256Mi"
    cpu: "100m"
```

### File Descriptor Monitoring
```bash
# Check current usage
cat /proc/$(pgrep -f app)/fd/count

# Warning thresholds
fd_usage_percent > 70% → warning
fd_usage_percent > 90% → critical
```

## AUTO-HEAL WORKFLOW

### Healing State Machine
```
HEALTHY → DETECT → INVESTIGATE → MITIGATE → VERIFY → HEALTHY
                  ↓
              ESCALATE (if cannot auto-heal)
```

### Auto-Heal Actions
| Condition | Action | Confidence | Rollback |
|-----------|--------|------------|----------|
| High memory | Restart container | 0.9 | Auto |
| Crash loop | Restart + clear logs | 0.95 | Auto |
| DB timeout | Retry + increase timeout | 0.8 | Auto |
| External dep down | Switch to fallback | 0.85 | Auto |
| Disk full | Clean old logs | 0.7 | Manual |
| Network partition | Wait + failover | 0.6 | Manual |

### Healing Execution
```typescript
class AutoHealer {
  async heal(serviceId: string, issue: Issue): Promise<HealingResult> {
    const action = this.determineAction(issue);
    
    if (action.confidence < 0.7) {
      await this.escalate(serviceId, issue);
      return { status: 'ESCALATED', reason: 'Low confidence' };
    }
    
    await this.executeAction(serviceId, action);
    
    if (await this.verifyHealth(serviceId)) {
      await this.recordHealing(issue, action);
      return { status: 'HEALED', action: action.type };
    }
    
    await this.rollback(serviceId, action);
    await this.escalate(serviceId, issue);
    return { status: 'FAILED', action: action.type };
  }
}
```

## EVALUATION CASES

### eval_case_1: Service Health Check
```
TASK: Add liveness and readiness probes to service at /services/api
CRITERIA:
- /health/live returns 200 when process is healthy
- /health/ready returns 200 when DB connection is established
- /health/ready returns 503 when DB is unreachable
- Both endpoints respond in < 50ms
EVAL: Deploy and verify probes trigger restart on failure
```

### eval_case_2: Circuit Breaker Implementation
```
TASK: Implement circuit breaker for external API calls
CRITERIA:
- Opens after 5 consecutive failures
- Half-open after 60s timeout
- Closes after 3 successes in half-open
- Returns fallback immediately when open
EVAL: Simulate failures and verify CB state transitions
```

### eval_case_3: MTTR Tracking
```
TASK: Add MTTR tracking to incident management system
CRITERIA:
- Records incident start, detection, and resolution times
- Calculates MTTR by severity level
- Dashboard shows MTTR trend over 30 days
- Target: MTTR < 30 min for P1 incidents
EVAL: Create test incidents and verify MTTR calculation
```

### eval_case_4: Alert Threshold Tuning
```
TASK: Configure alerting for API latency
CRITERIA:
- WARNING at p99 > 300ms for 5 minutes
- CRITICAL at p99 > 1000ms for 2 minutes
- Alert includes service name, endpoint, current value
- Suppress alerts during maintenance window
EVAL: Generate load and verify alerts fire at thresholds
```

### eval_case_5: Auto-Restart on Crash Loop
```
TASK: Detect and handle crash loop scenario
CRITERIA:
- Detects 3 crashes within 5 minutes
- Stops restart attempts after detection
- Escalates to L2 on-call
- Records crash logs for post-mortem
- Cooldown period of 30 minutes before retry
EVAL: Force crash loop and verify escalation
```

### eval_case_6: Graceful Degradation
```
TASK: Implement feature flags for degradation
CRITERIA:
- Level 0: All features enabled
- Level 1: Analytics disabled
- Level 2: Search disabled, use cache
- Level 3: Core API only, read-only
- Feature flags update within 1 second
EVAL: Trigger degradation and verify feature states
```

### eval_case_7: Escalation Matrix
```
TASK: Configure and test incident escalation
CRITERIAL:
- P1 escalates to L2 after 15 min no resolution
- P2 escalates to L2 after 30 min no resolution
- >20% users affected triggers immediate L3
- All escalations notify Slack and PagerDuty
EVAL: Create stalled incidents and verify escalation
```

### eval_case_8: Log Pattern Analysis
```
TASK: Set up real-time error detection from logs
CRITERIA:
- Detects OOM patterns within 10 seconds
- Correlates error patterns across services
- Groups similar errors to reduce noise
- Stores error context for root cause analysis
EVAL: Inject error patterns and verify detection
```

### eval_case_9: Resource Exhaustion
```
TASK: Monitor and prevent resource exhaustion
CRITERIA:
- Memory > 90% triggers warning + GC
- Memory > 95% triggers container restart
- File descriptors > 90% triggers connection cleanup
- Prevents OOM kills through proactive action
EVAL: Simulate resource exhaustion and verify response
```

### eval_case_10: Auto-Heal Verification
```
TASK: Create and test auto-heal workflow
CRITERIA:
- Detects degradation within 30 seconds
- Executes mitigation within 2 minutes
- Verifies health within 1 minute
- Rolls back if healing fails
- Records all healing attempts
EVAL: Inject failure and verify complete healing cycle
```

### eval_case_11: Full Stack Monitoring
```
TASK: Implement complete TMA monitoring stack
CRITERIA:
- Health endpoints for all services
- Circuit breakers on all external calls
- Graceful degradation for non-critical features
- MTTR tracking for all incidents
- Escalation matrix enforced
- Auto-heal for common failure modes
- Resource monitoring and alerting
EVAL: Run chaos engineering tests and verify resilience
```
