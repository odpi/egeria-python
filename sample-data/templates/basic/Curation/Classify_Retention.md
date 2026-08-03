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

>	**Description**: Status of a governance classification assignment.

>	**Valid Values**: PROPOSED,VALIDATED,DEPRECATED,OBSOLETE,OTHER

>	**Default Value**: VALIDATED


___
