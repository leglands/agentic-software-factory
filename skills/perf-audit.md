---
# SOURCE: Inspired by chrome-devtools-mcp (Apache-2.0)
# https://github.com/ChromeDevTools/chrome-devtools-mcp
#
# WHY THIS SKILL:
#   SF agents that build or deploy web apps had no way to measure real performance.
#   Without this skill, an agent that deploys a feature doesn't know if it broke
#   LCP, introduced render-blocking resources, or caused JS errors.
#   This skill gives agents the same perf tooling a developer has in Chrome DevTools.
#
# WHAT WE BUILD ON:
#   - chrome-devtools-mcp for Lighthouse, CDP traces, Core Web Vitals, network, console
#   - NOT playwright-mcp (automation) — different tool for different job
#   - Google's Web Vitals thresholds as the scoring standard (LCP/CLS/INP)
#
# ROLES: reviewer, qa, dev, architect
#   - reviewer/qa: run audits as acceptance criteria on deployed features
#   - dev: debug perf regressions during development
#   - architect: validate perf budget compliance across projects

name: perf-audit
description: >
  Performance audit skill using Chrome DevTools MCP. Runs Lighthouse audits,
  captures Core Web Vitals (LCP/CLS/INP), profiles network and console errors.
  Activate when: reviewing a deployed feature, validating perf budgets,
  debugging a slow page, or running perf acceptance criteria.

version: "1.3.0"

