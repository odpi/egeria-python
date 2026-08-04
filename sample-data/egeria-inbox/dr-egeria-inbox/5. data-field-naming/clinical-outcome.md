This file creates the **Outcome** subject area folder (`Clinical:Outcome`) and its
Prime Words / Modifiers / Class Words sub-folders in the Data Field Naming glossary, along with any terms
specific to this subject area. It also links the folder as a member of the existing `SubjectArea::Clinical:Outcome`
governance collection (see `CocoSubjectAreaDefinition.java`), so the two structures are connected.

Requires `glossary.md` and `clinical.md` to have been processed
first, and requires the `SubjectArea::Clinical:Outcome` collection to already exist in Egeria.

____

## Create Collection Folder

### Display Name

Outcome

### Qualified Name

CollectionFolder::DataFieldNaming:Clinical:Outcome

### Purpose

Groups the data field naming terms (prime words, modifiers, class words) for the Outcome subject area. Information relating to the work understanding the result of a course of treatment.

### Parent ID

CollectionFolder::DataFieldNaming:Clinical

### Parent Relationship Type Name

CollectionMembership

___

## Add Member to Collection
> Add/Remove a member to/from a collection.

### Element Id

CollectionFolder::DataFieldNaming:Clinical:Outcome

### Membership Rationale

Link the Outcome subject area to its data field naming vocabulary.

### Membership Status

VALIDATED

### Collection Id

SubjectArea::Clinical:Outcome

___

## Create Collection Folder

### Display Name

Prime Words

### Qualified Name

CollectionFolder::DataFieldNaming:Clinical:Outcome:PrimeWords

### Purpose

Prime words - the core business nouns - used to build data field names for the Outcome subject area.

### Parent ID

CollectionFolder::DataFieldNaming:Clinical:Outcome

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Modifiers

### Qualified Name

CollectionFolder::DataFieldNaming:Clinical:Outcome:Modifiers

### Purpose

Modifiers specific to the Outcome subject area, used to qualify a prime word or class word when building data field names.

### Parent ID

CollectionFolder::DataFieldNaming:Clinical:Outcome

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Class Words

### Qualified Name

CollectionFolder::DataFieldNaming:Clinical:Outcome:ClassWords

### Purpose

Class words specific to the Outcome subject area, used as the trailing element of a data field name.

### Parent ID

CollectionFolder::DataFieldNaming:Clinical:Outcome

### Parent Relationship Type Name

CollectionMembership

___

# Outcome

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Outcome

### Aliases

- Result

### Glossary Name

- Glossary::DataFieldNaming

### Summary

The measured result of a course of treatment.

### Folders

CollectionFolder::DataFieldNaming:Clinical:Outcome:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Outcome

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# AdverseEvent

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

AdverseEvent

### Abbreviation

AE

### Aliases

- Side Effect
- Adverse Reaction

### Glossary Name

- Glossary::DataFieldNaming

### Summary

An unintended and unwanted medical occurrence associated with treatment.

### Folders

CollectionFolder::DataFieldNaming:Clinical:Outcome:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::AdverseEvent

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Expected

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Expected

### Aliases

- Anticipated
- Known

### Glossary Name

- Glossary::DataFieldNaming

### Summary

Relating to an outcome anticipated as part of standard treatment, e.g. `ExpectedOutcomeDescription`.

### Folders

CollectionFolder::DataFieldNaming:Clinical:Outcome:Modifiers

### Qualified Name

GlossaryTerm::DataFieldNaming::Expected

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Unexpected

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Unexpected

### Aliases

- Unanticipated
- Unknown

### Glossary Name

- Glossary::DataFieldNaming

### Summary

Relating to an outcome not anticipated as part of standard treatment, e.g. `UnexpectedOutcomeDescription`.

### Folders

CollectionFolder::DataFieldNaming:Clinical:Outcome:Modifiers

### Qualified Name

GlossaryTerm::DataFieldNaming::Unexpected

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___
