# External References Family — Happy Path Tests
# Sales Forecast Theme

> This document tests the Dr.Egeria External References command family under normal conditions.
> All commands are expected to succeed when processed.
>
> Run with VALIDATE first, then PROCESS.
>
> GUID appears only in Create commands — the system fills it on first processing.
> Update commands are identified by Qualified Name.
> Link commands are identified by their endpoint attributes (Element Name + reference endpoint).
>
> Verb synonyms:
>   Establish: Link, Attach, Add (all equivalent)
>   Remove:    Detach, Unlink, Remove (all equivalent)
>
> Alternative attribute labels in use:
>   Element Name     → Referenceable
>   Reference Title  → Title
>   Reference Abstract → Abstract
>   Publication Series → Series
>   Sources          → Reference Sources
>
> External Reference subtypes (all share External Reference Base attributes):
>   Create External Reference   — generic external reference
>   Create External Data Source — external data source
>   Create External Model Source — external analytical or AI model source
>   Create Related Media        — image, audio, video, or document media
>   Create Cited Document       — published document with bibliographic metadata
>   Create External Source Code — software source code reference
>
> Media Type valid values:   IMAGE, AUDIO, DOCUMENT, VIDEO, OTHER
> Media Usage valid values:  ICON, THUMBNAIL, ILLUSTRATION, USAGE_GUIDANCE, OTHER

---

# ER-01: Create External Reference — minimal, QN auto-generated

> Display Name only. Expected: GUID filled, QN auto-generated, verb swapped to Update.

# Create External Reference

## Display Name
Salesforce CRM Documentation

## GUID

___

# ER-02: Create External Reference — full External Reference Base coverage, user-specified QN

> Exercises all External Reference Base own attributes:
>   Reference Title (alt: Title), Reference Abstract (alt: Abstract),
>   Organization, License, Copyright, Attribution,
>   Sources (Dictionary — map of URL/DOI/ISBN strings).
> Also exercises common Referenceable fields: Description, URL, Category,
>   Content Status, Version Identifier, Search Keywords, Journal Entry.
> User-specified QN for reliable downstream Link command reference.

# Create External Reference

## Display Name
Salesforce CRM API Reference

## Description
Official Salesforce CRM REST API reference documentation, used as the authoritative
source for field definitions in the Sales Forecast pipeline data structures.

## Title
Salesforce REST API Developer Guide

## Abstract
Comprehensive reference for the Salesforce REST API, covering authentication,
object model, query syntax, and field-level metadata for all standard CRM objects
including Opportunity, Account, Contact, and Lead.

## Organization
Salesforce Inc.

## License
Creative Commons Attribution 4.0

## Copyright
Copyright 2025 Salesforce Inc. All rights reserved.

## Attribution
Salesforce Inc., Salesforce REST API Developer Guide, 2025.

## Sources
{"url": "https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest", "version": "v60.0"}

## URL
https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest

## Category
CRM Documentation

## Content Status
ACTIVE

## Version Identifier
v60.0

## Search Keywords
Salesforce, CRM, REST API, Opportunity, pipeline, field definitions

## Journal Entry
Added as authoritative reference for CRM field definitions in Sales Forecast pipeline.

## Qualified Name
ExternalReference::Salesforce::CRM::APIReference::v60.0

## GUID

___

# ER-03: Update External Reference — identified by Qualified Name

> Update flavor. No GUID. Element located by Qualified Name.

# Update External Reference

## Display Name
Salesforce CRM API Reference

## Qualified Name
ExternalReference::Salesforce::CRM::APIReference::v60.0

## Version Identifier
v61.0

## Sources
{"url": "https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest", "version": "v61.0"}

## Journal Entry
Updated to v61.0 following Spring 2026 Salesforce release.

___

# ER-04: Update External Reference — identified by Display Name only

> No QN provided. Dr.Egeria forms QN from Display Name and attempts to match.

# Update External Reference

## Display Name
Salesforce CRM Documentation

## Description
Official Salesforce CRM documentation portal — smoke test reference updated with description.

___

# ER-05: Create External Data Source — user-specified QN

> External Data Source subtype. Shares all External Reference Base attributes.
> References the CRM Opportunity export feed used by the forecast pipeline.

# Create External Data Source

## Display Name
Salesforce Opportunity Export Feed

## Description
Daily SFTP export of Salesforce Opportunity records used as the primary data
input for the Q1 2026 Sales Forecast pipeline.

## Title
SF Opportunity Export — Daily SFTP Feed

## Organization
Salesforce Inc.

## Sources
{"sftp_host": "sftp.salesforce.example.com", "path": "/exports/opportunity/daily", "format": "CSV"}

## Category
CRM Data Source

## Content Status
ACTIVE

## Qualified Name
ExternalDataSource::Salesforce::OpportunityFeed::Daily::1.0

