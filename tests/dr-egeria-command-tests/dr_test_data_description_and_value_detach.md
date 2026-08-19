# New Commands Test — Data Description Link/Detach, Data Value Specification Detach

> This file tests the 2026-08-18 Dr.Egeria command additions:
>   1. Link Data Description    (Collections family)
>   2. Detach Data Description  (Collections family)
>   3. Detach Data Value Specification from Element (Data Designer family --
>      the existing Assign Data Value Specification processor, verb-branched)
>
> Self-contained: creates its own Collection, Data Structure, Data Value
> Specification, and Data Field so it doesn't depend on other test files
> having run first.
>
> Run with VALIDATE first, then PROCESS.

---

# DDV-01: Create Data Dictionary — collection used as the Data Description source

## Create Data Dictionary

### Display Name
Regression Test Data Description Dictionary

### Description
Data dictionary used only to exercise the Link/Detach Data Description commands.

### Content Status
ACTIVE

### Version Identifier
1.0

### Authors
jane.smith@example.com

### Qualified Name
DataDictionary::RegressionTestDataDescription::1.0

### GUID

___

# DDV-02: Create Data Structure — element the Data Description is attached to

## Create Data Structure

### Display Name
Regression Test Data Description Structure

### Description
Data structure used only to exercise the Link/Detach Data Description commands.

### Content Status
ACTIVE

### Version Identifier
1.0

### Authors
jane.smith@example.com

### Qualified Name
DataStructure::RegressionTestDataDescription::1.0

### GUID

___

# DDV-03: Link Data Description — attach the dictionary to the structure

## Link Data Description

### Collection Id
DataDictionary::RegressionTestDataDescription::1.0

### Element Id
DataStructure::RegressionTestDataDescription::1.0

### Description
Connects the regression-test dictionary to the regression-test structure via
the DataDescription relationship.

___

# DDV-04: Detach Data Description — remove the relationship created in DDV-03

## Detach Data Description

### Collection Id
DataDictionary::RegressionTestDataDescription::1.0

### Element Id
DataStructure::RegressionTestDataDescription::1.0

___

# DDV-05: Create Data Value Specification — used for the Assign/Detach pair

## Create Data Value Specification

### Display Name
Regression Test Value Spec

### Description
A data value specification used only to exercise the Assign/Detach Data
Value Specification commands.

### Content Status
ACTIVE

### Version Identifier
1.0

### Authors
jane.smith@example.com

### Data Type
string

### Specification
regression test value

### Qualified Name
DataValueSpecification::RegressionTest::1.0

### GUID

___

# DDV-06: Create Data Field — element the value specification is assigned to

## Create Data Field

### Display Name
Regression Test Field

### Description
Data field used only to exercise the Assign/Detach Data Value Specification commands.

### Content Status
ACTIVE

### Authors
jane.smith@example.com

### In Data Structure
DataStructure::RegressionTestDataDescription::1.0

### Data Type
string

### Is Nullable
true

### Position
0

### Minimum Cardinality
0

### Maximum Cardinality
1

### Qualified Name
DataField::RegressionTestDataDescription::RegressionTestField::1.0

### GUID

___

# DDV-07: Assign Data Value Specification — link the spec to the field

## Assign Data Value Specification

### Data Value Specification
DataValueSpecification::RegressionTest::1.0

### Element Id
DataField::RegressionTestDataDescription::RegressionTestField::1.0

### Description
Associates the regression-test value specification with the regression-test field.

___

# DDV-08: Detach Data Value Specification from Element — remove the DDV-07 relationship

## Detach Data Value Specification from Element

### Data Value Specification
DataValueSpecification::RegressionTest::1.0

### Element Id
DataField::RegressionTestDataDescription::RegressionTestField::1.0

___

> End of Data Description / Data Value Specification detach regression tests.
>
> Expected outcomes:
>   DDV-01..DDV-02, DDV-05..DDV-06 : Create commands executed. GUIDs filled.
>   DDV-03 : Link Data Description executed -- DataDescription relationship created.
>   DDV-04 : Detach Data Description executed -- relationship removed. No error
>            even though DDV-03 already ran (idempotent detach).
>   DDV-07 : Assign Data Value Specification executed -- DataValueAssignment
>            relationship created.
>   DDV-08 : Detach Data Value Specification from Element executed -- relationship
>            removed, routed through the same AssignDataValueSpecificationProcessor
>            as DDV-07 via its verb branch.
