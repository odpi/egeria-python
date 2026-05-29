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
>   RelatedTerm, Synonym, Antonym, PreferredTerm, ReplacementTerm, Translation, ISA, ValidValue

---

# GL-01: Create Glossary — minimal, QN auto-generated

> Display Name only. Expected: GUID filled, QN auto-generated, verb swapped to Update Glossary.


## Update Glossary

### Glossary Name 

Sales Forecast Glossary

### Category
None

### Description
None

### Display Name
Sales Forecast Glossary

### GUID
None

### Qualified Name
CocoPharma::Glossary::Sales-Forecast-Glossary::1.0

### Url
None

### Version Identifier
1.0

### Authors
None

### Content Status
ACTIVE

### Purpose
None

### Language
English

### Usage
None


___

# GL-02: Create Glossary — full coverage, user-specified QN

> Exercises all Glossary Base own attributes: Language, Usage.
> Also exercises Referenceable/Authored Referenceable fields:
>   Description, Category, Content Status, Version Identifier,
>   Search Keywords, Authors, Journal Entry.
> User-specified QN for reliable downstream term reference.


## Update Glossary

### Glossary Name 

Sales Forecast Domain Glossary

### Category
Sales Analytics

### Description
Controlled vocabulary for the Sales Forecasting domain. Defines key business terms
used across CRM data, pipeline management, revenue reporting, and governance.

### Display Name
Sales Forecast Domain Glossary

### GUID
None

### Qualified Name
Glossary::SalesForecast::Domain::1.0

### Url
None

### Version Identifier
1.0

### Authors
- jane.smith@example.com

### Content Status
ACTIVE

### Purpose
None

### Language
English

### Usage
Use this glossary to tag data assets, fields, and governance definitions within
the Sales Forecasting domain. All analysts and stewards should reference these
definitions before creating new metadata elements.


___

# GL-03: Update Glossary — identified by Qualified Name

> Update flavor. No GUID. Element located by Qualified Name.
> Only changed fields provided; Merge Update defaults to True.


## Update Glossary

### Glossary Name 

Sales Forecast Domain Glossary

### Category
Sales Analytics

### Description
Controlled vocabulary for the Sales Forecasting domain. Updated to include
additional pipeline and CRM terms following the Q1 2026 data quality review.

### Display Name
Sales Forecast Domain Glossary

### GUID
None

### Qualified Name
Glossary::SalesForecast::Domain::1.0

### Url
None

### Version Identifier
1.0

### Authors
- jane.smith@example.com

### Content Status
ACTIVE

### Purpose
None

### Language
English

### Usage
Use this glossary to tag data assets, fields, and governance definitions within
the Sales Forecasting domain. All analysts and stewards should reference these
definitions before creating new metadata elements.


___

# GL-04: Update Glossary — identified by Display Name only

> No QN provided. Dr.Egeria forms a QN from Display Name and attempts to match.
> Expected: element matched and updated, QN filled in output.


## Update Glossary

### Glossary Name 

Sales Forecast Glossary

### Category
None

### Description
Minimal glossary used for smoke testing. Updated with a description.

### Display Name
Sales Forecast Glossary

### GUID
None

### Qualified Name
CocoPharma::Glossary::Sales-Forecast-Glossary

### Url
None

### Version Identifier
None

### Authors
None

### Content Status
None

### Purpose
None

### Language
English

### Usage
None


___

# GL-05: Create Glossary Term — minimal, QN auto-generated

> Display Name only plus Glossary Name to link the term to its glossary.
> Expected: GUID filled, QN auto-generated, verb swapped to Update Glossary Term.


## Update Glossary Term

### Glossary Term Name 

Sales Forecast

### Category
None

### Description
None

### Display Name
Sales Forecast

### GUID
None

### Qualified Name
CocoPharma::Term::Sales-Forecast::1.0

### Url
None

### Version Identifier
1.0

### Authors
None

### Content Status
ACTIVE

### Abbreviation
None

### Aliases
None

### Example
None

### Folders
None

### Glossary Name
None

### Summary
None

### Usage
None


___


## Update Collection Folder

### Collection Folder Name 

Sales Metrics

### Category
None

### Description
A collection of metrics related to sales performance.

### Display Name
Sales Metrics

### GUID
None

### Qualified Name
CollectionFolder::SalesForecast::SalesMetrics::1.0

### Url
None

### Version Identifier
1.0

### Authors
None

### Content Status
ACTIVE

### Purpose
None


____

# GL-06: Create Glossary Term — full coverage, user-specified QN

> Exercises all Glossary Term Base own attributes:
>   Glossary Name (Reference Name List), Summary, Usage, Abbreviation,
>   Aliases (Simple List), Example, Folders (Reference Name List).
> Also exercises Referenceable fields: Description, Content Status, Authors.
> User-specified QN so later Link commands can reference this term reliably.


## Update Glossary Term

### Glossary Term Name 

Pipeline Coverage Ratio

### Category
Pipeline Management

### Description
Pipeline Coverage Ratio measures the total value of open opportunities in a
sales pipeline relative to the revenue target for the same period. A coverage
ratio above 3x is generally considered healthy. Values below 2x indicate
pipeline risk and may trigger forecast adjustments.

### Display Name
Pipeline Coverage Ratio

### GUID
None

### Qualified Name
GlossaryTerm::SalesForecast::PipelineCoverageRatio::1.0

### Url
None

### Version Identifier
1.0

### Authors
- jane.smith@example.com

### Content Status
ACTIVE

### Abbreviation
PCR

### Aliases
- Pipeline Coverage
- Coverage Ratio
- Pipeline-to-Quota Ratio

### Example
None

### Folders
None

### Glossary Name
None

