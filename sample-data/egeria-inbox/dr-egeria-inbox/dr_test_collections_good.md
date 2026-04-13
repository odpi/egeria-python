# Collections Family — Happy Path Tests
# Sales Forecast Theme

> This document tests the Dr.Egeria Collections command family under normal conditions.
> All commands are expected to succeed when processed.
>
> Run with VALIDATE first, then PROCESS.
>
> Key principle: Create commands that are referenced by later commands in this document
> always carry a user-specified Qualified Name. This allows reliable cross-referencing
> within the document without needing system-generated GUIDs.
>
> GUID appears only in Create commands — system fills it on first processing.
> Update commands are identified by Qualified Name — no GUID.
> Relationship commands (Add Member, Attach Collection, Detach, Unlink) are identified
> by their endpoint attributes — no GUID.
>
> Verb synonyms:
>   Establishment — Add, Link, Attach (all equivalent)
>   Removal       — Detach, Unlink, Remove (all equivalent)
>
> Content Status valid values: DRAFT, PREPARED, PROPOSED, APPROVED, REJECTED,
>                               PROPOSED, DEPRECATED, OTHER
> Membership Status valid values: UNKNOWN, DISCOVERED, PROPOSED, IMPORTED,
>                                  VALIDATED, DEPRECATED, OBSOLETE, OTHER

---

# HP-01: Create Collection — smoke test, QN auto-generated

> Minimal valid command: Display Name only (the one required field).
> Expected: GUID filled, QN auto-generated (non-empty), verb swapped to Update Collection.

# Create Collection

## Display Name
Sales Forecast Smoke Test

## GUID

___

# HP-02: Create Collection — common optional fields, QN auto-generated

> Exercises Description, Category (alt label Category Name), Content Status (Valid Value),
> Version Identifier (alt label Version), Search Keywords (Simple List),
> Authors (Simple List), URL, Journal Entry, Purpose (Collection Base own attr).
> QN left empty to verify auto-generation.

# Create Collection

## Display Name
Sales Forecast Reference Collections

## Description
A collection grouping reference materials used across the Sales Forecasting domain,
including data dictionaries, governance policies, and approved data sources.

## Category Name
Sales Forecasting

## Purpose
To provide a single governed location for all reference materials supporting
the Q1 2026 Sales Forecast initiative.

## Content Status
DRAFT

## Version
0.1

## Search Keywords
sales forecast, reference, governance, CRM

## Authors
data.governance@example.com

## URL
https://wiki.example.com/sales-forecast-governance

## Journal Entry
Initial creation as part of Q1 2026 Sales Forecast governance initiative.

## Qualified Name

## GUID

___

# HP-03: Create Collection — user-specified QN preserved

> QN is explicitly provided. Expected: QN in output matches input exactly.
> This collection is referenced by later commands in this document.

# Create Collection

## Display Name
Sales Forecast Master Collection

## Description
Master collection holding all metadata elements related to the Sales Forecasting domain.
Primary governance container for the Q1 2026 forecasting initiative.

## Purpose
Central governance container for all Sales Forecast metadata and lineage.

## Content Status
PROPOSED

## Version Identifier
1.0

## Qualified Name
Collection::SalesForecast::Master::1.0

## GUID

___

# HP-04: Create Collection — alternative command name (Folder)

> Tests that the alias Folder is recognised as Create Collection.

# Folder

## Display Name
SF-AltName-Test

## Description
Verifies that the alternative command name Folder is recognised as Create Collection.

## Qualified Name
Collection::SalesForecast::AltNameTest::1.0

## GUID

___

# HP-05: Update Collection — identified by Qualified Name

> Update flavor. No GUID. Element located by Qualified Name.
> Only changed fields provided; Merge Update defaults to True.

# Update Collection

## Display Name
Sales Forecast Master Collection

## Qualified Name
Collection::SalesForecast::Master::1.0

## Content Status
PROPOSED

## Journal Entry
Status confirmed PROPOSED following governance board approval on 2026-03-20.

___

# HP-06: Update Collection — identified by Display Name only

> No QN provided. Dr.Egeria forms a QN from Display Name and attempts to match.
> Expected: element matched and updated, QN filled in output.

# Update Collection

## Display Name
Sales Forecast Smoke Test

## Description
Updated description added after initial smoke test creation.

___

# HP-07: Create Root Collection

# Create Root Collection

## Display Name
Sales Forecast Hierarchy Root

## Description
Root collection for the entire Sales Forecasting metadata hierarchy.

## Purpose
Serve as the top-level anchor for all Sales Forecast sub-collections.

## Content Status
PROPOSED

## Version Identifier
1.0

## Qualified Name
Collection::SalesForecast::Root::1.0

## GUID

___

# HP-08: Create Collection Folder — nested under root

