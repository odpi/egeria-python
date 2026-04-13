# Link Agreement Item
> Attach or detach an agreement to an element referenced in its definition. Agreement item can be any referenceable element.
>
>	**Alternative Names**: Agreement from Item; Agreement to Item

## Agreement Name
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The name of the agreement to add an item to. Using qualified names is recommended.


## Item Name
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The name of the referenceable item to add to an agreement. Using qualified names is recommended.


## Label
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A label used to identify or categorise a relationship link.

>	**Alternative Labels**: Wire Label


## Agreement End Date
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Date when the agreement expires or was terminated, in ISO 8601 format.


## Agreement Item Id
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A user specified agreement item identifier.


## Agreement Start Date
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Date when the agreement becomes effective, in ISO 8601 format.


## Obligations
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: A dictionary of property:value pairs describing obligations.


## Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


## Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


## Entitlements
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: A dictionary of property:value pairs describing entitlements.


## Restrictions
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: A dictionary of property:value pairs describing restrictions.


## Usage Measurements
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: A dictionary of property:value pairs describing usage measurements.


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

