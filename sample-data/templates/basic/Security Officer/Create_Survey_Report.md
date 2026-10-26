___

## Create Survey Report
> A survey report catalogues one run of an analysis, such as a vulnerability scan or penetration test. Category says what kind of test it was, for example Penetration Test Results.

### Display Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The common name of an element.

>	**Alternative Labels**: "Term Name"


### Start Time
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Date/time (ISO 8601) that the work started - for a promise, work on delivering the promised resource; for a report, the run that produced it.


### Completion Time
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Date/time (ISO 8601) that the work finished - for a promise, when the promised resource was delivered; for a report, when the run completed.


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


### Purpose
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The purpose of this collection — a short description of why it exists or what it is used for.


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


### Report Subjects
>	**Input Required**: False

>	**Attribute Type**: Reference Name List

>	**Description**: The assets or other elements that the run tested. Each is linked with a ReportSubject relationship.


___
