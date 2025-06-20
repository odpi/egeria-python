
# `Data Fields` with filter: `*`

# Data Field Report - created at 2025-06-19 21:01
	Data Field  found from the search string:  `All`

# Data Field Name: HospitalId

## Description
Unique identifier for a hospital. Used in forming PatientId.

## Assigned Meanings
Term::Hospital Identifier

## Qualified Name
DataField::HospitalId

## Data Type
String

## GUID
88f05a4c-6efb-49a2-a4c8-386df5d7c303

## Is Nullable
True

## Sort Order
UNSORTED

## Parent Names
DataField::PatientId

## Data Dictionaries
DataDict::Clinical Trial Data Dictionary

## Data Structures
DataStruct::TBDF-Incoming Weekly Measurement Data,
DataStruct::WWT-Incoming Weekly Measurement Data

## Mermaid Graph
```mermaid
---
title: Data Field - HospitalId [88f05a4c-6efb-49a2-a4c8-386df5d7c303]
---
flowchart TD
%%{init: {"flowchart": {"htmlLabels": false}} }%%

1@{ shape: text, label: "*Description*
**Unique identifier for a hospital. Used in forming PatientId.**"}
2@{ shape: rect, label: "*Data Field*
**HospitalId**"}
3@{ shape: rect, label: "*Controlled Glossary Term*
**Hospital Identifier**"}
2==>|"Semantic Definition"|3
4@{ shape: rect, label: "*Collection [ Data Dictionary]*
**Clinical Trial Data Dictionary**"}
4==>|"Collection Membership"|2
5@{ shape: rect, label: "*Data Structure*
**TBDF-Incoming Weekly Measurement Data**"}
5==>|"[1] 1..*"|2
6@{ shape: rect, label: "*Data Structure*
**WWT-Incoming Weekly Measurement Data**"}
6==>|"[1] 1..*"|2
7@{ shape: rect, label: "*Data Field*
**PatientId**"}
7==>|"Nested Data Field"|2
style 1 color:#000000, fill:#F9F7ED, stroke:#b7c0c7
style 2 color:#000000, fill:#ffe3cc, stroke:#f9845b
style 3 color:#000000, fill:#66cdaa, stroke:#008080
style 4 color:#000000, fill:#d2691e, stroke:#000000
style 5 color:#000000, fill:#f9845b, stroke:#000000
style 6 color:#000000, fill:#f9845b, stroke:#000000
style 7 color:#000000, fill:#ffe3cc, stroke:#f9845b
```

---

# Data Field Name: PatientSN

## Description
Unique identifier of the patient within a hospital.

## Qualified Name
DataField::PatientSN

## Data Type
String

## GUID
15e891db-8b4b-41d7-9f67-d0ed721142e5

## Is Nullable
True

## Sort Order
UNSORTED

## Parent Names
DataField::PatientId

## Data Dictionaries
DataDict::Clinical Trial Data Dictionary

## Data Structures
DataStruct::TBDF-Incoming Weekly Measurement Data,
DataStruct::WWT-Incoming Weekly Measurement Data

## Mermaid Graph
```mermaid
---
title: Data Field - PatientSN [15e891db-8b4b-41d7-9f67-d0ed721142e5]
---
flowchart TD
%%{init: {"flowchart": {"htmlLabels": false}} }%%

1@{ shape: text, label: "*Description*
**Unique identifier of the patient within a hospital.**"}
2@{ shape: rect, label: "*Data Field*
**PatientSN**"}
3@{ shape: rect, label: "*Collection [ Data Dictionary]*
**Clinical Trial Data Dictionary**"}
3==>|"Collection Membership"|2
4@{ shape: rect, label: "*Data Structure*
**TBDF-Incoming Weekly Measurement Data**"}
4==>|"[2] 1..*"|2
5@{ shape: rect, label: "*Data Structure*
**WWT-Incoming Weekly Measurement Data**"}
5==>|"[2] 1..*"|2
6@{ shape: rect, label: "*Data Field*
**PatientId**"}
6==>|"Nested Data Field"|2
style 1 color:#000000, fill:#F9F7ED, stroke:#b7c0c7
style 2 color:#000000, fill:#ffe3cc, stroke:#f9845b
style 3 color:#000000, fill:#d2691e, stroke:#000000
style 4 color:#000000, fill:#f9845b, stroke:#000000
style 5 color:#000000, fill:#f9845b, stroke:#000000
style 6 color:#000000, fill:#ffe3cc, stroke:#f9845b
```