> Tests Parent ID (Reference Name) and Parent Relationship Type Name (Simple).
> Per spec: Parent Relationship Type Name is CollectionMembership when folder
> is inside another collection.

# Create Collection Folder

## Display Name
Sales Forecast Data Structures

## Description
Folder organising all data structure definitions used in the Sales Forecasting domain.

## Parent ID
Collection::SalesForecast::Root::1.0

## Parent Relationship Type Name
CollectionMembership

## Content Status
PROPOSED

## Version Identifier
1.0

## Qualified Name
Collection::SalesForecast::DataStructures::1.0

## GUID

___

# HP-09: Create Home Collection

# Create Home Collection

## Display Name
Jane Smith — Sales Forecast Favourites

## Description
Personal favourites collection for Jane Smith, Sales Analytics team.

## Qualified Name
Collection::HomeCollection::JaneSmith::SalesForecast::1.0

## GUID

___

# HP-10: Create Namespace

# Create Namespace

## Display Name
SalesForecast Namespace

## Description
Namespace collection grouping all elements within the SalesForecast domain
to ensure naming consistency and avoid qualified name collisions.

## Qualified Name
Collection::Namespace::SalesForecast::1.0

## GUID

___

# HP-11: Create Results Set

# Create Results Set

## Display Name
Q1 2026 Forecast Query Results

## Description
Results set produced by the Q1 2026 sales pipeline query run on 2026-03-15.
Contains all opportunities in Commit or Best Case stage with close date in Q1.

## Version Identifier
1.0

## Qualified Name
Collection::ResultsSet::SalesForecast::Q1-2026::1.0

## GUID

___

# HP-12: Create Recent Access

# Create Recent Access

## Display Name
Sales Forecast Recent Access — Analytics Team

## Description
Tracks metadata elements recently accessed by the Sales Analytics team
during Q1 2026 forecasting work.

## Qualified Name
Collection::RecentAccess::SalesForecast::AnalyticsTeam::1.0

## GUID

___

# HP-13: Create Work Item List

# Create Work Item List

## Display Name
Sales Forecast Data Quality Work Items

## Description
Work item list tracking outstanding data quality remediation tasks for the
Sales Forecasting pipeline identified during the Q4 2025 quality review.

## Content Status
PROPOSED

## Version Identifier
1.0

## Qualified Name
Collection::WorkItemList::SalesForecast::DataQuality::1.0

## GUID

___

---

# HP-14: Create Security Group — with Distinguished Name (Simple) and Purpose (Simple)

> Security Group is now a Collection-based command (Collection Base bundle).
> Available attrs: Purpose (Simple), Authors (Simple List), Content Status (Valid Value),
> plus all Referenceable attrs (Display Name, Description, QN etc.).
> Distinguished Name is a custom attr (Simple).
> NOT available: Domain Identifier, Importance, Implementation Description
> (those belong to the Governance bundle chain, not Collection Base).

# Create Security Group

## Display Name
Board Forecast Readers

## Description
Members of this group have read access to the board-level Sales Forecast
report and associated data quality attestations.

## Purpose
Control read access to the board-level Sales Forecast report.

## Distinguished Name
cn=BoardForecastReaders,ou=SecurityGroups,dc=example,dc=com

## Authors
jane.smith@example.com

## Content Status
PROPOSED

## Qualified Name
SecurityGroup::SalesForecast::BoardForecastReaders::1.0

## GUID

___

# HP-15: Create Security List — with Distinguished Name

# Create Security List

## Display Name
Sales Forecast Pipeline Identities

## Description
List of system identities authorised to access the Sales Forecast pipeline
data processing infrastructure.

## Purpose
Define the identity list for pipeline infrastructure access control.

## Distinguished Name
cn=SFPipelineIdentities,ou=SecurityLists,dc=example,dc=com

## Content Status
PROPOSED

## Qualified Name
SecurityList::SalesForecast::PipelineIdentities::1.0

## GUID

___

# HP-16: Create Security Role — with Distinguished Name

# Create Security Role

## Display Name
Sales Forecast Data Steward Role

## Description
Role grouping granting data steward permissions across all Sales Forecast
governed data assets in the SalesAnalytics governance zone.

## Purpose
Consolidate data steward access rights for Sales Forecast governance.

## Distinguished Name
cn=SFDataStewardRole,ou=SecurityRoles,dc=example,dc=com

## Content Status
PROPOSED

## Qualified Name
SecurityRole::SalesForecast::DataSteward::1.0

## GUID

___

---

# HP-17: Add Member to Collection — minimal, verb Add

> Minimum required for membership: Collection Id and Element Id only.
> No GUID on relationship commands — identified by endpoints.

# Add Member to Collection

## Collection Id
Collection::SalesForecast::Root::1.0

