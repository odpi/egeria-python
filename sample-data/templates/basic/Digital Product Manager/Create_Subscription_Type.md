___

## Create Subscription Type
> Add a subscription type to a digital product: a one-time, periodic or ongoing-update way to subscribe. Creates the product's notification type and returns the governance action process that Initiate Subscription runs to provision a subscription of this type. Safe to re-run: an existing subscription type is brought into line with the request rather than duplicated.

### Digital Product
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The digital product the subscription type is added to (name, qualified name or GUID).


### Subscription Kind
>	**Input Required**: True

>	**Attribute Type**: Valid Value

>	**Description**: How often subscribers are notified, and so how often the product's data is delivered: ONE_TIME (a single delivery, typically to evaluate the product), PERIODIC (every Subscription Notification Interval minutes) or ONGOING_UPDATE (when a Monitored Resource changes, but no more often than every Subscription Notification Interval minutes).

>	**Valid Values**: ONE_TIME,PERIODIC,ONGOING_UPDATE

>	**Default Value**: ONE_TIME


### Display Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The common name of an element.

>	**Alternative Labels**: "Term Name"


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


### Category
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A user specified category name that can be used for example, to define product types or agreement types.

>	**Alternative Labels**: Category Name


### Qualified Name
>	**Input Required**: False

>	**Attribute Type**: QN

>	**Description**: A unique qualified name for the element. Generated using the qualified name pattern  if not user specified.


### Subscription Notification Interval
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: Minutes between notifications -- the delivery interval for a PERIODIC subscription, the minimum interval for an ONGOING_UPDATE one. In MINUTES (unlike the Governance Officer family's 'Notification Interval', which is milliseconds).


### Monitored Resources
>	**Input Required**: False

>	**Attribute Type**: Reference Name List

>	**Description**: For an ONGOING_UPDATE subscription: the elements whose changes trigger a notification -- typically the product's asset.


### Version Identifier
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Published product version identifier.

>	**Alternative Labels**: Version

>	**Default Value**: 1.0


### GUID
>	**Input Required**: False

>	**Attribute Type**: GUID

>	**Description**: A system generated unique identifier.

>	**Alternative Labels**: Guid; guid


### URL
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Link to supporting information


### Search Keywords
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Keywords to facilitate finding the element


___
