---
name: customs-trade-compliance
version: 1.0.0
description: Codified expertise for customs documentation, tariff classification,
  duty optimisation, restricted party screening, and regulatory compliance across
  multiple jurisdictions.
metadata:
  category: development
  source: 'antigravity-awesome-skills (MIT) — source: https://github.com/ai-evos/agent-skills'
  triggers:
  - when working on customs trade compliance
eval_cases:
- id: customs-trade-compliance-approach
  prompt: How should I approach customs trade compliance for a production system?
  should_trigger: true
  checks:
  - length_min:150
  - no_placeholder
  expectations:
  - Provides concrete guidance on customs trade compliance
  tags:
  - customs
- id: customs-trade-compliance-best-practices
  prompt: What are the key best practices and pitfalls for customs trade compliance?
  should_trigger: true
  checks:
  - length_min:100
  - no_placeholder
  expectations:
  - Lists concrete best practices for customs trade compliance
  tags:
  - customs
  - best-practices
- id: customs-trade-compliance-antipatterns
  prompt: What are the most common mistakes to avoid with customs trade compliance?
  should_trigger: true
  checks:
  - length_min:80
  - no_placeholder
  expectations:
  - Identifies anti-patterns or mistakes to avoid
  tags:
  - customs
  - antipatterns
---
# customs-trade-compliance

## When to Use

Use when navigating international trade regulations, classifying goods under HS codes, determining Incoterms, managing import/export documentation, or optimising customs duty via FTAs.

# Customs & Trade Compliance

## Role and Context

Senior trade compliance specialist, 15+ yrs managing customs ops across US, EU, UK, Asia-Pacific. Interface: importers, exporters, customs brokers, freight forwarders, government agencies, legal counsel. Systems: ACE (Automated Commercial Environment), CHIEF/CDS (UK), ATLAS (DE), customs broker portals, denied party screening platforms, ERP trade management modules. Ensure lawful, cost-optimised movement of goods across borders; protect org from penalties, seizures, debarment.

## Core Knowledge

### HS Tariff Classification

Harmonized System: 6-digit international nomenclature maintained by WCO. First 2 digits = chapter, 4 digits = heading, 6 digits = subheading. National extensions: US uses 10-digit HTS numbers (Schedule B for exports), EU uses 10-digit TARIC codes, UK uses 10-digit commodity codes via UK Global Tariff.

Classification follows General Rules of Interpretation (GRI) in strict order — never invoke GRI 3 unless GRI 1 fails, never GRI 4 unless 1-3 fail:

- **GRI 1:** Classification determined by heading terms + Section/Chapter notes. Resolves ~90% of classifications. Read heading text literally; check every relevant Section/Chapter note before proceeding.
- **GRI 2(a):** Incomplete/unfinished articles → classify as complete article if they have essential character of complete article. Car body without engine = motor vehicle.
- **GRI 2(b):** Mixtures + combinations of materials → classify by material giving essential character.
- **GRI 3(a):** Goods prima facie classifiable under 2+ headings → prefer most specific heading. "Surgical gloves of rubber" > "articles of rubber."
- **GRI 3(b):** Composite goods, sets → classify by component giving essential character. Gift set w/ $40 perfume + $5 pouch → perfume.
- **GRI 3(c):** When 3(a) + 3(b) fail → use heading occurring last in numerical order.
- **GRI 4:** Goods cannot be classified by GRI 1-3 → classify under heading for most analogous goods.
- **GRI 5:** Cases, containers, packing materials → specific rules for classification w/ or separately from contents.
- **GRI 6:** Subheading level follows same principles within relevant heading. Subheading notes take precedence at this level.

**Common misclassification pitfalls:** Multi-function devices (classify by primary function per GRI 3(b), not most expensive component). Food preparations vs ingredients (Chapter 21 vs Chapters 7-12 — check whether product has been "prepared" beyond simple preservation). Textile composites (weight % of fibres determines classification, not surface area). Parts vs accessories (Section XVI Note 2 determines whether part classifies w/ machine or separately). Software on physical media (medium, not software, determines classification).

### Documentation Requirements

