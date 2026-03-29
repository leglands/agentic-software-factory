# SKILL: code-reading
# TOOL: trace-auditor
# ENCODING: utf-8

## PURPOSE
Enable rapid orientation in unfamiliar codebases. Extract structural signal from naming, layout, imports, and call graphs. Identify complexity hotspots, dead code, and architectural layers without executing code.

---

## PHASE 1: ENTRY POINT IDENTIFICATION

### Strategy
1. Scan for conventional entry files: `main`, `index`, `app`, `server`, `cli`, `program`, `lib`.
2. Check file extensions: `.py` → `if __name__ == "__main__"`, `.js` → `module.exports` / `export default`, `.rs` → `fn main()`, `.go` → `func main()`, `.java` → `public static void main`.
3. Inspect root-level files: `Makefile`, `CMakeLists.txt`, `package.json`, `Cargo.toml`, `go.mod`, `pom.xml`, `build.gradle`, `Dockerfile`.
4. Examine shebang lines: `#!/usr/bin/env python3`, `#!/bin/bash`.
5. Look for CLI argument parsers: `argparse`, `click`, `typer`, `commander`, `cobra`, `urfave/cli`.

### Eval Cases
- [ ] Given `src/main.py` with no documentation, user identifies it as entry by shebang + `if __name__` guard
- [ ] Given `cmd/server/main.go`, user correctly names it as entry for a Go HTTP service
- [ ] Given `popinz-v2-rust/Cargo.toml` workspace root, user locates binary crates via `[[bin]]` sections
- [ ] Given `package.json` with `"main": "dist/index.js"`, user maps entry to TypeScript source via `"scripts": { "build": "tsc" }`
- [ ] Given `Makefile` with `all: build run`, user traces targets to infer build pipeline entry

---

## PHASE 2: DEPENDENCY GRAPH TRAVERSAL

### Strategy
1. Map imports/uses/requires at file level: `import`, `use`, `require`, `include`.
2. Distinguish third-party (std-lib, package-manager deps) from local imports.
3. Build directional graph: module A imports B → edge A→B (A depends on B).
4. Identify hub modules (imported by many) vs leaf modules (import few, exported widely).
5. Use package managers for dependency scope: `node_modules/`, `vendor/`, `target/debug/deps/`.

### Commands
```bash
# Rust: show crate dependencies
cargo tree --depth 1

# Node: show package.json deps
cat package.json | jq '.dependencies, .devDependencies'

# Python: show pip deps
pip freeze

# Go: show module deps
go mod graph
```

### Eval Cases
- [ ] User constructs local import graph for `popinz-v2-rust/crates/core/src/` in <5 minutes
- [ ] User distinguishes third-party from first-party imports in `popinz-admin/application/controllers/`
- [ ] User identifies hub module as most-imported local file across 50-file Rust crate
- [ ] User uses `cargo tree -i crate-name` to find reverse dependencies of a specific crate
- [ ] User identifies circular dependency between two modules via import graph inspection

---

## PHASE 3: NAMING CONVENTION INFERENCE

### Strategy
1. Detect casing: `snake_case` (Python, Rust), `camelCase` (JS, TypeScript, Java), `PascalCase` (TypeScript classes, Rust structs, Go packages), `kebab-case` (CLI flags, file names).
2. Detect prefix/suffix patterns: `I*` interface prefix (Java, TypeScript), `*_t` type suffix (C), `m_` member prefix (C++), `set_`, `get_`, `is_`, `has_` accessors.
3. Identify domain terminology: specific jargon unique to the codebase (e.g., "tenant", "subscription", "pipeline", "stage").
4. Map acronyms: `cfg` (config), `ctx` (context), `msg` (message), `hdr` (header), `auth` (authentication), `pwd` (password).
5. Detect plural/singular conventions for collections.

### Eval Cases
- [ ] User infers snake_case + plural collection naming from Python file names in `tests/fixtures/`
- [ ] User decodes `IUserService` → TypeScript interface, `UserServiceImpl` → implementation class
- [ ] User recognizes `tenant_id`, `org_uuid` as domain key fields by consistent column/field patterns
- [ ] User maps `hdl`, `proc`, `svc`, `repo` to handler, processor, service, repository by convention
- [ ] User distinguishes entity files from utility files by naming pattern in `proto/` directory

---

## PHASE 4: ARCHITECTURE LAYER DETECTION

### Strategy
1. Inspect directory structure: layer by folder naming (e.g., `controllers/`, `services/`, `models/`, `repositories/`).
2. Detect framework-vs-business boundary: framework code in `vendor/`, `node_modules/`, `target/` vs application code in `src/`, `app/`.
3. Identify hexagonal/ports-and-adapters markers: `ports/`, `adapters/`, `domain/`, `application/`, `infrastructure/`.
4. Look for configuration vs runtime separation: `config/`, `env/`, `*.config.*` vs `src/`, `lib/`.
5. Detect middleware layers: HTTP handlers → middleware → controller → service → repository.

### Eval Cases
- [ ] User identifies 3-layer MVC pattern in `popinz-admin/application/` by folder layout
- [ ] User detects hexagonal architecture in `popinz-v2-rust/crates/domain/` by `ports/` and `adapters/` subdirs
- [ ] User maps request lifecycle: `handler` → `service` → `repository` in a Rust gRPC service
- [ ] User distinguishes shared library crate from binary crate by `Cargo.toml` `[lib]` vs `[[bin]]`
- [ ] User identifies `proto/` as schema/codegen layer separate from implementation

