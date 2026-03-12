# Link Notification Subscriber
>	Links a Referenceable as a subscriber to a NotificationType, defining the subscription parameters.

## Subscriber
>	**Input Required**: True

>	**Description**: The Referenceable entity subscribing to the notification type.


## Notification Type
>	**Input Required**: True

>	**Description**: The NotificationType entity to link the subscriber to.


## Label
>	**Input Required**: False

>	**Description**: A label used to identify or categorise a relationship link.


## Last Notification
>	**Input Required**: False

>	**Description**: The date of the last notification sent to this subscriber.


## Description
>	**Input Required**: False

>	**Description**: A description.


## Activity Status
>	**Input Required**: False

>	**Description**: The status of an activity - one of an enumerated set of values.

>	**Valid Values**: REQUESTED,APPROVED,WAITING,ACTIVATING,IN_PROGRESS,PAUSED,COMPLETED,INVALID,IGNORED,FAILED,CANCELLED,ABANDONED,OTHER

>	**Default Value**: REQUESTED

