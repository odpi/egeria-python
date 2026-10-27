___

## Link Control Applicability
> Record whether a control applies to a statement of applicability, why, and how far it is implemented. Linking a control that is already linked updates its applicability.

### Statement of Applicability
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The statement of applicability the control is assessed in.


### Control
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The governance definition describing the control being assessed - typically a GovernanceControl from a standard.


### Label
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A label used to identify or categorise a relationship link.

>	**Alternative Labels**: Wire Label


### Implementation Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Describes how this governance control is implemented.

>	**Alternative Labels**: Implementation


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


### Is Applicable
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Whether the control applies. Egeria treats a control as applicable unless this is false.


### Justification
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Why the control is included or excluded.


### Inclusion Reasons
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Why the control is included. Suggested values: Risk Treatment, Legal or Regulatory Requirement, Contractual Obligation, Business Requirement, Best Practice.


### Implementation Status
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: How far the control has been implemented. Egeria defaults a new link to NOT_STARTED.

>	**Valid Values**: NOT_STARTED,PLANNED,PARTIALLY_IMPLEMENTED,IMPLEMENTED,OTHER


### Review Date
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: When the statement, or this control's applicability, was last reviewed.


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


### Anchor Scope IDs
>	**Input Required**: False

>	**Attribute Type**: Reference Name List

>	**Description**: A list of IDs that are anchor scopes for this element.


### Make Anchor
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Is the element at end2 an anchor to end1?

>	**Default Value**: false


### Merge Update
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: A flag indicating if the update should be a merge or replace.

>	**Alternative Labels**: isMergeUpdate

>	**Default Value**: true


___
