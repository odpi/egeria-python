___

## Initiate Survey
> Run a survey of a resource. The action target name the survey expects is read from the survey type; set Action Target Name only to override it.

### Survey Type
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The survey to run: the qualified name of its governance action type, e.g. PostgreSQLSurvey::survey-postgres-database or FileSurvey::survey-folder.


### Resource to Survey
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The element describing the resource to survey (a server, database, folder, file, ...).


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Action Target Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The name an element is given when it is passed as an action target to a governance service.


### Request Parameters
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: Name: value parameters passed to the governance service(s) that run.

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


___