**Commercial Invoice:** Must include seller/buyer names + addresses, description of goods sufficient for classification, quantity, unit price, total value, currency, Incoterms, country of origin, payment terms. US CBP requires invoice conform to 19 CFR § 141.86. Undervaluation → penalties per 19 USC § 1592.

**Packing List:** Weight + dimensions per package, marks + numbers matching BOL, piece count. Discrepancies between packing list + physical count trigger examination.

**Certificate of Origin:** Varies by FTA. USMCA uses certification (no prescribed form) w/ nine data elements per Article 5.2. EUR.1 movement certificates for EU preferential trade. Form A for GSP claims. UK uses "origin declarations" on invoices for UK-EU TCA claims.

**Bill of Lading / Air Waybill:** Ocean BOL = title to goods, contract of carriage, + receipt. Air waybill = non-negotiable. Both must match commercial invoice — carrier-added notations ("said to contain," "shipper's load and count") limit carrier liability + affect customs risk scoring.

**ISF 10+2 (US):** Importer Security Filing — submitted 24 hrs before vessel loading at foreign port. Ten data elements from importer (manufacturer, seller, buyer, ship-to, country of origin, HS-6, container stuffing location, consolidator, importer of record number, consignee number). Two from carrier. Late/inaccurate ISF → $5,000 per violation liquidated damages. CBP uses ISF data for targeting; errors increase examination probability.

**Entry Summary (CBP 7501):** Filed within 10 business days of entry. Contains classification, value, duty rate, country of origin, preferential program claims. Legal declaration — errors create penalty exposure under 19 USC § 1592.

### Incoterms 2020

Incoterms define transfer of costs, risk, + responsibility between buyer + seller. Not law — contractual terms must be explicitly incorporated. Critical compliance implications:

- **EXW (Ex Works):** Seller's minimum obligation. Buyer arranges everything. Problem: buyer = exporter of record in seller's country → export compliance obligations buyer may not handle. Rarely appropriate.
- **FCA (Free Carrier):** Seller delivers to carrier at named place. Seller handles export clearance. 2020 revision allows buyer to instruct carrier to issue on-board BOL to seller — critical for letter of credit transactions.
- **CPT/CIP (Carriage Paid To / Carriage & Insurance Paid To):** Risk transfers at first carrier; seller pays freight to destination. CIP now requires Institute Cargo Clauses (A) — all-risks coverage; significant change from Incoterms 2010.
- **DAP (Delivered at Place):** Seller bears all risk + cost to destination, excluding import clearance + duties. Seller does not clear customs in destination country.
- **DDP (Delivered Duty Paid):** Seller bears everything including import duties + taxes. Seller must be registered as importer of record or use non-resident importer arrangement. Customs valuation based on DDP price minus duties (deductive method) — if seller includes duty in invoice price → circular valuation problem.
- **Valuation impact:** Under CIF/CIP, customs value includes freight + insurance. Under FOB/FCA, importing country may add freight to arrive at transaction value (US adds ocean freight; EU does not). Getting this wrong changes duty calculation.
- **Common misunderstandings:** Incoterms do not transfer title to goods — governed by sale contract + applicable law. Incoterms do not apply to domestic-only transactions by default — must be explicitly invoked. Using FOB for containerised ocean freight is technically incorrect (FCA preferred) — risk transfers at ship's rail under FOB but at container yard under FCA.

### Duty Optimisation

**FTA Utilisation:** Every preferential trade agreement has specific rules of origin goods must satisfy. USMCA requires product-specific rules (Annex 4-B) including tariff shift, regional value content (RVC), + net cost methods. EU-UK TCA uses "wholly obtained" + "sufficient processing" rules w/ product-specific list rules in Annex ORIG-2. RCEP has uniform rules for 15 Asia-Pacific nations w/ cumulation provisions. AfCFTA allows 60% cumulation across member states.

**RVC calculation matters:** USMCA offers two methods — transaction value (TV): RVC = ((TV - VNM) / TV) × 100; + net cost (NC): RVC = ((NC - VNM) / NC) × 100. Net cost method excludes sales promotion, royalties, + shipping costs from denominator — often yields higher RVC when margins are thin.

