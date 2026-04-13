# Governance Officer Family — Happy Path Tests
# Sales Forecast Theme

> This document tests the Dr.Egeria Governance Officer command family under normal conditions.
> All commands are expected to succeed when processed.
>
> Run with VALIDATE first, then PROCESS.
>
> GUID appears only in Create commands — system fills on first processing.
> Update commands are identified by Qualified Name — no GUID.
> Link commands are identified by their endpoint attributes — no GUID.
>
> Verb synonyms:
>   Establish: Link, Attach, Add (all equivalent)
>   Remove:    Detach, Unlink, Remove (all equivalent)
>
> Valid Value / Enum fields — only values from these lists appear below:
>
>   Domain Identifier (Enum):
>     ALL, DATA, PRIVACY, SECURITY, IT_INFRASTRUCTURE,
>     SOFTWARE_DEVELOPMENT, CORPORATE, ASSET_MANAGEMENT, OTHER
>
>   Content Status (Valid Value — Authored Referenceable):
>     DRAFT, PREPARED, PROPOSED, APPROVED, REJECTED,
>     ACTIVE, DEPRECATED, OTHER
>
>   Activity Status (Valid Value — Link Notification Subscriber only):
>     REQUESTED, APPROVED, WAITING, ACTIVATING, IN_PROGRESS,
>     PAUSED, COMPLETED, INVALID, IGNORED, FAILED, CANCELLED, ABANDONED, OTHER
>
>   Importance — Simple (free text, no defined valid values)
>   Implementation Description — Simple (free text)
>   All date fields — Simple (ISO-8601 string)
>   All interval fields — Simple Int (milliseconds)
>
> Bundle inheritance chains (28 Create commands):
>
>   Governance Driver:
>     Authored Referenceable → Governance Definition Core → Governance Driver
>     Own attrs: Domain Identifier(Enum), Summary, Scope, Usage, Importance,
>                Implications(Simple List), Outcomes(Simple List), Results(Simple List)
>     + Authored Referenceable: Authors(Simple List), Content Status(Valid Value)
>     Commands: Create Business Imperative, Create Governance Driver,
>               Create Governance Strategy (+Business Imperatives),
>               Create Threat, Create Regulation (+Regulation Source, Regulators),
>               Create Regulation Article
>
>   Governance Policy:
>     ... → Governance Definition Core → Governance Policy
>     Same own attrs as Governance Driver
>     Commands: Create Governance Policy, Create Governance Principle,
>               Create Governance Obligation, Create Governance Approach
>
>   Governance Control Base:
>     ... → Governance Definition Core → Governance Control Base
>     Adds: Implementation Description (Simple)
>     Commands: Create Governance Control, Create Governance Rule,
>               Create Governance Responsibility, Create Governance Procedure,
>               Create Service Level Objective, Create Methodology,
>               Create Governance Action, Create Data Processing Purpose,
>               Create Governance Metric (+Measurement, Target),
>               Create Naming Standard Rule (+Name Patterns),
>               Create Notification Type (+date/interval attrs),
>               Create Data Lens (+geo/temporal/scope attrs)
>
>   Terms and Conditions:
>     ... → Governance Control Base → Terms and Conditions
>     Adds: Entitlements(Dict), Obligations(Dict), Restrictions(Dict)
>     Commands: Create Certification Type, Create License Type,
>               Create Terms and Conditions
>
>   Security Access Control:
>     ... → Governance Control Base → Security Access Control
>     No additional own attrs
>     Commands: Create Security Access Control,
>               Create Governance Zone (+Criteria)
>
>   Governance Definition Core (direct):
>     Commands: Create Governance Definition

---

# ===== SECTION 1: GOVERNANCE DRIVERS =====

# GO-01: Create Business Imperative — full Governance Definition Core coverage, user-specified QN

