# Coco Pharmaceuticals Data Governance Program

> **Author:** Jules Keeper (Chief Data Officer)  
> **Version:** 1.0  
> **Status:** DRAFT  
> **Date:** 2026-07-01  
> **Description:** This document defines the data governance program for Coco Pharmaceuticals, covering governance drivers, policies, and controls across all governance domains.

---

## Overview

Coco Pharmaceuticals is undergoing a strategic transformation — moving from batch drug manufacturing towards personalised medicine. This transition requires a formal, multi-faceted governance program to ensure that data and information assets are managed consistently, securely, and ethically across the organisation.

The governance program is organised into three layers:

1. **Governance Drivers** — the business imperatives, threats, and regulations that motivate governance activity.
2. **Governance Policies** — the principles, obligations, and approaches that define how the organisation responds to the drivers.
3. **Governance Controls** — the roles, actions, metrics, and procedures that implement the policies in day-to-day operations.

---

## Part 1: Governance Drivers

Governance drivers are the reasons why Coco Pharmaceuticals needs a governance program. They are divided into three types: *business imperatives*, *threats*, and *regulations*.

---

### 1.1 Business Imperatives

___

## Create Business Imperative

### Display Name
Personalized Medicine Transition

### Qualified Name
CocoPharma::BusinessImperative::PersonalisedMedicineTransition

### Domain Identifier
ALL

### Summary
Coco Pharmaceuticals is shifting from batch manufacturing of generic drugs to personalised, genomic-targeted treatments delivered on-demand.

### Description
The organisation's core strategic direction is to provide personalised medicine to its customers. This requires a fundamental change in how data is collected, shared, and acted upon across research, manufacturing, clinical operations, and finance. Real-time data exchange between departments becomes essential; patient characteristics must drive treatment decisions; and manufacturing must operate a hybrid model supporting both existing batch processes and agile on-demand production for new drugs.

### Implications
- Data must be available in real-time across all departments
- Information about patients must be handled with appropriate privacy controls
- Manufacturing systems must integrate with active treatment plans
- Finance needs cash flow visibility across patients, suppliers, and predictions

### Outcomes
- Physicians have interactive decision support based on individual patient characteristics
- Hospital partners can order drugs on-demand rather than in batches
- Research cycles are accelerated through data-driven insights

### Importance
Critical — this is the primary strategic direction of the organisation.

### Category
Strategic Transformation

### Authors
Jules Keeper

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Business Imperative

### Display Name
Cycle Time Reduction

### Qualified Name
CocoPharma::BusinessImperative::CycleTimeReduction

### Domain Identifier
ALL

### Summary
Coco Pharmaceuticals must reduce cycle times across all business operations to remain competitive.

### Description
The move to personalised medicine and on-demand manufacturing demands that the organisation operates much faster. Hospitals require agile ordering and validation processes. Research teams need to accelerate drug development timelines. Finance and operations must have real-time visibility to support dynamic planning. Reducing cycle times is only possible with well-governed, high-quality, consistently defined data flowing between all departments without friction.

### Implications
- Data must be consistently defined so that it can be shared without manual reconciliation
- Information supply chains must be optimised and monitored for failures
- Authoritative data sources must be identified so staff are not delayed by uncertainty about data quality

### Outcomes
- Faster drug development from research to manufacturing
- Reduced time from patient referral to treatment
- Faster financial reporting and planning cycles

### Importance
High

### Category
Operational Efficiency

### Authors
Jules Keeper

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Business Imperative

### Display Name
Cyber Resilience

### Qualified Name
CocoPharma::BusinessImperative::CyberResilience

### Domain Identifier
SECURITY

### Summary
Coco Pharmaceuticals must protect its intellectual property, patient data, and operational systems against cyber threats to sustain its business.

### Description
As Coco Pharmaceuticals relies increasingly on digital systems and data sharing — including sharing patient data with hospitals, research partners, and regulators — it becomes a more attractive target for cyber-attacks. Intellectual property related to novel personalised treatments is particularly valuable. Cyber resilience requires governance over who can access what data, under what conditions, and with what audit trail.

### Implications
- All systems containing sensitive data must have access controls
- Audit logs must capture who accessed or modified data and when
- Security incidents must be detected and responded to promptly

### Outcomes
- Intellectual property is protected from theft or exposure
- Patient data is not compromised
- Business operations continue without disruption from cyber incidents

### Importance
Critical

### Category
Security & Resilience

### Authors
Ivor Padlock

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Business Imperative

### Display Name
Sustainability Reporting

### Qualified Name
CocoPharma::BusinessImperative::SustainabilityReporting

### Domain Identifier
CORPORATE

### Summary
Coco Pharmaceuticals must track, measure, and report on its environmental and social sustainability to meet stakeholder expectations and emerging regulatory requirements.

### Description
Stakeholders — including investors, customers, and regulators — increasingly expect organisations to demonstrate responsible environmental and social practices. Coco Pharmaceuticals must build the data infrastructure to measure its sustainability performance and report on it accurately. This requires governance over the data collected from manufacturing, logistics, facilities, and supply chains.

### Implications
- Sustainability data must be collected consistently and with clear definitions
- Authoritative sources for energy, emissions, and waste data must be identified
- Reports must be auditable and traceable to source data

### Outcomes
- Accurate sustainability reports that build stakeholder confidence
- Identification of areas where the organisation can improve its environmental impact
- Readiness for any future regulatory sustainability reporting requirements

### Importance
Medium-High

### Category
Sustainability

### Authors
Tom Tally

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

### 1.2 Threats

___

## Create Threat

### Display Name
Cyber-Attack on Operations or Data

### Qualified Name
CocoPharma::Threat::CyberAttackOnOperationsOrData

### Domain Identifier
SECURITY

### Summary
Malicious actors may attempt to disrupt Coco Pharmaceuticals' operations or steal sensitive data through cyber-attacks.

### Description
Coco Pharmaceuticals holds high-value intellectual property related to novel drug formulas and personalised treatment protocols. It also holds sensitive patient health data. Both categories make it an attractive target for cyber-attacks — whether ransomware disrupting manufacturing, data theft from research systems, or manipulation of clinical trial data. The threat is heightened as the organisation increases its use of digital systems and data sharing with external partners.

### Implications
- Access to sensitive systems must be tightly controlled and audited
- Data shared with external partners must be governed by agreements and monitored
- Incident response procedures must exist and be tested regularly

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

## Create Threat

### Display Name
Unauthorised Data Disclosure

### Qualified Name
CocoPharma::Threat::UnauthorisedDataDisclosure

### Domain Identifier
PRIVACY

### Summary
Patient data or commercially sensitive information may be disclosed to unauthorised parties — accidentally or through insider misuse.

### Description
Coco Pharmaceuticals handles sensitive patient health data as part of clinical trials and personalised treatment programmes. There is a real risk that this data could be inadvertently disclosed — through misconfigured access controls, human error, or deliberate insider misuse. Such disclosure could harm patients, expose the organisation to regulatory fines, and damage its reputation with hospital partners and patients. The risk increases as more data is shared digitally across organisational boundaries.

### Implications
- Personal data must be classified and handled under defined privacy controls
- Data sharing with hospitals and research partners must be governed by formal agreements
- Staff must understand their responsibilities for protecting patient data

### Importance
Critical

### Category
Privacy & Data Protection

### Authors
Faith Broker

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Threat

### Display Name
Fraudulent Supplier Activity

### Qualified Name
CocoPharma::Threat::FraudulentSupplierActivity

### Domain Identifier
CORPORATE

### Summary
The organisation may be exposed to fraud through bogus or compromised suppliers entering the supply chain.

### Description
A previous incident at Coco Pharmaceuticals involved a fraudulent supplier entering the procurement process. Without adequate governance over supplier data and procurement workflows, the organisation is vulnerable to financial loss, reputational damage, and — in the context of pharmaceutical manufacturing — potentially serious harm from substandard or counterfeit inputs. Strong data governance over supplier identity and procurement data reduces this risk.

### Implications
- Supplier master data must have a designated authoritative source
- Changes to supplier records must require approval and audit
- Procurement data must be accurate and traceable

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

## Create Threat

### Display Name
Loss of Key Talent and Knowledge

### Qualified Name
CocoPharma::Threat::LossOfKeyTalentAndKnowledge

### Domain Identifier
ALL

### Summary
Departure of key personnel could result in loss of critical knowledge about data definitions, processes, and governance practices.

### Description
Coco Pharmaceuticals has historically relied on informal knowledge sharing — a pattern common in startup cultures. As the organisation grows and formalises, there is a risk that institutional knowledge held by individuals is not captured in documented form. If key staff leave, this knowledge may be lost, leaving the organisation unable to operate processes or make decisions that depend on undocumented understanding. The governance program must capture knowledge as documented governance definitions and data specifications.

### Implications
- Governance definitions, data definitions, and process documentation must be maintained in a shared metadata catalog
- Authoritative sources and data stewards must be formally assigned — not left to informal convention
- Onboarding new staff must rely on documented knowledge rather than tribal knowledge

### Importance
Medium

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

### 1.3 Regulations

___

## Create Regulation

### Display Name
General Data Protection Regulation (GDPR)

### Qualified Name
CocoPharma::Regulation::GDPR

### Domain Identifier
PRIVACY

### Summary
EU regulation governing the collection, processing, storage, and sharing of personal data, including patient health data.

### Description
GDPR applies to all personal data processed by Coco Pharmaceuticals, including patient data collected during clinical trials, treatment programmes, and any data sharing activities with hospitals. It requires organisations to have a lawful basis for processing personal data, to protect data subjects' rights, to implement appropriate security measures, and to notify authorities and individuals in the event of a data breach. Non-compliance can result in fines of up to 4% of global annual turnover.

### Regulation Source
European Union — Regulation (EU) 2016/679

### Regulators
- Information Commissioner's Office (ICO) — UK
- National data protection authorities in EU member states

### Implications
- Personal data must be identified, classified, and handled under defined privacy controls
- Data processing must have a documented lawful basis
- Data subjects must be able to exercise their rights (access, erasure, portability)
- Data breach notification procedures must exist

### Importance
Critical

### Category
Privacy & Data Protection

### Domain Identifier
PRIVACY

### Authors
Faith Broker

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Regulation

### Display Name
FDA Clinical Trial Regulations

### Qualified Name
CocoPharma::Regulation::FDAClinicalTrialRegulations

### Domain Identifier
DATA

### Summary
US Food and Drug Administration regulations governing the conduct, recording, and reporting of clinical trials.

### Description
Coco Pharmaceuticals conducts clinical trials as part of its drug development activities. FDA regulations — including 21 CFR Parts 11, 50, 56, and 312 — impose strict requirements on how clinical trial data is collected, managed, validated, and reported. Electronic records must be trustworthy, reliable, and equivalent to paper records. Data integrity is critical; falsification or loss of clinical trial data can result in regulatory action, withdrawal of drug approvals, and criminal liability.

### Regulation Source
US Food and Drug Administration (FDA)

### Regulators
- US Food and Drug Administration (FDA)

### Implications
- Clinical trial data must have a clear audit trail from source to report
- Systems holding clinical trial data must have validated access controls
- Data quality rules must be enforced and documented
- Data retention periods must be respected

