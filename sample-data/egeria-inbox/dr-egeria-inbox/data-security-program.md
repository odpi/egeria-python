# Coco Pharmaceuticals Data Security Program

> **Author:** Ivor Padlock (Chief Information Security Officer), Sidney Seeker (Security Consultant), Simon Burr (Cyber-Security Specialist)  
> **Version:** 1.0  
> **Status:** ACTIVE  
> **Date:** 2026-07-18  
> **Description:** This document builds out the security governance domain of the [Data Governance Program](data-governance-program.md) around the ISO/IEC 27001:2022 information security management system (ISMS) standard, defining the policies and controls Coco Pharmaceuticals uses to operate and certify its ISMS.

---

## Overview

The [Data Governance Program](data-governance-program.md) already establishes the foundations of the security domain: the Cyber Resilience business imperative, the Cyber-Attack on Operations or Data threat, the Martyn's Law regulation, and the obligation that all users must be authenticated and accountable. The [Risk Register](risk-register.md) then rates the concrete risks that follow from those drivers — Ransomware Disruption to Manufacturing and Theft of Personalised Treatment Intellectual Property foremost among them.

This document adds the policies and controls needed to close the gap between those drivers and day-to-day security practice, structured around ISO/IEC 27001:2022 — the international standard Coco Pharmaceuticals is adopting as the operating framework for its information security management system (ISMS). It does not redefine the drivers already captured in the Data Governance Program; instead, every new policy and control is linked back to the existing drivers, obligation, and risks so that the CISO's Governance Folio remains a single, complete view of the security governance program.

The document is organised as follows:

1. **Governance Policies** — the principle, approach, and obligations that define how Coco Pharmaceuticals operates its ISMS.
2. **Governance Controls** — the ISO/IEC 27001:2022 certification and the metrics used to measure and evidence compliance.
3. **Governance Links** — connecting the new policies and controls to the drivers, obligations, and risks already defined in the Data Governance Program and Risk Register.
4. **Folio Membership** — adding every new definition to the Chief Information Security Officer's Governance Folio.

---

## Part 1: Governance Policies

### 1.1 Governance Principles

___

## Create Governance Principle

### Display Name
Risk-Based Information Security Management

### Qualified Name
CocoPharma::GovernancePrinciple::RiskBasedInformationSecurityManagement

### Domain Identifier
SECURITY

### Summary
Security controls are selected and prioritised according to a formal, documented assessment of information security risk, not applied uniformly regardless of risk.

### Description
Following ISO/IEC 27001:2022's risk assessment and risk treatment requirements, Coco Pharmaceuticals will identify information security risks to its assets, assess their likelihood and impact, and select controls proportionate to the risk — recording the justification for each choice in a Statement of Applicability. This mirrors the approach already used in the [Risk Register](risk-register.md), which rates risks such as Ransomware Disruption to Manufacturing and Theft of Personalised Treatment Intellectual Property by likelihood and impact. Applying the same discipline inside the ISMS ensures security investment is directed where it matters most.

### Implications
- A documented risk assessment methodology must be defined and applied consistently across the ISMS scope
- Identified risks must be recorded, assigned an owner, and tracked through to treatment
- Every control in the Statement of Applicability must be traceable to an assessed risk

### Outcomes
- Security investment is directed at the highest-risk areas first
- Controls are proportionate — avoiding both under-protection and wasteful over-protection
- Risk decisions are documented and defensible to regulators and certification auditors

### Domain Identifier
SECURITY

### Authors
- Ivor Padlock
- Sidney Seeker
- Simon Burr

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

### 1.2 Governance Obligations

___

## Create Governance Obligation

### Display Name
Information Assets Must Be Inventoried and Classified for the ISMS

### Qualified Name
CocoPharma::GovernanceObligation::InformationAssetsInventoriedAndClassifiedForISMS

### Domain Identifier
SECURITY

### Summary
Every information asset within the ISMS scope must appear in an asset inventory and be classified according to its confidentiality, integrity, and availability requirements.