> Exercises all core own attrs: Domain Identifier (Enum), Summary (Simple),
> Scope (Simple), Usage (Simple), Importance (Simple), Implications (Simple List),
> Outcomes (Simple List), Results (Simple List).
> Plus Authored Referenceable: Authors (Simple List), Content Status (Valid Value).

# Create Business Imperative

## Display Name
Sales Forecast Accuracy

## Summary
We must deliver reliable, auditable sales forecasts to meet board reporting
standards and support sound business planning decisions.

## Description
The Sales Forecasting function must produce accurate, timely, and well-governed
forecasts trusted by the board, finance, and sales leadership.

## Domain Identifier
CORPORATE

## Scope
Enterprise — all business units contributing to the consolidated revenue forecast.

## Importance
High

## Implications
Board reporting credibility depends on forecast accuracy
Capital allocation decisions are made based on forecast data

## Outcomes
Forecast variance to actuals within 5 percent
Board receives forecast with full data lineage and quality attestation

## Results
Q1 2026 forecast delivered on time with complete audit trail
Data quality issues resolved before board submission

## Usage
Reference this imperative when prioritising governance investments in the
Sales Forecasting domain.

## Authors
jane.smith@example.com

## Content Status
ACTIVE

## Version Identifier
1.0

## Journal Entry
Defined as part of Q1 2026 Sales Forecast governance programme.

## Qualified Name
BusinessImperative::SalesForecast::Accuracy::1.0

## GUID

___

# GO-02: Create Governance Driver — minimal, QN auto-generated

# Create Governance Driver

## Display Name
SF-Driver-Smoke-Test

## GUID

___

# GO-03: Create Governance Strategy — with Business Imperatives (Reference Name List)

# Create Governance Strategy

## Display Name
Sales Forecast Data Governance Strategy

## Summary
Govern all data assets and processes contributing to the Sales Forecasting
pipeline to ensure accuracy, auditability, and trust.

## Domain Identifier
DATA

## Scope
All CRM, pipeline, and revenue data assets used in Sales Forecasting.

## Importance
High

## Business Imperatives
BusinessImperative::SalesForecast::Accuracy::1.0

## Authors
jane.smith@example.com

## Content Status
ACTIVE

## Qualified Name
GovernanceStrategy::SalesForecast::DataGovernance::1.0

## GUID

___

# GO-04: Create Threat

# Create Threat

## Display Name
CRM Data Quality Degradation

## Summary
Poor CRM data quality leading to inaccurate sales forecasts and unreliable
pipeline reporting.

## Domain Identifier
DATA

## Importance
High

## Implications
Inaccurate forecasts presented to board
Pipeline coverage ratio inflated by duplicate records

## Outcomes
CRM data quality score above 95 percent

## Content Status
ACTIVE

## Qualified Name
Threat::SalesForecast::CRMDataQualityDegradation::1.0

## GUID

___

# GO-05: Create Regulation — with Regulation Source (Simple) and Regulators (Simple List)

# Create Regulation

## Display Name
Sales Forecast Disclosure Requirements

## Summary
Internal regulation governing the standards for sales forecast disclosure
to the board and external stakeholders.

## Domain Identifier
CORPORATE

## Regulation Source
Example Corp Board Governance Policy v3.2

## Regulators
Board Audit Committee
Chief Financial Officer
External Auditors

## Scope
All forecasts presented to the board or included in external disclosures.

## Importance
Critical

## Content Status
ACTIVE

## Qualified Name
Regulation::SalesForecast::DisclosureRequirements::1.0

## GUID

___

# GO-06: Create Regulation Article — Content Status DRAFT to test non-ACTIVE value

# Create Regulation Article

## Display Name
SF Disclosure Reg Article 3 — Data Lineage Attestation

## Summary
All forecast data must have documented lineage from source CRM records
to the final board-presented figures.

## Domain Identifier
CORPORATE

## Content Status
DRAFT

## Qualified Name
RegulationArticle::SalesForecast::DisclosureReg::Article3::1.0

## GUID

___

---

# ===== SECTION 2: GOVERNANCE POLICIES =====