### Importance
Critical

### Category
Drug Development & Clinical Trials

### Authors
Tessa Tube

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Regulation

### Display Name
Good Manufacturing Practice (GMP)

### Qualified Name
CocoPharma::Regulation::GoodManufacturingPractice

### Domain Identifier
DATA

### Summary
Regulations governing pharmaceutical manufacturing to ensure products are consistently produced and controlled according to quality standards.

### Description
GMP regulations (EU GMP Directive 2003/94/EC and US 21 CFR Parts 210–211) require pharmaceutical manufacturers to document all manufacturing processes, control quality at every stage, and maintain complete records. For Coco Pharmaceuticals, this means manufacturing data — including batch records, equipment logs, and quality control results — must be governed to ensure completeness, accuracy, and traceability. As the organisation moves towards personalised on-demand manufacturing, these requirements become even more complex.

### Regulation Source
EU European Medicines Agency (EMA) and US Food and Drug Administration (FDA)

### Regulators
- European Medicines Agency (EMA)
- Medicines and Healthcare products Regulatory Agency (MHRA) — UK
- US Food and Drug Administration (FDA)

### Implications
- Manufacturing data must be complete, accurate, and tamper-evident
- Batch records must be traceable to raw material sourcing
- Quality control data must be retained for defined periods
- Deviations from process must be documented and investigated

### Importance
Critical

### Category
Pharmaceutical Manufacturing

### Authors
Jules Keeper

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Regulation

### Display Name
Martyn's Law (Terrorism Protection of Premises Act 2025)

### Qualified Name
CocoPharma::Regulation::MartynsLaw

### Domain Identifier
SECURITY

### Summary
UK legislation requiring event venues with over 200 attendees to implement security measures, with enhanced requirements for venues over 800 attendees.

### Description
The UK Terrorism (Protection of Premises) Act 2025 — known as Martyn's Law — requires organisations that host public events to implement security measures appropriate to the size of the event. Coco Pharmaceuticals hosts an annual conference in London that currently attracts approximately 700 attendees, placing it within scope of the standard tier requirements. Enforcement begins in 2027, requiring advance planning. A designated "Responsible Person" role must be assigned to oversee compliance.

### Regulation Source
UK Parliament — Terrorism (Protection of Premises) Act 2025

### Regulators
- UK Home Office
- Security Industry Authority (SIA)

### Implications
- A Responsible Person must be formally designated for the annual conference
- Security assessments (including escape routes and safety infrastructure) must be documented
- If attendance grows beyond 800, enhanced tier requirements apply
- Compliance must be demonstrated and recorded

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

## Part 2: Governance Policies

Governance policies define how Coco Pharmaceuticals responds to the governance drivers above. They are divided into three types: *principles* (desired end states), *obligations* (mandatory requirements), and *approaches* (methods to be followed).

---

### 2.1 Governance Principles

___

## Create Governance Principle

### Display Name
Information is a Company Asset

### Qualified Name
CocoPharma::GovernancePrinciple::InformationIsACompanyAsset

### Domain Identifier
ALL

### Summary
All information created or used by Coco Pharmaceuticals is recognised as a company asset and will be managed accordingly.

### Description
Information — like physical equipment or financial capital — is a valuable asset that belongs to the organisation. It must be identified, catalogued, protected, and made available to authorised users who need it to do their work. Information that is not governed is information that is at risk of being lost, misused, or degraded in quality. Treating information as an asset means assigning ownership, defining quality standards, and maintaining a current inventory.

### Implications
- All significant data collections must be catalogued with a designated owner
- Information assets must be protected from unauthorised access, loss, or corruption
- The value of information assets must be considered in investment and risk decisions

### Outcomes
- A complete catalogue of Coco Pharmaceuticals' information assets exists and is kept current
- Every information asset has an accountable owner
- Information assets are protected proportionally to their value and sensitivity

### Domain Identifier
ALL

### Authors
Jules Keeper

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Governance Principle

### Display Name
Common Data Definitions Across the Organisation

### Qualified Name
CocoPharma::GovernancePrinciple::CommonDataDefinitions

### Domain Identifier
DATA

### Summary
Coco Pharmaceuticals will maintain shared, agreed definitions for data used across multiple departments, to eliminate ambiguity and enable reliable data sharing.

### Description
One of the most significant barriers to data sharing and integrated analytics is inconsistent data definitions. When different departments define "patient", "batch", "supplier", or "revenue" differently, data cannot be combined without manual reconciliation — which is slow, error-prone, and expensive. Coco Pharmaceuticals will establish and maintain a common glossary of data definitions, agreed across departments, covering what data means, how it is formatted, what valid values it can take, and how frequently it is updated.

### Implications
- A governed business glossary must be maintained and kept current
- Changes to data definitions must go through an agreed approval process
- Systems must use common definitions wherever possible; exceptions must be documented

### Outcomes
- Data can be shared between departments without manual reconciliation
- Analytics based on data from multiple sources produce consistent results
- New staff can quickly understand what data means

### Domain Identifier
DATA

### Authors
Jules Keeper

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Governance Principle

### Display Name
Data is a Shared Organisational Resource

### Qualified Name
CocoPharma::GovernancePrinciple::DataIsASharedOrganisationalResource

### Domain Identifier
DATA

### Summary
Data collected or created by one part of the organisation is available as a shared resource for authorised use by other parts of the organisation.

### Description
In the past, Coco Pharmaceuticals' departments have operated as data silos — each collecting its own data and sharing it reluctantly. This model is incompatible with personalised medicine, which requires research, manufacturing, clinical, and financial data to flow freely between departments. The principle is that data belongs to the organisation, not to the department that collected it. Subject to appropriate privacy and security controls, data collected for one purpose should be available for other authorised purposes.

### Implications
- Data sharing agreements must be established between departments
- Access controls must enable authorised sharing while preventing unauthorised access
- Data consumers must respect the quality and governance standards set by the data owner

### Outcomes
- Research can access manufacturing and clinical data to accelerate drug development
- Finance can access data from all departments for accurate reporting and forecasting
- Duplicate data collection is reduced as authoritative shared sources are established

### Domain Identifier
DATA

### Authors
Jules Keeper

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Governance Principle

### Display Name
Privacy by Design

### Qualified Name
CocoPharma::GovernancePrinciple::PrivacyByDesign

### Domain Identifier
PRIVACY

### Summary
Privacy controls will be built into systems and processes from the start, not added as an afterthought.

### Description
Coco Pharmaceuticals handles patient health data — some of the most sensitive personal data that exists. The principle of privacy by design means that when new systems or processes are designed, privacy protections are considered and built in from the beginning. This is more effective and less costly than retrofitting privacy controls after systems are deployed. It also supports compliance with GDPR, which explicitly requires privacy by design and by default.

### Implications
- All new systems handling personal data must include a privacy impact assessment during design
- Default settings must protect privacy — personal data must not be shared by default
- Data minimisation must be applied — only the personal data that is actually needed should be collected

### Outcomes
- Personal data is protected from unnecessary exposure
- GDPR compliance is built into systems rather than bolted on
- Trust with patients and hospital partners is maintained

### Domain Identifier
PRIVACY

### Authors
Faith Broker

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Governance Principle

### Display Name
Information Use Limited to Approved, Ethical Purposes

### Qualified Name
CocoPharma::GovernancePrinciple::InformationUseLimitedToApprovedEthicalPurposes

### Domain Identifier
ALL

### Summary
Data and information held by Coco Pharmaceuticals will only be used for purposes that have been formally approved and that are consistent with ethical standards.

### Description
Data — particularly patient health data — can be misused in ways that harm individuals or undermine trust. Coco Pharmaceuticals commits to using its information only for purposes that have been reviewed, approved, and documented, and that are consistent with ethical norms and legal requirements. Requests to use data for new purposes must go through an approval process. Staff must understand and respect the boundaries of approved use.

### Implications
- Data processing purposes must be documented and approved before use
- Staff must be trained on approved uses of different data types
- Requests to use data for new purposes must be formally assessed

### Outcomes
- Patient trust is maintained
- The organisation is protected from ethical and legal exposure
- Regulatory requirements around purpose limitation are met

### Domain Identifier
ALL

### Authors
Jules Keeper

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

### 2.2 Governance Obligations

___

## Create Governance Obligation

### Display Name
All Users Must Be Authenticated and Accountable

### Qualified Name
CocoPharma::GovernanceObligation::AllUsersMustBeAuthenticatedAndAccountable

### Domain Identifier
SECURITY

### Summary
Every user who accesses Coco Pharmaceuticals' systems must be uniquely identified and authenticated, and their actions must be recorded.

### Description
Accountability for data access and modification depends on knowing who did what and when. This obligation requires that every person accessing any system holding company data must authenticate with a unique identity. Shared accounts and generic logins are prohibited for systems holding sensitive data. Access must be logged and logs must be retained for a defined period to support audit and incident investigation.

### Implications
- All systems must enforce unique user authentication
- Shared accounts must be eliminated from systems holding company or patient data
- Access logs must be retained according to defined retention schedules

### Outcomes
- All data access can be traced to an individual
- Security incidents can be investigated with complete audit trails
- Regulatory audit requirements can be satisfied

### Domain Identifier
SECURITY

### Authors
Ivor Padlock

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Governance Obligation

### Display Name
Personal Data Must Be Classified and Handled According to Sensitivity

### Qualified Name
CocoPharma::GovernanceObligation::PersonalDataClassifiedBySensitivity

### Domain Identifier
PRIVACY

### Summary
Personal data must be identified, classified by sensitivity, and handled under controls appropriate to its classification.

### Description
Not all personal data carries the same risk. Patient health data is among the most sensitive; employee contact information is less so. This obligation requires that personal data held by Coco Pharmaceuticals is classified according to its sensitivity level, and that each classification has defined handling requirements — covering access controls, retention periods, sharing permissions, and disposal methods. Classification must be documented in the metadata catalog.

### Implications
- A personal data classification scheme must be defined and published
- Systems holding personal data must document what classifications of data they hold
- Staff handling personal data must understand the requirements for each classification

### Outcomes
- Personal data is protected proportionally to its sensitivity
- GDPR obligations around appropriate technical and organisational measures are satisfied
- Data subjects' rights can be exercised because data is identifiable and traceable

### Domain Identifier
PRIVACY

### Authors
Faith Broker

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Governance Obligation

### Display Name
Each Information Collection Must Have a Designated Owner

### Qualified Name
CocoPharma::GovernanceObligation::EachInformationCollectionHasDesignatedOwner

### Domain Identifier
DATA

### Summary
Every significant collection of data held by Coco Pharmaceuticals must have a formally assigned owner who is accountable for its quality and appropriate use.

### Description
Without clear ownership, data quality degrades, access controls become inconsistent, and nobody takes responsibility for problems. This obligation requires that every significant data collection — database, file store, data feed, report — has a designated owner who is accountable for its fitness for purpose. The owner is responsible for setting quality standards, approving access requests, monitoring quality, and escalating issues.

### Implications
- A register of information assets and their owners must be maintained
- Ownership must be formally assigned — not assumed by convention
- Owners must have the authority and capacity to discharge their responsibilities

### Outcomes
- Every data quality issue has a clear escalation path
- Access requests can be approved or denied promptly
- Information assets are maintained to a consistent standard

