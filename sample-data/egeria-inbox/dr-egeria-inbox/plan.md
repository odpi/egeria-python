# BCUHB External Data Quality & Reporting Review — Delivery Plan

> **Author:** Mandy Chessell (Lead Reviewer)
> **Version:** 0.2
> **Status:** DRAFT
> **Date:** 2026-08-03
> **Description:** Delivery plan for the *External Expert Review of Data Quality and Data Reporting* (BCUHB Service Specification, June 2026), built around the toolchain defined in [solution-blueprint.md](solution-blueprint.md). Structured against the specification's own methodology (Section 5), timescales (Section 7) and governance arrangements (Section 8).

---

## 1. Approach in brief

The specification's methodology (Section 5) — document review, data validation testing, interviews, process mapping, comparative benchmarking — is triangulated evidence gathering. The plan below runs those five strands in parallel from week 1, rather than sequentially, so that automated evidence (catalogue, lineage, quality scores) is available to sharpen the interviews rather than following them.

---

## 2. Budget and scope fit

£15–20k across 12 weeks is roughly 12–16 consultant days at a typical NHS-review blended day rate. A conventional, fully-manual review of this scope — cataloguing systems by hand, reconciling samples in spreadsheets, mapping data flows from interview notes — would not fit that budget; reviews of comparable breadth typically run several times this cost. This plan fits it, and the fit is the point worth making explicitly in the bid response rather than treating the budget as a constraint to apologise for.

**Why the toolchain makes this budget realistic.** Three of the six objective areas (3.1 Data Quality Assessment, 3.2 End-to-End Data Flow Review, 3.4 Systems and Infrastructure) are evidence-heavy but mechanically repetitive — profile every dataset, trace every flow, inventory every interface. That is exactly what the *Metadata Catalog*, *Lineage Capture Service* and *Data Quality Survey Engine* in the [solution blueprint](solution-blueprint.md) automate. Once source systems are catalogued (weeks 3–4), profiling and lineage-tracing run against the whole estate at once rather than one manually-audited dataset at a time, and every finding carries its evidence trail automatically (which asset, which flow, which rule) rather than needing to be reconstructed for the report. That is what converts a scope that would normally need 30–40+ days into one that fits 12–16.

**Where the budget still doesn't stretch.** Two areas resist compression because they are fundamentally about people, not systems:

- **3.5 Culture and Capability** — assessing openness, escalation behaviour and workforce confidence requires the Lead Reviewer's own judgement in conversation; it cannot be tool-accelerated. This plan scopes it to a fixed, purposively-sampled set of roughly 10–14 interviews (Board/Executive, data owners, analysts, clinical/operational staff, internal audit) rather than attempting broad coverage.
- **3.6 Benchmarking** — comparison against other NHS Wales organisations depends on what those organisations are willing to share, which is outside this review's control. The benchmarking output will be a structured maturity-model position (BCUHB's own scoring against a recognised framework such as DAMA DMBOK or a CMMI-aligned data management maturity model) with peer comparison included wherever equivalent published or shared data exists, rather than guaranteed as a like-for-like comparison.

**What this means for the bid response.** State the scope commitment plainly: full tool-driven depth on 3.1/3.2/3.4 across the entire in-scope estate (Spec 4.1), and a deliberately bounded, transparent interview sample for 3.3/3.5, sized to preserve budget for report quality and the Board presentation rather than spreading thin across every service. That is a stronger, more credible position than implying unlimited coverage at this price point.

---

## 3. Phased delivery against the Section 7 timeline

| Weeks | Spec stage | Activities | Egeria toolchain components used | Outputs |
|---|---|---|---|---|
| 1–2 | Procurement end and mobilisation | Access provisioning (read-only) to source systems, warehouse and reporting outputs; confirm in-scope datasets against Section 4.1; agree data-sharing/DPIA position with the Data Protection Officer; stand up the review's Egeria environment | *Metadata Catalog & Asset Inventory* (environment stood up, connectors configured) | Mobilisation note; confirmed scope and access plan; identification of focus information supply chains |
| 3–4 | Review fieldwork (start) | Document review (policies, standards, prior audits — Spec 5.1); begin cataloguing source and warehouse assets; begin lineage capture; first round of interviews (data owners, analysts) | *Metadata Catalog*, *Lineage Capture Service*, *Governance & Ownership Register* | Draft asset inventory; first lineage map; initial ownership map |
| 5–6 | Review fieldwork (continued) | Data validation testing — sample reconciliation of reported vs. source values (Spec 5.2); national-standards validation checks; process mapping of capture → processing → validation → reporting (Spec 5.4); interviews with Board/Executive and internal audit leads | *Data Quality Survey Engine*, *National Standards Validation Library*, *Lineage Capture Service* | Quantified data-quality findings (by dataset); process maps with failure points marked |
| 6–8 | Initial findings | Consolidate findings to date into risk-rated entries; draft the Initial Diagnostic Report — early findings, key risks, immediate actions | *Findings & Risk Register*, *Review Reporting Dashboard* | **Deliverable: Initial Diagnostic Report** (Spec 6.1, due within weeks 4–6 per spec; scheduled here at week 6 to allow one full fieldwork cycle of evidence — flag this at mobilisation if the client needs the earlier date held) |
| 7–8 | Review fieldwork (governance & culture strands) | Interviews on culture, escalation, and workforce capability (Spec 3.5); comparative benchmarking against other NHS Wales organisations and a recognised data quality maturity model (Spec 3.6, 5.5) | *Governance & Ownership Register*, *Review Reporting Dashboard* | Culture/capability findings; benchmarking position |
| 9–10 | Draft report | Root-cause analysis; full risk assessment (high/medium/low); prioritised recommendations; strengths and good-practice identification; draft Final Report circulated for factual accuracy check | *Findings & Risk Register*, *Review Reporting Dashboard* | **Draft Final Report** |
| 11–12 | Final report | Incorporate factual-accuracy feedback; finalise report; prepare and deliver formal presentation | — | **Deliverable: Final Report** (Spec 6.2) and **Presentation to Executive Team / Board** (Spec 6.3) |

