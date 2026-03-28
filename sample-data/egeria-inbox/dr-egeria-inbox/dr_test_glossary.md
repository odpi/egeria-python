# Glossary Family — Happy Path Tests
# Sales Forecast Theme

> This document tests the Dr.Egeria Glossary command family under normal conditions.
> All commands are expected to succeed when processed.
>
> Run with VALIDATE first, then PROCESS.
>
> GUID appears only in Create commands — the system fills it on first processing.
> Update commands are identified by Qualified Name.
> Link Term-Term Relationship commands are identified by Term 1, Term 2, and Relationship Type.
>
> Verb synonyms:
>   Establish: Link, Attach, Add (all equivalent)
>   Remove:    Detach, Unlink, Remove (all equivalent)
>
> Glossary Name accepts multiple alt labels:
>   Glossary Name, Glossaries, In Glossaries, In Glossary, Glossary Names
>
> Relationship Type valid values:
>   RelatedTerm, Synonym, Antonym, PreferredTerm, ReplacementTerm, Translation, IsA, ValidValue

---

# GL-01: Create Glossary — minimal, QN auto-generated

> Display Name only. Expected: GUID filled, QN auto-generated, verb swapped to Update Glossary.

# Create Glossary

## Display Name
Sales Forecast Glossary

## GUID

___

# GL-02: Create Glossary — full coverage, user-specified QN

> Exercises all Glossary Base own attributes: Language, Usage.
> Also exercises Referenceable/Authored Referenceable fields:
>   Description, Category, Content Status, Version Identifier,
>   Search Keywords, Authors, Journal Entry.
> User-specified QN for reliable downstream term reference.

# Create Glossary

## Display Name
Sales Forecast Domain Glossary

## Description
Controlled vocabulary for the Sales Forecasting domain. Defines key business terms
used across CRM data, pipeline management, revenue reporting, and governance.

## Language
English

## Usage
Use this glossary to tag data assets, fields, and governance definitions within
the Sales Forecasting domain. All analysts and stewards should reference these
definitions before creating new metadata elements.

## Category
Sales Analytics

## Content Status
ACTIVE

## Version Identifier
1.0

## Search Keywords
sales forecast, CRM, pipeline, revenue, glossary

## Authors
jane.smith@example.com

## Journal Entry
Initial glossary created to support Q1 2026 Sales Forecast governance initiative.

## Qualified Name
Glossary::SalesForecast::Domain::1.0

## GUID

___

# GL-03: Update Glossary — identified by Qualified Name

> Update flavor. No GUID. Element located by Qualified Name.
> Only changed fields provided; Merge Update defaults to True.

# Update Glossary

## Display Name
Sales Forecast Domain Glossary

## Qualified Name
Glossary::SalesForecast::Domain::1.0

## Description
Controlled vocabulary for the Sales Forecasting domain. Updated to include
additional pipeline and CRM terms following the Q1 2026 data quality review.

## Journal Entry
Description updated following Q1 2026 data quality review on 2026-03-20.

___

# GL-04: Update Glossary — identified by Display Name only

> No QN provided. Dr.Egeria forms a QN from Display Name and attempts to match.
> Expected: element matched and updated, QN filled in output.

# Update Glossary

## Display Name
Sales Forecast Glossary

## Description
Minimal glossary used for smoke testing. Updated with a description.

___

# GL-05: Create Glossary Term — minimal, QN auto-generated

> Display Name only plus Glossary Name to link the term to its glossary.
> Expected: GUID filled, QN auto-generated, verb swapped to Update Glossary Term.

# Create Glossary Term

## Display Name
Sales Forecast

## Glossary Name
Glossary::SalesForecast::Domain::1.0

## GUID

___

# Create Folder
## Display Name
Sales Metrics
## Qualified Name
CollectionFolder::SalesForecast::SalesMetrics::1.0
## Description 
A collection of metrics related to sales performance.


____

# GL-06: Create Glossary Term — full coverage, user-specified QN

> Exercises all Glossary Term Base own attributes:
>   Glossary Name (Reference Name List), Summary, Usage, Abbreviation,
>   Aliases (Simple List), Example, Folders (Reference Name List).
> Also exercises Referenceable fields: Description, Content Status, Authors.
> User-specified QN so later Link commands can reference this term reliably.

