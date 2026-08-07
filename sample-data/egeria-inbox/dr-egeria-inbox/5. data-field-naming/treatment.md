This file creates the **Treatment** subject area folder (`Treatment`) and its
Prime Words / Modifiers / Class Words sub-folders in the Data Field Naming glossary, along with any terms
specific to this subject area. It also links the folder as a member of the existing `SubjectArea::Treatment`
governance collection (see `CocoSubjectAreaDefinition.java`), so the two structures are connected.

Requires `glossary.md` to have been processed
first, and requires the `SubjectArea::Treatment` collection to already exist in Egeria.

____

## Create Collection Folder

### Display Name

Treatment

### Qualified Name

CollectionFolder::DataFieldNaming:Treatment

### Purpose

Groups the data field naming terms (prime words, modifiers, class words) for the Treatment subject area. Information relating to the Coco Pharmaceutical products and practices around patient care.

### Parent ID

Glossary::DataFieldNaming

### Parent Relationship Type Name

CollectionMembership

___

## Add Member to Collection
> Add/Remove a member to/from a collection.

### Element Id

CollectionFolder::DataFieldNaming:Treatment

### Membership Rationale

Link the Treatment subject area to its data field naming vocabulary.

### Membership Status

VALIDATED

### Collection Id

SubjectArea::Treatment

___

## Create Collection Folder

### Display Name

Prime Words

### Qualified Name

CollectionFolder::DataFieldNaming:Treatment:PrimeWords

### Purpose

Prime words - the core business nouns - used to build data field names for the Treatment subject area.

### Parent ID

CollectionFolder::DataFieldNaming:Treatment

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Modifiers

### Qualified Name

CollectionFolder::DataFieldNaming:Treatment:Modifiers

### Purpose

Modifiers specific to the Treatment subject area, used to qualify a prime word or class word when building data field names.

### Parent ID

CollectionFolder::DataFieldNaming:Treatment

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Class Words

### Qualified Name

CollectionFolder::DataFieldNaming:Treatment:ClassWords

### Purpose

Class words specific to the Treatment subject area, used as the trailing element of a data field name.

### Parent ID

CollectionFolder::DataFieldNaming:Treatment

### Parent Relationship Type Name

CollectionMembership

___

# Treatment

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Treatment

### Abbreviation

TX

### Aliases

- Care
- Therapy

### Glossary Name

- Glossary::DataFieldNaming

### Summary

A course of care given to a patient using Coco Pharmaceutical products and practices.

### Folders

CollectionFolder::DataFieldNaming:Treatment:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Treatment

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___