---

# Data Field Name: Date

## Description
A date of the form YYYY-MM-DD

## Qualified Name
DataField::Date

## Data Type
Date

## Data Class
DataClass::ISO-Date

## GUID
2ca5f6c9-1c9e-40b7-bffd-0ec440c1673d

## Is Nullable
True

## Sort Order
UNSORTED

## Data Dictionaries
DataDict::Clinical Trial Data Dictionary

## Data Structures
DataStruct::TBDF-Incoming Weekly Measurement Data,
DataStruct::WWT-Incoming Weekly Measurement Data

## Mermaid Graph
```mermaid
---
title: Data Field - Date [2ca5f6c9-1c9e-40b7-bffd-0ec440c1673d]
---
flowchart TD
%%{init: {"flowchart": {"htmlLabels": false}} }%%

1@{ shape: text, label: "*Description*
**A date of the form YYYY-MM-DD**"}
2@{ shape: rect, label: "*Data Field*
**Date**"}
3@{ shape: rect, label: "*Data Class*
**ISO-Date**"}
2==>|"Data Class Definition"|3
4@{ shape: rect, label: "*Collection [ Data Dictionary]*
**Clinical Trial Data Dictionary**"}
4==>|"Collection Membership"|2
5@{ shape: rect, label: "*Data Structure*
**TBDF-Incoming Weekly Measurement Data**"}
5==>|"[0] 1..*"|2
6@{ shape: rect, label: "*Data Structure*
**WWT-Incoming Weekly Measurement Data**"}
6==>|"[0] 1..*"|2
style 1 color:#000000, fill:#F9F7ED, stroke:#b7c0c7
style 2 color:#000000, fill:#ffe3cc, stroke:#f9845b
style 3 color:#000000, fill:#6495ed, stroke:#3079ab
style 4 color:#000000, fill:#d2691e, stroke:#000000
style 5 color:#000000, fill:#f9845b, stroke:#000000
style 6 color:#000000, fill:#f9845b, stroke:#000000
```

---

# Data Field Name: PatientId

## Description
Unique identifier of the patient

## Assigned Meanings
GlossaryTerm::ClinicalTrialTerminology::PatientId

## Qualified Name
DataField::PatientId

## Data Type
String

## GUID
e353268d-a125-49a1-9be5-3046b5c13bc3

## Is Nullable
True

## Sort Order
UNSORTED

## Data Dictionaries
DataDict::Pharma Data Dictionary,
DataDict::Clinical Trial Data Dictionary

## Data Structures
DataStruct::TBDF-Incoming Weekly Measurement Data,
DataStruct::WWT-Incoming Weekly Measurement Data

## Mermaid Graph
```mermaid
---
title: Data Field - PatientId [e353268d-a125-49a1-9be5-3046b5c13bc3]
---
flowchart TD
%%{init: {"flowchart": {"htmlLabels": false}} }%%

1@{ shape: text, label: "*Description*
**Unique identifier of the patient**"}
2@{ shape: rect, label: "*Data Field*
**PatientId**"}
3@{ shape: rect, label: "*Data Field*
**PatientSN**"}
4@{ shape: rect, label: "*Collection [ Data Dictionary]*
**Clinical Trial Data Dictionary**"}
4==>|"Collection Membership"|3
5@{ shape: rect, label: "*Data Structure*
**TBDF-Incoming Weekly Measurement Data**"}
5==>|"[2] 1..*"|3
6@{ shape: rect, label: "*Data Structure*
**WWT-Incoming Weekly Measurement Data**"}
6==>|"[2] 1..*"|3
2==>|"Nested Data Field"|3
2==>|"*"|3
7@{ shape: rect, label: "*Data Field*
**HospitalId**"}
8@{ shape: rect, label: "*Controlled Glossary Term*
**Hospital Identifier**"}
7==>|"Semantic Definition"|8
4==>|"Collection Membership"|7
5==>|"[1] 1..*"|7
6==>|"[1] 1..*"|7
2==>|"Nested Data Field"|7
2==>|"*"|7
9@{ shape: rect, label: "*Glossary Term*
**Patient Identifier**"}
2==>|"Semantic Definition"|9
10@{ shape: rect, label: "*Collection [ Data Dictionary]*
**Pharma Data Dictionary**"}
10==>|"Collection Membership"|2
4==>|"Collection Membership"|2
5==>|"[0] 1..*"|2
6==>|"[0] 1..*"|2
style 1 color:#000000, fill:#F9F7ED, stroke:#b7c0c7
style 2 color:#000000, fill:#ffe3cc, stroke:#f9845b
style 3 color:#000000, fill:#ffe3cc, stroke:#f9845b
style 4 color:#000000, fill:#d2691e, stroke:#000000
style 5 color:#000000, fill:#f9845b, stroke:#000000
style 6 color:#000000, fill:#f9845b, stroke:#000000
style 7 color:#000000, fill:#ffe3cc, stroke:#f9845b
style 8 color:#000000, fill:#66cdaa, stroke:#008080
style 9 color:#000000, fill:#66cdaa, stroke:#008080
style 10 color:#000000, fill:#d2691e, stroke:#000000
```



