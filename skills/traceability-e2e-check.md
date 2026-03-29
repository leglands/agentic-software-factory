# SKILL: trace-e2e-verify
# AGENT: trace-lead (Nadia)
# PURPOSE: E2E traceability gate — 13-layer coverage, veto if <80%, block regressions

## PHASE: e2e_traceability_check

### TOOL: project_traceability_report(project_id) → full 13-layer state
### TOOL: project_traceability_check_e2e(project_id) → PASS | FAIL gate
### TOOL: project_traceability_export_sqlite(project_id) → audit trail
### TOOL: memory_store(key, value) → coverage snapshots for trend tracking

---

## WORKFLOW

1. CALL project_traceability_report(project_id)
   - receive: 13-layer map { layer_name → { features:[], stories:[], code覆盖率, test覆盖率 } }
   - identify orphan items: feature/story with ZERO code AND ZERO test entries

2. CALL project_traceability_check_e2e(project_id)
   - receive: PASS or FAIL + list of failed layer names

3. IF FAIL:
   - LIST failed layers
   - LIST orphan features (no code, no tests)
   - LIST orphan stories (no code, no tests)
   - BUILD traceability_matrix: feature × layer → covered | gap | orphan
   - CALCULATE coverage_pct = (covered_items / total_items) × 100
   - IF coverage_pct < 80: VETO phase with detailed gap report
   - ELSE: proceed with warnings

4. IF PASS:
   - CALL project_traceability_export_sqlite(project_id)
   - STORE snapshot: { project_id, date, coverage_pct, layer_breakdown }
   - LOAD previous snapshot from memory_store
   - IF previous exists:
     - IF coverage_pct < previous.coverage_pct: VETO REGRESSION, block merge
     - ELSE: log improvement, allow proceed

5. STORE current snapshot in memory_store(key="trace_coverage_{project_id}")

---

## 13 LAYERS (in order)
1. requirements
2. acceptance_criteria
3. feature_spec
4. story_map
5. api_spec
6. data_model
7. code_impl
8. unit_tests
9. integration_tests
10. e2e_tests
11. perf_tests
12. security_tests
13. docs

---

## EVAL_CASES

### CASE 1: PASS at 85% — proceed
- project_traceability_check_e2e → PASS
- coverage_pct = 85
- previous = 80
- delta = +5 → IMPROVED → ALLOW merge

### CASE 2: PASS at 82% — no regression
- project_traceability_check_e2e → PASS
- coverage_pct = 82
- previous = 82
- delta = 0 → STABLE → ALLOW merge

### CASE 3: FAIL at 75% — VETO
- project_traceability_check_e2e → FAIL
- failed_layers: [code_impl, unit_tests, e2e_tests]
- orphan_features: ["login-oauth2", "payment-stripe"]
- orphan_stories: ["auth-001", "pay-003"]
- coverage_pct = 75
- → VETO: 5 missing items, coverage 75% < 80% threshold

### CASE 4: PASS but REGRESSION — VETO
- project_traceability_check_e2e → PASS
- coverage_pct = 78
- previous = 85
- delta = -7 → REGRESSION → VETO: coverage dropped from 85% to 78%

### CASE 5: FAIL — no orphans, layer gaps only
- project_traceability_check_e2e → FAIL
- failed_layers: [perf_tests, security_tests]
- orphan_features: []
- orphan_stories: []
- coverage_pct = 79
- → VETO: 2 layers incomplete, coverage 79% < 80%

### CASE 6: PASS — first run, no history
- project_traceability_check_e2e → PASS
- coverage_pct = 91
- previous = null
- → STORE snapshot, no comparison possible, ALLOW merge

### CASE 7: FAIL — multiple orphan features
- project_traceability_check_e2e → FAIL
- failed_layers: [code_impl, unit_tests, integration_tests]
- orphan_features: ["user-profile-update", "video-upload", "notification-push", "report-export"]
- orphan_stories: ["prof-002", "vid-001", "notif-007", "rpt-010"]
- coverage_pct = 68
- → VETO: 4 orphan features, 4 orphan stories, coverage 68% < 80%

### CASE 8: PASS but near threshold — warn
- project_traceability_check_e2e → PASS
- coverage_pct = 81
- previous = 80
- delta = +1
- → WARN: coverage near 80% floor, monitor next sprint

### CASE 9: FAIL — docs and security missing
- project_traceability_check_e2e → FAIL
- failed_layers: [security_tests, docs]
- orphan_features: []
- orphan_stories: ["sec-999"]
- coverage_pct = 77
- → VETO: critical layers security_tests and docs not covered

### CASE 10: PASS but one layer at 0%
- project_traceability_check_e2e → PASS (overall)
- one layer: perf_tests has 0% coverage
- coverage_pct = 82
- → WARN: layer perf_tests at 0%, add perf tests before next phase

### CASE 11: FAIL — data_model and api_spec gaps
- project_traceability_check_e2e → FAIL
- failed_layers: [data_model, api_spec]
- orphan_features: ["graphql-subscriptions"]
- orphan_stories: ["api-020"]
- coverage_pct = 72
- → VETO: foundational layers data_model and api_spec incomplete

### CASE 12: PASS — export and store
- project_traceability_check_e2e → PASS
- coverage_pct = 88
- previous = 84
- → CALL project_traceability_export_sqlite(project_id)
- → STORE snapshot in memory_store
- → delta = +4 → IMPROVED → ALLOW merge

### CASE 13: FAIL — partial code coverage
- project_traceability_check_e2e → FAIL
- failed_layers: [code_impl, unit_tests]
- code_impl coverage: 45%
- unit_tests coverage: 38%
- orphan_features: ["legacy-checkout", "old-inventory"]
- coverage_pct = 55
- → VETO: code implementation and unit tests severely incomplete

---

## OUTPUT FORMAT

```
TRACEABILITY E2E REPORT: {project_id}
═══════════════════════════════════════
Date: {timestamp}
Gate: {PASS|FAIL|VETO}
Coverage: {coverage_pct}%
Delta: {delta_from_previous}
Failed Layers: {list}
Orphan Features: {list}
Orphan Stories: {list}
Matrix:
  {feature} × {layer} → {covered|gap|orphan}
Decision: {ALLOW|BLOCK} merge
```

---

## THRESHOLDS
- MIN_COVERAGE = 80%
- REGRESSION_TOLERANCE = 0% (any drop triggers veto)
- LAYERS_REQUIRED = all 13 must have at least some entry