**Foreign Trade Zones (FTZs):** Goods admitted to FTZ are not in US customs territory. Benefits: duty deferral until goods enter commerce; inverted tariff relief (pay duty on finished product rate if lower than component rates); no duty on waste/scrap; no duty on re-exports. Zone-to-zone transfers maintain privileged foreign status.

**Temporary Import Bonds (TIBs):** ATA Carnet for professional equipment, samples, exhibition goods — duty-free entry into 78+ countries. US temporary importation under bond (TIB) per 19 USC § 1202, Chapter 98 — goods must be exported within 1 yr (extendable to 3 yrs). Failure to export → liquidation at full duty plus bond premium.

**Duty Drawback:** Refund of 99% of duties paid on imported goods subsequently exported. Three types: manufacturing drawback (imported materials used in US-manufactured exports), unused merchandise drawback (imported goods exported in same condition), + substitution drawback (commercially interchangeable goods). Claims filed within 5 yrs of import. TFTEA simplified drawback — no longer requires matching specific import entries to specific export entries for substitution claims.

### Restricted Party Screening

**Mandatory lists (US):** SDN (OFAC — Specially Designated Nationals), Entity List (BIS — export control), Denied Persons List (BIS — export privilege denied), Unverified List (BIS — cannot verify end use), Military End User List (BIS), Non-SDN Menu-Based Sanctions (OFAC). Screening must cover all parties: buyer, seller, consignee, end user, freight forwarder, banks, + intermediate consignees.

**EU/UK lists:** EU Consolidated Sanctions List, UK OFSI Consolidated List, UK Export Control Joint Unit.

**Red flags triggering enhanced due diligence:** Customer reluctant to provide end-use info. Unusual routing (high-value goods through free ports). Customer willing to pay cash for expensive items. Delivery to freight forwarder or trading company w/ no clear end user. Product capabilities exceed stated application. Customer has no business background in product type. Order patterns inconsistent w/ customer's business.

**False positive management:** ~95% of screening hits are false positives. Adjudication requires: exact name match vs partial match, address correlation, date of birth (for individuals), country nexus, alias analysis. Document adjudication rationale for every hit — regulators will ask during audits.

### Regional Specialties

**US CBP:** Centers of Excellence + Expertise (CEEs) specialise by industry. Trusted Trader programmes: C-TPAT (security) + Trusted Trader (combining C-TPAT + ISA). ACE = single window for all import/export data. Focused Assessment audits target specific compliance areas — prior disclosure before FA starts is critical.

**EU Customs Union:** Common External Tariff (CET) applies uniformly. Authorised Economic Operator (AEO) provides AEOC (customs simplifications) + AEOS (security). Binding Tariff Information (BTI) provides classification certainty for 3 yrs. Union Customs Code (UCC) governs since 2016.

**UK post-Brexit:** UK Global Tariff replaced CET. Northern Ireland Protocol / Windsor Framework creates dual-status goods. UK Customs Declaration Service (CDS) replaced CHIEF. UK-EU TCA requires Rules of Origin compliance for zero-tariff treatment — "originating" requires either wholly obtained in UK/EU or sufficient processing.

**China:** CCC (China Compulsory Certification) required for listed product categories before import. China uses 13-digit HS codes. Cross-border e-commerce has distinct clearance channels (9610, 9710, 9810 trade modes). Recent Unreliable Entity List creates new screening obligations.

### Penalties and Compliance

**US penalty framework under 19 USC § 1592:**

- **Negligence:** 2× unpaid duties or 20% of dutiable value for first violation. Reduced to 1× or 10% w/ mitigation. Most common assessment.
- **Gross negligence:** 4× unpaid duties or 40% of dutiable value. Harder to mitigate — requires showing systemic compliance measures.
- **Fraud:** Full domestic value of merchandise. Criminal referral possible. No mitigation without extraordinary cooperation.

**Prior disclosure (19 CFR § 162.74):** Filing prior disclosure before CBP initiates investigation caps penalties at interest on unpaid duties for negligence, 1× duties for gross negligence. Single most powerful tool in penalty mitigation. Requirements: identify violation, provide correct information, tender unpaid duties. Must be filed before CBP issues pre-penalty notice or commences formal investigation.

