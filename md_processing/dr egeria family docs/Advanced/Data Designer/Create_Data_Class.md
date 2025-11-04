# Create Data Class
>	Describes the data values that may be stored in data fields. Can be used to configure quality validators and data field classifiers.

## Display Name
>	**Input Required**: True

>	**Description**: Name of the data structure.

>	**Alternative Labels**: Data Class; Display Name; Name; Data Class Name


## Description
>	**Input Required**: False

>	**Description**: A description of the data class.


## Namespace
>	**Input Required**: False

>	**Description**: Optional namespace that scopes the field.


## Match Property Names
>	**Input Required**: False

>	**Description**: Names of the properties that are set.

>	**Default Value**: Can be determined by Dr. Egeria?


## Match Threshold
>	**Input Required**: False

>	**Description**: Percent of values that must match the data class specification.


## IsCaseSensitive
>	**Input Required**: False

>	**Description**: Are field values case sensitive?

>	**Default Value**: False


## Specification
>	**Input Required**: False

>	**Description**: Rules language


## Specification Details
>	**Input Required**: False

>	**Description**: Values for a rule.


## Data Type
>	**Input Required**: True

>	**Description**: Data type for the data class.

>	**Valid Values**: string; int; long; date; boolean; char; byte; float; double; biginteger; bigdecimal; array<string>; array<int>; map<string,string>; map<string, boolean>; map<string, int>; map<string, long>; map<string,double>; map<string, date> map<string, object>; short; map<string, array<string>>; other


## Allow Duplicate Values
>	**Input Required**: False

>	**Description**: Allow duplicate values within the data class?

>	**Default Value**: true


## isNullable
>	**Input Required**: False

>	**Description**: Can the values within the dataclass be absent?

>	**Alternative Labels**: Nullable

>	**Default Value**: true


## isCaseSensitive
>	**Input Required**: False

>	**Description**: Indicates if the values in a  data class are case sensitive.

>	**Alternative Labels**: Case Sensitive


## Default Value
>	**Input Required**: False

>	**Description**: Specify a default value for the data class.

>	**Alternative Labels**: Default


## Average Value
>	**Input Required**: False

>	**Description**: Average value for the data class.

>	**Alternative Labels**: Average


## Value List
>	**Input Required**: False

>	**Description**: 


## Value Range From
>	**Input Required**: False

>	**Description**: Beginning range of legal values.

>	**Alternative Labels**: Range From


## Value Range To
>	**Input Required**: False

>	**Description**: End of valid range for value.

>	**Alternative Labels**: Range To


## Sample Values
>	**Input Required**: False

>	**Description**: Sample values of the data class.

>	**Alternative Labels**: Samples


## Data Patterns
>	**Input Required**: False

>	**Description**: prescribed format of a data field - e.g. credit card numbers. Often expressed as a regular expression.


## In Data Dictionary
>	**Input Required**: False

>	**Description**: What data dictionaries is this data field in?


## Containing Data Class
>	**Input Required**: False

>	**Description**: Data classes this is part of.

>	**Alternative Labels**: Containing Class


## Specializes Data Class
>	**Input Required**: False

>	**Description**: Specializes a parent  data class.


## User Defined Status
>	**Input Required**: False

>	**Description**: Only valid if Product Status is set to OTHER. User defined & managed status values.


## Category
>	**Input Required**: False

>	**Description**: A user specified category name that can be used for example, to define product types or agreement types.

>	**Alternative Labels**: Category Name


## Version Identifier
>	**Input Required**: False

>	**Description**: Published product version identifier.

>	**Default Value**: 1.0


## URL
>	**Input Required**: False

>	**Description**: Link to supporting information


## Identifier
>	**Input Required**: False

>	**Description**: role identifier


## Classifications
>	**Input Required**: false

>	**Description**: Optionally specify the initial classifications for a collection. Multiple classifications can be specified. 

>	**Alternative Labels**: classification


## Is Own Anchor
>	**Input Required**: False

>	**Description**: Generally True. 

>	**Alternative Labels**: Own Anchor

>	**Default Value**: True


## Anchor ID
>	**Input Required**: False

>	**Description**: Anchor identity for the collection. Typically a qualified name but if display name is unique then it could be used (not recommended)


## Parent ID
>	**Input Required**: False

>	**Description**: Unique name of the parent element.

>	**Alternative Labels**: Parent;


## Parent Relationship Type Name
>	**Input Required**: False

>	**Description**: The kind of the relationship to the parent element.


## Anchor Scope Name
>	**Input Required**: False

>	**Description**: Optional qualified name of an anchor scope.


## Parent at End1
>	**Input Required**: False

>	**Description**: Is the parent at end1 of the relationship?

>	**Default Value**: True


## Qualified Name
>	**Input Required**: False

>	**Description**: A unique qualified name for the element. Generated using the qualified name pattern  if not user specified.


## GUID
>	**Input Required**: False

>	**Description**: A system generated unique identifier.

>	**Alternative Labels**: Guid; guid


## Effective Time
>	**Input Required**: False

>	**Description**: An ISO-8601 string representing the time to use for evaluating effectivity of the elements related to this one.


## Effective From
>	**Input Required**: False

>	**Description**: A string in ISO-8601 format that defines the when an element becomes effective (visible).


## Effective To
>	**Input Required**: False

>	**Description**: A string in ISO-8601 format that defines the when an element is no longer effective (visible).


## Merge Update
>	**Input Required**: False

>	**Description**: If True, only those attributes specified in the update will be updated; If False, any attributes not provided during the update will be set to None.

>	**Alternative Labels**: Merge

>	**Default Value**: True


## Additional Properties
>	**Input Required**: False

>	**Description**: Additional user defined values organized as name value pairs in a dictionary.


## External Source GUID
>	**Input Required**: False

>	**Description**: Identifier of an external source that is associated with this element.


## External Source Name
>	**Input Required**: False

>	**Description**: Name of an external element that is associated with this element.


## Journal Entry
>	**Input Required**: False

>	**Description**: 


## URL
>	**Input Required**: False

>	**Description**: Link to supporting information


## Search Keywords
>	**Input Required**: False

>	**Description**: Keywords to facilitate finding the element


## Supplementary Properties
>	**Input Required**: False

>	**Description**: Provide supplementary information to the element using the structure of a glossary term

