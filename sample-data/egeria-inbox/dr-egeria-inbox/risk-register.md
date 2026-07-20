# Coco Pharmaceuticals Risk Register

> **Author:** Jules Keeper (Chief Data Officer), Ivor Padlock (Chief Information Security Officer), Faith Broker (Chief Privacy Officer), Reggie Mint (Chief Financial Officer), Tessa Tube (Drug Development Lead)  
> **Version:** 1.0  
> **Status:** ACTIVE  
> **Date:** 2026-07-08  
> **Description:** This document defines the risk register for Coco Pharmaceuticals. Each risk records the likelihood and impact of a governance threat actually occurring, and is linked back to the threat it realises. Risks that arise from a regulatory obligation without an existing threat definition are matched to a newly defined threat.

---

## Overview

The [Data Governance Program](data-governance-program.md) defines the governance drivers, policies, and controls for Coco Pharmaceuticals. Threats are one category of governance driver — they describe things that could go wrong. The risk register takes each threat and works out the concrete, assessable risks it gives rise to, rating each one's likelihood and impact.

The register is organised as follows:

1. **Risk Register Structure** — a root collection holding one collection folder per risk category.
2. **New Threat Definitions** — threats needed to cover risks arising from regulatory obligations (clinical trials, manufacturing, event security) that were not already captured as threats in the data governance program.
3. **Risks** — one `Create Risk` entry per identified risk, grouped by category.
4. **Collection Membership** — links folders into the root collection, and risks into their category folder.
5. **Risk-to-Threat Links** — a `Link Governance Response` for every risk, recording which threat it is a response to (the risk is the *Policy* end of the relationship, the threat is the *Driver* end).

---

## Part 1: Risk Register Structure

### 1.1 Root Collection

___

## Create Root Collection

### Display Name
Coco Pharmaceuticals Risk Register

### Qualified Name
CocoPharma::Collection::RiskRegister

### Purpose
Holds the complete risk register for Coco Pharmaceuticals, organising risks into category folders and linking each risk to the governance threat it is a response to.

### Description
The master collection for all identified risks at Coco Pharmaceuticals. Each risk within this hierarchy assesses the likelihood and impact of a specific threat, and is linked to that threat via a Governance Response relationship.

### Category
Governance Program

### Authors
Jules Keeper

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

### 1.2 Risk Categories

___

## Create Collection Folder

### Display Name
Cyber Security Risks

### Qualified Name
CocoPharma::CollectionFolder::CyberSecurityRisks

### Purpose
Groups risks arising from cyber-attacks on Coco Pharmaceuticals' systems, data, and intellectual property.

### Description
Risks in this folder relate to the Cyber-Attack on Operations or Data threat and cover both operational disruption and loss of valuable intellectual property.

### Category
Risk Category

### Authors
Ivor Padlock

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Collection Folder

### Display Name
Privacy and Data Protection Risks

### Qualified Name
CocoPharma::CollectionFolder::PrivacyRisks

### Purpose
Groups risks arising from unauthorised disclosure or misuse of personal and patient data.

### Description
Risks in this folder relate to the Unauthorised Data Disclosure threat, covering both accidental exposure and deliberate insider misuse of sensitive data.

### Category
Risk Category

### Authors
Faith Broker

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Collection Folder

### Display Name
Supply Chain and Corporate Risks

### Qualified Name
CocoPharma::CollectionFolder::SupplyChainRisks

### Purpose
Groups risks arising from fraudulent or compromised suppliers entering Coco Pharmaceuticals' procurement and manufacturing supply chain.

### Description
Risks in this folder relate to the Fraudulent Supplier Activity threat, covering both financial fraud and the risk of counterfeit or substandard materials reaching manufacturing.

### Category
Risk Category

### Authors
Reggie Mint

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Collection Folder

### Display Name
Regulatory and Clinical Compliance Risks

### Qualified Name
CocoPharma::CollectionFolder::RegulatoryComplianceRisks

### Purpose
Groups risks arising from failure to meet clinical trial and manufacturing regulatory obligations.

### Description
Risks in this folder relate to newly defined threats covering FDA clinical trial data integrity and Good Manufacturing Practice compliance — areas governed by regulation but not previously captured as threats.

### Category
Risk Category

### Authors
Tessa Tube

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Collection Folder

### Display Name
Organisational and Knowledge Risks

### Qualified Name
CocoPharma::CollectionFolder::OrganisationalRisks

### Purpose
Groups risks arising from undocumented, informally held organisational knowledge.

### Description
Risks in this folder relate to the Loss of Key Talent and Knowledge threat, covering both loss of governance knowledge on staff departure and inconsistent data definitions that undermine cross-department reporting.

