# Report Family — Happy Path Tests
# Sales Forecast Theme

> This document tests the Dr.Egeria Report family under normal conditions.
> All commands are expected to succeed when processed.
>
> Run with PROCESS (or VALIDATE to confirm parsing before execution).
>
> Two commands, two very different behaviors:
>   - View Report (RP-* tests below): ad-hoc, execute-only
>       - No GUID slot, no Qualified Name, no verb swap on output
>       - No element is created or modified in Egeria
>       - Output is report data returned from the Egeria repository
>       - Report Spec is the only required attribute — it names the FormatSet to run
>   - Create Report (CR-* tests below): persists a real Egeria `Report` asset
>       - Has a GUID and Qualified Name; upserts (rerun with the same Display
>         Name transitions to Update Report automatically)
>       - Report Spec + execution params land in the Report's additionalProperties
>       - Display Name is required in addition to Report Spec
>
> Output Format valid values:
>   LIST, FORM, REPORT, MERMAID, DICT, MD, TABLE, JSON
>
> Output Sort Order valid values (Advanced):
>   ANY, CREATION_DATE_RECENT, CREATION_DATA_OLDEST,
>   LAST_UPDATE_RECENT, LAST_UPDATE_OLDEST,
>   PROPERTY_ASCENDING, PROPERTY_DESCENDING
>
> Limit Result by Status valid values (Advanced):
>   UNKNOWN, DRAFT, PREPARED, PROPOSED, APPROVED, REJECTED,
>   APPROVED_CONCEPT, UNDER_DEVELOPMENT, DEVELOPMENT_COMPLETE,
>   APPROVED_FOR_DEPLOYMENT, STANDBY, ACTIVE, FAILED, DISABLED,
>   COMPLETE, DEPRECATED, OTHER, DELETED

---

# RP-01: Report — minimal, Report Spec only

> Report Spec is the only required attribute.
> All other attributes take their defaults:
>   Search String defaults to * (match all)
>   Output Format defaults to JSON
>   Starts With defaults to True
> Expected: report runs against the Referenceable FormatSet and returns results.

## View Report

### Report Spec
Default

### Page Size 
5
___

# RP-02: Report — explicit Search String and Output Format LIST

> Adds a Search String to filter results and sets Output Format to LIST.
> Exercises the two most commonly used optional Domain-level attributes.

## View Report

### Report Spec
Collections

### Search String
Sales Forecast

### Output Format
LIST

___

# RP-03: Report — Output Format FORM

> FORM output renders each result as a structured form rather than a list.
> Uses the Sales Forecast Master Collection as the search target.

## View Report

### Report Spec
Collections

### Search String
Sales Forecast Master Collection

### Output Format
FORM

___

# RP-04: Report — Output Format TABLE

> TABLE output renders results in a tabular layout.

## View Report

### Report Spec
Digital-Products

### Search String
Sales Forecast

### Output Format
TABLE

___

# RP-05: Report — Output Format MD

> MD output renders results as Markdown.

## View Report

### Report Spec
Glossaries

### Search String
Pipeline

### Output Format
MD

___

# RP-06: Report — Output Format MERMAID

> MERMAID output renders results as a Mermaid diagram where supported by the FormatSet.

## View Report

### Report Spec
Projects

### Search String
Sales Forecast

### Output Format
MERMAID

___

# RP-07: Report — Starts With False, Ends With False (contains match)

> With both Starts With and Ends With set to False, the search string
> matches anywhere within the field — a contains search.
> Expected: broader result set than a starts-with search.

## View Report

### Report Spec
Glossaries

### Search String
Forecast

### Output Format
LIST

### Starts With
False

### Ends With
False

___

# RP-08: Report — Ends With True

> Ends With True matches the search string at the end of the field.
> Starts With defaults to True but is overridden here by Ends With True.

## View Report

### Report Spec
Collections

### Search String
1.0

### Output Format
LIST

### Starts With
False

### Ends With
True

___

# RP-09: Report — Ignore Case True

> Ignore Case True makes the search string case-insensitive.
> Expected: results matching 'sales forecast', 'Sales Forecast', 'SALES FORECAST' etc.

## View Report

### Report Spec
Digital-Products

### Search String
sales forecast

### Output Format
LIST

### Ignore Case
True

___

# RP-10: Report — Metadata Element Type Name filter

> Filters results to a specific Egeria metadata element type.
> Expected: only elements of type DigitalProduct returned.

