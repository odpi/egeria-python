# Dr.Egeria - designing data - part 2
## Adding information

In Part 1, we successfully create a data structure and some data fields. We took the resulting output and copied it into this new file to create Part 2.

Dr.Egeria allows us to incrementally refine and extend our work. So in this file, we will update the same definitions to place the data fields into the data structure and 
add more technical details to the data fields. We are also going to describe how the field PatientId is composed of two sub-fields, HospitalId and PatientNumber.

We will also extend our reporting to display a detailed report on the Data Structures and Data Fields.

___


# Update Data Structure

## Data Structure Name 

TBDF-Incoming Weekly Measurement Data

## GUID
c3f75f00-10c2-46f3-b4b3-048ef40bfc65

## Qualified Name
DataStruct::TBDF-Incoming Weekly Measurement Data

## Description
This describes the weekly measurement data for each patient for the Teddy Bear drop foot clinical trial.

## Data Fields

DataField::Date, DataField::PatientId, DataField::AngleLeft, DataField::AngleRight

> Note: Its always safest to use the qualified name for an element.
> Note: A list of elements can be separated by either `,` or a new line.

## Data Specification


## Namespace


## Version Identifier


## Extended Properties
{}

## Additional Properties
{}

___


> Note: While not required, it is good practice to end each Dr.Egeria command with a `___` so that a markdown
> seperator is displayed between commands. It improves the readability.

___

# Update Data Field

## Data Field Name 

Date

## GUID
b0a66e94-8473-42f7-91bb-a92d389c1ba6

## Qualified Name
DataField::Date

## Description
A date of the form YYYY-MM-DD

## In Data Structure
DataStruct::TBDF-Incoming Weekly Measurement Data

## Assigned Meanings


## Data Type
Date

## Data Class


## Is Nullable
True

## Minimum Length
0

## Length
0

## Precision
0

## Ordered Values
False

## Sort Order
UNSORTED

## Parent Names


## Extended Properties
{}

## Additional Properties
{}

## Data Dictionaries


## Data Structures




___




# Update Data Field

## Data Field Name 

PatientId

## GUID
c442adde-2c24-4b90-9dfb-111dbdf1b357

## Qualified Name
DataField::PatientId

## Description
Unique identifier of the patient

## In Data Structure
DataStruct::TBDF-Incoming Weekly Measurement Data

## Assigned Meanings


## Data Type
String

## Data Class


## Is Nullable
True

## Minimum Length
8

## Length
0

## Precision
0

## Ordered Values
False

## Sort Order
UNSORTED

## Parent Names


## Extended Properties
{}

## Additional Properties
{}

## Data Dictionaries


## Data Structures




___




# Update Data Field

## Data Field Name 

AngleLeft

## GUID
9f525f95-646f-4abf-874d-5de0b131a9ce

## Qualified Name
DataField::AngleLeft

## Description
Angle rotation of the left leg from vertical

## In Data Structure
DataStruct::TBDF-Incoming Weekly Measurement Data

## Assigned Meanings


## Data Type
Integer

## Data Class


## Is Nullable
True

## Minimum Length
0

## Length
0

## Precision
0

## Ordered Values
False

## Sort Order
UNSORTED

## Parent Names


## Extended Properties
{}

## Additional Properties
{}

## Data Dictionaries


## Data Structures




___




# Update Data Field

## Data Field Name 

AngleRight

## GUID
9c6d96f2-724b-4109-b513-f978d911fe34

## Qualified Name
DataField::AngleRight

## Description
Angle rotation of the left leg from vertical

## In Data Structure
DataStruct::TBDF-Incoming Weekly Measurement Data

## Assigned Meanings


## Data Type
Integer

## Data Class


## Is Nullable
True

## Minimum Length
0

## Length
0

## Precision
0

## Ordered Values
False

## Sort Order
UNSORTED

## Parent Names


## Extended Properties
{}

## Additional Properties
{}

## Data Dictionaries


## Data Structures




___




# Update Data Field

## Data Field Name 

HospitalId

## GUID
7f33b0a5-fe31-4fd3-a7ec-90dd7520cfa8

## Qualified Name
DataField::HospitalId

## Description
Unique identifier for a hospital. Used in forming PatientId.

## Assigned Meanings


## Data Type
String

## Data Class


## Is Nullable
False

## Minimum Length
0

## Length
0

## Precision
0

## Ordered Values
False

## Sort Order
UNSORTED

## Parent Names
DataField::PatientId

## Extended Properties
{}

## Additional Properties
{}

## Data Dictionaries


## Data Structures




___




# Update Data Field

## Data Field Name 

PatientNumber

## GUID
ed77dfa2-67ee-48b9-b724-515d54673653

## Qualified Name
DataField::PatientNumber

## Description
Unique identifier of the patient within a hospital.

## Assigned Meanings


## Data Type
String

## Data Class


## Is Nullable
False

## Minimum Length
0

## Length
0

## Precision
0

## Ordered Values
False

## Sort Order
UNSORTED

## Parent Names
DataField::PatientId

## Extended Properties
{}

## Additional Properties
{}

## Data Dictionaries


## Data Structures




___


# REPORTING
We can also use Dr.Egeria Commands to report on the Data Structures and Data Fields that we just created. Here
we request a simplified list form of the output.
___

# View Data Structures
## Output Format
LIST
___


# View Data Fields
## Output Format
LIST

___

# View Data Structures
## Output Format
REPORT
___

# View Data Fields
## Output Format
REPORT

___

# Building on what we have done
In this sample we have successfully extended our data design wtih relationships and technical details. We've also shown more extensive reporting on what we've accomplished.

## Next Steps
In our next step we will introduce Data Dictionaries and Data Specifications - both useful forms of collecting information for easy use and re-use.

# Provenance

* Results from processing file dr_egeria_data_designer_1.md on 2025-06-25 01:39
