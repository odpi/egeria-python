This file creates the **Prescription** subject area folder (`Clinical:Prescription`) and its
Prime Words / Modifiers / Class Words sub-folders in the Data Field Naming glossary, along with any terms
specific to this subject area. It also links the folder as a member of the existing `SubjectArea::Clinical:Prescription`
governance collection (see `CocoSubjectAreaDefinition.java`), so the two structures are connected.

Requires `glossary.md` and `clinical.md` to have been processed
first, and requires the `SubjectArea::Clinical:Prescription` collection to already exist in Egeria.

____

## Create Collection Folder

### Display Name

Prescription

### Qualified Name

CollectionFolder::DataFieldNaming:Clinical:Prescription

### Purpose

Groups the data field naming terms (prime words, modifiers, class words) for the Prescription subject area. Information relating to the treatment defined for a specific patient.

### Parent ID

CollectionFolder::DataFieldNaming:Clinical

### Parent Relationship Type Name

CollectionMembership

___

## Add Member to Collection
> Add/Remove a member to/from a collection.

### Element Id

CollectionFolder::DataFieldNaming:Clinical:Prescription

### Membership Rationale

Link the Prescription subject area to its data field naming vocabulary.

### Membership Status

VALIDATED

### Collection Id

SubjectArea::Clinical:Prescription

___

## Create Collection Folder

### Display Name

Prime Words

### Qualified Name

CollectionFolder::DataFieldNaming:Clinical:Prescription:PrimeWords

### Purpose

Prime words - the core business nouns - used to build data field names for the Prescription subject area.

### Parent ID

CollectionFolder::DataFieldNaming:Clinical:Prescription

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Modifiers

### Qualified Name

CollectionFolder::DataFieldNaming:Clinical:Prescription:Modifiers

### Purpose

Modifiers specific to the Prescription subject area, used to qualify a prime word or class word when building data field names.

### Parent ID

CollectionFolder::DataFieldNaming:Clinical:Prescription

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Class Words

### Qualified Name

CollectionFolder::DataFieldNaming:Clinical:Prescription:ClassWords

### Purpose

Class words specific to the Prescription subject area, used as the trailing element of a data field name.

### Parent ID

CollectionFolder::DataFieldNaming:Clinical:Prescription

### Parent Relationship Type Name

CollectionMembership

___

# Prescription

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Prescription

### Abbreviation

RX

### Aliases

- Script

### Glossary Name

- Glossary::DataFieldNaming

### Summary

An instruction from a clinician defining the treatment to be given to a specific patient.

### Folders

CollectionFolder::DataFieldNaming:Clinical:Prescription:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Prescription

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Dosage

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Dosage

### Aliases

- Dose

### Glossary Name

- Glossary::DataFieldNaming

### Summary

The quantity and frequency of a product to be administered to a patient.

### Folders

CollectionFolder::DataFieldNaming:Clinical:Prescription:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Dosage

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Repeat

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Repeat

### Aliases

- Recurring
- Renewable

### Glossary Name

- Glossary::DataFieldNaming

### Summary

Relating to a prescription that can be dispensed more than once without a new prescription being issued, e.g. `RepeatPrescriptionCount`.

### Folders

CollectionFolder::DataFieldNaming:Clinical:Prescription:Modifiers

### Qualified Name

GlossaryTerm::DataFieldNaming::Repeat

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Frequency

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Frequency

### Abbreviation

FREQ

### Aliases

- Dosing Interval

### Glossary Name

- Glossary::DataFieldNaming

### Summary

How often a dose is to be administered, e.g. `DosageFrequency`.

### Folders

CollectionFolder::DataFieldNaming:Clinical:Prescription:ClassWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Frequency

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___
