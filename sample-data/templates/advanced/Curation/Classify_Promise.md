___

## Classify Promise
> Classify an existing element as a Promise - a placeholder for a real-world digital resource/artifact that has not yet been delivered. Once classified, the element is only returned to lineage requests (For Lineage = true).

### Target Element
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: Qualified name of the existing element being classified or linked.


### User Defined Deployment Status
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A locally defined deployment status - only used when Deployment Status is OTHER.


### Start Time
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Date/time (ISO 8601) that work started on delivering the promised resource.


### Due Time
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Due date/time - for a Meeting, ToDo, or Review person action, or for delivery of the resource described by a Promise.


### Last Review Time
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Date/time (ISO 8601) that the promise was last reviewed.


### Completion Time
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Date/time (ISO 8601) that the promised resource was delivered.


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Deployment Status
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: The deployment status of the element - one of an enumerated set of values (DeploymentStatus). On a Promise it tracks progress toward delivering the promised resource.

>	**Valid Values**: PROPOSED,UNDER_DEVELOPMENT,DEVELOPMENT_COMPLETE,APPROVED_FOR_DEPLOYMENT,REJECTED,STANDBY,ACTIVE,DISABLED,FAILED,OTHER


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


### Additional Properties
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: Additional Properties  allow arbitrary properties not defined in the type definitions to be added to any referenceable element.

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


___
