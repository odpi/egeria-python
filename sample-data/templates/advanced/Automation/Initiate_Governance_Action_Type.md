___

## Initiate Governance Action Type
> Run a single governance action type: Egeria starts one engine action for it, passing the Action Targets and Request Parameters to its governance service.

### Governance Action Type
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The governance action type, identified by its qualified name, display name or GUID.

>	**Alternative Labels**: Action Type


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Action Targets
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: Elements passed to the governance service(s), one 'action target name: element' pair per line; each element is a qualified name, display name or GUID.

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


### Request Parameters
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: Name: value parameters passed to the governance service(s) that run.

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


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


### Request Source Elements
>	**Input Required**: False

>	**Attribute Type**: Reference Name List

>	**Description**: Elements that caused or requested the action.


___