# GO-07: Create Governance Policy

# Create Governance Policy

## Display Name
Sales Forecast Data Quality Policy

## Summary
All data used in sales forecasting must meet defined quality thresholds
before use in board-presented forecasts.

## Domain Identifier
DATA

## Scope
All data assets in the SalesAnalytics governance zone.

## Importance
Critical

## Implications
Forecast generation must include automated data quality checks
Data quality failures must be reported before board submission

## Outcomes
Zero unresolved critical data quality failures in any board forecast

## Authors
jane.smith@example.com

## Content Status
ACTIVE

## Qualified Name
GovernancePolicy::SalesForecast::DataQuality::1.0

## GUID

___

# GO-08: Create Governance Principle

# Create Governance Principle

## Display Name
Single Source of Truth for Pipeline Data

## Summary
CRM opportunity records are the authoritative source of pipeline data
for all Sales Forecasting purposes.

## Domain Identifier
DATA

## Importance
High

## Content Status
ACTIVE

## Qualified Name
GovernancePrinciple::SalesForecast::SingleSourceOfTruth::1.0

## GUID

___

# GO-09: Create Governance Obligation

# Create Governance Obligation

## Display Name
Monthly CRM Data Quality Review

## Summary
The Data Governance team must conduct a monthly review of CRM data quality
for all open opportunities used in the sales forecast.

## Domain Identifier
DATA

## Scope
All CRM opportunity records in Commit or Best Case pipeline stages.

## Importance
High

## Outcomes
Monthly data quality report produced and distributed
Critical issues resolved within 5 business days

## Content Status
ACTIVE

## Qualified Name
GovernanceObligation::SalesForecast::MonthlyCRMReview::1.0

## GUID

___

# GO-10: Create Governance Approach

# Create Governance Approach

## Display Name
Automated CRM Data Validation

## Summary
CRM data quality is enforced through automated validation rules applied
at the point of export to the forecast pipeline.

## Domain Identifier
DATA

## Importance
High

## Content Status
ACTIVE

## Qualified Name
GovernanceApproach::SalesForecast::AutomatedCRMValidation::1.0

## GUID

___

---

# ===== SECTION 3: GOVERNANCE CONTROLS =====

> All commands in this section use Governance Control Base bundle.
> Implementation Description (Simple) is the key additional attr.
> Domain Identifier (Enum) and Content Status (Valid Value) both available.

# GO-11: Create Governance Control

# Create Governance Control

## Display Name
CRM Export Validation Control

## Summary
Automated control that validates CRM opportunity data quality at export.

## Domain Identifier
DATA

## Implementation Description
Python validation script deployed in the Salesforce export ETL pipeline.
Validates required fields, stage values, amount ranges, and close date logic.
Failures are written to the data quality log and trigger an alert to the steward.

## Importance
Critical

## Content Status
ACTIVE

## Qualified Name
GovernanceControl::SalesForecast::CRMExportValidation::1.0

## GUID

___

# GO-12: Create Governance Rule

# Create Governance Rule

## Display Name
CRM Opportunity Amount Must Be Positive

## Summary
All CRM opportunity records used in the forecast must have a positive amount value.

## Implementation Description
Rule deployed in the export validation pipeline. Records with amount <= 0
are rejected and written to the data quality exception log.

## Domain Identifier
DATA

## Content Status
ACTIVE

## Qualified Name
GovernanceRule::SalesForecast::OpportunityAmountPositive::1.0

## GUID

___

# GO-13: Create Governance Responsibility

# Create Governance Responsibility

## Display Name
Sales Forecast Data Steward Responsibility

## Summary
The designated data steward reviews and resolves CRM data quality issues
before each forecast cycle.

## Implementation Description
Assigned to the Sales Analytics data steward role. Steward must review the
monthly data quality report, resolve critical issues within 5 business days,
and attest data quality before forecast submission.

## Domain Identifier
DATA

## Content Status
ACTIVE

