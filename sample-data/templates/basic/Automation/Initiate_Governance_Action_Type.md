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


___
