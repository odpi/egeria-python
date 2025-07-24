# **Create Data Class**
>	Describes the data values that may be stored in data fields. Can be used to configure quality validators and data field classifiers.

## **Display Name**
>	**Input Required**: True

>	**Description**: Name of the data structure.

>	**Alternative Labels**: Data Class; Display Name; Name; Data Class Name


## **Description**
>	**Input Required**: False

>	**Description**: A description of the data class.


## **Namespace**
>	**Input Required**: False

>	**Description**: Optional namespace that scopes the field.


## **Match Property Names**
>	**Input Required**: False

>	**Description**: Names of the properties that are set.

>	**Default Value**: Can be determined by Dr. Egeria?


## **Match Threshold**
>	**Input Required**: False

>	**Description**: Percent of values that must match the data class specification.


## **IsCaseSensitive**
>	**Input Required**: False

>	**Description**: Are field values case sensitive?

>	**Default Value**: False


## **Data Type**
>	**Input Required**: True

>	**Description**: Data type for the data class.

>	**Valid Values**: string; int; long; date; boolean; char; byte; float; double; biginteger; bigdecimal; array<string>; array<int>; map<string,string>; map<string, boolean>; map<string, int>; map<string, long>; map<string,double>; map<string, date> map<string, object>; short; map<string, array<string>>; other


## **Allow Duplicate Values**
>	**Input Required**: False

>	**Description**: Allow duplicate values within the data class?

>	**Default Value**: true


## **isNullable**
>	**Input Required**: False

>	**Description**: Can the values within the dataclass be absent?

>	**Alternative Labels**: Nullable

>	**Default Value**: true


## **isCaseSensitive**
>	**Input Required**: False

>	**Description**: Indicates if the values in a  data class are case sensitive.

>	**Alternative Labels**: Case Sensitive


## **Default Value**
>	**Input Required**: False

>	**Description**: Specify a default value for the data class.

>	**Alternative Labels**: Default


## **Average Value**
>	**Input Required**: False

>	**Description**: Average value for the data class.

>	**Alternative Labels**: Average


## **Value List**
>	**Input Required**: False

>	**Description**: 


## **Value Range From**
>	**Input Required**: False

>	**Description**: Beginning range of legal values.

>	**Alternative Labels**: Range From


## **Value Range To**
>	**Input Required**: False

>	**Description**: End of valid range for value.

>	**Alternative Labels**: Range To


## **Sample Values**
>	**Input Required**: False

>	**Description**: Sample values of the data class.

>	**Alternative Labels**: Samples


## **Data Patterns**
>	**Input Required**: False

>	**Description**: prescribed format of a data field - e.g. credit card numbers. Often expressed as a regular expression.


## **In Data Dictionary**
>	**Input Required**: False

>	**Description**: What data dictionaries is this data field in?


## **Containing Data Class**
>	**Input Required**: False

>	**Description**: Data classes this is part of.

>	**Alternative Labels**: Containing Class


## **Specializes Data Class**
>	**Input Required**: False

>	**Description**: Specializes a parent  data class.


## **Qualified Name**
>	**Input Required**: False

>	**Description**: A unique qualified name for the element. Generated using the qualified name pattern  if not user specified.


## **GUID**
>	**Input Required**: False

>	**Description**: A system generated unique identifier.

>	**Alternative Labels**: Guid; guid

