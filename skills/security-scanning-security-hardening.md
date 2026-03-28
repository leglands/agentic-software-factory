---
name: security-scanning-security-hardening
version: 1.0.0
description: Coordinate multi-layer security scanning and hardening across application,
  infrastructure, and compliance controls.
metadata:
  category: development
  source: 'antigravity-awesome-skills (MIT) — source: community'
  triggers:
  - when working on security scanning security hardening
eval_cases:
- id: security-scanning-security-hardening-approach
  prompt: How should I approach security scanning security hardening for a production
    system?
  should_trigger: true
  checks:
  - length_min:150
  - no_placeholder
  expectations:
  - Provides concrete guidance on security scanning security hardening
  tags:
  - security
- id: security-scanning-security-hardening-best-practices
  prompt: What are the key best practices and pitfalls for security scanning security
    hardening?
  should_trigger: true
  checks:
  - length_min:100
  - no_placeholder
  expectations:
  - Lists concrete best practices for security scanning security hardening
  tags:
  - security
  - best-practices
- id: security-scanning-security-hardening-antipatterns
  prompt: What are the most common mistakes to avoid with security scanning security
    hardening?
  should_trigger: true
  checks:
  - length_min:80
  - no_placeholder
  expectations:
  - Identifies anti-patterns or mistakes to avoid
  tags:
  - security
  - antipatterns
- id: security-scanning-sast-dast-approach
  prompt: Explain how to combine SAST and DAST scanning in a DevSecOps pipeline for
    comprehensive vulnerability detection.
  checks:
  - regex: (SAST|DAST|semgrep|zap|OWASP)
    length_min: 120
    has_keyword:
    - scan
    - security
    - pipeline
  expectations:
  - Describes both static and dynamic analysis approaches
  - Mentions specific tools or methodologies
  - Addresses integration points in CI/CD
- id: security-scanning-secrets-detection
  prompt: How do you detect hardcoded secrets, API keys, and credentials in a codebase
    using automated tools?
  checks:
  - regex: (gitLeaks|truffleHog|secret|credential|key)
    length_min: 80
    has_keyword:
    - detect
    - secret
    - scan
  expectations:
  - Names specific secrets detection tools
  - Explains the detection approach
  - Addresses remediation of found secrets
- id: security-scanning-sbom-generation
  prompt: What is an SBOM and why is it critical for supply chain security in modern
    applications?
  checks:
  - regex: (SBOM|supply.chain|dependency|inventory)
    length_min: 100
    has_keyword:
    - SBOM
    - supply
    - vulnerability
  expectations:
  - Defines SBOM clearly
  - Explains supply chain security importance
  - Mentions tools for SBOM generation
- id: security-scanning-threat-modeling-stride
  prompt: Apply the STRIDE threat modeling methodology to a microservice architecture
    with API gateway.
  checks:
  - regex: (STRIDE|threat.model|microservice|attack.vector)
    length_min: 150
    has_keyword:
    - STRIDE
    - threat
    - mitigation
  expectations:
  - Explains STRIDE methodology components
  - Applies it to the given architecture
  - Identifies specific threats and mitigations
- id: security-scanning-mitre-attack-mapping
  prompt: How do you map discovered vulnerabilities to the MITRE ATT&CK framework
    for better threat prioritization?
  checks:
  - regex: (MITRE|ATT.*CK|framework|tactic|technique)
    length_min: 100
    has_keyword:
    - MITRE
    - ATT&CK
    - mapping
  expectations:
  - Explains MITRE ATT&CK structure
  - Describes mapping process from vulnerabilities
  - Addresses prioritization using the framework
- id: security-scanning-cvss-scoring
  prompt: How do you prioritize vulnerability remediation using CVSS scores in a resource-constrained
    environment?
  checks:
  - regex: (CVSS|score|priority|severity|remediation)
    length_min: 100
    has_keyword:
    - CVSS
    - priority
    - vulnerability
  expectations:
  - Explains CVSS scoring system
  - Provides prioritization strategy
  - Addresses resource allocation decisions
