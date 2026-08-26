This file creates the **Hospital** subject area folder (`Organization:Hospital`) and its
Prime Words / Modifiers / Class Words sub-folders in the Data Field Naming glossary, along with any terms
specific to this subject area. It also links the folder as a member of the existing `SubjectArea::Organization:Hospital`
governance collection (see `CocoSubjectAreaDefinition.java`), so the two structures are connected.

Requires `glossary.md` and `organization.md` to have been processed
first, and requires the `SubjectArea::Organization:Hospital` collection to already exist in Egeria.

____

## Create Collection Folder

### Display Name

Hospital

### Qualified Name

CollectionFolder::DataFieldNaming:Organization:Hospital

### Purpose

Groups the data field naming terms (prime words, modifiers, class words) for the Hospital subject area. Information relating to a hospital's organization.

### Parent ID

CollectionFolder::DataFieldNaming:Organization

### Parent Relationship Type Name

CollectionMembership

___

## Add Member to Collection
> Add/Remove a member to/from a collection.

### Element Id

CollectionFolder::DataFieldNaming:Organization:Hospital

### Membership Rationale

Link the Hospital subject area to its data field naming vocabulary.

### Membership Status

VALIDATED

### Collection Id

SubjectArea::Organization:Hospital

___

## Create Collection Folder

### Display Name

Prime Words

### Qualified Name

CollectionFolder::DataFieldNaming:Organization:Hospital:PrimeWords

### Purpose

Prime words - the core business nouns - used to build data field names for the Hospital subject area.

### Parent ID

CollectionFolder::DataFieldNaming:Organization:Hospital

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Modifiers

### Qualified Name

CollectionFolder::DataFieldNaming:Organization:Hospital:Modifiers

### Purpose

Modifiers specific to the Hospital subject area, used to qualify a prime word or class word when building data field names.

### Parent ID

CollectionFolder::DataFieldNaming:Organization:Hospital

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Class Words

### Qualified Name

CollectionFolder::DataFieldNaming:Organization:Hospital:ClassWords

### Purpose

Class words specific to the Hospital subject area, used as the trailing element of a data field name.

### Parent ID

CollectionFolder::DataFieldNaming:Organization:Hospital

### Parent Relationship Type Name

CollectionMembership

___

# Hospital

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Hospital

### Aliases

- Medical Center
- Clinic
- Infirmary

### Glossary Name

- Glossary::DataFieldNaming

### Summary

A healthcare organization that provides in-patient and out-patient medical treatment.

### Folders

CollectionFolder::DataFieldNaming:Organization:Hospital:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Hospital

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Ward

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Ward

### Aliases

- Unit
- Wing

### Glossary Name

- Glossary::DataFieldNaming

### Summary

A distinct area within a hospital where patients are cared for.

### Folders

CollectionFolder::DataFieldNaming:Organization:Hospital:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Ward

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Bed

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Bed

### Aliases

- Berth

### Glossary Name

- Glossary::DataFieldNaming

### Summary

An individual place where a patient is accommodated within a ward.

### Folders

CollectionFolder::DataFieldNaming:Organization:Hospital:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Bed

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Inpatient

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Inpatient

### Abbreviation

IP

### Aliases

- In-Patient
- Admitted

### Glossary Name

- Glossary::DataFieldNaming

### Summary

Relating to a patient who stays overnight at the hospital, e.g. `HospitalInpatientCapacity`.

### Folders

CollectionFolder::DataFieldNaming:Organization:Hospital:Modifiers

### Qualified Name

GlossaryTerm::DataFieldNaming::Inpatient

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Outpatient

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Outpatient

### Abbreviation

OP

### Aliases

- Out-Patient
- Ambulatory

### Glossary Name

- Glossary::DataFieldNaming

### Summary

Relating to a patient who is treated without an overnight stay, e.g. `HospitalOutpatientCapacity`.

### Folders

CollectionFolder::DataFieldNaming:Organization:Hospital:Modifiers

### Qualified Name

GlossaryTerm::DataFieldNaming::Outpatient

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Capacity

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Capacity

### Abbreviation

CAP

### Aliases

- Max Occupancy

### Glossary Name

- Glossary::DataFieldNaming

### Summary

The maximum number of beds, patients or resources a facility can accommodate, e.g. `WardCapacity`.

### Folders

CollectionFolder::DataFieldNaming:Organization:Hospital:ClassWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Capacity

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___
