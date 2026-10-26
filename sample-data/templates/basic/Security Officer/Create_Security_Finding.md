___

## Create Security Finding
> A security finding from a test run that is neither a known vulnerability nor a penetration test finding, such as an insecure configuration.

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


### Severity
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: The CVSS severity rating of the finding.

>	**Valid Values**: None,Low,Medium,High,Critical


### CVSS Score
>	**Input Required**: False

>	**Attribute Type**: Simple Float

>	**Description**: CVSS base score, 0.0 to 10.0.


### Vulnerability Identifiers
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Identifiers of the vulnerability, such as CVE identifiers.


### Weakness Identifiers
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Identifiers of the weakness, such as CWE identifiers.


### Affected Location
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Where the finding is: host and port, URL, file path or package.


### Evidence
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: What demonstrated the finding, such as the request and response.


### Remediation
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The recommended fix.


### Exploit Available
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Whether an exploit is publicly available.


### Affected Elements
>	**Input Required**: False

>	**Attribute Type**: Reference Name List

>	**Description**: Catalogued elements the finding affects - the tested asset, and any catalogued element at the affected location or among the compromised resources. Each is linked with an AssociatedAnnotation relationship.


### Previous Finding
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The same finding in an earlier run. Linked with an AnnotationExtension relationship.


___
