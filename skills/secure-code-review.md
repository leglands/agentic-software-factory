name: secure-code-review
description: Security-critical code review for agent safety assessments. Evaluates OWASP Top 10, injection, auth bypass, secrets, validation, encoding, CSP, CORS, error disclosure.
trigger: code_review, security, vulnerability, audit, pentest
version: 1.0

## SECURE CODE REVIEW WORKFLOW

### PHASE 1: STATIC ANALYSIS
1. Parse AST/IR for taint tracking
2. Map user inputs → sinks
3. Trace authentication/authorization flows
4. Detect hardcoded secrets

### PHASE 2: OWASP TOP 10 CHECKS
1. A01 Broken Access Control → IDOR, privilege escalation, path traversal
2. A02 Cryptographic Failure → weak crypto, hardcoded keys, insecure RNG
3. A03 Injection → SQL, NoSQL, OS, Command, LDAP, XSS, SMTP
4. A04 Insecure Design → business logic flaws, race conditions
5. A05 Security Misconfiguration → default creds, debug mode, missing hardening
6. A06 Vulnerable Components → outdated deps, known CVEs
7. A07 Auth Failures → weak passwords, session fixation, missing MFA
8. A08 Data Integrity Failures → XXE, deserialization, supply chain
9. A09 Logging Failures → missing logs, log injection, insufficient audit
10. A10 SSRF → URL validation, redirect validation

### PHASE 3: INJECTION PATTERNS
```
SQL: SELECT/INSERT/UPDATE/DELETE + user_input → EXEC
NoSQL: $where, $function, eval() + user_input
OS: exec(), system(), popen(), shell_exec() + user_input
Command: | ; $ & ` 
LDAP: *, ), DN traversal
XSS: innerHTML, eval(), document.write(), dangerouslySetInnerHTML
SMTP: RCPT, FROM headers + user_input
XXE: XML parsing with external entities
Deserialization: pickle, yaml, xml, json
```

### PHASE 4: AUTH BYPASS DETECTION
- Missing authorization checks on sensitive endpoints
- IDOR via predictable IDs (UUID v1, auto-increment)
- Parameter tampering for privilege escalation
- JWT none algorithm attack
- Missing role validation
- Time-of-check to time-of-use (TOCTOU)

### PHASE 5: SECRET LEAKS
```
Hardcoded: api_key, password, secret, token, credential, private_key
Env exposure: process.env, getenv, os.environ, System.getenv
Log leakage: console.log, print, logger.*, System.out
Config exposure: config file, .env, settings.ini
Source comment: TODO: password, HACK, BUG, temporary
```

### PHASE 6: INPUT VALIDATION
- Null/NIL check on required fields
- Type validation (int, string, array, object)
- Length bounds (min/max)
- Range validation (numeric, date)
- Format validation (regex, schema, enum)
- Whitelist vs blacklist (prefer whitelist)
- File type validation (magic bytes, extension)
- URL/URI validation

### PHASE 7: OUTPUT ENCODING
```
HTML: < → &lt;, > → &gt;, & → &amp;, " → &quot;
URL: space → %20, special chars percent-encoding
JavaScript: <script> tags, quote escaping
CSS: expression(), url(), hex encoding
SQL: parameterized queries only
XML: CDATA sections, entity encoding
JSON: XSS via <script> in string values
```

### PHASE 8: CSP HEADERS
```
Required directives:
- default-src 'self'
- script-src 'self' [nonce] [hash]
- object-src 'none'
- base-uri 'self'
- frame-ancestors 'none'
Dangerous:
- 'unsafe-inline' (bypasses XSS protection)
- 'unsafe-eval'
- data: protocol
- blob: protocol
```

### PHASE 9: CORS CONFIGURATION
```
Allowed origins: exact match or strict subdomain
Credentials: Access-Control-Allow-Credentials true → must specify origin
Methods: minimal set required
Headers: Access-Control-Allow-Headers whitelist
Max-age: reasonable TTL (prefer short)
Vary: Origin header required when dynamic
Dangerous: wildcard *, null origin
```

### PHASE 10: ERROR DISCLOSURE
```
Forbidden leak sources:
- Stack traces (production)
- File paths (exposes structure)
- Version numbers (library fingerprinting)
- SQL errors (schema exposure)
- Exception messages (logic inference)
- Debug endpoints (/debug, /actuator, /health)
Required:
- Custom error pages
- Generic messages for users
- Detailed logs server-side only
- 500 → generic 500.html
```

## OUTPUT FORMAT
```
SECURITY_REVIEW:
  severity: CRITICAL|HIGH|MEDIUM|LOW|INFO
  category: [from OWASP Top 10]
  file: <path>:<line>
  issue: <brief>
  finding: <code snippet>
  impact: <exploitation scenario>
  remediation: <secure alternative>
  references: [CVE, CWE, OWASP]
