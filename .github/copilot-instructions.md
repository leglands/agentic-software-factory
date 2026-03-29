# Copilot Instructions — Software Factory

## Project
SAFe multi-agent orch platform. 324 agents · 26 patterns · 69 wf · 32 tpl · 55 tools.
Platform: macaron-software/software-factory (AGPL-3.0)
Port: dev :8099 · prod :8090 · baby :8093.
Native: sf-macos (Rust/AppKit, SQLite local, SSE remote).

## Stack
- Python 3.11 · FastAPI · Jinja2 · HTMX · SSE
- PostgreSQL 16 (62 tbl WAL) · Redis 7 · Infisical vault
- LLM: MiniMax M2.7 (93%) · Mistral devstral (87%) · azure-openai · local-mlx · ollama · opencode

## Architecture
```
platform/ (375py 148KLOC)
  server.py          lifespan · GZipMiddleware · auth mw · 8 bg tasks
  agents/            exec · store(324) · adversarial(L0+L1+L2) · tool_runner(134)
  patterns/          engine(26 topo) · fractal_{qa,stories,tests,worktree}
  workflows/         store(32-tpl) · definitions/(69 YAML)
  services/          epic_orch · auto_resume · pm_checkpoint · notif
  llm/               client(6 prov) · context tiers L0/L1/L2 · observability
  db/                adapter(PG) · schema(62tbl) · migrations
  tools/             55 tools: code·git·deploy·build·web·sec·mem·mcp·ast·lint·lsp
  auth/              JWT+bcrypt · RBAC mw · OAuth(GH/Azure)
  a2a/               bus · veto · jarvis_mcp · azure_bridge
  web/routes/        missions · wf · auth · tpl(124)
skills/              2389 (139 YAML) — Thompson Sampling Beta(a=wins, b=losses)
projects/            per-proj config + git_url
```

DB: `postgresql://macaron:macaron@localhost:5432/macaron_platform`
PG advisory locks conn-scoped → dedicated conn/mission

## Commands
```sh
uvicorn platform.server:app --host 0.0.0.0 --port 8099 --ws none --log-level warning
ruff check platform/ --select E9
pytest tests/ -v
psql: PGPASSWORD=macaron /opt/homebrew/bin/psql -h localhost -U macaron -d macaron_platform
```

## LLM Providers (6) — Fallback Chain
```
1. minimax/MiniMax-M2.7      93% TC-15 · free · primary
2. mistral/devstral-latest   87% TC-15 · free experiment · fallback #1
3. azure-openai/gpt-5-mini   paid · fallback #2
4. local-mlx/Qwen3.5-35B     local Mac
5. ollama/qwen3:14b           local
6. opencode                   self-hosted Go
```
- MiniMax: no temp · strip `<think>` · parallel_tool_calls=False
- Mistral: tool_call_id sanitized → 9-char alphanumeric hash (no underscores)
- GPT-5.x: max_completion_tokens · reasoning budget>=16K
- Timeouts: connect=30s read=300s stream=600s idle=120s

## Invariants
- `import platform` forbidden → use `from platform.X import Y`
- `--reload` banned · `*_API_KEY=dummy` banned
- SSE only (`--ws none`) · no WebSocket
- No emoji/gradient/inline/hardcoded hex · Feather SVG only
- No fake/mock data · LIVE PG only
- No test.skip · `@ts-ignore` · silent fallback
- No TODO stub · `return {}` · `pass`
- NodeStatus: PENDING · RUNNING · COMPLETED · VETOED · FAILED (no DONE)
- PG advisory lock conn-scoped · dedicated conn per mission

## Quality Gates (17+)
HARD: guardrails · veto · prompt_inject · tool_acl · adv-L0(25-det) · AC-reward · RBAC · CI
SOFT: adv-L1(LLM) · L2-visual(Playwright) · convergence · complexity
NEW: STACK_MISMATCH=absolute VETO · trivial-test detect · parasitic-file · phase-aware NO_TOOLS

