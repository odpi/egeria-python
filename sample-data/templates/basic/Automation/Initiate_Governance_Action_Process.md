___

## Initiate Governance Action Process
> Run a governance action process: Egeria uses the process as a template and starts its chain of engine actions. Action Targets and Request Parameters are passed to the first step.

### Governance Action Process
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The governance action process, identified by its qualified name, display name or GUID.


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
