This file creates the **Clinical Trial** subject area folder (`ProductDevelopment:ClinicalTrial`) and its
Prime Words / Modifiers / Class Words sub-folders in the Data Field Naming glossary, along with any terms
specific to this subject area. It also links the folder as a member of the existing `SubjectArea::ProductDevelopment:ClinicalTrial`
governance collection (see `CocoSubjectAreaDefinition.java`), so the two structures are connected.

Requires `glossary.md` and `product-development.md` to have been processed
first, and requires the `SubjectArea::ProductDevelopment:ClinicalTrial` collection to already exist in Egeria.

____

## Create Collection Folder

### Display Name

Clinical Trial

### Qualified Name

CollectionFolder::DataFieldNaming:ProductDevelopment:ClinicalTrial

### Purpose

Groups the data field naming terms (prime words, modifiers, class words) for the Clinical Trial subject area. Information relating to the clinical trials run to support Coco Pharmaceuticals product development initiatives.

### Parent ID

CollectionFolder::DataFieldNaming:ProductDevelopment

### Parent Relationship Type Name

CollectionMembership

___

## Add Member to Collection
> Add/Remove a member to/from a collection.

### Element Id

CollectionFolder::DataFieldNaming:ProductDevelopment:ClinicalTrial

### Membership Rationale

Link the Clinical Trial subject area to its data field naming vocabulary.

### Membership Status

VALIDATED

### Collection Id

SubjectArea::ProductDevelopment:ClinicalTrial

___

## Create Collection Folder

### Display Name

Prime Words

### Qualified Name

CollectionFolder::DataFieldNaming:ProductDevelopment:ClinicalTrial:PrimeWords

### Purpose

Prime words - the core business nouns - used to build data field names for the Clinical Trial subject area.

### Parent ID

CollectionFolder::DataFieldNaming:ProductDevelopment:ClinicalTrial

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Modifiers

### Qualified Name

CollectionFolder::DataFieldNaming:ProductDevelopment:ClinicalTrial:Modifiers

### Purpose

Modifiers specific to the Clinical Trial subject area, used to qualify a prime word or class word when building data field names.

### Parent ID

CollectionFolder::DataFieldNaming:ProductDevelopment:ClinicalTrial

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Class Words

### Qualified Name

CollectionFolder::DataFieldNaming:ProductDevelopment:ClinicalTrial:ClassWords

### Purpose

Class words specific to the Clinical Trial subject area, used as the trailing element of a data field name.

### Parent ID

CollectionFolder::DataFieldNaming:ProductDevelopment:ClinicalTrial

### Parent Relationship Type Name

CollectionMembership

___

# ClinicalTrial

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

ClinicalTrial

### Aliases

- Trial
- Study

### Glossary Name

- Glossary::DataFieldNaming

### Summary

A research study that evaluates a product candidate's safety and effectiveness in human participants.

### Folders

CollectionFolder::DataFieldNaming:ProductDevelopment:ClinicalTrial:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::ClinicalTrial

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Participant

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Participant

### Aliases

- Subject
- Volunteer

### Glossary Name

- Glossary::DataFieldNaming

### Summary

An individual who takes part in a clinical trial.

### Folders

CollectionFolder::DataFieldNaming:ProductDevelopment:ClinicalTrial:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Participant

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Protocol

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Protocol

### Aliases

- Study Plan
- Trial Protocol

### Glossary Name

- Glossary::DataFieldNaming

### Summary

The plan that defines how a clinical trial is conducted.

### Folders

CollectionFolder::DataFieldNaming:ProductDevelopment:ClinicalTrial:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Protocol

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Enrollment

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Enrollment

### Aliases

- Enrolment
- Recruitment

### Glossary Name

- Glossary::DataFieldNaming

### Summary

Relating to the point at which a participant joins a clinical trial, e.g. `ParticipantEnrollmentDate`.

### Folders

CollectionFolder::DataFieldNaming:ProductDevelopment:ClinicalTrial:Modifiers

### Qualified Name

GlossaryTerm::DataFieldNaming::Enrollment

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Phase

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Phase

### Aliases

- Stage

### Glossary Name

- Glossary::DataFieldNaming

### Summary

The stage of development a clinical trial represents, e.g. `ClinicalTrialPhase`.

### Folders

CollectionFolder::DataFieldNaming:ProductDevelopment:ClinicalTrial:ClassWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Phase

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___
