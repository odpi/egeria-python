# Digital Products Family — Happy Path Tests
# Sales Forecast Theme

> This document tests the Dr.Egeria Digital Products command family under normal conditions.
> All commands are expected to succeed when processed.
>
> Run with VALIDATE first, then PROCESS.
>
> Create commands carry user-specified Qualified Names so later commands
> can reference them reliably by QN without needing a system-generated GUID.
>
> GUID appears only in Create commands — the system fills it on first processing.
> Update commands are identified by Qualified Name.
> Relationship commands are identified by their endpoint attributes.
>
> Verb synonyms:
>   Establish: Link, Attach, Add (all equivalent)
>   Remove:    Detach, Unlink, Remove (all equivalent)

---

# DP-01: Create Digital Product — minimal, QN auto-generated

> Display Name only. Expected: GUID filled, QN auto-generated, verb swapped to Update.

# Create Digital Product

## Display Name
Sales Forecast Data Feed

## GUID

___

# DP-02: Create Digital Product — full coverage, user-specified QN

> Exercises all Digital Product Base own attributes: Product Name, Product Status,
> Product Type, Current Version, Introduction Date, Next Version Date,
> Service Life, Withdrawal Date, Maturity.
> Also exercises Collection Base Purpose and common fields.

# Create Digital Product

## Display Name
Sales Forecast Pipeline Product

## Description
A digital product providing governed access to the Sales Forecasting pipeline outputs,
including opportunity data, revenue projections, and pipeline health metrics.

## Purpose
Provide a governed, subscription-based data product for Sales Forecast consumers
across Finance, Sales Operations, and Executive Reporting.

## Product Name
Sales Forecast Pipeline

## Product Status
ACTIVE

## Product Type
Periodic Delta

## Current Version
1.2

## Introduction Date
2025-01-01

## Next Version Date
2026-07-01

## Service Life
3 years

## Withdrawal Date
2028-01-01

## Maturity
Production

## Category
Sales Analytics

## Content Status
ACTIVE

## Version Identifier
1.2

## Search Keywords
sales forecast, pipeline, CRM, revenue, data product

## Journal Entry
Version 1.2 released following Q4 2025 data quality remediation.

## Qualified Name
DigitalProduct::SalesForecast::Pipeline::1.2

## GUID

___

# DP-03: Create Digital Product Catalog

> Creates the catalog that organises digital products. User-specified QN
> for reliable reference.

# Create Digital Product Catalog

## Display Name
Sales Analytics Digital Product Catalog

## Description
Root catalog organising all digital products in the Sales Analytics domain,
including forecast feeds, pipeline health products, and CRM data products.

## Purpose
Single browsable catalog for all governed Sales Analytics data products.

## Content Status
ACTIVE

## Version Identifier
1.0

## Qualified Name
DigitalProductCatalog::SalesAnalytics::1.0

## GUID

___

# DP-04: Update Digital Product — identified by QN

> Update flavor. No GUID. Element located by Qualified Name.
> Only changed fields provided; Merge Update defaults to True.

# Update Digital Product

## Display Name
Sales Forecast Pipeline Product

## Qualified Name
DigitalProduct::SalesForecast::Pipeline::1.2

## Current Version
1.3

## Next Version Date
2026-10-01

## Journal Entry
Version bumped to 1.3 following March 2026 pipeline refresh.

___

# DP-05: Create Agreement — generic

> Creates a generic Agreement collection. Agreement Type exercises
> the family-specific attribute.

# Create Agreement

## Display Name
Sales Forecast Data Access Agreement

## Description
Generic agreement governing access to Sales Forecast data products by
internal business units.

## Agreement Type
DataAccessAgreement

## Purpose
Define the terms under which internal consumers may access Sales Forecast data products.

## Content Status
ACTIVE

## Version Identifier
1.0

## Qualified Name
Agreement::SalesForecast::DataAccess::1.0

## GUID

___

# DP-06: Create Data Sharing Agreement

> Creates an Agreement with the DataSharingAgreement classification.
> Exercises Agreement Start Date and Agreement End Date from Shared Attribute Definitions.

# Create Data Sharing Agreement

## Display Name
Sales Forecast — Finance Data Sharing Agreement

## Description
Data sharing agreement between the Sales Analytics team and the Finance department
for access to Q1 2026 Sales Forecast outputs for budget reconciliation.

## Agreement Type
DataSharingAgreement

## Purpose
Govern the sharing of Sales Forecast data with Finance for budget reconciliation.

## Content Status
ACTIVE

## Version Identifier
1.0

## Qualified Name
Agreement::SalesForecast::Finance::DataSharing::1.0

## GUID

___

# DP-07: Create Digital Subscription

> Creates a DigitalSubscription agreement. Exercises Subscription Level and Support Level
> from Digital Subscription Base.

# Create Digital Subscription

## Display Name
Finance Team — Sales Forecast Subscription