### Description
ISO/IEC 27001:2022 Annex A control area 5 requires organisations to maintain an inventory of information and other associated assets, and to classify information according to its protection needs. This obligation applies that requirement across all information assets in scope of Coco Pharmaceuticals' ISMS — research systems, manufacturing control systems, and corporate IT — not only the personal data already covered by the [Personal Data Must Be Classified and Handled According to Sensitivity](data-governance-program.md) obligation. The two classification schemes must remain consistent so that assets holding both personal and non-personal sensitive information are protected coherently.

### Implications
- An asset register must be maintained, covering systems, data collections, and the intellectual property they contain
- A classification scheme covering confidentiality, integrity, and availability must be defined and applied to every registered asset
- Asset entries and classifications must be reviewed at defined intervals and whenever an asset's use changes materially

### Outcomes
- Complete visibility of every asset in ISMS scope, supporting the Statement of Applicability
- Assets are protected proportionally to their classification, not uniformly
- Auditors can trace any control back to the asset and classification that justify it

### Domain Identifier
SECURITY

### Authors
- Ivor Padlock
- Sidney Seeker
- Simon Burr

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Governance Obligation

### Display Name
Third-Party and Supplier Access Must Be Risk-Assessed

### Qualified Name
CocoPharma::GovernanceObligation::SupplierSecurityRiskAssessment

### Domain Identifier
SECURITY

### Summary
Suppliers, cloud providers, and research or hospital partners who can access Coco Pharmaceuticals' systems or data must be security-assessed before onboarding and periodically thereafter.

### Description
ISO/IEC 27001:2022 Annex A control area 5 requires organisations to manage information security risk in supplier relationships — from initial assessment through contractual security requirements to ongoing monitoring and offboarding. The [Cyber-Attack on Operations or Data](data-governance-program.md) threat already identifies that "data shared with external partners must be governed by agreements and monitored"; this obligation makes that requirement concrete and auditable.

### Implications
- Security requirements must be included in contracts with suppliers, cloud providers, and data-sharing partners
- Third parties must undergo a security assessment before being granted access, and be reassessed periodically
- Access granted to a third party must be revoked promptly when a contract or engagement ends

### Outcomes
- Reduced risk of compromise entering through the supply chain or a partner organisation
- Evidence of supplier due diligence is available for certification and regulatory audits
- Third-party access is time-bound to the life of the relationship it supports

### Domain Identifier
SECURITY

### Authors
- Ivor Padlock
- Sidney Seeker
- Simon Burr

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Governance Obligation

### Display Name
Security Incidents Must Be Logged, Reported, and Reviewed

### Qualified Name
CocoPharma::GovernanceObligation::SecurityIncidentsLoggedReportedReviewed

### Domain Identifier
SECURITY

### Summary
Every suspected information security incident must be reported through a defined channel, logged, investigated, and reviewed for lessons learned.

### Description
ISO/IEC 27001:2022 Annex A control area 5 requires a consistent, effective approach to managing information security incidents — planning, assessment, response, evidence collection, and learning from incidents. This obligation puts that lifecycle in place, directly implementing the incident response commitment already identified under the [Cyber-Attack on Operations or Data](data-governance-program.md) threat: "incident response procedures must exist and be tested regularly." It is the control that would have governed Coco Pharmaceuticals' response had either of the [Ransomware Disruption to Manufacturing](risk-register.md) or [Theft of Personalised Treatment Intellectual Property](risk-register.md) risks materialised.

### Implications
- A single reporting channel for suspected security incidents must exist and be known to all staff
- All reported incidents must be logged, triaged, and investigated within defined timeframes
- Lessons learned from incidents must feed back into the ISMS as corrective actions

### Outcomes
- Faster containment and recovery when incidents occur
- A documented evidence trail for regulators and certification auditors
- Continuous improvement of controls based on real incident experience

### Domain Identifier
SECURITY

### Authors
- Ivor Padlock
- Sidney Seeker
- Simon Burr

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Governance Obligation

### Display Name
Staff Must Complete Annual Security Awareness Training