### Domain Identifier
DATA

### Authors
Jules Keeper

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Governance Obligation

### Display Name
Data Quality Issues Must Be Reported and Resolved

### Qualified Name
CocoPharma::GovernanceObligation::DataQualityIssuesMustBeReportedAndResolved

### Domain Identifier
DATA

### Summary
When data quality problems are detected, they must be reported to the responsible data owner and resolved within defined timeframes.

### Description
Data quality problems that are not detected and corrected can lead to incorrect decisions, failed processes, regulatory non-compliance, and patient harm. This obligation requires that data quality monitoring is in place, that quality failures generate notifications, that notifications reach the responsible owner, and that owners resolve issues within agreed service levels. Unresolved issues must be escalated.

### Implications
- Data quality rules must be defined for all critical data collections
- Automated monitoring must generate notifications when rules are violated
- Escalation paths must be defined for unresolved quality issues

### Outcomes
- Data quality problems are identified and fixed quickly
- Decisions are based on data that meets defined quality standards
- Regulatory requirements for data integrity are met

### Domain Identifier
DATA

### Authors
Jules Keeper

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

### 2.3 Governance Approaches

___

## Create Governance Approach

### Display Name
Metadata-Driven Governance

### Qualified Name
CocoPharma::GovernanceApproach::MetadataDrivenGovernance

### Domain Identifier
ALL

### Summary
Governance definitions, data definitions, and governance controls will be maintained as metadata in Egeria's open metadata catalog, making them discoverable, linked, and actionable.

### Description
Traditional governance programs produce documents that become stale and disconnected from the systems they govern. Coco Pharmaceuticals will use a metadata-driven approach: governance drivers, policies, and controls are recorded as structured metadata in the Egeria open metadata ecosystem. This means they are linked to the actual data assets, systems, and processes they govern. Changes to the governance program are reflected immediately in the catalog. Automated governance actions can be triggered by metadata.

### Implications
- All governance definitions must be created and maintained in the Egeria metadata catalog using tools such as Dr.Egeria, pyegeria, Egeria Advisor, Resource Explorer and the Egeria Portal.
- Governance definitions must be linked to the data assets and processes they govern
- The metadata catalog must be the authoritative source for governance program information

### Outcomes
- Governance definitions are always current and linked to live systems
- Automated governance actions can be triggered based on metadata
- Staff can discover what governance applies to any data asset

### Domain Identifier
ALL

### Authors
Jules Keeper

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Governance Approach

### Display Name
Federated Governance with Central Coordination

### Qualified Name
CocoPharma::GovernanceApproach::FederatedGovernanceWithCentralCoordination

### Domain Identifier
ALL

### Summary
Each governance domain is managed by a specialist domain lead, with central coordination by the Chief Data Officer to ensure consistency and avoid gaps or conflicts.

### Description
Governance across data, security, privacy, IT infrastructure, software development, corporate compliance, and sustainability requires deep specialist expertise in each domain. Coco Pharmaceuticals will therefore federate governance responsibility to domain leads — each empowered to define and enforce governance in their domain. However, the domains are interconnected: a data governance decision affects security; a privacy decision affects data architecture. The Chief Data Officer coordinates across domains, identifies conflicts, and ensures that the overall governance program is consistent and complete.

### Implications
- Domain leads must be formally appointed with clear responsibilities
- A cross-domain governance forum must meet regularly to identify and resolve conflicts
- The CDO has authority to resolve cross-domain conflicts where domain leads cannot agree

### Outcomes
- Governance in each domain benefits from specialist expertise
- Cross-domain issues are identified and resolved promptly
- The overall governance program is coherent and complete

### Domain Identifier
ALL

### Authors
Jules Keeper

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Governance Approach

### Display Name
Automated Quality Monitoring

### Qualified Name
CocoPharma::GovernanceApproach::AutomatedQualityMonitoring

### Domain Identifier
DATA

### Summary
Data quality will be monitored through automated rules that run continuously or on a schedule, generating alerts when quality thresholds are not met.

### Description
Manual data quality checking is slow, expensive, and inconsistent. Coco Pharmaceuticals will implement automated data quality monitoring — rules that check data against defined quality standards and generate alerts when problems are detected. Monitoring will run during low-load periods (e.g. nightly surveys) and continuously where real-time quality is critical. Alerts will be routed to the responsible data steward for investigation and resolution.

### Implications
- Data quality rules must be defined and documented for all critical data collections
- Automated quality scanning must be scheduled and results recorded in the metadata catalog
- Alerting and notification mechanisms must route quality failures to the right person

### Outcomes
- Data quality problems are detected quickly, often before they affect users
- Quality improvement over time can be measured and reported
- Manual quality checking effort is reduced

### Domain Identifier
DATA

### Authors
Jules Keeper

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

## Part 3: Governance Controls

Governance controls define how the governance policies are implemented. They include roles, automated actions, and metrics.

---

### 3.1 Governance Roles

The following governance roles are assigned as part of the Coco Pharmaceuticals governance program. Each role carries accountability for a specific aspect of governance.

| Role | Appointed Person | Domain | Responsibility |
|------|-----------------|--------|---------------|
| Chief Data Officer | Jules Keeper | ALL | Overall governance program leadership and cross-domain coordination |
| Chief Information Security Officer | Ivor Padlock | SECURITY | Security governance — access controls, incident response, cyber resilience |
| Chief Privacy Officer | Faith Broker | PRIVACY | Privacy governance — personal data handling, GDPR compliance |
| Chief Financial Officer (Governance) | Reggie Mint | CORPORATE | Corporate governance — financial reporting, supplier management |
| IT Infrastructure Lead | Gary Geeke | IT_INFRASTRUCTURE | Infrastructure governance — systems, platforms, and networks |
| Senior Software Manager | Polly Tasker | SOFTWARE_DEVELOPMENT | Software development governance — development standards and DevOps |
| Information Architect | Erin Overview | DATA | Data architecture, classification schemes, and subject area definitions |
| Drug Development Lead | Tessa Tube | DATA | Clinical trial data governance and FDA compliance |
| Sustainability Lead | Tom Tally | CORPORATE | Sustainability data collection and reporting governance |

---

___

## Create Governance Role

### Display Name
Chief Data Officer

### Qualified Name
CocoPharma::GovernanceRole::ChiefDataOfficer

### Description
The Chief Data Officer (CDO) is responsible for the overall data governance program at Coco Pharmaceuticals. The CDO defines the data strategy, establishes governance policies and standards, coordinates across all governance domains, chairs the cross-domain governance forum, and is accountable to the board for the quality, availability, and appropriate use of the organisation's information assets.

### Scope
Organisation-wide across all governance domains.

### Headcount
1

### Category
Governance Role

### Search Keywords
- CDO
- data governance
- data strategy
- governance program

### Version Identifier
1.0

___

---

___

## Link Person Role Appointment

### Person
Person::UK::296776

### Person Role
CocoPharma::GovernanceRole::ChiefDataOfficer

___

---

___

## Create Governance Role

### Display Name
Chief Information Security Officer

### Qualified Name
CocoPharma::GovernanceRole::ChiefInformationSecurityOfficer

### Description
The Chief Information Security Officer (CISO) is responsible for Coco Pharmaceuticals' information security governance domain. The CISO defines security policies and standards, oversees access controls and authentication requirements, leads incident response, manages cyber resilience, and ensures compliance with security-related regulations including the Terrorism (Protection of Premises) Act 2025 (Martyn's Law).

### Scope
Security governance domain — all systems, data, and physical events operated by Coco Pharmaceuticals.

### Headcount
1

### Category
Governance Role

### Search Keywords
- CISO
- security governance
- cyber resilience
- information security

### Version Identifier
1.0

___

---

___

## Link Person Role Appointment

### Person
Person::USA::499888

### Person Role
CocoPharma::GovernanceRole::ChiefInformationSecurityOfficer

___

---

___

## Create Governance Role

### Display Name
Chief Privacy Officer

### Qualified Name
CocoPharma::GovernanceRole::ChiefPrivacyOfficer

### Description
The Chief Privacy Officer (CPO) is responsible for Coco Pharmaceuticals' privacy governance domain. The CPO defines privacy policies, oversees the classification and handling of personal data, ensures compliance with GDPR and other data protection regulations, manages data breach notification, and maintains the organisation's data processing register. The CPO works closely with the CDO and CISO to ensure privacy controls are embedded in data and security governance.

### Scope
Privacy governance domain — all personal data processed by Coco Pharmaceuticals, including patient health data, employee data, and clinical trial participant data.

### Headcount
1

### Category
Governance Role

### Search Keywords
- CPO
- privacy governance
- GDPR
- data protection
- personal data

### Version Identifier
1.0

___

---

___

## Link Person Role Appointment

### Person
Person::NL::139870

### Person Role
CocoPharma::GovernanceRole::ChiefPrivacyOfficer

___

---

___

## Create Governance Role

### Display Name
Chief Financial Officer (Corporate Governance Lead)

### Qualified Name
CocoPharma::GovernanceRole::ChiefFinancialOfficer

### Description
The Chief Financial Officer (CFO) holds the corporate governance domain lead role in addition to their primary financial responsibilities. In this governance capacity, the CFO is accountable for supplier master data integrity, procurement governance, financial reporting data quality, and other corporate compliance obligations. The CFO coordinates with the CDO to ensure financial and corporate data assets are appropriately governed.

### Scope
Corporate governance domain — financial data, supplier data, procurement processes, and corporate compliance reporting.

### Headcount
1

### Category
Governance Role

### Search Keywords
- CFO
- corporate governance
- financial governance
- supplier management

### Version Identifier
1.0

___

---

___

## Link Person Role Appointment

### Person
Person::UK::188888

### Person Role
CocoPharma::GovernanceRole::ChiefFinancialOfficer

___

---

___

## Create Governance Role

### Display Name
IT Infrastructure Lead

### Qualified Name
CocoPharma::GovernanceRole::ITInfrastructureLead

### Description
The IT Infrastructure Lead is responsible for the IT infrastructure governance domain. This role defines standards for platforms, networks, and systems; governs the deployment and decommissioning of infrastructure assets; ensures infrastructure changes are managed with appropriate audit trails; and coordinates with the CISO on infrastructure security controls and with the CDO on metadata cataloguing of infrastructure components.

### Scope
IT infrastructure governance domain — all computing platforms, networks, storage systems, and cloud services operated by or on behalf of Coco Pharmaceuticals.

### Headcount
1

### Category
Governance Role

### Search Keywords
- IT governance
- infrastructure governance
- platform management

### Version Identifier
1.0

___

---

___

## Link Person Role Appointment

### Person
Person::NL::199995

### Person Role
CocoPharma::GovernanceRole::ITInfrastructureLead

___

---

___

## Create Governance Role

### Display Name
Senior Software Manager (Software Development Governance Lead)

### Qualified Name
CocoPharma::GovernanceRole::SeniorSoftwareManager

### Description
The Senior Software Manager holds the software development governance domain lead role. This role defines coding standards, DevOps practices, software quality gates, and release governance for Coco Pharmaceuticals' internally developed and maintained software. The role ensures that governance requirements — including audit logging, access controls, and data handling — are embedded in software development practices from the design stage.

