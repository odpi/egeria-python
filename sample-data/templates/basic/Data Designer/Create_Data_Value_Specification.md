___

## Create Data Value Specification
> Creates or updates a data value classification which represents the characteristics of a data value. DataClass and DataGrain are subtypes.

### Display Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The common name of an element.

>	**Alternative Labels**: "Term Name"


### Absolute Uncertainty
>	**Input Required**: False

>	**Attribute Type**: Simple Float

>	**Description**: The absolute margin of error for numeric values in this data value specification (in the same units as the value).


### Data Type
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The data type of the field or value specification (e.g. string, int, date, boolean).

>	**Valid Values**: string,int,long,date,boolean,char,byte,float,double,biginteger,bigdecimal,array<string>,array<int>,map<string,string>,map<string,boolean>,map<string,int>,map<string,long>,map<string,double>,map<string,date>,map<string,object>,short,map<string,array<string>>,other

>	**Default Value**: string


### In Data Value Specification
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The data value specification that this element is a sub-specification of (DataValueHierarchy relationship).

>	**Alternative Labels**: In Data Class; In Data Grain


### Match Property Names
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: The names of the properties used when matching values against this data value specification.


### Match Threshold
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: The confidence threshold (0-100) required for a value to be considered a match for this data value specification.


### Name Patterns
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Name patterns for naming standard rules.


### Namespace Path
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The namespace path that qualifies the element's name within a larger naming hierarchy.


### Relative Uncertainty
>	**Input Required**: False

>	**Attribute Type**: Simple Float

>	**Description**: The relative margin of error for values in this data value specification, expressed as a percentage (0-100).


### Specializes Data Value Specification
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The parent data value specification that this one specializes or refines.


### Specification
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A formal or technical specification string that describes the valid values or format for this data value specification.


### Specification Details
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: Additional key-value details that extend the formal specification for this data value specification.

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


### Units
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The unit of measure for numeric values in this field or specification (e.g. metres, kg, USD).


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Category
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A user-defined category for the element, used to group related elements for display or search purposes.

>	**Alternative Labels**: Category Name


### Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


### Qualified Name
>	**Input Required**: False

>	**Attribute Type**: QN

>	**Description**: The unique, text name of an element.


### Content Status
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: The lifecycle status of an element.

>	**Valid Values**: DRAFT,PREPARED,PROPOSED,APPROVED,REJECTED,ACTIVE,DEPRECATED,OTHER

>	**Default Value**: ACTIVE


### Search Keywords
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: A list of search keywords.


### GUID
>	**Input Required**: False

>	**Attribute Type**: GUID

>	**Description**: A unique identifier - typically of an element in this context.

>	**Alternative Labels**: guid; Guid


### URL
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: URL for further information.


### Version Identifier
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The version of the element

>	**Alternative Labels**: Version

>	**Default Value**: 1.0


### Authors
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: The authors.


___