# Create Glossary Term

## Display Name
Pipeline Coverage Ratio

## Glossary Name
Glossary::SalesForecast::Domain::1.0

## Summary
The ratio of pipeline value to revenue target, used to assess whether
sufficient opportunities exist to meet the sales forecast.

## Description
Pipeline Coverage Ratio measures the total value of open opportunities in a
sales pipeline relative to the revenue target for the same period. A coverage
ratio above 3x is generally considered healthy. Values below 2x indicate
pipeline risk and may trigger forecast adjustments.

## Abbreviation
PCR

## Aliases
Pipeline Coverage, Coverage Ratio, Pipeline-to-Quota Ratio

## Example
If the Q1 revenue target is $10M and the open pipeline value is $32M,
the Pipeline Coverage Ratio is 3.2x.

## Usage
Use to evaluate pipeline health during forecast reviews. Report monthly
to Sales Operations and quarterly to the board.

## Folders
CollectionFolder::SalesForecast::SalesMetrics::1.0

## Category
Pipeline Management

## Content Status
ACTIVE

## Version Identifier
1.0

## Authors
jane.smith@example.com

## Journal Entry
Term created as part of Q1 2026 Sales Forecast governance initiative.

## Qualified Name
GlossaryTerm::SalesForecast::PipelineCoverageRatio::1.0

## GUID

___

# GL-07: Create Glossary Term — alternative Glossary Name label

> Uses the alternative label In Glossary instead of Glossary Name.
> Expected: resolved to the canonical Glossary Name attribute.

# Create Glossary Term

## Display Name
Commit Forecast

## In Glossary
Glossary::SalesForecast::Domain::1.0

## Summary
A high-confidence revenue forecast based on opportunities the sales team
has committed to closing within the period.

## Description
Commit Forecast represents the portion of the sales forecast that the field
sales team has committed to delivering. It is composed of opportunities in
the Commit stage of the CRM pipeline and is used as the baseline for
executive revenue reporting.

## Abbreviation
CF

## Example
A rep commits $500K for Q1; this contributes $500K to the Commit Forecast.

## Usage
Use as the primary forecast input for board-level revenue reporting.

## Qualified Name
GlossaryTerm::SalesForecast::CommitForecast::1.0

## GUID

___

# GL-08: Create Glossary Term — member of multiple glossaries

> Glossary Name accepts a Reference Name List — a term can belong to multiple glossaries.
> This term is added to both the Sales Forecast glossary and a second glossary.

# Create Glossary Term

## Display Name
Opportunity

## Glossary Names
Glossary::SalesForecast::Domain::1.0
Glossary::CRM::Domain::1.0

## Summary
A qualified sales prospect that has been assessed as having a realistic
chance of converting to revenue within a defined period.

## Description
An Opportunity is a CRM record representing a potential sale to an identified
customer or prospect. It includes attributes such as stage, close date, amount,
and probability. Opportunities are the primary unit of analysis in the Sales Forecast.

## Abbreviation
OPP

## Example
Account: Acme Corp, Stage: Commit, Amount: $250K, Close Date: 2026-03-31

## Usage
Reference this term when tagging CRM data structures, pipeline reports,
and forecast models that operate on opportunity-level data.

## Qualified Name
GlossaryTerm::SalesForecast::Opportunity::1.0

## GUID

___

# GL-09: Update Glossary Term — identified by Qualified Name

> Update flavor. No GUID. Term located by Qualified Name.

# Update Glossary Term

## Display Name
Pipeline Coverage Ratio

## Qualified Name
GlossaryTerm::SalesForecast::PipelineCoverageRatio::1.0

## Content Status
ACTIVE

## Journal Entry
Definition reviewed and approved by Sales Analytics governance board 2026-03-20.

___

# GL-10: Link Term-Term Relationship — Synonym, verb Link

> Links two terms as Synonyms. Term 1, Term 2, and Relationship Type are all input_required.
> No GUID on relationship commands.

# Link Term-Term Relationship

## Term 1
GlossaryTerm::SalesForecast::CommitForecast::1.0

## Term 2
GlossaryTerm::SalesForecast::PipelineCoverageRatio::1.0

## Relationship Type
RelatedTerm

