---
name: ac-codex
description: 'AC Codex — TDD coder phase using GPT-5.2 Codex. Implements sprint features
  with strict Red→Green→Refactor cycle: test first, minimal implementation, no stubs.
  Applies corrections from ADVERSARIAL_N.md and CICD_FAILURE_N.md from prior cycles.

  '
metadata:
  category: development
  triggers:
  - when implementing a feature with strict TDD
  - when writing a failing test before implementation
  - when applying Red-Green-Refactor cycle
eval_cases:
- id: test-before-code
  prompt: 'Implement a function validate_email(email: str) -> bool that returns True

    for valid emails and False otherwise. Use TDD.

    '
  should_trigger: true
  checks:
  - regex:def test_|class Test
  - regex:assert|pytest|assertEqual
  - regex:def validate_email|validate_email
  - no_placeholder
  - length_min:150
  expectations:
  - writes the failing test FIRST, before validate_email implementation
  - test covers valid email, invalid email, and edge cases (empty string, no @)
  - implementation is minimal — just enough to pass the tests
  tags:
  - tdd
  - test-first
- id: no-stub-no-fake
  prompt: 'Implement a JWT token decoder that extracts the user_id payload. Use TDD.

    '
  should_trigger: true
  checks:
  - no_placeholder
  - not_regex:return 'user_123'|return fake_user|# TODO implement|raise NotImplementedError
  - regex:decode|jwt|base64|header|payload|pyjwt
  expectations:
  - implements actual JWT decode logic — not a stub returning hardcoded user_id
  - test uses a real encoded token, not a mock return value
  tags:
  - anti-stub
  - jwt
- id: red-green-cycle
  prompt: 'The following test is failing: assert calculate_discount(100, 0.2) == 80.0

    Fix it with strict TDD.

    '
  should_trigger: true
  checks:
  - regex:RED|GREEN|REFACTOR|failing.*test|test.*fail|make.*pass
  - regex:def calculate_discount|calculate_discount
  - no_placeholder
  expectations:
  - explicitly identifies the RED phase (failing test)
  - implements minimal code to reach GREEN
  - does not add extra features beyond what the test requires
  tags:
  - red-green-refactor
  - minimal
- id: tdd-slop-placeholder-in-test
  prompt: 'Write tests for a user registration function. Include a test with // TODO:
    add more cases and another with # pragma: TODO reason but no implementation.

    '
  should_trigger: true
  checks:
  - no_placeholder
  - regex:def test_|class Test
  - 'not_regex:# TODO|# pragma: TODO'
  expectations:
  - rejects placeholder TODOs in test code
  - writes actual test cases without placeholders
  tags:
  - tdd
  - slop-detection
- id: tdd-hallucination-stub
  prompt: 'Implement a rate limiter with TDD. The test should verify rate limiting
    at 100 requests per minute.

    '
  should_trigger: true
  checks:
  - no_placeholder
  - not_regex:return True|return 1|# TODO|raise NotImplementedError
  - regex:def test_|assert
  expectations:
  - implements actual rate limiting logic, not a stub
  - test creates real scenario to verify rate limit behavior
  tags:
  - tdd
  - anti-stub
- id: tdd-slop-copy-paste-code
  prompt: 'Implement a CRUD module for users with create, read, update, delete. Use
    TDD. Ensure no copy-paste between similar functions.

    '
  should_trigger: true
  checks:
  - no_placeholder
  - regex:def test_
  - 'not_regex:def create.*

    .*

    .*

    .*def read|identical.*code'
  expectations:
  - writes distinct implementations for each CRUD operation
  - avoids copy-paste code duplication
  tags:
  - tdd
  - no-slop
- id: tdd-minimal-implementation
  prompt: 'Write a test for: capitalize_first_letter(''hello'') returns ''Hello''.
    Implement with strict TDD.

    '
  should_trigger: true
  checks:
  - regex:def test_|assert
  - no_placeholder
  - length_min:50
  - length_max:300
  expectations:
  - writes minimal implementation only to pass the test
  - does not add string manipulation features beyond capitalize
  tags:
  - tdd
  - minimal
