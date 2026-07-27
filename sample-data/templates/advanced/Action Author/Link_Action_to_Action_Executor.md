___

## Link Action to Action Executor
> Links a governance action type to a governance engine, defining which engine executes it and how (request type, request parameters, and target/parameter filtering and renaming).

### Governance Action Type
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The governance action type to link to a governance engine executor.

>	**Alternative Labels**: Action Type


### Governance Engine
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The governance engine that will execute the linked governance action type.


### Label
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A label used to identify or categorise a relationship link.

>	**Alternative Labels**: Wire Label


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


### Request Type
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The request type the executing governance engine uses to identify the governance service to run.


### Request Parameters
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: Parameters to pass to the governance service when this step executes.

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


### Anchor Scope IDs
>	**Input Required**: False

>	**Attribute Type**: Reference Name List

>	**Description**: A list of IDs that are anchor scopes for this element.


### Make Anchor
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Is the element at end2 an anchor to end1?

>	**Default Value**: false


### Request Parameter Filter
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Names of request parameters to remove before they are passed to the governance engine.


### Request Parameter Map
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: Map to override the name that a request parameter is passed as to the governance engine.

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


### Action Target Filter
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Names of action targets to remove before they are passed to the governance engine.


### Action Target Map
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: Map to override the name that an action target is passed as to the governance engine.

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


___
