This file creates the **Symptom** subject area folder (`Clinical:Symptom`) and its
Prime Words / Modifiers / Class Words sub-folders in the Data Field Naming glossary, along with any terms
specific to this subject area. It also links the folder as a member of the existing `SubjectArea::Clinical:Symptom`
governance collection (see `CocoSubjectAreaDefinition.java`), so the two structures are connected.

Requires `glossary.md` and `clinical.md` to have been processed
first, and requires the `SubjectArea::Clinical:Symptom` collection to already exist in Egeria.

____

## Create Collection Folder

### Display Name

Symptom

### Qualified Name

CollectionFolder::DataFieldNaming:Clinical:Symptom

### Purpose

Groups the data field naming terms (prime words, modifiers, class words) for the Symptom subject area. Information relating to the symptoms of a medical condition.

### Parent ID

CollectionFolder::DataFieldNaming:Clinical

### Parent Relationship Type Name

CollectionMembership

___

## Add Member to Collection
> Add/Remove a member to/from a collection.

### Element Id

CollectionFolder::DataFieldNaming:Clinical:Symptom

### Membership Rationale

Link the Symptom subject area to its data field naming vocabulary.

### Membership Status

VALIDATED

### Collection Id

SubjectArea::Clinical:Symptom

___

## Create Collection Folder

### Display Name

Prime Words

### Qualified Name

CollectionFolder::DataFieldNaming:Clinical:Symptom:PrimeWords

### Purpose

Prime words - the core business nouns - used to build data field names for the Symptom subject area.

### Parent ID

CollectionFolder::DataFieldNaming:Clinical:Symptom

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Modifiers

### Qualified Name

CollectionFolder::DataFieldNaming:Clinical:Symptom:Modifiers

### Purpose

Modifiers specific to the Symptom subject area, used to qualify a prime word or class word when building data field names.

### Parent ID

CollectionFolder::DataFieldNaming:Clinical:Symptom

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Class Words

### Qualified Name

CollectionFolder::DataFieldNaming:Clinical:Symptom:ClassWords

### Purpose

Class words specific to the Symptom subject area, used as the trailing element of a data field name.

### Parent ID

CollectionFolder::DataFieldNaming:Clinical:Symptom

### Parent Relationship Type Name

CollectionMembership

___

# Symptom

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Symptom

### Abbreviation

SX

### Aliases

- Sign
- Presentation
- Complaint

### Glossary Name

- Glossary::DataFieldNaming

### Summary

A physical or mental feature indicating a medical condition, as reported or observed.

### Folders

CollectionFolder::DataFieldNaming:Clinical:Symptom:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Symptom

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Reported

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Reported

### Aliases

- Patient-Reported
- Self-Reported

### Glossary Name

- Glossary::DataFieldNaming

### Summary

Relating to a symptom as described by the patient, e.g. `ReportedSymptomSeverity`.

### Folders

CollectionFolder::DataFieldNaming:Clinical:Symptom:Modifiers

### Qualified Name

GlossaryTerm::DataFieldNaming::Reported

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Observed

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Observed

### Aliases

- Clinician-Observed
- Noted

### Glossary Name

- Glossary::DataFieldNaming

### Summary

Relating to a symptom as noted by a clinician, e.g. `ObservedSymptomSeverity`.

### Folders

CollectionFolder::DataFieldNaming:Clinical:Symptom:Modifiers

### Qualified Name

GlossaryTerm::DataFieldNaming::Observed

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Severity

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Severity

### Abbreviation

SEV

### Aliases

- Intensity
- Grading

### Glossary Name

- Glossary::DataFieldNaming

### Summary

A measure of how serious a symptom or condition is, e.g. `SymptomSeverity`.

### Folders

CollectionFolder::DataFieldNaming:Clinical:Symptom:ClassWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Severity

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___