### Qualified Name
CocoPharma::GovernanceObligation::AnnualSecurityAwarenessTraining

### Domain Identifier
SECURITY

### Summary
All staff and contractors must complete security awareness training at induction and at least annually thereafter, with additional role-specific training for high-risk roles.

### Description
ISO/IEC 27001:2022 Annex A control area 6 requires personnel to receive appropriate information security awareness, education, and training. Most successful cyber-attacks begin with human error — a phishing email opened, a credential shared — so this obligation is one of the most direct mitigations of the [Cyber-Attack on Operations or Data](data-governance-program.md) threat. Staff with access to personalised treatment research or patient data receive additional, role-specific training reflecting the sensitivity of what they handle.

### Implications
- Security awareness training must be part of new-starter induction for staff and contractors
- All staff must complete refresher training at least annually
- Staff in roles with access to sensitive research or patient data must complete additional, role-specific training

### Outcomes
- Reduced likelihood of incidents caused by human error, such as phishing
- Demonstrable, trackable compliance evidence for certification audits
- A workforce that recognises and reports suspicious activity promptly

### Domain Identifier
SECURITY

### Authors
- Ivor Padlock
- Sidney Seeker
- Simon Burr

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

### 1.3 Governance Approaches

___

## Create Governance Approach

### Display Name
ISMS Plan-Do-Check-Act Continuous Improvement Cycle

### Qualified Name
CocoPharma::GovernanceApproach::ISMSPlanDoCheckActCycle

### Domain Identifier
SECURITY

### Summary
Coco Pharmaceuticals' information security management system is operated as a continuous Plan-Do-Check-Act cycle, in line with ISO/IEC 27001:2022, rather than a one-off compliance exercise.

### Description
ISO/IEC 27001:2022 requires the ISMS to be planned, implemented, monitored, and improved on an ongoing basis. Coco Pharmaceuticals adopts this as its operating approach for the security domain: risks and controls are planned and implemented, their operation is checked through internal audit and management review, and corrective actions are acted upon before the cycle repeats. This gives the CISO a repeatable rhythm for demonstrating compliance at the annual surveillance audits that maintain ISO/IEC 27001:2022 certification.

### Implications
- The ISMS must undergo internal audit at least annually, covering all Annex A controls declared applicable
- Management review meetings, chaired by the CISO, must be held at planned intervals to assess ISMS performance
- Corrective actions arising from audits, incidents, or management review must be tracked to closure

### Outcomes
- The ISMS improves continuously rather than degrading between audits
- Certification is sustained through a repeatable, evidenced cycle rather than last-minute preparation
- Management maintains ongoing visibility of the security program's effectiveness

### Domain Identifier
SECURITY

### Authors
- Ivor Padlock
- Sidney Seeker
- Simon Burr

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

## Part 2: Governance Controls

### 2.1 Certification

___

## Create Certification Type

### Display Name
ISO/IEC 27001:2022 — Information Security Management System Certification

### Qualified Name
CocoPharma::CertificationType::ISO27001

### Domain Identifier
SECURITY

### Summary
The international standard for establishing, implementing, maintaining, and continually improving an information security management system (ISMS), used as the certifiable framework for Coco Pharmaceuticals' security governance program.

### Description
ISO/IEC 27001:2022 sets out requirements for an ISMS and, in Annex A, a reference set of controls covering organisational, people, physical, and technological aspects of information security. Coco Pharmaceuticals is pursuing certification against this standard to give patients, hospital partners, and regulators independent assurance that the intellectual property behind its personalised treatments and the patient data it holds are protected to a recognised international standard. Certification is issued and periodically re-audited by an accredited certification body.

### Scope
Coco Pharmaceuticals' information security management system, covering research systems holding personalised treatment intellectual property, manufacturing control systems, corporate IT, and data shared with hospital and research partners.

### Implications
- A Statement of Applicability must be maintained, recording which Annex A controls are applicable and how they are implemented
- The ISMS must pass an initial certification audit and subsequent annual surveillance audits by an accredited certification body
- Any significant change to ISMS scope or risk must be reflected in the Statement of Applicability before the next audit