## Description
Premium subscription for the Finance team to access the Sales Forecast Pipeline Product,
with business-hours support and daily data refresh.

## Subscription Level
Premium

## Support Level
BusinessHours

## Agreement Type
DigitalSubscription

## Purpose
Provide the Finance team governed subscription access to Sales Forecast Pipeline data.

## Content Status
ACTIVE

## Version Identifier
1.0

## Qualified Name
DigitalSubscription::SalesForecast::Finance::Premium::1.0

## GUID

___

# DP-08: Update Digital Subscription — identified by QN

> Update the subscription support level. No GUID. Located by QN.

# Update Digital Subscription

## Display Name
Finance Team — Sales Forecast Subscription

## Qualified Name
DigitalSubscription::SalesForecast::Finance::Premium::1.0

## Support Level
24x7

## Journal Entry
Support level upgraded to 24x7 following Finance executive escalation.

___

# DP-09: Link Product Dependency — verb Link

> Establishes a DigitalProductDependency relationship between two products.
> Digital Product 1 and Digital Product 2 are both input_required.
> No GUID on relationship commands.

# Link Product Dependency

## Digital Product 1
DigitalProduct::SalesForecast::Pipeline::1.2

## Digital Product 2
PDR::DigitalProduct::Sales-Forecast-Data-Feed

## Dependency Description
The Sales Forecast Pipeline Product is listed and discoverable via the
Sales Analytics Digital Product Catalog.

___

# DP-10: Link Agreement to Actor — verb Link

> Links an actor (role or person) to the Data Sharing Agreement.
> Agreement Name is input_required.

# Link Agreement to Actor

## Agreement Name
Agreement::SalesForecast::Finance::DataSharing::1.0

## Actors
jane.smith@example.com

___

# DP-11: Link Agreement Item — verb Attach

> Uses establish synonym Attach. Links an item (any Referenceable) to the agreement.
> Agreement Name and Item Name are both input_required.

# Attach Agreement to Item

## Agreement Name
Agreement::SalesForecast::Finance::DataSharing::1.0

## Item Name
DigitalProduct::SalesForecast::Pipeline::1.2

## Agreement Item Id
SF-FINANCE-ITEM-001

___

# DP-12: Link Agreement Item — full bundle attributes

> Exercises Entitlements (Dictionary), Obligations (Dictionary), Restrictions (Dictionary),
> Usage Measurements (Dictionary), Agreement Start Date, Agreement End Date.

# Link Agreement Item

## Agreement Name
Agreement::SalesForecast::DataAccess::1.0

## Item Name
DigitalProduct::SalesForecast::Pipeline::1.2

## Agreement Item Id
SF-ACCESS-ITEM-001

## Agreement Start Date
2026-01-01

## Agreement End Date
2026-12-31

## Entitlements
{"read_access": "permitted", "export_to_excel": "permitted", "share_externally": "not_permitted"}

## Obligations
{"report_usage": "quarterly", "notify_on_breach": "immediately"}

## Restrictions
{"resale": "forbidden", "sublicensing": "forbidden"}

## Usage Measurements
{"max_api_calls_per_day": "10000", "max_users": "50"}

___

# DP-13: Link Digital Subscriber — verb Add

> Uses establish synonym Add. Links a subscriber to a subscription.
> Subscriber Id is input_required; Subscription Id identifies the subscription.

# Add Digital Subscriber

## Subscription Id
DigitalSubscription::SalesForecast::Finance::Premium::1.0

## Subscriber Id
Campaign:Sustainability

___

# DP-14: Detach Product Dependency — verb Detach

> Removes the dependency relationship established in DP-09.
> Identified by the two product endpoint attributes.

# Detach Product Dependency

## Digital Product 1
DigitalProduct::SalesForecast::Pipeline::1.2

## Digital Product 2
DigitalProductCatalog::SalesAnalytics::1.0

___

# DP-15: Unlink Digital Subscriber — verb Unlink

> Removes the subscriber relationship established in DP-13.
> Detach and Remove are equivalent synonyms.

# Unlink Digital Subscriber

## Subscription Id
DigitalSubscription::SalesForecast::Finance::Premium::1.0

## Subscriber Id
Campaign:Sustainability

___

> End of Digital Products happy path tests.
>
> Expected outcomes:
>   DP-01          : GUID filled, QN auto-generated, verb swapped to Update Digital Product
>   DP-02, DP-03   : GUID filled, user-specified QN preserved exactly, verb swapped
>   DP-05 to DP-07 : GUID filled, user-specified QN preserved, verb swapped
>   DP-04, DP-08   : Update commands locate element by QN, apply changes, no GUID slot
>   DP-09 to DP-13 : Relationship commands executed, no GUID slot
>   DP-14, DP-15   : Relationships removed
>   DP-11          : Attach synonym accepted, processed as Link Agreement Item
>   DP-13          : Add synonym accepted, processed as Link Digital Subscriber