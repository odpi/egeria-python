___

## Link Report Run Of
> Link a results set to the report it is a run of, with the run's result state (ReportRunOf relationship: ResultsSet -> Report).

### Results Set
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: A results set (collection) name. Preferably a qualified name.


### Report
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: A report name. Preferably a qualified name.


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


### Result State
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: Status of the results of this report run. Validated against Egeria's valid metadata values for resultState.


### Result State Reason
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: Reason for the result state. Validated against Egeria's valid metadata values for resultStateReason.


### Result Location
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Where the results of this run are stored.


___
