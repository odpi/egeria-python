___

## Link First Process Step
> Links a governance action process to its first governance action process step, so processing begins there when the process is triggered. There can be only one first process step per process.

### Governance Action Process
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The governance action process to link.


### Governance Action Process Step
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The governance action process step to link.


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


### Guard
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Informational value passed to the process step; the step's behaviour may vary depending on the guard it receives.


### Request Parameters
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: Parameters to pass to the governance service when this step executes.

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


___
