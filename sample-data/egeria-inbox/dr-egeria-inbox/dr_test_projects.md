# Projects Family — Happy Path Tests
# Sales Forecast Theme

> This document tests the Dr.Egeria Projects command family under normal conditions.
> All commands are expected to succeed when processed.
>
> Run with VALIDATE first, then PROCESS.
>
> GUID appears only in Create commands — the system fills it on first processing.
> Update commands are identified by Qualified Name.
> Relationship commands are identified by their endpoint attributes (Parent Project, Child Project).
>
> Verb synonyms:
>   Establish: Link, Attach, Add (all equivalent)
>   Remove:    Detach, Unlink, Remove (all equivalent)
>
> Project subtypes: Campaign, Task, Personal Project, Study Project, and Experiment
> are all classifications on the Project entity in Egeria. They share an identical
> attribute set (Project Base). The command name carries the classification.
> Project Type valid values: Project, Campaign, Task, PersonalProject, StudyProject, Experiment

---

# PR-01: Create Project — minimal, QN auto-generated

> Display Name only. Expected: GUID filled, QN auto-generated, verb swapped to Update Project.

# Create Project

## Display Name
Sales Forecast Initiative

## GUID

___

# PR-02: Create Project — full Project Base coverage, user-specified QN

> Exercises all Project Base own attributes:
>   Mission, Purposes (Simple List), Project Type (Enum), Project Identifier,
>   Planned Start Date, Planned Completion Date, Actual Start Date,
>   Priority (Simple Int), Project Phase, Project Status, Project Health,
>   Project Scope, Project Approach, Project Management Style,
>   Project Results Usage, Success Criteria (Simple List).
> Also exercises Authored Referenceable fields: Authors, Content Status.
> User-specified QN for reliable downstream reference.

# Create Project

## Display Name
Q1 2026 Sales Forecast Delivery

## Description
Project to deliver the Q1 2026 Sales Forecast, covering pipeline analysis,
data quality remediation, and executive reporting for the March board review.

## Mission
Deliver a reliable, auditable Q1 2026 Sales Forecast to support the March
board review and annual business plan validation.

## Purposes
Drive accountability for forecast accuracy
Enable data-driven pipeline management
Support board-level financial reporting

## Project Type
Project

## Project Identifier
SF-2026-Q1

## Planned Start Date
2026-01-05

## Planned Completion Date
2026-03-31

## Actual Start Date
2026-01-06

## Priority
1

## Project Phase
Execution

## Project Status
InProgress

## Project Health
Green

## Project Scope
In scope: Q1 opportunity pipeline, CRM data quality, revenue projections.
Out of scope: Historical restatements, non-CRM revenue sources.

## Project Approach
Agile sprint cycles with weekly stakeholder reviews.

## Project Management Style
Formal

## Project Results Usage
InformBoardReview

## Success Criteria
Forecast delivered by 2026-03-28
Variance to actuals within 5 percent
All data quality issues resolved or documented

## Authors
jane.smith@example.com

## Content Status
ACTIVE

## Version Identifier
1.0

## Search Keywords
sales forecast, Q1 2026, pipeline, CRM, board review

## Journal Entry
Project initiated following Q4 2025 forecast retrospective.

## Qualified Name
Project::SalesForecast::Q1-2026::Delivery::1.0

## GUID

___

# PR-03: Update Project — identified by Qualified Name

> Update flavor. No GUID. Element located by Qualified Name.
> Only changed fields provided; Merge Update defaults to True.

# Update Project

## Display Name
Q1 2026 Sales Forecast Delivery

## Qualified Name
Project::SalesForecast::Q1-2026::Delivery::1.0

## Project Status
NearingCompletion

## Project Phase
Closeout

## Actual Completion Date
2026-03-27

## Journal Entry
Project moved to closeout phase on 2026-03-20 following board submission.

___

# PR-04: Update Project — identified by Display Name only

