# Data Designer Family — Happy Path Tests
# Sales Forecast Theme

> This document tests the Dr.Egeria Data Designer command family under normal conditions.
> All commands are expected to succeed when processed.
>
> Run with VALIDATE first, then PROCESS.
>
> Key principle: Create commands that are referenced by later commands in this document
> always carry a user-specified Qualified Name. This allows reliable cross-referencing
> within the document without needing system-generated GUIDs.
>
> Sort Order valid values: UNKNOWN, UNSORTED, ASCENDING, DESCENDING, OTHER
> Content Status valid values: DRAFT, PREPARED, PROPOSED, APPROVED, REJECTED,
>                               ACTIVE, DEPRECATED, OTHER

---

# DD-01: Create Certification Type — from Governance Officer family, referenced later

> Creates the certification type used in DD-17 (Link Certification Type to Data Structure).
> Defined here first so the qualified name is available for cross-referencing.

# Create Certification Type

## Display Name
Sales Forecast Certified

## Description
Certification type indicating that a data structure meets the sales forecast
data quality and completeness standards.

## Scope
All data structures used in sales forecast reporting.

## Content Status
ACTIVE

## Version Identifier
1.0

## Authors
data.governance@example.com

## Entitlements
{"use": "Approved for use in certified forecast pipelines"}

## Obligations
{"review": "Annual review required"}

## Restrictions
{"redistribution": "Not for external distribution"}

## Qualified Name
CertificationType::SalesForecastCertified::1.0

## GUID

___

# DD-02: Create Data Dictionary — minimal with required fields

# Create Data Dictionary

## Display Name
Sales Forecast Dictionary

## Description
Central data dictionary for all sales forecast data definitions and standards.

## Content Status
ACTIVE

## Version Identifier
1.0

## Authors
jane.smith@example.com

## Qualified Name
DataDictionary::SalesForecast::1.0

## GUID

___

# DD-03: Create Data Specification

# Create Data Spec

## Display Name
Sales Forecast Specification

## Description
Data specification describing the structure requirements for the sales forecast initiative.

## Content Status
ACTIVE

## Version Identifier
1.0

## Authors
jane.smith@example.com

## Qualified Name
DataSpecification::SalesForecast::1.0

## GUID

___

# DD-04: Create Data Class — Revenue Amount

> Data class for monetary amounts. Referenced by DD-10 (Predicted Revenue field).

# Create Data Class

## Display Name
Revenue Amount

## Description
A data class representing monetary amounts used for revenue and forecast figures.

## Content Status
ACTIVE

## Version Identifier
1.0

## Authors
jane.smith@example.com

## Data Type
double

## Allow Duplicate Values
true

## Is Nullable
false

## Is Case Sensitive
false

## Value Range From
0.0

## Value Range To
999999999.99

## Sample Values
1000.00, 25000.50, 500000.00

## Average Value
45000.00

## Qualified Name
DataClass::RevenueAmount::1.0

## GUID

___

# DD-05: Create Data Value Specification — Bounded Integer

> Parent spec, used in DD-15 (Link Data Value Composition).

# Create Data Value Specification

## Display Name
Bounded Integer Spec

## Description
A data value specification for bounded integer values.

## Content Status
ACTIVE

## Version Identifier
1.0

## Authors
jane.smith@example.com

## Data Type
int

## Specification
bounded integer

## Qualified Name
DataValueSpecification::BoundedInteger::1.0

## GUID

___

# DD-06: Create Data Value Specification — Percentage Range

> Child spec specialising Bounded Integer. Referenced by DD-13 and DD-15.

# Create Data Value Specification

## Display Name
Percentage Range Spec

## Description
A data value specification for percentage values between 0 and 100.

## Content Status
ACTIVE

## Version Identifier
1.0

## Authors
jane.smith@example.com

## Data Type
int

## Specification
integer in range [0, 100]

## Match Threshold
95

## Match Property Names
confidence_score, percentage, rate

## Qualified Name
DataValueSpecification::PercentageRange::1.0

## GUID

___

# DD-07: Create Data Structure — Sales Forecast Record

> Core data structure. Referenced by field creation and link commands below.

# Create Data Structure

## Display Name
Sales Forecast Record

## Description
Data structure representing a single sales forecast record including region,
product, period, and predicted revenue.

## Content Status
ACTIVE

## Version Identifier
1.0

## Authors
jane.smith@example.com

## In Data Dictionary
DataDictionary::SalesForecast::1.0

## In Data Specification
DataSpecification::SalesForecast::1.0

## Namespace Path
sales.forecast

## Qualified Name
DataStructure::SalesForecastRecord::1.0

## GUID

___

# DD-08: Create Data Grain — Monthly Region

# Create Data Grain

## Display Name
Monthly Region Grain

## Description
Grain definition representing one row per sales region per calendar month.

## Content Status
ACTIVE

## Version Identifier
1.0

## Authors
jane.smith@example.com

## Granularity Basis
time period

## Grain Statement
One row per sales region per calendar month.

## Qualified Name
DataGrain::MonthlyRegion::1.0

## GUID

___

# DD-09: Create Data Field — Region Code

# Create Data Field

## Display Name
Region Code

## Description
Two-letter regional identifier for the sales territory covered by this forecast.

## Content Status
ACTIVE

## Authors
jane.smith@example.com

## In Data Structure
DataStructure::SalesForecastRecord::1.0

## Data Type
string

## Is Nullable
false

## Position
0

## Minimum Cardinality
1

## Maximum Cardinality
1

## Length
2

## Minimum Length
2

