This file creates the **Supplier** subject area folder (`Organization:Supplier`) and its
Prime Words / Modifiers / Class Words sub-folders in the Data Field Naming glossary, along with any terms
specific to this subject area. It also links the folder as a member of the existing `SubjectArea::Organization:Supplier`
governance collection (see `CocoSubjectAreaDefinition.java`), so the two structures are connected.

Requires `glossary.md` and `organization.md` to have been processed
first, and requires the `SubjectArea::Organization:Supplier` collection to already exist in Egeria.

____

## Create Collection Folder

### Display Name

Supplier

### Qualified Name

CollectionFolder::DataFieldNaming:Organization:Supplier

### Purpose

Groups the data field naming terms (prime words, modifiers, class words) for the Supplier subject area. Information relating to a supplier's organization.

### Parent ID

CollectionFolder::DataFieldNaming:Organization

### Parent Relationship Type Name

CollectionMembership

___

## Add Member to Collection
> Add/Remove a member to/from a collection.

### Element Id

CollectionFolder::DataFieldNaming:Organization:Supplier

### Membership Rationale

Link the Supplier subject area to its data field naming vocabulary.

### Membership Status

VALIDATED

### Collection Id

SubjectArea::Organization:Supplier

___

## Create Collection Folder

### Display Name

Prime Words

### Qualified Name

CollectionFolder::DataFieldNaming:Organization:Supplier:PrimeWords

### Purpose

Prime words - the core business nouns - used to build data field names for the Supplier subject area.

### Parent ID

CollectionFolder::DataFieldNaming:Organization:Supplier

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Modifiers

### Qualified Name

CollectionFolder::DataFieldNaming:Organization:Supplier:Modifiers

### Purpose

Modifiers specific to the Supplier subject area, used to qualify a prime word or class word when building data field names.

### Parent ID

CollectionFolder::DataFieldNaming:Organization:Supplier

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Class Words

### Qualified Name

CollectionFolder::DataFieldNaming:Organization:Supplier:ClassWords

### Purpose

Class words specific to the Supplier subject area, used as the trailing element of a data field name.

### Parent ID

CollectionFolder::DataFieldNaming:Organization:Supplier

### Parent Relationship Type Name

CollectionMembership

___

# Supplier

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Supplier

### Aliases

- Vendor
- Provider

### Glossary Name

- Glossary::DataFieldNaming

### Summary

An organization that provides goods or services to Coco Pharmaceuticals.

### Folders

CollectionFolder::DataFieldNaming:Organization:Supplier:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Supplier

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# RawMaterial

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

RawMaterial

### Aliases

- Raw Material
- Material
- Feedstock

### Glossary Name

- Glossary::DataFieldNaming

### Summary

A material sourced from a supplier for use in manufacturing.

### Folders

CollectionFolder::DataFieldNaming:Organization:Supplier:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::RawMaterial

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Preferred

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Preferred

### Aliases

- Priority

### Glossary Name

- Glossary::DataFieldNaming

### Summary

Relating to a supplier selected as the primary source for a given material or service, e.g. `PreferredSupplierStatus`.

### Folders

CollectionFolder::DataFieldNaming:Organization:Supplier:Modifiers

### Qualified Name

GlossaryTerm::DataFieldNaming::Preferred

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Approved

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Approved

### Abbreviation

APPR

### Aliases

- Qualified
- Certified

### Glossary Name

- Glossary::DataFieldNaming

### Summary

Relating to a supplier that has passed Coco Pharmaceuticals' qualification process, e.g. `ApprovedSupplierList`.

### Folders

CollectionFolder::DataFieldNaming:Organization:Supplier:Modifiers

### Qualified Name

GlossaryTerm::DataFieldNaming::Approved

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Rating

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Rating

### Aliases

- Score
- Ranking
- Grade

### Glossary Name

- Glossary::DataFieldNaming

### Summary

A score reflecting the assessed performance or quality of an entity, e.g. `SupplierRating`.

### Folders

CollectionFolder::DataFieldNaming:Organization:Supplier:ClassWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Rating

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___