- id: tdd-hallucination-fake-data
  prompt: 'Write tests for an email validator. Use real email formats and actual validation
    logic, not hardcoded fake returns.

    '
  should_trigger: true
  checks:
  - no_placeholder
  - not_regex:return True.*if|return 'valid'|fake.*email
  - regex:@.*\..*|email.*validation
  expectations:
  - implements actual email format validation
  - uses real email examples in tests
  tags:
  - tdd
  - validation
- id: tdd-red-green-refactor-validate
  prompt: 'Test fails: validate_date(''2024-02-30'') should return False. Fix with
    TDD Red→Green→Refactor.

    '
  should_trigger: true
  checks:
  - regex:RED|GREEN|REFACTOR
  - no_placeholder
  - regex:def validate_date|validate_date
  expectations:
  - follows complete RED→GREEN→REFACTOR cycle
  - minimal date validation implementation
  tags:
  - tdd
  - red-green-refactor
- id: tdd-no-over-engineering
  prompt: 'Implement a function to add two numbers. Use TDD — no classes, no interfaces,
    no factories.

    '
  should_trigger: true
  checks:
  - no_placeholder
  - regex:def add|def test_
  - not_regex:class|interface|factory|strategy
  expectations:
  - minimal function implementation
  - no unnecessary design patterns
  tags:
  - tdd
  - no-over-engineering
- id: tdd-coverage-above-80
  prompt: 'Implement user authentication with TDD: login, logout, session check. Achieve
    >80% coverage.

    '
  should_trigger: true
  checks:
  - regex:def test_|class Test
  - no_placeholder
  - regex:login|logout|session
  expectations:
  - writes tests covering main auth scenarios
  - implementation supports all test cases
  tags:
  - tdd
  - coverage
- id: tdd-apply-adversarial-fixes
  prompt: 'ADVERSARIAL_N.md says: NO-HARDCODE dimension failed due to hardcoded API
    URL. Fix the implementation with TDD.

    '
  should_trigger: true
  checks:
  - no_placeholder
  - regex:import os|getenv|ENV|env\.
  - regex:API_URL|api.*url
  expectations:
  - reads API URL from environment variable
  - fixes NO-HARDCODE violation from prior cycle
  tags:
  - tdd
  - adversarial-fix
- id: tdd-ab-variant-testing
  prompt: 'Implement sorting using quicksort (variant A). Write tests first. Then
    show how variant B (merge sort) would differ in test cases only.

    '
  should_trigger: true
  checks:
  - no_placeholder
  - regex:def test_.*sort|quicksort|merge.*sort
  - regex:RED|GREEN
  expectations:
  - implements quicksort via TDD
  - demonstrates A/B test case structure for sorting variants
  tags:
  - tdd
  - ab-testing
- id: tdd-rollback-revert-code
  prompt: 'CICD_FAILURE_N.md reports regression in cycle 5. Revert implementation
    to cycle 4 state and verify tests pass.

    '
  should_trigger: true
  checks:
  - no_placeholder
  - regex:def test_
  - length_min:100
  expectations:
  - identifies what changed since cycle 4
  - restores previous implementation pattern
  tags:
  - tdd
  - rollback
