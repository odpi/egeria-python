___

## Reclassify Confidence
> Update the Confidence classification (0422) already applied to an element.

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

>	**Description**: Status of a governance classification assignment.

>	**Valid Values**: PROPOSED,VALIDATED,DEPRECATED,OBSOLETE,OTHER

>	**Default Value**: VALIDATED


___