## Sort Order
ASCENDING

## Aliases
Region, Territory Code

## Qualified Name
DataField::SalesForecastRecord::RegionCode::1.0

## GUID

___

# DD-10: Create Data Field — Forecast Period

# Create Data Field

## Display Name
Forecast Period

## Description
The period (month and year) to which this sales forecast applies, in YYYY-MM format.

## Content Status
ACTIVE

## Authors
jane.smith@example.com

## In Data Structure
DataStructure::SalesForecastRecord::1.0

## Data Type
string

## Is Nullable
false

## Position
1

## Minimum Cardinality
1

## Maximum Cardinality
1

## Length
7

## Sort Order
ASCENDING

## Qualified Name
DataField::SalesForecastRecord::ForecastPeriod::1.0

## GUID

___

# DD-11: Create Data Field — Predicted Revenue

# Create Data Field

## Display Name
Predicted Revenue

## Description
The predicted revenue for the region and period, in USD.

## Content Status
ACTIVE

## Authors
jane.smith@example.com

## In Data Structure
DataStructure::SalesForecastRecord::1.0

## Data Type
double

## Is Nullable
false

## Position
2

## Minimum Cardinality
1

## Maximum Cardinality
1

## Data Class
DataClass::RevenueAmount::1.0

## Units
USD

## Default Value
0.0

## Qualified Name
DataField::SalesForecastRecord::PredictedRevenue::1.0

## GUID

___

# DD-12: Create Data Field — Confidence Score

# Create Data Field

## Display Name
Confidence Score

## Description
A percentage score (0-100) indicating the model confidence in this forecast value.

## Content Status
ACTIVE

## Authors
jane.smith@example.com

## In Data Structure
DataStructure::SalesForecastRecord::1.0

## Data Type
int

## Is Nullable
true

## Position
3

## Minimum Cardinality
0

## Maximum Cardinality
1

## Default Value
0

## Qualified Name
DataField::SalesForecastRecord::ConfidenceScore::1.0

## GUID

___

# DD-13: Link Data Value Definition — PercentageRange to ConfidenceScore field

# Attach Data Value Specification

## Data Value Specification
DataValueSpecification::PercentageRange::1.0

## Element Id
DataField::SalesForecastRecord::ConfidenceScore::1.0

## Description
Associates the percentage range specification with the confidence score field.

___

# DD-14: Link Data Field — PredictedRevenue DerivedFrom ConfidenceScore

# Link Data Field

## Linked Data Field 1
DataField::SalesForecastRecord::PredictedRevenue::1.0

## Linked Data Field 2
DataField::SalesForecastRecord::ConfidenceScore::1.0

## Link Relationship Type Name
DerivedFrom

## Description
The confidence score is derived from the predicted revenue calculation.

___

# DD-15: Link Data Value Composition — PercentageRange under BoundedInteger

# Link Data Value Composition

## Data Value Specification
DataValueSpecification::BoundedInteger::1.0

## Data Value Specification Child
DataValueSpecification::PercentageRange::1.0

## Description
Percentage Range Spec is a specialisation of the Bounded Integer Spec.

___

# DD-16: Create Data Class — Forecast Revenue Amount (child of Revenue Amount)

> Child data class, linked under Revenue Amount in DD-16b.

# Create Data Class

## Display Name
Forecast Revenue Amount

## Description
A specialised data class for forecast revenue figures, child of Revenue Amount.

## Content Status
ACTIVE

## Authors
jane.smith@example.com

## Data Type
double

## Is Nullable
false

## Value Range From
0.0

## Value Range To
9999999.99

## Qualified Name
DataClass::ForecastRevenueAmount::1.0

## GUID

___

# DD-16b: Link Data Class Composition — ForecastRevenueAmount under RevenueAmount

# Link Data Class Composition

## Data Class
DataClass::RevenueAmount::1.0

## Data Class Child
DataClass::ForecastRevenueAmount::1.0

## Description
Forecast Revenue Amount is a sub-class of Revenue Amount.

___

# DD-17: Link Field to Structure — RegionCode into SalesForecastRecord

# Link Data Field to Data Structure

## Data Field
DataField::SalesForecastRecord::RegionCode::1.0

## Data Structure
DataStructure::SalesForecastRecord::1.0

## Description
Associates the Region Code field as a member of the Sales Forecast Record structure.

___

# DD-18: Link Certification Type to Data Structure

# Link Certification Type to Data Structure

## Data Structure
DataStructure::SalesForecastRecord::1.0

## Certification Type
CertificationType::SalesForecastCertified::1.0

## Description
Assigns the Sales Forecast Certified certification type to the Sales Forecast Record
data structure.

___

# DD-19: Attach Data Description to Element

# Attach Data Description to Element

## Collection Id
DataSpecification::SalesForecast::1.0

## Element Id
DataStructure::SalesForecastRecord::1.0

## Description
Connects the Sales Forecast Specification to the Sales Forecast Record structure
via the DataDescription relationship.

___

> End of Data Designer happy path tests.
>
> Expected outcomes:
>   DD-01        : Certification Type created (GO family command). GUID filled.
>   DD-02..DD-08 : Create commands executed. GUIDs filled. Verbs swapped to Update.
>   DD-09..DD-12 : Data Fields created within SalesForecastRecord structure.
>   DD-13..DD-19 : Link/Attach commands executed. No GUID slots.
>   DD-15        : Data Value Composition links PercentageRange under BoundedInteger.
>   DD-16b       : Data Class Composition links ForecastRevenueAmount under RevenueAmount.