# `DataDictionary` with filter: `Test Spec2`

```
[
    {
        "guid": "3162ac1c-82c0-48b9-86cc-2b5b45aaf63d",
        "display_name": "Test Spec2",
        "description": "A test spec - Meow",
        "qualified_name": "DataSpec::Test Spec2",
        "classifications": "Anchors, DataSpec",
        "members": "DataStruct::WWT-Incoming Weekly Measurement Data",
        "additional_properties": {},
        "extended_properties": {}
    }
]
```



# `DataSpec` with filter: `*`

# DataSpecs Table

DataSpecs found from the search string: `All`

| Name | Qualified Name | Description | Classifications | Members | 
|-------------|-------------|-------------|-------------|-------------|
| Data Specification for the Teddy Bear Dropt Clinical Trial | DataSpec::Data Specification for the Teddy Bear Dropt Clinical Trial | Principle data requirements for Teddy Bear Dropt Clinical Trial. Meow | Anchors, DataSpec | DataStruct::TBDF-Incoming Weekly Measurement Data | 
| Test Spec2 | DataSpec::Test Spec2 | A test spec - Meow | Anchors, DataSpec | DataStruct::WWT-Incoming Weekly Measurement Data | 



# `Data Structures` with filter: `*`

# Data Structure Report - created at 2025-06-19 21:01
	Data Structure  found from the search string:  `All`

# Data Structure Name: WWT-Incoming Weekly Measurement Data

## Qualified Name
DataStruct::WWT-Incoming Weekly Measurement Data

## Description
A collection of data fields that form a data structure.

## Data Fields
DataField::Date,
DataField::HospitalId,
DataField::PatientSN,
DataField::PatientId

## Data Specification
DataSpec::Test Spec2

## GUID
c920d08c-acc3-4c7d-b963-5d8b1723665e

