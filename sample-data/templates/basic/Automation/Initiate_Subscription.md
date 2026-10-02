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


___
