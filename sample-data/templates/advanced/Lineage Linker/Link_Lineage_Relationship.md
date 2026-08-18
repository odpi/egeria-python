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


### ISC Qualified Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Qualified name of the Information Supply Chain this lineage relationship belongs to, if any.


### Formula
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The logic implemented by this process, expressed in the language of the business rather than any one implementation language.


### Formula Type
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The specification language used to express the Formula (e.g. SQL, Python, natural language).


### Query ID
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Identifier for the query fragment (DataMapping only) that this relationship represents.


### Query
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The query text (DataMapping only) that this relationship represents.


### Query Type
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The query language used to express Query (DataMapping only), e.g. SQL.


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