eval_cases:
  - id: interpret-lighthouse-results
    prompt: |
      You just ran perf_audit_lighthouse on http://localhost:8099 and got this result:
      {
        "performance": 62, "accessibility": 88, "best-practices": 75, "seo": 91,
        "opportunities": [
          {"id": "render-blocking-resources", "score": 0.3, "savings_ms": 1850,
           "details": "3 CSS files block first paint: /static/main.css (420ms), /vendor/bootstrap.css (380ms), /fonts/inter.css (290ms)"},
          {"id": "unused-javascript", "score": 0.4, "savings_ms": 920,
           "details": "/static/app.js is 1.4MB (only 180KB used on this page)"},
          {"id": "unoptimized-images", "score": 0.5, "savings_ms": 680,
           "details": "hero.jpg is 2.8MB (could be 210KB as WebP)"}
        ],
        "console_errors": ["TypeError: Cannot read property 'user' of undefined (app.js:142)"]
      }
      Summarize the audit and give me the top 3 fixes ranked by impact.
    checks:
      - "regex:62|performance|render.block|bootstrap|app\\.js|WebP|hero"
      - "length_min:120"
      - "no_placeholder"
    expectations:
      - States performance score is 62/100 (Amber)
      - Lists render-blocking resources as #1 fix (1850ms savings — 3 CSS files)
      - Lists unused JS as #2 fix (app.js 1.4MB → trim to used 180KB)
      - Lists image optimization as #3 fix (hero.jpg 2.8MB → WebP 210KB)
      - Flags the console error TypeError in app.js:142
      - Does NOT ask for more info — all data is in the prompt

  - id: interpret-mobile-cwv
    prompt: |
      The perf_emulate_mobile and perf_audit_lighthouse tools have already been executed.
      Below are the collected results — do NOT run any tools, just interpret and recommend:

      Mobile audit complete (Moto G4 / fast-3g). Core Web Vitals from perf_audit_lighthouse:
      LCP: 5.2s (threshold: < 2.5s)
      CLS: 0.08 (threshold: < 0.1)
      INP: 420ms (threshold: < 200ms)
      Performance score: 41/100
      Top issue: "LCP element is hero.jpg — 2.8MB unoptimized image loaded eagerly"
      Are these results acceptable? What should be fixed first?
    checks:
      - "regex:5\\.2|LCP|Poor|41|hero\\.jpg|420|INP"
      - "length_min:120"
      - "no_placeholder"
    expectations:
      - States LCP 5.2s is ❌ Poor (> 4s threshold)
      - States CLS 0.08 is ✅ Good (< 0.1)
      - States INP 420ms is ❌ Poor (> 200ms threshold)
      - Identifies hero.jpg as the primary LCP fix (compress + lazy-load or WebP)
      - Says performance score 41/100 is unacceptable (below 80 budget)
      - Does NOT just restate the numbers — provides actionable recommendation

  - id: diagnose-slow-trace
    prompt: |
      You ran perf_trace_start + perf_trace_stop on http://localhost:8099. Trace results:
      LCP: 7.8s, CLS: 0.02, INP: 95ms
      Insights detected:
        - "render-blocking-resource": /static/vendor.js (2.1MB, blocks for 3.4s)
        - "long-animation-frame": dashboard_graph.js at line 445 (200ms frame)
      perf_network_slow results (threshold 1000ms):
        - GET /api/dashboard/stats — 4.1s (no cache headers, called on every render)
        - GET /api/users/me — 1.3s
      What is the root cause and what is the single most impactful fix?
    checks:
      - "regex:vendor\\.js|4\\.1s|/api/dashboard|cache|3\\.4s|root.cause"
      - "length_min:120"
      - "no_placeholder"
    expectations:
      - Identifies LCP=7.8s as ❌ Poor (root cause = vendor.js blocking 3.4s)
      - Names /api/dashboard/stats 4.1s as the most impactful network fix
      - Recommends adding cache headers or memoization to /api/dashboard/stats
      - Recommends splitting or lazy-loading vendor.js (2.1MB)
      - Gives concrete fix for the worst insight (render-blocking vendor.js)
      - Does NOT ask for clarification

  - id: zero-opportunity-audit
    prompt: |
      You ran perf_audit_lighthouse on http://localhost:8099. Results:
      {
        "performance": 98, "accessibility": 94, "best-practices": 97, "seo": 100,
        "opportunities": [],
        "console_errors": []
      }
      The team is celebrating. What do you actually report?
    checks:
      - "regex:98|100|green|no.opportunit|clean|congrat|all.scores"
      - "length_min:80"
      - "no_placeholder"
    expectations:
      - Reports all four category scores (98 perf, 94 accessibility, 97 best-practices, 100 SEO)
      - States the opportunities list is empty and there are no console errors
      - Confirms the page passes all perf budgets
      - Does NOT invent issues that are not present in the data
      - Provides a brief positive validation summary

  - id: conflicting-cwv-signal
    prompt: |
      perf_audit_lighthouse results for http://localhost:8099:
      Lighthouse Performance: 91/100 (Green)
      LCP: 2.1s (Good < 2.5s)
      CLS: 0.04 (Good < 0.1)
      INP: 890ms (Poor > 500ms)
      TBT: 850ms (Poor > 600ms)
      Console errors: none
      Why does Lighthouse show Green when INP and TBT are failing?
    checks:
      - "regex:91|Green|INP|890|TBT|850|weight|long.task|interaction|LCP.CLS"
      - "length_min:100"
      - "no_placeholder"
    expectations:
      - Explains Lighthouse score weights LCP/CLS heavily, missing INP/TBT contribution
      - Identifies INP 890ms as the critical failure
      - Identifies TBT 850ms as contributing to poor interaction score
      - Names long JavaScript tasks as root cause of INP/TBT
      - Does NOT just restate the numbers — explains the disconnect between score and reality

  - id: cls-blind-spot
    prompt: |
      perf_trace_start + perf_trace_stop on http://localhost:8099:
      LCP: 1.8s ✅
      CLS: 0.24 ❌ (threshold < 0.1)
      INP: 95ms ✅
      Insights:
        - "cumulative-layout-shift": signup-form at step 3 — radio buttons shift 180px
        - "render-blocking-resource": /fonts/lato.css (14ms only)
      What caused the CLS failure and what is the fix?
    checks:
      - "regex:CLS|0\\.24|signup|radio|shift|font|swap|font-display|layout"
      - "length_min:80"
      - "no_placeholder"
    expectations:
      - Identifies CLS 0.24 as Poor (above 0.1 threshold)
      - Traces cause to signup-form radio button layout shift at step 3
      - Notes LCP and INP are fine — CLS is isolated to form UX
      - Recommends fixing the radio button CSS (reserved space or font preloading)
      - Does NOT suggest optimizing LCP since it is already good

  - id: mobile-vs-desktop-gap
    prompt: |
      You ran perf_emulate_mobile + perf_audit_lighthouse on http://localhost:8099.
      Mobile results: Performance 52/100, LCP 6.1s, CLS 0.12, INP 380ms
      Desktop results: Performance 91/100, LCP 1.9s, CLS 0.03, INP 95ms
      The team says "desktop passes, we're good." What is your verdict?
    checks:
      - "regex:52|mobile|desktop|gap|differ|real.user|3G|throttl|not.good|mobile-first"
      - "length_min:100"
      - "no_placeholder"
    expectations:
      - States mobile score 52/100 is NOT acceptable (below 80 budget)
      - States LCP 6.1s on mobile is ❌ Poor (> 4s)
      - Points out mobile performance is what real users on 3G experience
      - Recommends fixing the mobile case — desktop passing is irrelevant for mobile-first products
      - Mentions specific mobile bottlenecks (unoptimized images or heavy JS bundle)

  - id: seo-score-failure
    prompt: |
      perf_audit_lighthouse on http://localhost:8099:
      {
        "performance": 85, "accessibility": 92, "best-practices": 88, "seo": 58,
        "opportunities": [
          {"id": "meta-description", "score": 0, "savings_ms": 0,
           "details": "Missing meta description on 12 pages"}
        ],
        "console_errors": []
      }
      The product team says SEO is not a priority right now. What do you recommend?
    checks:
      - "regex:seo|58|meta.description|missing|crawl|index|priority|recommend|budget"
      - "length_min:80"
      - "no_placeholder"
    expectations:
      - Reports SEO score 58/100 is failing (below 80 budget threshold)
      - Identifies missing meta description on 12 pages
      - Recommends fixing meta descriptions as a quick SEO win
      - Notes SEO 58 is a budget failure even if not a user-facing bug
      - Does NOT agree that SEO should be ignored — flags it as a budget violation

  - id: accessibility-critical
    prompt: |
      perf_audit_lighthouse on http://localhost:8099:
      {
        "performance": 91, "accessibility": 42, "best-practices": 90, "seo": 88,
        "opportunities": [],
        "console_errors": []
      }
      The team says performance is green so they are good to ship. Your verdict?
    checks:
      - "regex:accessibility|42|accessib|contrast|alt.text|keyboard|focus|a11y|disabilit"
      - "length_min:80"
      - "no_placeholder"
    expectations:
      - States accessibility 42/100 is ❌ failing (below 90 budget)
      - Names at least one specific accessibility issue type
      - Explains accessibility failures are real user-facing issues (users with disabilities)
      - Does NOT let the team ship just because performance is green
      - Recommends fixing accessibility before release

  - id: third-party-tag-impact
    prompt: |
      perf_audit_lighthouse + perf_network_slow on http://localhost:8099:
      Performance score: 71/100
      Slow requests (threshold 500ms):
        - GET https://analytics.example.com/track — 1.8s (no cache, third party)
        - GET https://cdn.optimizely.com — 920ms (third party)
        - GET /api/dashboard — 340ms (internal, fine)
      Console errors: none
      The marketing team insists on keeping the analytics tag. What can be done?
    checks:
      - "regex:third.party|analytics|1\\.8s|cache|async|defer|segment|load|preserve"
      - "length_min:80"
      - "no_placeholder"
    expectations:
      - Explains third-party scripts are hurting performance (1.8s analytics call)
      - Recommends loading third-party scripts asynchronously with async/defer
      - Suggests adding cache headers on the analytics endpoint
      - Notes the internal API is fine (340ms) — third party is the problem
      - Provides a concrete fix that preserves analytics while reducing impact

  - id: bundle-size-regression
    prompt: |
      perf_trace_start + perf_trace_stop + perf_analyze_insight on http://localhost:8099:
      Insight: "large-javascript": /static/app.a1b2c3.js (2.8MB, parse+execute: 4.2s on fast desktop)
      Background: Last week's audit showed app.js at 980KB. Something was bundled that shouldn't have been.
      What happened and what is the fix?
    checks:
      - "regex:2\\.8MB|regression|bundle|tree.shak|lazy|code.split|980KB|4\\.2s|added"
      - "length_min:80"
      - "no_placeholder"
    expectations:
      - Identifies bundle size regression: 980KB → 2.8MB
      - Recommends code splitting or tree shaking to reduce bundle size
      - Recommends identifying what was added since last week (new dependency?)
      - Notes 4.2s parse+execute time is a real user blocking issue on desktop too
      - Gives concrete next step (audit package.json diff or webpack bundle analyzer)

  - id: font-loading-blocking
    prompt: |
      perf_trace_start + perf_trace_stop on http://localhost:8099:
      LCP: 3.1s ⚠️ (threshold < 2.5s)
      CLS: 0.01 ✅
      INP: 110ms ✅
      Insights:
        - "render-blocking-resource": /fonts/roboto-400.woff2 (280ms block)
        - "render-blocking-resource": /fonts/roboto-700.woff2 (250ms block)
      What is the root cause of the LCP failure and what is the fix?
    checks:
      - "regex:font|blocking|LCP|3\\.1|font.display|swap|preload|woff2|preconnect"
      - "length_min:80"
      - "no_placeholder"
    expectations:
      - Identifies LCP 3.1s as Needs Work (between 2.5s and 4s)
      - Identifies font files as the render-blocking resources causing LCP delay
      - Recommends font-display: swap or preloading critical fonts
      - Recommends preconnecting to font origins
      - Notes CLS is fine so fonts are not causing layout shift

  - id: inp-critical-failure
    prompt: |
      perf_trace_start + perf_trace_stop on http://localhost:8099 after clicking "Submit Order":
      LCP: 1.9s ✅
      CLS: 0.02 ✅
      INP: 1200ms ❌ (threshold < 200ms)
      TBT: 1800ms ❌ (threshold < 200ms)
      Insights:
        - "long-animation-frame": checkout.js at line 203 (1200ms)
        - "long-animation-frame": checkout.js at line 310 (600ms)
      The user clicks Submit Order and the page freezes for 1.2 seconds. What is the fix?
    checks:
      - "regex:INP|1200|1200ms|long.task|checkout|submit|freeze|web.worker|break.up"
      - "length_min:80"
      - "no_placeholder"
    expectations:
      - Identifies INP 1200ms as Critical (12x over threshold)
      - Identifies long animation frames in checkout.js (lines 203, 310) as root cause
      - Recommends breaking up the long task (web worker, setTimeout batching, or code splitting)
      - Explains that TBT 1800ms compounds the INP issue
      - Does NOT suggest optimizing LCP since it is already good

  - id: cache-headers-missing
    prompt: |
      perf_audit_lighthouse on http://localhost:8099:
      {
        "performance": 79, "accessibility": 90, "best-practices": 88, "seo": 87,
        "opportunities": [
          {"id": "uses-long-cache-ttl", "score": 0.2, "savings_ms": 0,
           "details": "Static assets have no cache headers — 0% cache rate"}
        ],
        "console_errors": []
      }
      Performance is 79, just barely below the 80 budget. The team says caching is a backend ops task. What do you say?
    checks:
      - "regex:79|cache|TTL|static|header|Cache-Control|backend|ops|budget"
      - "length_min:80"
      - "no_placeholder"
    expectations:
      - Notes performance 79/100 is below the 80 budget threshold
      - Identifies missing cache headers on static assets as a fix
      - Explains that adding Cache-Control headers is a straightforward ops task
      - Provides the specific fix (Cache-Control: max-age=31536000 for static assets)
      - Does NOT let the team pass with 79 — flags it as a budget failure

  - id: tbt-critical
    prompt: |
      perf_trace_start + perf_trace_stop on http://localhost:8099:
      LCP: 1.4s ✅
      CLS: 0.03 ✅
      INP: 180ms ✅
      TBT: 1200ms ❌ (threshold < 200ms)
      Performance score: 74/100
      The team asks why Lighthouse is 74 when all CWV pass. What is your analysis?
    checks:
      - "regex:TBT|1200|Total Blocking|74|long.task|JS|script|main.thread"
      - "length_min:80"
      - "no_placeholder"
    expectations:
      - Notes TBT 1200ms is ❌ Critical (6x over threshold)
      - Explains that TBT is not a Core Web Vital but heavily impacts Lighthouse score
      - Names long JavaScript tasks as the cause of high TBT
      - Recommends breaking up long tasks (code splitting, web workers, defer non-critical JS)
      - Notes CWV (LCP/CLS/INP) are good so the user experience is OK, but TBT hurts the score
