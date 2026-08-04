This file creates the **Clinical** subject area folder (`Clinical`) and its
Prime Words / Modifiers / Class Words sub-folders in the Data Field Naming glossary, along with any terms
specific to this subject area. It also links the folder as a member of the existing `SubjectArea::Clinical`
governance collection (see `CocoSubjectAreaDefinition.java`), so the two structures are connected.

Requires `glossary.md` to have been processed
first, and requires the `SubjectArea::Clinical` collection to already exist in Egeria.

____

## Create Collection Folder

### Display Name

Clinical

### Qualified Name

CollectionFolder::DataFieldNaming:Clinical

### Purpose

Groups the data field naming terms (prime words, modifiers, class words) for the Clinical subject area. Information relating to the work understanding medical conditions and their resolution.

### Parent ID

Glossary::DataFieldNaming

### Parent Relationship Type Name

CollectionMembership

___

## Add Member to Collection
> Add/Remove a member to/from a collection.

### Element Id

CollectionFolder::DataFieldNaming:Clinical

### Membership Rationale

Link the Clinical subject area to its data field naming vocabulary.

### Membership Status

VALIDATED

### Collection Id

SubjectArea::Clinical

___

## Create Collection Folder

### Display Name

Prime Words

### Qualified Name

CollectionFolder::DataFieldNaming:Clinical:PrimeWords

### Purpose

Prime words - the core business nouns - used to build data field names for the Clinical subject area.

### Parent ID

CollectionFolder::DataFieldNaming:Clinical

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Modifiers

### Qualified Name

CollectionFolder::DataFieldNaming:Clinical:Modifiers

### Purpose

Modifiers specific to the Clinical subject area, used to qualify a prime word or class word when building data field names.

### Parent ID

CollectionFolder::DataFieldNaming:Clinical

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Class Words

### Qualified Name

CollectionFolder::DataFieldNaming:Clinical:ClassWords

### Purpose

Class words specific to the Clinical subject area, used as the trailing element of a data field name.

### Parent ID

CollectionFolder::DataFieldNaming:Clinical

### Parent Relationship Type Name

CollectionMembership

___

# Condition

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Condition

### Aliases

- Ailment
- Disorder

### Glossary Name

- Glossary::DataFieldNaming

### Summary

A medical condition being investigated, monitored or treated.

### Folders

CollectionFolder::DataFieldNaming:Clinical:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Condition

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Diagnosis

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Diagnosis

### Abbreviation

DX

### Glossary Name

- Glossary::DataFieldNaming

### Summary

The identification of a medical condition based on its signs and symptoms.

### Folders

CollectionFolder::DataFieldNaming:Clinical:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Diagnosis

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___