- id: security-scanning-owasp-top10-remediation
  prompt: What are the most effective countermeasures against SQL injection and XSS
    vulnerabilities in web applications?
  checks:
  - regex: (SQL.injection|XSS|parameterized|encoding|OWASP)
    length_min: 120
    has_keyword:
    - SQL injection
    - XSS
    - remediation
  expectations:
  - Identifies root causes of both vulnerabilities
  - Provides specific remediation techniques
  - References OWASP guidance
- id: security-scanning-csp-implementation
  prompt: How do you implement a Content Security Policy that effectively prevents
    XSS attacks without breaking application functionality?
  checks:
  - regex: (CSP|Content.Security.Policy|XSS|directive|nonce)
    length_min: 100
    has_keyword:
    - CSP
    - XSS
    - policy
  expectations:
  - Explains CSP directives
  - Addresses XSS prevention mechanism
  - Mentions deployment considerations
- id: security-scanning-auth-mfa-implementation
  prompt: Implement multi-factor authentication using TOTP and WebAuthn/FIDO2 for
    a web application.
  checks:
  - regex: (MFA|TOTP|WebAuthn|FIDO2|authenticator)
    length_min: 120
    has_keyword:
    - MFA
    - TOTP
    - authentication
  expectations:
  - Describes TOTP implementation approach
  - Explains WebAuthn/FIDO2 advantages
  - Addresses user enrollment flow
- id: security-scanning-rate-limiting-ddos
  prompt: Design a rate limiting strategy to protect API endpoints from DDoS attacks
    while allowing legitimate traffic.
  checks:
  - regex: (rate.limit|DDoS|throttle|WAF|burst)
    length_min: 100
    has_keyword:
    - rate limiting
    - DDoS
    - API
  expectations:
  - Describes rate limiting algorithms
  - Addresses DDoS protection layers
  - Considers legitimate traffic patterns
- id: security-scanning-penetration-testing
  prompt: What is the methodology for conducting a penetration test that validates
    the effectiveness of implemented security controls?
  checks:
  - regex: (pentest|Burp.Suite|Metasploit|exploit|validation)
    length_min: 120
    has_keyword:
    - pentest
    - exploit
    - validation
  expectations:
  - Outlines penetration testing phases
  - Names common tools used
  - Addresses validation of security controls
- id: security-scanning-compliance-owasp-asvs
  prompt: How do you verify that an application meets OWASP ASVS Level 2 requirements
    and generate compliance documentation?
  checks:
  - regex: (ASVS|OWASP|compliance|verification|audit)
    length_min: 100
    has_keyword:
    - ASVS
    - compliance
    - verification
  expectations:
  - Explains OWASP ASVS levels
  - Describes verification methodology
  - Addresses documentation requirements
---
# security-scanning-security-hardening

Implement comprehensive security hardening with defense-in-depth strategy through coordinated multi-agent orchestration:

[Extended thinking: This workflow implements a defense-in-depth security strategy across all application layers. It coordinates specialized security agents to perform comprehensive assessments, implement layered security controls, and establish continuous security monitoring. The approach follows modern DevSecOps principles with shift-left security, automated scanning, and compliance validation. Each phase builds upon previous findings to create a resilient security posture that addresses both current vulnerabilities and future threats.]

## Use this skill when

- Running a coordinated security hardening program
- Establishing defense-in-depth controls across app, infra, and CI/CD
- Prioritizing remediation from scans and threat modeling

## Do not use this skill when

- You only need a quick scan without remediation work
- You lack authorization for security testing or changes
- The environment cannot tolerate invasive security controls

## Instructions

1. Execute Phase 1 to establish a security baseline.
2. Apply Phase 2 remediations for high-risk issues.
3. Implement Phase 3 controls and validate defenses.
4. Complete Phase 4 validation and compliance checks.

## Safety

- Avoid intrusive testing in production without approval.
- Ensure rollback plans exist before hardening changes.

## Phase 1: Comprehensive Security Assessment

