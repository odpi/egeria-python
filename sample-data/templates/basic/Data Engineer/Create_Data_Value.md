___

## Create Data Value
> Create or update a Data Value (Egeria 6.4): a value used or produced by processing, with its format, type, length and fingerprints. A Literal Value, Literal Value List or Literal Value Map makes it a LiteralDataValue that carries the value itself. Needs Egeria 6.4.

### Display Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The common name of an element.

>	**Alternative Labels**: "Term Name"


### Data Format
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The format of the data value (e.g. JSON, CSV, ISO 8601).


### Length
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: The maximum number of characters or digits allowed in the field, or the length of a data value.


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


### Fingerprint
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A fingerprint of the data value, for spotting copies.


### Fingerprint Algorithm
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The algorithm that produced the Fingerprint.


### Hash
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: A hash of the data value (a whole number).


### Hash Algorithm
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The algorithm that produced the Hash.


### Literal Value
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The value itself, as text. Giving a Literal Value, Literal Value List or Literal Value Map makes this a LiteralDataValue.


### Literal Value List
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: The value as a list of text values, one per line or comma separated. Makes this a LiteralDataValue.


### Literal Value Map
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: The value as name: value pairs, one per line. Makes this a LiteralDataValue.

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


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


### Search Keywords
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: A list of search keywords.


### Zone Membership
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Zones scope visibility of elements to different users.


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


___