---

# Performance Audit Skill

Audit deployed web apps for performance, accessibility, and runtime errors
using Chrome DevTools. Same tooling as a developer opening DevTools in Chrome.

---

## RULES

**MUST:**
- MUST call every tool listed in the workflow and **display the full returned data** in your response
- MUST use `http://localhost:8099` as default URL when none is specified in the request
- MUST report actual numbers from tool output (e.g. LCP=3.2s, score=74/100) — not hypothetical values
- MUST complete the entire workflow before presenting results

**NEVER:**
- NEVER ask the user for the URL — infer from context or use `http://localhost:8099`
- NEVER show only the tool invocation without showing what it returned
- NEVER write code or mock audit results instead of calling the tools
- NEVER say "I would call perf_audit_lighthouse" — just call it

---

## When to use this skill

- After deploying a feature: "does this page still meet our perf budget?"
- Before a release: acceptance criteria on LCP/CLS/INP scores
- Debugging a slow page: "what's making this page take 8 seconds to load?"
- Mobile performance check: "is this usable on 3G?"
- Monitoring: "did the last deploy introduce console errors?"

**Do NOT use this skill for:**
- Writing automated test scripts → use `e2e-browser-testing` skill
- Exploring page structure or clicking through a UI → use `browser-exploration` skill
- Fetching API data → use `web_fetch` or REST tools

