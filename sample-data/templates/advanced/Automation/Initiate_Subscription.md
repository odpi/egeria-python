___

## Initiate Subscription
> Take out a subscription to a digital product by running the product's subscription process for the chosen subscription type. The process creates the subscription, its license and the data delivery to the destination. Unlike Create Digital Subscription, which only records a subscription element, this provisions it.

### Subscription Type
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The subscription type to take out: a digital product's subscribing action process, ProvisioningActionProcess::<product name>::Create Subscription::<subscription type>.


### Subscription Requester
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The actor (person, team, ...) requesting the subscription.


### Destination Data Set
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The asset the subscribed data is delivered to.


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Request Parameters
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: Name: value parameters passed to the governance service(s) that run.

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


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


___
