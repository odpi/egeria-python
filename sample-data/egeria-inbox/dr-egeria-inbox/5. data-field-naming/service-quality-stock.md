This file creates the **Stock** subject area folder (`ServiceQuality:Stock`) and its
Prime Words / Modifiers / Class Words sub-folders in the Data Field Naming glossary, along with any terms
specific to this subject area. It also links the folder as a member of the existing `SubjectArea::ServiceQuality:Stock`
governance collection (see `CocoSubjectAreaDefinition.java`), so the two structures are connected.

Requires `glossary.md` and `service-quality.md` to have been processed
first, and requires the `SubjectArea::ServiceQuality:Stock` collection to already exist in Egeria.

____

## Create Collection Folder

### Display Name

Stock

### Qualified Name

CollectionFolder::DataFieldNaming:ServiceQuality:Stock

### Purpose

Groups the data field naming terms (prime words, modifiers, class words) for the Stock subject area. Information relating to the Coco Pharmaceuticals stock management and control.

### Parent ID

CollectionFolder::DataFieldNaming:ServiceQuality

### Parent Relationship Type Name

CollectionMembership

___

## Add Member to Collection
> Add/Remove a member to/from a collection.

### Element Id

CollectionFolder::DataFieldNaming:ServiceQuality:Stock

### Membership Rationale

Link the Stock subject area to its data field naming vocabulary.

### Membership Status

VALIDATED

### Collection Id

SubjectArea::ServiceQuality:Stock

___

## Create Collection Folder

### Display Name

Prime Words

### Qualified Name

CollectionFolder::DataFieldNaming:ServiceQuality:Stock:PrimeWords

### Purpose

Prime words - the core business nouns - used to build data field names for the Stock subject area.

### Parent ID

CollectionFolder::DataFieldNaming:ServiceQuality:Stock

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Modifiers

### Qualified Name

CollectionFolder::DataFieldNaming:ServiceQuality:Stock:Modifiers

### Purpose

Modifiers specific to the Stock subject area, used to qualify a prime word or class word when building data field names.

### Parent ID

CollectionFolder::DataFieldNaming:ServiceQuality:Stock

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Class Words

### Qualified Name

CollectionFolder::DataFieldNaming:ServiceQuality:Stock:ClassWords

### Purpose

Class words specific to the Stock subject area, used as the trailing element of a data field name.

### Parent ID

CollectionFolder::DataFieldNaming:ServiceQuality:Stock

### Parent Relationship Type Name

CollectionMembership

___

# Stock

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Stock

### Aliases

- Inventory

### Glossary Name

- Glossary::DataFieldNaming

### Summary

The quantity of a product held in inventory at a location.

### Folders

CollectionFolder::DataFieldNaming:ServiceQuality:Stock:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Stock

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Warehouse

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Warehouse

### Abbreviation

WH

### Aliases

- Depot
- Distribution Center

### Glossary Name

- Glossary::DataFieldNaming

### Summary

A facility used to store stock.

### Folders

CollectionFolder::DataFieldNaming:ServiceQuality:Stock:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Warehouse

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Level

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Level

### Aliases

- On-Hand Quantity
- Inventory Level

### Glossary Name

- Glossary::DataFieldNaming

### Summary

The quantity of stock currently held, e.g. `StockLevel`.

### Folders

CollectionFolder::DataFieldNaming:ServiceQuality:Stock:ClassWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Level

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___