> No QN provided. Dr.Egeria forms a QN from Display Name and attempts to match.
> Expected: element matched and updated, QN filled in output.

# Update Project

## Display Name
Sales Forecast Initiative

## Description
Top-level initiative tracking all Sales Forecast governance activity across 2026.

___

# PR-05: Create Campaign

> Campaign classification on Project. Project Type set to Campaign.
> User-specified QN — referenced as Parent Project in PR-11 and PR-12.

# Create Campaign

## Display Name
Sales Forecast Governance Program

## Description
Campaign organising all governance, data quality, and reporting projects
that support the Sales Forecasting function across 2026.

## Mission
Establish and maintain a trusted, governed Sales Forecast capability across
all business units by end of 2026.

## Purposes
Ensure forecast data quality meets board reporting standards
Build reusable governance assets for future forecast cycles

## Project Type
Campaign

## Project Identifier
SF-GOV-2026

## Planned Start Date
2026-01-01

## Planned Completion Date
2026-12-31

## Priority
1

## Project Status
InProgress

## Project Health
Green

## Content Status
ACTIVE

## Qualified Name
Project::SalesForecast::GovernanceProgram::2026::1.0

## GUID

___

# PR-06: Create Task

> Task classification on Project. Represents a small, assignable unit of work.
> Exercises Actual Start Date and Actual Completion Date (task is already complete).

# Create Task

## Display Name
Validate CRM Opportunity Data — Q1 2026

## Description
Validate that all CRM opportunity records have required fields populated
and pass data quality rules before the Q1 forecast is generated.

## Mission
Ensure CRM data quality is sufficient for Q1 forecast accuracy.

## Project Type
Task

## Project Identifier
SF-TASK-CRM-VALIDATE-001

## Planned Start Date
2026-01-10

## Planned Completion Date
2026-01-24

## Actual Start Date
2026-01-10

## Actual Completion Date
2026-01-23

## Priority
2

## Project Status
Completed

## Project Health
Green

## Success Criteria
All required CRM fields populated for open opportunities
Zero critical data quality rule failures

## Qualified Name
Project::SalesForecast::Task::CRMValidation::Q1-2026::1.0

## GUID

___

# PR-07: Create Personal Project

> PersonalProject classification on Project. Informal project for a single person.

# Create Personal Project

## Display Name
Jane Smith — Forecast Dashboard Design

## Description
Jane Smith's personal project to prototype a self-service forecast dashboard
for the Sales Analytics team using the Q1 2026 data product.

## Mission
Prototype a reusable forecast dashboard for the Sales Analytics team.

## Project Type
PersonalProject

## Project Identifier
JS-DASH-001

## Planned Start Date
2026-02-01

## Planned Completion Date
2026-03-15

## Priority
3

## Project Status
InProgress

## Qualified Name
Project::SalesForecast::Personal::JaneSmith::Dashboard::1.0

## GUID

___

# PR-08: Create Study Project

> StudyProject classification on Project. Focused analysis of a topic or situation.

# Create Study Project

## Display Name
CRM Pipeline Conversion Rate Analysis

## Description
Study project analysing historical CRM pipeline conversion rates to improve
forecast model accuracy for future quarters.

## Mission
Identify the key drivers of forecast variance in CRM pipeline conversion rates.

## Project Type
StudyProject

## Project Identifier
SF-STUDY-CONV-001

## Planned Start Date
2026-02-15

## Planned Completion Date
2026-04-30

## Priority
2

## Project Status
Active

## Project Results Usage
InformForecastModel

## Success Criteria
Conversion rate model validated against 4 prior quarters
Key variance drivers identified and documented

## Qualified Name
Project::SalesForecast::Study::CRMConversion::1.0

## GUID

___

# PR-09: Create Experiment — new Project Type

> Experiment classification on Project. Exercises the new Experiment value
> added to the Project Type enum.

# Create Project

