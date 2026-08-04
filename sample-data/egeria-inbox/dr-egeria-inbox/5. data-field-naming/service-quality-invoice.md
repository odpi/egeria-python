This file creates the **Invoice** subject area folder (`ServiceQuality:Invoice`) and its
Prime Words / Modifiers / Class Words sub-folders in the Data Field Naming glossary, along with any terms
specific to this subject area. It also links the folder as a member of the existing `SubjectArea::ServiceQuality:Invoice`
governance collection (see `CocoSubjectAreaDefinition.java`), so the two structures are connected.

Requires `glossary.md` and `service-quality.md` to have been processed
first, and requires the `SubjectArea::ServiceQuality:Invoice` collection to already exist in Egeria.

____

## Create Collection Folder

### Display Name

Invoice

### Qualified Name

CollectionFolder::DataFieldNaming:ServiceQuality:Invoice

### Purpose

Groups the data field naming terms (prime words, modifiers, class words) for the Invoice subject area. Information relating to the Coco Pharmaceuticals billing and payments.

### Parent ID

CollectionFolder::DataFieldNaming:ServiceQuality

### Parent Relationship Type Name

CollectionMembership

___

## Add Member to Collection
> Add/Remove a member to/from a collection.

### Element Id

CollectionFolder::DataFieldNaming:ServiceQuality:Invoice

### Membership Rationale

Link the Invoice subject area to its data field naming vocabulary.

### Membership Status

VALIDATED

### Collection Id

SubjectArea::ServiceQuality:Invoice

___

## Create Collection Folder

### Display Name

Prime Words

### Qualified Name

CollectionFolder::DataFieldNaming:ServiceQuality:Invoice:PrimeWords

### Purpose

Prime words - the core business nouns - used to build data field names for the Invoice subject area.

### Parent ID

CollectionFolder::DataFieldNaming:ServiceQuality:Invoice

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Modifiers

### Qualified Name

CollectionFolder::DataFieldNaming:ServiceQuality:Invoice:Modifiers

### Purpose

Modifiers specific to the Invoice subject area, used to qualify a prime word or class word when building data field names.

### Parent ID

CollectionFolder::DataFieldNaming:ServiceQuality:Invoice

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Class Words

### Qualified Name

CollectionFolder::DataFieldNaming:ServiceQuality:Invoice:ClassWords

### Purpose

Class words specific to the Invoice subject area, used as the trailing element of a data field name.

### Parent ID

CollectionFolder::DataFieldNaming:ServiceQuality:Invoice

### Parent Relationship Type Name

CollectionMembership

___

# Invoice

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Invoice

### Abbreviation

INV

### Aliases

- Bill

### Glossary Name

- Glossary::DataFieldNaming

### Summary

A statement of the amount owed by a customer for products or services supplied.

### Folders

CollectionFolder::DataFieldNaming:ServiceQuality:Invoice:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Invoice

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Payment

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Payment

### Aliases

- Remittance
- Settlement

### Glossary Name

- Glossary::DataFieldNaming

### Summary

A transfer of funds made to settle an invoice.

### Folders

CollectionFolder::DataFieldNaming:ServiceQuality:Invoice:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Payment

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Overdue

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Overdue

### Aliases

- Past Due
- Late

### Glossary Name

- Glossary::DataFieldNaming

### Summary

Relating to an invoice that has not been paid by its due date, e.g. `InvoiceOverdueAmount`.

### Folders

CollectionFolder::DataFieldNaming:ServiceQuality:Invoice:Modifiers

### Qualified Name

GlossaryTerm::DataFieldNaming::Overdue

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Due

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Due

### Aliases

- Payable

### Glossary Name

- Glossary::DataFieldNaming

### Summary

Relating to the date by which an invoice must be paid, e.g. `InvoiceDueDate`.

### Folders

CollectionFolder::DataFieldNaming:ServiceQuality:Invoice:Modifiers

### Qualified Name

GlossaryTerm::DataFieldNaming::Due

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___
