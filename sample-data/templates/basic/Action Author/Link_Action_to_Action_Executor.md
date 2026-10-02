___

## Link Action to Action Executor
> Links a governance action type to a governance engine, defining which engine executes it and how (request type, request parameters, and target/parameter filtering and renaming).

### Governance Action Type
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The governance action type, identified by its qualified name, display name or GUID.

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

>	**Description**: Name: value parameters passed to the governance service(s) that run.

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


___
