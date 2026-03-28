---
name: skill-developer
version: 1.0.0
description: Create and manage Claude Code skills following Anthropic best practices.
  Use when creating new skills, modifying skill-rules.json, understanding trigger
  patterns, working with hooks, debugging skil...
metadata:
  category: development
  source: 'antigravity-awesome-skills (MIT) — source: community'
  triggers:
  - creating new skills, modifying skill-rules
  - creating or adding skills
eval_cases:
- id: skill-developer-approach
  prompt: How should I approach skill developer for a production system?
  should_trigger: true
  checks:
  - length_min:150
  - no_placeholder
  expectations:
  - Provides concrete guidance on skill developer
  tags:
  - skill
- id: skill-developer-best-practices
  prompt: What are the key best practices and pitfalls for skill developer?
  should_trigger: true
  checks:
  - length_min:100
  - no_placeholder
  expectations:
  - Lists concrete best practices for skill developer
  tags:
  - skill
  - best-practices
- id: skill-developer-antipatterns
  prompt: What are the most common mistakes to avoid with skill developer?
  should_trigger: true
  checks:
  - length_min:80
  - no_placeholder
  expectations:
  - Identifies anti-patterns or mistakes to avoid
  tags:
  - skill
  - antipatterns
- id: skill-developer-create-guardrail
  prompt: Create a guardrail skill that blocks direct SQL queries to prevent injection
    attacks
  checks:
  - has_keyword: guardrail
  - has_keyword: block
  - length_min: 120
  expectations:
  - Explains guardrail type and enforcement
  - Mentions block with exit code 2
  - Covers trigger patterns for SQL keywords
- id: skill-developer-skip-conditions
  prompt: How do session tracking and file markers work to avoid repeated nag prompts?
  checks:
  - has_keyword: session
  - has_keyword: skip-validation
  - length_min: 100
  expectations:
  - Describes session state file location
  - Explains file marker syntax
  - Clarifies difference between temporary and permanent skip
- id: skill-developer-500-line-rule
  prompt: What is the 500-line rule and why should I follow it when creating skills?
  checks:
  - has_keyword: 500-line
  - has_keyword: progressive disclosure
  - length_min: 80
  expectations:
  - Explains 500-line limit purpose
  - Mentions progressive disclosure pattern
  - Suggests using reference files
- id: skill-developer-hook-flow
  prompt: Walk me through the UserPromptSubmit hook flow and how it injects suggestions
  checks:
  - has_keyword: UserPromptSubmit
  - has_keyword: stdout
  - length_min: 100
  expectations:
  - Describes hook trigger timing
  - Explains context injection method
  - Mentions intent pattern matching
- id: skill-developer-enforcement-levels
  prompt: What are the differences between BLOCK, SUGGEST, and WARN enforcement levels?
  checks:
  - regex: BLOCK.*exit code
  - length_min: 120
  expectations:
  - Explains BLOCK uses exit code 2
  - Clarifies SUGGEST is advisory
  - Notes WARN is rarely used
- id: skill-developer-skill-rules-schema
  prompt: Show me the structure of skill-rules.json and required fields for a domain
    skill
  checks:
  - has_keyword: skill-rules.json
  - has_keyword: enforcement
  - length_min: 100
  expectations:
  - Shows JSON structure with type, enforcement, priority
  - Mentions promptTriggers object
  - Includes keywords and intentPatterns
- id: skill-developer-troubleshooting-not-triggering
  prompt: My skill is not activating even though I added keywords. How do I debug
    this?
  checks:
  - has_keyword: troubleshooting
  - has_keyword: keywords
  - length_min: 100
  expectations:
  - Suggests testing with tsx command
  - Recommends checking skill-rules.json syntax
  - Mentions refining intent patterns
- id: skill-developer-skip-env-vars
  prompt: How can I temporarily disable skill guardrails using environment variables?
  checks:
  - has_keyword: SKIP_SKILL_GUARDRAILS
  - has_keyword: environment
  - length_min: 60
  expectations:
  - Shows global disable env var
  - Mentions skill-specific env var pattern
  - Notes emergency use case
- id: skill-developer-reference-files
  prompt: When should I create reference files instead of putting everything in SKILL.md?
  checks:
  - has_keyword: reference
  - has_keyword: progressive disclosure
  - length_min: 80
  expectations:
  - Explains when to use reference files
  - Mentions table of contents for files >100 lines
  - Recommends keeping SKILL.md under 500 lines