**Record-keeping:** 19 USC § 1508 requires 5-year retention of all entry records. EU requires 3 yrs (some member states require 10). Failure to produce records during audit → adverse inference — CBP can reconstruct value/classification unfavourably.

## Decision Frameworks

### Classification Decision Logic

When classifying product, follow sequence without shortcuts. See [decision-frameworks.md](references/decision-frameworks.md) for full decision trees.

1. **Identify good precisely.** Get full technical specification — material composition, function, dimensions, intended use. Never classify from product name alone.
2. **Determine Section + Chapter.** Use Section + Chapter notes to confirm or exclude. Chapter notes override heading text.
3. **Apply GRI 1.** Read heading terms literally. If only one heading covers good → classification decided.
4. **If GRI 1 produces multiple candidate headings,** apply GRI 2 then GRI 3 in sequence. For composite goods, determine essential character by function, value, bulk, or factor most relevant to specific good.
5. **Validate at subheading level.** Apply GRI 6. Check subheading notes. Confirm national tariff line (8/10-digit) aligns w/ 6-digit determination.
6. **Check for binding rulings.** Search CBP CROSS database, EU BTI database, or WCO classification opinions for same or analogous products. Existing rulings are persuasive even if not directly binding.
7. **Document rationale.** Record GRI applied, headings considered + rejected, + determining factor. This documentation = defence in audit.

### FTA Qualification Analysis

1. **Identify applicable FTAs** based on origin + destination countries.
2. **Determine product-specific rule of origin.** Look up HS heading in relevant FTA's annex. Rules vary by product — some require tariff shift, some require minimum RVC, some require both.
3. **Trace all non-originating materials** through bill of materials. Each input must be classified to determine whether tariff shift has occurred.
4. **Calculate RVC if required.** Choose method yielding most favourable result (where FTA offers choice). Verify all cost data w/ supplier.
5. **Apply cumulation rules.** USMCA allows accumulation across US, Mexico, + Canada. EU-UK TCA allows bilateral cumulation. RCEP allows diagonal cumulation among all 15 parties.
6. **Prepare certification.** USMCA certifications must include nine prescribed data elements. EUR.1 requires Chamber of Commerce or customs authority endorsement. Retain supporting documentation for 5 yrs (USMCA) or 4 yrs (EU).

### Valuation Method Selection

Customs valuation follows WTO Agreement on Customs Valuation (based on GATT Article VII). Methods applied in hierarchical order — proceed to next method only when prior method cannot be applied:

1. **Transaction Value (Method 1):** Price actually paid or payable, adjusted for additions (assists, royalties, commissions, packing) + deductions (post-importation costs, duties). Used for ~90% of entries. Fails when: related-party transaction where relationship influenced price; no sale (consignment, leases, free goods); or conditional sale w/ unquantifiable conditions.
2. **Transaction Value of Identical Goods (Method 2):** Same goods, same country of origin, same commercial level. Rarely available — "identical" is strictly defined.
3. **Transaction Value of Similar Goods (Method 3):** Commercially interchangeable goods. Broader than Method 2 but still requires same country of origin.
4. **Deductive Value (Method 4):** Start from resale price in importing country, deduct: profit margin, transport, duties, + any post-importation processing costs.
5. **Computed Value (Method 5):** Build up from: cost of materials, fabrication, profit, + general expenses in country of export. Only available if exporter cooperates w/ cost data.
6. **Fallback Method (Method 6):** Flexible application of Methods 1-5 w/ reasonable adjustments. Cannot be based on arbitrary values, minimum values, or price of goods in domestic market of exporting country.

### Screening Hit Assessment

When restricted party screening tool returns match, do not block transaction automatically or clear without investigation. Follow protocol:

1. **Assess match quality:** Name match %, address correlation, country nexus, alias analysis, date of birth (individuals). Matches below 85% name similarity w/ no address or country correlation → likely false positives — document + clear.
2. **Verify entity identity:** Cross-reference against company registrations, D&B numbers, website verification, + prior transaction history. Legitimate customer w/ years of clean transaction history + partial name match to SDN entry → almost certainly false positive.
3. **Check list specifics:** SDN hits require OFAC licence to proceed. Entity List hits require BIS licence w/ presumption of denial. Denied Persons List hits = absolute prohibitions — no licence available.
4. **Escalate true positives + ambiguous cases** to compliance counsel immediately. Never proceed w/ transaction while screening hit is unresolved.
5. **Document everything.** Record screening tool used, date, match details, adjudication rationale, + disposition. Retain for 5 yrs minimum.

## Key Edge Cases

Situations where obvious approach is wrong. Brief summaries — see [edge-cases.md](references/edge-cases.md) for full analysis.

1. **De minimis threshold exploitation:** Supplier restructures shipments to stay below $800 US de minimis threshold to avoid duties. Multiple shipments on same day to same consignee may be aggregated by CBP. Section 321 entry does not eliminate quota, AD/CVD, or PGA requirements — only waives duty.

2. **Transshipment circumventing AD/CVD orders:** Goods manufactured in China but routed through Vietnam w/ minimal processing to claim Vietnamese origin. CBP uses evasion investigations (EAPA) w/ subpoena power. "Substantial transformation" test requires new article of commerce w/ different name, character, + use.

3. **Dual-use goods at EAR/ITAR boundary:** Component w/ both commercial + military applications. ITAR controls based on item; EAR controls based on item plus end use + end user. Commodity jurisdiction determination (CJ request) required when classification ambiguous. Filing under wrong regime = violation of both.

4. **Post-importation adjustments:** Transfer pricing adjustments between related parties after entry is liquidated. CBP requires reconciliation entries (CF 7501 w/ reconciliation flag) when final price not known at entry. Failure to reconcile → duty exposure on unpaid difference plus penalties.

5. **First sale valuation for related parties:** Using price paid by middleman (first sale) rather than price paid by importer (last sale) as customs value. CBP allows this under "first sale rule" (Nissho Iwai) but requires demonstrating first sale = bona fide arm's-length transaction. EU + most other jurisdictions do not recognise first sale — they value on last sale before importation.

6. **Retroactive FTA claims:** Discovering 18 months post-importation that goods qualified for preferential treatment. US allows post-importation claims via PSC (Post Summary Correction) within liquidation period. EU requires certificate of origin to have been valid at time of importation. Timing + documentation requirements differ by FTA + jurisdiction.

7. **Classification of kits vs components:** Retail kit containing items from different HS chapters (eg, camping kit w/ tent, stove, utensils). GRI 3(b) classifies by essential character — but if no single component gives essential character, GRI 3(c) applies (last heading in numerical order). Kits "put up for retail sale" have specific rules under GRI 3(b) that differ from industrial assortments.

8. **Temporary imports that become permanent:** Equipment imported under ATA Carnet or TIB that importer decides to keep. Carnet/bond must be discharged by paying full duty plus any penalties. If temporary import period has expired without export or duty payment, carnet guarantee is called → liability for guaranteeing chamber of commerce.

## Communication Patterns

### Tone Calibration

Match communication tone to counterparty, regulatory context, + risk level:

- **Customs broker (routine):** Collaborative + precise. Provide complete documentation, flag unusual items, confirm classification up front. "HS 8471.30 confirmed — our GRI 1 analysis + 2019 CBP ruling HQ H298456 support this classification. Packed 3 of 4 required docs, C/O follows by EOD."
- **Customs broker (urgent hold/exam):** Direct, factual, time-sensitive. "Shipment held at LA/LB — CBP requesting manufacturer documentation. Sending MID verification + production records now. Need your filing within 2 hrs to avoid demurrage."
- **Regulatory authority (ruling request):** Formal, thoroughly documented, legally precise. Follow agency's prescribed format exactly. Provide samples if requested. Never overstate certainty — use "it is our position that" rather than "this product is classified as."
- **Regulatory authority (penalty response):** Measured, cooperative, factual. Acknowledge error if it exists. Present mitigation factors systematically. Never admit fraud when facts support negligence.
- **Internal compliance advisory:** Clear business impact, specific action items, deadline. Translate regulatory requirements into operational language. "Effective March 1, all lithium battery imports require UN 38.3 test summaries at entry. Operations must collect these from suppliers before booking. Non-compliance: $10K+ per shipment in fines + cargo holds."
- **Supplier questionnaire:** Specific, structured, explain why you need info. Suppliers who understand duty savings from FTA are more cooperative w/ origin data.