## Adversarial (Swiss Cheese)
L0: deterministic (25+ rules, 0ms) → VETO ABSOLU
  + STACK_MISMATCH absolute VETO (L0+L1, not overridable by write tools)
  + Trivial test detection (assert_eq!(2+2,4), tautology, literal compare)
  + Parasitic file detection (.bak, .tmp, .orig)
  + Phase-aware: NO_TOOLS_USED skipped for non-coding phases (contract/committee/review/trace/audit)
  + Role-aware: trace/auditor/monitor/ciso/portfolio/coach exempt from NO_CODE_WRITE
L1: LLM semantic (SLOP, hallucination, logic) → VETO ABSOLU
L2: visual screenshot eval (Playwright, UI phases only)
ACE feedback: each L0 issue → harmful on KO · clean pass → helpful
SBD: 25/25 controls (Yems221/securebydesign-llmskill MIT v1.1)

## Memory (ICM + ACE + napkin inspired)
- ICM (rtk-ai/icm): exponential decay · Jaccard dedup >85% · graph relations
- ACE (arXiv:2505.14852 ICLR 2026): helpful/harmful counters · delta patch mode
- napkin (Michaelliv/napkin): PROJECT_BRIEF L0 → SPECS.md L1 progressive disclosure
- Knowledge Bootstrap: auto at run start, refreshed after archi phases
- Doc agents = "sachants" — maintain SPECS.md in memory_project

## Workspace Isolation
- code_write: blocked on existing files (forces code_edit)
- code_write: dynamic roots from active epic_runs (real project paths)
- code_read: sensitive file regex (.env, .ssh, credentials)
- Landlock: Linux-only (disabled macOS) · Docker sandbox: opt-in
- Post-phase cleanup: auto-delete .bak/.tmp before git commit

## Build Detection (centralized)
- tools/build_tools.py: _BUILD_MANIFEST_MAP (15 build systems, data-driven)
- detect_build_commands(ws) → {build, test, run, manifests}
- Zero hardcoded per-language commands in prompts

## Skills (1133 total, 0 missing refs)
Domain: sveltekit-dataless-ui · nextjs-server-components-dataless · grpc-protobuf-client
  jwt-rbac-grpc-interceptor · skeleton-loading-pattern · redis-queue/cache · pg-binary-entity
Security: secure-by-design-full (25 SBD, 5-layer, source: Yems221 MIT) · owasp-top-10 · secure-code-review
Testing: business-testing-saas (CRUD/RBAC/billing/GDPR) · e2e-testing-patterns (POM/fixtures/a11y)
Teams: traceability-{audit,writing,e2e-check} · tma-{incident,autoheal} · design-patterns · code-reading
Assignment: dynamic from SPECS.md keywords → skill library scan (no hardcode)

## Key Decisions
| Decision | Rationale |
|----------|-----------|
| HTMX over SPA | SSE + Jinja2, no React/Vue bundling |
| PostgreSQL only | SQLite deprecated, advisory locks per mission |
| Feather SVG | no emoji, no FontAwesome |
| JWT+bcrypt auth | 15min access, 7d refresh, rate 5/min/IP |
| Infisical vault | .env = bootstrap only |
| Thompson Sampling | skill selection Beta per skill |
| Darwin GA | team fitness evolution nightly |
| MiniMax primary | 93% TC-15, free, fallback=Mistral |
| No hardcode prompts | agents read manifests, LLM reasons about stack |
| code_write=new only | existing files → code_edit (prevents Cargo.toml destruction) |
| Knowledge Bootstrap | SPECS.md auto-generated, doc agents maintain it |
| ACE feedback | helpful/harmful per KO, prune harmful>helpful*2 after 5 feedbacks |
| Mistral fallback | 87% TC-15, free experiment, tool_call_id quirk handled |

## Deployments
```
OVH Demo  :8090  MiniMax-M2.7 → Mistral devstral  blue-green Docker
OVH Baby  :8093  MiniMax-M2.7 → Mistral devstral  simple mode
Local dev :8099  local-mlx or minimax              direct uvicorn
sf-macos  native Ollama local or SSE remote        Rust/AppKit
```