### Scope
Software development governance domain — all software developed, maintained, or deployed by Coco Pharmaceuticals' engineering teams.

### Headcount
1

### Category
Governance Role

### Search Keywords
- software governance
- DevOps governance
- development standards

### Version Identifier
1.0

___

---

___

## Link Person Role Appointment

### Person
Person::NL::338575

### Person Role
CocoPharma::GovernanceRole::SeniorSoftwareManager

___

---

___

## Create Governance Role

### Display Name
Information Architect

### Qualified Name
CocoPharma::GovernanceRole::InformationArchitect

### Description
The Information Architect is responsible for defining and maintaining the organisation's data architecture within the data governance domain. This role designs subject area structures, classification schemes, and data zone definitions; works with domain leads to identify authoritative data sources; and oversees the structure of the business glossary and metadata catalog. The Information Architect reports to the CDO and works closely with the Data Designer and Data Steward roles.

### Scope
Data governance domain — data architecture, subject area definitions, classification schemes, metadata catalog structure, and authoritative source identification across the organisation.

### Headcount
1

### Category
Governance Role

### Search Keywords
- information architect
- data architecture
- subject areas
- metadata catalog

### Version Identifier
1.0

___

---

___

## Link Person Role Appointment

### Person
Person::UK::324713

### Person Role
CocoPharma::GovernanceRole::InformationArchitect

___

---

___

## Create Governance Role

### Display Name
Drug Development Lead (Data Governance)

### Qualified Name
CocoPharma::GovernanceRole::DrugDevelopmentLead

### Description
The Drug Development Lead holds governance responsibility for the drug development and clinical trials data domain. This role defines data governance requirements specific to clinical trial conduct, ensures compliance with FDA regulations (including 21 CFR Part 11), oversees the integrity and retention of clinical trial data, and coordinates with the CDO on data quality standards for drug development data. The role works closely with clinical operations, research, and regulatory affairs teams.

### Scope
Drug development governance domain — clinical trial data, research data, drug development records, and regulatory submission data.

### Headcount
1

### Category
Governance Role

### Search Keywords
- drug development governance
- clinical trial governance
- FDA compliance
- clinical data

### Version Identifier
1.0

___

---

___

## Link Person Role Appointment

### Person
Person::USA::302145

### Person Role
CocoPharma::GovernanceRole::DrugDevelopmentLead

___

---

___

## Create Governance Role

### Display Name
Sustainability Lead (Data Governance)

### Qualified Name
CocoPharma::GovernanceRole::SustainabilityLead

### Description
The Sustainability Lead holds governance responsibility for the sustainability data domain. This role defines what sustainability data is collected, from which authoritative sources, with what definitions and quality standards, and how it is reported internally and externally. The role ensures that sustainability reports are accurate, auditable, and traceable to source data. The Sustainability Lead coordinates with the CDO on data definitions and with the CFO on corporate reporting obligations.

### Scope
Sustainability governance domain — environmental data (energy, emissions, waste), social data, supply chain sustainability data, and sustainability reporting outputs.

### Headcount
1

### Category
Governance Role

### Search Keywords
- sustainability governance
- ESG
- sustainability reporting
- environmental data

### Version Identifier
1.0

___

---

___

## Link Person Role Appointment

### Person
Person::UK::896419

### Person Role
CocoPharma::GovernanceRole::SustainabilityLead

___

---

### 3.2 Governance Metrics

___

## Create Governance Metric

### Display Name
Percentage of Data Assets with Designated Owner

### Qualified Name
CocoPharma::GovernanceMetric::PercentageOfDataAssetsWithDesignatedOwner

### Domain Identifier
DATA

### Summary
Measures the proportion of catalogued data assets that have a formally assigned and current owner.

### Description
This metric tracks progress towards the obligation that every information collection has a designated owner. It is calculated as (number of data assets with a current designated owner / total number of catalogued data assets) × 100. The target is 100%. Assets without an owner are at risk of quality degradation and governance failure.

### Implications
- Requires a complete and current inventory of data assets in the catalog
- Requires owner assignments to be kept current as staff change roles

### Outcomes
- Drives accountability for data governance across the organisation
- Identifies gaps where governance attention is needed

### Domain Identifier
DATA

### Authors
Jules Keeper

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Governance Metric

### Display Name
Data Quality Rule Pass Rate

### Qualified Name
CocoPharma::GovernanceMetric::DataQualityRulePassRate

### Domain Identifier
DATA

### Summary
Measures the percentage of automated data quality rule checks that pass within a reporting period.

### Description
This metric aggregates the results of all automated data quality rule checks run against Coco Pharmaceuticals' critical data collections. It is calculated as (number of rule checks that pass / total number of rule checks run) × 100. A declining pass rate indicates degrading data quality. A sustained high pass rate (target: ≥98%) indicates that data quality governance is effective.

### Implications
- Requires automated quality monitoring to be in place and consistently run
- Rule checks must be comprehensive enough to be meaningful

### Outcomes
- Provides an organisation-wide view of data quality health
- Enables governance team to identify domains or systems where quality is declining

### Domain Identifier
DATA

### Authors
Jules Keeper

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Governance Metric

### Display Name
Open Data Quality Issues by Age

### Qualified Name
CocoPharma::GovernanceMetric::OpenDataQualityIssuesByAge

### Domain Identifier
DATA

### Summary
Tracks the number of unresolved data quality issues and their age, to monitor whether issues are being resolved within agreed timeframes.

### Description
When a data quality rule failure generates an alert, the resulting issue must be investigated and resolved. This metric counts open (unresolved) quality issues and categorises them by age: less than 24 hours, 1–7 days, 7–30 days, and over 30 days. Issues outstanding for over 30 days are escalated to the CDO. The target is zero issues outstanding for over 7 days for critical data assets.

### Implications
- Requires a tracking mechanism for quality issue notifications and their resolution status
- Requires defined escalation paths and timeframes

### Outcomes
- Ensures that quality problems are not silently ignored
- Drives accountability for resolution
- Enables identification of systemic quality problems that require deeper intervention

### Domain Identifier
DATA

### Authors
Jules Keeper

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Create Governance Metric

### Display Name
Personal Data Breaches Reported

### Qualified Name
CocoPharma::GovernanceMetric::PersonalDataBreachesReported

### Domain Identifier
PRIVACY

### Summary
Counts the number of personal data breaches identified and reported in a period, including near-misses.

### Description
Under GDPR, Coco Pharmaceuticals must report personal data breaches to the relevant supervisory authority within 72 hours of becoming aware of them, where the breach is likely to result in risk to individuals. This metric counts breaches (and near-misses) detected in each period. The existence of this metric does not mean breaches are acceptable — the aim is zero breaches. However, a metric of zero may also indicate inadequate detection capability. Near-misses must also be reported to enable proactive risk reduction.

### Implications
- Requires breach detection and reporting mechanisms
- Requires clear definition of what constitutes a breach versus a near-miss
- Requires a process for 72-hour GDPR notification

### Outcomes
- GDPR reporting obligations are met
- Near-misses are captured and used to prevent future breaches
- The organisation's privacy risk profile is tracked over time

### Domain Identifier
PRIVACY

### Authors
Faith Broker

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

## Part 4: Governance Links

This section captures the relationships between governance definitions. These links are used by Egeria to connect definitions for navigation and impact analysis.

---

### 4.1 Governance Responses — Drivers linked to Policies

Each link below records a governance policy as a direct response to a governance driver.

___

## Link Governance Response

### Driver
CocoPharma::BusinessImperative::PersonalisedMedicineTransition

### Policy
CocoPharma::GovernancePrinciple::CommonDataDefinitions

### Rationale
Personalised medicine requires that data about patients, treatments, and research can flow between departments without ambiguity. Common data definitions are the foundation for this.

___

---

___

## Link Governance Response

### Driver
CocoPharma::BusinessImperative::PersonalisedMedicineTransition

### Policy
CocoPharma::GovernancePrinciple::DataIsASharedOrganisationalResource

### Rationale
On-demand, personalised treatment decisions require real-time access to data across research, manufacturing, clinical, and finance. Data must be shared — not siloed by department.

___

---

___

## Link Governance Response

### Driver
CocoPharma::BusinessImperative::PersonalisedMedicineTransition

### Policy
CocoPharma::GovernanceApproach::MetadataDrivenGovernance

### Rationale
The scale and pace of the personalised medicine transformation requires governance that is embedded in live systems via metadata, not maintained separately in documents that quickly become stale.

___

---

___

## Link Governance Response

### Driver
CocoPharma::BusinessImperative::CycleTimeReduction

### Policy
CocoPharma::GovernancePrinciple::CommonDataDefinitions

### Rationale
Reducing cycle times is only possible when data can be exchanged between departments without manual reconciliation. Common definitions eliminate that reconciliation overhead.

___

---

___

## Link Governance Response

### Driver
CocoPharma::BusinessImperative::CycleTimeReduction

### Policy
CocoPharma::GovernanceApproach::AutomatedQualityMonitoring

### Rationale
Manual quality checking adds latency to every process that depends on data. Automated monitoring detects problems quickly so that data consumers are not blocked by undetected quality issues.

___

---

___

## Link Governance Response

### Driver
CocoPharma::BusinessImperative::CycleTimeReduction

### Policy
CocoPharma::GovernanceObligation::DataQualityIssuesMustBeReportedAndResolved

### Rationale
Fast cycle times require fast resolution of data quality problems. The obligation to report and resolve issues within defined timeframes directly supports this imperative.

___

---

___

## Link Governance Response

### Driver
CocoPharma::BusinessImperative::CyberResilience

### Policy
CocoPharma::GovernanceObligation::AllUsersMustBeAuthenticatedAndAccountable

### Rationale
Cyber resilience requires knowing who is accessing what. Unique authentication and access logging are the foundation of the audit trail needed for incident investigation and deterrence.

___

---

___

## Link Governance Response

### Driver
CocoPharma::BusinessImperative::SustainabilityReporting

### Policy
CocoPharma::GovernancePrinciple::InformationIsACompanyAsset

### Rationale
Accurate sustainability reporting depends on data being treated as a managed asset — with designated owners, quality standards, and traceability to source.

___

---

___

## Link Governance Response

### Driver
CocoPharma::BusinessImperative::SustainabilityReporting

### Policy
CocoPharma::GovernanceObligation::EachInformationCollectionHasDesignatedOwner

### Rationale
Sustainability reports must be auditable. Designated data owners are accountable for the completeness and accuracy of the underlying data.

___

---

___

## Link Governance Response

### Driver
CocoPharma::Threat::CyberAttackOnOperationsOrData

### Policy
CocoPharma::GovernanceObligation::AllUsersMustBeAuthenticatedAndAccountable

### Rationale
Cyber-attacks frequently exploit weak or shared credentials. Mandatory unique authentication and access logging reduce both the attack surface and the time to detect a breach.

___

---

___

## Link Governance Response

### Driver
CocoPharma::Threat::UnauthorisedDataDisclosure

### Policy
CocoPharma::GovernancePrinciple::PrivacyByDesign

### Rationale
Building privacy controls into systems from the start — rather than adding them later — is the most effective way to prevent inadvertent disclosure of patient and sensitive data.

___

---

___

## Link Governance Response