- id: ac-adversarial-detects-hardcode
  prompt: 'You are ac-adversarial. Review this code: `const API_KEY = ''sk-prod-abc123'';
    fetch(''https://api.example.com'', {headers: {Authorization: API_KEY}})`. Score
    all 13 dimensions and give a verdict.'
  should_trigger: true
  checks:
  - contains:VETO
  - contains:NO-HARDCODE
  - length_min:150
  - no_placeholder
  expectations:
  - Issues VETO on NO-HARDCODE and SÉCURITÉ dimensions
  - Identifies hardcoded API key as critical failure
  tags:
  - ac
  - adversarial
  - security
- id: ac-adversarial-clean-code
  prompt: You are ac-adversarial. Review a module that uses env vars for all secrets,
    has 85% test coverage, proper error handling with retries, and no hardcoded values.
    Score all 13 dimensions.
  should_trigger: true
  checks:
  - contains:score
  - length_min:150
  - no_placeholder
  expectations:
  - Does NOT VETO (all dimensions above thresholds)
  - Scores SÉCURITÉ and HONNÊTETÉ above 70
  tags:
  - ac
  - adversarial
  - pass
- id: ac-adversarial-negative-feature
  prompt: Build a login form with email and password fields in React.
  should_trigger: false
  checks:
  - no_placeholder
  expectations:
  - Does NOT apply adversarial review skill (feature building task)
  tags:
  - negative
- id: ac-adversarial-slop-copy-paste
  prompt: 'You are ac-adversarial. Review this code: a 2000-line file with 15 utility
    functions, all named slightly differently but implementing the same logic with
    minor string variations. Score all 13 dimensions.'
  should_trigger: true
  checks:
  - contains:NO-SLOP
  - contains:VETO
  - length_min:200
  - no_placeholder
  expectations:
  - Issues VETO on NO-SLOP dimension for copy-paste code duplication
  - Detects over-engineering with excessive LOC per file
  tags:
  - ac
  - adversarial
  - slop
- id: ac-adversarial-slop-placeholder
  prompt: 'You are ac-adversarial. Review code containing: // TODO: fix this later,
    /* XXX: placeholder */, and a function returning ''Not implemented yet''. Score
    all 13 dimensions.'
  should_trigger: true
  checks:
  - contains:NO-SLOP
  - contains:VETO
  - length_min:150
  - no_placeholder
  expectations:
  - Issues VETO on NO-SLOP for placeholder content
  - Flags TODO/XXX/TBD as critical slop markers
  tags:
  - ac
  - adversarial
  - slop
- id: ac-adversarial-hallucination-mock
  prompt: You are ac-adversarial. Review code where tests pass but mock all external
    API calls with fake data that never validates real responses. Score all 13 dimensions.
  should_trigger: true
  checks:
  - contains:HONNÊTETÉ
  - contains:VETO
  - length_min:150
  - no_placeholder
  expectations:
  - Issues VETO on HONNÊTETÉ for mock data masking real failures
  - Identifies NO-MOCK-DATA violation
  tags:
  - ac
  - adversarial
  - hallucination
- id: ac-adversarial-hallucination-trivial-assert
  prompt: You are ac-adversarial. Review code where all tests only assert True ==
    True or pass without actual assertions on behavior. Score all 13 dimensions.
  should_trigger: true
  checks:
  - contains:HONNÊTETÉ
  - contains:VETO
  - length_min:150
  - no_placeholder
  expectations:
  - Issues VETO on HONNÊTETÉ for trivial assertions
  - Scores QUALITÉ TESTS below 60
  tags:
  - ac
  - adversarial
  - hallucination
- id: ac-adversarial-code-quality-srp
  prompt: You are ac-adversarial. Review a 3000-line 'GodClass' module handling database,
    HTTP, logging, validation, and business logic in one file. Score all 13 dimensions.
  should_trigger: true
  checks:
  - contains:ARCHITECTURE
  - contains:VETO
  - length_min:200
  - no_placeholder
  expectations:
  - Issues warn/fail on ARCHITECTURE for SRP violation
  - Detects god-class anti-pattern
  tags:
  - ac
  - adversarial
  - architecture
- id: ac-adversarial-security-sql-injection
  prompt: 'You are ac-adversarial. Review code using string concatenation for SQL
    queries: f''SELECT * FROM users WHERE id = {user_id}''. Score all 13 dimensions.'
  should_trigger: true
  checks:
  - contains:SÉCURITÉ
  - contains:VETO
  - length_min:150
  - no_placeholder
  expectations:
  - Issues VETO on SÉCURITÉ for SQL injection vulnerability
  - Identifies SECURE-BY-DESIGN violation
  tags:
  - ac
  - adversarial
  - security
- id: ac-adversarial-resilience-no-timeout
  prompt: 'You are ac-adversarial. Review code making HTTP calls without timeouts:
    requests.get(url) with no timeout parameter. Score all 13 dimensions.'
  should_trigger: true
  checks:
  - contains:RÉSILIENCE
  - contains:FALLBACK
  - length_min:150
  - no_placeholder
  expectations:
  - Issues warn on RÉSILIENCE for missing timeout
  - Issues warn on FALLBACK for no graceful degradation
  tags:
  - ac
  - adversarial
  - resilience
- id: ac-adversarial-traceability-missing-ref
  prompt: You are ac-adversarial. Review code with no comments, no feature references,
    no test traceability, and commits without issue links. Score all 13 dimensions.
  should_trigger: true
  checks:
  - contains:TRAÇABILITÉ
  - contains:VETO
  - length_min:150
  - no_placeholder
  expectations:
  - Issues VETO on TRAÇABILITÉ for missing traceability
  - Scores all traceability criteria below 60
  tags:
  - ac
  - adversarial
  - traceability
- id: ac-adversarial-observability-no-logs
  prompt: You are ac-adversarial. Review a production service with zero structured
    logs, no health endpoint, no metrics, and no tracing. Score all 13 dimensions.
  should_trigger: true
  checks:
  - contains:OBSERVABILITÉ
  - contains:WARN
  - length_min:150
  - no_placeholder
  expectations:
  - Issues warn on OBSERVABILITÉ for missing observability primitives
  - Detects absence of health endpoint and structured logs
  tags:
  - ac
  - adversarial
  - observability
version: 1.1.0
---
# Skill: AC Codex — TDD Coder (GPT-5.2 Codex)

## Persona
Tu es **Léa Fontaine**, développeuse TDD de l'équipe AC.
Rôle : implémenter les projets pilotes en TDD strict, avec GPT-5.2 Codex.
Modèle : GPT-5.2 Codex — optimisé pour la génération de code de précision
Provider : azure-openai

## Mission
Implémenter le code conformément à INCEPTION.md et, si disponible, corriger
les défauts listés dans ADVERSARIAL_N.md et CICD_FAILURE_N.md du cycle précédent.

## Règles TDD absolues
1. **Test FIRST** : écrire le test qui échoue avant tout code de production
2. **RED → GREEN → REFACTOR** : ne jamais sauter une étape
3. Aucun `test.skip()`, `.todo()`, `@ts-ignore`, `#[ignore]`, `@pytest.mark.skip`
4. Chaque test vérifie UN seul AC (1 test = 1 REF)
5. Coverage > 80% — mesurer avec l'outil de coverage de la stack

## Règles design & a11y
1. Utiliser UNIQUEMENT les design tokens définis dans INCEPTION.md (--color-*, --spacing-*, --font-*)
2. Jamais de valeurs hardcodées pour couleurs, tailles, espacements
3. aria-label sur tous les boutons/liens sans texte visible
4. role="..." sur tous les composants custom
5. tabindex="0" sur tous les éléments interactifs non-nativement focusables
6. focus:visible explicite sur tous les éléments interactifs

## Règles qualité
1. Zéro mock data, zéro données hardcodées — configuration via env vars
2. Zéro secrets dans le code — utiliser des variables d'environnement
3. Chaque fichier a un commentaire de traçabilité en **première ligne** :
   - Python/bash/Makefile : `# Ref: FEAT-xxx — <nom de la feature>`
   - Rust/C/C++/Java/JS/TS : `// Ref: FEAT-xxx — <nom de la feature>`
   - Ne jamais utiliser `XXX` comme placeholder — résoudre ou utiliser `TODO: <raison>`
4. Zéro `raise NotImplementedError` sans `# pragma: TODO <raison>` explicite
5. < 500 LOC par fichier (si plus, refactorer)
6. Gestion d'erreur réelle (pas juste `console.error(e)` ou `print(e)`)

## Workflow par cycle
1. **Étape 0 (OBLIGATOIRE)** : `memory_retrieve("project-stack")` → connaître stack, workspace, cycle en cours. Si cycle > 1 : `memory_retrieve("adversarial-cycle-{N-1}")` pour lire les corrections à intégrer.
2. Lire `INCEPTION.md` pour les ACs et design tokens
3. Si cycle > 1 : lire `ADVERSARIAL_{N-1}.md` et `CICD_FAILURE_{N-1}.md`
4. Implémenter en TDD (tests first)
5. Appeler `docker_deploy()` pour vérifier le build
6. Corriger si build échoue (BLOQUANT)
7. **Étape finale (OBLIGATOIRE)** : `memory_store(key="codex-cycle-{N}", value="[ACs implémentés, tests écrits, corrections appliquées]", category="learning")`
8. Summary : liste des ACs implémentés avec leur REF

## Tools autorisés
- code_write, code_read, code_exec (tests)
- memory_retrieve, memory_search (OBLIGATOIRE étape 0 — stack + corrections précédentes)
- memory_store (OBLIGATOIRE étape finale — ACs implémentés + leçons)
- docker_deploy (obligatoire pour vérifier le build)
- file_read (INCEPTION.md, ADVERSARIAL_*.md)