---

## Google Web Vitals Thresholds (your scoring standard)

| Metric | Good ✅ | Needs Work ⚠️ | Poor ❌ |
|--------|---------|--------------|--------|
| **LCP** (Largest Contentful Paint) | < 2.5s | 2.5–4s | > 4s |
| **CLS** (Cumulative Layout Shift) | < 0.1 | 0.1–0.25 | > 0.25 |
| **INP** (Interaction to Next Paint) | < 200ms | 200–500ms | > 500ms |
| **FCP** (First Contentful Paint) | < 1.8s | 1.8–3s | > 3s |
| **TBT** (Total Blocking Time) | < 200ms | 200–600ms | > 600ms |

Lighthouse score ≥ 90 = Green, 50–89 = Amber, < 50 = Red.

---

## Tools reference

| Tool | When to use | Key params |
|------|------------|------------|
| `perf_audit_lighthouse` | Full audit (first step) | `url`, `categories` |
| `perf_emulate_mobile` | Before mobile audit | `device`, `network` |
| `perf_trace_start` | Profile a specific interaction | `url` |
| `perf_trace_stop` | Get CWV after interaction | — |
| `perf_analyze_insight` | Drill into a trace finding | `insight` |
| `perf_network_slow` | Find slow/failed requests | `url`, `threshold_ms` |
| `perf_console_errors` | Find runtime JS errors | `url`, `level` |