### Driver
CocoPharma::Threat::UnauthorisedDataDisclosure

### Policy
CocoPharma::GovernanceObligation::PersonalDataClassifiedBySensitivity

### Rationale
Disclosure risk varies by data sensitivity. Classifying personal data enables proportionate controls — the highest-risk data receives the strongest protection.

___

---

___

## Link Governance Response

### Driver
CocoPharma::Threat::UnauthorisedDataDisclosure

### Policy
CocoPharma::GovernancePrinciple::InformationUseLimitedToApprovedEthicalPurposes

### Rationale
Insider misuse of data — a key disclosure vector — is deterred when staff understand that data use is limited to formally approved purposes and that breaches carry consequences.

___

---

___

## Link Governance Response

### Driver
CocoPharma::Threat::FraudulentSupplierActivity

### Policy
CocoPharma::GovernanceObligation::EachInformationCollectionHasDesignatedOwner

### Rationale
Supplier fraud is enabled when supplier master data has no clear owner and changes can be made without scrutiny. Designated ownership ensures that supplier data changes require authorisation.

___

---

___

## Link Governance Response

### Driver
CocoPharma::Threat::LossOfKeyTalentAndKnowledge

### Policy
CocoPharma::GovernanceApproach::MetadataDrivenGovernance

### Rationale
When governance knowledge is captured as structured metadata in the catalog — rather than held informally in people's heads — it survives staff departures and is accessible to successors.

___

---

___

## Link Governance Response

### Driver
CocoPharma::Threat::LossOfKeyTalentAndKnowledge

### Policy
CocoPharma::GovernancePrinciple::CommonDataDefinitions

### Rationale
Documented, agreed data definitions in a shared catalog are the antidote to critical data knowledge being lost when key staff leave.

___

---

___

## Link Governance Response

### Driver
CocoPharma::Regulation::GDPR

### Policy
CocoPharma::GovernancePrinciple::PrivacyByDesign

### Rationale
GDPR Article 25 explicitly requires data protection by design and by default. The Privacy by Design principle directly implements this legal requirement.

___

---

___

## Link Governance Response

### Driver
CocoPharma::Regulation::GDPR

### Policy
CocoPharma::GovernanceObligation::PersonalDataClassifiedBySensitivity

### Rationale
GDPR requires appropriate technical and organisational measures proportionate to the risk. Classification by sensitivity is the mechanism for determining what measures are appropriate.

___

---

___

## Link Governance Response

### Driver
CocoPharma::Regulation::GDPR

### Policy
CocoPharma::GovernancePrinciple::InformationUseLimitedToApprovedEthicalPurposes

### Rationale
GDPR's purpose limitation principle (Article 5(1)(b)) requires that personal data is only processed for the specific purposes for which it was collected. This principle gives effect to that requirement.

___

---

___

## Link Governance Response

### Driver
CocoPharma::Regulation::FDAClinicalTrialRegulations

### Policy
CocoPharma::GovernanceObligation::DataQualityIssuesMustBeReportedAndResolved

### Rationale
FDA regulations require that clinical trial data is accurate and that deviations are documented and investigated. The obligation to report and resolve quality issues ensures this standard is met.

___

---

___

## Link Governance Response

### Driver
CocoPharma::Regulation::FDAClinicalTrialRegulations

### Policy
CocoPharma::GovernanceObligation::AllUsersMustBeAuthenticatedAndAccountable

### Rationale
21 CFR Part 11 requires that electronic records have a reliable audit trail tied to individual users. Mandatory unique authentication is the control that delivers this.

___

---

___

## Link Governance Response

### Driver
CocoPharma::Regulation::GoodManufacturingPractice

### Policy
CocoPharma::GovernanceObligation::DataQualityIssuesMustBeReportedAndResolved

### Rationale
GMP requires that deviations from manufacturing standards are detected, documented, and investigated. The obligation to report and resolve data quality issues is the governance expression of this requirement.

___

---

___

## Link Governance Response

### Driver
CocoPharma::Regulation::GoodManufacturingPractice

### Policy
CocoPharma::GovernanceObligation::EachInformationCollectionHasDesignatedOwner

### Rationale
GMP traceability requirements depend on knowing who is accountable for each category of manufacturing data. Designated ownership provides that accountability.

___

---

___

## Link Governance Response

### Driver
CocoPharma::Regulation::MartynsLaw

### Policy
CocoPharma::GovernanceObligation::AllUsersMustBeAuthenticatedAndAccountable

### Rationale
Martyn's Law requires a designated Responsible Person for event security compliance. The obligation for accountability and audit trails supports the record-keeping requirements of this role.

___

---

### 4.2 Governance Mechanisms — Policies linked to Controls

Each link below connects a governance policy to the metric or control that implements it.

___

## Link Governance Mechanism

### Policy
CocoPharma::GovernanceObligation::EachInformationCollectionHasDesignatedOwner

### Mechanism
CocoPharma::GovernanceMetric::PercentageOfDataAssetsWithDesignatedOwner

### Rationale
This metric directly measures compliance with the obligation. A score below 100% identifies assets that lack governance accountability.

___

---

___

## Link Governance Mechanism

### Policy
CocoPharma::GovernanceObligation::DataQualityIssuesMustBeReportedAndResolved

### Mechanism
CocoPharma::GovernanceMetric::OpenDataQualityIssuesByAge

### Rationale
Tracking open issues by age measures whether the obligation to resolve quality problems within defined timeframes is being met. Issues ageing beyond the threshold are a direct compliance indicator.

___

---

___

## Link Governance Mechanism

### Policy
CocoPharma::GovernanceApproach::AutomatedQualityMonitoring

### Mechanism
CocoPharma::GovernanceMetric::DataQualityRulePassRate

### Rationale
The pass rate is the primary output metric for automated quality monitoring. A high and sustained pass rate confirms the approach is effective; a declining rate signals systemic quality problems.

___

---

___

## Link Governance Mechanism

### Policy
CocoPharma::GovernanceApproach::AutomatedQualityMonitoring

### Mechanism
CocoPharma::GovernanceMetric::OpenDataQualityIssuesByAge

### Rationale
Automated monitoring generates the issues tracked by this metric. Together, the approach and the metric form a detect-and-resolve feedback loop for data quality governance.

___

---

___

## Link Governance Mechanism

### Policy
CocoPharma::GovernanceObligation::PersonalDataClassifiedBySensitivity

### Mechanism
CocoPharma::GovernanceMetric::PersonalDataBreachesReported

### Rationale
Proper classification and proportionate controls are the primary means of preventing breaches. This metric measures the outcome — breach occurrence — as an indicator of whether classification controls are effective.

___

---

___

## Link Governance Mechanism

### Policy
CocoPharma::GovernancePrinciple::PrivacyByDesign

### Mechanism
CocoPharma::GovernanceMetric::PersonalDataBreachesReported

### Rationale
Privacy by Design aims to eliminate breach risk through proactive system design. Reported breaches (and near-misses) are the key outcome measure for this principle.

___

---

### 4.3 Peer Driver Links — Related Governance Drivers

These links connect governance drivers that are closely related, helping readers understand how threats, imperatives, and regulations reinforce each other.

___

## Link Governance Drivers

### Governance Driver 1
CocoPharma::BusinessImperative::PersonalisedMedicineTransition

### Governance Driver 2
CocoPharma::BusinessImperative::CycleTimeReduction

### Description
Both imperatives arise from the same strategic transformation. Personalised medicine requires faster cycles; cycle time reduction is a prerequisite for personalised medicine to be operationally viable.

___

---

___

## Link Governance Drivers

### Governance Driver 1
CocoPharma::BusinessImperative::CyberResilience

### Governance Driver 2
CocoPharma::Threat::CyberAttackOnOperationsOrData

### Description
The Cyber Resilience imperative is a direct organisational response to the Cyber-Attack threat. They represent the same risk viewed from the positive (what we must achieve) and negative (what we must prevent) perspectives.

___

---

___

## Link Governance Drivers

### Governance Driver 1
CocoPharma::Regulation::GDPR

### Governance Driver 2
CocoPharma::Threat::UnauthorisedDataDisclosure

### Description
GDPR and the unauthorised disclosure threat are closely linked: the regulation exists precisely because unauthorised disclosure of personal data causes harm. Compliance with GDPR is a key mitigant of the threat.

___

---

___

## Link Governance Drivers

### Governance Driver 1
CocoPharma::Regulation::FDAClinicalTrialRegulations

### Governance Driver 2
CocoPharma::Regulation::GoodManufacturingPractice

### Description
Both regulations apply to Coco Pharmaceuticals' drug development and manufacturing activities. They share common themes of data integrity, audit trails, and traceability, and are often assessed together.

___

---

### 4.4 Peer Policy Links — Related Governance Policies

These links connect governance policies that reinforce or depend on each other.

___

## Link Governance Policies

### Governance Policy 1
CocoPharma::GovernancePrinciple::CommonDataDefinitions

### Governance Policy 2
CocoPharma::GovernancePrinciple::DataIsASharedOrganisationalResource

### Description
These principles are mutually dependent: data cannot be shared reliably without common definitions, and common definitions only add value when data is genuinely shared across the organisation.

___

---

___

## Link Governance Policies

### Governance Policy 1
CocoPharma::GovernancePrinciple::InformationIsACompanyAsset

### Governance Policy 2
CocoPharma::GovernanceObligation::EachInformationCollectionHasDesignatedOwner

### Description
Ownership is the operational expression of the asset principle. Recognising information as an asset (principle) demands that someone is accountable for it (obligation).

___

---

___

## Link Governance Policies

### Governance Policy 1
CocoPharma::GovernancePrinciple::PrivacyByDesign

### Governance Policy 2
CocoPharma::GovernanceObligation::PersonalDataClassifiedBySensitivity

### Description
Privacy by Design specifies the approach; data classification provides the mechanism for applying proportionate controls. Together they form the core of Coco Pharmaceuticals' privacy governance.

___

---

___

## Link Governance Policies

### Governance Policy 1
CocoPharma::GovernanceApproach::MetadataDrivenGovernance

### Governance Policy 2
CocoPharma::GovernanceApproach::AutomatedQualityMonitoring

### Description
Both approaches depend on the same metadata infrastructure. Automated quality monitoring is only possible when data assets, quality rules, and owners are captured as metadata in the catalog.

___

---

___

## Link Governance Policies

### Governance Policy 1
CocoPharma::GovernanceApproach::FederatedGovernanceWithCentralCoordination

### Governance Policy 2
CocoPharma::GovernanceApproach::MetadataDrivenGovernance

### Description
Federated governance requires a shared view of governance definitions across domains. The metadata catalog — delivered by the Metadata-Driven Governance approach — is the coordination layer that makes federation practical.

___

---

## Part 5: External References

This section defines external web resources — regulation texts, regulatory body home pages, and Egeria documentation — and links them to the governance definitions they relate to.

---

### 5.1 External Reference Definitions

___

## Create External Reference

### Display Name
GDPR — Full Regulation Text (EUR-Lex)

### Qualified Name
CocoPharma::ExternalReference::GDPR::EURLex

### Reference Title
Regulation (EU) 2016/679 of the European Parliament and of the Council

### Organization
Publications Office of the European Union

