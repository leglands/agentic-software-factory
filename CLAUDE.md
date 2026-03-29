# Software Factory — Quick Ref

## WHAT
- SAFe multi-agent orch: 324 agents · 26 patterns · 69 wf · 32 tpl · 55 tools.
- Stack: Py3.11 + FastAPI + Jinja2 + HTMX + SSE · PG16(62tbl WAL) + Redis7 + Infisical.
- Ports: dev :8099 · prod :8090.
- 3 deployments: OVH Demo(:8090) · OVH Baby(:8093) · local dev(:8099).
- Native client: sf-macos (Rust/AppKit, SQLite local, SSE remote).

## RUN
```sh
uvicorn platform.server:app --host 0.0.0.0 --port 8099 --ws none --log-level warning
ruff check platform/ --select E9
pytest tests/ -v
```

## TREE
```
platform/ (375py 148KLOC)
- server.py — lifespan · GZipMiddleware · auth mw · 8 bg tasks
- agents/ — exec · store(324) · adversarial(L0+L1+L2) · tool_runner(134)
- patterns/ — engine(26 topo) · fractal_{qa,stories,tests,worktree}
- workflows/ — store(32-tpl) · definitions/(69 YAML)
- services/ — epic_orch · auto_resume · pm_checkpoint · notif
- llm/ — client(6 prov) · context tiers L0/L1/L2
- db/ — adapter(PG) · schema(62tbl) · migrations
- tools/ — 55 tools: code, git, deploy, build, web, sec, mem, mcp, ast, lint, lsp
- auth/ — JWT+bcrypt · RBAC mw · OAuth(GH/Azure)
- a2a/ — bus · veto · jarvis_mcp · azure_bridge
- web/routes/ — missions pages · wf · auth · tpl(124)
skills/ — 2389 (139 YAML)
projects/ — per-proj config + git_url
```

## DB
- LIVE PG: `postgresql://macaron:macaron@localhost:5432/macaron_platform`
- PG advisory locks conn-scoped → dedicated conn/mission
- psql: `PGPASSWORD=macaron /opt/homebrew/bin/psql -h localhost -U macaron -d macaron_platform`

## NEVER
- `import platform` → shadows stdlib; use `from platform.X import Y`
- `--reload` banned; `*_API_KEY=dummy` banned
- SSE only (`--ws none`); no WebSocket
- No emoji/gradient/inline/hardcoded hex; Feather SVG only
- No fake/mock data; LIVE PG only
- No TODO stub · no `return {}` · no `pass`

## AUTH (SF)
- JWT+bcrypt · access=15min · refresh=7d · rate=5/60s/IP
- `SF_DEMO_PASSWORD` in .env · `SF_LOCAL=1` → local-dev auth bypass

## LLM — 6 PROVIDERS
```
Primary:  minimax/MiniMax-M2.7     (93% ToolCall-15, free)
Fallback: mistral/devstral-latest  (87% ToolCall-15, free experiment tier)
          azure-openai/gpt-5-mini  (paid, if key)
          local-mlx/Qwen3.5        (local Mac)
          ollama/qwen3:14b          (local)
          opencode                  (self-hosted Go)
```
- Chain: PLATFORM_LLM_PROVIDER env → _FALLBACK_CHAIN auto-built
- MiniMax: no temp · `<think>` stripped · parallel_tool_calls=False
- Mistral: tool_call_id sanitized (9-char hash, no underscores)
- GPT-5.x: max_completion_tokens (not max_tokens) · reasoning>=16K
- Cache: model+msgs+temp+tools keyed. tool_choice NOT cached.
- Timeouts: connect=30s read=300s stream_hard=600s idle=120s

## EPIC/WORKFLOW ENGINE
- Epic → wf(YAML) → epic_runs(PG) → PM-LLM → next|loop|done|skip|phase(dyn)
- `on_complete`: 41 wf auto-chain; MAX_RELOOPS=5; cap=20
- Resume via `POST /api/missions/runs/{run_id}/resume` or `/run` (reset+start)
- context_reset: true in phase YAML → clean context per phase
- Knowledge Bootstrap: auto at run start → LLM scans workspace → SPECS.md in memory
- Post-archi hook: SPECS.md refreshed after architecture/design/setup phases
- Real workspace: uses project.path (not blank data/workspaces/) if exists
- code_write blocked on existing files → forces code_edit (prevents overwrite)
- Dynamic workspace roots: code_write allowed in active run workspace_path

## QUALITY GATES (17+)
- HARD: guardrails · veto · prompt_inject · tool_acl · adv-L0(25-det) · AC-reward · RBAC · CI
- SOFT: adv-L1(LLM) · L2-visual(Playwright) · convergence · complexity
- L0 additions: STACK_MISMATCH=absolute VETO · trivial-test detection · parasitic-file (.bak)
- Phase-aware: NO_TOOLS_USED skipped for non-coding phases (contract/committee/review)
- ACE counters: helpful/harmful per KO entry (arXiv:2505.14852) → prune if harmful>helpful*2

## MEMORY (ICM + ACE + napkin)
- 4-layer: session → pattern → project → global (PG tsvector FTS)
- ICM (rtk-ai/icm): exponential decay · Jaccard dedup >85% · knowledge graph relations
- ACE (arXiv:2505.14852): helpful/harmful counters per KO · delta patch skill updates
- napkin (Michaelliv/napkin): PROJECT_BRIEF progressive disclosure L0 → SPECS.md L1
- Knowledge Bootstrap: doc agents scan workspace → SPECS.md → all agents inherit
- Decay sweep: on boot + post-phase (access-aware, pinned items never <0.5)

## BUILD DETECTION
- Centralized: tools/build_tools.py _BUILD_MANIFEST_MAP (15 build systems)
- detect_build_commands(ws) → {build, test, run, manifests}
- No hardcoded per-language commands in prompts — agents read manifests

## SKILLS (9 new domain skills)
- sveltekit-dataless-ui · nextjs-server-components-dataless
- grpc-protobuf-client · jwt-rbac-grpc-interceptor
- skeleton-loading-pattern · redis-queue-async-worker
- redis-cache-layer · postgres-binary-entity-storage · entity-domain-modeling
- 36 skills enriched to 10+ eval_cases (batch MiniMax enrichment)

## TOOLCALL-15 BENCH
- Port of stevibe/ToolCall-15 (MIT): 15 scenarios, 5 categories, deterministic scoring
- API: POST /api/toolcall-bench/run · GET /api/toolcall-bench/job/{id} · GET /api/toolcall-bench/list
- compare_models(a, b) → delta + recommendation (upgrade/rollback/neutral)
- Watchdog: auto-run daily, regression logging

## UI
- HTMX: `hx-get="/partial/X"` · `hx-trigger="load"` → HTML
- CSS: custom-prop tokens · dark-first · `[data-theme]`
- i18n: 40 locales · RTL (ar, he, fa, ur)
- Components: Atoms29 · Molecules20 · Organisms11; Feather SVG only
- Markdown: md() in JS for agent chat rendering (addMsg + SSE stream)

## GOTCHAS
- NodeStatus: PENDING · RUNNING · COMPLETED · VETOED · FAILED (no DONE)
- PG advisory lock conn-scoped; use dedicated conn per mission
- SSE test: `curl --max-time` (urllib blocks forever)
- Docker cp lost on restart (image overwrites); use env vars or volume mounts
- OVH seed_builtins() resets agent model on restart → use PLATFORM_LLM_MODEL env var

@.ai/ARCHITECTURE.md
@.ai/PLANS.md