## Qualified Name
GovernanceResponsibility::SalesForecast::DataSteward::1.0

## GUID

___

# GO-14: Create Governance Procedure

# Create Governance Procedure

## Display Name
Sales Forecast Data Quality Attestation Procedure

## Summary
Manual procedure for attesting data quality before each board forecast submission.

## Implementation Description
Performed manually by the designated data steward. Attestation recorded in the
governance portal and attached to the forecast submission record.

## Domain Identifier
DATA

## Content Status
ACTIVE

## Qualified Name
GovernanceProcedure::SalesForecast::DataQualityAttestation::1.0

## GUID

___

# GO-15: Create Service Level Objective

# Create Service Level Objective

## Display Name
Sales Forecast Pipeline SLOs

## Summary
Performance and availability objectives for the Sales Forecast pipeline.

## Implementation Description
SLOs monitored via the pipeline observability dashboard. Breaches trigger
automated alerts to the data engineering team.

## Domain Identifier
DATA

## Outcomes
Pipeline data freshness within 24 hours
Processing latency under 2 hours for full forecast run
99.5 percent availability during forecast cycles

## Content Status
ACTIVE

## Qualified Name
ServiceLevelObjective::SalesForecast::Pipeline::1.0

## GUID

___

# GO-16: Create Methodology

# Create Methodology

## Display Name
Sales Forecast Governance Framework

## Summary
The overall methodology used to govern the Sales Forecasting data domain.

## Domain Identifier
DATA

## Content Status
ACTIVE

## Qualified Name
Methodology::SalesForecast::GovernanceFramework::1.0

## GUID

___

# GO-17: Create Governance Action

# Create Governance Action

## Display Name
Remediate Duplicate CRM Opportunities

## Summary
Identify and merge duplicate CRM opportunity records in the Sales Forecast pipeline.

## Domain Identifier
DATA

## Importance
High

## Content Status
ACTIVE

## Qualified Name
GovernanceAction::SalesForecast::RemediateDuplicateCRM::1.0

## GUID

___

# GO-18: Create Data Processing Purpose

# Create Data Processing Purpose

## Display Name
Sales Forecast Revenue Projection

## Summary
Processing CRM opportunity data to project Q1 2026 revenue for board reporting.

## Domain Identifier
PRIVACY

## Scope
Q1 2026 forecast cycle only. Data retained for 7 years per audit policy.

## Content Status
ACTIVE

## Qualified Name
DataProcessingPurpose::SalesForecast::RevenueProjection::Q1-2026::1.0

## GUID

___

# GO-19: Create Governance Metric — Measurement (Simple) and Target (Simple)

# Create Governance Metric

## Display Name
CRM Data Quality Score

## Summary
Percentage of CRM opportunity records passing all data quality validation rules.

## Domain Identifier
DATA

## Measurement
Percentage of open opportunity records passing all automated validation rules.

## Target
95 percent or above.

## Importance
High

## Content Status
ACTIVE

## Qualified Name
GovernanceMetric::SalesForecast::CRMDataQualityScore::1.0

## GUID

___

# GO-20: Create Naming Standard Rule — Name Patterns (Simple List)

# Create Naming Standard Rule

## Display Name
Sales Forecast Qualified Name Standard

## Summary
Naming standard for all Qualified Names in the Sales Forecast governance domain.

## Implementation Description
Pattern enforced by Dr.Egeria validation on Create commands.

## Name Patterns
<ElementType>::SalesForecast::<ElementName>::<Version>
<ElementType>::SalesForecast::<SubDomain>::<ElementName>::<Version>

## Domain Identifier
DATA

## Content Status
ACTIVE

## Qualified Name
NamingStandardRule::SalesForecast::QualifiedNameStandard::1.0

## GUID

___

# GO-21: Create Notification Type — notification-specific custom attrs