### Reference Abstract
The full text of the General Data Protection Regulation (GDPR), Regulation (EU) 2016/679, as published in the Official Journal of the European Union. This is the authoritative legal source for all GDPR obligations referenced in this governance program.

### Sources
| Parameter Name | Parameter Value |
|---|---|
| URL | https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32016R0679 |

### Category
Regulation

### Content Status
ACTIVE

___

---

___

## Create External Reference

### Display Name
ICO — Information Commissioner's Office

### Qualified Name
CocoPharma::ExternalReference::ICO::HomePage

### Reference Title
ICO — The UK's independent authority set up to uphold information rights

### Organization
Information Commissioner's Office (ICO)

### Reference Abstract
The UK supervisory authority for data protection. The ICO provides guidance on GDPR compliance, handles complaints, and can investigate and fine organisations for data protection breaches. The ICO website includes practical guidance on implementing GDPR requirements.

### Sources
| Parameter Name | Parameter Value |
|---|---|
| URL | https://ico.org.uk/ |
| GDPR Guidance | https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/ |

### Category
Regulatory Body

### Content Status
ACTIVE

___

---

___

## Create External Reference

### Display Name
FDA — Clinical Trials and Human Subject Protection

### Qualified Name
CocoPharma::ExternalReference::FDA::ClinicalTrials

### Reference Title
FDA Clinical Trials and Human Subject Protection

### Organization
US Food and Drug Administration (FDA)

### Reference Abstract
The FDA's main resource page for clinical trial regulations, guidance documents, and information on human subject protection. Covers the regulatory framework that applies to Coco Pharmaceuticals' drug development activities.

### Sources
| Parameter Name | Parameter Value |
|---|---|
| URL | https://www.fda.gov/science-research/clinical-trials-and-human-subject-protection |

### Category
Regulatory Guidance

### Content Status
ACTIVE

___

---

___

## Create External Reference

### Display Name
FDA 21 CFR Part 11 — Electronic Records and Signatures

### Qualified Name
CocoPharma::ExternalReference::FDA::21CFRPart11

### Reference Title
21 CFR Part 11 — Electronic Records; Electronic Signatures

### Organization
US Food and Drug Administration (FDA)

### Reference Abstract
The specific FDA regulation governing electronic records and electronic signatures. Part 11 sets out the requirements for audit trails, access controls, and system validation that Coco Pharmaceuticals must meet for systems holding clinical trial data. Referenced directly by the FDA Clinical Trial Regulations governance driver.

### Sources
| Parameter Name | Parameter Value |
|---|---|
| URL | https://www.ecfr.gov/current/title-21/chapter-I/subchapter-A/part-11 |

### Category
Regulation

### Content Status
ACTIVE

___

---

___

## Create External Reference

### Display Name
EudraLex Volume 4 — EU Guidelines for Good Manufacturing Practice

### Qualified Name
CocoPharma::ExternalReference::EMA::GMPGuidelines

### Reference Title
EudraLex — The Rules Governing Medicinal Products in the European Union, Volume 4

### Organization
European Commission — Directorate-General for Health and Food Safety

### Reference Abstract
Volume 4 of EudraLex contains the EU Guidelines for Good Manufacturing Practice for Medicinal Products for Human and Veterinary Use. This is the primary reference for GMP obligations applicable to Coco Pharmaceuticals' EU manufacturing operations.

### Sources
| Parameter Name | Parameter Value |
|---|---|
| URL | https://health.ec.europa.eu/medicinal-products/eudralex/eudralex-volume-4_en |

### Category
Regulatory Guidance

### Content Status
ACTIVE

___

---

___

## Create External Reference

### Display Name
EMA — European Medicines Agency

### Qualified Name
CocoPharma::ExternalReference::EMA::HomePage

### Reference Title
European Medicines Agency

### Organization
European Medicines Agency (EMA)

### Reference Abstract
The EMA is the European Union agency responsible for the scientific evaluation, supervision, and safety monitoring of medicines. It publishes GMP inspection findings, guidance documents, and regulatory decisions relevant to Coco Pharmaceuticals' EU drug development and manufacturing activities.

### Sources
| Parameter Name | Parameter Value |
|---|---|
| URL | https://www.ema.europa.eu/ |
| GMP Inspections | https://www.ema.europa.eu/en/human-regulatory-overview/research-and-development/compliance-and-inspection/good-manufacturing-practice |

### Category
Regulatory Body

### Content Status
ACTIVE

___

---

___

## Create External Reference

### Display Name
MHRA — Medicines and Healthcare products Regulatory Agency

### Qualified Name
CocoPharma::ExternalReference::MHRA::HomePage

### Reference Title
Medicines and Healthcare products Regulatory Agency

### Organization
Medicines and Healthcare products Regulatory Agency (MHRA)

### Reference Abstract
The MHRA is the UK government agency responsible for regulating medicines, medical devices, and blood components. It is the relevant GMP regulatory authority for Coco Pharmaceuticals' UK manufacturing operations following Brexit.

### Sources
| Parameter Name | Parameter Value |
|---|---|
| URL | https://www.gov.uk/government/organisations/medicines-and-healthcare-products-regulatory-agency |
| GMP Guidance | https://www.gov.uk/guidance/good-manufacturing-practice-and-good-distribution-practice |

### Category
Regulatory Body

### Content Status
ACTIVE

___

---

___

## Create External Reference

### Display Name
Martyn's Law — UK Government Protect Duty Guidance

### Qualified Name
CocoPharma::ExternalReference::MartynsLaw::GovUK

### Reference Title
Protect Duty — Terrorism (Protection of Premises) Act 2025

### Organization
UK Home Office

### Reference Abstract
The UK government's official guidance on the Terrorism (Protection of Premises) Act 2025 (Martyn's Law), including information on which premises and events are in scope, what the standard and enhanced tier requirements are, the role of the Responsible Person, and the compliance timeline (enforcement from 2027).

### Sources
| Parameter Name | Parameter Value |
|---|---|
| URL | https://www.gov.uk/government/collections/protect-duty |
| Act Text | https://www.legislation.gov.uk/ukpga/2025/10/contents |

### Category
Regulation

### Content Status
ACTIVE

___

---

___

## Create External Reference

### Display Name
Security Industry Authority (SIA)

### Qualified Name
CocoPharma::ExternalReference::SIA::HomePage

### Reference Title
Security Industry Authority

### Organization
Security Industry Authority (SIA)

### Reference Abstract
The SIA is the UK body responsible for regulating the private security industry and, under Martyn's Law, for supporting compliance with the Terrorism (Protection of Premises) Act 2025. The SIA provides guidance for Responsible Persons and publishes updates on enforcement activity.

### Sources
| Parameter Name | Parameter Value |
|---|---|
| URL | https://www.sia.homeoffice.gov.uk/ |

### Category
Regulatory Body

### Content Status
ACTIVE

___

---

___

## Create External Reference

### Display Name
Egeria — Governance Program Planning Guide

### Qualified Name
CocoPharma::ExternalReference::Egeria::GovernanceProgramGuide

### Reference Title
Planning a Governance Program with Egeria

### Organization
ODPi / LF AI & Data — Egeria Project

### Reference Abstract
The Egeria documentation page describing how to plan and implement a governance program using Egeria's open metadata capabilities. Covers governance domains, governance definitions, and the relationship between drivers, policies, and controls — the framework used to structure this document.

### Sources
| Parameter Name | Parameter Value |
|---|---|
| URL | https://egeria-project.org/guides/planning/governance-program/overview/ |

### Category
Egeria Documentation

### Content Status
ACTIVE

___

---

___

## Create External Reference

### Display Name
Egeria — Governance Officer View Service

### Qualified Name
CocoPharma::ExternalReference::Egeria::GovernanceOfficerAPI

### Reference Title
Governance Officer OMVS — API Reference

### Organization
ODPi / LF AI & Data — Egeria Project

### Reference Abstract
Documentation for the Egeria Governance Officer Open Metadata View Service (OMVS), the API used to create, update, and query governance definitions (drivers, policies, controls, and their relationships) in the Egeria metadata catalog. The Dr.Egeria templates in this document map to this API.

### Sources
| Parameter Name | Parameter Value |
|---|---|
| URL | https://egeria-project.org/services/omvs/governance-officer/overview/ |

### Category
Egeria Documentation

### Content Status
ACTIVE

___

---

___

## Create External Reference

### Display Name
Egeria — Open Metadata Types for Governance Definitions

### Qualified Name
CocoPharma::ExternalReference::Egeria::GovernanceDefinitionTypes

### Reference Title
Open Metadata Type — Governance Definitions (Area 4)

### Organization
ODPi / LF AI & Data — Egeria Project

### Reference Abstract
The Egeria documentation page describing the open metadata types that underpin governance definitions, including GovernanceDriver, BusinessImperative, Threat, Regulation, GovernancePrinciple, GovernanceObligation, GovernanceApproach, and GovernanceMetric. Understanding these types helps relate the definitions in this document to the underlying metadata model.

### Sources
| Parameter Name | Parameter Value |
|---|---|
| Governance Definitions | https://egeria-project.org/types/4/0401-Governance-Definitions/ |
| Governance Drivers | https://egeria-project.org/types/4/0405-Governance-Drivers/ |
| Governance Responses | https://egeria-project.org/types/4/0415-Governance-Responses/ |
| Governance Controls | https://egeria-project.org/types/4/0420-Governance-Controls/ |
| Governance Metrics | https://egeria-project.org/types/4/0450-Governance-Rollout/ |

### Category
Egeria Documentation

### Content Status
ACTIVE

___

---

___

## Create External Reference

### Display Name
Egeria — Dr.Egeria User Interface

### Qualified Name
CocoPharma::ExternalReference::Egeria::DrEgeria

### Reference Title
Dr.Egeria — Markdown-Driven Metadata Authoring Interface

### Organization
ODPi / LF AI & Data — Egeria Project

### Reference Abstract
Documentation for Dr.Egeria, the Egeria user interface that interprets Markdown files (like this one) using Dr.Egeria templates to create and update metadata in the Egeria catalog. The templates in the Governance Officer subdirectory are used to load the governance definitions in this document into the live metadata catalog.

### Sources
| Parameter Name | Parameter Value |
|---|---|
| URL | https://egeria-project.org/user-interfaces/dr-egeria/overview/ |

### Category
Egeria Documentation

### Content Status
ACTIVE

___

---

___

## Create External Reference

### Display Name
Egeria — Coco Pharmaceuticals Data Strategy Scenario

### Qualified Name
CocoPharma::ExternalReference::Egeria::CocoDataStrategy

### Reference Title
Coco Pharmaceuticals — Defining the Data Strategy

### Organization
ODPi / LF AI & Data — Egeria Project

### Reference Abstract
The Egeria project's worked example of defining a data strategy for the fictional Coco Pharmaceuticals organisation. This scenario is the primary source material for the governance definitions in this document and provides narrative context for why each driver, policy, and control exists.

### Sources
| Parameter Name | Parameter Value |
|---|---|
| Data Strategy Overview | https://egeria-project.org/practices/coco-pharmaceuticals/scenarios/defining-the-data-strategy/overview/ |
| Governance Program | https://egeria-project.org/practices/coco-pharmaceuticals/scenarios/creating-data-governance-program/overview/ |
| Building the Team | https://egeria-project.org/practices/coco-pharmaceuticals/scenarios/building-the-governance-team/overview/ |
| Multi-Faceted Governance | https://egeria-project.org/practices/coco-pharmaceuticals/scenarios/defining-multi-faceted-governance/overview/ |

