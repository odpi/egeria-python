# Collections Family — Mean Path Tests (Error Handling)
# Sales Forecast Theme

> This document tests Dr.Egeria's error handling for the Collections command family.
> Every command below is intentionally malformed in some way.
>
> Run with VALIDATE to confirm each error is detected and reported without writing to Egeria.
> Run with PROCESS to confirm each command is rejected with an informative message
> in the output document, and that subsequent valid commands (if any) still execute.
>
> Each test notes what error is expected and what the correct behaviour should be.

---

# MP-01: Missing required field — Display Name absent

> Display Name is the only required field for Create Collection.
> It is intentionally omitted here.
> Expected: validation error — missing required field Display Name, command not executed.

# Create Collection

## Description
This collection intentionally omits Display Name to test required-field validation.

## Content Status
ACTIVE

## Qualified Name
Collection::SalesForecast::MP01::1.0

## GUID

___

# MP-02: Invalid valid-value for Content Status

> Content Status is set to BANANA, which is not in the valid values list.
> Valid values: DRAFT, PREPARED, PROPOSED, APPROVED, REJECTED, ACTIVE, DEPRECATED, OTHER
> Expected: validation error on Content Status value, command not executed.

# Create Collection

## Display Name
SF-MP02-Invalid-Content-Status

## Content Status
BANANA

## Qualified Name
Collection::SalesForecast::MP02::1.0

## GUID

___

# MP-03: Invalid valid-value for Membership Status

> Membership Status is set to an out-of-range value.
> Valid values: UNKNOWN, DISCOVERED, PROPOSED, IMPORTED, VALIDATED, DEPRECATED, OBSOLETE, OTHER
> Expected: validation error on Membership Status value, command not executed.

# Add Member to Collection

## Collection Id
Collection::SalesForecast::Master::1.0

## Element Id
DataStructure::CRMOpportunity::Salesforce::1.0

## Membership Status
NOT_A_STATUS

## GUID

___

# MP-04: Reference to non-existent Collection Id

> Collection Id references a qualified name that does not exist in Egeria.
> Expected: validation or processing error — collection not found, command not executed.

# Add Member to Collection

## Collection Id
Collection::SalesForecast::DoesNotExist::1.0

## Element Id
DataStructure::CRMOpportunity::Salesforce::1.0

## GUID

___

# MP-05: Reference to non-existent Element Id

> Element Id references a qualified name that does not exist in Egeria.
> Expected: validation or processing error — element not found, command not executed.

# Add Member to Collection

## Collection Id
Collection::SalesForecast::Master::1.0

## Element Id
DataStructure::NoSuchStructure::99.9

## GUID

___

# MP-06: Update with no identifying information

> Neither GUID nor Qualified Name is provided, and the Display Name
> cannot be resolved to a unique existing element.
> Expected: error — cannot identify element to update, command not executed.

# Update Collection

## Description
Attempting an update with no way to identify the target element.

## Content Status
ACTIVE

## GUID

___

# MP-07: Confidence out of range (Advanced attr)

> Confidence must be an integer between 0 and 100.
> Value of 150 is out of range.
> Expected: validation error on Confidence value, command not executed.
> Note: only relevant in advanced mode — in basic mode this attr is skipped entirely.

# Add Member to Collection

## Collection Id
Collection::SalesForecast::Master::1.0

## Element Id
DataStructure::CRMOpportunity::Salesforce::1.0

## Membership Status
PROPOSED

## Confidence
150

## GUID

___

# MP-08: Attach Collection to Resource — missing both endpoint identifiers

> Neither Collection Id nor Element Id is provided.
> Expected: validation error — both endpoints required for relationship commands.

# Attach Collection to Resource

## Resource Description
A resource attachment with no endpoints specified.

## Resource Use
GovernanceDefinitions

## GUID

___

# MP-09: Detach relationship that was never established

> Attempts to remove a membership relationship that does not exist.
> Expected: error or warning — relationship not found, command not executed or gracefully reported.

# Detach Member from Collection

## Collection Id
Collection::SalesForecast::Master::1.0

## Element Id
Collection::SalesForecast::NeverLinked::1.0

## GUID

___

# MP-10: Unrecognised command name

> The command name SF-Nonexistent-Command does not match any known command
> or alternative command name in the Collections family or any other family.
> Expected: command block skipped or flagged as unknown, no execution.

# SF-Nonexistent-Command

## Display Name
This should not be processed

## GUID

___

# MP-11: User Defined Content Status without Content Status OTHER

> User Defined Content Status is only valid when Content Status is set to OTHER.
> Here Content Status is ACTIVE, making User Defined Content Status invalid.
> Expected: validation warning that User Defined Content Status is ignored or rejected.
> Note: only relevant in advanced mode.

# Create Collection

## Display Name
SF-MP11-Bad-User-Defined-Status

## Content Status
ACTIVE

## User Defined Content Status
MyCustomStatus

## Qualified Name
Collection::SalesForecast::MP11::1.0

## GUID

___

> End of mean path tests.
>
> Expected outcomes for all MP tests:
>   VALIDATE mode : each error detected and reported, no Egeria writes attempted.
>   PROCESS mode  : each command rejected with informative message in output document.
>
> Specific expectations:
>   MP-01 : missing required field error on Display Name
>   MP-02 : invalid value error on Content Status (BANANA not in valid values)
>   MP-03 : invalid value error on Membership Status (NOT_A_STATUS not in valid values)
>   MP-04 : element not found error for Collection Id
>   MP-05 : element not found error for Element Id
>   MP-06 : cannot identify update target — no GUID, no QN, no resolvable Display Name
>   MP-07 : Confidence value 150 out of range 0-100 (advanced mode only)
>   MP-08 : missing required endpoint identifiers for relationship command
>   MP-09 : relationship not found (graceful — warn and continue or report clearly)
>   MP-10 : unrecognised command name — block skipped or flagged
>   MP-11 : User Defined Content Status invalid when Content Status is not OTHER (advanced mode)