## Mermaid Graph
```mermaid
---
title: Data Structure - WWT-Incoming Weekly Measurement Data [c920d08c-acc3-4c7d-b963-5d8b1723665e]
---
flowchart TD
%%{init: {"flowchart": {"htmlLabels": false}} }%%

1@{ shape: text, label: "*Description*
**A collection of data fields that form a data structure.**"}
2@{ shape: rect, label: "*Data Structure*
**c920d08c-acc3-4c7d-b963-5d8b1723665e**"}
subgraph 3 [Data fields]
4@{ shape: rect, label: "*Data Field*
**Date**"}
5@{ shape: rect, label: "*Data Class*
**ISO-Date**"}
4==>|"Data Class Definition"|5
6@{ shape: rect, label: "*Collection [ Data Dictionary]*
**Clinical Trial Data Dictionary**"}
6==>|"Collection Membership"|4
7@{ shape: rect, label: "*Data Structure*
**TBDF-Incoming Weekly Measurement Data**"}
7==>|"[0] 1..*"|4
8@{ shape: rect, label: "*Data Structure*
**WWT-Incoming Weekly Measurement Data**"}
8==>|"[0] 1..*"|4
2==>|"[0] 1..1"|4
9@{ shape: rect, label: "*Data Field*
**HospitalId**"}
10@{ shape: rect, label: "*Controlled Glossary Term*
**Hospital Identifier**"}
9==>|"Semantic Definition"|10
6==>|"Collection Membership"|9
7==>|"[1] 1..*"|9
8==>|"[1] 1..*"|9
11@{ shape: rect, label: "*Data Field*
**PatientId**"}
11==>|"Nested Data Field"|9
2==>|"[1] 1..1"|9
12@{ shape: rect, label: "*Data Field*
**PatientSN**"}
6==>|"Collection Membership"|12
7==>|"[2] 1..*"|12
8==>|"[2] 1..*"|12
11==>|"Nested Data Field"|12
2==>|"[2] 1..1"|12
11==>|"*"|12
11==>|"*"|9
13@{ shape: rect, label: "*Glossary Term*
**Patient Identifier**"}
11==>|"Semantic Definition"|13
14@{ shape: rect, label: "*Collection [ Data Dictionary]*
**Pharma Data Dictionary**"}
14==>|"Collection Membership"|11
6==>|"Collection Membership"|11
7==>|"[0] 1..*"|11
8==>|"[0] 1..*"|11
2==>|"[0] 1..1"|11
end
8==>|"contains"|3
15@{ shape: rect, label: "*Collection [ Data Spec]*
**Test Spec2**"}
15==>|"Collection Membership"|8
style 11 color:#000000, fill:#ffe3cc, stroke:#f9845b
style 12 color:#000000, fill:#ffe3cc, stroke:#f9845b
style 13 color:#000000, fill:#66cdaa, stroke:#008080
style 14 color:#000000, fill:#d2691e, stroke:#000000
style 15 color:#000000, fill:#deb887, stroke:#000000
style 1 color:#000000, fill:#F9F7ED, stroke:#b7c0c7
style 2 color:#000000, fill:#f9845b, stroke:#000000
style 3 color:#000000, fill:#ffab66, stroke:#f9845b
style 4 color:#000000, fill:#ffe3cc, stroke:#f9845b
style 5 color:#000000, fill:#6495ed, stroke:#3079ab
style 6 color:#000000, fill:#d2691e, stroke:#000000
style 7 color:#000000, fill:#f9845b, stroke:#000000
style 8 color:#000000, fill:#f9845b, stroke:#000000
style 9 color:#000000, fill:#ffe3cc, stroke:#f9845b
style 10 color:#000000, fill:#66cdaa, stroke:#008080
```

---

# Data Structure Name: TBDF-Incoming Weekly Measurement Data

## Qualified Name
DataStruct::TBDF-Incoming Weekly Measurement Data

## Description
This describes the weekly measurement data for each patient for the Teddy Bear dropt clinical trial.

## Data Fields
DataField::PatientSN,
DataField::HospitalId,
DataField::Date,
DataField::PatientId

## Data Specification
DataSpec::Data Specification for the Teddy Bear Dropt Clinical Trial

## GUID
18f6cd2e-e225-4e24-a630-5e4e35b0b650