### Category
Egeria Documentation

### Content Status
ACTIVE

___

---

### 5.2 External Reference Links

___

## Link External Reference

### Element Name
CocoPharma::Regulation::GDPR

### External Reference
CocoPharma::ExternalReference::GDPR::EURLex

### Description
Full text of the regulation that this governance driver is based on.

___

---

___

## Link External Reference

### Element Name
CocoPharma::Regulation::GDPR

### External Reference
CocoPharma::ExternalReference::ICO::HomePage

### Description
The UK supervisory authority for GDPR. The ICO's guidance and enforcement decisions are directly relevant to Coco Pharmaceuticals' GDPR compliance obligations.

___

---

___

## Link External Reference

### Element Name
CocoPharma::GovernancePrinciple::PrivacyByDesign

### External Reference
CocoPharma::ExternalReference::ICO::HomePage

### Description
The ICO publishes practical guidance on implementing privacy by design that informs how this principle is applied at Coco Pharmaceuticals.

___

---

___

## Link External Reference

### Element Name
CocoPharma::GovernanceObligation::PersonalDataClassifiedBySensitivity

### External Reference
CocoPharma::ExternalReference::ICO::HomePage

### Description
The ICO provides guidance on classifying and handling personal data that informs the implementation of this obligation.

___

---

___

## Link External Reference

### Element Name
CocoPharma::Regulation::FDAClinicalTrialRegulations

### External Reference
CocoPharma::ExternalReference::FDA::ClinicalTrials

### Description
The FDA's primary resource page for the clinical trial regulatory framework that this governance driver is based on.

___

---

___

## Link External Reference

### Element Name
CocoPharma::Regulation::FDAClinicalTrialRegulations

### External Reference
CocoPharma::ExternalReference::FDA::21CFRPart11

### Description
21 CFR Part 11 is the specific regulation governing electronic records and audit trails for clinical trial data — a core requirement referenced by this governance driver.

___

---

___

## Link External Reference

### Element Name
CocoPharma::Regulation::GoodManufacturingPractice

### External Reference
CocoPharma::ExternalReference::EMA::GMPGuidelines

### Description
EudraLex Volume 4 is the primary EU source for the Good Manufacturing Practice requirements that this governance driver is based on.

___

---

___

## Link External Reference

### Element Name
CocoPharma::Regulation::GoodManufacturingPractice

### External Reference
CocoPharma::ExternalReference::EMA::HomePage

### Description
The EMA is the EU regulatory authority for GMP compliance and publishes inspection findings and updated guidance.

___

---

___

## Link External Reference

### Element Name
CocoPharma::Regulation::GoodManufacturingPractice

### External Reference
CocoPharma::ExternalReference::MHRA::HomePage

### Description
The MHRA is the UK regulatory authority for GMP compliance, relevant to Coco Pharmaceuticals' UK manufacturing operations.

___

---

___

## Link External Reference

### Element Name
CocoPharma::Regulation::MartynsLaw

### External Reference
CocoPharma::ExternalReference::MartynsLaw::GovUK

### Description
The official UK government guidance on the Terrorism (Protection of Premises) Act 2025 that this governance driver is based on.

___

---

___

## Link External Reference

### Element Name
CocoPharma::Regulation::MartynsLaw

### External Reference
CocoPharma::ExternalReference::SIA::HomePage

### Description
The SIA is the enforcement body for Martyn's Law and the primary point of contact for compliance guidance.

___

---

___

## Link External Reference

### Element Name
CocoPharma::GovernanceApproach::MetadataDrivenGovernance

### External Reference
CocoPharma::ExternalReference::Egeria::GovernanceOfficerAPI

### Description
The Governance Officer API is the Egeria service through which this approach is implemented — all governance definitions are created and maintained via this API.

___

---

___

## Link External Reference

### Element Name
CocoPharma::GovernanceApproach::MetadataDrivenGovernance

### External Reference
CocoPharma::ExternalReference::Egeria::DrEgeria

### Description
Dr.Egeria is the authoring interface used to load governance definitions from Markdown documents (like this one) into the Egeria catalog, directly implementing this approach.

___

---

___

## Link External Reference

### Element Name
CocoPharma::GovernanceApproach::MetadataDrivenGovernance

### External Reference
CocoPharma::ExternalReference::Egeria::GovernanceProgramGuide

### Description
The Egeria governance program planning guide describes the framework and best practices that underpin this approach.

___

---

___

## Link External Reference

### Element Name
CocoPharma::BusinessImperative::PersonalisedMedicineTransition

### External Reference
CocoPharma::ExternalReference::Egeria::CocoDataStrategy

### Description
The Coco Pharmaceuticals data strategy scenario on the Egeria website provides the narrative context and background for this business imperative.

___

---

___

## Link External Reference

### Element Name
CocoPharma::GovernanceApproach::FederatedGovernanceWithCentralCoordination

### External Reference
CocoPharma::ExternalReference::Egeria::GovernanceProgramGuide

### Description
Egeria's governance program guide describes the federated, multi-domain governance model that this approach implements.

___

---

___

## Link External Reference

### Element Name
CocoPharma::GovernanceMetric::DataQualityRulePassRate

### External Reference
CocoPharma::ExternalReference::Egeria::GovernanceDefinitionTypes

### Description
The GovernanceMetric open metadata type definition describes how this metric is represented and linked in the Egeria catalog.

___

---

## Part 6: Governance Folios

A folio is a collection of governance definitions that a specific role is responsible for. Each folio groups the definitions owned or authored by a domain lead, making it easy to find all the governance work associated with a given role.

---

### 6.1 Folio Definitions

___

## Create Folio

### Display Name
Chief Data Officer — Governance Folio

### Qualified Name
CocoPharma::Folio::ChiefDataOfficer

### Description
The governance definitions owned by the Chief Data Officer (Jules Keeper). This folio covers the cross-cutting data governance program: the strategic business imperatives driving the transformation, the foundational data governance principles and obligations, the approaches that define how governance is practised, and the metrics used to measure effectiveness.

### Purpose
Provides Jules Keeper with a single view of all governance definitions she is responsible for authoring, maintaining, and enforcing across the organisation.

### Category
Governance Folio

### Authors
Jules Keeper

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Link Assignment Scope

### Assigned Actor
CocoPharma::GovernanceRole::ChiefDataOfficer

### Assignment Type
Governance Folio

### Scope Element
CocoPharma::Folio::ChiefDataOfficer

### Description
Assigns the Chief Data Officer role responsibility for all governance definitions collected in the Chief Data Officer Governance Folio.

___

---

___

## Create Folio

### Display Name
Chief Information Security Officer — Governance Folio

### Qualified Name
CocoPharma::Folio::ChiefInformationSecurityOfficer

### Description
The governance definitions owned by the Chief Information Security Officer (Ivor Padlock). This folio covers the security domain: the business imperative for cyber resilience, the cyber-attack threat, Martyn's Law, and the obligation for universal user authentication and accountability.

### Purpose
Provides Ivor Padlock with a single view of all security governance definitions he is responsible for authoring, maintaining, and enforcing.

### Category
Governance Folio

### Authors
Ivor Padlock

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Link Assignment Scope

### Assigned Actor
CocoPharma::GovernanceRole::ChiefInformationSecurityOfficer

### Assignment Type
Governance Folio

### Scope Element
CocoPharma::Folio::ChiefInformationSecurityOfficer

### Description
Assigns the Chief Information Security Officer role responsibility for all governance definitions collected in the Chief Information Security Officer Governance Folio.

___

---

___

## Create Folio

### Display Name
Chief Privacy Officer — Governance Folio

### Qualified Name
CocoPharma::Folio::ChiefPrivacyOfficer

### Description
The governance definitions owned by the Chief Privacy Officer (Faith Broker). This folio covers the privacy domain: the unauthorised data disclosure threat, the GDPR regulation, the Privacy by Design principle, the obligation to classify personal data by sensitivity, and the metric tracking personal data breaches.

### Purpose
Provides Faith Broker with a single view of all privacy governance definitions she is responsible for authoring, maintaining, and enforcing.

### Category
Governance Folio

### Authors
Faith Broker

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Link Assignment Scope

### Assigned Actor
CocoPharma::GovernanceRole::ChiefPrivacyOfficer

### Assignment Type
Governance Folio

### Scope Element
CocoPharma::Folio::ChiefPrivacyOfficer

### Description
Assigns the Chief Privacy Officer role responsibility for all governance definitions collected in the Chief Privacy Officer Governance Folio.

___

---

___

## Create Folio

### Display Name
Chief Financial Officer — Governance Folio

### Qualified Name
CocoPharma::Folio::ChiefFinancialOfficer

### Description
The governance definitions owned by the Chief Financial Officer (Reggie Mint) in his capacity as the corporate governance domain lead. This folio currently covers the fraudulent supplier activity threat and will expand as corporate governance controls are defined.

### Purpose
Provides Reggie Mint with a single view of all corporate governance definitions he is responsible for authoring, maintaining, and enforcing.

### Category
Governance Folio

### Authors
Reggie Mint

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Link Assignment Scope

### Assigned Actor
CocoPharma::GovernanceRole::ChiefFinancialOfficer

### Assignment Type
Governance Folio

### Scope Element
CocoPharma::Folio::ChiefFinancialOfficer

### Description
Assigns the Chief Financial Officer role responsibility for all governance definitions collected in the Chief Financial Officer Governance Folio.

___

---

___

## Create Folio

### Display Name
Drug Development Lead — Governance Folio

### Qualified Name
CocoPharma::Folio::DrugDevelopmentLead

### Description
The governance definitions owned by the Drug Development Lead (Tessa Tube). This folio covers the FDA clinical trial regulatory requirements and will expand to include clinical data governance controls, certification types, and data processing purposes as the governance program matures.

### Purpose
Provides Tessa Tube with a single view of all drug development governance definitions she is responsible for authoring, maintaining, and enforcing.

### Category
Governance Folio

### Authors
Tessa Tube

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Link Assignment Scope

### Assigned Actor
CocoPharma::GovernanceRole::DrugDevelopmentLead

### Assignment Type
Governance Folio

### Scope Element
CocoPharma::Folio::DrugDevelopmentLead

### Description
Assigns the Drug Development Lead role responsibility for all governance definitions collected in the Drug Development Lead Governance Folio.

___

---

___

## Create Folio

### Display Name
Sustainability Lead — Governance Folio

### Qualified Name
CocoPharma::Folio::SustainabilityLead

### Description
The governance definitions owned by the Sustainability Lead (Tom Tally). This folio currently covers the sustainability reporting business imperative and will expand to include sustainability data collection standards, authoritative data sources, and reporting metrics as the sustainability governance program develops.

### Purpose
Provides Tom Tally with a single view of all sustainability governance definitions he is responsible for authoring, maintaining, and enforcing.

### Category
Governance Folio

### Authors
Tom Tally

### Version Identifier
1.0

### Content Status
ACTIVE

___

---

___

## Link Assignment Scope

