# Link Notification Subscriber
> Links a Referenceable as a subscriber to a NotificationType, defining the subscription parameters.

## Notification Type
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The NotificationType entity to link the subscriber to or for a monitored resource.


## Subscriber
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The Referenceable entity subscribing to the notification type.


## Label
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A label used to identify or categorise a relationship link.

>	**Alternative Labels**: Wire Label


## Last Notification
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The date of the last notification sent to this subscriber.


## Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


## Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


## Activity Status
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: The status of an activity - one of an enumerated set of values.

>	**Valid Values**: REQUESTED,APPROVED,WAITING,ACTIVATING,IN_PROGRESS,PAUSED,COMPLETED,INVALID,IGNORED,FAILED,CANCELLED,ABANDONED,OTHER

>	**Default Value**: REQUESTED


## Effective From
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The beginning of when an element is viewable.


## Effective Time
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The time at which an element must be effective in order to be returned by the request.


## Effective To
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The ending time at which an element is visible.


## External Source GUID
>	**Input Required**: False

>	**Attribute Type**: GUID

>	**Description**: The unique identifier of an external source.


## External Source Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The name of an external source


## For Duplicate Processing
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Flag indicating if the request is to support duplicate processing.


## For Lineage
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Flag indicating if the request is to support lineage.


## Request ID
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A user provided or system generated request id for a conversation.


## Anchor Scope IDs
>	**Input Required**: False

>	**Attribute Type**: Reference Name List

>	**Description**: A list of IDs that are anchor scopes for this element.


## Make Anchor
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Is the element at end2 an anchor to end1?

>	**Default Value**: false


## Zone Membership
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Zones scope visibility of elements to different users.

