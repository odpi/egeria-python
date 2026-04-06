
# HP-17: Add Member to Collection — minimal, verb Add

> Minimum required for membership: Collection Id and Element Id only.
> No GUID on relationship commands — identified by endpoints.

# Add Member to Collection

## Collection Id
Collection::SalesForecast::Root::1.0

## Element Id
Collection::SalesForecast::DataStructures::1.0
## Membership Status

___

# HP-18: Add Member to Collection — Domain-level attributes

> Exercises Domain-level membership attributes: Membership Status (Valid Value),
> Membership Rationale (Simple), Notes (Simple).

# Add Member to Collection

## Collection Id
Collection::SalesForecast::Master::1.0

## Element Id
Collection::SalesForecast::DataStructures::1.0


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
DataStructure::CRMOpportunity::Salesforce::1.0



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
