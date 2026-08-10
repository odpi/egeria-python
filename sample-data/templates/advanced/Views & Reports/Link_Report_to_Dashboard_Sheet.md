___

## Link Report to Dashboard Sheet

### Dashboard Sheet Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The unique name of a Dashboard Sheet — a local pyegeria-managed record (planned to become a Collection subtype in Egeria; see Container/ContainerDict in pyegeria.view._output_container_models for the current pre-Egeria model). Used both to define a new Dashboard Sheet's identity (Create Dashboard Sheet) and to reference an existing one (Link Report to Dashboard Sheet).


### Report Name
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The name of a report asset.

>	**Default Value**: Referenceable


### Placement Emphasis
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: Presentation hint for a Report Spec placed in a Dashboard Sheet — 'kpi' (compact tile) or 'panel' (larger, detailed).

>	**Valid Values**: kpi,panel

>	**Default Value**: kpi


### Placement Span
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: Layout width hint for a Report Spec placed in a Dashboard Sheet — '1'/'2' (relative columns) or 'full' (row width).

>	**Valid Values**: 1,2,full

>	**Default Value**: 1


### Effective Time
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: An ISO-8601 string representing the time to use for evaluating effectivity of the elements related to this one.


### Effective From
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A string in ISO-8601 format that defines the when an element becomes effective (visible).


### Effective To
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A string in ISO-8601 format that defines the when an element is no longer effective (visible).


___