---

## PHASE 5: DEAD CODE IDENTIFICATION

### Strategy
1. Search for code paths that cannot be reached: no function calls to exported function, no return statement, infinite loops without break.
2. Check for unused exports: `pub` items never imported elsewhere, `export` statements never used.
3. Look for commented-out code blocks: large comment blocks, commented function signatures.
4. Identify placeholder stubs: `TODO`, `FIXME`, `NotImplementedError`, `panic!("unimplemented")`.
5. Detect feature-gated code: `#[cfg(test)]`, `#ifdef DEBUG`, `if const { unreachable!() }`.

### Commands
```bash
# Rust: find unused functions
cargo clippy -- -W unused-function

# Python: find unreachable code
python -m pyflakes .

# TypeScript: find unused exports (requires tsconfig)
npx tsc --noEmit --stripInternal

# Go: find dead code
staticcheck ./...
```

### Eval Cases
- [ ] User finds `pub fn unused_helper()` in Rust crate with zero internal calls
- [ ] User identifies `// TODO: remove before prod` comment as marker for dead code path
- [ ] User detects `#[cfg(test)]` block containing production-only logic as dead code
- [ ] User locates PHP class never instantiated via grep across `application/controllers/`
- [ ] User flags `NotImplementedException` in `popinz-admin/` as dead branch confirmed by grep

---

## PHASE 6: CODE SMELL PATTERNS

### Strategy
1. Detect God objects: files >500 lines with many responsibilities (import many unrelated modules).
2. Detect feature envy: class A calls many methods on class B → B's behavior should be in B.
3. Detect data clumps: same three fields appear together across many structs/classes.
4. Detect shotgun surgery: one behavior change requires edits in many files.
5. Detect long parameter lists: functions with >5 parameters → introduce parameter object.
6. Detect deeply nested callbacks: >3 levels of async callbacks or nested lambdas.
7. Detect magic numbers: hardcoded numeric literals without named constants.

### Eval Cases
- [ ] User flags a 600-line `UserService.php` that handles auth, validation, persistence, and email
- [ ] User detects `OrderController` calling 12 methods on `CustomerService` → feature envy
- [ ] User identifies `tenant_id + org_uuid + user_token` appearing as fields in 4+ structs
- [ ] User notes one `changeUserRole` API touch 7 files across 4 directories → shotgun surgery
- [ ] User flags `calculatePrice(items, 0.15, 30, 100, true)` with 5 positional params

---

## PHASE 7: COMPLEXITY HOTSPOTS

### Strategy
1. Count cyclomatic complexity: branching per function (`if`, `match`, `for`, `while`, `&&`, `||`).
2. Measure function length: functions >50 lines (or >100 for data transformation) are hotspots.
3. Identify deep nesting: >4 levels of `if`/`match` nesting within a function.
4. Track state mutation: functions that modify >3 mutable fields are complex.
5. Evaluate cognitive load: long parameter lists + nested conditions + side effects = high complexity.
6. Use static analysis tools: `radon`, `complexity`, `eslint`, `clippy`, `gometalinter`.

### Commands
```bash
# Python: cyclomatic complexity
pip install radon && radon cc ./src -a -s

# JavaScript: cyclomatic complexity
npx eslint --rule 'complexity: [error, 10]' ./src

# Rust: complexity warnings
cargo clippy -- -W clippy::cyclomatic_complexity

# Go: function length
gofmt -r 'func length > 50' ./...
```

### Eval Cases
- [ ] User identifies `src/price_engine.py` with cyclomatic complexity 18 via `radon cc`
- [ ] User flags a 250-line `main()` function in a Go CLI tool
- [ ] User detects 6-level nested `match` arms in a Rust protocol handler
- [ ] User finds `processWebhook()` mutating 5 shared state variables
- [ ] User reports `radon cc -a` output showing top-5 complex functions in a Python module

---

## PHASE 8: STRUCTURAL SUMMARY OUTPUT

### Format
After tracing, produce:
```
## [repo-name] Structure Summary

ENTRY: [file(s)]
ARCH: [pattern: MVC / hexagonal / layered / microkernel / ...]
LAYERS: [list detected layers]
HUBS: [most-imported modules]
COMPLEXITY-HOTSPOTS: [file:line — reason]
DEAD-CODE: [file:line — reason]
SMELLS: [file:line — pattern]
DOMAIN-VOCABULARY: [inferred terms table]
```

### Eval Cases
- [ ] User produces valid structural summary for `popinz-v2-rust/` in <15 minutes
- [ ] User produces valid structural summary for `popinz-admin/` in <15 minutes
- [ ] User produces valid structural summary for `popinz-web/` in <15 minutes
- [ ] Structural summary correctly identifies entry, layers, hubs, and top 3 complexity hotspots
- [ ] Domain vocabulary includes at least 5 inferred terms with their meanings

---

## PERFORMANCE TARGET
- Orient in 50-file codebase: <10 min
- Orient in 200-file codebase: <30 min
- Orient in 500+ file monorepo: <60 min

---

## TOOLS
- grep, ripgrep, find
- tree, ls, wc
- Language-specific: cargo, npm, pip, go
- Static analysis: radon, eslint, clippy, staticcheck, pyflakes
- Import graph: cargo tree, go mod graph, webpack --mode production --stats

---

## CONSTRAINTS
- Do NOT execute code during trace
- Do NOT install packages to trace
- Do NOT modify files
- Assume telegraphic English output
