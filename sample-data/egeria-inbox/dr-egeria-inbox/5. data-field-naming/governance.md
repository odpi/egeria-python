This file creates the **Governance** subject area folder (`Governance`) and its
Prime Words / Modifiers / Class Words sub-folders in the Data Field Naming glossary, along with any terms
specific to this subject area. It also links the folder as a member of the existing `SubjectArea::Governance`
governance collection (see `CocoSubjectAreaDefinition.java`), so the two structures are connected.

Requires `glossary.md` to have been processed
first, and requires the `SubjectArea::Governance` collection to already exist in Egeria.

____

## Create Collection Folder

### Display Name

Governance

### Qualified Name

CollectionFolder::DataFieldNaming:Governance

### Purpose

Groups the data field naming terms (prime words, modifiers, class words) for the Governance subject area. Information relating to the Coco Pharmaceuticals governance initiatives.

### Parent ID

Glossary::DataFieldNaming

### Parent Relationship Type Name

CollectionMembership

___

## Add Member to Collection
> Add/Remove a member to/from a collection.

### Element Id

CollectionFolder::DataFieldNaming:Governance

### Membership Rationale

Link the Governance subject area to its data field naming vocabulary.

### Membership Status

VALIDATED

### Collection Id

SubjectArea::Governance

___

## Create Collection Folder

### Display Name

Prime Words

### Qualified Name

CollectionFolder::DataFieldNaming:Governance:PrimeWords

### Purpose

Prime words - the core business nouns - used to build data field names for the Governance subject area.

### Parent ID

CollectionFolder::DataFieldNaming:Governance

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Modifiers

### Qualified Name

CollectionFolder::DataFieldNaming:Governance:Modifiers

### Purpose

Modifiers specific to the Governance subject area, used to qualify a prime word or class word when building data field names.

### Parent ID

CollectionFolder::DataFieldNaming:Governance

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Class Words

### Qualified Name

CollectionFolder::DataFieldNaming:Governance:ClassWords

### Purpose

Class words specific to the Governance subject area, used as the trailing element of a data field name.

### Parent ID

CollectionFolder::DataFieldNaming:Governance

### Parent Relationship Type Name

CollectionMembership

___

# Policy

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Policy

### Aliases

- Rule
- Guideline

### Glossary Name

- Glossary::DataFieldNaming

### Summary

A statement of intent adopted by Coco Pharmaceuticals to guide decisions.

### Folders

CollectionFolder::DataFieldNaming:Governance:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Policy

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Control

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Control

### Aliases

- Safeguard
- Mitigation

### Glossary Name

- Glossary::DataFieldNaming

### Summary

A mechanism put in place to enforce a policy or manage a risk.

### Folders

CollectionFolder::DataFieldNaming:Governance:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Control

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Risk

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Risk

### Aliases

- Hazard
- Exposure

### Glossary Name

- Glossary::DataFieldNaming

### Summary

A potential event that could have a negative impact on Coco Pharmaceuticals.

### Folders

CollectionFolder::DataFieldNaming:Governance:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Risk

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___
