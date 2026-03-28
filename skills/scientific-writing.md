---
name: scientific-writing
version: 1.0.0
description: Core skill for the deep research and writing tool. Write scientific manuscripts
  in full paragraphs (never bullet points). Use two-stage process with (1) section
  outlines with key points using resea...
metadata:
  category: ai
  source: 'antigravity-awesome-skills (MIT) — source: community'
  triggers:
  - writing or revising any section of a scientific manuscript (abstract, introducti
eval_cases:
- id: scientific-writing-approach
  prompt: How should I approach scientific writing for a production system?
  should_trigger: true
  checks:
  - length_min:150
  - no_placeholder
  expectations:
  - Provides concrete guidance on scientific writing
  tags:
  - scientific
- id: scientific-writing-best-practices
  prompt: What are the key best practices and pitfalls for scientific writing?
  should_trigger: true
  checks:
  - length_min:100
  - no_placeholder
  expectations:
  - Lists concrete best practices for scientific writing
  tags:
  - scientific
  - best-practices
- id: scientific-writing-antipatterns
  prompt: What are the most common mistakes to avoid with scientific writing?
  should_trigger: true
  checks:
  - length_min:80
  - no_placeholder
  expectations:
  - Identifies anti-patterns or mistakes to avoid
  tags:
  - scientific
  - antipatterns
---
# scientific-writing

# Scientific Writing

## Overview

**Core skill for deep research + writing tool**—AI-driven research + well-formatted outputs. Every document backed by comprehensive lit search + verified citations via research-lookup skill.

Scientific writing = process for communicating research w/ precision + clarity. Write manuscripts using IMRAD structure, citations (APA/AMA/Vancouver), figures/tables, reporting guidelines (CONSORT/STROBE/PRISMA). Apply for research papers + journal submissions.

**Critical Principle: Always write in full paragraphs w/ flowing prose. Never submit bullet points in final manuscript.** Two-stage process: (1) create section outlines w/ key points using research-lookup, (2) convert outlines → complete paragraphs.

## When to Use This Skill

Use when:
- Writing/revising any section of scientific manuscript (abstract, intro, methods, results, discussion)
- Structuring research paper using IMRAD or other standard formats
- Formatting citations + references in specific styles (APA, AMA, Vancouver, Chicago, IEEE)
- Creating, formatting, improving figures, tables, data visualizations
- Applying study-specific reporting guidelines (CONSORT for trials, STROBE for observational, PRISMA for reviews)
- Drafting abstracts meeting journal requirements (structured or unstructured)
- Preparing manuscripts for specific journal submission
- Improving writing clarity, conciseness, precision
- Ensuring proper use of field-specific terminology + nomenclature
- Addressing reviewer comments + revising manuscripts

## Visual Enhancement w/ Scientific Schematics

**⚠️ MANDATORY: Every scientific paper MUST include graphical abstract + 1-2 additional AI-generated figures using scientific-schematics skill.**

Not optional. Scientific papers w/o visual elements incomplete. Before finalizing any document:
1. **ALWAYS generate a graphical abstract** as first visual element
2. Generate at minimum ONE additional schematic or diagram using scientific-schematics
3. Prefer 3-4 total figures for comprehensive papers (graphical abstract + methods flowchart + results viz + conceptual diagram)

### Graphical Abstract (REQUIRED)

**Every scientific writeup MUST include a graphical abstract.** Visual summary that:
- Appears before or immediately after text abstract
- Captures entire paper's key message in one image
- Suitable for journal table of contents display
- Uses landscape orientation (typically 1200x600px)

**Generate graphical abstract FIRST:**
```bash
python scripts/generate_schematic.py "Graphical abstract for [paper title]: [brief description showing workflow from input → methods → key findings → conclusions]" -o figures/graphical_abstract.png
```

**Graphical Abstract Requirements:**
- **Content**: Visual summary showing workflow, key methods, main findings, conclusions
- **Style**: Clean, professional, suitable for journal TOC
- **Elements**: Include 3-5 key steps/concepts w/ connecting arrows or flow
- **Text**: Minimal labels, large readable fonts
- Log: `[HH:MM:SS] GENERATED: Graphical abstract for paper summary`

### Additional Figures (GENERATE EXTENSIVELY)

**⚠️ CRITICAL: Use BOTH scientific-schematics AND generate-image EXTENSIVELY throughout all documents.**

Every document should be richly illustrated. Generate figures liberally - when in doubt, add a visual.

**MINIMUM Figure Requirements:**

| Document Type | Minimum | Recommended |
|--------------|---------|-------------|
| Research Papers | 5 | 6-8 |
| Literature Reviews | 4 | 5-7 |
| Market Research | 20 | 25-30 |
| Presentations | 1/slide | 1-2/slide |
| Posters | 6 | 8-10 |
| Grants | 4 | 5-7 |
| Clinical Reports | 3 | 4-6 |

**Use scientific-schematics EXTENSIVELY for technical diagrams:**
```bash
python scripts/generate_schematic.py "your diagram description" -o figures/output.png
```

- Study design + methodology flowcharts (CONSORT, PRISMA, STROBE)
- Conceptual framework diagrams
- Experimental workflow illustrations
- Data analysis pipeline diagrams
- Biological pathway or mechanism diagrams
- System architecture visualizations
- Neural network architectures
- Decision trees, algorithm flowcharts
- Comparison matrices, timeline diagrams
- Any technical concept benefiting from schematic visualization

**Use generate-image EXTENSIVELY for visual content:**
```bash
python scripts/generate_image.py "your image description" -o figures/output.png
```

- Photorealistic illustrations of concepts
- Medical/anatomical illustrations
- Environmental/ecological scenes
- Equipment + lab setup visualizations
- Artistic visualizations, infographics
- Cover images, header graphics
- Product mockups, prototype visualizations
- Any visual enhancing understanding or engagement

AI will automatically:
- Create publication-quality images w/ proper formatting
- Review + refine through multiple iterations
- Ensure accessibility (colorblind-friendly, high contrast)
- Save outputs in figures/ directory

**When in Doubt, Generate a Figure:**
- Complex concept → generate schematic
- Data discussion → generate visualization
- Process description → generate flowchart
- Comparison → generate comparison diagram
- Reader benefit → generate visual

For detailed guidance, refer to scientific-schematics + generate-image skill docs.

---

## Core Capabilities

### 1. Manuscript Structure + Organization

**IMRAD Format**: Guide papers through standard Introduction, Methods, Results, And Discussion structure used across most scientific disciplines. Includes:
- **Introduction**: Establish research context, identify gaps, state objectives
- **Methods**: Detail study design, populations, procedures, analysis approaches
- **Results**: Present findings objectively w/o interpretation
- **Discussion**: Interpret results, acknowledge limitations, propose future directions

For detailed IMRAD guidance, refer to `references/imrad_structure.md`.

**Alternative Structures**: Support discipline-specific formats:
- Review articles (narrative, systematic, scoping)
- Case reports + case series
- Meta-analyses + pooled analyses
- Theoretical/modeling papers
- Methods papers + protocols

### 2. Section-Specific Writing Guidance

**Abstract Composition**: Craft concise, standalone summaries (100-250 words) capturing paper's purpose, methods, results, conclusions. Support both structured (w/ labeled sections) + unstructured single-paragraph formats.

**Introduction Development**: Build compelling introductions that:
- Establish research problem's importance
- Review relevant literature systematically
- Identify knowledge gaps or controversies
- State clear research questions or hypotheses
- Explain study's novelty + significance

**Methods Documentation**: Ensure reproducibility through:
- Detailed participant/sample descriptions
- Clear procedural documentation
- Statistical methods w/ justification
- Equipment + materials specifications
- Ethical approval + consent statements

**Results Presentation**: Present findings w/:
- Logical flow from primary to secondary outcomes
- Integration w/ figures + tables
- Statistical significance w/ effect sizes
- Objective reporting w/o interpretation

**Discussion Construction**: Synthesize findings by:
- Relating results to research questions
- Comparing w/ existing literature
- Acknowledging limitations honestly
- Proposing mechanistic explanations
- Suggesting practical implications + future research

### 3. Citation + Reference Management

Apply citation styles correctly across disciplines. For comprehensive style guides, refer to `references/citation_styles.md`.

**Major Citation Styles:**
- **AMA**: Numbered superscript citations, common in medicine
- **Vancouver**: Numbered citations in square brackets, biomedical standard
- **APA**: Author-date in-text citations, common in social sciences
- **Chicago**: Notes-bibliography or author-date, humanities + sciences
- **IEEE**: Numbered square brackets, engineering + computer science

**Best Practices:**
- Cite primary sources when possible
- Include recent literature (last 5-10 years for active fields)
- Balance citation distribution across intro + discussion
- Verify all citations against original sources
- Use reference management software (Zotero, Mendeley, EndNote)

### 4. Figures + Tables

Create effective data visualizations enhancing comprehension. For detailed best practices, refer to `references/figures_tables.md`.

**When to Use Tables vs. Figures:**
- **Tables**: Precise numerical data, complex datasets, multiple variables requiring exact values
- **Figures**: Trends, patterns, relationships, comparisons best understood visually

**Design Principles:**
- Make each table/figure self-explanatory w/ complete captions
- Use consistent formatting + terminology across all display items
- Label all axes, columns, rows w/ units
- Include sample sizes (n) + statistical annotations
- Follow "one table/figure per 1000 words" guideline
- Avoid duplicating info between text, tables, figures

**Common Figure Types:**
- Bar graphs: Comparing discrete categories
- Line graphs: Showing trends over time
- Scatterplots: Displaying correlations
- Box plots: Showing distributions + outliers
- Heatmaps: Visualizing matrices + patterns

### 5. Reporting Guidelines by Study Type

Ensure completeness + transparency by following established reporting standards. For comprehensive guideline details, refer to `references/reporting_guidelines.md`.

**Key Guidelines:**
- **CONSORT**: Randomized controlled trials
- **STROBE**: Observational studies (cohort, case-control, cross-sectional)
- **PRISMA**: Systematic reviews + meta-analyses
- **STARD**: Diagnostic accuracy studies
- **TRIPOD**: Prediction model studies
- **ARRIVE**: Animal research
- **CARE**: Case reports
- **SQUIRE**: Quality improvement studies
- **SPIRIT**: Study protocols for clinical trials
- **CHEERS**: Economic evaluations

Each guideline provides checklists ensuring all critical methodological elements reported.

### 6. Writing Principles + Style

Apply fundamental scientific writing principles. For detailed guidance, refer to `references/writing_principles.md`.

**Clarity**:
- Use precise, unambiguous language
- Define technical terms + abbreviations at first use
- Maintain logical flow within + between paragraphs
- Use active voice when appropriate for clarity

**Conciseness**:
- Eliminate redundant words + phrases
- Favor shorter sentences (15-20 words average)
- Remove unnecessary qualifiers
- Respect word limits strictly

**Accuracy**:
- Report exact values w/ appropriate precision
- Use consistent terminology throughout
- Distinguish between observations + interpretations
- Acknowledge uncertainty appropriately

**Objectivity**:
- Present results w/o bias
- Avoid overstating findings or implications
- Acknowledge conflicting evidence
- Maintain professional, neutral tone

### 7. Writing Process: From Outline to Full Paragraphs

**CRITICAL: Always write in full paragraphs, never submit bullet points in scientific papers.**

Scientific papers must be written in complete, flowing prose. Use two-stage approach for effective writing:

**Stage 1: Create Section Outlines w/ Key Points**

When starting new section:
1. Use research-lookup skill to gather relevant literature + data
2. Create structured outline w/ bullet points marking:
   - Main arguments or findings to present
   - Key studies to cite
   - Data points + statistics to include
   - Logical flow + organization
3. These bullet points serve as scaffolding—they are NOT final manuscript

**Example outline (Introduction section):**
```
- Background: AI in drug discovery gaining traction
  * Cite recent reviews (Smith 2023, Jones 2024)
  * Traditional methods are slow + expensive
- Gap: Limited application to rare diseases
  * Only 2 prior studies (Lee 2022, Chen 2023)
  * Small datasets remain a challenge
- Our approach: Transfer learning from common diseases
  * Novel architecture combining X + Y
- Study objectives: Validate on 3 rare disease datasets
```

**Stage 2: Convert Key Points to Full Paragraphs**

Once outline complete, expand each bullet point into proper prose:

1. **Transform bullet points into complete sentences** w/ subjects, verbs, objects
2. **Add transitions** between sentences + ideas (however, moreover, in contrast, subsequently)
3. **Integrate citations naturally** within sentences, not as lists
4. **Expand w/ context + explanation** that bullet points omit
5. **Ensure logical flow** from one sentence to next within each paragraph
6. **Vary sentence structure** to maintain reader engagement

**Example conversion to prose:**

```
Artificial intelligence approaches have gained significant traction in drug discovery 
pipelines over the past decade (Smith, 2023; Jones, 2024). While these computational 
methods show promise for accelerating the identification of therapeutic candidates, 
traditional experimental approaches remain slow and resource-intensive, often requiring 
years of laboratory work and substantial financial investment. However, the application 
of AI to rare diseases has been limited, with only two prior studies demonstrating 
proof-of-concept results (Lee, 2022; Chen, 2023). The primary obstacle has been the 
scarcity of training data for conditions affecting small patient populations. 

To address this challenge, we developed a transfer learning approach that leverages 
knowledge from well-characterized common diseases to predict therapeutic targets for 
rare conditions. Our novel neural architecture combines convolutional layers for 
molecular feature extraction with attention mechanisms for protein-ligand interaction 
modeling. The objective of this study was to validate our approach across three 
independent rare disease datasets, assessing both predictive accuracy and biological 
interpretability of the results.
```

**Key Differences Between Outlines + Final Text:**

| Outline (Planning) | Final Manuscript |
|--------------------|------------------|
| Bullet points + fragments | Complete sentences + paragraphs |
| Telegraphic notes | Full explanations w/ context |
| List of citations | Citations integrated into prose |
| Abbreviated ideas | Developed arguments w/ transitions |
| For your eyes only | For publication + peer review |

**Common Mistakes to Avoid:**

- ❌ **Never** leave bullet points in final manuscript
- ❌ **Never** submit lists where paragraphs should be
- ❌ **Don't** use numbered or bulleted lists in Results or Discussion (except specific cases like study hypotheses or inclusion criteria)
- ❌ **Don't** write sentence fragments or incomplete thoughts
- ✅ **Do** use occasional lists only in Methods (e.g., inclusion/exclusion criteria, materials lists)
- ✅ **Do** ensure every section flows as connected prose
- ✅ **Do** read paragraphs aloud to check for natural flow

**When Lists ARE Acceptable (Limited Cases):**

Lists may appear in scientific papers only in specific contexts:
- **Methods**: Inclusion/exclusion criteria, materials + reagents, participant characteristics
- **Supplementary Materials**: Extended protocols, equipment lists, detailed parameters
- **Never in**: Abstract, Introduction, Results, Discussion, Conclusions

**Abstract Format Rule:**
- ❌ **NEVER** use labeled sections (Background:, Methods:, Results:, Conclusions:)
- ✅ **ALWAYS** write as flowing paragraph(s) w/ natural transitions
- Exception: Only use structured format if journal explicitly requires it in author guidelines

**Integration w/ Research Lookup:**

research-lookup skill essential for Stage 1 (creating outlines):
1. Search for relevant papers using research-lookup
2. Extract key findings, methods, data
3. Organize findings as bullet points in outline
4. Then convert outline to full paragraphs in Stage 2

Two-stage process ensures you:
- Gather + organize information systematically
- Create logical structure before writing
- Produce polished, publication-ready prose
- Maintain focus on narrative flow

### 8. Professional Report Formatting (Non-Journal Documents)

For research reports, technical reports, white papers, other professional documents that are NOT journal manuscripts, use `scientific_report.sty` LaTeX style package for polished, professional appearance.

**When to Use Professional Report Formatting:**
- Research reports + technical reports
- White papers + policy briefs
- Grant reports + progress reports
- Industry reports + technical documentation
- Internal research summaries
- Feasibility studies + project deliverables

**When NOT to Use (Use Venue-Specific Formatting Instead):**
- Journal manuscripts → Use `venue-templates` skill
- Conference papers → Use `venue-templates` skill
- Academic theses → Use institutional templates

**The `scientific_report.sty` Style Package Provides:**

| Feature | Description |
|---------|-------------|
| Typography | Helvetica font family for modern, professional appearance |
| Color Scheme | Professional blues, greens, accent colors |
| Box Environments | Colored boxes for key findings, methods, recommendations, limitations |
| Tables | Alternating row colors, professional headers |
| Figures | Consistent caption formatting |
| Scientific Commands | Shortcuts for p-values, effect sizes, confidence intervals |

**Box Environments for Content Organization:**

```latex
% Key findings (blue) - for major discoveries
\begin{keyfindings}[Title]
Content with key findings and statistics.
\end{keyfindings}

% Methodology (green) - for methods highlights
\begin{methodology}[Study Design]
Description of methods and procedures.
\end{methodology}

% Recommendations (purple) - for action items
\begin{recommendations}[Clinical Implications]
\begin{enumerate}
    \item Specific recommendation 1
    \item Specific recommendation 2
\end{enumerate}
\end{recommendations}

% Limitations (orange) - for caveats + cautions
\begin{limitations}[Study Limitations]
Description of limitations and their implications.
\end{limitations}
```

**Professional Table Formatting:**

```latex
\begin{table}[htbp]
\centering
\caption{Results Summary}
\begin{tabular}{@{}lccc@{}}
\toprule
\textbf{Variable} & \textbf{Treatment} & \textbf{Control} & \textbf{p} \\
\midrule
Outcome 1 & \meansd{42.5}{8.3} & \meansd{35.2}{7.9} & <.001\sigthree \\
\rowcolor{tablealt} Outcome 2 & \meansd{3.8}{1.2} & \meansd{3.1}{1.1} & .012\sigone \\
Outcome 3 & \meansd{18.2}{4.5} & \meansd{17.8}{4.2} & .58\signs \\
\bottomrule
\end{tabular}

{\small \siglegend}
\end{table}
```

**Scientific Notation Commands:**

| Command | Output | Purpose |
|---------|--------|---------|
| `\pvalue{0.023}` | *p* = 0.023 | P-values |
| `\psig{< 0.001}` | ***p* = < 0.001** | Significant p-values (bold) |
| `\CI{0.45}{0.72}` | 95% CI [0.45, 0.72] | Confidence intervals |
| `\effectsize{d}{0.75}` | d = 0.75 | Effect sizes |
| `\samplesize{250}` | *n* = 250 | Sample sizes |
| `\meansd{42.5}{8.3}` | 42.5 ± 8.3 | Mean w/ SD |
| `\sigone`, `\sigtwo`, `\sigthree` | *, **, *** | Significance stars |

**Getting Started:**

```latex
\documentclass[11pt,letterpaper]{report}
\usepackage{scientific_report}

\begin{document}
\makereporttitle
    {Report Title}
    {Subtitle}
    {Author Name}
    {Institution}
    {Date}

% Your content with professional formatting
\end{document}
```

**Compilation**: Use XeLaTeX or LuaLaTeX for proper Helvetica font rendering:
```bash
xelatex report.tex
```

For complete documentation, refer to:
- `assets/scientific_report.sty`: The style package
- `assets/scientific_report_template.tex`: Complete template example
- `assets/REPORT_FORMATTING_GUIDE.md`: Quick reference guide
- `references/professional_report_formatting.md`: Comprehensive formatting guide

### 9. Journal-Specific Formatting

Adapt manuscripts to journal requirements:
- Follow author guidelines for structure, length, format
- Apply journal-specific citation styles
- Meet figure/table specs (resolution, file formats, dimensions)
- Include required statements (funding, conflicts of interest, data availability, ethical approval)
- Adhere to word limits for each section
- Format according to template requirements when provided

### 10. Field-Specific Language + Terminology

Adapt language, terminology, conventions to match specific scientific discipline. Each field has established vocabulary, preferred phrasings, domain-specific conventions signaling expertise + ensuring clarity for target audience.

**Identify Field-Specific Linguistic Conventions:**
- Review terminology used in recent high-impact papers in target journal
- Note field-specific abbreviations, units, notation systems
- Identify preferred terms (e.g., "participants" vs. "subjects," "compound" vs. "drug," "specimens" vs. "samples")
- Observe how methods, organisms, or techniques typically described

**Biomedical + Clinical Sciences:**
- Use precise anatomical + clinical terminology (e.g., "myocardial infarction" not "heart attack" in formal writing)
- Follow standardized disease nomenclature (ICD, DSM, SNOMED-CT)
- Specify drug names using generic names first, brand names in parentheses if needed
- Use "patients" for clinical studies, "participants" for community-based research
- Follow Human Genome Variation Society (HGVS) nomenclature for genetic variants
- Report lab values w/ standard units (SI units in most international journals)

**Molecular Biology + Genetics:**
- Use italics for gene symbols (e.g., *TP53*), regular font for proteins (e.g., p53)
- Follow species-specific gene nomenclature (uppercase for human: *BRCA1*; sentence case for mouse: *Brca1*)
- Specify organism names in full at first mention, then use accepted abbreviations (e.g., *Escherichia coli*, then *E. coli*)
- Use standard genetic notation (e.g., +/+, +/-, -/- for genotypes)
- Employ established terminology for molecular techniques (e.g., "quantitative PCR" or "qPCR," not "real-time PCR")

**Chemistry + Pharmaceutical Sciences:**
- Follow IUPAC nomenclature for chemical compounds
- Use systematic names for novel compounds, common names for well-known substances
- Specify chemical structures using standard notation (e.g., SMILES, InChI for databases)
- Report concentrations w/ appropriate units (mM, μM, nM, or % w/v, v/v)
- Describe synthesis routes using accepted reaction nomenclature
- Use terms like "bioavailability," "pharmacokinetics," "IC50" consistently w/ field definitions

**Ecology + Environmental Sciences:**
- Use binomial nomenclature for species (italicized: *Homo sapiens*)
- Specify taxonomic authorities at first species mention when relevant
- Employ standardized habitat + ecosystem classifications
- Use consistent terminology for ecological metrics (e.g., "species richness," "Shannon diversity index")
- Describe sampling methods w/ field-standard terms (e.g., "transect," "quadrat," "mark-recapture")

**Physics + Engineering:**
- Follow SI units consistently unless field conventions dictate otherwise
- Use standard notation for physical quantities (scalars vs. vectors, tensors)
- Employ established terminology for phenomena (e.g., "quantum entanglement," "laminar flow")
- Specify equipment w/ model numbers + manufacturers when relevant
- Use mathematical notation consistent w/ field standards (e.g., ℏ for reduced Planck constant)

**Neuroscience:**
- Use standardized brain region nomenclature (e.g., refer to atlases like Allen Brain Atlas)
- Specify coordinates for brain regions using established stereotaxic systems
- Follow conventions for neural terminology (e.g., "action potential" not "spike" in formal writing)
- Use "neural activity," "neuronal firing," "brain activation" appropriately based on measurement method
- Describe recording techniques w/ proper specificity (e.g., "whole-cell patch clamp," "extracellular recording")

**Social + Behavioral Sciences:**
- Use person-first language when appropriate (e.g., "people with schizophrenia" not "schizophrenics")
- Employ standardized psychological constructs + validated assessment names
- Follow APA guidelines for reducing bias in language
- Specify theoretical frameworks using established terminology
- Use "participants" rather than "subjects" for human research

**General Principles:**

**Match Audience Expertise:**
- For specialized journals: Use field-specific terminology freely, define only highly specialized or novel terms
- For broad-impact journals (e.g., *Nature*, *Science*): Define more technical terms, provide context for specialized concepts
- For interdisciplinary audiences: Balance precision w/ accessibility, define terms at first use

**Define Technical Terms Strategically:**
- Define abbreviations at first use: "messenger RNA (mRNA)"
- Provide brief explanations for specialized techniques when writing for broader audiences
- Avoid over-defining terms well-known to target audience (signals unfamiliarity w/ field)
- Create glossary if numerous specialized terms unavoidable

**Maintain Consistency:**
- Use same term for same concept throughout (don't alternate between "medication," "drug," "pharmaceutical")
- Follow consistent system for abbreviations (decide on "PCR" or "polymerase chain reaction" after first definition)
- Apply same nomenclature system throughout (especially for genes, species, chemicals)

**Avoid Field Mixing Errors:**
- Don't use clinical terminology for basic science (e.g., don't call mice "patients")
- Avoid colloquialisms or overly general terms in place of precise field terminology
- Don't import terminology from adjacent fields w/o ensuring proper usage

**Verify Terminology Usage:**
- Consult field-specific style guides + nomenclature resources
- Check how terms used in recent papers from target journal
- Use domain-specific databases + ontologies (e.g., Gene Ontology, MeSH terms)
- When uncertain, cite key reference establishing terminology

### 11. Common Pitfalls to Avoid

**Top Rejection Reasons:**
1. Inappropriate, incomplete, insufficiently described statistics
2. Over-interpretation of results or unsupported conclusions
3. Poorly described methods affecting reproducibility
4. Small, biased, or inappropriate samples
5. Poor writing quality or difficult-to-follow text
6. Inadequate literature review or context
7. Figures + tables unclear or poorly designed
8. Failure to follow reporting guidelines

**Writing Quality Issues:**
- Mixing tenses inappropriately (use past tense for methods/results, present for established facts)
- Excessive jargon or undefined acronyms
- Paragraph breaks disrupting logical flow
- Missing transitions between sections
- Inconsistent notation or terminology

## Workflow for Manuscript Development

**Stage 1: Planning**
1. Identify target journal + review author guidelines
2. Determine applicable reporting guideline (CONSORT, STROBE, etc.)
3. Outline manuscript structure (usually IMRAD)
4. Plan figures + tables as backbone of paper

**Stage 2: Drafting** (Use two-stage writing process for each section)
1. Start w/ figures + tables (core data story)
2. For each section below, follow two-stage process:
   - **First**: Create outline w/ bullet points using research-lookup
   - **Second**: Convert bullet points to full paragraphs w/ flowing prose
3. Write Methods (often easiest to draft first)
4. Draft Results (describing figures/tables objectively)
5. Compose Discussion (interpreting findings)
6. Write Introduction (setting up research question)
7. Craft Abstract (synthesizing complete story)
8. Create Title (concise + descriptive)

**Remember**: Bullet points are for planning only—final manuscript must be in complete paragraphs.

**Stage 3: Revision**
1. Check logical flow + "red thread" throughout
2. Verify consistency in terminology + notation
3. Ensure figures/tables are self-explanatory
4. Confirm adherence to reporting guidelines
5. Verify all citations accurate + properly formatted
6. Check word counts for each section
7. Proofread for grammar, spelling, clarity

**Stage 4: Final Preparation**
1. Format according to journal requirements
2. Prepare supplementary materials
3. Write cover letter highlighting significance
4. Complete submission checklists
5. Gather all required statements + forms

## Integration w/ Other Scientific Skills

This skill works effectively w/:
- **Data analysis skills**: For generating results to report
- **Statistical analysis**: For determining appropriate statistical presentations
- **Literature review skills**: For contextualizing research
- **Figure creation tools**: For developing publication-quality visualizations
- **venue-templates skill**: For venue-specific writing styles + formatting (journal manuscripts)
- **scientific_report.sty**: For professional reports, white papers, technical documents

### Professional Reports vs. Journal Manuscripts

**Choose right formatting approach:**

| Document Type | Formatting Approach |
|---------------|---------------------|
| Journal manuscripts | Use `venue-templates` skill |
| Conference papers | Use `venue-templates` skill |
| Research reports | Use `scientific_report.sty` (this skill) |
| White papers | Use `scientific_report.sty` (this skill) |
| Technical reports | Use `scientific_report.sty` (this skill) |
| Grant reports | Use `scientific_report.sty` (this skill) |

### Venue-Specific Writing Styles

**Before writing for specific venue, consult venue-templates skill for writing style guides:**

Different venues have dramatically different writing expectations:
- **Nature/Science**: Accessible, story-driven, broad significance
- **Cell Press**: Mechanistic depth, graphical abstracts, Highlights
- **Medical journals (NEJM, Lancet)**: Structured abstracts, evidence language
- **ML conferences (NeurIPS, ICML)**: Contribution bullets, ablation studies
- **CS conferences (CHI, ACL)**: Field-specific conventions

venue-templates skill provides:
- `venue_writing_styles.md`: Master style comparison
- Venue-specific guides: `nature_science_style.md`, `cell_press_style.md`, `medical_journal_styles.md`, `ml_conference_style.md`, `cs_conference_style.md`
- `reviewer_expectations.md`: What reviewers look for at each venue
- Writing examples in `assets/examples/`

**Workflow**: First use this skill for general scientific writing principles (IMRAD, clarity, citations), then consult venue-templates for venue-specific style adaptation.

## References

This skill includes comprehensive reference files covering specific aspects:

- `references/imrad_structure.md`: Detailed guide to IMRAD format + section-specific content
- `references/citation_styles.md`: Complete citation style guides (APA, AMA, Vancouver, Chicago, IEEE)
- `references/figures_tables.md`: Best practices for creating effective data visualizations
- `references/reporting_guidelines.md`: Study-specific reporting standards + checklists
- `references/writing_principles.md`: Core principles of effective scientific communication
- `references/professional_report_formatting.md`: Guide to professional report styling w/ `scientific_report.sty`

## Assets

This skill includes LaTeX style packages + templates for professional report formatting:

- `assets/scientific_report.sty`: Professional LaTeX style package w/ Helvetica fonts, colored boxes, attractive tables
- `assets/scientific_report_template.tex`: Complete report template demonstrating all style features
- `assets/REPORT_FORMATTING_GUIDE.md`: Quick reference guide for style package

**Key Features of `scientific_report.sty`:**
- Helvetica font family for modern, professional appearance
- Professional color scheme (blues, greens, oranges, purples)
- Box environments: `keyfindings`, `methodology`, `resultsbox`, `recommendations`, `limitations`, `criticalnotice`, `definition`, `executivesummary`, `hypothesis`
- Tables w/ alternating row colors + professional headers
- Scientific notation commands for p-values, effect sizes, confidence intervals
- Professional headers + footers

**For venue-specific writing styles** (tone, voice, abstract format, reviewer expectations), see **venue-templates** skill which provides comprehensive style guides for Nature/Science, Cell Press, medical journals, ML conferences, CS conferences.

Load these references as needed when working on specific aspects of scientific writing.