- id: skill-developer-guardrail-vs-domain
  prompt: Should I create a guardrail or domain skill for enforcing TypeScript strict
    mode?
  checks:
  - has_keyword: guardrail
  - has_keyword: domain
  - length_min: 100
  expectations:
  - Recommends guardrail for blocking critical practices
  - Notes domain for advisory guidance
  - Explains priority levels
- id: skill-developer-testing-checklist
  prompt: What is the complete testing checklist before deploying a new skill?
  checks:
  - has_keyword: testing
  - has_keyword: skill-rules.json
  - length_min: 150
  expectations:
  - Lists multiple verification steps
  - Mentions JSON validation with jq
  - Covers false positive and negative testing
- id: skill-developer-content-patterns
  prompt: How do I use content patterns to auto-activate a skill when specific code
    is detected?
  checks:
  - has_keyword: content
  - has_keyword: regex
  - length_min: 80
  expectations:
  - Explains content pattern matching
  - Mentions regex-based detection
  - Describes use case for technology-specific skills
- id: skill-developer-naming-conventions
  prompt: What naming conventions should I follow when creating new skills?
  checks:
  - has_keyword: gerund
  - regex: lowercase.*
  - length_min: 80
  expectations:
  - Mentions lowercase with hyphens
  - Recommends verb+-ing form
  - Notes max 1024 chars for description
- id: skill-developer-frontmatter-schema
  prompt: Show me the required frontmatter fields for a skill file
  checks:
  - has_keyword: frontmatter
  - has_keyword: name
  - length_min: 100
  expectations:
  - Lists required fields (name, description)
  - Explains description should include trigger keywords
  - Mentions max 1024 char limit
- id: skill-developer-prompt-triggers-deep
  prompt: How do I create effective intent patterns for skill activation?
  checks:
  - has_keyword: intentPatterns
  - regex: regex.*
  - length_min: 100
  expectations:
  - Explains regex-based intent matching
  - Shows example patterns
  - Warns about false positives
- id: skill-developer-file-path-patterns
  prompt: How can I activate a skill only when editing specific file types?
  checks:
  - has_keyword: file.*path
  - has_keyword: glob
  - length_min: 80
  expectations:
  - Describes glob pattern matching
  - Explains file location-based triggers
  - Mentions common use cases
- id: skill-developer-session-state-internals
  prompt: How does session state prevent repeated skill prompts in the same session?
  checks:
  - has_keyword: session
  - regex: state.*
  - length_min: 100
  expectations:
  - Explains state file location and format
  - Describes how first edit differs from second
  - Clarifies session_id scoping
- id: skill-developer-exit-codes
  prompt: What exit codes do hooks use and what do they mean?
  checks:
  - regex: exit.*code.*2
  - has_keyword: stderr
  - length_min: 80
  expectations:
  - Explains exit code 2 means BLOCK
  - Notes stderr carries error message to Claude
  - Clarifies non-zero for other failures
- id: skill-developer-progressive-disclosure
  prompt: When should I use reference files instead of putting everything in SKILL.md?
  checks:
  - has_keyword: progressive disclosure
  - has_keyword: reference
  - length_min: 100
  expectations:
  - Explains 500-line rule rationale
  - Recommends TOC for files over 100 lines
  - Mentions not nesting references deeply
- id: skill-developer-guardrail-vs-suggest
  prompt: Should I use BLOCK or SUGGEST enforcement for a security-related skill?
  checks:
  - has_keyword: BLOCK
  - has_keyword: SUGGEST
  - length_min: 100
  expectations:
  - Recommends BLOCK for security/critical issues
  - Notes SUGGEST is advisory only
  - Explains exit code 2 requirement for BLOCK
- id: skill-developer-content-pattern-matching
  prompt: How do I make a skill auto-activate when TypeScript code is detected?
  checks:
  - has_keyword: content
  - regex: regex|pattern
  - length_min: 80
  expectations:
  - Explains regex-based content detection
  - Describes technology-specific use cases
  - Mentions file content scanning
- id: skill-developer-json-validation
  prompt: How do I validate my skill-rules.json has no syntax errors?
  checks:
  - has_keyword: jq
  - regex: json.*
  - length_min: 60
  expectations:
  - Shows jq validation command
  - Mentions checking syntax before testing
  - Notes common JSON errors
