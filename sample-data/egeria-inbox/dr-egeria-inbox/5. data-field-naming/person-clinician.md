This file creates the **Clinician** subject area folder (`Person:Clinician`) and its
Prime Words / Modifiers / Class Words sub-folders in the Data Field Naming glossary, along with any terms
specific to this subject area. It also links the folder as a member of the existing `SubjectArea::Person:Clinician`
governance collection (see `CocoSubjectAreaDefinition.java`), so the two structures are connected.

Requires `glossary.md` and `person.md` to have been processed
first, and requires the `SubjectArea::Person:Clinician` collection to already exist in Egeria.

____

## Create Collection Folder

### Display Name

Clinician

### Qualified Name

CollectionFolder::DataFieldNaming:Person:Clinician

### Purpose

Groups the data field naming terms (prime words, modifiers, class words) for the Clinician subject area. Information relating to an individual who works with patients.

### Parent ID

CollectionFolder::DataFieldNaming:Person

### Parent Relationship Type Name

CollectionMembership

___

## Add Member to Collection
> Add/Remove a member to/from a collection.

### Element Id

CollectionFolder::DataFieldNaming:Person:Clinician

### Membership Rationale

Link the Clinician subject area to its data field naming vocabulary.

### Membership Status

VALIDATED

### Collection Id

SubjectArea::Person:Clinician

___

## Create Collection Folder

### Display Name

Prime Words

### Qualified Name

CollectionFolder::DataFieldNaming:Person:Clinician:PrimeWords

### Purpose

Prime words - the core business nouns - used to build data field names for the Clinician subject area.

### Parent ID

CollectionFolder::DataFieldNaming:Person:Clinician

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Modifiers

### Qualified Name

CollectionFolder::DataFieldNaming:Person:Clinician:Modifiers

### Purpose

Modifiers specific to the Clinician subject area, used to qualify a prime word or class word when building data field names.

### Parent ID

CollectionFolder::DataFieldNaming:Person:Clinician

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Class Words

### Qualified Name

CollectionFolder::DataFieldNaming:Person:Clinician:ClassWords

### Purpose

Class words specific to the Clinician subject area, used as the trailing element of a data field name.

### Parent ID

CollectionFolder::DataFieldNaming:Person:Clinician

### Parent Relationship Type Name

CollectionMembership

___

# Clinician

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Clinician

### Aliases

- Doctor
- Physician
- Practitioner
- Provider

### Glossary Name

- Glossary::DataFieldNaming

### Summary

An individual who provides direct clinical care to patients, such as a doctor or nurse.

### Folders

CollectionFolder::DataFieldNaming:Person:Clinician:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Clinician

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Specialism

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Specialism

### Abbreviation

SPEC

### Aliases

- Specialty
- Field of Practice

### Glossary Name

- Glossary::DataFieldNaming

### Summary

The medical field in which a clinician is qualified to practice.

### Folders

CollectionFolder::DataFieldNaming:Person:Clinician:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Specialism

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Attending

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Attending

### Abbreviation

ATT

### Aliases

- Attending Physician
- Lead Clinician

### Glossary Name

- Glossary::DataFieldNaming

### Summary

Relating to the clinician with primary responsibility for a patient's care, e.g. `AttendingClinicianName`.

### Folders

CollectionFolder::DataFieldNaming:Person:Clinician:Modifiers

### Qualified Name

GlossaryTerm::DataFieldNaming::Attending

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Referring

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Referring

### Abbreviation

REF

### Aliases

- Referrer

### Glossary Name

- Glossary::DataFieldNaming

### Summary

Relating to the clinician who refers a patient for further care, e.g. `ReferringClinicianIdentifier`.

### Folders

CollectionFolder::DataFieldNaming:Person:Clinician:Modifiers

### Qualified Name

GlossaryTerm::DataFieldNaming::Referring

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___
