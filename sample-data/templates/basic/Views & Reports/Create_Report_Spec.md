___

## Create Report Spec
> Creates or updates a report specification held in Egeria (ReportSpec, a ReportType collection): its micro-flow, target type, aliases and output types.

### Display Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The common name of an element.

>	**Alternative Labels**: "Term Name"


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


### Purpose
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The purpose of this collection — a short description of why it exists or what it is used for.


### Aliases
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Alternative names for this  field, used in different systems or contexts.

>	**Alternative Labels**: Alias


### Search Keywords
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: A list of search keywords.


### Zone Membership
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Zones scope visibility of elements to different users.


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


### Microflow
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The report spec's micro-flow, parameters and formatters, as microflow/1 JSON: {"format": "microflow/1", "params": {name: {type, default, required}}, "stages": [...], "formatters": {OUTPUT_TYPE: {"columns": [...]}}}. A find stage names its method as Class.method (read-only: find_, get_ or list_); an analytic stage names a registered analytic. A bare JSON list of stages (the older format 0) is accepted and converted to microflow/1 when written. Invalid JSON is an error.


### Target Type Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The type of element the report spec reports on.


### Output Types
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: The output formats that can be generated from this report spec.


### Include Preamble
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Should the preamble be included in the report?

>	**Default Value**: false


___
