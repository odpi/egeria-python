This file creates the **Recipe** subject area folder (`Treatment:Recipe`) and its
Prime Words / Modifiers / Class Words sub-folders in the Data Field Naming glossary, along with any terms
specific to this subject area. It also links the folder as a member of the existing `SubjectArea::Treatment:Recipe`
governance collection (see `CocoSubjectAreaDefinition.java`), so the two structures are connected.

Requires `glossary.md` and `treatment.md` to have been processed
first, and requires the `SubjectArea::Treatment:Recipe` collection to already exist in Egeria.

____

## Create Collection Folder

### Display Name

Recipe

### Qualified Name

CollectionFolder::DataFieldNaming:Treatment:Recipe

### Purpose

Groups the data field naming terms (prime words, modifiers, class words) for the Recipe subject area. Information relating to the ingredients and manufacturing know-how for Coco Pharmaceutical products.

### Parent ID

CollectionFolder::DataFieldNaming:Treatment

### Parent Relationship Type Name

CollectionMembership

___

## Add Member to Collection
> Add/Remove a member to/from a collection.

### Element Id

CollectionFolder::DataFieldNaming:Treatment:Recipe

### Membership Rationale

Link the Recipe subject area to its data field naming vocabulary.

### Membership Status

VALIDATED

### Collection Id

SubjectArea::Treatment:Recipe

___

## Create Collection Folder

### Display Name

Prime Words

### Qualified Name

CollectionFolder::DataFieldNaming:Treatment:Recipe:PrimeWords

### Purpose

Prime words - the core business nouns - used to build data field names for the Recipe subject area.

### Parent ID

CollectionFolder::DataFieldNaming:Treatment:Recipe

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Modifiers

### Qualified Name

CollectionFolder::DataFieldNaming:Treatment:Recipe:Modifiers

### Purpose

Modifiers specific to the Recipe subject area, used to qualify a prime word or class word when building data field names.

### Parent ID

CollectionFolder::DataFieldNaming:Treatment:Recipe

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Class Words

### Qualified Name

CollectionFolder::DataFieldNaming:Treatment:Recipe:ClassWords

### Purpose

Class words specific to the Recipe subject area, used as the trailing element of a data field name.

### Parent ID

CollectionFolder::DataFieldNaming:Treatment:Recipe

### Parent Relationship Type Name

CollectionMembership

___

# Recipe

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Recipe

### Aliases

- Formula
- Bill of Materials
- BOM

### Glossary Name

- Glossary::DataFieldNaming

### Summary

The ingredients and manufacturing method used to produce a Coco Pharmaceutical product.

### Folders

CollectionFolder::DataFieldNaming:Treatment:Recipe:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Recipe

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Ingredient

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Ingredient

### Aliases

- Component
- Constituent

### Glossary Name

- Glossary::DataFieldNaming

### Summary

A substance used in the manufacture of a product.

### Folders

CollectionFolder::DataFieldNaming:Treatment:Recipe:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Ingredient

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Manufacturing

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Manufacturing

### Abbreviation

MFG

### Aliases

- Production

### Glossary Name

- Glossary::DataFieldNaming

### Summary

Relating to the process of producing a product from a recipe, e.g. `ManufacturingMethodDescription`.

### Folders

CollectionFolder::DataFieldNaming:Treatment:Recipe:Modifiers

### Qualified Name

GlossaryTerm::DataFieldNaming::Manufacturing

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Proportion

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Proportion

### Aliases

- Ratio
- Percentage

### Glossary Name

- Glossary::DataFieldNaming

### Summary

The relative amount of an ingredient within a recipe, e.g. `IngredientProportion`.

### Folders

CollectionFolder::DataFieldNaming:Treatment:Recipe:ClassWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Proportion

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___