### 1. Initial Vulnerability Scanning
- Use Task tool with subagent_type="security-auditor"
- Prompt: "Perform comprehensive security assessment on: $ARGUMENTS. Execute SAST analysis with Semgrep/SonarQube, DAST scanning with OWASP ZAP, dependency audit with Snyk/Trivy, secrets detection with GitLeaks/TruffleHog. Generate SBOM for supply chain analysis. Identify OWASP Top 10 vulnerabilities, CWE weaknesses, and CVE exposures."
- Output: Detailed vulnerability report with CVSS scores, exploitability analysis, attack surface mapping, secrets exposure report, SBOM inventory
- Context: Initial baseline for all remediation efforts

### 2. Threat Modeling and Risk Analysis
- Use Task tool with subagent_type="security-auditor"
- Prompt: "Conduct threat modeling using STRIDE methodology for: $ARGUMENTS. Analyze attack vectors, create attack trees, assess business impact of identified vulnerabilities. Map threats to MITRE ATT&CK framework. Prioritize risks based on likelihood and impact."
- Output: Threat model diagrams, risk matrix with prioritized vulnerabilities, attack scenario documentation, business impact analysis
- Context: Uses vulnerability scan results to inform threat priorities

### 3. Architecture Security Review
- Use Task tool with subagent_type="backend-api-security::backend-architect"
- Prompt: "Review architecture for security weaknesses in: $ARGUMENTS. Evaluate service boundaries, data flow security, authentication/authorization architecture, encryption implementation, network segmentation. Design zero-trust architecture patterns. Reference threat model and vulnerability findings."
- Output: Security architecture assessment, zero-trust design recommendations, service mesh security requirements, data classification matrix
- Context: Incorporates threat model to address architectural vulnerabilities

## Phase 2: Vulnerability Remediation

### 4. Critical Vulnerability Fixes
- Use Task tool with subagent_type="security-auditor"
- Prompt: "Coordinate immediate remediation of critical vulnerabilities (CVSS 7+) in: $ARGUMENTS. Fix SQL injections with parameterized queries, XSS with output encoding, authentication bypasses with secure session management, insecure deserialization with input validation. Apply security patches for CVEs."
- Output: Patched code with vulnerability fixes, security patch documentation, regression test requirements
- Context: Addresses high-priority items from vulnerability assessment

### 5. Backend Security Hardening
- Use Task tool with subagent_type="backend-api-security::backend-security-coder"
- Prompt: "Implement comprehensive backend security controls for: $ARGUMENTS. Add input validation with OWASP ESAPI, implement rate limiting and DDoS protection, secure API endpoints with OAuth2/JWT validation, add encryption for data at rest/transit using AES-256/TLS 1.3. Implement secure logging without PII exposure."
- Output: Hardened API endpoints, validation middleware, encryption implementation, secure configuration templates
- Context: Builds upon vulnerability fixes with preventive controls

### 6. Frontend Security Implementation
- Use Task tool with subagent_type="frontend-mobile-security::frontend-security-coder"
- Prompt: "Implement frontend security measures for: $ARGUMENTS. Configure CSP headers with nonce-based policies, implement XSS prevention with DOMPurify, secure authentication flows with PKCE OAuth2, add SRI for external resources, implement secure cookie handling with SameSite/HttpOnly/Secure flags."
- Output: Secure frontend components, CSP policy configuration, authentication flow implementation, security headers configuration
- Context: Complements backend security with client-side protections

### 7. Mobile Security Hardening
- Use Task tool with subagent_type="frontend-mobile-security::mobile-security-coder"
- Prompt: "Implement mobile app security for: $ARGUMENTS. Add certificate pinning, implement biometric authentication, secure local storage with encryption, obfuscate code with ProGuard/R8, implement anti-tampering and root/jailbreak detection, secure IPC communications."
- Output: Hardened mobile application, security configuration files, obfuscation rules, certificate pinning implementation
- Context: Extends security to mobile platforms if applicable

## Phase 3: Security Controls Implementation

### 8. Authentication and Authorization Enhancement
- Use Task tool with subagent_type="security-auditor"
- Prompt: "Implement modern authentication system for: $ARGUMENTS. Deploy OAuth2/OIDC with PKCE, implement MFA with TOTP/WebAuthn/FIDO2, add risk-based authentication, implement RBAC/ABAC with principle of least privilege, add session management with secure token rotation."
- Output: Authentication service configuration, MFA implementation, authorization policies, session management system
- Context: Strengthens access controls based on architecture review