### Importance
Critical

### Category
Security & Resilience

### Authors
- Ivor Padlock
- Sidney Seeker
- Simon Burr

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

### 2.2 Governance Metrics

___

## Create Governance Metric

### Display Name
ISO 27001 Annex A Control Implementation Rate

### Qualified Name
CocoPharma::GovernanceMetric::ISO27001ControlImplementationRate

### Domain Identifier
SECURITY

### Summary
Measures the percentage of Annex A controls marked applicable in the Statement of Applicability that are fully implemented and evidenced.

### Description
This metric is calculated as (number of applicable Annex A controls fully implemented and evidenced / total number of applicable Annex A controls) × 100. The target is 100% ahead of any certification or surveillance audit. A control that is applicable but not yet implemented represents an open gap in the ISMS and a risk to certification.

### Implications
- Requires a current, accurate Statement of Applicability
- Requires evidence of implementation to be collected and kept current for every applicable control

### Outcomes
- Gives the CISO and management an at-a-glance view of ISMS readiness for audit
- Identifies specific control gaps that need remediation before certification or surveillance audits

### Domain Identifier
SECURITY

### Authors
- Ivor Padlock
- Sidney Seeker
- Simon Burr

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Governance Metric

### Display Name
Security Incident Mean Time to Containment

### Qualified Name
CocoPharma::GovernanceMetric::SecurityIncidentMeanTimeToContainment

### Domain Identifier
SECURITY

### Summary
Measures the average time between a security incident being reported and it being contained.

### Description
This metric is calculated across all logged security incidents in a reporting period, as the mean elapsed time from initial report to confirmed containment. A sustained downward trend indicates an effective incident response capability; a rising trend signals that response procedures, tooling, or staffing need attention. This is the primary outcome measure for the obligation that security incidents must be logged, reported, and reviewed.

### Implications
- Requires consistent, timestamped logging of every reported incident from report through to containment
- Requires a clear, shared definition of "contained" so measurements are comparable across incidents

### Outcomes
- Tracks whether incident response is improving over time
- Surfaces slow or failed responses for root-cause analysis and process improvement

### Domain Identifier
SECURITY

### Authors
- Ivor Padlock
- Sidney Seeker
- Simon Burr

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Governance Metric

### Display Name
Security Awareness Training Completion Rate

### Qualified Name
CocoPharma::GovernanceMetric::SecurityAwarenessTrainingCompletionRate

### Domain Identifier
SECURITY

### Summary
Measures the percentage of staff and contractors who have completed required security awareness training within its due period.

### Description
This metric is calculated as (number of staff and contractors with current, completed training / total number required to complete it) × 100, tracked separately for general induction/annual training and for role-specific training required of staff with access to sensitive research or patient data. The target is 100%. This is the primary compliance measure for the annual security awareness training obligation.

### Implications
- Requires training completion to be tracked centrally against a current list of staff and contractors in scope
- Requires role-specific training requirements to be identified and tracked separately from general training

### Outcomes
- Demonstrates compliance with the training obligation to certification auditors
- Identifies individuals or teams falling behind on required training before it becomes an audit finding

### Domain Identifier
SECURITY

### Authors
- Ivor Padlock
- Sidney Seeker
- Simon Burr

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

## Part 3: Governance Links

This section links the policies and controls defined above to the drivers, obligations, and risks already defined in the [Data Governance Program](data-governance-program.md) and the [Risk Register](risk-register.md).

---

### 3.1 Governance Responses — Existing Drivers linked to New Policies

___

## Link Governance Response

### Driver
CocoPharma::BusinessImperative::CyberResilience

### Policy
CocoPharma::GovernancePrinciple::RiskBasedInformationSecurityManagement

### Rationale
Cyber resilience is best achieved by directing finite security effort at the highest-risk areas first. Risk-based information security management is how the ISMS translates the imperative into prioritised action.

___

---

___

## Link Governance Response

