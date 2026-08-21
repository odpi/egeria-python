# Curation Family — Regression Coverage
# (plus Create Meeting / Create ToDo / Create Review — Person Action Base bundle)

> Exercises every implemented Curation family command (classifications and
> relationships applied to *existing* elements) plus the three Person Action
> Base commands that live in other families' compact specs (Create Meeting
> in Project, Create ToDo in Actor Manager, Create Review in Feedback).
>
> Run with VALIDATE first, then PROCESS.
>
> Setup (CT-01..CT-04) creates two throwaway Data Dictionary elements (Target,
> Peer) and a throwaway Glossary + Term, all referenced by qualified name in
> the commands that follow -- consistent with the "Create commands referenced
> later always carry a user-specified Qualified Name" convention used
> throughout this test folder.
>
> Intentionally NOT covered (known, documented gap -- see
> docs/dr_egeria_manual.md's Curation section):
>   - Update/Detach Search Keyword -- need the SearchKeyword entity's own
>     GUID, which this command's attribute set has no way to reference.
>
> No classification in this family remains genuinely unimplemented as of
> 2026-08-21 -- Class Word/Modifier/Prime Word (2026-08-09), and Policy
> Management Point plus 9 sibling governance-point classifications, 6
> classification-explorer markers, ProjectKind, CollectionKind, and a Data
> Sharing Agreement retrofit pair (2026-08-21), are all now registered.
> None of the 2026-08-21 additions have dedicated regression coverage in
> this file yet -- add cases here if you're touching that area.
>
> `--process` cleanup: this file creates two Data Dictionaries, one Glossary,
> one Glossary Term, one Meeting, one ToDo, and one Review as persistent
> elements. Delete them from the target server after the run if you don't
> want them left behind (Curation's classify/link commands themselves clean
> up after each other -- Declassify/Unlink blocks immediately follow their
> Classify/Link counterparts).

---

# CT-01: Create anchor element (classification/link target)

## Create Data Dictionary

### Display Name
Curation Test Target

### Description
Anchor element for Curation family regression coverage (classifications and relationship Target Element).

### Content Status
ACTIVE

### Version Identifier
1.0

### Authors
dr-egeria-tests@example.com

### Qualified Name
DataDictionary::CurationTest::Target::1.0

### GUID

___

# CT-02: Create peer element (relationship 'other side')

## Create Data Dictionary

### Display Name
Curation Test Peer

### Description
Second element for Curation relationship commands (Scope Reference, Resource, More Information Resource, Peer Duplicate, Consolidated Source).

### Content Status
ACTIVE

### Version Identifier
1.0

### Authors
dr-egeria-tests@example.com

### Qualified Name
DataDictionary::CurationTest::Peer::1.0

### GUID

___

# CT-03: Create glossary for Semantic Assignment / Semantic Definition

## Create Glossary

### Display Name
Curation Test Glossary

### Description
Glossary providing the term used by Semantic Assignment and Semantic Definition regression coverage.

### Qualified Name
Glossary::CurationTest::1.0

### GUID

___

# CT-04: Create glossary term for Semantic Assignment / Semantic Definition

## Create Glossary Term

### Display Name
Curation Test Term

### Glossary Name
Glossary::CurationTest::1.0

### Qualified Name
GlossaryTerm::CurationTest::Term::1.0

### GUID

___

# CT-05: Classify Impact

## Classify Impact

### Target Element
DataDictionary::CurationTest::Target::1.0

### Level Identifier
2

### Governance Status
ACTIVE

### Steward
steward@example.com

### Source
Data Governance Team

### Description
Applied by dr_test_curation.md regression coverage.

___

# CT-06: Reclassify Impact

## Reclassify Impact

### Target Element
DataDictionary::CurationTest::Target::1.0

### Level Identifier
2

### Governance Status
ACTIVE

### Steward
steward@example.com

### Source
Data Governance Team

### Description
Applied by dr_test_curation.md regression coverage.

___

# CT-07: Declassify Impact

## Declassify Impact

### Target Element
DataDictionary::CurationTest::Target::1.0

___

# CT-08: Classify Confidence

## Classify Confidence

### Target Element
DataDictionary::CurationTest::Target::1.0

### Level Identifier
2

### Governance Status
ACTIVE

### Steward
steward@example.com

### Source
Data Governance Team

### Description
Applied by dr_test_curation.md regression coverage.

___

# CT-09: Reclassify Confidence

## Reclassify Confidence

### Target Element
DataDictionary::CurationTest::Target::1.0

### Level Identifier
2

### Governance Status
ACTIVE

### Steward
steward@example.com

### Source
Data Governance Team

### Description
Applied by dr_test_curation.md regression coverage.

___

# CT-10: Declassify Confidence

## Declassify Confidence

### Target Element
DataDictionary::CurationTest::Target::1.0

___

# CT-11: Classify Confidentiality

## Classify Confidentiality

### Target Element
DataDictionary::CurationTest::Target::1.0

### Level Identifier
2

### Governance Status
ACTIVE

### Steward
steward@example.com

### Source
Data Governance Team

### Description
Applied by dr_test_curation.md regression coverage.

___

# CT-12: Reclassify Confidentiality

## Reclassify Confidentiality

### Target Element
DataDictionary::CurationTest::Target::1.0

### Level Identifier
2

### Governance Status
ACTIVE

### Steward
steward@example.com

### Source
Data Governance Team

### Description
Applied by dr_test_curation.md regression coverage.

___

# CT-13: Declassify Confidentiality

## Declassify Confidentiality

### Target Element
DataDictionary::CurationTest::Target::1.0

___

# CT-14: Classify Criticality

## Classify Criticality

### Target Element
DataDictionary::CurationTest::Target::1.0

### Level Identifier
2

### Governance Status
ACTIVE

### Steward
steward@example.com

### Source
Data Governance Team

### Description
Applied by dr_test_curation.md regression coverage.

___

# CT-15: Reclassify Criticality

## Reclassify Criticality

### Target Element
DataDictionary::CurationTest::Target::1.0

### Level Identifier
2

### Governance Status
ACTIVE

### Steward
steward@example.com

### Source
Data Governance Team

### Description
Applied by dr_test_curation.md regression coverage.

___

# CT-16: Declassify Criticality

## Declassify Criticality

### Target Element
DataDictionary::CurationTest::Target::1.0

___

# CT-17: Classify Retention

## Classify Retention

### Target Element
DataDictionary::CurationTest::Target::1.0

### Level Identifier
2

### Governance Status
ACTIVE

### Steward
steward@example.com

### Source
Data Governance Team

### Description
Applied by dr_test_curation.md regression coverage.

### Retention Basis
PROJECT_LIFETIME

### Archive After
2027-01-01

### Delete After
2028-01-01

___

# CT-18: Reclassify Retention

## Reclassify Retention

### Target Element
DataDictionary::CurationTest::Target::1.0

### Level Identifier
2

### Governance Status
ACTIVE

### Steward
steward@example.com

### Source
Data Governance Team

### Description
Applied by dr_test_curation.md regression coverage.

### Retention Basis
PROJECT_LIFETIME

### Archive After
2027-01-01

### Delete After
2028-01-01

___

# CT-19: Declassify Retention

## Declassify Retention

### Target Element
DataDictionary::CurationTest::Target::1.0

___

# CT-20: Classify Ownership (minimal -- Owner intentionally omitted, see note below)

> Owner/Owner Type Name/Owner Property Name are all optional (min_cardinality 0); omitted here to avoid needing a throwaway actor profile just for this test.

## Classify Ownership

### Target Element
DataDictionary::CurationTest::Target::1.0

___

# CT-21: Reclassify Ownership

## Reclassify Ownership

### Target Element
DataDictionary::CurationTest::Target::1.0

___

# CT-22: Declassify Ownership

## Declassify Ownership

### Target Element
DataDictionary::CurationTest::Target::1.0

___

# CT-23: Classify Digital Resource Origin (minimal -- Organization/Business Capability omitted)

> Organization/Business Capability are Reference Name attributes (optional); omitted for the same reason as Ownership above. Also see the NOTE in curation.py's CLASSIFICATION_METHODS -- this field mapping is best-effort/unverified against a live server.

## Classify Digital Resource Origin

### Target Element
DataDictionary::CurationTest::Target::1.0

___

# CT-24: Reclassify Digital Resource Origin

## Reclassify Digital Resource Origin

### Target Element
DataDictionary::CurationTest::Target::1.0

___

# CT-25: Declassify Digital Resource Origin

## Declassify Digital Resource Origin

### Target Element
DataDictionary::CurationTest::Target::1.0

___

# CT-26: Classify Zone Membership

## Classify Zone Membership

### Target Element
DataDictionary::CurationTest::Target::1.0

### Zone Membership
governance-zone-1, governance-zone-2

___

# CT-27: Reclassify Zone Membership

## Reclassify Zone Membership

### Target Element
DataDictionary::CurationTest::Target::1.0

### Zone Membership
governance-zone-1

___

# CT-28: Declassify Zone Membership

## Declassify Zone Membership

### Target Element
DataDictionary::CurationTest::Target::1.0

___

# CT-29: Classify Security Tags

## Classify Security Tags

### Target Element
DataDictionary::CurationTest::Target::1.0

### Security Labels
confidential, restricted

### Security Properties
{"classification-source": "dr-egeria-test"}

___

# CT-30: Reclassify Security Tags

## Reclassify Security Tags

### Target Element
DataDictionary::CurationTest::Target::1.0

### Security Labels
confidential

___

# CT-31: Declassify Security Tags

## Declassify Security Tags

### Target Element
DataDictionary::CurationTest::Target::1.0

___

# CT-32: Classify Data Scope

## Classify Data Scope

### Target Element
DataDictionary::CurationTest::Target::1.0

### Description
Initial data scope for regression coverage.

### Additional Properties
{"region": "test"}

___

# CT-33: Update Data Scope

## Update Data Scope

### Target Element
DataDictionary::CurationTest::Target::1.0

### Description
Updated data scope for regression coverage.

___

# CT-34: Declassify Data Scope

## Declassify Data Scope

### Target Element
DataDictionary::CurationTest::Target::1.0

___

# CT-35: Classify Governance Expectations

## Classify Governance Expectations

### Target Element
DataDictionary::CurationTest::Target::1.0

### Governance Expectations Counts
{"expectedRecords": 100}

___

# CT-36: Update Governance Expectations

## Update Governance Expectations

### Target Element
DataDictionary::CurationTest::Target::1.0

### Governance Expectations Counts
{"expectedRecords": 150}

___

# CT-37: Declassify Governance Expectations

## Declassify Governance Expectations

### Target Element
DataDictionary::CurationTest::Target::1.0

___

# CT-38: Classify Governance Measurements

## Classify Governance Measurements

### Target Element
DataDictionary::CurationTest::Target::1.0

### Governance Measurements
{"actualRecords": 90}

___

# CT-39: Update Governance Measurements

## Update Governance Measurements

### Target Element
DataDictionary::CurationTest::Target::1.0

### Governance Measurements
{"actualRecords": 95}

___

# CT-40: Declassify Governance Measurements

## Declassify Governance Measurements

### Target Element
DataDictionary::CurationTest::Target::1.0

___

# CT-41: Classify Known Duplicate

## Classify Known Duplicate

### Target Element
DataDictionary::CurationTest::Target::1.0

### Duplicate Notes
Flagged as a known duplicate for regression coverage.

___

# CT-42: Declassify Known Duplicate

## Declassify Known Duplicate

### Target Element
DataDictionary::CurationTest::Target::1.0

___

# CT-43: Classify Consolidated Duplicate

## Classify Consolidated Duplicate

### Target Element
DataDictionary::CurationTest::Target::1.0

### Duplicate Notes
Flagged as a consolidated duplicate for regression coverage.

___

# CT-44: Declassify Consolidated Duplicate

## Declassify Consolidated Duplicate

### Target Element
DataDictionary::CurationTest::Target::1.0

___

# CT-45: Attach Search Keyword

> Update/Detach Search Keyword are intentionally NOT covered here -- they are a known, documented gap (need the SearchKeyword entity's own GUID, which this command's attribute set has no way to reference; see docs/dr_egeria_manual.md).

## Attach Search Keyword

### Target Element
DataDictionary::CurationTest::Target::1.0

### Keyword
curation-test-keyword

### Keyword Description
Test keyword for Attach Search Keyword regression coverage.

___

# CT-46: Link Semantic Assignment

## Link Semantic Assignment

### Target Element
DataDictionary::CurationTest::Target::1.0

### Glossary Term
GlossaryTerm::CurationTest::Term::1.0

### Confidence Level
80

### Semantic Expression
is exactly

### Steward
steward@example.com

### Source
Data Governance Team

### Governance Status
ACTIVE

___

# CT-47: Unlink Semantic Assignment

## Unlink Semantic Assignment

### Target Element
DataDictionary::CurationTest::Target::1.0

### Glossary Term
GlossaryTerm::CurationTest::Term::1.0

___

# CT-48: Link Semantic Definition

> Target Element here is a Data Dictionary for test simplicity. A live --process run of this command normally needs a real data-definition element (DataField/DataStructure/DataClass), since it calls data_designer._async_link_semantic_definition -- see the OM_TYPE=SemanticDefinition note in md_processing/v2/curation.py.

## Link Semantic Definition

### Target Element
DataDictionary::CurationTest::Target::1.0

### Semantic Definition
GlossaryTerm::CurationTest::Term::1.0

### Description
Formal definition link for regression coverage.

___

# CT-49: Unlink Semantic Definition

## Unlink Semantic Definition

### Target Element
DataDictionary::CurationTest::Target::1.0

### Semantic Definition
GlossaryTerm::CurationTest::Term::1.0

___

# CT-50: Link Element To Scope

## Link Element To Scope

### Target Element
DataDictionary::CurationTest::Target::1.0

### Scope Reference
DataDictionary::CurationTest::Peer::1.0

___

# CT-51: Unlink Element From Scope

## Unlink Element From Scope

### Target Element
DataDictionary::CurationTest::Target::1.0

### Scope Reference
DataDictionary::CurationTest::Peer::1.0

___

# CT-52: Link Resource To Element

## Link Resource To Element

### Target Element
DataDictionary::CurationTest::Target::1.0

### Resource
DataDictionary::CurationTest::Peer::1.0

### Resource Use
Related Information

___

# CT-53: Unlink Resource From Element

## Unlink Resource From Element

### Target Element
DataDictionary::CurationTest::Target::1.0

### Resource
DataDictionary::CurationTest::Peer::1.0

___

# CT-54: Link More Information

## Link More Information

### Target Element
DataDictionary::CurationTest::Target::1.0

### More Information Resource
DataDictionary::CurationTest::Peer::1.0

___

# CT-55: Unlink More Information

## Unlink More Information

### Target Element
DataDictionary::CurationTest::Target::1.0

### More Information Resource
DataDictionary::CurationTest::Peer::1.0

___

# CT-56: Link Peer Duplicate

## Link Peer Duplicate

### Target Element
DataDictionary::CurationTest::Target::1.0

### Peer Duplicate
DataDictionary::CurationTest::Peer::1.0

### Duplicate Notes
Linked as a peer duplicate for regression coverage.

___

# CT-57: Unlink Peer Duplicate

## Unlink Peer Duplicate

### Target Element
DataDictionary::CurationTest::Target::1.0

### Peer Duplicate
DataDictionary::CurationTest::Peer::1.0

___

# CT-58: Link Consolidated Duplicate To Source

## Link Consolidated Duplicate To Source

### Target Element
DataDictionary::CurationTest::Target::1.0

### Consolidated Source
DataDictionary::CurationTest::Peer::1.0

___

# CT-59: Unlink Consolidated Duplicate From Source

## Unlink Consolidated Duplicate From Source

### Target Element
DataDictionary::CurationTest::Target::1.0

### Consolidated Source
DataDictionary::CurationTest::Peer::1.0

___

# CT-60: Create Meeting (Project family, Person Action Base bundle)

## Create Meeting

### Display Name
Curation Regression Kickoff

### Situation
Kickoff meeting to review Curation family regression coverage.

### Objective
Confirm all Curation commands are wired to real pyegeria calls.

### Activity Status
REQUESTED

### Description
Created by dr_test_curation.md regression coverage.

___

# CT-61: Create ToDo (Actor Manager family, Person Action Base bundle)

## Create ToDo

### Display Name
Follow up on Curation regression results

### Situation
Regression run flagged items needing manual review.

### Priority
5

### Activity Status
REQUESTED

### Description
Created by dr_test_curation.md regression coverage.

___

# CT-62: Create Review (Feedback family, Person Action Base bundle)

## Create Review

### Display Name
Review Curation family output

### Situation
Peer review of Curation regression run results.

### Activity Status
REQUESTED

### Description
Created by dr_test_curation.md regression coverage.

