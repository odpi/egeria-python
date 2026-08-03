This file creates the **Patient** subject area folder (`Person:Patient`) and its
Prime Words / Modifiers / Class Words sub-folders in the Data Field Naming glossary, along with any terms
specific to this subject area. It also links the folder as a member of the existing `SubjectArea::Person:Patient`
governance collection (see `CocoSubjectAreaDefinition.java`), so the two structures are connected.

Requires `glossary.md` and `person.md` to have been processed
first, and requires the `SubjectArea::Person:Patient` collection to already exist in Egeria.

____

## Create Collection Folder

### Display Name

Patient

### Qualified Name

CollectionFolder::DataFieldNaming:Person:Patient

### Purpose

Groups the data field naming terms (prime words, modifiers, class words) for the Patient subject area. Information relating to an individual patient.

### Parent ID

CollectionFolder::DataFieldNaming:Person

### Parent Relationship Type Name

CollectionMembership

___

## Add Member to Collection
> Add/Remove a member to/from a collection.

### Element Id

CollectionFolder::DataFieldNaming:Person:Patient

### Membership Rationale

Link the Patient subject area to its data field naming vocabulary.

### Membership Status

VALIDATED

### Collection Id

SubjectArea::Person:Patient

___

## Create Collection Folder

### Display Name

Prime Words

### Qualified Name

CollectionFolder::DataFieldNaming:Person:Patient:PrimeWords

### Purpose

Prime words - the core business nouns - used to build data field names for the Patient subject area.

### Parent ID

CollectionFolder::DataFieldNaming:Person:Patient

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Modifiers

### Qualified Name

CollectionFolder::DataFieldNaming:Person:Patient:Modifiers

### Purpose

Modifiers specific to the Patient subject area, used to qualify a prime word or class word when building data field names.

### Parent ID

CollectionFolder::DataFieldNaming:Person:Patient

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Class Words

### Qualified Name

CollectionFolder::DataFieldNaming:Person:Patient:ClassWords

### Purpose

Class words specific to the Patient subject area, used as the trailing element of a data field name.

### Parent ID

CollectionFolder::DataFieldNaming:Person:Patient

### Parent Relationship Type Name

CollectionMembership

___

# Patient

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Patient

### Abbreviation

PT

### Aliases

- Client
- Case

### Glossary Name

- Glossary::DataFieldNaming

### Summary

An individual who is receiving, or is registered to receive, medical care from Coco Pharmaceuticals or a partner organization.

### Folders

CollectionFolder::DataFieldNaming:Person:Patient:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Patient

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# NextOfKin

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

NextOfKin

### Abbreviation

NOK

### Aliases

- Emergency Contact
- Kin

### Glossary Name

- Glossary::DataFieldNaming

### Summary

The person nominated by a patient as their closest relative or contact in an emergency.

### Folders

CollectionFolder::DataFieldNaming:Person:Patient:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::NextOfKin

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Guardian

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Guardian

### Aliases

- Legal Guardian
- Carer

### Glossary Name

- Glossary::DataFieldNaming

### Summary

A person with legal responsibility for a patient who is not able to make decisions for themselves.

### Folders

CollectionFolder::DataFieldNaming:Person:Patient:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Guardian

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Admitting

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Admitting

### Abbreviation

ADM

### Aliases

- Admission
- Intake

### Glossary Name

- Glossary::DataFieldNaming

### Summary

Relating to the point at which a patient is admitted for care, e.g. `PatientAdmittingDate`.

### Folders

CollectionFolder::DataFieldNaming:Person:Patient:Modifiers

### Qualified Name

GlossaryTerm::DataFieldNaming::Admitting

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Discharge

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Discharge

### Abbreviation

DISCH

### Aliases

- Release

### Glossary Name

- Glossary::DataFieldNaming

### Summary

Relating to the point at which a patient's episode of care ends and they leave, e.g. `PatientDischargeDate`.

### Folders

CollectionFolder::DataFieldNaming:Person:Patient:Modifiers

### Qualified Name

GlossaryTerm::DataFieldNaming::Discharge

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Registered

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Registered

### Abbreviation

REG

### Aliases

- Enrolled
- Registration

### Glossary Name

- Glossary::DataFieldNaming

### Summary

Relating to the point at which a patient enrolls with an organization, e.g. `PatientRegisteredDate`.

### Folders

CollectionFolder::DataFieldNaming:Person:Patient:Modifiers

### Qualified Name

GlossaryTerm::DataFieldNaming::Registered

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___