## Mermaid Graph
```mermaid
---
title: Data Structure - TBDF-Incoming Weekly Measurement Data [18f6cd2e-e225-4e24-a630-5e4e35b0b650]
---
flowchart TD
%%{init: {"flowchart": {"htmlLabels": false}} }%%

1@{ shape: text, label: "*Description*
**This describes the weekly measurement data for each patient for the Teddy Bear dropt clinical trial.**"}
2@{ shape: rect, label: "*Data Structure*
**18f6cd2e-e225-4e24-a630-5e4e35b0b650**"}
subgraph 3 [Data fields]
4@{ shape: rect, label: "*Data Field*
**PatientSN**"}
5@{ shape: rect, label: "*Collection [ Data Dictionary]*
**Clinical Trial Data Dictionary**"}
5==>|"Collection Membership"|4
6@{ shape: rect, label: "*Data Structure*
**TBDF-Incoming Weekly Measurement Data**"}
6==>|"[2] 1..*"|4
7@{ shape: rect, label: "*Data Structure*
**WWT-Incoming Weekly Measurement Data**"}
7==>|"[2] 1..*"|4
8@{ shape: rect, label: "*Data Field*
**PatientId**"}
8==>|"Nested Data Field"|4
2==>|"[2] 1..1"|4
9@{ shape: rect, label: "*Data Field*
**HospitalId**"}
10@{ shape: rect, label: "*Controlled Glossary Term*
**Hospital Identifier**"}
9==>|"Semantic Definition"|10
5==>|"Collection Membership"|9
6==>|"[1] 1..*"|9
7==>|"[1] 1..*"|9
8==>|"Nested Data Field"|9
2==>|"[1] 1..1"|9
11@{ shape: rect, label: "*Data Field*
**Date**"}
12@{ shape: rect, label: "*Data Class*
**ISO-Date**"}
11==>|"Data Class Definition"|12
5==>|"Collection Membership"|11
6==>|"[0] 1..*"|11
7==>|"[0] 1..*"|11
2==>|"[0] 1..1"|11
8==>|"*"|4
8==>|"*"|9
13@{ shape: rect, label: "*Glossary Term*
**Patient Identifier**"}
8==>|"Semantic Definition"|13
14@{ shape: rect, label: "*Collection [ Data Dictionary]*
**Pharma Data Dictionary**"}
14==>|"Collection Membership"|8
5==>|"Collection Membership"|8
6==>|"[0] 1..*"|8
7==>|"[0] 1..*"|8
2==>|"[0] 1..1"|8
end
6==>|"contains"|3
15@{ shape: rect, label: "*Collection [ Data Spec]*
**Data Specification for the Teddy Bear Dropt Clinical Trial**"}
15==>|"Collection Membership"|6
style 11 color:#000000, fill:#ffe3cc, stroke:#f9845b
style 12 color:#000000, fill:#6495ed, stroke:#3079ab
style 13 color:#000000, fill:#66cdaa, stroke:#008080
style 14 color:#000000, fill:#d2691e, stroke:#000000
style 15 color:#000000, fill:#deb887, stroke:#000000
style 1 color:#000000, fill:#F9F7ED, stroke:#b7c0c7
style 2 color:#000000, fill:#f9845b, stroke:#000000
style 3 color:#000000, fill:#ffab66, stroke:#f9845b
style 4 color:#000000, fill:#ffe3cc, stroke:#f9845b
style 5 color:#000000, fill:#d2691e, stroke:#000000
style 6 color:#000000, fill:#f9845b, stroke:#000000
style 7 color:#000000, fill:#f9845b, stroke:#000000
style 8 color:#000000, fill:#ffe3cc, stroke:#f9845b
style 9 color:#000000, fill:#ffe3cc, stroke:#f9845b
style 10 color:#000000, fill:#66cdaa, stroke:#008080
```


#  foo Create Glossary
## Glossary Name
Test Glossary
## Description
This glossary is just for testing

___

#  foo Create Term
## In Glossary
Test Glossary
## Term Name
Hospital Identifier
## Description
Identifies each hospital uniquely. Used within the PatientId field.

___

# foo Create Data Dictionary
## Name
Clinical Trial Data Dictionary

## Description
A data dictionary for clinical trial data elements.


#  foo Create Data Dictionary
## Name
Pharma Data Dictionary

## Description
A data dictionary of elements relevant to the Pharma communities.


___

#  foo Create Data Spec

## Data Specification

Data Specification for the Teddy Bear Dropt Clinical Trial

## Description
Principle data requirements for Teddy Bear Dropt Clinical Trial. Meow

## Qualified Name
DataSpec::Data Specification for the Teddy Bear Dropt Clinical Trial

## Classifications

## Guid


___


#  foo Create Data Specification

## Data Specification Name

Test Spec2

## Description
A test spec - Meow

## Qualified Name

## Classifications

## Guid

## Additional Properties
{
"a prop" : "meow",
"another" : "woof"
}
___

# foo Create Data Dictionary

## Dictionary Name

dw

## Description
A data dictionary for dan..
## Qualified Name
DataDict::dw

## Classifications

## GUID


___


#  foo Create Data Structure

## Data Structure Name

TBDF-Incoming Weekly Measurement Data