## Display Name
ML Forecast Model Experiment — Q2 2026

## Description
Experiment to evaluate whether a machine learning model can improve
Sales Forecast accuracy beyond the current rule-based approach.

## Mission
Assess feasibility of ML-driven forecast models for Q2 2026 and beyond.

## Project Type
Experiment

## Project Identifier
SF-EXP-ML-001

## Planned Start Date
2026-04-01

## Planned Completion Date
2026-06-30

## Priority
2

## Project Status
Planned

## Project Results Usage
InformFutureProjects

## Success Criteria
ML model accuracy within 3 percent of actuals on holdout data
Results documented and shared with Data Science team

## Qualified Name
Project::SalesForecast::Experiment::MLModel::Q2-2026::1.0

## GUID

___

# PR-10: Link Project Hierarchy — verb Link

> Links a parent campaign and child project via ProjectHierarchy.
> Parent Project and Child Project are both input_required.
> No GUID on relationship commands.

# Link Project Hierarchy

## Parent Project
Project::SalesForecast::GovernanceProgram::2026::1.0

## Child Project
Project::SalesForecast::Q1-2026::Delivery::1.0

## Description
Q1 2026 Delivery project is a child of the Sales Forecast Governance Program campaign.

___

# PR-11: Link Project Hierarchy — second child, verb Attach

> Uses establish synonym Attach. Links another child to the same parent.

# Attach Project Hierarchy

## Parent Project
Project::SalesForecast::GovernanceProgram::2026::1.0

## Child Project
Project::SalesForecast::Task::CRMValidation::Q1-2026::1.0

## Description
CRM Validation task is a child of the Sales Forecast Governance Program campaign.

___

# PR-12: Link Project Dependency — verb Link

> Q1 Delivery depends on CRM Validation completing first.
> Parent Project is the dependency (must complete first);
> Child Project is the dependent (cannot start until parent completes).

# Link Project Dependency

## Parent Project
Project::SalesForecast::Task::CRMValidation::Q1-2026::1.0

## Child Project
Project::SalesForecast::Q1-2026::Delivery::1.0

## Description
Q1 2026 Delivery depends on CRM Validation completing before forecast generation begins.

___

# PR-13: Detach Project Hierarchy — verb Detach

> Removes the hierarchy link established in PR-11.
> Identified by endpoint attributes — no GUID.

# Detach Project Hierarchy

## Parent Project
Project::SalesForecast::GovernanceProgram::2026::1.0

## Child Project
Project::SalesForecast::Task::CRMValidation::Q1-2026::1.0

___

# PR-14: Unlink Project Dependency — verb Unlink

> Removes the dependency established in PR-12.
> Detach and Remove are equivalent synonyms.

# Unlink Project Dependency

## Parent Project
Project::SalesForecast::Task::CRMValidation::Q1-2026::1.0

## Child Project
Project::SalesForecast::Q1-2026::Delivery::1.0

___

> End of Projects happy path tests.
>
> Expected outcomes:
>   PR-01               : GUID filled, QN auto-generated, verb swapped to Update Project
>   PR-02, PR-05 to PR-09 : GUID filled, user-specified QN preserved exactly, verb swapped
>   PR-03               : Update locates element by QN, applies partial update, no GUID slot
>   PR-04               : Update locates element by Display Name, QN filled in output
>   PR-05               : Project Type=Campaign classification set correctly
>   PR-06               : Project Type=Task; Actual Start Date and Actual Completion Date present
>   PR-07               : Project Type=PersonalProject classification set correctly
>   PR-08               : Project Type=StudyProject classification set correctly
>   PR-09               : Project Type=Experiment (new enum value) accepted and processed
>   PR-10 to PR-12      : Relationship commands executed, no GUID slot
>   PR-13, PR-14        : Relationships removed; Detach and Unlink synonyms accepted
>   PR-11               : Attach synonym accepted, processed as Link Project Hierarchy