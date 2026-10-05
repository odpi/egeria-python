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


___