## Description
Commit Forecast and Pipeline Coverage Ratio are related — PCR is used to
validate whether the Commit Forecast is achievable.

___

# GL-11: Link Term-Term Relationship — IsA, verb Attach

> Uses establish synonym Attach. Tests the IsA relationship type,
> expressing that Commit Forecast is a kind of Sales Forecast.

# Attach Term-Term Relationship

## Term 1
GlossaryTerm::SalesForecast::CommitForecast::1.0

## Term 2
GlossaryTerm::SalesForecast::Opportunity::1.0

## Relationship Type
IsA

## Description
A Commit Forecast is a specific type of Sales Forecast, representing
the high-confidence committed portion of the overall forecast.

___

# GL-12: Link Term-Term Relationship — Synonym with Advanced attributes

> Full coverage of Advanced-level Term-Term Link Base attributes:
> Expression, Confidence, Steward, Source, Term Relationship Status (Valid Value).
>
> In BASIC mode: Expression, Confidence, Steward, Source, Term Relationship Status silently skipped.
> In ADVANCED mode: all fields present in output.

# Link Term-Term Relationship

## Term 1
GlossaryTerm::SalesForecast::Opportunity::1.0

## Term 2
PDR::Glossary Term::Sales-Forecast

## Relationship Type
Synonym

## Description
Opportunity and Sales Pipeline Entry are used interchangeably in CRM reporting contexts.

## Expression
context == 'CRM_REPORTING'

## Confidence
85

## Steward
jane.smith@example.com

## Source
Q1-2026-Data-Governance-Review

## Term Relationship Status
ACTIVE

___

# GL-13: Link Term-Term Relationship — PreferredTerm, verb Add

> Uses establish synonym Add. PreferredTerm indicates Term 2 is the preferred
> form and Term 1 should be replaced by it.

# Add Term-Term Relationship

## Term 1
GlossaryTerm::SalesForecast::PipelineCoverageRatio::1.0

## Term 2
GlossaryTerm::SalesForecast::CommitForecast::1.0

## Relationship Type
PreferredTerm

## Description
When discussing forecast confidence, Commit Forecast is the preferred term
over Pipeline Coverage Ratio in executive communications.

___

# GL-14: Detach Term-Term Relationship — verb Detach

> Removes the relationship established in GL-10.
> Identified by Term 1, Term 2, and Relationship Type — no GUID.

# Detach Term-Term Relationship

## Term 1
GlossaryTerm::SalesForecast::CommitForecast::1.0

## Term 2
GlossaryTerm::SalesForecast::PipelineCoverageRatio::1.0

## Relationship Type
RelatedTerm

___

# GL-15: Unlink Term-Term Relationship — verb Unlink

> Removes the relationship established in GL-13.
> Detach and Remove are equivalent synonyms.

# Unlink Term-Term Relationship

## Term 1
GlossaryTerm::SalesForecast::PipelineCoverageRatio::1.0

## Term 2
GlossaryTerm::SalesForecast::CommitForecast::1.0

## Relationship Type
PreferredTerm

___

> End of Glossary happy path tests.
>
> Expected outcomes:
>   GL-01               : GUID filled, QN auto-generated, verb swapped to Update Glossary
>   GL-02               : GUID filled, user-specified QN preserved exactly, verb swapped
>   GL-03               : Update locates glossary by QN, applies partial update, no GUID slot
>   GL-04               : Update locates glossary by Display Name, QN filled in output
>   GL-05               : GUID filled, QN auto-generated, term linked to glossary by QN
>   GL-06               : GUID filled, user-specified QN preserved, all Term Base attrs present
>   GL-07               : In Glossary alt label resolved to Glossary Name attribute
>   GL-08               : Glossary Names (list) accepted; term linked to two glossaries
>   GL-09               : Update locates term by QN, applies partial update, no GUID slot
>   GL-10 to GL-13      : Relationship commands executed, no GUID slot
>   GL-14, GL-15        : Relationships removed; Detach and Unlink synonyms accepted
>   GL-11               : Attach synonym accepted, processed as Link Term-Term Relationship
>   GL-13               : Add synonym accepted, processed as Link Term-Term Relationship
>   GL-12 in basic mode : Expression, Confidence, Steward, Source, Term Relationship Status skipped
>   GL-12 in advanced mode : all fields present in output