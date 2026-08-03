This file creates the **Product** subject area folder (`Treatment:Product`) and its
Prime Words / Modifiers / Class Words sub-folders in the Data Field Naming glossary, along with any terms
specific to this subject area. It also links the folder as a member of the existing `SubjectArea::Treatment:Product`
governance collection (see `CocoSubjectAreaDefinition.java`), so the two structures are connected.

Requires `glossary.md` and `treatment.md` to have been processed
first, and requires the `SubjectArea::Treatment:Product` collection to already exist in Egeria.

____

## Create Collection Folder

### Display Name

Product

### Qualified Name

CollectionFolder::DataFieldNaming:Treatment:Product

### Purpose

Groups the data field naming terms (prime words, modifiers, class words) for the Product subject area. Information relating to the Coco Pharmaceutical products to be used in particular treatments.

### Parent ID

CollectionFolder::DataFieldNaming:Treatment

### Parent Relationship Type Name

CollectionMembership

___

## Add Member to Collection
> Add/Remove a member to/from a collection.

### Element Id

CollectionFolder::DataFieldNaming:Treatment:Product

### Membership Rationale

Link the Product subject area to its data field naming vocabulary.

### Membership Status

VALIDATED

### Collection Id

SubjectArea::Treatment:Product

___

## Create Collection Folder

### Display Name

Prime Words

### Qualified Name

CollectionFolder::DataFieldNaming:Treatment:Product:PrimeWords

### Purpose

Prime words - the core business nouns - used to build data field names for the Product subject area.

### Parent ID

CollectionFolder::DataFieldNaming:Treatment:Product

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Modifiers

### Qualified Name

CollectionFolder::DataFieldNaming:Treatment:Product:Modifiers

### Purpose

Modifiers specific to the Product subject area, used to qualify a prime word or class word when building data field names.

### Parent ID

CollectionFolder::DataFieldNaming:Treatment:Product

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Class Words

### Qualified Name

CollectionFolder::DataFieldNaming:Treatment:Product:ClassWords

### Purpose

Class words specific to the Product subject area, used as the trailing element of a data field name.

### Parent ID

CollectionFolder::DataFieldNaming:Treatment:Product

### Parent Relationship Type Name

CollectionMembership

___

# Product

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Product

### Aliases

- Item
- SKU

### Glossary Name

- Glossary::DataFieldNaming

### Summary

A Coco Pharmaceutical product that can be used in a treatment.

### Folders

CollectionFolder::DataFieldNaming:Treatment:Product:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Product

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Batch

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Batch

### Aliases

- Lot
- Production Run

### Glossary Name

- Glossary::DataFieldNaming

### Summary

A quantity of product manufactured together in a single production run.

### Folders

CollectionFolder::DataFieldNaming:Treatment:Product:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Batch

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# ActiveIngredient

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

ActiveIngredient

### Abbreviation

API

### Aliases

- Active Pharmaceutical Ingredient

### Glossary Name

- Glossary::DataFieldNaming

### Summary

The component of a product responsible for its therapeutic effect.

### Folders

CollectionFolder::DataFieldNaming:Treatment:Product:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::ActiveIngredient

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Expiry

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Expiry

### Abbreviation

EXP

### Aliases

- Expiration

### Glossary Name

- Glossary::DataFieldNaming

### Summary

Relating to the point at which a product is no longer fit for use, e.g. `ProductExpiryDate`.

### Folders

CollectionFolder::DataFieldNaming:Treatment:Product:Modifiers

### Qualified Name

GlossaryTerm::DataFieldNaming::Expiry

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Strength

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Strength

### Aliases

- Potency
- Concentration

### Glossary Name

- Glossary::DataFieldNaming

### Summary

The concentration or potency of a product's active ingredient, e.g. `ProductStrength`.

### Folders

CollectionFolder::DataFieldNaming:Treatment:Product:ClassWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Strength

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___