## Element Id
Collection::SalesForecast::DataStructures::1.0

## Membership Status
PROPOSED
___

# HP-18: Add Member to Collection — Domain-level attributes

> Exercises Domain-level membership attributes: Membership Status (Valid Value),
> Membership Rationale (Simple), Notes (Simple).

# Add Member to Collection

## Collection Id
Collection::SalesForecast::Master::1.0

## Element Id
Collection::SalesForecast::DataStructures::1.0

## Membership Status
VALIDATED

## Membership Rationale
Data Structures folder validated as complete and accurate for Q1 2026 forecasting.

## Notes
Reviewed and approved by Sales Analytics team on 2026-03-01.

___

# HP-19: Add Member to Collection — Advanced attributes, verb synonym Link

> Uses establish synonym Link and all Advanced-level membership attributes:
> Expression (Simple), Confidence (Simple Int), Steward (Simple),
> Steward Type Name (Simple), Steward Property Name (Simple), Source (Simple),
> User Defined Status (Simple).
>
> In BASIC mode: Advanced attributes silently skipped; Membership Status,
>   Membership Rationale, Notes (Domain level) still processed.
> In ADVANCED mode: all fields appear in output.

# Link Member to Collection

## Collection Id
Collection::SalesForecast::Master::1.0

## Element Id
Collection::SalesForecast::DataStructures::1.0

## Membership Status
VALIDATED

## Membership Rationale
CRM Opportunity data is the primary input source for the sales forecasting pipeline.

## Expression
stage IN ('Commit','Best Case') AND close_date >= CURRENT_DATE

## Confidence
92

## Steward
jane.smith@example.com

## Steward Type Name
Person

## Steward Property Name
qualifiedName

## Source
Q4-2025-Data-Quality-Assessment

## Notes
Reviewed and approved by Sales Analytics team on 2026-03-01.

___

# HP-20: Attach Collection to Resource — existing project as resource

> Demonstrates that the resource endpoint can be any existing Egeria element.
> Uses the project Campaign:Clinical Trials Management.
> Resource Use is freeform (Valid Value attr with no values populated in spec).
> Watch Resource — Bool.

# Attach Collection to Resource

## Collection Id
Collection::SalesForecast::Master::1.0

## Element Id
Campaign:Clinical Trials Management

## Resource Description
Clinical Trials Management project linked as a downstream consumer of Sales Forecast
governance definitions for cross-domain reporting purposes.

## Resource Use
Related Information

## Watch Resource
True

___

# HP-21: Attach Collection to Resource — full Resource List attributes

> Tests Resource Id (Reference Name), Resource Properties (Dictionary).

# Attach Collection to Resource

## Collection Id
Collection::SalesForecast::Master::1.0

## Element Id
Campaign:Clinical Trials Management

## Resource Description
Enterprise data catalog providing lineage and provenance for all Sales Forecast
domain metadata elements.

## Resource Id
Collection::SalesForecast::Master::1.0

## Resource Use
Related Information

## Watch Resource
True

## Resource Properties
{"catalog_version": "3.2", "refresh_schedule": "daily", "owner_team": "Sales Analytics"}

___

# HP-22: Detach Member from Collection — verb Detach

> Removes the membership established in HP-17.
> Identified by Collection Id and Element Id — no GUID.

# Detach Member from Collection

## Collection Id
Collection::SalesForecast::Root::1.0

## Element Id
Collection::SalesForecast::DataStructures::1.0

___

# HP-23: Unlink Collection from Resource — verb Unlink

> Removes the ResourceList relationship established in HP-20.

# Unlink Collection from Resource

## Collection Id
Collection::SalesForecast::Master::1.0

## Element Id
Campaign:Clinical Trials Management

___

> End of Collections happy path tests.
>
> Expected outcomes:
>   HP-01 to HP-16 : All Create commands executed. GUIDs filled. Create verb swapped to Update.
>   HP-03, HP-07 to HP-16 : QN in output matches user-specified value exactly.
>   HP-01, HP-02, HP-06 : QN in output is auto-generated (non-empty).
>   HP-02 : Content Status=DRAFT in output (tests non-PROPOSED value).
>   HP-05, HP-06 : Update commands locate and update existing elements. No GUID slot.
>   HP-14 to HP-16 : Security Group/List/Role — Purpose and Distinguished Name in output;
>                    Domain Identifier and Implementation Description NOT present
>                    (Collection Base bundle, not Governance bundle chain).
>   HP-17 to HP-21 : Relationship commands executed. No GUID slot.
>   HP-19 in basic mode : Expression, Confidence, Steward fields silently skipped.
>   HP-19 in advanced mode : All fields present in output.
>   HP-22, HP-23 : Relationships removed. No GUID slot.