```

## EVAL_CASES

- id: "SCR-001"
  prompt: "Review auth middleware in api/middleware/auth.ts for privilege escalation"
  checks:
    - role validation present
    - IDOR prevention
    - token signature verification
    - session timeout
  expectations:
    - reject: "role: 'admin' hardcoded bypass"
    - reject: "user.id from request body without DB lookup"
    - reject: "JWT RS256 → HS256 algorithm confusion"
    - accept: "proper role hierarchy check"

- id: "SCR-002"
  prompt: "Audit database queries in services/user.rs for SQL injection"
  checks:
    - parameterized queries
    - ORM usage
    - input sanitization
    - LIKE clause escaping
  expectations:
    - reject: "format!(\"SELECT * FROM users WHERE id = {}\", user_input)"
    - reject: "raw sql interpolation"
    - accept: "sqlx::query(\"SELECT * FROM users WHERE id = $1\").bind(user_id)"

- id: "SCR-003"
  prompt: "Check config.rs for hardcoded secrets and credentials"
  checks:
    - env vars for all secrets
    - no default passwords
    - no API keys in source
    - .gitignore excludes secrets
  expectations:
    - reject: "password: String = \"admin123\""
    - reject: "api_key: &str = \"sk-...\""
    - accept: "password: env::var(\"DB_PASSWORD\").expect(\"DB_PASSWORD must be set\")"

- id: "SCR-004"
  prompt: "Review HTML rendering in templates/*.html for XSS"
  checks:
    - auto-escaping enabled
    - no dangerouslySetInnerHTML
    - no innerHTML assignments
    - no eval in template context
  expectations:
    - reject: "element.innerHTML = userInput"
    - reject: "dangerouslySetInnerHTML={{ __html: userContent }}"
    - accept: "{userContent}" (auto-escaped)

- id: "SCR-005"
  prompt: "Audit CORS config in server.rs for misconfiguration"
  checks:
    - no wildcard origin
    - credentials flag correct
    - methods whitelist
    - headers whitelist
  expectations:
    - reject: "Access-Control-Allow-Origin: *"
    - reject: "origin: \"*\" with credentials: true"
    - accept: "origin: \"https://app.example.com\" with credentials: true"

- id: "SCR-006"
  prompt: "Review error handling in handlers/*.rs for information disclosure"
  checks:
    - no stack traces to client
    - no file path leaks
    - custom error pages
    - structured logging server-side
  expectations:
    - reject: "e.backtrace().to_string() in response"
    - reject: "println!(\"Error: {:?}\", e) in prod"
    - accept: "log::error!(\"{:?}\", e); HttpResponse::InternalServerError().body(\"Error\")"

- id: "SCR-007"
  prompt: "Check file upload handler for path traversal and type validation"
  checks:
    - filename sanitization
    - path canonicalization
    - magic byte validation
    - extension whitelist
    - size limits
  expectations:
    - reject: "let path = format!(\"uploads/{}\", filename)"
    - reject: "extension.is_empty()"
    - accept: "Path::new(&filename).canonicalize().starts_with(UPLOAD_DIR)"

- id: "SCR-008"
  prompt: "Audit session management in auth/session.rs for session fixation/hijacking"
  checks:
    - secure cookie flags
    - session rotation on auth
    - session timeout
    - regenerate after privilege change
  expectations:
    - reject: "cookie: \"session_id=...\" without Secure, HttpOnly"
    - reject: "session ID in URL query param"
    - accept: "Cookie::build((name, id)).secure().http_only().same_site(SameSite::Strict).finish()"

- id: "SCR-009"
  prompt: "Review XXE prevention in XML parsing code for external entity injection"
  checks:
    - DTD disabled
    - external entities disabled
    - no document() function
    - safe XML parsing library
  expectations:
    - reject: "XmlParser { dtd: true, .. }"
    - reject: "<!ENTITY external SYSTEM \"file:///etc/passwd\">"
    - accept: "XmlParser { external_entities: false, dtd: false }"

- id: "SCR-010"
  prompt: "Check SSRF prevention in webhook/handler.rs for URL validation"
  checks:
    - allowlist for destinations
    - DNS rebinding protection
    - no follow redirects to arbitrary hosts
    - scheme validation (http/https only)
  expectations:
    - reject: "reqwest::get(user_url)"
    - reject: "redirects to private IP ranges"
    - accept: "validate_url_scheme(user_url)? && allowlist_check(user_url)?"

- id: "SCR-011"
  prompt: "Review CSP headers in middleware/security.rs for bypass prevention"
  checks:
    - no unsafe-inline
    - no unsafe-eval
    - object-src none
    - script-src restrict
    - base-uri set
  expectations:
    - reject: "Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'"
    - accept: "Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-{random}'; object-src 'none'"

- id: "SCR-012"
  prompt: "Audit deserialization in utils/parse.rs for unsafe deserialization"
  checks:
    - no pickle.loads()
    - no yaml.load() without SafeLoader
    - no jsonpickle
    - no XML decoders with XXE
  expectations:
    - reject: "pickle.loads(user_data)"
    - reject: "yaml.load(data) # arbitrary code exec"
    - accept: "yaml::load(data) with SafeLoader"
    - accept: "serde_json::from_str(data)"
