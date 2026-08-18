___

## Link Lineage Relationship
> Create a lineage relationship (DataFlow, ControlFlow, ProcessCall, LineageMapping, DataMapping, UltimateSource, or UltimateDestination) between two elements, e.g. to trace how data moves through a pipeline.

### Element One
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: Qualified name, display name, or GUID of the element at end one of the lineage relationship.


### Element Two
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: Qualified name, display name, or GUID of the element at end two of the lineage relationship.


### Lineage Relationship Type
>	**Input Required**: True

>	**Attribute Type**: Valid Value

>	**Description**: The kind of lineage relationship to create/update -- determines which of the type-specific properties below apply (Formula/Formula Type: DataFlow, ProcessCall, DataMapping; Guard/Mandatory Guard: ControlFlow; Query/Query ID/Query Type: DataMapping only).

>	**Valid Values**: DataFlow,ControlFlow,ProcessCall,LineageMapping,DataMapping,UltimateSource,UltimateDestination


### Label
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A label used to identify or categorise a relationship link.

>	**Alternative Labels**: Wire Label


### Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


### Guard
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Informational value passed to the process step; the step's behaviour may vary depending on the guard it receives.


### Mandatory Guard
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Whether this guard must be present for the step to be actioned.

>	**Default Value**: false


___
