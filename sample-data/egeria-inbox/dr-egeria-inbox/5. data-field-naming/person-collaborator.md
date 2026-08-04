This file creates the **Collaborator** subject area folder (`Person:Collaborator`) and its
Prime Words / Modifiers / Class Words sub-folders in the Data Field Naming glossary, along with any terms
specific to this subject area. It also links the folder as a member of the existing `SubjectArea::Person:Collaborator`
governance collection (see `CocoSubjectAreaDefinition.java`), so the two structures are connected.

Requires `glossary.md` and `person.md` to have been processed
first, and requires the `SubjectArea::Person:Collaborator` collection to already exist in Egeria.

____

## Create Collection Folder

### Display Name

Collaborator

### Qualified Name

CollectionFolder::DataFieldNaming:Person:Collaborator

### Purpose

Groups the data field naming terms (prime words, modifiers, class words) for the Collaborator subject area. Information relating to an individual who works for a business partner.

### Parent ID

CollectionFolder::DataFieldNaming:Person

### Parent Relationship Type Name

CollectionMembership

___

## Add Member to Collection
> Add/Remove a member to/from a collection.

### Element Id

CollectionFolder::DataFieldNaming:Person:Collaborator

### Membership Rationale

Link the Collaborator subject area to its data field naming vocabulary.

### Membership Status

VALIDATED

### Collection Id

SubjectArea::Person:Collaborator

___

## Create Collection Folder

### Display Name

Prime Words

### Qualified Name

CollectionFolder::DataFieldNaming:Person:Collaborator:PrimeWords

### Purpose

Prime words - the core business nouns - used to build data field names for the Collaborator subject area.

### Parent ID

CollectionFolder::DataFieldNaming:Person:Collaborator

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Modifiers

### Qualified Name

CollectionFolder::DataFieldNaming:Person:Collaborator:Modifiers

### Purpose

Modifiers specific to the Collaborator subject area, used to qualify a prime word or class word when building data field names.

### Parent ID

CollectionFolder::DataFieldNaming:Person:Collaborator

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Class Words

### Qualified Name

CollectionFolder::DataFieldNaming:Person:Collaborator:ClassWords

### Purpose

Class words specific to the Collaborator subject area, used as the trailing element of a data field name.

### Parent ID

CollectionFolder::DataFieldNaming:Person:Collaborator

### Parent Relationship Type Name

CollectionMembership

___

# Collaborator

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Collaborator

### Aliases

- Partner Contact
- Associate

### Glossary Name

- Glossary::DataFieldNaming

### Summary

An individual who works for a business partner and interacts with Coco Pharmaceuticals.

### Folders

CollectionFolder::DataFieldNaming:Person:Collaborator:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Collaborator

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Visiting

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Visiting

### Aliases

- Guest
- Temporary Visitor

### Glossary Name

- Glossary::DataFieldNaming

### Summary

Relating to a collaborator who is temporarily present at a Coco Pharmaceuticals site, e.g. `VisitingCollaboratorBadge`.

### Folders

CollectionFolder::DataFieldNaming:Person:Collaborator:Modifiers

### Qualified Name

GlossaryTerm::DataFieldNaming::Visiting

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___
