# Add Member->Collection
>	Add/Remove a member to/from a collection.

## Element Id
>	**Input Required**: True

>	**Description**: The name of the element to add to the collection.

>	**Alternative Labels**: Member; Member Id


## Collection Id
>	**Input Required**: True

>	**Description**: The name of the collection to link to. There are many collection types, including Digital Products, Agreements and Subscriptions.

>	**Alternative Labels**: Parent; Parent Id; Collection Id; Agreement Id; Subscription Id; Digital Product Id; Folder; Folder Id


## Membership Rationale
>	**Input Required**: False

>	**Description**: Rationale for membership.

>	**Alternative Labels**: Rationale


## Expression
>	**Input Required**: False

>	**Description**: Expression that describes why the element is part of this collection.


## Confidence
>	**Input Required**: False

>	**Description**: A percent confidence in the proposed adding of the member.


## Membership Status
>	**Input Required**: False

>	**Description**: The status of adding a member to a collection.

>	**Valid Values**: UNKNOWN; DISCOVERED; PROPOSED; IMPORTED; VALIDATED; DEPRECATED; OBSOLETE; OTHER

>	**Default Value**: VALIDATED


## Steward
>	**Input Required**: False

>	**Description**: Name of the steward reviewing the proposed membership. Initially, just a string.


## Steward Type Name
>	**Input Required**: False

>	**Description**: Type of steward.


## Steward Property Name
>	**Input Required**: False

>	**Description**: Property name to discern the type of the steward.


## Source
>	**Input Required**: False

>	**Description**: Source of the member.


## Notes
>	**Input Required**: False

>	**Description**: Notes about the membership addition.


## Effective Time
>	**Input Required**: False

>	**Description**: An ISO-8601 string representing the time to use for evaluating effectivity of the elements related to this one.


## Effective From
>	**Input Required**: False

>	**Description**: A string in ISO-8601 format that defines the when an element becomes effective (visible).


## Effective To
>	**Input Required**: False

>	**Description**: A string in ISO-8601 format that defines the when an element is no longer effective (visible).

