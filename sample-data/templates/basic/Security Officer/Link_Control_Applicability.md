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


___