### Summary
The ratio of pipeline value to revenue target, used to assess whether
sufficient opportunities exist to meet the sales forecast.

### Usage
Use to evaluate pipeline health during forecast reviews. Report monthly
to Sales Operations and quarterly to the board.


___

# GL-07: Create Glossary Term — alternative Glossary Name label

> Uses the alternative label In Glossary instead of Glossary Name.
> Expected: resolved to the canonical Glossary Name attribute.


## Update Glossary Term

### Glossary Term Name 

Commit Forecast

### Category
None

### Description
Commit Forecast represents the portion of the sales forecast that the field
sales team has committed to delivering. It is composed of opportunities in
the Commit stage of the CRM pipeline and is used as the baseline for
executive revenue reporting.

### Display Name
Commit Forecast

### GUID
None

### Qualified Name
GlossaryTerm::SalesForecast::CommitForecast::1.0

### Url
None

### Version Identifier
1.0

### Authors
None

### Content Status
ACTIVE

### Abbreviation
CF

### Aliases
None

### Example
None

### Folders
None

### Glossary Name
None

### Summary
A high-confidence revenue forecast based on opportunities the sales team
has committed to closing within the period.

### Usage
Use as the primary forecast input for board-level revenue reporting.


___

# GL-08: Create Glossary Term — member of multiple glossaries

> Glossary Name accepts a Reference Name List — a term can belong to multiple glossaries.
> This term is added to both the Sales Forecast glossary and a second glossary.


## Update Glossary Term

### Glossary Term Name 

Opportunity

### Category
None

### Description
An Opportunity is a CRM record representing a potential sale to an identified
customer or prospect. It includes attributes such as stage, close date, amount,
and probability. Opportunities are the primary unit of analysis in the Sales Forecast.

### Display Name
Opportunity

### GUID
None

### Qualified Name
GlossaryTerm::SalesForecast::Opportunity::1.0

### Url
None

### Version Identifier
1.0

### Authors
None

### Content Status
ACTIVE

### Abbreviation
OPP

### Aliases
None

### Example
None

### Folders
None

### Glossary Name
None

### Summary
A qualified sales prospect that has been assessed as having a realistic
chance of converting to revenue within a defined period.

### Usage
Reference this term when tagging CRM data structures, pipeline reports,
and forecast models that operate on opportunity-level data.


___

# GL-09: Update Glossary Term — identified by Qualified Name

> Update flavor. No GUID. Term located by Qualified Name.


## Update Glossary Term

### Glossary Term Name 

Pipeline Coverage Ratio

### Category
Pipeline Management

### Description
Pipeline Coverage Ratio measures the total value of open opportunities in a
sales pipeline relative to the revenue target for the same period. A coverage
ratio above 3x is generally considered healthy. Values below 2x indicate
pipeline risk and may trigger forecast adjustments.

### Display Name
Pipeline Coverage Ratio

### GUID
None

### Qualified Name
GlossaryTerm::SalesForecast::PipelineCoverageRatio::1.0

### Url
None

### Version Identifier
1.0

### Authors
- jane.smith@example.com

### Content Status
ACTIVE

### Abbreviation
PCR

### Aliases
- Pipeline Coverage
- Coverage Ratio
- Pipeline-to-Quota Ratio

### Example
None

### Folders
None

### Glossary Name
None

### Summary
The ratio of pipeline value to revenue target, used to assess whether
sufficient opportunities exist to meet the sales forecast.

### Usage
Use to evaluate pipeline health during forecast reviews. Report monthly
to Sales Operations and quarterly to the board.


___

# GL-10: Link Term-Term Relationship — Synonym, verb Link

> Links two terms as Synonyms. Term 1, Term 2, and Relationship Type are all input_required.
> No GUID on relationship commands.



## Link Term-Term Relationship

### Term 1 Name:

None

### Term 2 Name:

None

### Term Relationship:

RelatedTerm
___

# GL-11: Link Term-Term Relationship — IsA, verb Attach

> Uses establish synonym Attach. Tests the IsA relationship type,
> expressing that Commit Forecast is a kind of Sales Forecast.



## Attach Term-Term Relationship

### Term 1 Name:

None

### Term 2 Name:

None

### Term Relationship:

ISARelationship
___

# GL-12: Link Term-Term Relationship — Synonym with Advanced attributes

> Full coverage of Advanced-level Term-Term Link Base attributes:
> Expression, Confidence, Steward, Source, Term Relationship Status (Valid Value).
>
> In BASIC mode: Expression, Confidence, Steward, Source, Term Relationship Status silently skipped.
> In ADVANCED mode: all fields present in output.



## Link Term-Term Relationship

### Term 1 Name:

None

### Term 2 Name:

None

### Term Relationship:

Synonym
___

# GL-13: Link Term-Term Relationship — PreferredTerm, verb Add

> Uses establish synonym Add. PreferredTerm indicates Term 2 is the preferred
> form and Term 1 should be replaced by it.



## Add Term-Term Relationship

### Term 1 Name:

None

### Term 2 Name:

None

### Term Relationship:

PreferredTerm
___

# GL-14: Detach Term-Term Relationship — verb Detach

> Removes the relationship established in GL-10.
> Identified by Term 1, Term 2, and Relationship Type — no GUID.



## Detach Term-Term Relationship

### Term 1 Name:

None

### Term 2 Name:

None

### Term Relationship:

RelatedTerm
___

# GL-15: Unlink Term-Term Relationship — verb Unlink

> Removes the relationship established in GL-13.
> Detach and Remove are equivalent synonyms.



## Unlink Term-Term Relationship

### Term 1 Name:

None

### Term 2 Name:

None

### Term Relationship:

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



## Provenance:
 
- Derived from processing file dr_test_glossary.md on 2026-05-19 21:20
