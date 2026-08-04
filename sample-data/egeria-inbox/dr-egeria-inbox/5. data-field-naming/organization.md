This file creates the **Organization** subject area folder (`Organization`) and its
Prime Words / Modifiers / Class Words sub-folders in the Data Field Naming glossary, along with any terms
specific to this subject area. It also links the folder as a member of the existing `SubjectArea::Organization`
governance collection (see `CocoSubjectAreaDefinition.java`), so the two structures are connected.

Requires `glossary.md` to have been processed
first, and requires the `SubjectArea::Organization` collection to already exist in Egeria.

____

## Create Collection Folder

### Display Name

Organization

### Qualified Name

CollectionFolder::DataFieldNaming:Organization

### Purpose

Groups the data field naming terms (prime words, modifiers, class words) for the Organization subject area. Information relating to an organization.

### Parent ID

Glossary::DataFieldNaming

### Parent Relationship Type Name

CollectionMembership

___

## Add Member to Collection
> Add/Remove a member to/from a collection.

### Element Id

CollectionFolder::DataFieldNaming:Organization

### Membership Rationale

Link the Organization subject area to its data field naming vocabulary.

### Membership Status

VALIDATED

### Collection Id

SubjectArea::Organization

___

## Create Collection Folder

### Display Name

Prime Words

### Qualified Name

CollectionFolder::DataFieldNaming:Organization:PrimeWords

### Purpose

Prime words - the core business nouns - used to build data field names for the Organization subject area.

### Parent ID

CollectionFolder::DataFieldNaming:Organization

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Modifiers

### Qualified Name

CollectionFolder::DataFieldNaming:Organization:Modifiers

### Purpose

Modifiers specific to the Organization subject area, used to qualify a prime word or class word when building data field names.

### Parent ID

CollectionFolder::DataFieldNaming:Organization

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Class Words

### Qualified Name

CollectionFolder::DataFieldNaming:Organization:ClassWords

### Purpose

Class words specific to the Organization subject area, used as the trailing element of a data field name.

### Parent ID

CollectionFolder::DataFieldNaming:Organization

### Parent Relationship Type Name

CollectionMembership

___

# Organization

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Organization

### Abbreviation

ORG

### Aliases

- Company
- Institution
- Entity

### Glossary Name

- Glossary::DataFieldNaming

### Summary

A company, institution or other structured body that Coco Pharmaceuticals interacts with or is part of.

### Folders

CollectionFolder::DataFieldNaming:Organization:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Organization

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Department

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Department

### Abbreviation

DEPT

### Aliases

- Division
- Unit

### Glossary Name

- Glossary::DataFieldNaming

### Summary

An organizational sub-division responsible for a specific function.

### Folders

CollectionFolder::DataFieldNaming:Organization:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Department

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Site

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Site

### Aliases

- Facility
- Premises

### Glossary Name

- Glossary::DataFieldNaming

### Summary

A physical location operated by an organization.

### Folders

CollectionFolder::DataFieldNaming:Organization:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Site

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Office

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Office

### Aliases

- Branch
- Workplace

### Glossary Name

- Glossary::DataFieldNaming

### Summary

A physical workplace location operated by an organization.

### Folders

CollectionFolder::DataFieldNaming:Organization:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Office

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___