> Planned Start Date, Planned Completion Date — Simple (ISO-8601 date string)
> Multiple Notifications Permitted — Bool
> Notification Interval, Minimum Notification Interval — Simple Int (milliseconds)
> Next Scheduled Notification — Simple (ISO-8601 datetime string)
> Notification Count — Simple Int

# Create Notification Type

## Display Name
CRM Data Quality Breach Alert

## Summary
Notification triggered when CRM data quality score falls below the 95 percent target.

## Domain Identifier
DATA

## Planned Start Date
2026-01-01

## Planned Completion Date
2026-12-31

## Multiple Notifications Permitted
True

## Notification Interval
86400000

## Minimum Notification Interval
3600000

## Next Scheduled Notification
2026-04-01T07:00:00Z

## Notification Count
0

## Content Status
ACTIVE

## Qualified Name
NotificationType::SalesForecast::CRMDataQualityBreachAlert::1.0

## GUID

___

# GO-22: Create Data Lens — geographic (Simple Float), temporal (Simple), scope (Dictionary)

# Create Data Lens

## Display Name
Sales Forecast North America Data Lens

## Summary
Geographic data lens scoping Sales Forecast data collection to North America.

## Domain Identifier
DATA

## Min Latitude
24.396308

## Max Latitude
49.384358

## Min Longitude
-125.0

## Max Longitude
-66.93457

## Min Height
0.0

## Max Height
0.0

## Data Collection Start Time
2026-01-01T00:00:00Z

## Data Collection End Time
2026-03-31T23:59:59Z

## Scope Elements
{"region": "NorthAmerica", "territories": "US,CA,MX", "currency": "USD"}

## Content Status
ACTIVE

## Qualified Name
DataLens::SalesForecast::NorthAmerica::Q1-2026::1.0

## GUID

___

---

# ===== SECTION 4: GOVERNANCE DEFINITION (base type) =====

# GO-23: Create Governance Definition — DRAFT, then Update to ACTIVE via QN

# Create Governance Definition

## Display Name
Sales Forecast Governance Framework Definition

## Summary
Umbrella governance definition covering the Sales Forecast domain.

## Domain Identifier
DATA

## Content Status
DRAFT

## Qualified Name
GovernanceDefinition::SalesForecast::FrameworkDefinition::1.0

## GUID

___

# Update Governance Definition

## Display Name
Sales Forecast Governance Framework Definition

## Qualified Name
GovernanceDefinition::SalesForecast::FrameworkDefinition::1.0

## Content Status
ACTIVE

## Description
Umbrella governance definition for the Sales Forecast domain, incorporating
Q1 2026 lessons learned and updated data quality thresholds.

## Journal Entry
Updated and promoted to ACTIVE following Q1 2026 governance review 2026-03-20.

___

---

# ===== SECTION 5: TERMS AND CONDITIONS, CERTIFICATION, LICENSING =====

> Bundle: Terms and Conditions inherits Governance Control Base.
> Adds: Entitlements (Dictionary), Obligations (Dictionary), Restrictions (Dictionary).
> Domain Identifier (Enum), Content Status (Valid Value), Implementation Description (Simple) available.

# GO-24: Create Certification Type

# Create Certification Type

## Display Name
Sales Forecast Data Quality Certification

## Summary
Certification awarded to data assets meeting Sales Forecast data quality
standards for board reporting.

## Domain Identifier
DATA

## Implementation Description
Certification valid for one forecast cycle. Awarded by the data steward
following the monthly data quality review.

## Entitlements
{"use_in_board_forecast": "permitted", "use_in_regulatory_disclosure": "permitted"}

## Obligations
{"monthly_quality_review": "required", "steward_attestation": "required"}

## Restrictions
{"use_without_attestation": "forbidden", "share_externally_without_approval": "forbidden"}

## Content Status
ACTIVE

## Qualified Name
CertificationType::SalesForecast::DataQuality::1.0

## GUID

___

# GO-25: Create License Type

# Create License Type

## Display Name
Sales Forecast Data Consumer License

