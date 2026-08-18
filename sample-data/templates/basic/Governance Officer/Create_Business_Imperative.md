___

## Create Business Imperative
> The BusinessImperative entity defines a business goal that is critical to the success of the organization.

### Display Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The common name of an element.

>	**Alternative Labels**: "Term Name"


### Domain Identifier
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: The governance domain, looked up from the domainIdentifier valid value set (deployments may extend this set without rebuilding Egeria). All domains is "All Domains". Accepts either the current display name or a preferred-value integer; old-style ALL_CAPS enum names (e.g. IT_INFRASTRUCTURE) are still accepted for backward compatibility.

>	**Valid Values**: All Domains,Data,Privacy,Security,IT Infrastructure,Software Development,Corporate,Asset Management,Other

>	**Default Value**: All Domains


### Implications
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: List of implications.


### Importance
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Importance of the definition.


### Outcomes
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: List of desired outcomes.


### Results
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: A list of expected results.


### Summary
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A short summary of the element's meaning or purpose.


### Usage
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The usage guidance for this element — how it is intended to be used in context.


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


### Scope
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Scope of the definition or element.


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


___
