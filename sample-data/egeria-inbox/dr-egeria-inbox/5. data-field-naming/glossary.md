This file creates the **Data Field Naming Glossary** for Coco Pharmaceuticals. Its purpose is to hold the
vocabulary used to build consistent, readable names for data fields, following the classic
**prime word + modifier(s) + class word** naming convention:

* **Prime word** - the core business noun the field is about (e.g. `Patient`, `Hospital`, `Contract`).
* **Modifier** - an optional qualifier that refines the prime word or class word (e.g. `Current`, `Primary`, `Discharge`).
* **Class word** - a generic suffix describing the kind of value held (e.g. `Name`, `Identifier`, `Date`).

For example: `PatientAdmittingDate` = Patient (prime word) + Admitting (modifier) + Date (class word).

The glossary is organized into a folder for each subject area defined in `CocoSubjectAreaDefinition`, mirroring
its parent/child structure - see the other files in this directory, one per subject area, plus
`common-modifiers.md` and `common-class-words.md` for terms shared across subject areas. See `README.md` for the
load order.

This file must be processed first, since every other file references `Glossary::DataFieldNaming` as a parent.

____

## Create Glossary

### Display Name

Data Field Naming

### Language

English

### Usage

This glossary is used by data architects and data stewards when naming new data fields. Build a field name by
combining a prime word (from the relevant subject area), zero or more modifiers (from the subject area or the
Common Modifiers folder), and a class word (from the subject area or the Common Class Words folder).

### Description

The vocabulary of prime words, modifiers and class words used to construct consistent data field names across
Coco Pharmaceuticals, organized by subject area (see `CocoSubjectAreaDefinition`).

### Qualified Name

Glossary::DataFieldNaming

### Content Status

ACTIVE

### Purpose

To support consistent, self-describing data field naming across Coco Pharmaceuticals' data structures.

### Search Keywords

- Data Field Naming
- Naming Standards
- Data Architecture

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

____
