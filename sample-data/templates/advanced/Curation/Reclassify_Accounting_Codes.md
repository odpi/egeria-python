___

## Reclassify Accounting Codes
> Replace the Accounting Codes classification (0715) already applied to an element.

### Target Element
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: Qualified name of the existing element being classified or linked.


### Accounting Code
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The single accounting code for the element (0715 AccountingCodes classification).


### Accounting Code List
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: List of accounting codes for the element; accountingCode holds the primary/default value if multiple codes are used (0715 AccountingCodes classification).


### Accounting Code Map
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: Map of name-to-accounting-code mappings for the element (0715 AccountingCodes classification).

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


### Effective From
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The beginning of when an element is viewable.


### Effective Time
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The time at which an element must be effective in order to be returned by the request.


### Effective To
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The ending time at which an element is visible.


### External Source GUID
>	**Input Required**: False

>	**Attribute Type**: GUID

>	**Description**: The unique identifier of an external source.


### External Source Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The name of an external source


### For Duplicate Processing
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Flag indicating if the request is to support duplicate processing.


### For Lineage
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Flag indicating if the request is to support lineage.


### Request ID
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A user provided or system generated request id for a conversation.


___
