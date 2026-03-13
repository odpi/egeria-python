# Link Notification Subscriber
> Links a Referenceable as a subscriber to a NotificationType, defining the subscription parameters.

## Subscriber
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The Referenceable entity subscribing to the notification type.


## Notification Type
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The NotificationType entity to link the subscriber to.


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