## Summary
License governing the use of Sales Forecast data products by internal consumers.

## Domain Identifier
DATA

## Entitlements
{"read_forecast_outputs": "permitted", "export_to_excel": "permitted"}

## Obligations
{"report_usage_quarterly": "required"}

## Restrictions
{"redistribute_externally": "forbidden", "modify_forecast_figures": "forbidden"}

## Content Status
ACTIVE

## Qualified Name
LicenseType::SalesForecast::DataConsumer::1.0

## GUID

___

# GO-26: Create Terms and Conditions

# Create Terms and Conditions

## Display Name
Sales Forecast Data Sharing Terms and Conditions

## Summary
Terms and conditions governing data sharing agreements for Sales Forecast data.

## Entitlements
{"read_access": "permitted", "dashboard_access": "permitted"}

## Obligations
{"quarterly_usage_report": "required", "notify_on_data_breach": "immediately"}

## Restrictions
{"sublicensing": "forbidden", "use_for_performance_management": "forbidden"}

## Content Status
ACTIVE

## Qualified Name
TermsAndConditions::SalesForecast::DataSharing::1.0

## GUID

___

---

# ===== SECTION 6: SECURITY ACCESS CONTROL AND GOVERNANCE ZONE =====

> Bundle: Security Access Control inherits Governance Control Base.
> Domain Identifier (Enum), Content Status (Valid Value), Implementation Description (Simple) available.
> Create Governance Zone adds Criteria (Simple) as a custom attr.

# GO-27: Create Security Access Control

# Create Security Access Control

## Display Name
Sales Forecast Board Report Access Control

## Summary
Access control governing read access to the board-level Sales Forecast report.

## Domain Identifier
SECURITY

## Implementation Description
Row-level security policy in the reporting platform. Access granted via
membership in the BoardForecastReaders security group.

## Content Status
ACTIVE

## Qualified Name
SecurityAccessControl::SalesForecast::BoardReportAccess::1.0

## GUID

___

# GO-28: Create Governance Zone — Criteria (Simple)

# Create Governance Zone

## Display Name
SalesAnalytics Zone

## Summary
Governance zone encompassing all data assets used in Sales Analytics
and Sales Forecasting functions.

## Description
The SalesAnalytics governance zone defines the boundary within which
Sales Analytics data policies, controls, and quality standards apply.

## Criteria
Elements are included if they are used in the production or consumption of
Sales Forecast data, including CRM records, pipeline aggregations,
revenue projections, and governance definitions.

## Domain Identifier
DATA

## Content Status
ACTIVE

## Qualified Name
GovernanceZone::SalesAnalytics::1.0

## GUID

___

---

# ===== SECTION 7: LINK COMMANDS =====

> All 14 Link commands use Link Command Base bundle (Description, Label from Request Base).
> No GUID on any Link command.
> All dates — Simple (ISO-8601). Activity Status — Valid Value (see list above).

# GO-29: Link Governance Response — Driver (input_required), Policy (input_required)

# Link Governance Response

## Driver
BusinessImperative::SalesForecast::Accuracy::1.0

## Policy
GovernancePolicy::SalesForecast::DataQuality::1.0

## Rationale
The Data Quality Policy is the primary policy response to the Sales Forecast
Accuracy business imperative.

___

# GO-30: Link Governance Response — second, verb Attach

# Attach Governance Response

## Driver
Threat::SalesForecast::CRMDataQualityDegradation::1.0

## Policy
GovernancePolicy::SalesForecast::DataQuality::1.0

## Rationale
The Data Quality Policy directly mitigates the CRM Data Quality Degradation threat.

___

# GO-31: Link Governance Mechanism — Policy (input_required), Mechanism

# Link Governance Mechanism

## Policy
GovernancePolicy::SalesForecast::DataQuality::1.0

## Mechanism
GovernanceControl::SalesForecast::CRMExportValidation::1.0

## Rationale
The CRM Export Validation Control implements the Data Quality Policy.

