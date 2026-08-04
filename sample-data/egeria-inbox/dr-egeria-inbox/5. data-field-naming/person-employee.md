This file creates the **Employee** subject area folder (`Person:Employee`) and its
Prime Words / Modifiers / Class Words sub-folders in the Data Field Naming glossary, along with any terms
specific to this subject area. It also links the folder as a member of the existing `SubjectArea::Person:Employee`
governance collection (see `CocoSubjectAreaDefinition.java`), so the two structures are connected.

Requires `glossary.md` and `person.md` to have been processed
first, and requires the `SubjectArea::Person:Employee` collection to already exist in Egeria.

____

## Create Collection Folder

### Display Name

Employee

### Qualified Name

CollectionFolder::DataFieldNaming:Person:Employee

### Purpose

Groups the data field naming terms (prime words, modifiers, class words) for the Employee subject area. Information relating to an individual who is employed by an organization.

### Parent ID

CollectionFolder::DataFieldNaming:Person

### Parent Relationship Type Name

CollectionMembership

___

## Add Member to Collection
> Add/Remove a member to/from a collection.

### Element Id

CollectionFolder::DataFieldNaming:Person:Employee

### Membership Rationale

Link the Employee subject area to its data field naming vocabulary.

### Membership Status

VALIDATED

### Collection Id

SubjectArea::Person:Employee

___

## Create Collection Folder

### Display Name

Prime Words

### Qualified Name

CollectionFolder::DataFieldNaming:Person:Employee:PrimeWords

### Purpose

Prime words - the core business nouns - used to build data field names for the Employee subject area.

### Parent ID

CollectionFolder::DataFieldNaming:Person:Employee

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Modifiers

### Qualified Name

CollectionFolder::DataFieldNaming:Person:Employee:Modifiers

### Purpose

Modifiers specific to the Employee subject area, used to qualify a prime word or class word when building data field names.

### Parent ID

CollectionFolder::DataFieldNaming:Person:Employee

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Class Words

### Qualified Name

CollectionFolder::DataFieldNaming:Person:Employee:ClassWords

### Purpose

Class words specific to the Employee subject area, used as the trailing element of a data field name.

### Parent ID

CollectionFolder::DataFieldNaming:Person:Employee

### Parent Relationship Type Name

CollectionMembership

___

# Employee

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Employee

### Abbreviation

EMP

### Aliases

- Staff Member
- Worker
- Staff

### Glossary Name

- Glossary::DataFieldNaming

### Summary

An individual employed by Coco Pharmaceuticals.

### Folders

CollectionFolder::DataFieldNaming:Person:Employee:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Employee

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Role

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Role

### Aliases

- Job Function
- Position

### Glossary Name

- Glossary::DataFieldNaming

### Summary

The job function an employee performs within the organization.

### Folders

CollectionFolder::DataFieldNaming:Person:Employee:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Role

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Manager

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Manager

### Abbreviation

MGR

### Aliases

- Supervisor
- Line Manager

### Glossary Name

- Glossary::DataFieldNaming

### Summary

The employee responsible for supervising another employee.

### Folders

CollectionFolder::DataFieldNaming:Person:Employee:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Manager

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Title

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Title

### Aliases

- Job Title
- Position Title

### Glossary Name

- Glossary::DataFieldNaming

### Summary

The formal name of the position an employee holds within the organization, e.g. `EmployeeTitle`.

### Folders

CollectionFolder::DataFieldNaming:Person:Employee:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Title

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Permanent

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Permanent

### Abbreviation

PERM

### Aliases

- Full-Time
- Fixed

### Glossary Name

- Glossary::DataFieldNaming

### Summary

Relating to an employee with an open-ended contract of employment, e.g. `PermanentEmployeeCount`.

### Folders

CollectionFolder::DataFieldNaming:Person:Employee:Modifiers

### Qualified Name

GlossaryTerm::DataFieldNaming::Permanent

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Temporary

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Temporary

### Abbreviation

TEMP

### Aliases

- Fixed-Term
- Casual
- Contract

### Glossary Name

- Glossary::DataFieldNaming

### Summary

Relating to an employee engaged for a fixed period, e.g. `TemporaryEmployeeCount`.

### Folders

CollectionFolder::DataFieldNaming:Person:Employee:Modifiers

### Qualified Name

GlossaryTerm::DataFieldNaming::Temporary

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Hire

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Hire

### Aliases

- Onboarding
- Joining
- Start

### Glossary Name

- Glossary::DataFieldNaming

### Summary

Relating to the point at which an employee joins the organization, e.g. `EmployeeHireDate`.

### Folders

CollectionFolder::DataFieldNaming:Person:Employee:Modifiers

### Qualified Name

GlossaryTerm::DataFieldNaming::Hire

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Leave

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Leave

### Aliases

- Termination
- Departure
- Exit

### Glossary Name

- Glossary::DataFieldNaming

### Summary

Relating to the point at which an employee's employment with the organization ends, e.g. `EmployeeLeaveDate`.

### Folders

CollectionFolder::DataFieldNaming:Person:Employee:Modifiers

### Qualified Name

GlossaryTerm::DataFieldNaming::Leave

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Grade

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Grade

### Abbreviation

GRD

### Aliases

- Level
- Band
- Job Grade

### Glossary Name

- Glossary::DataFieldNaming

### Summary

The job grade or level assigned to an employee, e.g. `EmployeeGrade`.

### Folders

CollectionFolder::DataFieldNaming:Person:Employee:ClassWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Grade

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___