## Description
This describes the weekly measurement data for each patient for the Teddy Bear dropt clinical trial.

## Qualified Name
DataStruct::TBDF-Incoming Weekly Measurement Data

## Namespace

## In Data Specification
Data Specification for the Teddy Bear Dropt Clinical Trial

## Version Identifier


## Guid


___

#  foo Create Data Structure

## Data Structure Name

WWT-Incoming Weekly Measurement Data

## Description
A collection of data fields that form a data structure.

## Qualified Name
DataStruct::WWT-Incoming Weekly Measurement Data

## In Data Specification
Test Spec2

## Namespace


## Version Identifier


## GUID



___

# foo Create Data Field

## Data Field Name

PatientId

## Description
Unique identifier of the patient

## Qualified Name
DataField::PatientId


## Data Type

String

## Guid

## Data Class

## In Data Dictionary
DataDict::Clinical Trial Data Dictionary, Pharma Data Dictionary

## In Data Structure
TBDF-Incoming Weekly Measurement Data
DataStruct::WWT-Incoming Weekly Measurement Data

## Glossary Term
GlossaryTerm::ClinicalTrialTerminology::PatientId
___



#  foo Create Data Field

## Data Field Name

HospitalId

## Description
Unique identifier for a hospital. Used in forming PatientId.

## Qualified Name
DataField::HospitalId

## Data Type
String

## In Data Dictionary
DataDict::Clinical Trial Data Dictionary

## In Data Structure

DataStruct::TBDF-Incoming Weekly Measurement Data
DataStruct::WWT-Incoming Weekly Measurement Data

## Position
1

## Min Cardinality
0

## Max Cardinality
1

## Glossary Term
Term::Hospital Identifier

## Parent Data Field
DataField::PatientId

## Journal Entry
Just creating this term

___

# foo Create Data Field

## Data Field Name

PatientSN

## Description
Unique identifier of the patient within a hospital.

## Qualified Name
DataField::PatientSN


## Data Type

String
## Position
2

## Min Cardinality
0

## Max Cardinality
1

## In Data Dictionary
DataDict::Clinical Trial Data Dictionary

## In Data Structure
DataStruct::TBDF-Incoming Weekly Measurement Data
DataStruct::WWT-Incoming Weekly Measurement Data

## Parent Data Field
DataField::PatientId

## Journal Entry
Just creating this term

___

#  foo Create Data Class

## Data Class Name

Date

## Description
A date of the form YYYY-MM-DD

## Qualified Name
DataClass::Date

## Data Type
date
## Position
0

## Min Cardinality
0

## Max Cardinality
1

## In Data Dictionary
DataDict::Clinical Trial Data Dictionary


## Containing Data Class

## Specializes Data Class

## Journal Entry
Just creating this date



___

#  foo Update Data Class

## Data Class Name

ISO-Date

## Description
ISO 8601 standard date. A date of the form YYYY-MM-DD

## Qualified Name
DataClass::ISO-Date

## Data Type
date
## Position
0

## Min Cardinality
0

## Max Cardinality
1

## In Data Dictionary
DataDict::Clinical Trial Data Dictionary


## Containing Data Class

## Specializes Data Class
DataClass::Date
## Journal Entry
Just creating this date


___


# foo Update Data Field

## Data Field

Date

## Description
A date of the form YYYY-MM-DD

## Qualified Name
DataField::Date


## Data Type
date

## Position
0

## Min Cardinality
0

## Max Cardinality
1

## In Data Dictionary
DataDict::Clinical Trial Data Dictionary

## In Data Structure
TBDF-Incoming Weekly Measurement Data,
DataStruct::WWT-Incoming Weekly Measurement Data

## Parent Data Field

## Data Class
DataClass::ISO-Date

## Journal Entry
Just creating this date


___



# foo Create Data Class

## Data Class Name

Address

## Description
Address Class

## Qualified Name



## Data Type

String
## Position
0

## Min Cardinality
0

## Max Cardinality
1

## In Data Dictionary
DataDict::Clinical Trial Data Dictionary


## Containing Data Class

## Specializes Data Class

## Journal Entry
Just creating this date
# Provenance

* Results from processing file data_test2.md on 2025-06-19 21:01