- id: skill-developer-stop-hook-philosophy
  prompt: Why did the team switch from PreToolUse blocking to post-response reminders
    for error handling?
  checks:
  - has_keyword: Stop.*hook
  - regex: gentle.*reminder
  - length_min: 100
  expectations:
  - Explains philosophy change rationale
  - Mentions avoiding workflow blocking
  - Notes maintaining code quality awareness
- id: skill-developer-skip-validation-markup
  prompt: How do I permanently skip validation for a specific file using a marker?
  checks:
  - has_keyword: skip-validation
  - regex: marker|@
  - length_min: 80
  expectations:
  - Shows // @skip-validation syntax
  - Warns about overuse defeating purpose
  - Explains permanent vs session skip
---
# skill-developer

# Skill Developer Guide

## Purpose

Comprehensive guide for creating and managing skills in Claude Code with auto-activation system, following Anthropic's official best practices including the 500-line rule and progressive disclosure pattern.

## When to Use This Skill

Automatically activates when you mention:
- Creating or adding skills
- Modifying skill triggers or rules
- Understanding how skill activation works
- Debugging skill activation issues
- Working with skill-rules.json
- Hook system mechanics
- Claude Code best practices
- Progressive disclosure
- YAML frontmatter
- 500-line rule

---

## System Overview

### Two-Hook Architecture

