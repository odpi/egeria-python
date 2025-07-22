# **Create Data Field**
>	A data field is a fundamental building block for a data structure.

## **Display Name**
>	**Input Required**: True

>	**Description**: Name of the Data Field

>	**Alternative Labels**: Name; Data Field Name


## **Description**
>	**Input Required**: False

>	**Description**: A description of the Data Field


## **Data Type**
>	**Input Required**: True

>	**Description**: The data type of the data field. Point to data type valid value list if exists.

>	**Valid Values**: string; int; long; date; boolean; char; byte; float; double; biginteger; bigdecimal; array<string>; array<int>; map<string,string>; map<string, boolean>; map<string, int>; map<string, long>; map<string,double>; map<string, date> map<string, object>; short; map<string, array<string>>; other

>	**Default Value**: string


## **Position**
>	**Input Required**: False

>	**Description**: Position of the data field in the data structure. If 0, position is irrelevant.

>	**Default Value**: 0


## **Minimum Cardinality**
>	**Input Required**: False

>	**Description**: The minimum cardinality for a data element.

>	**Alternative Labels**: Min Cardinality; min cardinality

>	**Default Value**: 1


## **Maximum Cardinality**
>	**Input Required**: False

>	**Description**: The maximum cardinality for a data element.

>	**Alternative Labels**: max cardinality; Max Cardinality

>	**Default Value**: 1


## **In Data Structure**
>	**Input Required**: False

>	**Description**: The data structure this field is a member of. If display name is not unique, use qualified name.

>	**Alternative Labels**: Data Structure


## **Data Class**
>	**Input Required**: False

>	**Description**: The data class that values of this data field conform to.


## **Glossary Term**
>	**Input Required**: False

>	**Description**: Term that provides meaning to this field.

>	**Alternative Labels**: Term


## **isNullable**
>	**Input Required**: False

>	**Description**: Can the values within the dataclass be absent?

>	**Alternative Labels**: Nullable

>	**Default Value**: true


## **Minimum Length**
>	**Input Required**: False

>	**Description**: 

>	**Alternative Labels**: Min Length


## **Length**
>	**Input Required**: False

>	**Description**: The length of a value for a field.


## **Precision**
>	**Input Required**: False

>	**Description**: The precision of a numeric


## **Ordered Values**
>	**Input Required**: False

>	**Description**: is this field in an ordered list?


## **Units**
>	**Input Required**: False

>	**Description**: An optional string indicating the units of the field.

>	**Alternative Labels**: gradians


## **Default Value**
>	**Input Required**: False

>	**Description**: Specify a default value for the data class.

>	**Alternative Labels**: Default


## **Version Identifier**
>	**Input Required**: False

>	**Description**: A user supplied version identifier.


## **In Data Dictionary**
>	**Input Required**: False

>	**Description**: What data dictionaries is this data field in?


## **Parent Data Field**
>	**Input Required**: False

>	**Description**: Optional parent field if this is a nested field.

>	**Alternative Labels**: Parent Field


## **Qualified Name**
>	**Input Required**: False

>	**Description**: A unique qualified name for the element. Generated using the qualified name pattern  if not user specified.


## **GUID**
>	**Input Required**: False

>	**Description**: A system generated unique identifier.

>	**Alternative Labels**: Guid; guid

