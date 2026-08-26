___

## Classify Impact
> Classify an existing element with the Impact classification (0422), indicating the level of impact an event/issue described by the element will have on the organization.

### Target Element
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: Qualified name of the existing element being classified or linked.


### Level Identifier
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: Numeric, org-defined severity/level (0422 GovernanceClassificationBase.levelIdentifier) used by Impact, Confidence, Confidentiality, Criticality, and Retention classifications.


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


___
