This file creates the **Person** subject area folder (`Person`) and its
Prime Words / Modifiers / Class Words sub-folders in the Data Field Naming glossary, along with any terms
specific to this subject area. It also links the folder as a member of the existing `SubjectArea::Person`
governance collection (see `CocoSubjectAreaDefinition.java`), so the two structures are connected.

Requires `glossary.md` to have been processed
first, and requires the `SubjectArea::Person` collection to already exist in Egeria.

____

## Create Collection Folder

### Display Name

Person

### Qualified Name

CollectionFolder::DataFieldNaming:Person

### Purpose

Groups the data field naming terms (prime words, modifiers, class words) for the Person subject area. Information relating to an individual.

### Parent ID

Glossary::DataFieldNaming

### Parent Relationship Type Name

CollectionMembership

___

## Add Member to Collection
> Add/Remove a member to/from a collection.

### Element Id

CollectionFolder::DataFieldNaming:Person

### Membership Rationale

Link the Person subject area to its data field naming vocabulary.

### Membership Status

VALIDATED

### Collection Id

SubjectArea::Person

___

## Create Collection Folder

### Display Name

Prime Words

### Qualified Name

CollectionFolder::DataFieldNaming:Person:PrimeWords

### Purpose

Prime words - the core business nouns - used to build data field names for the Person subject area.

### Parent ID

CollectionFolder::DataFieldNaming:Person

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Modifiers

### Qualified Name

CollectionFolder::DataFieldNaming:Person:Modifiers

### Purpose

Modifiers specific to the Person subject area, used to qualify a prime word or class word when building data field names.

### Parent ID

CollectionFolder::DataFieldNaming:Person

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Class Words

### Qualified Name

CollectionFolder::DataFieldNaming:Person:ClassWords

### Purpose

Class words specific to the Person subject area, used as the trailing element of a data field name.

### Parent ID

CollectionFolder::DataFieldNaming:Person

### Parent Relationship Type Name

CollectionMembership

___

# Person

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Person

### Aliases

- Individual
- Party

### Glossary Name

- Glossary::DataFieldNaming

### Summary

An individual known to Coco Pharmaceuticals in any capacity.

### Folders

CollectionFolder::DataFieldNaming:Person:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Person

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Birth

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Birth

### Aliases

- Born
- DOB
- Date of Birth

### Glossary Name

- Glossary::DataFieldNaming

### Summary

Relating to the date or place an individual was born, e.g. `PersonBirthDate`.

### Folders

CollectionFolder::DataFieldNaming:Person:Modifiers

### Qualified Name

GlossaryTerm::DataFieldNaming::Birth

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___