---

## 4. Governance and reporting cadence (Spec Section 8)

- **Sponsor:** Chief Executive.
- **Oversight:** Audit Committee (initial), transitioning to monitoring via the Planning, Population Health and Partnerships Committee.
- **Operational reporting line:** Acting Director of Digital, Data and Technology — fortnightly written updates, drawn directly from the *Review Reporting Dashboard* so status is evidence-backed rather than a narrative summary.
- **Escalation:** any finding assessed as high risk (patient safety adjacency, statutory non-compliance, or evidence of data manipulation) is escalated to the Acting Director within 48 hours of identification, ahead of the next scheduled update — do not hold high-risk findings for the fortnightly cycle.

---

## 5. Team and resourcing

A small team is proposed, sized to the £15–20k budget:

- **Lead Reviewer** (governance, root-cause analysis, stakeholder interviews, report authorship, Board presentation) — the named expert providing NHS/healthcare data governance credibility (Spec Section 9).
- **Data/Tooling Analyst** (part-time) — configures the Egeria catalogue and connectors, runs lineage capture and quality surveys, maintains the dashboard.

Both roles can be one person for a review of this size, provided source-system access is granted early (weeks 1–2) — the biggest schedule risk is late access, not lack of capacity.

---

## 6. Indicative budget shape (within £15–20k)

| Item | Approx. share |
|---|---|
| Lead Reviewer time (interviews, analysis, report, presentation) | ~55% |
| Tooling/analyst time (catalogue, lineage, quality surveys, dashboard) | ~30% |
| Report production, Board materials, contingency | ~15% |

Day-rate and total-days assumptions should be confirmed once the provider is appointed; the split above is illustrative of where effort goes, not a quote.

---

## 7. Risks and mitigations (Spec Section 11, plus tooling-specific risks)

| Risk | Mitigation |
|---|---|
| Data availability and completeness | Cataloguing in weeks 3–4 surfaces access gaps early, while there's still schedule room to escalate |
| Staff engagement and openness | Lead Reviewer holds all culture/openness interviews personally, with a clear confidentiality commitment (Spec 13) |
| Reputational sensitivity | Findings routed through the *Findings & Risk Register* with root cause attached, so the Final Report distinguishes systemic issues from individual error — avoids findings reading as blame |
| Independence vs. collaboration | Toolchain access is read-only; the review does not modify source systems, the warehouse, or reporting outputs |
| Late or restricted system access | Access requirements confirmed in the mobilisation plan (weeks 1–2), escalated to the Acting Director immediately if not met |
| PII/confidentiality in catalogued metadata | Cataloguing captures structural and quality metadata (schemas, profiles, scores), not patient-level data extracts; any sample testing (Spec 5.2) uses the minimum data necessary and is handled per Spec Section 13. However, organised metadata linked to business context represents a valuable resource for cyber-attackers.  With Egeria it is possible to restrict access to named users, and to zone the metadata so that users only need to see the information relevant to their role. |
| Interview sample (3.5) too narrow to be representative | Sample composition agreed with the Acting Director at mobilisation; findings framed as indicative of culture rather than exhaustive, consistent with the bounded scope set out in Section 2 |

---

## 8. Ethics and confidentiality (Spec Section 13)

- Full compliance with GDPR and NHS confidentiality standards throughout.
- No patient-identifiable data leaves BCUHB's environment; the Egeria toolchain runs within BCUHB's infrastructure or a controlled environment agreed at mobilisation. User security and optional governance zones are enabled to protect the information gathered during the review.
- Findings are anonymised at the individual level in the Final Report — issues are attributed to processes and systems, not named individuals, consistent with the review's stated aim of restoring confidence rather than assigning blame.

---

## 9. Open items to confirm at mobilisation

1. Exact list of in-scope national/statutory returns (Spec 4.1) and their source systems.
2. Whether the Initial Diagnostic Report is required strictly within weeks 4–6, or whether week 6 (after one full fieldwork cycle) is acceptable — the spec's own table shows "Initial findings" spanning weeks 6–8, which is the interpretation this plan follows.
3. Environment for the Egeria toolchain — BCUHB-hosted vs. reviewer-hosted — and the associated data-sharing agreement.
4. Named data owners/stewards to prioritise for early interviews (weeks 3–4), to unblock the *Governance & Ownership Register*.
5. Acceptable composition of the 3.5 interview sample (Section 2) and any services that must be represented.
