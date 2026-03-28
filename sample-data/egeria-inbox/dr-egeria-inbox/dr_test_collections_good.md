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
> Verb synonyms in use:
>   Relationship establishment — Add, Link, Attach (all equivalent)
>   Relationship removal      — Detach, Unlink, Remove (all equivalent)

---

# HP-01: Create Collection — smoke test, QN auto-generated

> Minimal valid command: Display Name only (the one required field).
> Expected: GUID filled, QN auto-generated (non-empty), verb swapped to Update Collection.

# Create Collection

## Display Name
Sales Forecast Smoke Test

___

# HP-02: Create Collection — common optional fields, QN auto-generated

> Exercises Description, Category (with alt label Category Name), Content Status (Valid Value),
> Version Identifier (with alt label Version), Search Keywords (Simple List),
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
ACTIVE

## Version Identifier
1.0

## Qualified Name
Collection::SalesForecast::Master::1.0

## GUID

___

# HP-04: Create Collection — alternative command name (Folder)

> Tests that the alias Folder is recognised as Create Collection.
> Expected: processed identically to Create Collection.

# Folder

## Display Name
SF-AltName-Test

## Description
Verifies that the alternative command name Folder is recognised as Create Collection.

## Qualified Name
Collection::SalesForecast::AltNameTest::1.0

## GUID

___

# HP-05: Update Collection — identify by user-specified QN

> Update flavor. Element identified by Qualified Name — no GUID required.
> Only changed fields need to be provided; Merge Update defaults to True.
> Expected: matching element updated, output shows filled GUID.

# Update Collection

## Display Name
Sales Forecast Master Collection

## Qualified Name
Collection::SalesForecast::Master::1.0

## Content Status
ACTIVE

## Journal Entry
Status promoted to ACTIVE following governance board approval on 2026-03-20.

## GUID

___

# HP-06: Update Collection — identify by Display Name only

> No QN provided. Dr.Egeria forms a QN from Display Name and attempts to match.
> Expected: element matched and updated, QN filled in output.

# Update Collection

## Display Name
Sales Forecast Smoke Test

## Description
Updated description added after initial smoke test creation.

## GUID

___

# HP-07: Create Root Collection

> Creates a RootCollection. User-specified QN for reliable downstream reference.

# Create Root Collection

## Display Name
Sales Forecast Hierarchy Root

## Description
Root collection for the entire Sales Forecasting metadata hierarchy.

## Purpose
Serve as the top-level anchor for all Sales Forecast sub-collections.

## Content Status
ACTIVE

## Version Identifier
1.0

## Qualified Name
Collection::SalesForecast::Root::1.0

## GUID

___

# HP-08: Create Collection Folder — nested under root

> Creates a CollectionFolder. Tests Parent ID (Reference Name) and
> Parent Relationship Type Name per spec: CollectionMembership when
> the folder is inside another collection.

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
ACTIVE

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
ACTIVE

## Version Identifier
1.0

## Qualified Name
Collection::WorkItemList::SalesForecast::DataQuality::1.0

## GUID

___

# HP-14: Add Member to Collection — minimal, verb Add

> Minimum required for membership: Collection Id and Element Id only.

# Add Member to Collection

## Collection Id
Collection::SalesForecast::Root::1.0

## Element Id
Collection::SalesForecast::DataStructures::1.0


___

# HP-15: Add Member to Collection — Domain-level attributes

> Exercises Domain-level membership attributes processed in both basic and advanced mode:
> Membership Status (Valid Value), Membership Rationale, Notes.

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

# HP-16: Add Member to Collection — Advanced attributes, verb synonym Link

> Uses establish synonym Link and all Advanced-level membership attributes:
> Expression, Confidence, Steward, Steward Type Name, Steward Property Name,
> Source, User Defined Status.
>
> In BASIC mode: Advanced attributes must be silently skipped.
>   Membership Status, Membership Rationale, Notes (Domain) still processed.
> In ADVANCED mode: all fields must appear in output.

# Add Member to Collection

## Collection Id
Collection::SalesForecast::Master::1.0

## Element Id
DatabricksUnityCatalogServer:CreateAndSurveyGovernanceActionProcess
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

# HP-17: Attach Collection to Resource — using an existing project as resource

> Demonstrates that the resource endpoint can be any existing Egeria element,
> not just catalogs. Uses the project Campaign:Clinical Trials Management.
> Tests Resource Description, Resource Use (freeform), Watch Resource (Bool).
> Verb: Attach.

# Attach Collection to Resource

## Collection Id
Collection::SalesForecast::Master::1.0

## Element Id
Campaign:Clinical Trials Management

## Resource Description
Clinical Trials Management project linked as a downstream consumer of Sales Forecast
governance definitions for cross-domain reporting purposes.

## Resource Use
Generate Insight 

## Watch Resource
True


___

# HP-18: Attach Collection to Resource — full Resource List attributes

> Tests Resource Id (Reference Name), Resource Properties (Dictionary),
> Resource Use, Watch Resource.
> Verb: Attach (synonym for Link).

# Attach Collection to Resource

## Collection Id
Collection::SalesForecast::Master::1.0

## Element Id
DigitalProduct::OpenMetadataDigitalProduct::LOCATIONS-LIST::List of Locations_dataSpec

## Resource Description
Enterprise data catalog providing lineage and provenance for all Sales Forecast
domain metadata elements.

## Resource Id
DatabricksUnityCatalogServer:CreateAndSurveyGovernanceActionProcess

## Resource Use
Generate Insight

## Watch Resource
True

## Resource Properties
{"catalog_version": "3.2", "refresh_schedule": "daily", "owner_team": "Sales Analytics"}


___

# HP-19: Detach Member from Collection — verb Detach

> Removes the membership established in HP-14.
> Only Collection Id and Element Id needed to identify the relationship.
> Detach, Unlink, and Remove are all equivalent removal verbs.

# Detach Member from Collection

## Collection Id
Collection::SalesForecast::Root::1.0

## Element Id
Collection::SalesForecast::DataStructures::1.0


___

# HP-20: Unlink Collection from Resource — verb Unlink

> Removes the ResourceList relationship established in HP-17.
> Unlink used here; Detach and Remove are equivalent synonyms.

# Unlink Collection from Resource

## Collection Id
Collection::SalesForecast::Master::1.0

## Element Id
Campaign:Clinical Trials Management



___

> End of happy path tests.
>
> Expected outcomes:
>   HP-01 to HP-13 : All Create/Update commands executed. GUIDs filled. Create verb swapped to Update.
>   HP-03, HP-07 to HP-13 : QN in output matches user-specified value exactly.
>   HP-01, HP-02, HP-06 : QN in output is auto-generated (non-empty).
>   HP-05, HP-06 : Update commands locate and update existing elements.
>   HP-14 to HP-18 : Relationship commands executed. GUIDs filled.
>   HP-19, HP-20 : Relationships removed.
>   HP-16 in basic mode : Expression, Confidence, Steward fields silently skipped.
>   HP-16 in advanced mode : All fields present in output.