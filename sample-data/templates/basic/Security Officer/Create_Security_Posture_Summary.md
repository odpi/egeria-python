___

## Create Security Posture Summary
> The summary of one security test run: findings by severity, resources in scope and tested, and new and resolved findings.

### Display Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The common name of an element.

>	**Alternative Labels**: "Term Name"


### Survey Report
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The survey report for the test run this belongs to. Linked with a ReportedAnnotation relationship.


### Summary
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A short summary of the element's meaning or purpose.


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Category
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A user-defined category for the element, used to group related elements for display or search purposes.

>	**Alternative Labels**: Category Name


### Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


### Legal
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Copyright and/or license information for the element or associated resource.


### Qualified Name
>	**Input Required**: False

>	**Attribute Type**: QN

>	**Description**: The unique, text name of an element.


### Content Status
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: The lifecycle status of an element.

>	**Valid Values**: DRAFT,PREPARED,PROPOSED,APPROVED,REJECTED,ACTIVE,DEPRECATED,OTHER

>	**Default Value**: ACTIVE


### Search Keywords
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: A list of search keywords.


### GUID
>	**Input Required**: False

>	**Attribute Type**: GUID

>	**Description**: A unique identifier - typically of an element in this context.

>	**Alternative Labels**: guid; Guid


### URL
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: URL for further information.


### Version Identifier
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The version of the element

>	**Alternative Labels**: Version

>	**Default Value**: 1.0


### Authors
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: The authors.


### Finding Counts By Severity
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: Number of findings at each severity, one 'severity: count' pair per line (or a JSON object).

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


### Resources In Scope Count
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: Number of resources in scope for the run.


### Resources Tested Count
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: Number of resources the run tested.


### New Finding Count
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: Findings seen for the first time in this run.


### Resolved Finding Count
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: Findings from earlier runs that are no longer detected.


___
