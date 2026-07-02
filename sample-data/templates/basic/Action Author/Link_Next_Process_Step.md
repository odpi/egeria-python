___

## Link Next Process Step
> Links two governance action process steps together, defining the flow from one step to the next.

### Governance Action Process Step
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The governance action process step to link.


### Next Governance Action Process Step
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The next governance action process step in the flow.


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


### Mandatory Guard
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Whether this guard must be present for the step to be actioned.

>	**Default Value**: false


### Guard
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Informational value passed to the process step; the step's behaviour may vary depending on the guard it receives.


___