---

## Workflow 1 — Full Audit (standard)

Use for: release gates, PR reviews, onboarding a new project.

```
1. perf_audit_lighthouse(url, categories=["performance","accessibility","best-practices","seo"])
   → Get scores for all 4 categories
   → Extract top 3 opportunities with biggest score impact

2. If performance score < 90:
   perf_network_slow(url, threshold_ms=500)
   → Identify slow resources, oversized assets, failed fetches

3. perf_console_errors(url, level="error")
   → Find JS errors that may degrade UX or block interactions

4. Report format (see below)
```

## Workflow 2 — Mobile Audit

Use for: features visible to end users on mobile devices.

```
1. perf_emulate_mobile(device="Moto G4", network="fast-3g")
   → Set realistic mobile constraints

2. perf_audit_lighthouse(url, categories=["performance","accessibility"])
   → Mobile Lighthouse scores (will be lower than desktop — that's expected)

3. perf_trace_start(url) → interact → perf_trace_stop()
   → Real CWV under mobile throttling

4. perf_analyze_insight(insight="LCP")  ← if LCP is worst metric
   → Specific fix suggestions for the worst Core Web Vital

5. Reset: perf_emulate_mobile(device="desktop")
```

## Workflow 3 — Debug Slow Page

Use for: "page takes 8 seconds to load, why?"

