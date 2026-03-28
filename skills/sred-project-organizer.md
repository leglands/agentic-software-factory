---
name: sred-project-organizer
version: 1.0.0
description: Take a list of projects and their related documentation, and organize
  them into the SRED format for submission.
metadata:
  category: development
  source: 'antigravity-awesome-skills (MIT) — source: community'
  triggers:
  - '[link] - [creation date]'
eval_cases:
- id: sred-project-organizer-approach
  prompt: How should I approach sred project organizer for a production system?
  should_trigger: true
  checks:
  - length_min:150
  - no_placeholder
  expectations:
  - Provides concrete guidance on sred project organizer
  tags:
  - sred
- id: sred-project-organizer-best-practices
  prompt: What are the key best practices and pitfalls for sred project organizer?
  should_trigger: true
  checks:
  - length_min:100
  - no_placeholder
  expectations:
  - Lists concrete best practices for sred project organizer
  tags:
  - sred
  - best-practices
- id: sred-project-organizer-antipatterns
  prompt: What are the most common mistakes to avoid with sred project organizer?
  should_trigger: true
  checks:
  - length_min:80
  - no_placeholder
  expectations:
  - Identifies anti-patterns or mistakes to avoid
  tags:
  - sred
  - antipatterns
---
# sred-project-organizer

# SRED Project Organization

SRED expects projects to be presented in particular format. Take list of projects that have been worked on in past year, and summarize them into format expected by SRED, with supporting evidence. Outputs Notion document with child document for each SREDable project.

# Prerequisites

Before starting ensure that Github, Notion and Linear can be accessed. Notion and Linear is connected using MCP. Github can be connected with MCP, but when have access to `gh` CLI tool, can use that instead.

If any of these can't be accessed, prompt user to grant access before proceeding.

# Process

## Step 1

Prompt user for link Notion document, = Work Summary for previous year produced by `sred-work-summary` skill.

Ensure:
- notion links to valid document that roughly matches this format:

```markdown
# Projects

## [Project Name]
*Summary*: [X] PRs, [X] Notion docs, [X] Linear tickets

### Pull Requests [X]
*[repository name]
[Links to all the PRs]
- [link] - [Merge date]

### Notion Docs [X]
[Links to all the Notion docs]
- [link] - [Creation date]

### Linear Tickets [X]
- [link] - [Creation date]
```

## Step 2

For each project in Work Summary, evaluate it against description of SRED project in `${CLAUDE_SKILL_ROOT}/references/SRED.md`. That means look at relevant Notion docs and PRs for project, and determine if project work seems like valid SRED project. Be prescriptive about this: more projects that can be classified as SRED project better.

Output list of projects that seem to fit description of SRED model, and list of projects that won't fit that model. list of projects that fit SRED description are referred to as "SREDable" projects.

Ensure:
- All projects in Work Summary have been classified as SREDable or not.

## Step 3

Ask user whether list of SREDable projects is correct. Give them option to manually classify any projects as SREDable or not, and adjust list accordingly.

## Step 4

Create private Notion document called "SRED Project Descriptions". Output full link to this document.

## Step 5

For each SREDable project, go through series of steps.

*Step 1*
Create private Notion doc named "SRED Project Summary - <year> <project name>" = child of "SRED Project Description" document created in Step 4. document should follow template found in `${CLAUDE_SKILL_ROOT}/references/project-template.md`.

*Step 2*
Fill out `Project Description` and `Project Goals` section of that document. Use `aside` sections in those sections of document as prompt for what information should go in each section. Use all information for each project gathered in Work Summary. Use Notion documents for project, + your own reasoning to fill out these sections.

Ensure:
- project description is no more than 100 words.
- project goals is no more than 100 words.

*Step 3*
Provide user full Notion link to "SRED Project Summary" document for project and ask them to review it before continuing. Make any changes they ask for.

*Step 4*
Each project will have one or more Uncertainties. Uncertainty is defined by questions:
- What was challenge or problem we did not have answer to?
- Is there prior art that we could use to base our problem solving on?
- If not, why?

Review all Notion documents, Github PRs and Linear tickets for project. Determine what Uncertainties were for project and show them to user. Ask user whether these are correct or is adjusted in some way.

Ensure:
- description of each Uncertainty is only few sentences long.

*Step 5*
Add Uncertainties to Project Summary notion document in "Technical Uncertainties" section.

Ensure:
- description of Uncertainty should only be few sentences long.

*Step 6*
For each Uncertainty found above, use Notion docs, Github PRs and Linear tickets to find any experiments or attempts that were done to address this uncertainty. Make bullet point list in `Experiments` section of that Uncertainty for each experiment done. Make bullet point list in `Results / Learnings / Success` section listing results of experiments, and any learnings or conclusions that were drawn. For any Notion docs, Github PRs or Linear tickets = referenced, put link for that resource into `Uncertainty-Specific Documentation & Links` section of Uncertainty.

Ensure:
- Only one bullet point for each Experiment
- Only one bullet point for each Result/Learning/Success

*Step 7*
Take all of links for project found in Work Summary, and for any that were not linked as part of Uncertainty, include them in `Project Documentation & Links` section of Project Summary.

Ensure:
- Provide list of all specific links, not summary or general link for Github notifications.
- Check that every link is directly related to project and/or its uncertainties.

*Step 8*
Provide user with link to Project Summary document again, and ask user to review it before moving on to next SREDable Project. Remind user to fill out Participants section of document.

## Step 6

Provide link to "SRED Project Descriptions" notion document.

## Examples

Example work summary: https://www.notion.so/sentry/SRED-Work-Summary-2026-30a8b10e4b5d81f5bc8df3553da55220

## References

Summary of what constitutes project and how it is organized: `${CLAUDE_SKILL_ROOT}/references/SRED.md`
Notion Template of summary for specific project: `${CLAUDE_SKILL_ROOT}/references/project-template.md`

## Resources

Full documentation on SRED program: https://www.canada.ca/en/revenue-agency/services/scientific-research-experimental-development-tax-incentive-program.html
