___

## Create Reference Data Set
> Creates or updates a reference data set -- a named list of allowed values, such as order statuses or country codes. Members can be linked (Members), created inline one per line (Values), or created with their own properties from a table (Value Table).

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


### Members
>	**Input Required**: False

>	**Attribute Type**: Reference Name List

>	**Description**: Existing values that belong to this set, one per line or comma-separated. Each is linked as a member (ValidValueMember). On a re-run, a value no longer listed is unlinked, not deleted.


### Values
>	**Input Required**: False

>	**Attribute Type**: Line List

>	**Description**: Member values to create and link, one per line. Commas are part of the value. Each value's qualified name is the set's qualified name plus '::' and the value, so a re-run reuses it. Ordinal follows list position.


### Value Table
>	**Input Required**: False

>	**Attribute Type**: Table

>	**Description**: Member values to create or update and link, as a markdown table with a header row. Columns: Value (required), Display Name, Description, Usage, Data Type, Is Case Sensitive, Default, Ordinal. Use \| for a literal pipe.


### Default Member
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Which entry in Values is the set's default (match on the value).


___
