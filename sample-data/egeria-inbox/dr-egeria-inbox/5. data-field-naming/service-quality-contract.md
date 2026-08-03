This file creates the **Contract** subject area folder (`ServiceQuality:Contract`) and its
Prime Words / Modifiers / Class Words sub-folders in the Data Field Naming glossary, along with any terms
specific to this subject area. It also links the folder as a member of the existing `SubjectArea::ServiceQuality:Contract`
governance collection (see `CocoSubjectAreaDefinition.java`), so the two structures are connected.

Requires `glossary.md` and `service-quality.md` to have been processed
first, and requires the `SubjectArea::ServiceQuality:Contract` collection to already exist in Egeria.

____

## Create Collection Folder

### Display Name

Contract

### Qualified Name

CollectionFolder::DataFieldNaming:ServiceQuality:Contract

### Purpose

Groups the data field naming terms (prime words, modifiers, class words) for the Contract subject area. Information relating to the Coco Pharmaceuticals contracts.

### Parent ID

CollectionFolder::DataFieldNaming:ServiceQuality

### Parent Relationship Type Name

CollectionMembership

___

## Add Member to Collection
> Add/Remove a member to/from a collection.

### Element Id

CollectionFolder::DataFieldNaming:ServiceQuality:Contract

### Membership Rationale

Link the Contract subject area to its data field naming vocabulary.

### Membership Status

VALIDATED

### Collection Id

SubjectArea::ServiceQuality:Contract

___

## Create Collection Folder

### Display Name

Prime Words

### Qualified Name

CollectionFolder::DataFieldNaming:ServiceQuality:Contract:PrimeWords

### Purpose

Prime words - the core business nouns - used to build data field names for the Contract subject area.

### Parent ID

CollectionFolder::DataFieldNaming:ServiceQuality:Contract

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Modifiers

### Qualified Name

CollectionFolder::DataFieldNaming:ServiceQuality:Contract:Modifiers

### Purpose

Modifiers specific to the Contract subject area, used to qualify a prime word or class word when building data field names.

### Parent ID

CollectionFolder::DataFieldNaming:ServiceQuality:Contract

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Class Words

### Qualified Name

CollectionFolder::DataFieldNaming:ServiceQuality:Contract:ClassWords

### Purpose

Class words specific to the Contract subject area, used as the trailing element of a data field name.

### Parent ID

CollectionFolder::DataFieldNaming:ServiceQuality:Contract

### Parent Relationship Type Name

CollectionMembership

___

# Contract

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Contract

### Aliases

- Agreement

### Glossary Name

- Glossary::DataFieldNaming

### Summary

A formal agreement between Coco Pharmaceuticals and another party.

### Folders

CollectionFolder::DataFieldNaming:ServiceQuality:Contract:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Contract

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Clause

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Clause

### Aliases

- Term
- Provision

### Glossary Name

- Glossary::DataFieldNaming

### Summary

An individual term or condition within a contract.

### Folders

CollectionFolder::DataFieldNaming:ServiceQuality:Contract:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Clause

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Renewal

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Renewal

### Aliases

- Extension
- Rollover

### Glossary Name

- Glossary::DataFieldNaming

### Summary

Relating to a contract being extended beyond its original term, e.g. `ContractRenewalDate`.

### Folders

CollectionFolder::DataFieldNaming:ServiceQuality:Contract:Modifiers

### Qualified Name

GlossaryTerm::DataFieldNaming::Renewal

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___
