name: owasp-top-10-audit
description: OWASP Top 10 2025 security audit skill. Covers all 10 categories with check items, vulnerable code patterns, and remediation guidance. Use for code review, pentest prep, and security hardening. Compressed telegraphic English.
author: security-team
version: 1.0.0
tags: [security, audit, owasp, pentest, sast]

trigger_templates:
  - "audit security"
  - "owasp check"
  - "security review"
  - "penetration test prep"
  - "vulnerability scan"
  - "secure code review"

check_items:
  A01_BROKEN_ACCESS_CONTROL:
    name: "A01:2021 – Broken Access Control"
    description: |
      Access control enforces policy such that users cannot act outside intended permissions.
      Failures typically lead to unauthorized information disclosure, modification, or destruction.
    what_to_check:
      - Vertical privilege escalation (user acts as admin)
      - Horizontal privilege escalation (user accesses another user's resources)
      - Insecure direct object references (IDOR)
      - Missing function-level access control on API endpoints
      - CORS misconfiguration allowing unauthorized cross-origin requests
      - Forceful browsing to protected routes
      - API mass assignment overwriting read-only fields
      - Role manipulation via request parameters or tokens
      - Directory traversal / path traversal in file operations
      - Client-side enforcement only (no server-side validation)
    code_patterns:
      vulnerable:
        - id: vac-001
          pattern: "router.get('/admin', handler)  # no auth check"
          severity: critical
        - id: vac-002
          pattern: "SELECT * FROM orders WHERE id = $1 AND user_id = $2  # missing user check"
          severity: high
        - id: vac-003
          pattern: "res.sendFile(req.params.file)  # path traversal risk"
          severity: critical
        - id: vac-004
          pattern: "Access-Control-Allow-Origin: *  # overly permissive CORS"
          severity: high
        - id: vac-005
          pattern: "const role = req.user.role; if(role === 'admin')  # client-controlled role"
          severity: critical
        - id: vac-006
          pattern: "User.findByIdAndUpdate(id, req.body)  # mass assignment"
          severity: high
      safe:
        - pattern: "requireAuth(), requireRole('admin')"
        - pattern: "WHERE resource_owner_id = $1"
        - pattern: "validatePath(req.params.file, allowedDir)"
        - pattern: "Access-Control-Allow-Origin: https://trusted.example.com"
    remediation:
      - Deny by default; explicit allow for each resource
      - Implement access control matrices; enforce in centralized middleware
      - Validate object ownership on every request
      - Avoid exposing internal IDs; use indirect references (maps)
      - Log all access control failures; alert on anomalies
      - Rate-limit administrative endpoints
      - Never rely on client-side role/permission checks
      - Use scoped queries: always filter by current user's ownership

  A02_CRYPTO_FAILURES:
    name: "A02:2021 – Cryptographic Failures"
    description: |
      Failures related to cryptography which often lead to sensitive data exposure.
      Includes weak hashing, improper key management, use of broken algorithms.
    what_to_check:
      - Sensitive data transmitted in clear text (HTTP, unencrypted DB connections)
      - Weak or custom encryption algorithms (DES, ROT13, custom XOR)
      - Hardcoded encryption keys, secrets in source code
      - Insecure password hashing (MD5, SHA1 without salt)
      - Insufficient key length (RSA < 2048, symmetric < 128)
      - IV reuse in CBC mode
      - Missing TLS enforcement (hsts header absent)
      - ECB mode for encryption of structured data
      - Client-side crypto used instead of server-side
      - Default crypto keys in frameworks/libraries
    code_patterns:
      vulnerable:
        - id: vcf-001
          pattern: "bcrypt('password')  # missing cost factor"
          severity: high
        - id: vcf-002
          pattern: "const hash = md5(password)  # broken hash"
          severity: critical
        - id: vcf-003
          pattern: "const key = 'hardcoded-key-123'  # secret in code"
          severity: critical
        - id: vcf-004
          pattern: "cipher.update(data, 'utf8', 'hex')  # ECB mode risk"
          severity: high
        - id: vcf-005
          pattern: "https.get(url)  # no TLS check"
          severity: high
        - id: vcf-006
          pattern: "AES.new(key, AES.MODE_CBC, iv=iv)  # IV reuse"
          severity: high
      safe:
        - pattern: "bcrypt.hash(password, bcrypt_cost)"
        - pattern: "argon2id.hash(password)"
        - pattern: "process.env.ENCRYPTION_KEY"
        - pattern: "AES.new(key, AES.MODE_GCM)"
        - pattern: "tls.createSecureContext()"
    remediation:
      - Classify data; encrypt only what must be stored/transmitted
      - Use NIST-approved algorithms (AES-256-GCM, ChaCha20-Poly1305, RSA-2048+)
      - Use strong password hashing: Argon2id, bcrypt (cost>=12), scrypt
      - Store keys in HSM / secrets manager (Vault, AWS KMS, Azure KeyVault)
      - Enforce TLS 1.2+ on all connections; set HSTS header
      - Never commit secrets; use pre-commit hooks (secret scanning)
      - Rotate keys periodically; have key lifecycle process

  A03_INJECTION:
    name: "A03:2021 – Injection"
    description: |
      User-supplied data is not validated, filtered, or sanitized by the application.
      Includes SQL, NoSQL, OS command, LDAP, XPath injection.
    what_to_check:
      - SQL query construction with string concatenation
      - NoSQL injection in MongoDB, Elasticsearch queries
      - OS command injection via exec(), system(), shell()
      - Code injection via eval(), setTimeout(string), Function()
      - LDAP injection in directory lookups
      - XPath injection in XML document queries
      - Template injection (Jinja2, ERB, Handlebars in unsafe contexts)
      - SMTP injection in email headers
      - GraphQL injection in resolver arguments
      - ORM entity filtering bypassed
    code_patterns:
      vulnerable:
        - id: vinj-001
          pattern: "db.query('SELECT * FROM users WHERE id=' + req.params.id)"
          severity: critical
        - id: vinj-002
          pattern: "db.collection.find({$where: req.params.filter})  # NoSQL"
          severity: critical
        - id: vinj-003
          pattern: "child_process.exec('ls ' + directory)  # OS command"
          severity: critical
        - id: vinj-004
          pattern: "eval('var x=' + req.body.expr)  # code injection"
          severity: critical
        - id: vinj-005
          pattern: "Template.render(user_input)  # SSTI risk"
          severity: critical
        - id: vinj-006
          pattern: "curl -s 'https://api.com?q=' + query  # shell metacharacters"
          severity: high
      safe:
        - pattern: "db.query('SELECT * FROM users WHERE id=$1', [id])"
        - pattern: "{username: {$eq: sanitized}}"
        - pattern: "child_process.execFile('ls', [directory])"
        - pattern: "sanitize(userInput).escape()"
    remediation:
      - Use parameterized queries / prepared statements for all DB access
      - Use ORM/PDO with typed bound parameters
      - Escape shell metacharacters; avoid shell execution of user input
      - Never pass user input to eval, Function, exec
      - Implement input validation at API boundary (schema validation)
      - Use auto-escaping template engines; avoid unsafe template concatenation
      - Apply Content Security Policy to reduce injection impact

  A04_INSECURE_DESIGN:
    name: "A04:2021 – Insecure Design"
    description: |
      Missing or ineffective security controls due to insecure design patterns.
      Threat modeling absent; business logic flaws exploited.
    what_to_check:
      - Missing threat modeling during design phase
      - Insecure default configurations shipped
      - Overly permissive feature flags / toggles
      - Missing rate limiting on business logic endpoints
      - Credential recovery using insecure methods (security questions)
      - Missing integration test coverage for security controls
      - Business logic flaws (bypass payment, race conditions)
      - Mass assignment accepted without validation
      - Insufficient anti-automation on critical operations
      - DoS susceptibility in design (expensive operations without throttling)
    code_patterns:
      vulnerable:
        - id: vid-001
          pattern: "if (req.body.isAdmin) user.role = 'admin'  # mass assignment"
          severity: high
        - id: vid-002
          pattern: "for (let i=0; i<1000000; i++) {}  # CPU-bound DoS"
          severity: medium
        - id: vid-003
          pattern: "const total = items.reduce((sum, i) => sum + i.price, 0)  # float precision exploit"
          severity: medium
        - id: vid-004
          pattern: "await db.insert(order)  # missing idempotency key check"
          severity: high
        - id: vid-005
          pattern: "if (password === secretQuestion)  # insecure recovery"
          severity: high
      safe:
        - pattern: "defineSchema({ isAdmin: z.boolean().readonly() })"
        - pattern: "rateLimit({ windowMs: 60000, max: 10 })"
        - pattern: "idempotencyKey in redis"
        - pattern: "sendPasswordResetEmail(user)"
    remediation:
      - Conduct threat modeling (STRIDE, PASTA) during design
      - Implement secure design patterns (defense in depth, zero trust)
      - Use secure development lifecycle (SDL); security champion in each sprint
      - Segregate tenant data at design level; no shared database rows by default
      - Apply rate limiting and throttling to all exposed endpoints
      - Use established auth providers for credential recovery
      - Implement idempotency keys for critical operations

  A05_SECURITY_MISCONFIGURATION:
    name: "A05:2021 – Security Misconfiguration"
    description: |
      Incorrectly configured permissions, unnecessary features enabled, default credentials present.
    what_to_check:
      - Default credentials on admin panels, databases, middleware
      - Unnecessary features / components enabled (i.e., trace, debug mode)
      - Verbose error messages exposing stack traces
      - Missing security headers (X-Frame-Options, CSP, X-XSS-Protection)
      - Overly permissive file permissions on servers
      - Directory listing enabled on web servers
      - Missing principle of least privilege in IAM roles
      - Cloud storage buckets publicly accessible
      - Unpatched servers, containers, dependencies
      - SSL/TLS misconfigured (self-signed certs, weak ciphers)
    code_patterns:
      vulnerable:
        - id: vsmc-001
          pattern: "app.use(express.static(__dirname + '/public'))  # missing cache-control"
          severity: low
        - id: vsmc-002
          pattern: "app.set('env', 'production'); app.set('debug', true)  # debug in prod"
          severity: high
        - id: vsmc-003
          pattern: "Access-Control-Allow-Credentials: true, Access-Control-Allow-Origin: *"
          severity: critical
        - id: vsmc-004
          pattern: "chmod 777 /etc/app/config  # overly permissive"
          severity: high
        - id: vsmc-005
          pattern: "django.settings DEBUG=True  # debug mode in production"
          severity: critical
      safe:
        - pattern: "Content-Security-Policy: default-src 'self'"
        - pattern: "X-Frame-Options: DENY"
        - pattern: "Strict-Transport-Security: max-age=31536000"
        - pattern: "docker run --read-only --no-exec"
        - pattern: "cloud storage bucket not public"
    remediation:
      - Hardened baseline: CIS benchmarks, STIGs
      - Automated configuration verification (Anchore, Terrascan)
      - Disable debug mode in all non-dev environments
      - Minimalist image deployment (distroless, scratch)
      - All secrets in Vault/secrets manager; no defaults
      - Regular penetration testing and configuration audits
      - Automated deployment with immutable infrastructure
      - Error handling returns generic messages; logs detailed errors server-side only

  A06_VULNERABLE_COMPONENTS:
    name: "A06:2021 – Vulnerable and Outdated Components"
    description: |
      Using components with known vulnerabilities or no longer maintained.
    what_to_check:
      - Outdated libraries, frameworks, runtime (Node.js, Python, Java)
      - Known CVEs in direct and transitive dependencies
      - Components with no security patch available
      - Use of abandoned / unmaintained open-source packages
      - Client-side components with XSS vulnerabilities
      - Third-party scripts (analytics, chat widgets) with vulnerabilities
      - Container images with outdated base OS packages
      - Outdated firmware on appliances or IoT
      - Unknown component provenance (supply chain)
      - License compliance issues indicating security risk
    code_patterns:
      vulnerable:
        - id: vvc-001
          pattern: "lodash < 4.17.21  # prototype pollution CVE"
          severity: critical
        - id: vvc-002
          pattern: "node-fetch < 2.6.1  # SSRF via absolute URL"
          severity: high
        - id: vvc-003
          pattern: "FROM node:14  # outdated base image"
          severity: high
        - id: vvc-004
          pattern: "serialize-javascript  # RCE risk"
          severity: critical
      safe:
        - pattern: "npm audit, snyk test, dependabot"
        - pattern: "FROM node:20-alpine"
        - pattern: "renovate.yml with auto-merge critical"
        - pattern: "OWASP Dependency-Check in CI"
    remediation:
      - SBOM generation (Syft, CycloneDX) for all artifacts
      - Dependency scanning in CI: Dependabot, Snyk, Renovate, Grype, Trivy
      - Pin exact versions; use lockfiles (package-lock.json, Pipfile.lock)
      - Remove unused dependencies; minimal dependency surface
      - Subscribe to security advisories (GitHub Advisories, NVD)
      - Use only official / verified container registries
      - Patch critical vulnerabilities within 24-48h; SLA per severity
      - Verify component integrity (SLSA, Sigstore signatures)

  A07_AUTH_FAILURES:
    name: "A07:2021 – Identification and Authentication Failures"
    description: |
      Weaknesses in session management, credential handling, multi-factor authentication.
    what_to_check:
      - Weak password policy (no complexity, no length requirement)
      - Credential stuffing enabled (no rate limiting on login)
      - Session fixation after login (session ID does not regenerate)
      - Session token exposed in URL (session replay)
      - Session timeout absent or too long
      - Missing or weak MFA (SMS-based OTP easily intercepted)
      - Insecure password reset flow (token not invalidated after use)
      - OAuth / OIDC misconfiguration (redirect URI validation missing)
      - JWT algorithm confusion (alg: none, RS256 to HS256)
      - API keys used for user authentication without additional checks
    code_patterns:
      vulnerable:
        - id: vaf-001
          pattern: "session.regenerate()  # not called after login"
          severity: high
        - id: vaf-002
          pattern: "jwt.verify(token, 'secret')  # symmetric for asymmetric algorithm"
          severity: critical
        - id: vaf-003
          pattern: "Cookie: session_id=abc123; HttpOnly missing"
          severity: high
        - id: vaf-004
          pattern: "if (loginAttempts < 5)  # no lockout"
          severity: medium
        - id: vaf-005
          pattern: "const resetToken = Math.random()  # predictable token"
          severity: critical
        - id: vaf-006
          pattern: "jwt.decode(token)  # no signature verification"
          severity: critical
      safe:
        - pattern: "session.regenerate() after login"
        - pattern: "jwt.verify(token, publicKey, { algorithms: ['RS256'] })"
        - pattern: "Set-Cookie: HttpOnly; Secure; SameSite=Strict"
        - pattern: "rateLimit({ max: 5 }) on login"
        - pattern: "crypto.randomBytes(32)"
    remediation:
      - Implement account lockout after failed attempts; CAPTCHA on repeated failures
      - Use secure session ID generation (128-bit entropy, cryptographically random)
      - Regenerate session ID after privilege elevation (login, role change)
      - Set HttpOnly, Secure, SameSite cookies
      - Enforce strong password policy (NIST 800-63B guidelines)
      - Support FIDO2 / WebAuthn for MFA; avoid SMS OTP
      - Use short session timeout; idle timeout < 30 minutes
      - Store password hashes with Argon2id / bcrypt (cost>=12); never store plaintext
      - Validate redirect URIs in OAuth/OIDC strictly against allowlist

  A08_SOFTWARE_INTEGRITY:
    name: "A08:2021 – Software and Data Integrity Failures"
    description: |
      Code and infrastructure that do not protect against integrity violations.
      Includes insecure CI/CD pipelines, auto-update without verification.
    what_to_check:
      - CI/CD pipeline with insecure configurations (no code signing)
      - Direct use of untrusted CDN / library URLs in production
      - Auto-update mechanism without signature verification
      - Serialized data deserialized from untrusted sources
      - Insecure deserialization (pickle, YAML.load, JSON.parse from user)
      - Trusted internal components making outbound calls to internet
      - Compiled dependencies checked into source repo without integrity check
      - Docker container running as root
      - Privileged container capabilities
      - No SBOM or provenance for third-party artifacts
    code_patterns:
      vulnerable:
        - id: vsdi-001
          pattern: "pickle.loads(userData)  # insecure deserialization"
          severity: critical
        - id: vsdi-002
          pattern: "yaml.load(req.body)  # arbitrary code exec"
          severity: critical
        - id: vsdi-003
          pattern: "curl http://cdn.com/lib.js | bash  # remote code execution"
          severity: critical
        - id: vsdi-004
          pattern: "RUN pip install -r requirements.txt  # no hash check"
          severity: high
        - id: vsdi-005
          pattern: "docker run --privileged  # overly permissive"
          severity: high
      safe:
        - pattern: "yaml.safe_load(data)"
        - pattern: "pip install --require-hashes -r requirements.txt"
        - pattern: "docker run --user 1000:1000"
        - pattern: "cosign verify --certificate-identity"
        - pattern: "SLSA Level 3 provenance"
    remediation:
      - Verify artifact signatures: Sigstore cosign, Notary
      - Pin dependency hashes in lockfiles (pip hash, npm audit)
      - Use immutable deployments; no runtime updates from external sources
      - Sanitize all deserialized data; use safe serializers (JSON, YAML safe_load)
      - CI/CD pipeline hardening: least privilege, secret scanning, no manual gates
      - Run containers as non-root; use read-only root filesystem
      - Enforce SLSA framework for supply chain integrity
      - Disable or restrict serialization formats across application layers

  A09_LOGGING_FAILURES:
    name: "A09:2021 – Security Logging and Monitoring Failures"
    description: |
      Insufficient logging, detection, monitoring, and incident response.
    what_to_check:
      - No logging of security events (login, logout, access denial)
      - Sensitive data in logs (passwords, tokens, PII without masking)
      - Logs not protected against tampering (write-only storage)
      - No alerting on suspicious activity patterns
      - Missing audit trail for administrative actions
      - Insufficient logging for forensic investigation (no timestamps, IPs)
      - Logs aggregated in single system without retention policy
      - No correlation between logs from different services
      - Default log level in production (debug, info exposing internals)
      - No alerting on breach attempt patterns (credential stuffing)
    code_patterns:
      vulnerable:
        - id: vll-001
          pattern: "console.log('User logged in:', user.password)  # secret in logs"
          severity: critical
        - id: vll-002
          pattern: "logger.setLevel(logger.DEBUG)  # debug in production"
          severity: medium
        - id: vll-003
          pattern: "# no login failure logging"
          severity: high
        - id: vll-004
          pattern: "process.on('uncaughtException', () => {})  # silent crash"
          severity: high
      safe:
        - pattern: "logger.info('Login attempt', { email: maskPII(user.email) })"
        - pattern: "logger.warn('Auth failure', { ip: req.ip, attempt: count })"
        - pattern: "Write-only log sink with cryptographic hash chain"
        - pattern: "SIEM integration with alerting rules"
    remediation:
      - Log all authentication events: success, failure, lockout, reset
      - Log all access control denials with subject, object, reason
      - Mask or redact PII and secrets from logs (use masking functions)
      - Immutable log storage with cryptographic integrity (hash chain, WORM)
      - Real-time alerting on threshold: failed logins, privilege escalation
      - Centralized log management (ELK, Splunk, Loki); correlate across services
      - Define alert rules for common attack patterns (OWASP Top 10 mapped)
      - Retain logs per compliance requirement (PCI-DSS: 1 year; GDPR: 3 years)

  A10_SSRF:
    name: "A10:2021 – Server-Side Request Forgery"
    description: |
      Fetching remote resources without validating the user-supplied URL.
    what_to_check:
      - User-supplied URL used in HTTP requests (fetch, curl, axios)
      - URL validation only on client side
      - Allowlist bypass via DNS rebinding, URL parsing confusion
      - Access to internal services via file://, dict://, gopher://
      - SSRF in PDF/image generation (fetching remote resources for rendering)
      - Blind SSRF where response not returned but request executed
      - Webhook URLs provided by users
      - URL preview / link expansion features
      - Open redirects combined with SSRF to bypass domain allowlist
    code_patterns:
      vulnerable:
        - id: vssrf-001
          pattern: "fetch(userProvidedUrl)  # no validation"
          severity: critical
        - id: vssrf-002
          pattern: "curl -s ${url}  # shell injection + SSRF"
          severity: critical
        - id: vssrf-003
          pattern: "phantomjs.render(url)  # server-side request"
          severity: high
        - id: vssrf-004
          pattern: "requests.get(url, timeout=5)  # python without validation"
          severity: critical
        - id: vssrf-005
          pattern: "file:///etc/passwd  # scheme injection"
          severity: critical
      safe:
        - pattern: "const allowed = new URL(url); if (!['http:', 'https:'].includes(allowed.protocol)) throw"
        - pattern: "dns.resolve() + block private IP ranges"
        - pattern: "url.startsWith('https://trusted.com')"
        - pattern: "blocklist check for 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16"
    remediation:
      - Validate and sanitize all user-supplied URLs against allowlist
      - Enforce scheme allowlist: only http, https
      - Block access to internal networks and cloud metadata endpoints (169.254.169.254)
      - Use URL parsing libraries; do not rely on string manipulation
      - Disable unused URL schemes (file, dict, gopher, ftp)
      - Implement network segmentation; microservice cannot reach internal APIs directly
      - Timeout and size limit on all outbound requests
      - Log and alert on all SSRF probe attempts
      - Disable automatic following of redirects in HTTP clients

eval_cases:
  - id: eval-001
    category: A01_BROKEN_ACCESS_CONTROL
    description: "Admin endpoint accessed without authorization check"
    code: |
      router.delete('/users/:id', async (req, res) => {
        await db.users.delete({ where: { id: req.params.id } });
        res.json({ success: true });
      });
    expected_finding: "No auth middleware; any user can delete any user"
    severity: critical

  - id: eval-002
    category: A01_BROKEN_ACCESS_CONTROL
    description: "Horizontal privilege escalation via IDOR"
    code: |
      GET /api/orders/12345
      // Response includes orders from all users when iterating IDs
    expected_finding: "IDOR vulnerability; no ownership check on order"
    severity: high

  - id: eval-003
    category: A02_CRYPTO_FAILURES
    description: "Password hashed with MD5"
    code: |
      const hash = crypto.createHash('md5').update(password).digest('hex');
    expected_finding: "MD5 is broken; use bcrypt or Argon2id"
    severity: critical

  - id: eval-004
    category: A02_CRYPTO_FAILURES
    description: "JWT verified with symmetric key but RS256 expected"
    code: |
      jwt.verify(token, process.env.JWT_SECRET);
      // Should use RS256 public key from identity provider
    expected_finding: "Algorithm confusion; force HS256 to RS256"
    severity: critical

  - id: eval-005
    category: A03_INJECTION
    description: "SQL injection via string concatenation"
    code: |
      const query = `SELECT * FROM products WHERE name LIKE '%${searchTerm}%'`;
      db.query(query);
    expected_finding: "SQL injection; use parameterized query"
    severity: critical

  - id: eval-006
    category: A03_INJECTION
    description: "Command injection via shell exec"
    code: |
      const { execSync } = require('child_process');
      execSync(`ping -c 4 ${req.query.host}`);
    expected_finding: "Command injection; sanitize or use execFile"
    severity: critical

  - id: eval-007
    category: A04_INSECURE_DESIGN
    description: "Price manipulation in order total"
    code: |
      const total = parseFloat(req.body.price) * parseInt(req.body.qty);
      // price comes from client without server-side validation
    expected_finding: "Business logic flaw; validate price server-side"
    severity: high

  - id: eval-008
    category: A05_SECURITY_MISCONFIGURATION
    description: "Debug mode enabled in production"
    code: |
      app.use(express.errorHandler({ showStack: true, dumpExceptions: true }));
    expected_finding: "Stack traces exposed to users"
    severity: high

  - id: eval-009
    category: A06_VULNERABLE_COMPONENTS
    description: "Outdated lodash version with known prototype pollution"
    code: |
      // package.json: "lodash": "4.17.19"
      _.merge({}, JSON.parse(req.body.data));
    expected_finding: "Prototype pollution CVE in lodash < 4.17.21"
    severity: critical

  - id: eval-010
    category: A07_AUTH_FAILURES
    description: "Session fixation after login"
    code: |
      app.post('/login', (req, res) => {
        req.session.userId = user.id;
        // Should call req.session.regenerate() before setting
      });
    expected_finding: "Session fixation; regenerate session ID on login"
    severity: high

  - id: eval-011
    category: A08_SOFTWARE_INTEGRITY
    description: "Insecure deserialization of user data"
    code: |
      const obj = pickle.loads(base64.b64decode(req.body.data));
    expected_finding: "Insecure deserialization; use JSON or yaml.safe_load"
    severity: critical

  - id: eval-012
    category: A09_LOGGING_FAILURES
    description: "No logging of authentication failures"
    code: |
      app.post('/login', (req, res) => {
        if (!validUser) return res.status(401).send('Bad credentials');
        // No logging of this failure event
      });
    expected_finding: "Auth failures not logged; no audit trail"
    severity: high

  - id: eval-013
    category: A10_SSRF
    description: "URL preview feature fetches arbitrary URLs"
    code: |
      app.get('/preview', async (req, res) => {
        const data = await fetch(req.query.url);
        res.send(data);
      });
    expected_finding: "SSRF; no URL validation against internal ranges"
    severity: critical

  - id: eval-014
    category: A01_BROKEN_ACCESS_CONTROL
    description: "CORS allows any origin with credentials"
    code: |
      app.use(cors({ origin: '*', credentials: true }));
    expected_finding: "CORS misconfiguration; cannot use origin:* with credentials"
    severity: critical

  - id: eval-015
    category: A03_INJECTION
    description: "NoSQL injection via MongoDB query operator injection"
    code: |
      db.users.find({ $where: `this.username === '${req.body.user}'` });
    expected_finding: "NoSQL injection via $where; use query operators safely"
    severity: critical

  - id: eval-016
    category: A07_AUTH_FAILURES
    description: "Predictable password reset token"
    code: |
      const resetToken = Math.random().toString(36).substring(7);
      // Math.random is not cryptographically random
    expected_finding: "Predictable token; use crypto.randomBytes"
    severity: high

  - id: eval-017
    category: A04_INSECURE_DESIGN
    description: "Missing rate limiting on OTP verification"
    code: |
      app.post('/verify-otp', (req, res) => {
        // No rate limit; unlimited OTP attempts
        verifyOTP(req.body.code);
      });
    expected_finding: "No rate limiting on OTP; susceptible to brute force"
    severity: high

  - id: eval-018
    category: A08_SOFTWARE_INTEGRITY
    description: "Docker container running as root"
    code: |
      docker run -u 0 myapp:latest
      # or no USER directive in Dockerfile
    expected_finding: "Container running as root; use least-privilege user"
    severity: high

  - id: eval-019
    category: A05_SECURITY_MISCONFIGURATION
    description: "Missing security headers on API responses"
    code: |
      app.get('/api/data', (req, res) => {
        // No X-Frame-Options, CSP, HSTS, etc.
        res.json({ data: 'secret' });
      });
    expected_finding: "Security headers missing; add all OWASP-recommended headers"
    severity: medium

  - id: eval-020
    category: A09_LOGGING_FAILURES
    description: "Sensitive PII logged without masking"
    code: |
      logger.info('Payment processed', { card: req.body.cardNumber });
      // Full credit card number in logs
    expected_finding: "PCI-DSS violation; mask card number in logs"
    severity: critical
