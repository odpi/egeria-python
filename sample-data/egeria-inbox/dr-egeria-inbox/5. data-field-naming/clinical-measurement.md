This file creates the **Measurement** subject area folder (`Clinical:Measurement`) and its
Prime Words / Modifiers / Class Words sub-folders in the Data Field Naming glossary, along with any terms
specific to this subject area. It also links the folder as a member of the existing `SubjectArea::Clinical:Measurement`
governance collection (see `CocoSubjectAreaDefinition.java`), so the two structures are connected.

Requires `glossary.md` and `clinical.md` to have been processed
first, and requires the `SubjectArea::Clinical:Measurement` collection to already exist in Egeria.

____

## Create Collection Folder

### Display Name

Measurement

### Qualified Name

CollectionFolder::DataFieldNaming:Clinical:Measurement

### Purpose

Groups the data field naming terms (prime words, modifiers, class words) for the Measurement subject area. Information relating to the measurements taken to understand medical conditions and their effectiveness.

### Parent ID

CollectionFolder::DataFieldNaming:Clinical

### Parent Relationship Type Name

CollectionMembership

___

## Add Member to Collection
> Add/Remove a member to/from a collection.

### Element Id

CollectionFolder::DataFieldNaming:Clinical:Measurement

### Membership Rationale

Link the Measurement subject area to its data field naming vocabulary.

### Membership Status

VALIDATED

### Collection Id

SubjectArea::Clinical:Measurement

___

## Create Collection Folder

### Display Name

Prime Words

### Qualified Name

CollectionFolder::DataFieldNaming:Clinical:Measurement:PrimeWords

### Purpose

Prime words - the core business nouns - used to build data field names for the Measurement subject area.

### Parent ID

CollectionFolder::DataFieldNaming:Clinical:Measurement

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Modifiers

### Qualified Name

CollectionFolder::DataFieldNaming:Clinical:Measurement:Modifiers

### Purpose

Modifiers specific to the Measurement subject area, used to qualify a prime word or class word when building data field names.

### Parent ID

CollectionFolder::DataFieldNaming:Clinical:Measurement

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Class Words

### Qualified Name

CollectionFolder::DataFieldNaming:Clinical:Measurement:ClassWords

### Purpose

Class words specific to the Measurement subject area, used as the trailing element of a data field name.

### Parent ID

CollectionFolder::DataFieldNaming:Clinical:Measurement

### Parent Relationship Type Name

CollectionMembership

___

# Measurement

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Measurement

### Abbreviation

MEAS

### Aliases

- Reading
- Observation

### Glossary Name

- Glossary::DataFieldNaming

### Summary

A quantified observation taken about a patient's condition.

### Folders

CollectionFolder::DataFieldNaming:Clinical:Measurement:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Measurement

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# VitalSign

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

VitalSign

### Aliases

- Vital Signs
- Vitals

### Glossary Name

- Glossary::DataFieldNaming

### Summary

A measurement of a basic body function, such as heart rate or blood pressure.

### Folders

CollectionFolder::DataFieldNaming:Clinical:Measurement:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::VitalSign

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Baseline

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Baseline

### Aliases

- Initial
- Reference Point

### Glossary Name

- Glossary::DataFieldNaming

### Summary

Relating to the initial measurement taken before treatment begins, e.g. `BaselineMeasurementValue`.

### Folders

CollectionFolder::DataFieldNaming:Clinical:Measurement:Modifiers

### Qualified Name

GlossaryTerm::DataFieldNaming::Baseline

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Unit

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Unit

### Aliases

- Unit of Measure
- UOM

### Glossary Name

- Glossary::DataFieldNaming

### Summary

The unit in which a measurement or quantity is expressed, e.g. `MeasurementUnit`.

### Folders

CollectionFolder::DataFieldNaming:Clinical:Measurement:ClassWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Unit

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Value

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Value

### Aliases

- Reading
- Result

### Glossary Name

- Glossary::DataFieldNaming

### Summary

The numeric result of a measurement, e.g. `MeasurementValue`.

### Folders

CollectionFolder::DataFieldNaming:Clinical:Measurement:ClassWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Value

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___