## View Report

### Report Spec
Digital-Products

### Search String
Sales Forecast

### Output Format
LIST

### Metadata Element Type Name
DigitalProduct

___

# RP-11: Report — Metadata Element Subtype Names filter (Simple List)

> Filters results to specific subtypes. Multiple values provided as a list.

## View Report

### Report Spec
Collections

### Search String
*

### Output Format
LIST

### Metadata Element Subtype Names
RootCollection
CollectionFolder

___

# RP-12: Report — Pagination with Page Size and Start From

> Tests pagination attributes. Page Size limits results per page;
> Start From sets the offset for the first result returned.
> Useful for large result sets such as all Sales Forecast glossary terms.

## View Report

### Report Spec
Glossaries

### Search String
*

### Output Format
LIST

### Page Size
10

### Start From
0

___

# RP-13: Report — second page via Start From

> Retrieves the second page of results from the same query as RP-12.

## View Report

### Report Spec
Glossaries

### Search String
*

### Output Format
LIST

### Page Size
10

### Start From
10

___

# RP-14: Report — Advanced: Limit Result by Status

> Advanced attribute. Filters results to elements in ACTIVE status only.
> Default is ['ACTIVE'] but here it is set explicitly to verify the attribute is parsed.

## View Report

### Report Spec
Collections

### Search String
Sales Forecast

### Output Format
LIST

### Limit Result by Status
ACTIVE

___

# RP-15: Report — Advanced: Output Sort Order PROPERTY_ASCENDING

> Sorts results by a named property in ascending order.
> Order Property Name specifies which property to sort by.

## View Report

### Report Spec
Glossaries

### Search String
*

### Output Format
TABLE

### Output Sort Order
PROPERTY_ASCENDING

### Order Property Name
displayName

___

# RP-16: Report — Advanced: Output Sort Order LAST_UPDATE_RECENT

> Sorts by most recently updated first — useful for governance review workflows.

## View Report

### Report Spec
Projects

### Search String
Sales Forecast

### Output Format
LIST

### Output Sort Order
LAST_UPDATE_RECENT

___

# RP-17: Report — Advanced: Graph Query Depth

> Graph Query Depth controls how many levels of hierarchy are returned.
> Depth 0 returns only top-level attributes; higher values traverse relationships.

## View Report

### Report Spec
Collections

### Search String
Sales Forecast Hierarchy Root

### Output Format
REPORT

### Graph Query Depth
3

___

# RP-18: Report — Advanced: Skip Relationships (Simple List)

> Skips specified relationship types from the output.
> Useful for focusing on element properties without traversing all relationships.

## View Report

### Report Spec
Digital-Products

### Search String
Sales Forecast Pipeline Product

### Output Format
REPORT

### Skip Relationships
ResourceList
CollectionMembership

___

# RP-19: Report — Advanced: Include Only Classified Elements

> Returns only elements that carry the specified classifications.

## View Report

### Report Spec
Collections

### Search String
*

### Output Format
LIST

### Include Only Classified Elements
RootCollection

___

# RP-20: Report — Advanced: Governance Zone Filter

> Restricts results to elements in the specified governance zone(s).

## View Report

### Report Spec
Digital-Products

### Search String
*

### Output Format
LIST

### Governance Zone Filter
SalesAnalytics
Finance

___

# RP-21: Report — Advanced: Anchor Scope ID

> Restricts the search to elements anchored within the specified scope.

## View Report

### Report Spec
Collections

### Search String
*

### Output Format
LIST

### Anchor Scope ID
Collection::SalesForecast::Root::1.0

___

# RP-22: Report — Advanced: AsOfTime (point-in-time query)

> Returns the state of the repository as it was at a specific point in time.
> Uses an ISO-8601 timestamp.

## View Report

### Report Spec
Collections

### Search String
Sales Forecast

### Output Format
LIST

### AsOfTime
2026-03-01T00:00:00Z

___

# RP-23: Report — multiple Domain attributes combined

> Exercises Search String, Output Format, Starts With, Ignore Case,
> Metadata Element Type Name, Page Size, and Start From together.
> Tests that multiple Domain-level filter attributes combine correctly.

## View Report

### Report Spec
Glossaries

### Search String
pipeline

### Output Format
TABLE

### Starts With
False

### Ignore Case
True

### Metadata Element Type Name
GlossaryTerm

### Page Size
25