## GUID

___

# ER-06: Create External Model Source — user-specified QN

> External Model Source subtype for an analytical model reference.
> References the regression model used to generate the Best Case forecast.

# Create External Model Source

## Display Name
Best Case Forecast Regression Model

## Description
Logistic regression model used to generate the Best Case Sales Forecast tier
from CRM opportunity data. Model artefacts stored in the ML model registry.

## Title
SF Best Case Forecast — Logistic Regression Model v2.1

## Organization
Sales Analytics Team — Example Corp

## Sources
{"model_registry": "mlflow://models/sf-best-case-forecast", "version": "2.1", "artifact_path": "s3://ml-models/sf-bestcase/v2.1"}

## Category
Forecast Model

## Content Status
ACTIVE

## Qualified Name
ExternalModelSource::SalesForecast::BestCaseRegression::v2.1

## GUID

___

# ER-07: Create External Source Code — user-specified QN

> External Source Code subtype referencing the forecast pipeline code repository.

# Create External Source Code

## Display Name
Sales Forecast Pipeline — Source Code

## Description
GitHub repository containing the Dr.Egeria Sales Forecast pipeline code,
including data ingestion, transformation, and output generation scripts.

## Title
SalesForecast Pipeline Repository

## Organization
Example Corp Engineering

## Sources
{"github": "https://github.com/example-corp/sales-forecast-pipeline", "branch": "main", "tag": "v1.2.0"}

## License
Apache 2.0

## Category
Pipeline Source Code

## Content Status
ACTIVE

## Qualified Name
ExternalSourceCode::SalesForecast::Pipeline::v1.2.0

## GUID

___

# ER-08: Create Related Media — IMAGE type, user-specified QN

> Related Media subtype. Exercises Related Media Base own attributes:
>   Media Type (Valid Value), Media Type Other Id,
>   Default Media Usage (Valid Value), Default Media Usage Other Id.
> References a dashboard screenshot used in governance documentation.

# Create Related Media

## Display Name
Sales Forecast Dashboard Screenshot — Q1 2026

## Description
Screenshot of the Q1 2026 Sales Forecast executive dashboard, used as an
illustration in the governance documentation for the forecast pipeline.

## Title
Q1 2026 Sales Forecast Dashboard

## Media Type
IMAGE

## Default Media Usage
ILLUSTRATION

## Organization
Sales Analytics Team — Example Corp

## Sources
{"url": "https://wiki.example.com/images/sf-dashboard-q1-2026.png"}

## Category
Dashboard Screenshot

## Content Status
ACTIVE

## Qualified Name
RelatedMedia::SalesForecast::Dashboard::Q1-2026::1.0

## GUID

___

# ER-09: Create Related Media — DOCUMENT type with OTHER Media Type

> Exercises the OTHER valid value path for Media Type plus Media Type Other Id.

# Create Related Media

## Display Name
Sales Forecast Data Dictionary — PDF

## Description
PDF export of the Sales Forecast data dictionary, used as USAGE_GUIDANCE
reference material for analysts onboarding to the forecast pipeline.

## Title
Sales Forecast Data Dictionary

## Media Type
OTHER

## Media Type Other Id
PDF_DOCUMENT

## Default Media Usage
USAGE_GUIDANCE

## Organization
Data Governance Team — Example Corp

## Sources
{"url": "https://wiki.example.com/docs/sf-data-dictionary.pdf"}

## Qualified Name
RelatedMedia::SalesForecast::DataDictionary::PDF::1.0

## GUID

___

# ER-10: Create Cited Document — full bibliographic coverage, user-specified QN

> Cited Document subtype. Exercises all Cited Document Base own attributes:
>   Publisher, Publication Date, Publication Year, First Publication Date,
>   Edition, Number of Pages (Simple Int), Page Range,
>   Publication Series (alt: Series), Publication Series Volume,
>   Publication City, Publication Numbers (Simple List).
> Also exercises Reference Title (alt: Title) and Reference Abstract.

# Create Cited Document

## Display Name
Enterprise Data Management — Best Practices Guide

## Description
Industry best practices guide for enterprise data management, cited as the
authoritative reference for the Sales Forecast data governance framework.

## Title
Enterprise Data Management: A Best Practices Guide for Sales Analytics

## Abstract
This guide covers data governance frameworks, data quality management, and
metadata standards as applied to sales analytics and forecasting domains.
Includes case studies from Fortune 500 organisations.

## Publisher
Data Governance Institute Press

## Publication Date
2024-09-15

## Publication Year
2024

## First Publication Date
2020-01-01

## Edition
3rd Edition

## Number of Pages
412

## Page Range
180-220

## Series
Data Management Best Practices Series

## Publication Series Volume
Volume 7

## Publication City
New York