### Assigned Actor
CocoPharma::GovernanceRole::SustainabilityLead

### Assignment Type
Governance Folio

### Scope Element
CocoPharma::Folio::SustainabilityLead

### Description
Assigns the Sustainability Lead role responsibility for all governance definitions collected in the Sustainability Lead Governance Folio.

___

---

### 6.2 Folio Members

---

#### Chief Data Officer Folio Members

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefDataOfficer

### Element Id
CocoPharma::BusinessImperative::PersonalisedMedicineTransition

### Membership Rationale
The CDO is accountable for ensuring data governance supports Coco Pharmaceuticals' strategic shift to personalised medicine.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefDataOfficer

### Element Id
CocoPharma::BusinessImperative::CycleTimeReduction

### Membership Rationale
Reducing cycle times depends on well-governed, high-quality data flowing between departments — a core CDO responsibility.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefDataOfficer

### Element Id
CocoPharma::Threat::LossOfKeyTalentAndKnowledge

### Membership Rationale
The CDO owns the response to this threat: ensuring governance knowledge is captured as documented metadata rather than held informally by individuals.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefDataOfficer

### Element Id
CocoPharma::Regulation::GoodManufacturingPractice

### Membership Rationale
GMP data integrity and traceability requirements sit within the CDO's data governance remit, in coordination with the Drug Development Lead.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefDataOfficer

### Element Id
CocoPharma::GovernancePrinciple::InformationIsACompanyAsset

### Membership Rationale
This foundational principle is authored and championed by the CDO as the basis for the entire data governance program.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefDataOfficer

### Element Id
CocoPharma::GovernancePrinciple::CommonDataDefinitions

### Membership Rationale
Establishing and maintaining common data definitions is a core CDO responsibility.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefDataOfficer

### Element Id
CocoPharma::GovernancePrinciple::DataIsASharedOrganisationalResource

### Membership Rationale
The CDO is the sponsor of the cultural and governance shift from data silos to shared organisational data.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefDataOfficer

### Element Id
CocoPharma::GovernancePrinciple::InformationUseLimitedToApprovedEthicalPurposes

### Membership Rationale
Ensuring data is only used for approved, ethical purposes is a cross-cutting CDO responsibility spanning all domains.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefDataOfficer

### Element Id
CocoPharma::GovernanceObligation::EachInformationCollectionHasDesignatedOwner

### Membership Rationale
The CDO is accountable for the register of information assets and their owners across the organisation.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefDataOfficer

### Element Id
CocoPharma::GovernanceObligation::DataQualityIssuesMustBeReportedAndResolved

### Membership Rationale
The CDO sets the data quality standards and escalation paths that this obligation defines.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefDataOfficer

### Element Id
CocoPharma::GovernanceApproach::MetadataDrivenGovernance

### Membership Rationale
The CDO is the sponsor and accountable owner of the Egeria-based metadata-driven governance approach.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefDataOfficer

### Element Id
CocoPharma::GovernanceApproach::FederatedGovernanceWithCentralCoordination

### Membership Rationale
The CDO chairs the cross-domain governance forum and is the central coordinator of the federated governance model.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefDataOfficer

### Element Id
CocoPharma::GovernanceApproach::AutomatedQualityMonitoring

### Membership Rationale
The CDO owns the approach to automated data quality monitoring and is accountable for the tooling and processes that deliver it.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefDataOfficer

### Element Id
CocoPharma::GovernanceMetric::PercentageOfDataAssetsWithDesignatedOwner

### Membership Rationale
The CDO is responsible for reporting this metric to the board and for driving the action needed to reach 100%.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefDataOfficer

### Element Id
CocoPharma::GovernanceMetric::DataQualityRulePassRate

### Membership Rationale
The CDO owns the organisation-wide data quality pass rate and uses it to assess the effectiveness of the data governance program.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefDataOfficer

### Element Id
CocoPharma::GovernanceMetric::OpenDataQualityIssuesByAge

### Membership Rationale
The CDO reviews this metric to identify unresolved quality issues and trigger escalations where service levels are being missed.

### Membership Status
VALIDATED

___

---

#### Chief Information Security Officer Folio Members

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefInformationSecurityOfficer

### Element Id
CocoPharma::BusinessImperative::CyberResilience

### Membership Rationale
The CISO is the accountable executive for the cyber resilience imperative and owns the security governance program that delivers it.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefInformationSecurityOfficer

### Element Id
CocoPharma::Threat::CyberAttackOnOperationsOrData

### Membership Rationale
The CISO is responsible for threat assessment and for the controls that mitigate the risk of cyber-attack.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefInformationSecurityOfficer

### Element Id
CocoPharma::Regulation::MartynsLaw

### Membership Rationale
Martyn's Law is a security regulation. The CISO is the domain lead for security compliance including this act.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefInformationSecurityOfficer

### Element Id
CocoPharma::GovernanceObligation::AllUsersMustBeAuthenticatedAndAccountable

### Membership Rationale
User authentication and access logging are core security controls authored and owned by the CISO.

### Membership Status
VALIDATED

___

---

#### Chief Privacy Officer Folio Members

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefPrivacyOfficer

### Element Id
CocoPharma::Threat::UnauthorisedDataDisclosure

### Membership Rationale
Preventing unauthorised disclosure of personal data is a primary CPO responsibility.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefPrivacyOfficer

### Element Id
CocoPharma::Regulation::GDPR

### Membership Rationale
The CPO is the accountable executive for GDPR compliance across the organisation.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefPrivacyOfficer

### Element Id
CocoPharma::GovernancePrinciple::PrivacyByDesign

### Membership Rationale
Privacy by Design is the foundational privacy principle authored and championed by the CPO.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefPrivacyOfficer

### Element Id
CocoPharma::GovernanceObligation::PersonalDataClassifiedBySensitivity

### Membership Rationale
The CPO defines the personal data classification scheme and is accountable for its implementation across the organisation.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefPrivacyOfficer

### Element Id
CocoPharma::GovernanceMetric::PersonalDataBreachesReported

### Membership Rationale
The CPO is accountable for monitoring and reporting personal data breaches and for the 72-hour GDPR notification process.

### Membership Status
VALIDATED

___

---

#### Chief Financial Officer Folio Members

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::ChiefFinancialOfficer

### Element Id
CocoPharma::Threat::FraudulentSupplierActivity

### Membership Rationale
Supplier fraud is a financial and procurement risk. The CFO is accountable for the controls over supplier master data and procurement governance.

### Membership Status
VALIDATED

___

---

#### Drug Development Lead Folio Members

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::DrugDevelopmentLead

### Element Id
CocoPharma::Regulation::FDAClinicalTrialRegulations

### Membership Rationale
Tessa Tube is the domain lead for drug development and is accountable for ensuring clinical trial data governance meets FDA requirements.

### Membership Status
VALIDATED

___

---

#### Sustainability Lead Folio Members

___

## Add Member to Collection

### Collection Id
CocoPharma::Folio::SustainabilityLead

### Element Id
CocoPharma::BusinessImperative::SustainabilityReporting

### Membership Rationale
Tom Tally is the sustainability domain lead and is accountable for the data governance that underpins accurate and auditable sustainability reporting.

### Membership Status
VALIDATED

___

---

### 6.3 Root Collection Membership

The six governance folios are registered as members of the organisation's root governance folios collection, making them discoverable as a group in Egeria.

___

## Add Member to Collection

### Collection Id
RootCollection::Coco::Governance Folios

### Element Id
CocoPharma::Folio::ChiefDataOfficer

### Membership Rationale
The CDO folio is part of the Coco Pharmaceuticals governance folios collection.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
RootCollection::Coco::Governance Folios

### Element Id
CocoPharma::Folio::ChiefInformationSecurityOfficer

### Membership Rationale
The CISO folio is part of the Coco Pharmaceuticals governance folios collection.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
RootCollection::Coco::Governance Folios

### Element Id
CocoPharma::Folio::ChiefPrivacyOfficer

### Membership Rationale
The CPO folio is part of the Coco Pharmaceuticals governance folios collection.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
RootCollection::Coco::Governance Folios

### Element Id
CocoPharma::Folio::ChiefFinancialOfficer

### Membership Rationale
The CFO folio is part of the Coco Pharmaceuticals governance folios collection.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
RootCollection::Coco::Governance Folios

### Element Id
CocoPharma::Folio::DrugDevelopmentLead

### Membership Rationale
The Drug Development Lead folio is part of the Coco Pharmaceuticals governance folios collection.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
RootCollection::Coco::Governance Folios

### Element Id
CocoPharma::Folio::SustainabilityLead

### Membership Rationale
The Sustainability Lead folio is part of the Coco Pharmaceuticals governance folios collection.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CollectionFolder::Coco::Pharmaceutical Industry Regulations

### Element Id
CocoPharma::Regulation::GoodManufacturingPractice

### Membership Rationale
Good Manufacturing Practice is a pharmaceutical industry regulation applicable to Coco Pharmaceuticals' drug manufacturing operations.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CollectionFolder::Coco::Clinical Trial Regulations

### Element Id
CocoPharma::Regulation::FDAClinicalTrialRegulations

### Membership Rationale
The FDA Clinical Trial Regulations govern the conduct, recording, and reporting of clinical trials undertaken by Coco Pharmaceuticals.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CollectionFolder::Coco::Privacy Regulations

### Element Id
CocoPharma::Regulation::GDPR

### Membership Rationale
GDPR is the primary privacy regulation applicable to Coco Pharmaceuticals' processing of personal data, including patient health data.

### Membership Status
VALIDATED

___

---

___

## Add Member to Collection

### Collection Id
CollectionFolder::Coco::Security Regulations

### Element Id
CocoPharma::Regulation::MartynsLaw

### Membership Rationale
Martyn's Law is a security regulation requiring Coco Pharmaceuticals to implement appropriate protective security measures for its events.

### Membership Status
VALIDATED

___

---

## Appendix: Governance Domain Leads

| Domain | Identifier | Lead | Description |
|--------|-----------|------|-------------|
| Data | DATA | Jules Keeper | Governance of data assets, definitions, quality, and use |
| Privacy | PRIVACY | Faith Broker | Governance of personal data handling and privacy compliance |
| Security | SECURITY | Ivor Padlock | Governance of access controls, cyber resilience, and incident response |
| IT Infrastructure | IT_INFRASTRUCTURE | Gary Geeke | Governance of systems, platforms, networks, and infrastructure |
| Software Development | SOFTWARE_DEVELOPMENT | Polly Tasker | Governance of software development practices and DevOps |
| Corporate | CORPORATE | Reggie Mint | Governance of financial reporting, supplier management, and corporate compliance |
| Asset Management | ASSET_MANAGEMENT | (TBD) | Governance of physical and digital assets |

---

## Appendix: Related Resources

- [Coco Pharmaceuticals Data Strategy Overview](https://egeria-project.org/practices/coco-pharmaceuticals/scenarios/defining-the-data-strategy/overview/)
- [Building the Governance Team](https://egeria-project.org/practices/coco-pharmaceuticals/scenarios/building-the-governance-team/overview/)
- [Defining Multi-Faceted Governance](https://egeria-project.org/practices/coco-pharmaceuticals/scenarios/defining-multi-faceted-governance/overview/)