### 9. Infrastructure Security Controls
- Use Task tool with subagent_type="deployment-strategies::deployment-engineer"
- Prompt: "Deploy infrastructure security controls for: $ARGUMENTS. Configure WAF rules for OWASP protection, implement network segmentation with micro-segmentation, deploy IDS/IPS systems, configure cloud security groups and NACLs, implement DDoS protection with rate limiting and geo-blocking."
- Output: WAF configuration, network security policies, IDS/IPS rules, cloud security configurations
- Context: Implements network-level defenses

### 10. Secrets Management Implementation
- Use Task tool with subagent_type="deployment-strategies::deployment-engineer"
- Prompt: "Implement enterprise secrets management for: $ARGUMENTS. Deploy HashiCorp Vault or AWS Secrets Manager, implement secret rotation policies, remove hardcoded secrets, configure least-privilege IAM roles, implement encryption key management with HSM support."
- Output: Secrets management configuration, rotation policies, IAM role definitions, key management procedures
- Context: Eliminates secrets exposure vulnerabilities

## Phase 4: Validation and Compliance

### 11. Penetration Testing and Validation
- Use Task tool with subagent_type="security-auditor"
- Prompt: "Execute comprehensive penetration testing for: $ARGUMENTS. Perform authenticated and unauthenticated testing, API security testing, business logic testing, privilege escalation attempts. Use Burp Suite, Metasploit, and custom exploits. Validate all security controls effectiveness."
- Output: Penetration test report, proof-of-concept exploits, remediation validation, security control effectiveness metrics
- Context: Validates all implemented security measures

### 12. Compliance and Standards Verification
- Use Task tool with subagent_type="security-auditor"
- Prompt: "Verify compliance with security frameworks for: $ARGUMENTS. Validate against OWASP ASVS Level 2, CIS Benchmarks, SOC2 Type II requirements, GDPR/CCPA privacy controls, HIPAA/PCI-DSS if applicable. Generate compliance attestation reports."
- Output: Compliance assessment report, gap analysis, remediation requirements, audit evidence collection
- Context: Ensures regulatory and industry standard compliance

### 13. Security Monitoring and SIEM Integration
- Use Task tool with subagent_type="incident-response::devops-troubleshooter"
- Prompt: "Implement security monitoring and SIEM for: $ARGUMENTS. Deploy Splunk/ELK/Sentinel integration, configure security event correlation, implement behavioral analytics for anomaly detection, set up automated incident response playbooks, create security dashboards and alerting."
- Output: SIEM configuration, correlation rules, incident response playbooks, security dashboards, alert definitions
- Context: Establishes continuous security monitoring

## Configuration Options
- scanning_depth: "quick" | "standard" | "comprehensive" (default: comprehensive)
- compliance_frameworks: ["OWASP", "CIS", "SOC2", "GDPR", "HIPAA", "PCI-DSS"]
- remediation_priority: "cvss_score" | "exploitability" | "business_impact"
- monitoring_integration: "splunk" | "elastic" | "sentinel" | "custom"
- authentication_methods: ["oauth2", "saml", "mfa", "biometric", "passwordless"]

## Success Criteria
- All critical vulnerabilities (CVSS 7+) remediated
- OWASP Top 10 vulnerabilities addressed
- Zero high-risk findings in penetration testing
- Compliance frameworks validation passed
- Security monitoring detecting and alerting on threats
- Incident response time < 15 minutes for critical alerts
- SBOM generated and vulnerabilities tracked
- All secrets managed through secure vault
- Authentication implements MFA and secure session management
- Security tests integrated into CI/CD pipeline

## Coordination Notes
- Each phase provides detailed findings that inform subsequent phases
- Security-auditor agent coordinates with domain-specific agents for fixes
- All code changes undergo security review before implementation
- Continuous feedback loop between assessment and remediation
- Security findings tracked in centralized vulnerability management system
- Regular security reviews scheduled post-implementation

Security hardening target: $ARGUMENTS