___

# GO-32: Link Governed By — Governance Definition (input_required), Referenceable (input_required)

# Link Governed By

## Governance Definition
GovernancePolicy::SalesForecast::DataQuality::1.0

## Referenceable
DigitalProduct::SalesForecast::Pipeline::1.2

___

# GO-33: Link Governed By — second element, verb Add

# Add Governed By

## Governance Definition
GovernanceZone::SalesAnalytics::1.0

## Referenceable
Collection::SalesForecast::Master::1.0

___

# GO-34: Link Governance Drivers — peer link (both input_required)

# Link Governance Drivers

## Governance Driver 1
BusinessImperative::SalesForecast::Accuracy::1.0

## Governance Driver 2
Threat::SalesForecast::CRMDataQualityDegradation::1.0

___

# GO-35: Link Governance Policies — peer link (both input_required)

# Link Governance Policies

## Governance Policy 1
GovernancePrinciple::SalesForecast::SingleSourceOfTruth::1.0

## Governance Policy 2
GovernanceObligation::SalesForecast::MonthlyCRMReview::1.0

___

# GO-36: Link Governance Controls — peer link (both input_required)

# Link Governance Controls

## Governance Control 1
GovernanceControl::SalesForecast::CRMExportValidation::1.0

## Governance Control 2
GovernanceRule::SalesForecast::OpportunityAmountPositive::1.0

___

# GO-37: Link Zone Hierarchy — Parent Zone (input_required), Child Zone (input_required)

# Link Zone Hierarchy

## Parent Zone
GovernanceZone::SalesAnalytics::1.0

## Child Zone
GovernanceZone::SalesForecast::DataStructures::1.0

___

# GO-38: Link Regulation Certification Type — Certification Type (input_required)

# Link Regulation Certification Type

## Regulation
Regulation::SalesForecast::DisclosureRequirements::1.0

## Certification Type
CertificationType::SalesForecast::DataQuality::1.0

___

# GO-39: Link Certification — full attribute coverage

> Certification Type (input_required Reference Name), Referenceable (input_required Reference Name).
> Certificate GUID, Certified By, Conditions, Custodian, Recipient — all Simple.
> Start Date, End Date — Simple (ISO-8601 date strings).
> Entitlements, Obligations, Restrictions — Dictionary.

# Link Certification

## Certification Type
CertificationType::SalesForecast::DataQuality::1.0

## Referenceable
DigitalProduct::SalesForecast::Pipeline::1.2

## Certificate GUID
CERT-SF-DQ-2026-Q1-001

## Certified By
Jane Smith, Sales Analytics Data Steward

## Recipient
Sales Forecast Pipeline v1.2

## Conditions
Certification valid for Q1 2026 forecast cycle only.

## Custodian
Data Governance Team

## Start Date
2026-01-01

## End Date
2026-03-31

## Entitlements
{"use_in_board_forecast": "permitted"}

## Obligations
{"monthly_review": "required"}

## Restrictions
{"use_without_attestation": "forbidden"}

___

# GO-40: Link License — full attribute coverage

> License Type (input_required Reference Name), Referenceable (input_required Reference Name).
> License GUID, Licensed By, Licensee, Custodian, Conditions — all Simple.
> Start Date, End Date — Simple (ISO-8601 date strings).
> Entitlements, Obligations, Restrictions — Dictionary.

# Link License

## License Type
LicenseType::SalesForecast::DataConsumer::1.0

## Referenceable
Agreement::SalesForecast::Finance::DataSharing::1.0

## License GUID
LIC-SF-DC-2026-FINANCE-001

## Licensed By
Data Governance Office — Example Corp

## Licensee
Finance Department — Example Corp

## Custodian
Data Governance Team

## Start Date
2026-01-01

## End Date
2026-12-31

## Conditions
License renewable annually subject to usage review.

## Entitlements
{"read_forecast_outputs": "permitted", "export_to_excel": "permitted"}

