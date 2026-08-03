This file creates the **Service Quality** subject area folder (`ServiceQuality`) and its
Prime Words / Modifiers / Class Words sub-folders in the Data Field Naming glossary, along with any terms
specific to this subject area. It also links the folder as a member of the existing `SubjectArea::ServiceQuality`
governance collection (see `CocoSubjectAreaDefinition.java`), so the two structures are connected.

Requires `glossary.md` to have been processed
first, and requires the `SubjectArea::ServiceQuality` collection to already exist in Egeria.

____

## Create Collection Folder

### Display Name

Service Quality

### Qualified Name

CollectionFolder::DataFieldNaming:ServiceQuality

### Purpose

Groups the data field naming terms (prime words, modifiers, class words) for the Service Quality subject area. Information relating to the Coco Pharmaceuticals business operations.

### Parent ID

Glossary::DataFieldNaming

### Parent Relationship Type Name

CollectionMembership

___

## Add Member to Collection
> Add/Remove a member to/from a collection.

### Element Id

CollectionFolder::DataFieldNaming:ServiceQuality

### Membership Rationale

Link the Service Quality subject area to its data field naming vocabulary.

### Membership Status

VALIDATED

### Collection Id

SubjectArea::ServiceQuality

___

## Create Collection Folder

### Display Name

Prime Words

### Qualified Name

CollectionFolder::DataFieldNaming:ServiceQuality:PrimeWords

### Purpose

Prime words - the core business nouns - used to build data field names for the Service Quality subject area.

### Parent ID

CollectionFolder::DataFieldNaming:ServiceQuality

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Modifiers

### Qualified Name

CollectionFolder::DataFieldNaming:ServiceQuality:Modifiers

### Purpose

Modifiers specific to the Service Quality subject area, used to qualify a prime word or class word when building data field names.

### Parent ID

CollectionFolder::DataFieldNaming:ServiceQuality

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Class Words

### Qualified Name

CollectionFolder::DataFieldNaming:ServiceQuality:ClassWords

### Purpose

Class words specific to the Service Quality subject area, used as the trailing element of a data field name.

### Parent ID

CollectionFolder::DataFieldNaming:ServiceQuality

### Parent Relationship Type Name

CollectionMembership

___

# Complaint

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Complaint

### Aliases

- Grievance
- Issue

### Glossary Name

- Glossary::DataFieldNaming

### Summary

A concern raised by a customer, patient or partner about the quality of Coco Pharmaceuticals' products or services.

### Folders

CollectionFolder::DataFieldNaming:ServiceQuality:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Complaint

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Customer

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Customer

### Abbreviation

CUST

### Aliases

- Client
- Account
- Buyer

### Glossary Name

- Glossary::DataFieldNaming

### Summary

An individual or organization that purchases Coco Pharmaceuticals' products or services.

### Folders

CollectionFolder::DataFieldNaming:ServiceQuality:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Customer

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___
