This file creates the **Order** subject area folder (`Treatment:Order`) and its
Prime Words / Modifiers / Class Words sub-folders in the Data Field Naming glossary, along with any terms
specific to this subject area. It also links the folder as a member of the existing `SubjectArea::Treatment:Order`
governance collection (see `CocoSubjectAreaDefinition.java`), so the two structures are connected.

Requires `glossary.md` and `treatment.md` to have been processed
first, and requires the `SubjectArea::Treatment:Order` collection to already exist in Egeria.

____

## Create Collection Folder

### Display Name

Order

### Qualified Name

CollectionFolder::DataFieldNaming:Treatment:Order

### Purpose

Groups the data field naming terms (prime words, modifiers, class words) for the Order subject area. Information relating to orders for Coco Pharmaceutical products.

### Parent ID

CollectionFolder::DataFieldNaming:Treatment

### Parent Relationship Type Name

CollectionMembership

___

## Add Member to Collection
> Add/Remove a member to/from a collection.

### Element Id

CollectionFolder::DataFieldNaming:Treatment:Order

### Membership Rationale

Link the Order subject area to its data field naming vocabulary.

### Membership Status

VALIDATED

### Collection Id

SubjectArea::Treatment:Order

___

## Create Collection Folder

### Display Name

Prime Words

### Qualified Name

CollectionFolder::DataFieldNaming:Treatment:Order:PrimeWords

### Purpose

Prime words - the core business nouns - used to build data field names for the Order subject area.

### Parent ID

CollectionFolder::DataFieldNaming:Treatment:Order

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Modifiers

### Qualified Name

CollectionFolder::DataFieldNaming:Treatment:Order:Modifiers

### Purpose

Modifiers specific to the Order subject area, used to qualify a prime word or class word when building data field names.

### Parent ID

CollectionFolder::DataFieldNaming:Treatment:Order

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Class Words

### Qualified Name

CollectionFolder::DataFieldNaming:Treatment:Order:ClassWords

### Purpose

Class words specific to the Order subject area, used as the trailing element of a data field name.

### Parent ID

CollectionFolder::DataFieldNaming:Treatment:Order

### Parent Relationship Type Name

CollectionMembership

___

# Order

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Order

### Aliases

- Purchase Order
- PO

### Glossary Name

- Glossary::DataFieldNaming

### Summary

A request for a quantity of Coco Pharmaceutical products to be supplied.

### Folders

CollectionFolder::DataFieldNaming:Treatment:Order:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Order

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# LineItem

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

LineItem

### Aliases

- Line Item
- Order Line

### Glossary Name

- Glossary::DataFieldNaming

### Summary

An individual product and quantity requested within an order.

### Folders

CollectionFolder::DataFieldNaming:Treatment:Order:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::LineItem

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Backorder

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Backorder

### Aliases

- Back Order
- Pending Supply

### Glossary Name

- Glossary::DataFieldNaming

### Summary

Relating to a part of an order that cannot currently be fulfilled and is pending future supply, e.g. `BackorderQuantity`.

### Folders

CollectionFolder::DataFieldNaming:Treatment:Order:Modifiers

### Qualified Name

GlossaryTerm::DataFieldNaming::Backorder

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Quantity

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Quantity

### Abbreviation

QTY

### Aliases

- Count
- Amount

### Glossary Name

- Glossary::DataFieldNaming

### Summary

The number of units of a product involved, e.g. `OrderQuantity`.

### Folders

CollectionFolder::DataFieldNaming:Treatment:Order:ClassWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Quantity

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___