**1. UserPromptSubmit Hook** (Proactive Suggestions)
- **File**: `.claude/hooks/skill-activation-prompt.ts`
- **Trigger**: BEFORE Claude sees user's prompt
- **Purpose**: Suggest relevant skills based on keywords + intent patterns
- **Method**: Injects formatted reminder as context (stdout → Claude's input)
- **Use Cases**: Topic-based skills, implicit work detection

**2. Stop Hook - Error Handling Reminder** (Gentle Reminders)
- **File**: `.claude/hooks/error-handling-reminder.ts`
- **Trigger**: AFTER Claude finishes responding
- **Purpose**: Gentle reminder to self-assess error handling in code written
- **Method**: Analyzes edited files for risky patterns, displays reminder if needed
- **Use Cases**: Error handling awareness without blocking friction

**Philosophy Change (2025-10-27):** We moved away from blocking PreToolUse for Sentry/error handling. Instead, use gentle post-response reminders that don't block workflow but maintain code quality awareness.

### Configuration File

**Location**: `.claude/skills/skill-rules.json`

Defines:
- All skills and their trigger conditions
- Enforcement levels (block, suggest, warn)
- File path patterns (glob)
- Content detection patterns (regex)
- Skip conditions (session tracking, file markers, env vars)

---

## Skill Types

### 1. Guardrail Skills

**Purpose:** Enforce critical best practices that prevent errors

**Characteristics:**
- Type: `"guardrail"`
- Enforcement: `"block"`
- Priority: `"critical"` or `"high"`
- Block file edits until skill used
- Prevent common mistakes (column names, critical errors)
- Session-aware (don't repeat nag in same session)

**Examples:**
- `database-verification` - Verify table/column names before Prisma queries
- `frontend-dev-guidelines` - Enforce React/TypeScript patterns

**When to Use:**
- Mistakes that cause runtime errors
- Data integrity concerns
- Critical compatibility issues

### 2. Domain Skills

**Purpose:** Provide comprehensive guidance for specific areas

**Characteristics:**
- Type: `"domain"`
- Enforcement: `"suggest"`
- Priority: `"high"` or `"medium"`
- Advisory, not mandatory
- Topic or domain-specific
- Comprehensive documentation

**Examples:**
- `backend-dev-guidelines` - Node.js/Express/TypeScript patterns
- `frontend-dev-guidelines` - React/TypeScript best practices
- `error-tracking` - Sentry integration guidance

**When to Use:**
- Complex systems requiring deep knowledge
- Best practices documentation
- Architectural patterns
- How-to guides

---

## Quick Start: Creating a New Skill

### Step 1: Create Skill File

**Location:** `.claude/skills/{skill-name}/SKILL.md`

**Template:**
```markdown
---
name: my-new-skill
description: Brief description including keywords that trigger this skill. Mention topics, file types, and use cases. Be explicit about trigger terms.
---

# My New Skill

## Purpose
What this skill helps with

## When to Use
Specific scenarios and conditions

## Key Information
The actual guidance, documentation, patterns, examples
```

**Best Practices:**
- ✅ **Name**: Lowercase, hyphens, gerund form (verb + -ing) preferred
- ✅ **Description**: Include ALL trigger keywords/phrases (max 1024 chars)
- ✅ **Content**: Under 500 lines - use reference files for details
- ✅ **Examples**: Real code examples
- ✅ **Structure**: Clear headings, lists, code blocks

### Step 2: Add to skill-rules.json

See [SKILL_RULES_REFERENCE.md](SKILL_RULES_REFERENCE.md) for complete schema.

**Basic Template:**
```json
{
  "my-new-skill": {
    "type": "domain",
    "enforcement": "suggest",
    "priority": "medium",
    "promptTriggers": {
      "keywords": ["keyword1", "keyword2"],
      "intentPatterns": ["(create|add).*?something"]
    }
  }
}
```

### Step 3: Test Triggers

**Test UserPromptSubmit:**
```bash
echo '{"session_id":"test","prompt":"your test prompt"}' | \
  npx tsx .claude/hooks/skill-activation-prompt.ts
```

**Test PreToolUse:**
```bash
cat <<'EOF' | npx tsx .claude/hooks/skill-verification-guard.ts
{"session_id":"test","tool_name":"Edit","tool_input":{"file_path":"test.ts"}}
EOF
```

### Step 4: Refine Patterns

Based on testing:
- Add missing keywords
- Refine intent patterns to reduce false positives
- Adjust file path patterns
- Test content patterns against actual files

### Step 5: Follow Anthropic Best Practices

✅ Keep SKILL.md under 500 lines
✅ Use progressive disclosure with reference files
✅ Add table of contents to reference files > 100 lines
✅ Write detailed description with trigger keywords
✅ Test with 3+ real scenarios before documenting
✅ Iterate based on actual usage

---

## Enforcement Levels

### BLOCK (Critical Guardrails)

- Physically prevents Edit/Write tool execution
- Exit code 2 from hook, stderr → Claude
- Claude sees message and must use skill to proceed
- **Use For**: Critical mistakes, data integrity, security issues

**Example:** Database column name verification

### SUGGEST (Recommended)

- Reminder injected before Claude sees prompt
- Claude is aware of relevant skills
- Not enforced, just advisory
- **Use For**: Domain guidance, best practices, how-to guides

**Example:** Frontend development guidelines

### WARN (Optional)

- Low priority suggestions
- Advisory only, minimal enforcement
- **Use For**: Nice-to-have suggestions, informational reminders

**Rarely used** - most skills are either BLOCK or SUGGEST.

---

## Skip Conditions & User Control

### 1. Session Tracking

**Purpose:** Don't nag repeatedly in same session

**How it works:**
- First edit → Hook blocks, updates session state
- Second edit (same session) → Hook allows
- Different session → Blocks again

**State File:** `.claude/hooks/state/skills-used-{session_id}.json`

### 2. File Markers

**Purpose:** Permanent skip for verified files

**Marker:** `// @skip-validation`

**Usage:**
```typescript
// @skip-validation
import { PrismaService } from './prisma';
// This file has been manually verified
```

**NOTE:** Use sparingly - defeats the purpose if overused

### 3. Environment Variables

**Purpose:** Emergency disable, temporary override

**Global disable:**
```bash
export SKIP_SKILL_GUARDRAILS=true  # Disables ALL PreToolUse blocks
```

**Skill-specific:**
```bash
export SKIP_DB_VERIFICATION=true
export SKIP_ERROR_REMINDER=true
```

---

## Testing Checklist

When creating a new skill, verify:

- [ ] Skill file created in `.claude/skills/{name}/SKILL.md`
- [ ] Proper frontmatter with name and description
- [ ] Entry added to `skill-rules.json`
- [ ] Keywords tested with real prompts
- [ ] Intent patterns tested with variations
- [ ] File path patterns tested with actual files
- [ ] Content patterns tested against file contents
- [ ] Block message is clear and actionable (if guardrail)
- [ ] Skip conditions configured appropriately
- [ ] Priority level matches importance
- [ ] No false positives in testing
- [ ] No false negatives in testing
- [ ] Performance is acceptable (<100ms or <200ms)
- [ ] JSON syntax validated: `jq . skill-rules.json`
- [ ] **SKILL.md under 500 lines** ⭐
- [ ] Reference files created if needed
- [ ] Table of contents added to files > 100 lines

---

## Reference Files

For detailed information on specific topics, see:

### [TRIGGER_TYPES.md](TRIGGER_TYPES.md)
Complete guide to all trigger types:
- Keyword triggers (explicit topic matching)
- Intent patterns (implicit action detection)
- File path triggers (glob patterns)
- Content patterns (regex in files)
- Best practices and examples for each
- Common pitfalls and testing strategies

### [SKILL_RULES_REFERENCE.md](SKILL_RULES_REFERENCE.md)
Complete skill-rules.json schema:
- Full TypeScript interface definitions
- Field-by-field explanations
- Complete guardrail skill example
- Complete domain skill example
- Validation guide and common errors

### [HOOK_MECHANISMS.md](HOOK_MECHANISMS.md)
Deep dive into hook internals:
- UserPromptSubmit flow (detailed)
- PreToolUse flow (detailed)
- Exit code behavior table (CRITICAL)
- Session state management
- Performance considerations

### [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
Comprehensive debugging guide:
- Skill not triggering (UserPromptSubmit)
- PreToolUse not blocking
- False positives (too many triggers)
- Hook not executing at all
- Performance issues

### [PATTERNS_LIBRARY.md](PATTERNS_LIBRARY.md)
Ready-to-use pattern collection:
- Intent pattern library (regex)
- File path pattern library (glob)
- Content pattern library (regex)
- Organized by use case
- Copy-paste ready

### [ADVANCED.md](ADVANCED.md)
Future enhancements and ideas:
- Dynamic rule updates
- Skill dependencies
- Conditional enforcement
- Skill analytics
- Skill versioning

---

## Quick Reference Summary

### Create New Skill (5 Steps)

1. Create `.claude/skills/{name}/SKILL.md` with frontmatter
2. Add entry to `.claude/skills/skill-rules.json`
3. Test with `npx tsx` commands
4. Refine patterns based on testing
5. Keep SKILL.md under 500 lines

### Trigger Types

- **Keywords**: Explicit topic mentions
- **Intent**: Implicit action detection
- **File Paths**: Location-based activation
- **Content**: Technology-specific detection

See [TRIGGER_TYPES.md](TRIGGER_TYPES.md) for complete details.

### Enforcement

- **BLOCK**: Exit code 2, critical only
- **SUGGEST**: Inject context, most common
- **WARN**: Advisory, rarely used

### Skip Conditions

- **Session tracking**: Automatic (prevents repeated nags)
- **File markers**: `// @skip-validation` (permanent skip)
- **Env vars**: `SKIP_SKILL_GUARDRAILS` (emergency disable)

### Anthropic Best Practices

✅ **500-line rule**: Keep SKILL.md under 500 lines
✅ **Progressive disclosure**: Use reference files for details
✅ **Table of contents**: Add to reference files > 100 lines
✅ **One level deep**: Don't nest references deeply
✅ **Rich descriptions**: Include all trigger keywords (max 1024 chars)
✅ **Test first**: Build 3+ evaluations before extensive documentation
✅ **Gerund naming**: Prefer verb + -ing (e.g., "processing-pdfs")

### Troubleshoot

Test hooks manually:
```bash
# UserPromptSubmit
echo '{"prompt":"test"}' | npx tsx .claude/hooks/skill-activation-prompt.ts

# PreToolUse
cat <<'EOF' | npx tsx .claude/hooks/skill-verification-guard.ts
{"tool_name":"Edit","tool_input":{"file_path":"test.ts"}}
EOF
```

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for complete debugging guide.

---

## Related Files

**Configuration:**
- `.claude/skills/skill-rules.json` - Master configuration
- `.claude/hooks/state/` - Session tracking
- `.claude/settings.json` - Hook registration

**Hooks:**
- `.claude/hooks/skill-activation-prompt.ts` - UserPromptSubmit
- `.claude/hooks/error-handling-reminder.ts` - Stop event (gentle reminders)

**All Skills:**
- `.claude/skills/*/SKILL.md` - Skill content files

---

**Skill Status**: COMPLETE - Restructured following Anthropic best practices ✅
**Line Count**: < 500 (following 500-line rule) ✅
**Progressive Disclosure**: Reference files for detailed information ✅

**Next**: Create more skills, refine patterns based on usage