### Category
Risk Category

### Authors
Jules Keeper

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Collection Folder

### Display Name
Physical Security and Event Risks

### Qualified Name
CocoPharma::CollectionFolder::PhysicalSecurityRisks

### Purpose
Groups risks arising from physical security threats at Coco Pharmaceuticals' public events.

### Description
Risks in this folder relate to a newly defined threat covering terrorism at public events — the driver behind Martyn's Law (the Terrorism (Protection of Premises) Act 2025).

### Category
Risk Category

### Authors
Ivor Padlock

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

## Part 2: New Threat Definitions

The [Data Governance Program](data-governance-program.md) already defines four threats: Cyber-Attack on Operations or Data, Unauthorised Data Disclosure, Fraudulent Supplier Activity, and Loss of Key Talent and Knowledge. Most risks below are responses to those. Three risks, however, arise from regulatory obligations (FDA clinical trial regulations, Good Manufacturing Practice, and Martyn's Law) that were captured as *Regulations* but not as *Threats*. The following threats fill that gap so each risk can be linked to a driver of type Threat.

___

## Create Threat

### Display Name
Clinical Trial Data Integrity Failure

### Qualified Name
CocoPharma::Threat::ClinicalTrialDataIntegrityFailure

### Domain Identifier
DATA

### Summary
Clinical trial data may be falsified, lost, or otherwise fail to meet the integrity standards required by FDA regulations.

### Description
Clinical trial data underpins every drug approval decision Coco Pharmaceuticals seeks from the FDA. Loss of integrity — whether through system failure, human error, or deliberate falsification — threatens patient safety, drug approvals, and exposes the organisation to regulatory action and criminal liability under 21 CFR Part 11. The risk grows as trial data is captured and shared across more systems and partners.

### Implications
- Electronic clinical trial records must have a complete, tamper-evident audit trail
- Systems holding trial data must have validated access controls
- Data integrity failures must be detected, investigated, and reported

### Importance
Critical

### Category
Drug Development and Clinical Trials

### Authors
Tessa Tube

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Threat

### Display Name
Manufacturing Quality Deviation

### Qualified Name
CocoPharma::Threat::ManufacturingQualityDeviation

### Domain Identifier
DATA

### Summary
Manufacturing data may fail to demonstrate that products were consistently produced and controlled to the standard required by Good Manufacturing Practice.

### Description
Good Manufacturing Practice requires complete, traceable records of every stage of pharmaceutical manufacturing. An undetected or undocumented deviation — an out-of-tolerance reading, a missing batch record, an untraceable raw material — can result in unsafe product reaching patients, and regulatory sanctions against Coco Pharmaceuticals. The risk is heightened by the move towards personalised, on-demand manufacturing, which multiplies the number of distinct production runs requiring their own complete record.

### Implications
- Batch records must be complete, accurate, and traceable to raw material sourcing
- Deviations from process must be documented and investigated before product release
- Quality control data must be retained for the periods required by regulation

### Importance
Critical

### Category
Pharmaceutical Manufacturing

### Authors
Tessa Tube

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Threat

### Display Name
Terrorism at Public Events

### Qualified Name
CocoPharma::Threat::TerrorismAtPublicEvents

### Domain Identifier
SECURITY

### Summary
Coco Pharmaceuticals' public events, including its annual conference, could be the target of, or affected by, a terrorist attack.

### Description
Coco Pharmaceuticals hosts an annual conference in London attracting around 700 attendees. Any venue hosting the public is a potential target for, or could be caught up in, an act of terrorism. This is the threat that the UK Terrorism (Protection of Premises) Act 2025 (Martyn's Law) is designed to reduce the impact of. Failure to prepare for this threat exposes attendees to physical harm and Coco Pharmaceuticals to legal and reputational consequences.

### Implications
- Public protection procedures (evacuation, invacuation, lockdown, communication) must be documented and rehearsed
- A Responsible Person must be designated for events in scope of Martyn's Law
- Security assessments must be kept current as attendance and venues change

### Importance
Medium-High

### Category
Event Security

### Authors
Ivor Padlock

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

## Part 3: Risks

### 3.1 Cyber Security Risks

___

## Create Risk

### Display Name
Ransomware Disruption to Manufacturing Operations

### Qualified Name
CocoPharma::Risk::RansomwareDisruptionToManufacturing

### Domain Identifier
SECURITY

### Summary
Ransomware could encrypt manufacturing control or scheduling systems, halting drug production.

### Description
**Likelihood:** Medium — ransomware attacks against pharmaceutical and healthcare manufacturers have risen sharply industry-wide, and Coco Pharmaceuticals' expanding digital footprint (real-time links between research, manufacturing, and hospital partners) increases the number of possible entry points. **Impact:** Critical — a successful attack on manufacturing systems could halt production of both batch and on-demand personalised treatments, directly affecting patient care and causing significant financial and reputational damage. **Overall rating:** Critical.

### Implications
- Manufacturing systems must be segmented from general corporate networks
- Offline, tested backups must exist for all systems critical to production
- An incident response plan must specifically cover manufacturing downtime scenarios

### Importance
Critical

### Category
Cyber Security

### Authors
Ivor Padlock

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Risk

### Display Name
Theft of Personalised Treatment Intellectual Property

### Qualified Name
CocoPharma::Risk::TheftOfPersonalisedTreatmentIP

### Domain Identifier
SECURITY

### Summary
Research systems holding novel personalised treatment formulas and genomic-targeting methods could be breached and their contents stolen.

### Description
**Likelihood:** Medium — the intellectual property behind personalised, genomic-targeted treatments is exactly the kind of high-value, hard-to-replace asset that attracts state-sponsored and commercial espionage. **Impact:** Critical — loss of this intellectual property would erode Coco Pharmaceuticals' competitive advantage in its core strategic transformation and could take years of research investment to recover from. **Overall rating:** Critical.

### Implications
- Research systems holding treatment formulas must have the strongest tier of access control
- Access to this intellectual property must be logged and regularly reviewed
- Data loss prevention controls must monitor for bulk export of research data

### Importance
Critical

### Category
Cyber Security

### Authors
Ivor Padlock

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

### 3.2 Privacy and Data Protection Risks

___

## Create Risk

### Display Name
Accidental Disclosure of Patient Data through Misconfigured Access

### Qualified Name
CocoPharma::Risk::AccidentalPatientDataDisclosure

### Domain Identifier
PRIVACY

### Summary
Patient health data could be exposed to unauthorised parties through a misconfigured access control, rather than through deliberate attack.

### Description
**Likelihood:** Medium — as more systems are connected to support real-time data sharing between research, manufacturing, and hospital partners, the number of access control configurations that must be got right — and kept right as systems change — grows. Misconfiguration is a leading cause of data exposure across the industry. **Impact:** Critical — patient health data is among the most sensitive personal data categories under GDPR; exposure would harm patients, trigger mandatory breach notification, and expose Coco Pharmaceuticals to fines of up to 4% of global turnover. **Overall rating:** High.

### Implications
- Access control configurations for systems holding patient data must be reviewed on a defined schedule
- Automated scanning for over-permissive access should be considered for critical patient data stores
- Configuration changes to these systems must go through a change control process

### Importance
High

### Category
Privacy and Data Protection

### Authors
Faith Broker

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Risk

### Display Name
Insider Misuse of Sensitive Patient Data

### Qualified Name
CocoPharma::Risk::InsiderMisuseOfPatientData

### Domain Identifier
PRIVACY

### Summary
A member of staff with legitimate access to patient data could use it for a purpose that has not been approved.

### Description
**Likelihood:** Low-Medium — most staff act in good faith, but as more people gain legitimate access to patient data to support cross-department data sharing, the population of people who could misuse it grows. **Impact:** Critical — insider misuse is harder to detect than external attack, can go on for longer before discovery, and carries the same regulatory and reputational consequences as any other unauthorised disclosure. **Overall rating:** High.

### Implications
- Data processing purposes must be documented and approved before staff are granted access
- Access to patient data should be logged and subject to periodic review for purpose-consistency
- Staff must receive training on approved uses of patient data and the consequences of misuse

### Importance
High

### Category
Privacy and Data Protection

### Authors
Faith Broker

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

### 3.3 Supply Chain and Corporate Risks

___

## Create Risk

### Display Name
Onboarding of a Fraudulent or Compromised Supplier

### Qualified Name
CocoPharma::Risk::FraudulentSupplierOnboarding

### Domain Identifier
CORPORATE

### Summary
A bogus or compromised supplier could be onboarded into the procurement process, as has already happened once at Coco Pharmaceuticals.

### Description
**Likelihood:** Medium — this has already occurred once, and the underlying weaknesses in supplier data ownership and change control that allowed it have not yet been fully remediated. **Impact:** High — a fraudulent supplier can cause direct financial loss and, if payments or approvals are involved, can escalate into a wider financial control failure. **Overall rating:** High.

### Implications
- Supplier master data must have a designated, accountable owner
- New supplier onboarding must include identity verification steps
- Changes to existing supplier records (particularly banking details) must require independent approval

### Importance
High

### Category
Supply Chain Risk

### Authors
Reggie Mint

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Risk

### Display Name
Counterfeit or Substandard Materials Entering Manufacturing

### Qualified Name
CocoPharma::Risk::CounterfeitMaterialsInManufacturing

### Domain Identifier
CORPORATE

### Summary
A compromised supplier could introduce counterfeit or substandard raw materials into the pharmaceutical manufacturing process.

### Description
**Likelihood:** Low-Medium — the pharmaceutical supply chain is a known target for counterfeit material, though Coco Pharmaceuticals' existing supplier vetting reduces exposure relative to organisations without any controls. **Impact:** Critical — counterfeit or substandard inputs to drug manufacturing can directly harm patients and would trigger the most severe possible regulatory and reputational consequences for the organisation. **Overall rating:** Critical.

### Implications
- Raw material sourcing must be traceable back to a verified, approved supplier for every batch
- Incoming material quality checks must be performed before release to production
- Supplier approval status must be checked before each order, not only at initial onboarding

### Importance
Critical

### Category
Supply Chain Risk

### Authors
Reggie Mint

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

### 3.4 Regulatory and Clinical Compliance Risks

___

## Create Risk

### Display Name
Loss of Clinical Trial Data Integrity

### Qualified Name
CocoPharma::Risk::ClinicalTrialDataIntegrityLoss

### Domain Identifier
DATA

### Summary
Clinical trial data could lose the completeness, accuracy, or auditability required by FDA regulations, whether through system failure or human error.

### Description
**Likelihood:** Low-Medium — clinical systems are typically well-controlled, but the requirements of 21 CFR Part 11 are exacting and any gap in validated access controls or audit trail completeness constitutes a failure. **Impact:** Critical — a finding of compromised clinical trial data integrity can result in rejection of trial results, withdrawal of drug approvals, and criminal liability for the organisation and individuals involved. **Overall rating:** Critical.

### Implications
- Systems holding clinical trial data must be validated and their access controls tested regularly
- Electronic records must have a complete audit trail from source data to reported result
- Any detected integrity gap must be investigated and reported through a formal deviation process

### Importance
Critical

### Category
Drug Development and Clinical Trials

### Authors
Tessa Tube

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Risk

### Display Name
Manufacturing Batch Records Failing GMP Traceability Requirements

### Qualified Name
CocoPharma::Risk::GMPBatchRecordNonCompliance

### Domain Identifier
DATA

### Summary
Manufacturing batch records could be incomplete or fail to trace back to raw material sourcing, breaching Good Manufacturing Practice requirements.

### Description
**Likelihood:** Medium — the shift towards personalised, on-demand manufacturing multiplies the number of distinct batch records that must be completed correctly, increasing the chance that one falls short of GMP traceability requirements. **Impact:** High — incomplete batch records can delay or block product release, trigger regulatory inspection findings, and in the worst case allow an unsafe product to reach a patient undetected. **Overall rating:** High.

### Implications
- Batch record templates must capture every data point required for GMP traceability
- Batch records must be reviewed and signed off before product release
- Deviations found during batch review must be investigated and documented

### Importance
High

### Category
Pharmaceutical Manufacturing

### Authors
Tessa Tube

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

### 3.5 Organisational and Knowledge Risks

___

## Create Risk

### Display Name
Loss of Undocumented Governance Knowledge on Staff Departure

### Qualified Name
CocoPharma::Risk::LossOfUndocumentedGovernanceKnowledge

### Domain Identifier
ALL

### Summary
Departure of a domain lead or other key member of staff could remove undocumented knowledge of governance decisions, data definitions, or processes.

### Description
**Likelihood:** Medium — Coco Pharmaceuticals has historically relied on informal knowledge sharing, and the formal metadata-driven governance program is still being built out, so there is currently more undocumented knowledge than documented. **Impact:** High — loss of this knowledge could stall governance activity, cause inconsistent decisions by successors, and delay onboarding of replacement staff. **Overall rating:** High.

### Implications
- Governance decisions and rationale must be captured in the metadata catalog as they are made, not reconstructed afterwards
- Domain leads should identify and document undocumented knowledge as a standing responsibility, not a one-off exercise
- Handover documentation must be required as part of any planned staff transition

### Importance
High

### Category
Knowledge Management

### Authors
Jules Keeper

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Risk

### Display Name
Inconsistent Data Definitions Undermining Cross-Department Reporting

### Qualified Name
CocoPharma::Risk::InconsistentDataDefinitionsReportingErrors

### Domain Identifier
DATA

### Summary
Different departments could continue to define the same data (such as "patient", "batch", or "revenue") differently, causing combined reports to be wrong without anyone noticing.

### Description
**Likelihood:** Medium — this pattern already exists at Coco Pharmaceuticals today, as a direct consequence of historically siloed, informally governed departments; the common glossary intended to fix it is still being populated. **Impact:** Medium-High — reports and analytics that silently combine inconsistently defined data can drive incorrect business, clinical, or financial decisions without any error being visible to the people relying on them. **Overall rating:** Medium-High.

### Implications
- Cross-department reports must state which glossary definitions their inputs conform to
- New data sharing between departments should trigger a check that shared terms have agreed definitions
- Discrepancies discovered between departmental definitions must be escalated for resolution, not silently reconciled

### Importance
Medium-High

### Category
Knowledge Management

### Authors
Jules Keeper

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

### 3.6 Physical Security and Event Risks

___

## Create Risk

### Display Name
Terrorism-Related Incident at the Annual Conference

### Qualified Name
CocoPharma::Risk::TerrorismIncidentAtAnnualConference

### Domain Identifier
SECURITY

### Summary
Coco Pharmaceuticals' annual conference, attracting around 700 attendees, could be the scene of, or affected by, a terrorism-related incident.

### Description
**Likelihood:** Low — there is no specific intelligence suggesting Coco Pharmaceuticals or its conference is a targeted risk, but any large public gathering carries a baseline exposure to this threat. **Impact:** Critical — any incident affecting attendee safety would be catastrophic in human terms and would carry severe legal and reputational consequences for the organisation. **Overall rating:** Medium-High, reflecting low likelihood combined with critical impact.

### Implications
- Public protection procedures (evacuation, invacuation, lockdown, communication) must be documented and rehearsed before each conference
- Venue security assessments must be refreshed for each event, particularly if attendance approaches the 800-attendee enhanced tier threshold
- Staff working at the event must be briefed on their role in the public protection procedures

### Importance
Medium-High

### Category
Event Security

### Authors
Ivor Padlock

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Risk

### Display Name
Failure to Discharge Martyn's Law Responsible Person Duties

### Qualified Name
CocoPharma::Risk::MartynsLawResponsiblePersonNonCompliance

### Domain Identifier
SECURITY

### Summary
Coco Pharmaceuticals could fail to formally designate, or adequately support, the Responsible Person role required by Martyn's Law for its annual conference.

### Description
**Likelihood:** Low-Medium — enforcement of Martyn's Law begins in 2027, giving time to prepare, but the role has not yet been formally assigned and the required security assessments and documentation are not yet in place. **Impact:** High — non-compliance exposes Coco Pharmaceuticals to enforcement action from the Security Industry Authority and, more importantly, leaves the underlying terrorism risk to the conference unmanaged. **Overall rating:** Medium-High.

### Implications
- A Responsible Person must be formally designated with clear authority and resourcing well ahead of the 2027 enforcement date
- Required security assessments and public protection procedure documentation must be prepared and kept current
- Compliance status must be tracked and reported to the CISO as part of routine security governance

### Importance
Medium-High

### Category
Event Security

### Authors
Ivor Padlock

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

## Part 4: Collection Membership

### 4.1 Risk Categories linked to the Root Collection

___

## Add Member to Collection

### Element Id
CocoPharma::CollectionFolder::CyberSecurityRisks

### Membership Rationale
Cyber security risks are grouped under the risk register root collection.

### Membership Status
VALIDATED

### Collection Id
CocoPharma::Collection::RiskRegister

___

---

___

## Add Member to Collection

### Element Id
CocoPharma::CollectionFolder::PrivacyRisks

### Membership Rationale
Privacy and data protection risks are grouped under the risk register root collection.

### Membership Status
VALIDATED

### Collection Id
CocoPharma::Collection::RiskRegister

___

---

___

## Add Member to Collection

### Element Id
CocoPharma::CollectionFolder::SupplyChainRisks

### Membership Rationale
Supply chain and corporate risks are grouped under the risk register root collection.

### Membership Status
VALIDATED

### Collection Id
CocoPharma::Collection::RiskRegister

___

---

___

## Add Member to Collection

### Element Id
CocoPharma::CollectionFolder::RegulatoryComplianceRisks

### Membership Rationale
Regulatory and clinical compliance risks are grouped under the risk register root collection.

### Membership Status
VALIDATED

### Collection Id
CocoPharma::Collection::RiskRegister

___

---

___

## Add Member to Collection

### Element Id
CocoPharma::CollectionFolder::OrganisationalRisks

### Membership Rationale
Organisational and knowledge risks are grouped under the risk register root collection.

### Membership Status
VALIDATED

### Collection Id
CocoPharma::Collection::RiskRegister

___

---

___

## Add Member to Collection

### Element Id
CocoPharma::CollectionFolder::PhysicalSecurityRisks

### Membership Rationale
Physical security and event risks are grouped under the risk register root collection.

### Membership Status
VALIDATED

### Collection Id
CocoPharma::Collection::RiskRegister

___

---

### 4.2 Risks linked to their Category Folder

___

## Add Member to Collection

### Element Id
CocoPharma::Risk::RansomwareDisruptionToManufacturing

### Membership Rationale
Add this risk to the Cyber Security Risks folder.

### Membership Status
VALIDATED

### Collection Id
CocoPharma::CollectionFolder::CyberSecurityRisks

___

---

___

## Add Member to Collection

### Element Id
CocoPharma::Risk::TheftOfPersonalisedTreatmentIP

### Membership Rationale
Add this risk to the Cyber Security Risks folder.

### Membership Status
VALIDATED

### Collection Id
CocoPharma::CollectionFolder::CyberSecurityRisks

___

---

___

## Add Member to Collection

### Element Id
CocoPharma::Risk::AccidentalPatientDataDisclosure

### Membership Rationale
Add this risk to the Privacy and Data Protection Risks folder.

### Membership Status
VALIDATED

### Collection Id
CocoPharma::CollectionFolder::PrivacyRisks

___

---

___

## Add Member to Collection

### Element Id
CocoPharma::Risk::InsiderMisuseOfPatientData

### Membership Rationale
Add this risk to the Privacy and Data Protection Risks folder.

### Membership Status
VALIDATED

### Collection Id
CocoPharma::CollectionFolder::PrivacyRisks

___

---

___

## Add Member to Collection

### Element Id
CocoPharma::Risk::FraudulentSupplierOnboarding

### Membership Rationale
Add this risk to the Supply Chain and Corporate Risks folder.

### Membership Status
VALIDATED

### Collection Id
CocoPharma::CollectionFolder::SupplyChainRisks

___

---

___

## Add Member to Collection

### Element Id
CocoPharma::Risk::CounterfeitMaterialsInManufacturing

### Membership Rationale
Add this risk to the Supply Chain and Corporate Risks folder.

### Membership Status
VALIDATED

### Collection Id
CocoPharma::CollectionFolder::SupplyChainRisks

___

---

___

## Add Member to Collection

### Element Id
CocoPharma::Risk::ClinicalTrialDataIntegrityLoss

### Membership Rationale
Add this risk to the Regulatory and Clinical Compliance Risks folder.

### Membership Status
VALIDATED

### Collection Id
CocoPharma::CollectionFolder::RegulatoryComplianceRisks

___

---

___

## Add Member to Collection

### Element Id
CocoPharma::Risk::GMPBatchRecordNonCompliance

### Membership Rationale
Add this risk to the Regulatory and Clinical Compliance Risks folder.

### Membership Status
VALIDATED

### Collection Id
CocoPharma::CollectionFolder::RegulatoryComplianceRisks

___

---

___

## Add Member to Collection

### Element Id
CocoPharma::Risk::LossOfUndocumentedGovernanceKnowledge

### Membership Rationale
Add this risk to the Organisational and Knowledge Risks folder.

### Membership Status
VALIDATED

### Collection Id
CocoPharma::CollectionFolder::OrganisationalRisks

___

---

___

## Add Member to Collection

### Element Id
CocoPharma::Risk::InconsistentDataDefinitionsReportingErrors

### Membership Rationale
Add this risk to the Organisational and Knowledge Risks folder.

### Membership Status
VALIDATED

### Collection Id
CocoPharma::CollectionFolder::OrganisationalRisks

___

---

___

## Add Member to Collection

### Element Id
CocoPharma::Risk::TerrorismIncidentAtAnnualConference

### Membership Rationale
Add this risk to the Physical Security and Event Risks folder.

### Membership Status
VALIDATED

### Collection Id
CocoPharma::CollectionFolder::PhysicalSecurityRisks

___

---

___

## Add Member to Collection

### Element Id
CocoPharma::Risk::MartynsLawResponsiblePersonNonCompliance

### Membership Rationale
Add this risk to the Physical Security and Event Risks folder.

### Membership Status
VALIDATED

### Collection Id
CocoPharma::CollectionFolder::PhysicalSecurityRisks

___

---

## Part 5: Risk-to-Threat Links

Each link below records a risk (the Policy end of the relationship) as a Governance Response to the threat (the Driver end) whose likelihood and impact it assesses.

___

## Link Governance Response

### Driver
CocoPharma::Threat::CyberAttackOnOperationsOrData

### Policy
CocoPharma::Risk::RansomwareDisruptionToManufacturing

### Rationale
This risk assesses the specific likelihood and impact of the cyber-attack threat manifesting as a ransomware attack on manufacturing operations.

___

---

___

## Link Governance Response

### Driver
CocoPharma::Threat::CyberAttackOnOperationsOrData

### Policy
CocoPharma::Risk::TheftOfPersonalisedTreatmentIP

### Rationale
This risk assesses the specific likelihood and impact of the cyber-attack threat manifesting as theft of high-value research intellectual property.

___

---

___

## Link Governance Response

### Driver
CocoPharma::Threat::UnauthorisedDataDisclosure

### Policy
CocoPharma::Risk::AccidentalPatientDataDisclosure

### Rationale
This risk assesses the specific likelihood and impact of the unauthorised disclosure threat manifesting through accidental misconfiguration rather than deliberate action.

___

---

___

## Link Governance Response

### Driver
CocoPharma::Threat::UnauthorisedDataDisclosure

### Policy
CocoPharma::Risk::InsiderMisuseOfPatientData

### Rationale
This risk assesses the specific likelihood and impact of the unauthorised disclosure threat manifesting through deliberate insider misuse.

___

---

___

## Link Governance Response

### Driver
CocoPharma::Threat::FraudulentSupplierActivity

### Policy
CocoPharma::Risk::FraudulentSupplierOnboarding

### Rationale
This risk assesses the specific likelihood and impact of the fraudulent supplier threat manifesting during supplier onboarding.

___

---

___

## Link Governance Response

### Driver
CocoPharma::Threat::FraudulentSupplierActivity

### Policy
CocoPharma::Risk::CounterfeitMaterialsInManufacturing

### Rationale
This risk assesses the specific likelihood and impact of the fraudulent supplier threat manifesting as counterfeit or substandard materials reaching manufacturing.

___

---

___

## Link Governance Response

### Driver
CocoPharma::Threat::ClinicalTrialDataIntegrityFailure

### Policy
CocoPharma::Risk::ClinicalTrialDataIntegrityLoss

### Rationale
This risk directly assesses the likelihood and impact of the clinical trial data integrity threat.

___

---

___

## Link Governance Response

### Driver
CocoPharma::Threat::ManufacturingQualityDeviation

### Policy
CocoPharma::Risk::GMPBatchRecordNonCompliance

### Rationale
This risk directly assesses the likelihood and impact of the manufacturing quality deviation threat manifesting as incomplete or untraceable batch records.

___

---

___

## Link Governance Response

### Driver
CocoPharma::Threat::LossOfKeyTalentAndKnowledge

### Policy
CocoPharma::Risk::LossOfUndocumentedGovernanceKnowledge

### Rationale
This risk directly assesses the likelihood and impact of the loss of key talent and knowledge threat on governance knowledge specifically.

___

---

___

## Link Governance Response

### Driver
CocoPharma::Threat::LossOfKeyTalentAndKnowledge

### Policy
CocoPharma::Risk::InconsistentDataDefinitionsReportingErrors

### Rationale
This risk assesses the likelihood and impact of the loss of key talent and knowledge threat manifesting as inconsistent, undocumented data definitions rather than as a single point-in-time knowledge loss.

___

---

___

## Link Governance Response

### Driver
CocoPharma::Threat::TerrorismAtPublicEvents

### Policy
CocoPharma::Risk::TerrorismIncidentAtAnnualConference

### Rationale
This risk directly assesses the likelihood and impact of the terrorism at public events threat as it applies to Coco Pharmaceuticals' own annual conference.

___

---

___

## Link Governance Response

### Driver
CocoPharma::Threat::TerrorismAtPublicEvents

### Policy
CocoPharma::Risk::MartynsLawResponsiblePersonNonCompliance

### Rationale
This risk assesses the likelihood and impact of failing to put in place the governance response (the Responsible Person role and supporting procedures) that Martyn's Law requires to manage the terrorism at public events threat.

___

---

## Part 6: Folio Membership

The [Data Governance Program](data-governance-program.md) defines a governance folio for each domain lead (Part 6: Governance Folios), collecting the definitions that role is accountable for. The new threats and risks defined in this register are added as members of the existing folio matching their domain and author, so each domain lead's folio remains a complete view of the governance work they own.

---

### 6.1 Chief Data Officer Folio Members

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefDataOfficer

### Element Id
CocoPharma::Risk::LossOfUndocumentedGovernanceKnowledge

### Membership Rationale
This risk assesses the likelihood and impact of the Loss of Key Talent and Knowledge threat, which is already a member of the CDO's folio. The CDO is accountable for capturing governance knowledge as metadata rather than allowing it to remain undocumented.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefDataOfficer

### Element Id
CocoPharma::Risk::InconsistentDataDefinitionsReportingErrors

### Membership Rationale
Establishing and maintaining common data definitions is a core CDO responsibility; this risk assesses the impact of that responsibility not yet being fully discharged.

### Membership Status
VALIDATED

___

---

### 6.2 Chief Information Security Officer Folio Members

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefInformationSecurityOfficer

### Element Id
CocoPharma::Threat::TerrorismAtPublicEvents

### Membership Rationale
The CISO is the domain lead for security compliance, including Martyn's Law — already a member of this folio — and this threat is the underlying driver that regulation responds to.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefInformationSecurityOfficer

### Element Id
CocoPharma::Risk::RansomwareDisruptionToManufacturing

### Membership Rationale
This risk assesses the likelihood and impact of the Cyber-Attack on Operations or Data threat, which the CISO is responsible for mitigating.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefInformationSecurityOfficer

### Element Id
CocoPharma::Risk::TheftOfPersonalisedTreatmentIP

### Membership Rationale
This risk assesses the likelihood and impact of the Cyber-Attack on Operations or Data threat, which the CISO is responsible for mitigating.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefInformationSecurityOfficer

### Element Id
CocoPharma::Risk::TerrorismIncidentAtAnnualConference

### Membership Rationale
Physical event security, including terrorism preparedness for the annual conference, falls within the CISO's security governance domain.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefInformationSecurityOfficer

### Element Id
CocoPharma::Risk::MartynsLawResponsiblePersonNonCompliance

### Membership Rationale
The CISO is accountable for Martyn's Law compliance, including designation and support of the Responsible Person role this risk assesses.

### Membership Status
VALIDATED

___

---

### 6.3 Chief Privacy Officer Folio Members

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefPrivacyOfficer

### Element Id
CocoPharma::Risk::AccidentalPatientDataDisclosure

### Membership Rationale
This risk assesses the likelihood and impact of the Unauthorised Data Disclosure threat, already a member of the CPO's folio, arising through accidental misconfiguration.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefPrivacyOfficer

### Element Id
CocoPharma::Risk::InsiderMisuseOfPatientData

### Membership Rationale
This risk assesses the likelihood and impact of the Unauthorised Data Disclosure threat, already a member of the CPO's folio, arising through deliberate insider misuse.

### Membership Status
VALIDATED

___

---

### 6.4 Chief Financial Officer Folio Members

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefFinancialOfficer

### Element Id
CocoPharma::Risk::FraudulentSupplierOnboarding

### Membership Rationale
This risk assesses the likelihood and impact of the Fraudulent Supplier Activity threat, already a member of the CFO's folio, arising during supplier onboarding.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefFinancialOfficer

### Element Id
CocoPharma::Risk::CounterfeitMaterialsInManufacturing

### Membership Rationale
This risk assesses the likelihood and impact of the Fraudulent Supplier Activity threat, already a member of the CFO's folio, arising as counterfeit or substandard materials reaching manufacturing.

### Membership Status
VALIDATED

___

---

### 6.5 Drug Development Lead Folio Members

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::DrugDevelopmentLead

### Element Id
CocoPharma::Threat::ClinicalTrialDataIntegrityFailure

### Membership Rationale
Tessa Tube is accountable for ensuring clinical trial data governance meets FDA requirements, of which data integrity is the central concern.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::DrugDevelopmentLead

### Element Id
CocoPharma::Threat::ManufacturingQualityDeviation

### Membership Rationale
Tessa Tube's drug development remit extends to Good Manufacturing Practice compliance for the manufacturing of the treatments developed under her leadership.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::DrugDevelopmentLead

### Element Id
CocoPharma::Risk::ClinicalTrialDataIntegrityLoss

### Membership Rationale
This risk directly assesses the likelihood and impact of the Clinical Trial Data Integrity Failure threat, owned by the Drug Development Lead.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::DrugDevelopmentLead

### Element Id
CocoPharma::Risk::GMPBatchRecordNonCompliance

### Membership Rationale
This risk directly assesses the likelihood and impact of the Manufacturing Quality Deviation threat, owned by the Drug Development Lead.

### Membership Status
VALIDATED

___

---