### Key Templates

Brief templates below. Full versions w/ variables in [communication-templates.md](references/communication-templates.md).

**Customs broker instructions:** Subject: `Entry Instructions — {PO/shipment_ref} — {origin} to {destination}`. Include: classification w/ GRI rationale, declared value w/ Incoterms, FTA claim w/ supporting documentation reference, any PGA requirements (FDA prior notice, EPA TSCA certification, FCC declaration).

**Prior disclosure filing:** Addressed to CBP port director or Fines, Penalties + Forfeitures office w/ jurisdiction. Include: entry numbers, dates, specific violations, correct information, duty owed, + tender of unpaid amount.

**Internal compliance alert:** Subject: `COMPLIANCE ACTION REQUIRED: {topic} — Effective {date}`. Lead w/ business impact, then regulatory basis, then required action, then deadline + consequences of non-compliance.

## Escalation Protocols

### Automatic Escalation Triggers

| Trigger | Action | Timeline |
| ----------------------------------------------- | --------------------------------------------------------- | ----------------- |
| CBP detention or seizure | Notify VP + legal counsel | Within 1 hr |
| Restricted party screening true positive | Halt transaction, notify compliance officer + legal | Immediately |
| Potential penalty exposure > $50,000 | Notify VP Trade Compliance + General Counsel | Within 2 hrs |
| Customs examination w/ discrepancy found | Assign dedicated specialist, notify broker | Within 4 hrs |
| Denied party / SDN match confirmed | Full stop on all transactions w/ entity globally | Immediately |
| AD/CVD evasion investigation received | Retain outside trade counsel | Within 24 hrs |
| FTA origin audit from foreign customs authority | Notify all affected suppliers, begin documentation review | Within 48 hrs |
| Voluntary self-disclosure decision | Legal counsel approval required before filing | Before submission |

### Escalation Chain

Level 1 (Analyst) → Level 2 (Trade Compliance Manager, 4 hrs) → Level 3 (Director of Compliance, 24 hrs) → Level 4 (VP Trade Compliance, 48 hrs) → Level 5 (General Counsel / C-suite, immediate for seizures, SDN matches, or penalty exposure > $100K)

## Performance Indicators

Track monthly; trend quarterly:

| Metric | Target | Red Flag |
| -------------------------------------------- | ------------ | ------------------------------ |
| Classification accuracy (post-audit) | > 98% | < 95% |
| FTA utilisation rate (eligible shipments) | > 90% | < 70% |
| Entry rejection rate | < 2% | > 5% |
| Prior disclosure frequency | < 2 per yr | > 4 per yr |
| Screening false positive adjudication time | < 4 hrs | > 24 hrs |
| Duty savings captured (FTA + FTZ + drawback) | Track trend | Declining quarter-over-quarter |
| CBP examination rate | < 3% | > 7% |
| Penalty exposure (annual) | $0 | Any material penalty assessed |

## Additional Resources

- Detailed decision frameworks, classification logic, valuation methodology → [decision-frameworks.md](references/decision-frameworks.md)
- Comprehensive edge case library w/ full analysis → [edge-cases.md](references/edge-cases.md)
- Complete communication templates w/ variables + formatting guidance → [communication-templates.md](references/communication-templates.md)

## When to Use

Use when **planning, auditing, or remediating customs + trade compliance processes**:

- Classifying products (HS/HTS/TARIC), designing documentation flows, implementing Incoterms for new trade lanes.
- Evaluating or optimising duty exposure via FTAs, FTZs, drawback, valuation, or Incoterms changes.
- Investigating compliance risk, penalty exposure, or restricted-party screening issues across import/export operations.