## Obligations
{"quarterly_usage_report": "required"}

## Restrictions
{"redistribute_externally": "forbidden"}

___

# GO-41: Link Agreement Terms and Conditions

> Terms & Conditions Id (input_required Reference Name),
> Agreement Name (input_required Reference Name).

# Link Agreement Terms and Conditions

## Terms & Conditions Id
TermsAndConditions::SalesForecast::DataSharing::1.0

## Agreement Name
Agreement::SalesForecast::Finance::DataSharing::1.0

___

# GO-42: Link Associated Group — Access Control, Security Group (Reference Names), Operation Name (Simple)

# Link Associated Group

## Access Control
SecurityAccessControl::SalesForecast::BoardReportAccess::1.0

## Security Group
SecurityGroup::SalesForecast::BoardForecastReaders::1.0

## Operation Name
read_board_forecast_report

___

# GO-43: Link Monitored Resource — Notification Type → Monitored Resource

# Link Monitored Resource

## Notification Type
NotificationType::SalesForecast::CRMDataQualityBreachAlert::1.0

## Monitored Resource
ExternalDataSource::Salesforce::OpportunityFeed::Daily::1.0

___

# GO-44: Link Notification Subscriber

> Activity Status — Valid Value: REQUESTED, APPROVED, WAITING, ACTIVATING, IN_PROGRESS,
>   PAUSED, COMPLETED, INVALID, IGNORED, FAILED, CANCELLED, ABANDONED, OTHER
> Last Notification — Simple (ISO-8601 datetime string).

# Link Notification Subscriber

## Notification Type
NotificationType::SalesForecast::CRMDataQualityBreachAlert::1.0

## Subscriber
GovernanceResponsibility::SalesForecast::DataSteward::1.0

## Activity Status
APPROVED

## Last Notification
2026-03-15T08:30:00Z

___

# GO-45: Detach Governance Response — removes GO-30

# Detach Governance Response

## Driver
Threat::SalesForecast::CRMDataQualityDegradation::1.0

## Policy
GovernancePolicy::SalesForecast::DataQuality::1.0

___

# GO-46: Unlink Governed By — removes GO-33

# Unlink Governed By

## Governance Definition
GovernanceZone::SalesAnalytics::1.0

## Referenceable
Collection::SalesForecast::Master::1.0

___

> End of Governance Officer happy path tests.
>
> Expected outcomes:
>
> CREATE (GO-01 to GO-28):
>   All commands   : GUID filled, QN preserved or auto-generated, verb swapped to Update
>   GO-01          : Domain Identifier=CORPORATE (Enum), Content Status=ACTIVE (Valid Value)
>   GO-06          : Content Status=DRAFT — tests non-ACTIVE Content Status value
>   GO-11 to GO-22 : Implementation Description (Simple) in output for all Control Base commands
>   GO-19          : Measurement (Simple) and Target (Simple) in output
>   GO-20          : Name Patterns (Simple List) in output
>   GO-21          : Bool, Simple Int, Simple ISO-date notification attrs accepted
>   GO-22          : Simple Float geographic attrs and Dictionary Scope Elements accepted
>   GO-23          : Create with Content Status=DRAFT; Update sets it to ACTIVE — both verified
>   GO-24 to GO-26 : Entitlements, Obligations, Restrictions (Dictionary) in output
>
> LINK (GO-29 to GO-46):
>   All commands   : Executed; no GUID slot in output
>   GO-30          : Attach synonym accepted for Link Governance Response
>   GO-33          : Add synonym accepted for Link Governed By
>   GO-39          : All Link Certification attrs including Dictionaries accepted
>   GO-40          : All Link License attrs including Dictionaries accepted
>   GO-41          : Terms & Conditions Id and Agreement Name (both Reference Names) accepted
>   GO-44          : Activity Status=APPROVED (valid value from REQUESTED;APPROVED;... list)
>   GO-45          : Detach removes governance response link
>   GO-46          : Unlink removes governed by link