### Driver
CocoPharma::BusinessImperative::CyberResilience

### Policy
CocoPharma::GovernanceApproach::ISMSPlanDoCheckActCycle

### Rationale
Cyber resilience is not a one-off state but an ongoing capability. The Plan-Do-Check-Act cycle is how Coco Pharmaceuticals sustains and improves that capability over time.

___

---

___

## Link Governance Response

### Driver
CocoPharma::Threat::CyberAttackOnOperationsOrData

### Policy
CocoPharma::GovernanceObligation::InformationAssetsInventoriedAndClassifiedForISMS

### Rationale
The threat's own implications require that access to sensitive systems be tightly controlled; controlling access to an asset first requires knowing that the asset exists and how sensitive it is.

___

---

___

## Link Governance Response

### Driver
CocoPharma::Threat::CyberAttackOnOperationsOrData

### Policy
CocoPharma::GovernanceObligation::SupplierSecurityRiskAssessment

### Rationale
This obligation directly implements the threat's implication that "data shared with external partners must be governed by agreements and monitored."

___

---

___

## Link Governance Response

### Driver
CocoPharma::Threat::CyberAttackOnOperationsOrData

### Policy
CocoPharma::GovernanceObligation::SecurityIncidentsLoggedReportedReviewed

### Rationale
This obligation directly implements the threat's implication that "incident response procedures must exist and be tested regularly."

___

---

___

## Link Governance Response

### Driver
CocoPharma::Threat::CyberAttackOnOperationsOrData

### Policy
CocoPharma::GovernanceObligation::AnnualSecurityAwarenessTraining

### Rationale
Most cyber-attacks begin with human error. Staff awareness training is a direct mitigation of the threat, complementing the technical and access controls covering the same risk.

___

---

### 3.2 Governance Mechanisms — New Policies linked to New Controls

___

## Link Governance Mechanism

### Policy
CocoPharma::GovernanceApproach::ISMSPlanDoCheckActCycle

### Mechanism
CocoPharma::CertificationType::ISO27001

### Rationale
ISO/IEC 27001:2022 certification is the external validation that the Plan-Do-Check-Act cycle is being operated effectively. The certification audit cycle and the ISMS improvement cycle are the same rhythm viewed from outside and inside the organisation.

___

---

___

## Link Governance Mechanism

### Policy
CocoPharma::GovernanceApproach::ISMSPlanDoCheckActCycle

### Mechanism
CocoPharma::GovernanceMetric::ISO27001ControlImplementationRate

### Rationale
This metric is the primary indicator used at each management review to check ISMS status before deciding what to act on next.

___

---

___

## Link Governance Mechanism

### Policy
CocoPharma::GovernancePrinciple::RiskBasedInformationSecurityManagement

### Mechanism
CocoPharma::GovernanceMetric::ISO27001ControlImplementationRate

### Rationale
The implementation rate shows whether the controls selected as a result of risk assessment have actually been put in place — the practical follow-through on risk-based decisions.

___

---

___

## Link Governance Mechanism

### Policy
CocoPharma::GovernanceObligation::SecurityIncidentsLoggedReportedReviewed

### Mechanism
CocoPharma::GovernanceMetric::SecurityIncidentMeanTimeToContainment

### Rationale
This metric directly measures how well the incident logging, reporting, and review obligation is being met in practice.

___

---

___

## Link Governance Mechanism

### Policy
CocoPharma::GovernanceObligation::AnnualSecurityAwarenessTraining

### Mechanism
CocoPharma::GovernanceMetric::SecurityAwarenessTrainingCompletionRate

### Rationale
This metric directly measures compliance with the training obligation, including the additional role-specific training requirement.

___

---

### 3.3 Peer Policy Links — New Policies linked to Existing and New Policies

___

## Link Governance Policies

### Governance Policy 1
CocoPharma::GovernancePrinciple::RiskBasedInformationSecurityManagement

### Governance Policy 2
CocoPharma::GovernanceApproach::ISMSPlanDoCheckActCycle

