name: trace-auditor
description: Traceability audit across 13-layer chain. VETO if any layer <50%.
commands:
  - id: legacy_scan
    description: Inventory all source files with UUIDs in workspace
    args:
      workspace: string
    returns: "{ files: [{ path, uuid, type }] }"
  - id: traceability_coverage
    description: Get 13-layer coverage for project
    args:
      project_id: string
    returns: "{ layers: { epic, persona, feature, story, ac, ihm, code, tu, e2e, crud, rbac, screen, nft }, coverage_pct }"
  - id: traceability_validate
    description: Check chain integrity (orphans, gaps)
    args:
      project_id: string
    returns: "{ orphans: [], gaps: [{ from, to, layer }] }"
  - id: traceability_link
    description: Create missing traceability link
    args:
      from_artifact: string
      to_artifact: string
      layer: string
    returns: "{ link_id, status }"
  - id: code_read
    description: Read source file content
    args:
      path: string
    returns: string

workflow:
  steps:
    - run: legacy_scan
      args:
        workspace: "${WORKSPACE}"
      save: legacy_files

    - run: traceability_coverage
      args:
        project_id: "${PROJECT_ID}"
      save: coverage

    - run: traceability_validate
      args:
        project_id: "${PROJECT_ID}"
      save: validation

    - for_each: gap in validation.gaps
      run: traceability_link
      args:
        from_artifact: "${gap.from}"
        to_artifact: "${gap.to}"
        layer: "${gap.layer}"

    - for_each: file in legacy_files.files
      when: file.type == "source"
      run: code_read
      args:
        path: "${file.path}"
      save: file_content
      extract:
        pattern: "// Ref: feat-\\d+"
        artifacts: artifact_refs

    - build_traceability_map:
        source_refs: artifact_refs
        files: legacy_files.files

    - veto_check:
        layers: coverage.layers
        threshold: 50
        coverage: coverage

    - report:
        coverage_pct: coverage.layers
        veto: veto_check.vetoed
        orphans: validation.orphans
        gaps_fixed: count(validation.gaps)

eval_cases:
  - id: 1
    prompt: "Audit project prj-001. Report coverage per layer. Veto if any layer <50%."
    checks:
      - legacy_scan called with workspace
      - traceability_coverage called with project_id
      - traceability_validate called
      - coverage_pct reported per layer
    expectations:
      - all 13 layers reported
      - veto=true if any layer<50

  - id: 2
    prompt: "Fix all gaps in prj-002 traceability chain."
    checks:
      - traceability_validate returns gaps
      - traceability_link called for each gap
    expectations:
      - all gaps resolved
      - link_id returned per gap

  - id: 3
    prompt: "Scan legacy codebase /src/old for UUIDs. Map to artifacts."
    checks:
      - legacy_scan called with /src/old
      - code_read called on each source file
    expectations:
      - all source files inventoried
      - // Ref: feat-XXXX extracted

  - id: 4
    prompt: "VETO check prj-003: layers={code:45,ihm:60,test_tu:30,test_e2e:70,crud:55,rbac:80,screen:40,nft:90}."
    checks:
      - veto_check threshold=50
      - layer values extracted
    expectations:
      - veto=true (code=45<50, test_tu=30<50, screen=40<50)

  - id: 5
    prompt: "Extract artifact refs from /app/src/*.rs files."
    checks:
      - code_read on each .rs file
      - pattern "// Ref: feat-\\d+" matched
    expectations:
      - all feat-XXXX refs captured
      - mapped to source file path

  - id: 6
    prompt: "Report coverage for Epic→Persona→Feature→Story→AC chain."
    checks:
      - coverage.layers includes epic,persona,feature,story,ac
    expectations:
      - 5 layers reported with pct values

  - id: 7
    prompt: "Check IHM→Code→TU→E2E traceability."
    checks:
      - ihm,code,tu,e2e coverage checked
      - orphans identified
    expectations:
      - 4 layers with pct
      - orphan list populated

  - id: 8
    prompt: "Validate CRUD→RBAC→Screen→NFT layer chain."
    checks:
      - crud,rbac,screen,nft coverage checked
      - gaps between layers identified
    expectations:
      - 4 layers with pct
      - gaps list complete

  - id: 9
    prompt: "Full 13-layer audit for prj-004 with gap fixing."
    checks:
      - all 13 layers reported
      - gaps fixed via traceability_link
      - veto applied if needed
    expectations:
      - all 13 coverage_pct values
      - all gaps resolved
      - veto=false

  - id: 10
    prompt: "Orphan check: prj-005 has code files with no artifact refs."
    checks:
      - orphan detection via traceability_validate
      - legacy_scan finds orphaned files
    expectations:
      - orphans list non-empty
      - orphaned files listed

  - id: 11
    prompt: "VETO check all layers >50%: code=51,ihm=55,test_tu=52,test_e2e=60,crud=70,rbac=80,screen=60,nft=95."
    checks:
      - all layer values >=50
    expectations:
      - veto=false

  - id: 12
    prompt: "Edge case: empty project prj-006 has no files, no artifacts."
    checks:
      - legacy_scan returns empty
      - coverage returns all 0 or null
    expectations:
      - coverage_pct=0 for all
      - veto=true

  - id: 13
    prompt: "Mixed veto: screen=49, nft=48, all others >70."
    checks:
      - screen and nft below threshold
    expectations:
      - veto=true
      - failing layers: screen, nft
