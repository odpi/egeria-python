This file creates the **Product Development** subject area folder (`ProductDevelopment`) and its
Prime Words / Modifiers / Class Words sub-folders in the Data Field Naming glossary, along with any terms
specific to this subject area. It also links the folder as a member of the existing `SubjectArea::ProductDevelopment`
governance collection (see `CocoSubjectAreaDefinition.java`), so the two structures are connected.

Requires `glossary.md` to have been processed
first, and requires the `SubjectArea::ProductDevelopment` collection to already exist in Egeria.

____

## Create Collection Folder

### Display Name

Product Development

### Qualified Name

CollectionFolder::DataFieldNaming:ProductDevelopment

### Purpose

Groups the data field naming terms (prime words, modifiers, class words) for the Product Development subject area. Information relating to the Coco Pharmaceuticals treatment development initiatives.

### Parent ID

Glossary::DataFieldNaming

### Parent Relationship Type Name

CollectionMembership

___

## Add Member to Collection
> Add/Remove a member to/from a collection.

### Element Id

CollectionFolder::DataFieldNaming:ProductDevelopment

### Membership Rationale

Link the Product Development subject area to its data field naming vocabulary.

### Membership Status

VALIDATED

### Collection Id

SubjectArea::ProductDevelopment

___

## Create Collection Folder

### Display Name

Prime Words

### Qualified Name

CollectionFolder::DataFieldNaming:ProductDevelopment:PrimeWords

### Purpose

Prime words - the core business nouns - used to build data field names for the Product Development subject area.

### Parent ID

CollectionFolder::DataFieldNaming:ProductDevelopment

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Modifiers

### Qualified Name

CollectionFolder::DataFieldNaming:ProductDevelopment:Modifiers

### Purpose

Modifiers specific to the Product Development subject area, used to qualify a prime word or class word when building data field names.

### Parent ID

CollectionFolder::DataFieldNaming:ProductDevelopment

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Class Words

### Qualified Name

CollectionFolder::DataFieldNaming:ProductDevelopment:ClassWords

### Purpose

Class words specific to the Product Development subject area, used as the trailing element of a data field name.

### Parent ID

CollectionFolder::DataFieldNaming:ProductDevelopment

### Parent Relationship Type Name

CollectionMembership

___

# Candidate

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Candidate

### Aliases

- Drug Candidate
- Lead Compound

### Glossary Name

- Glossary::DataFieldNaming

### Summary

A product formulation under evaluation during development, before it is approved.

### Folders

CollectionFolder::DataFieldNaming:ProductDevelopment:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Candidate

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Formulation

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Formulation

### Aliases

- Composition
- Mix
- Formula

### Glossary Name

- Glossary::DataFieldNaming

### Summary

A specific composition of ingredients being developed into a product.

### Folders

CollectionFolder::DataFieldNaming:ProductDevelopment:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Formulation

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___