### Start From
0

___

___

# Create Report — Happy Path Tests

> Tests the Dr.Egeria Create Report command — persists a real Egeria `Report`
> asset (DataSet -> Asset -> Referenceable) carrying a Report Spec reference
> plus optional default execution parameters, so a Dashboard Sheet placement
> can reference a concrete, parameterized instance instead of a bare Report
> Spec (see egeria-workspaces-fs BACKLOG.md NEXT-14).
>
> Unlike View Report: Create Report DOES create/update an element (has a
> GUID, a Qualified Name, and upserts -- rerunning with the same Display
> Name transitions to Update Report automatically).
>
> Short-term design: every attribute below Display Name/Description lands in
> the Report element's `additionalProperties` dict (no dedicated
> `ReportDefinition` subtype yet). `Report Spec` is the only required
> attribute beyond Display Name.

___

# CR-01: Create Report — minimal, Display Name + Report Spec only

> All other attributes take their defaults (Search String *, Starts With
> True, etc. -- same defaults View Report uses).
> Expected: a new Report element is created; GUID and Qualified Name appear
> in the output.

## Create Report

### Display Name
Sales Forecast Pipeline Report

### Report Spec
Collections

___

# CR-02: Create Report — explicit Output Format and Search String

> Sets the two most commonly overridden execution defaults.
> Expected: `additionalProperties` on the created Report contains
> `outputFormat: TABLE` and `searchString: Sales Forecast`.

## Create Report

### Display Name
Sales Forecast Collections Table

### Description
Table view of Sales Forecast collections, for placement on a dashboard.

### Report Spec
Collections

### Output Format
TABLE

### Search String
Sales Forecast

___

# CR-03: Create Report — Advanced filters combined

> Exercises several Advanced-level execution parameters together, mirroring
> RP-23's combined-attributes style but on a persisted Report rather than an
> ad-hoc View.

## Create Report

### Display Name
Sales Forecast Products Governed View

### Report Spec
Digital-Products

### Output Format
LIST

### Search String
Sales Forecast

### Metadata Element Type Name
DigitalProduct

### Page Size
25

### Governance Zone Filter
SalesAnalytics

___

# CR-04: Create Report — re-run CR-01 with a changed Description

> Same Display Name as CR-01, with Report Spec unchanged and a new
> Description. Expected: the base class's Create<->Update upsert transition
> fires -- output shows "Update Report", same GUID as CR-01, not a second
> element.

## Create Report

### Display Name
Sales Forecast Pipeline Report

### Description
Now includes a description that wasn't present on the first run.

### Report Spec
Collections

___

> End of Create Report happy path tests.
>
> Expected outcomes for all CR tests:
>   CR-01 : New Report element created; GUID + Qualified Name present in output
>   CR-02 : additionalProperties contains outputFormat=TABLE, searchString="Sales Forecast"
>   CR-03 : additionalProperties contains all combined filter params
>   CR-04 : Transitions to Update Report; same GUID as CR-01, description updated

___

> End of Report happy path tests.
>
> Expected outcomes for all RP tests:
>   All commands  : Report runs without error; results returned from Egeria repository
>   All commands  : No GUID slot, no QN, no verb swap — output is report data only
>   RP-01         : Default Search String (*), Output Format (JSON), Starts With (True) applied
>   RP-02 to RP-06 : Each Output Format value accepted and applied correctly
>   RP-07         : Contains-style match returns broader results than starts-with
>   RP-08         : Ends With match returns elements whose name ends with '1.0'
>   RP-09         : Case-insensitive match returns results regardless of capitalisation
>   RP-10         : Only DigitalProduct type elements returned
>   RP-11         : Only RootCollection and CollectionFolder subtypes returned
>   RP-12, RP-13  : Pagination returns 10 results per page from the correct offset
>   RP-14         : Only ACTIVE status elements returned
>   RP-15         : Results sorted alphabetically by displayName
>   RP-16         : Results sorted most recently updated first
>   RP-17         : Hierarchy traversed to depth 3
>   RP-18         : ResourceList and CollectionMembership relationships absent from output
>   RP-19         : Only RootCollection-classified elements returned
>   RP-20         : Only elements in SalesAnalytics or Finance governance zones returned
>   RP-21         : Search scoped to elements anchored under the specified collection
>   RP-22         : Repository state as of 2026-03-01 returned
>   RP-23         : All combined Domain filters applied simultaneously