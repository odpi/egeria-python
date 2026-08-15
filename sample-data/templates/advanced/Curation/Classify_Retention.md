___

## Classify Retention
> Classify an existing element with the Retention classification (0422), indicating the retention policy for the element/resource.

### Target Element
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: Qualified name of the existing element being classified or linked.


### Level Identifier
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: Numeric, org-defined severity/level (0422 GovernanceClassificationBase.levelIdentifier) used by Impact, Confidence, Confidentiality, Criticality, and Retention classifications.


### Retention Basis
>	**Input Required**: False

>	**Attribute Type**: Enum

>	**Description**: Policy basis governing how long the element/resource is retained (0422 RetentionBasis enum) — confirm exact enum values against the type definition before finalizing.


### Archive After
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Date after which the retained element/resource should be archived (0422 Retention classification).


### Delete After
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Date after which the retained element/resource should be deleted (0422 Retention classification).


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


### Governance Status
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: Status of a governance classification assignment, looked up from the statusIdentifier valid value set. Accepts the current display name or a preferred-value integer.

>	**Valid Values**: Discovered,Proposed,Imported,Validated,Deprecated,Obsolete,Other

>	**Default Value**: Validated


### Effective From
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The beginning of when an element is viewable.


### Effective Time
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The time at which an element must be effective in order to be returned by the request.


### Effective To
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The ending time at which an element is visible.


### External Source GUID
>	**Input Required**: False

>	**Attribute Type**: GUID

>	**Description**: The unique identifier of an external source.


### External Source Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The name of an external source


### For Duplicate Processing
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Flag indicating if the request is to support duplicate processing.


### For Lineage
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Flag indicating if the request is to support lineage.


### Request ID
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A user provided or system generated request id for a conversation.


### Steward
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The identifier of the steward responsible for the element.


### Source
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The source of the information.


___