```
1. perf_trace_start(url)
   → Starts recording while page loads

2. perf_trace_stop()
   → Returns: LCP/CLS/INP values + timeline + insight names

3. For each insight in trace results:
   perf_analyze_insight(insight="<name from trace>")
   → Deep analysis + specific code/resource to fix

4. perf_network_slow(url, threshold_ms=1000)
   → Find API calls or assets taking > 1s

5. Synthesize: root cause + fix recommendation
```

---

## Output format

Always structure perf audit output as:

```markdown
## Performance Audit — <url>

### Scores
| Category | Score | Status |
|----------|-------|--------|
| Performance | 73/100 | ⚠️ Amber |
| Accessibility | 91/100 | ✅ Green |
| Best Practices | 83/100 | ⚠️ Amber |
| SEO | 95/100 | ✅ Green |

### Core Web Vitals
| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| LCP | 3.8s | < 2.5s | ❌ Poor |
| CLS | 0.05 | < 0.1 | ✅ Good |
| INP | 180ms | < 200ms | ✅ Good |

### Top Issues (by score impact)
1. **[HIGH] Render-blocking resources** (+12 score) — 3 CSS files blocking first paint
   Fix: Add `defer` to non-critical CSS, or inline critical CSS
2. **[MED] Oversized images** (+8 score) — hero.jpg is 2.4MB (should be <300KB)
   Fix: Convert to WebP, compress, add `loading="lazy"`
3. **[LOW] Missing meta description** (+3 score) — affects SEO
   Fix: Add `<meta name="description" content="...">` to <head>

### Console Errors
- TypeError: Cannot read property 'user' of undefined (app.js:142)

### Slow Requests
- /api/dashboard/stats — 2.3s (P95) → add DB index on created_at
```

---

## Perf budgets for SF projects

Default budgets to enforce on all SF-managed projects:

```yaml
perf_budget:
  lighthouse_performance: ">= 80"
  lighthouse_accessibility: ">= 90"
  lcp: "< 3.0s"
  cls: "< 0.1"
  inp: "< 300ms"
  bundle_size_js: "< 300KB (gzipped)"
  bundle_size_css: "< 50KB (gzipped)"
```

Override per project in `PRINCIPLES.md` → `## Performance Budget` section.

---

## Integration with TMA / auto-heal

When a perf regression is detected (Lighthouse perf < 80 after deploy):
1. Log as an incident cluster in `error_state.py` with type `perf_regression`
2. Trigger a TMA epic via `monitoring_create_tma_epic` tool
3. Attach the full audit report as epic context

This wires perf audits into the same auto-heal loop as runtime errors.
