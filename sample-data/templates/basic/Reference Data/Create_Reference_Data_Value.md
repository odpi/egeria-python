___

## Create Reference Data Value
> Creates or updates a single reference data value, optionally adding it to a reference data set.

### Display Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The common name of an element.

>	**Alternative Labels**: "Term Name"


### Preferred Value
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The preferred value -- the value itself, as stored and exchanged. For Setup/Clear Valid Metadata commands, the value being set up for the property (or map name/value); required there unless a Metadata Value Table is given.


### Data Type
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The data type of the field or value specification (e.g. string, int, date, boolean).

>	**Valid Values**: string,int,long,date,boolean,char,byte,float,double,biginteger,bigdecimal,array<string>,array<int>,map<string,string>,map<string,boolean>,map<string,int>,map<string,long>,map<string,double>,map<string,date>,map<string,object>,short,map<string,array<string>>,other

>	**Default Value**: string


### Usage
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The usage guidance for this element — how it is intended to be used in context.


### Namespace Path
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The namespace path that qualifies the element's name within a larger naming hierarchy.


### Is Case Sensitive
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: If true, values for this data class or field are case-sensitive.

>	**Default Value**: false


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


### Legal
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Copyright and/or license information for the element or associated resource.


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


### Scope
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Scope of the definition or element.


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


### In Reference Data Set
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The reference data set this value belongs to. Links the value as a member of the set (ValidValueMember).


### Is Default Member
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: If true, this value is the set's default (isDefaultValue on the ValidValueMember relationship).

>	**Default Value**: false


### Member Ordinal
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: Position of the value within the set (ordinal on the ValidValueMember relationship).

>	**Default Value**: 0


___
