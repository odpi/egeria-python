# Link Subscriber->Subscription
>	Attach or detach a subscriber to a subscription. Subscriber can be any type of element.

## Subscriber Id
>	**Input Required**: False

>	**Description**:  identifier of a subscriber. Initially, will let this be an arbitrary string - could harden this to a qualified name later if needed.

>	**Alternative Labels**: Subscriber


## Subscription
>	**Input Required**: True

>	**Description**: Name of the  subscription agreement. Recommend using qualified name.

>	**Alternative Labels**: Subscription Name


## Effective Time
>	**Input Required**: False

>	**Description**: An ISO-8601 string representing the time to use for evaluating effectivity of the elements related to this one.


## Effective From
>	**Input Required**: False

>	**Description**: A string in ISO-8601 format that defines the when an element becomes effective (visible).


## Effective To
>	**Input Required**: False

>	**Description**: A string in ISO-8601 format that defines the when an element is no longer effective (visible).

