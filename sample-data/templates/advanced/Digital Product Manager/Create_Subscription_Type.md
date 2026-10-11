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


### Identifier
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: An identier

>	**Alternative Labels**: ID


### Subscription Manager
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The integration connector that notifies subscribers. Defaults to the Baudot Digital Product Subscription Manager from the digital products content pack.


### Subscription License Type
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The license type granted to a subscriber's asset. Defaults to the first license type the product is governed by.


### Subscription Service Level Objective
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The service level objective the subscription offers. Defaults to the first service level objective the product is governed by.


### Status
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: The status of the digital product. There is a list of valid values that this conforms to.

>	**Default Value**: ACTIVE


### User Defined Status
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Only valid if  Status is set to OTHER. User defined & managed status values.


### Classifications
>	**Input Required**: false

>	**Attribute Type**: Named DICT

>	**Description**: Optionally specify the initial classifications for a collection. Multiple classifications can be specified. 

>	**Alternative Labels**: classification

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


### Is Own Anchor
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Generally True. 

>	**Alternative Labels**: Own Anchor

>	**Default Value**: True


### Anchor ID
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: Anchor identity for the collection. Typically a qualified name but if display name is unique then it could be used (not recommended)


### Parent ID
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: Unique name of the parent element.

>	**Alternative Labels**: Parent;


### Parent Relationship Type Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The kind of the relationship to the parent element.


### Anchor Scope Name
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: Optional qualified name of an anchor scope.


### Parent at End1
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Is the parent at end1 of the relationship?

>	**Default Value**: True


### Merge Update
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: If True, only those attributes specified in the update will be updated; If False, any attributes not provided during the update will be set to None.

>	**Alternative Labels**: Merge

>	**Default Value**: True


### Additional Properties
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: Additional user defined values organized as name value pairs in a dictionary.

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


### Supplementary Properties
>	**Input Required**: False

>	**Attribute Type**: Named DICT

>	**Description**: Provide supplementary information to the element using the structure of a glossary term

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


___