## Publication Numbers
ISBN-13: 978-3-16-148410-0, DOI: 10.1000/xyz123

## Organization
Data Governance Institute

## License
All rights reserved

## Copyright
Copyright 2024 Data Governance Institute Press

## Sources
{"isbn": "978-3-16-148410-0", "doi": "10.1000/xyz123", "publisher_url": "https://dgi-press.example.com/edm-guide-v3"}

## Category
Governance Reference

## Content Status
ACTIVE

## Qualified Name
CitedDocument::DataGovernanceInstitute::EDMGuide::3rdEd::2024

## GUID

___

# ER-11: Link External Reference — verb Link

> Links an external reference to a referenceable element.
> Element Name (alt: Referenceable) and External Reference are both input_required.
> No GUID on Link commands.

# Link External Reference

## Element Name
GlossaryTerm::SalesForecast::Opportunity::1.0

## External Reference
ExternalReference::Salesforce::CRM::APIReference::v60.0

___

# ER-12: Link External Reference — using alt label Referenceable, verb Attach

> Uses the alt label Referenceable for Element Name, and the Attach synonym.

# Attach External Reference

## Referenceable
DigitalProduct::SalesForecast::Pipeline::1.2

## External Reference
ExternalDataSource::Salesforce::OpportunityFeed::Daily::1.0

___

# ER-13: Link Media Reference — verb Link

> Links a Related Media reference to a referenceable.
> Element Name and Media Reference are both input_required.
> Exercises Media Usage (Valid Value) and Media Id.

# Link Media Reference

## Element Name
DigitalProduct::SalesForecast::Pipeline::1.2

## Media Reference
RelatedMedia::SalesForecast::Dashboard::Q1-2026::1.0

## Media Usage
ILLUSTRATION

## Media Id
SF-DASHBOARD-Q1-2026-001

___

# ER-14: Link Media Reference — THUMBNAIL usage, verb Add

> Uses establish synonym Add. Tests the THUMBNAIL media usage value.

# Add Media Reference

## Element Name
GlossaryTerm::SalesForecast::PipelineCoverageRatio::1.0

## Media Reference
RelatedMedia::SalesForecast::DataDictionary::PDF::1.0

## Media Usage
USAGE_GUIDANCE

___

# ER-15: Link Cited Document — verb Link

> Links a cited document to a referenceable element via DocumentCitationLink.
> Element Name and Cited Document are both input_required.
> Also exercises Pages and Reference Id.

# Link Cited Document

## Element Name
Collection::SalesForecast::Master::1.0

## Cited Document
CitedDocument::DataGovernanceInstitute::EDMGuide::3rdEd::2024

## Pages
180-220

## Reference Id
SF-CITATION-EDM-001

___

# ER-16: Detach External Reference — verb Detach

> Removes the link established in ER-11.
> Identified by Element Name and External Reference — no GUID.

# Detach External Reference

## Element Name
GlossaryTerm::SalesForecast::Opportunity::1.0

## External Reference
ExternalReference::Salesforce::CRM::APIReference::v60.0

___

# ER-17: Unlink Media Reference — verb Unlink

> Removes the link established in ER-13.
> Detach and Remove are equivalent synonyms.

# Unlink Media Reference

## Element Name
DigitalProduct::SalesForecast::Pipeline::1.2

## Media Reference
RelatedMedia::SalesForecast::Dashboard::Q1-2026::1.0

___

# ER-18: Remove Cited Document — verb Remove

> Removes the link established in ER-15.
> Exercises the third removal synonym Remove (Detach and Unlink also valid).

# Remove Cited Document

## Element Name
Collection::SalesForecast::Master::1.0

## Cited Document
CitedDocument::DataGovernanceInstitute::EDMGuide::3rdEd::2024

___

> End of External References happy path tests.
>
> Expected outcomes:
>   ER-01               : GUID filled, QN auto-generated, verb swapped to Update External Reference
>   ER-02               : GUID filled, user-specified QN preserved exactly, verb swapped
>   ER-03               : Update locates element by QN, applies partial update, no GUID slot
>   ER-04               : Update locates element by Display Name, QN filled in output
>   ER-05 to ER-10      : GUID filled, QN preserved, correct subtype classification set
>   ER-09               : Media Type OTHER accepted, Media Type Other Id present in output
>   ER-10               : All bibliographic fields present in output; Publication Numbers list accepted
>   ER-11 to ER-15      : Link commands executed, no GUID slot
>   ER-12               : Referenceable alt label resolved to Element Name; Attach synonym accepted
>   ER-14               : Add synonym accepted, processed as Link Media Reference
>   ER-16               : Detach synonym accepted, link removed
>   ER-17               : Unlink synonym accepted, link removed
>   ER-18               : Remove synonym accepted, link removed