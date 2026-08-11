# BCUHB External Data Quality & Reporting Review — Translated Dr.Egeria Plan

> **Note:** This document translates the [original plan.md](plan.md) into Dr.Egeria commands using Campaigns, Projects, and hierarchical linkages.

---

## Create Campaign
### Qualified Name
BCUHB:Campaign:DataQualityReview:2026
### Display Name
BCUHB External Data Quality & Reporting Review
### Description
Delivery plan for the External Expert Review of Data Quality and Data Reporting (BCUHB Service Specification, June 2026).
### Mission
Triangulated evidence gathering across document review, data validation testing, interviews, process mapping, and comparative benchmarking to improve data quality and reporting confidence.
### Project Identifier
BCUHB-REVIEW-2026
### Project Status
APPROVED
### Planned Start Date
2026-08-03
### Planned Completion Date
2026-10-26
### Project Management Style
Waterfall (Phased delivery)
### Project Results Usage
Fortnightly written updates to Acting Director of Digital, Data and Technology; final report to Board.
### Success Criteria
- Initial Diagnostic Report (Week 6)
- Draft Final Report (Week 10)
- Final Report and Board Presentation (Week 12)

---

## Create Project
### Qualified Name
BCUHB:Project:Phase1:Mobilisation
### Display Name
Phase 1: Procurement end and mobilisation
### Description
Access provisioning (read-only) to source systems, warehouse and reporting outputs; confirm in-scope datasets; agree data-sharing/DPIA position; stand up the review's Egeria environment.
### Project Phase
Mobilisation
### Planned Start Date
2026-08-03
### Planned Completion Date
2026-08-14
### Success Criteria
Mobilisation note; confirmed scope and access plan; identification of focus information supply chains.

---

## Create Project
### Qualified Name
BCUHB:Project:Phase2:Fieldwork:Start
### Display Name
Phase 2: Review fieldwork (start)
### Description
Document review (policies, standards, prior audits); begin cataloguing source and warehouse assets; begin lineage capture; first round of interviews.
### Project Phase
Fieldwork
### Planned Start Date
2026-08-17
### Planned Completion Date
2026-08-28
### Success Criteria
Draft asset inventory; first lineage map; initial ownership map.

---

## Create Project
### Qualified Name
BCUHB:Project:Phase3:Fieldwork:Continued
### Display Name
Phase 3: Review fieldwork (continued)
### Description
Data validation testing; sample reconciliation; national-standards validation checks; process mapping of capture → processing → validation → reporting.
### Project Phase
Fieldwork
### Planned Start Date
2026-08-31
### Planned Completion Date
2026-09-11
### Success Criteria
Quantified data-quality findings (by dataset); process maps with failure points marked.

---

## Create Project
### Qualified Name
BCUHB:Project:Phase4:InitialFindings
### Display Name
Phase 4: Initial findings
### Description
Consolidate findings to date into risk-rated entries; draft the Initial Diagnostic Report — early findings, key risks, immediate actions.
### Project Phase
Reporting
### Planned Start Date
2026-09-07
### Planned Completion Date
2026-09-25
### Success Criteria
Deliverable: Initial Diagnostic Report (Spec 6.1).

---

## Create Project
### Qualified Name
BCUHB:Project:Phase5:GovernanceCulture
### Display Name
Phase 5: Governance & Culture Review
### Description
Interviews on culture, escalation, and workforce capability; comparative benchmarking against other NHS Wales organisations and maturity models.
### Project Phase
Fieldwork
### Planned Start Date
2026-09-14
### Planned Completion Date
2026-09-25
### Success Criteria
Culture/capability findings; benchmarking position.

---

## Create Project
### Qualified Name
BCUHB:Project:Phase6:DraftReport
### Display Name
Phase 6: Draft report
### Description
Root-cause analysis; full risk assessment; prioritised recommendations; strengths and good-practice identification; draft Final Report circulated.
### Project Phase
Reporting
### Planned Start Date
2026-09-28
### Planned Completion Date
2026-10-09
### Success Criteria
Draft Final Report.

---

## Create Project
### Qualified Name
BCUHB:Project:Phase7:FinalReport
### Display Name
Phase 7: Final report
### Description
Incorporate factual-accuracy feedback; finalise report; prepare and deliver formal presentation.
### Project Phase
Reporting
### Planned Start Date
2026-10-12
### Planned Completion Date
2026-10-23
### Success Criteria
Deliverable: Final Report (Spec 6.2) and Presentation to Executive Team / Board (Spec 6.3).

---

## Link Project Hierarchy
### Parent Project
BCUHB:Campaign:DataQualityReview:2026
### Child Project
BCUHB:Project:Phase1:Mobilisation

---

## Link Project Hierarchy
### Parent Project
BCUHB:Campaign:DataQualityReview:2026
### Child Project
BCUHB:Project:Phase2:Fieldwork:Start

---

## Link Project Hierarchy
### Parent Project
BCUHB:Campaign:DataQualityReview:2026
### Child Project
BCUHB:Project:Phase3:Fieldwork:Continued

---

## Link Project Hierarchy
### Parent Project
BCUHB:Campaign:DataQualityReview:2026
### Child Project
BCUHB:Project:Phase4:InitialFindings

---

## Link Project Hierarchy
### Parent Project
BCUHB:Campaign:DataQualityReview:2026
### Child Project
BCUHB:Project:Phase5:GovernanceCulture

---

## Link Project Hierarchy
### Parent Project
BCUHB:Campaign:DataQualityReview:2026
### Child Project
BCUHB:Project:Phase6:DraftReport

---

## Link Project Hierarchy
### Parent Project
BCUHB:Campaign:DataQualityReview:2026
### Child Project
BCUHB:Project:Phase7:FinalReport

---

## Link Project Dependency
### Dependent Project
BCUHB:Project:Phase2:Fieldwork:Start
### Depends on Project
BCUHB:Project:Phase1:Mobilisation

---

## Link Project Dependency
### Dependent Project
BCUHB:Project:Phase3:Fieldwork:Continued
### Depends on Project
BCUHB:Project:Phase2:Fieldwork:Start

---

## Link Project Dependency
### Dependent Project
BCUHB:Project:Phase4:InitialFindings
### Depends on Project
BCUHB:Project:Phase3:Fieldwork:Continued

---

## Link Project Dependency
### Dependent Project
BCUHB:Project:Phase6:DraftReport
### Depends on Project
BCUHB:Project:Phase4:InitialFindings

---

## Link Project Dependency
### Dependent Project
BCUHB:Project:Phase7:FinalReport
### Depends on Project
BCUHB:Project:Phase6:DraftReport
