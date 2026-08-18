# BCUHB External Data Quality & Reporting Review — Solution Blueprint

> **Author:** Mandy Chessell (Lead Reviewer / Solution Architect)
> **Version:** 0.1
> **Status:** DRAFT
> **Date:** 2026-08-03
> **Description:** Solution architecture for delivering the *External Expert Review of Data Quality and Data Reporting* requested by Betsi Cadwaladr University Health Board (BCUHB) (Service Specification, June 2026). Describes the landscape being reviewed and the Egeria-based toolchain used to gather evidence, trace lineage, assess quality and manage findings across the review.

---

## Overview

The specification asks for an independent, evidence-based review spanning data quality, end-to-end data flow, governance, systems/infrastructure, culture and benchmarking (Sections 3.1–3.6), delivered against a £15–20k budget in 12 weeks. That scope-to-budget ratio only works if evidence-gathering is largely automated rather than manually assembled interview-by-interview and spreadsheet-by-spreadsheet.

The architecture below has two halves:

- **The landscape being reviewed** (four components): the source and feeder systems, the data warehouse, the reconciliation/sign-off process, and the statutory/Board reporting that consumes it — this is BCUHB's existing estate, taken as-is.
- **The review toolchain** (seven components): an Egeria-based metadata catalogue, lineage capture, national-standards validation, data-quality survey engine, governance/ownership register, findings & risk register, and a reporting dashboard — this is what the review stands up (largely read-only, temporary, and handed over or decommissioned at the end of the engagement per the client's preference).

### How each objective in the specification is addressed

| Spec section | Objective | Addressed by |
|---|---|---|
| 3.1 Data Quality Assessment | Accuracy, completeness, timeliness, consistency; sample testing against source | Data Quality Survey Engine, National Standards Validation Library |
| 3.2 End-to-End Data Flow Review | Capture → processing → validation → reporting mapping | Lineage Capture Service |
| 3.3 Governance and Assurance | Ownership, sign-off, escalation, change management | Governance & Ownership Register, Findings & Risk Register (via escalation workflow) |
| 3.4 Systems and Infrastructure | Manual processes, system interfaces, fragmentation risk | Metadata Catalog & Asset Inventory, Lineage Capture Service |
| 3.5 Culture and Capability | Ownership/accountability, openness, skills | Governance & Ownership Register supplies the "who owns what" evidence base; the culture assessment itself remains interview-led (see the Plan) |
| 3.6 Benchmarking | Comparison against NHS Wales peers and recognised maturity models | Review Reporting Dashboard (scores rolled up against a maturity model) |

---

## Part 1: Solution Blueprint

___

## Create Solution Blueprint

### Display Name
BCUHB Data Quality Review Architecture

### Qualified Name
BCUHB::SolutionBlueprint::DataQualityReviewArchitecture

### Description
The solution architecture used to deliver the External Expert Review of Data Quality and Data Reporting for Betsi Cadwaladr University Health Board: BCUHB's existing data landscape (source systems, data warehouse, reconciliation process, statutory reporting), combined with the Egeria-based toolchain used to catalogue, trace, assess and report on it during the review.

### Authors
- Mandy Chessell

### Version Identifier
0.1

### Content Status
DRAFT

___

---

## Part 2: Solution Components

### 2.1 The landscape being reviewed

___

## Create Solution Component

### Display Name
Source & Feeder Systems

### Qualified Name
BCUHB::SolutionComponent::SourceFeederSystems

### Description
The operational systems that originate the data behind national and statutory returns — acute service systems and, where relevant, primary/community systems (Spec Section 4.1). Point of data capture and the start of the audit trail.

### Solution Component Type
Third Party Process

### In Solution Blueprints
BCUHB::SolutionBlueprint::DataQualityReviewArchitecture

### Authors
- Mandy Chessell

### Version Identifier
0.1

### Content Status
DRAFT

___

---

___

## Create Solution Component

### Display Name
BCUHB Data Warehouse

### Qualified Name
BCUHB::SolutionComponent::DataWarehouse

### Description
The central warehouse that consolidates feeds from source systems ahead of reconciliation, sign-off and onward reporting. The specification's stated point of concern (Section 1, Background and Context).

### Solution Component Type
Data Storage

### In Solution Blueprints
BCUHB::SolutionBlueprint::DataQualityReviewArchitecture

### Authors
- Mandy Chessell

### Version Identifier
0.1

### Content Status
DRAFT

___

---

___

## Create Solution Component

### Display Name
Reconciliation & Sign-off Process

### Qualified Name
BCUHB::SolutionComponent::ReconciliationSignOff

### Description
The submission checks, reconciliation and approval process — and its ownership within services — that sits between the warehouse and external reporting (Spec Section 3.3). A process component, not a system: this is where manual steps and single points of failure are most likely to surface.

### Solution Component Type
Manual Process

### In Solution Blueprints
BCUHB::SolutionBlueprint::DataQualityReviewArchitecture

### Authors
- Mandy Chessell

### Version Identifier
0.1

### Content Status
DRAFT

___

---

___

## Create Solution Component

### Display Name
Statutory & Board Reporting

### Qualified Name
BCUHB::SolutionComponent::StatutoryBoardReporting

### Description
The national/statutory returns and internal performance reports consumed by the Executive Team, the Board, Welsh Government and regulators (Spec Section 4.1). The end of the data's journey and the point where trust is won or lost.

### Solution Component Type
Publishing

### In Solution Blueprints
BCUHB::SolutionBlueprint::DataQualityReviewArchitecture

### Authors
- Mandy Chessell

### Version Identifier
0.1

### Content Status
DRAFT

___

---

### 2.2 The review toolchain

___

## Create Solution Component

### Display Name
Metadata Catalog & Asset Inventory

### Qualified Name
BCUHB::SolutionComponent::MetadataCatalog

### Description
Egeria integration connectors harvest and register the source systems and the warehouse as catalogued assets, producing the inventory the review's other components are built on. Directly supports Spec Section 3.4 (systems and infrastructure) and gives an early, objective read on data fragmentation.

### Solution Component Type
Data Storage

### In Solution Blueprints
BCUHB::SolutionBlueprint::DataQualityReviewArchitecture

### Authors
- Mandy Chessell

### Version Identifier
0.1

### Content Status
DRAFT

___

---

___

## Create Solution Component

### Display Name
Lineage Capture Service

### Qualified Name
BCUHB::SolutionComponent::LineageCapture

### Description
Traces data flow from point of capture through processing, validation and reconciliation to reported figures (Spec Section 3.2). Gaps where lineage cannot be automatically established are themselves findings — they mark undocumented manual steps or single points of failure (Spec Section 5.4).

### Solution Component Type
Long Running Daemon

### In Solution Blueprints
BCUHB::SolutionBlueprint::DataQualityReviewArchitecture

### Authors
- Mandy Chessell

### Version Identifier
0.1

### Content Status
DRAFT

___

---

___

## Create Solution Component

### Display Name
National Standards Validation Library

### Qualified Name
BCUHB::SolutionComponent::NationalStandardsLibrary

### Description
A governed reference set of NHS Wales / Welsh Government validation and reporting criteria (e.g. waiting-times rules, statutory return definitions), held as valid values and used to check whether reporting processes correctly apply national standards (Spec Section 3.1, first bullet).

### Solution Component Type
Software Library

### In Solution Blueprints
BCUHB::SolutionBlueprint::DataQualityReviewArchitecture

### Authors
- Mandy Chessell

### Version Identifier
0.1

### Content Status
DRAFT

___

---

___

## Create Solution Component

### Display Name
Data Quality Survey Engine

### Qualified Name
BCUHB::SolutionComponent::DataQualitySurveyEngine

### Description
Runs profiling and quality assessments (completeness, validity, consistency, timeliness) against catalogued assets, and supports sample testing of reported figures against source records (Spec Sections 3.1, 5.2). Produces quantified, evidenced findings rather than impressionistic ones.

### Solution Component Type
Multi-Step Process

### In Solution Blueprints
BCUHB::SolutionBlueprint::DataQualityReviewArchitecture

### Authors
- Mandy Chessell

### Version Identifier
0.1

### Content Status
DRAFT

___

---

___

## Create Solution Component

### Display Name
Governance & Ownership Register

### Qualified Name
BCUHB::SolutionComponent::GovernanceOwnershipRegister

### Description
Captures data owners, stewards and sign-off roles against each catalogued asset and flow, built from interview and document-review evidence (Spec Sections 3.3, 3.5). The factual backbone for the review's findings on accountability and escalation.

### Solution Component Type
Data Storage

### In Solution Blueprints
BCUHB::SolutionBlueprint::DataQualityReviewArchitecture

### Authors
- Mandy Chessell

### Version Identifier
0.1

### Content Status
DRAFT

___

---

___

## Create Solution Component

### Display Name
Findings & Risk Register

### Qualified Name
BCUHB::SolutionComponent::FindingsRiskRegister

### Description
Consolidates quality survey results, lineage gaps and governance evidence into root-caused, risk-rated findings (high/medium/low), each traceable back to the specific asset or flow that produced it (Spec Section 6.2).

### Solution Component Type
Data Storage

### In Solution Blueprints
BCUHB::SolutionBlueprint::DataQualityReviewArchitecture

### Authors
- Mandy Chessell

### Version Identifier
0.1

### Content Status
DRAFT

___

---

___

## Create Solution Component

### Display Name
Review Reporting Dashboard

### Qualified Name
BCUHB::SolutionComponent::ReviewReportingDashboard

### Description
Rolls up catalogue coverage, lineage completeness, quality scores and open findings for the fortnightly updates to the Acting Director of Digital, Data and Technology, and for the Board/Executive presentation (Spec Sections 6.3, 8). Also carries the benchmarking view against a recognised data quality maturity model (Spec Section 3.6).

### Solution Component Type
User Interface

### In Solution Blueprints
BCUHB::SolutionBlueprint::DataQualityReviewArchitecture

### Authors
- Mandy Chessell

### Version Identifier
0.1

### Content Status
DRAFT

___

---

## Part 3: Solution Linking Wires

### 3.1 Existing data flow (BCUHB's landscape, as-is)

___

## Link Solution Components

### Component1
BCUHB::SolutionComponent::SourceFeederSystems

### Component2
BCUHB::SolutionComponent::DataWarehouse

### Label
operational-data

___

---

___

## Link Solution Components

### Component1
BCUHB::SolutionComponent::DataWarehouse

### Component2
BCUHB::SolutionComponent::ReconciliationSignOff

### Label
submission-for-reconciliation

___

---

___

## Link Solution Components

### Component1
BCUHB::SolutionComponent::ReconciliationSignOff

### Component2
BCUHB::SolutionComponent::StatutoryBoardReporting

### Label
signed-off-submission

___

---

### 3.2 Catalogue and lineage capture (review reads BCUHB's landscape)

___

## Link Solution Components

### Component1
BCUHB::SolutionComponent::SourceFeederSystems

### Component2
BCUHB::SolutionComponent::MetadataCatalog

### Label
catalogued-by

___

---

___

## Link Solution Components

### Component1
BCUHB::SolutionComponent::DataWarehouse

### Component2
BCUHB::SolutionComponent::MetadataCatalog

### Label
catalogued-by

___

---

___

## Link Solution Components

### Component1
BCUHB::SolutionComponent::ReconciliationSignOff

### Component2
BCUHB::SolutionComponent::MetadataCatalog

### Label
catalogued-by

___

---

___

## Link Solution Components

### Component1
BCUHB::SolutionComponent::MetadataCatalog

### Component2
BCUHB::SolutionComponent::LineageCapture

### Label
asset-context

___

---

___

## Link Solution Components

### Component1
BCUHB::SolutionComponent::SourceFeederSystems

### Component2
BCUHB::SolutionComponent::LineageCapture

### Label
observed-flow

___

---

___

## Link Solution Components

### Component1
BCUHB::SolutionComponent::DataWarehouse

### Component2
BCUHB::SolutionComponent::LineageCapture

### Label
observed-flow

___

---

___

## Link Solution Components

### Component1
BCUHB::SolutionComponent::ReconciliationSignOff

### Component2
BCUHB::SolutionComponent::LineageCapture

### Label
observed-flow

___

---

### 3.3 Quality assessment and findings

___

## Link Solution Components

### Component1
BCUHB::SolutionComponent::NationalStandardsLibrary

### Component2
BCUHB::SolutionComponent::DataQualitySurveyEngine

### Label
validation-rules

___

---

___

## Link Solution Components

### Component1
BCUHB::SolutionComponent::MetadataCatalog

### Component2
BCUHB::SolutionComponent::DataQualitySurveyEngine

### Label
profiling-target

___

---

___

## Link Solution Components

### Component1
BCUHB::SolutionComponent::DataQualitySurveyEngine

### Component2
BCUHB::SolutionComponent::FindingsRiskRegister

### Label
quality-findings

___

---

___

## Link Solution Components

### Component1
BCUHB::SolutionComponent::LineageCapture

### Component2
BCUHB::SolutionComponent::FindingsRiskRegister

### Label
lineage-gaps

___

---

___

## Link Solution Components

### Component1
BCUHB::SolutionComponent::GovernanceOwnershipRegister

### Component2
BCUHB::SolutionComponent::FindingsRiskRegister

### Label
ownership-context

___

---

### 3.4 Reporting back to the client

___

## Link Solution Components

### Component1
BCUHB::SolutionComponent::FindingsRiskRegister

### Component2
BCUHB::SolutionComponent::ReviewReportingDashboard

### Label
findings-feed

___

---

___

## Link Solution Components

### Component1
BCUHB::SolutionComponent::GovernanceOwnershipRegister

### Component2
BCUHB::SolutionComponent::ReviewReportingDashboard

### Label
ownership-coverage

___

---

___

## Link Solution Components

### Component1
BCUHB::SolutionComponent::LineageCapture

### Component2
BCUHB::SolutionComponent::ReviewReportingDashboard

### Label
lineage-coverage

___

---

___

## Link Solution Components

### Component1
BCUHB::SolutionComponent::ReviewReportingDashboard

### Component2
BCUHB::SolutionComponent::StatutoryBoardReporting

### Label
informs-reporting

___
