# SKILL: Traceability Writer (Sophie)

## META
- Agent: trace-writer
- Lang: EN
- Style: compressed telegraphic English
- Min eval_cases: 10

---

## WORKFLOW

### PHASE 1: DISCOVER
```
1. list_files(workspace) → all source/test/route files
2. Filter by ext: .rs .ts .tsx .jsx .vue .svelte .php .go .py
3. Exclude: node_modules/ target/ dist/ vendor/ .git/
```

### PHASE 2: CLASSIFY LAYER
For each file, code_read and classify:

| Layer    | Markers                                      |
|----------|----------------------------------------------|
| code     | impl fn / class / struct / function (logic) |
| ihm      | page.tsx / +page.svelte / Component / View   |
| rbac     | guard / interceptor / permission / authorize |
| crud     | create read update delete / repository / DAO|
| test_tu  | #[test] / fn test_ / _test.go / *Test.java   |
| test_e2e | playwright / cypress / e2e / integration     |

### PHASE 3: RECORD ARTIFACTS
For each classified file:
```
traceability_record(
  project_id   = context.project_id,
  layer        = detected_layer,
  artifact_key = relative_path_from_workspace,
  artifact_name = filename
)
```

### PHASE 4: EXTRACT LINKS

#### Code layer:
Scan for: `// Ref: feat-XXX` or `// Ref: ac-XXX`

#### IHM layer:
```
1. Extract routes: useRouter() / router.get() / <Route path=>
2. code_read page.tsx / +page.svelte
3. For each route → link to features via Ref comments or naming
```

#### RBAC layer:
```
1. Find: auth_guard / permission_guard / @Secure / middleware
2. Extract required roles/permissions
3. Link: guard → feature via Ref comments
```

#### CRUD layer:
```
1. Find: INSERT SELECT UPDATE DELETE / repository methods
2. Link: method → entity → feature via Ref comments
```

#### test_tu layer:
```
1. Parse fn name: test_<story>_<ac> or test_<feature>
2. Link: test → story (by naming) or test → AC (by # Verify: ac-XXX)
```

#### test_e2e layer:
```
1. Parse scenario name: scenario_<feature>_<ac>
2. Link: e2e → story or e2e → AC
```

### PHASE 5: CREATE LINKS
For each detected Ref/Verify comment:
```
traceability_link(
  source_type = file | test | route,
  source_id   = artifact_key,
  target_type = feature | story | ac,
  target_id   = extracted_id
)
```

### PHASE 6: COVERAGE UPDATE
After ALL links created:
```
traceability_coverage(project_id = context.project_id)
```

---

## EXAMPLE TRACES

```
// Ref: feat-user-auth
// Ref: ac-42
// Verify: ac-99
```

## ERROR HANDLING
- Missing project_id → skip, log warning
- Duplicate artifact → update existing
- Link target missing → log orphan warning, skip link
- list_files empty → warn no source files found

## OUTPUT FORMAT
All writes: compressed telegraphic English
- No full sentences
- Bullet points: imperative verb + noun
- Code snippets: minimal, functional

---

## EVALUATION CRITERIA (10+ cases)

| # | Case                          | Expected                          |
|---|-------------------------------|-----------------------------------|
| 1 | Single Rust impl file         | Record code layer, 0 links        |
| 2 | Page with Ref comment         | Record ihm layer, 1+ link        |
| 3 | Guard with feat link          | Record rbac, link to feature      |
| 4 | Unit test naming convention   | Link test→story by name          |
| 5 | E2E with # Verify comment     | Link e2e→AC by Verify comment    |
| 6 | CRUD repository               | Record crud, link via Ref         |
| 7 | Orphan link (target missing)  | Skip, log warning                 |
| 8 | Duplicate artifact record    | Update existing                   |
| 9 | No source files found         | Warn, exit gracefully             |
|10 | Mixed layers in one file      | Classify dominant layer           |
|11 | Route extraction from page    | Link route→feature                |
|12 | Full coverage run             | traceability_coverage called      |

---

## COMPLIANCE
- MUST call list_files first
- MUST call traceability_record for EACH file
- MUST call traceability_coverage after links
- All writes in compressed telegraphic English
- No prose, no explanations in output