### Description
The principle sets the criterion for prioritising security work; the approach is the operating cycle through which that prioritisation is planned, executed, checked, and improved.

___

---

___

## Link Governance Policies

### Governance Policy 1
CocoPharma::GovernanceApproach::ISMSPlanDoCheckActCycle

### Governance Policy 2
CocoPharma::GovernanceObligation::AllUsersMustBeAuthenticatedAndAccountable

### Description
Unique user authentication and access logging is one of the existing controls whose operation the ISMS Plan-Do-Check-Act cycle audits and improves over time.

___

---

___

## Link Governance Policies

### Governance Policy 1
CocoPharma::GovernanceObligation::InformationAssetsInventoriedAndClassifiedForISMS

### Governance Policy 2
CocoPharma::GovernanceObligation::PersonalDataClassifiedBySensitivity

### Description
Both obligations require classification by sensitivity, one covering all information assets in ISMS scope and the other specifically personal data. The two classification schemes must stay consistent for assets that hold both.

___

---

___

## Link Governance Policies

### Governance Policy 1
CocoPharma::GovernanceObligation::SecurityIncidentsLoggedReportedReviewed

### Governance Policy 2
CocoPharma::GovernanceObligation::DataQualityIssuesMustBeReportedAndResolved

### Description
Both obligations establish the same detect-report-resolve-within-timeframe pattern, one for security incidents and one for data quality issues, reinforcing a consistent approach to issue management across governance domains.

___

---

## Part 4: Folio Membership

The [Data Governance Program](data-governance-program.md) defines a Chief Information Security Officer Governance Folio collecting the definitions Ivor Padlock is accountable for. Every governance definition created in this document is added as a member of that folio, so it remains a complete view of the CISO's governance work.

---

### 4.1 Chief Information Security Officer Folio Members

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefInformationSecurityOfficer

### Element Id
CocoPharma::GovernancePrinciple::RiskBasedInformationSecurityManagement

### Membership Rationale
The CISO owns the risk-based approach that determines how security controls are prioritised across the ISMS.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefInformationSecurityOfficer

### Element Id
CocoPharma::GovernanceObligation::InformationAssetsInventoriedAndClassifiedForISMS

### Membership Rationale
The CISO is accountable for the asset inventory and classification scheme underpinning the ISMS.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefInformationSecurityOfficer

### Element Id
CocoPharma::GovernanceObligation::SupplierSecurityRiskAssessment

### Membership Rationale
The CISO owns the security assessment of suppliers and partners, a control area of the ISMS.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefInformationSecurityOfficer

### Element Id
CocoPharma::GovernanceObligation::SecurityIncidentsLoggedReportedReviewed

### Membership Rationale
The CISO leads incident response and is accountable for this obligation.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefInformationSecurityOfficer

### Element Id
CocoPharma::GovernanceObligation::AnnualSecurityAwarenessTraining

### Membership Rationale
The CISO is accountable for the security awareness training programme.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefInformationSecurityOfficer

### Element Id
CocoPharma::GovernanceApproach::ISMSPlanDoCheckActCycle

### Membership Rationale
The CISO owns the ISMS operating cycle that this approach defines.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefInformationSecurityOfficer

### Element Id
CocoPharma::CertificationType::ISO27001

### Membership Rationale
The CISO is accountable for achieving and maintaining ISO/IEC 27001:2022 certification.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefInformationSecurityOfficer

### Element Id
CocoPharma::GovernanceMetric::ISO27001ControlImplementationRate

### Membership Rationale
The CISO uses this metric to track ISMS readiness for certification and surveillance audits.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefInformationSecurityOfficer

### Element Id
CocoPharma::GovernanceMetric::SecurityIncidentMeanTimeToContainment

### Membership Rationale
The CISO uses this metric to monitor the effectiveness of incident response.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefInformationSecurityOfficer

### Element Id
CocoPharma::GovernanceMetric::SecurityAwarenessTrainingCompletionRate

### Membership Rationale
The CISO uses this metric to track compliance with the security awareness training obligation.

### Membership Status
VALIDATED

___
