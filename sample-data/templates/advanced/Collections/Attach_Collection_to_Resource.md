# Attach Collection to Resource
> Connect an existing collection to an element using the ResourceList relationship.
>
>	**Alternative Names**: Collection to Resource; Collection from Resource

## Element Id
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The unique identifier (qualified name or GUID) of the element being referenced.

>	**Alternative Labels**: Element Name; Member Id


## Label
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A label used to identify or categorise a relationship link.

>	**Alternative Labels**: Wire Label


## Resource Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Description of the resource or how it is being used. From the ResourceList relationship (0019).


## Resource Id
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The unique identifier (qualified name or GUID) of the supporting resource in a ResourceList relationship.


## Resource Properties
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: Additional properties needed to use the resource. From the ResourceList relationship (0019).


## Watch Resource
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Whether the parent entity should receive notifications about changes to this resource. From the ResourceList relationship (0019).


## Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


## Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


## Resource Use
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: Describes how the resource is being used. From the ResourceList relationship (0019).

>	**Valid Values**: Validate Resource,Hosted Service,Supporting Template,Called Service,Supporting Person,Member Template,Supporting Team,Derived Element Template,Generate Insight,Activity Folder,Inform Steward,Certify Resource,Provision Resource,Hosted Connector,Improve Metadata Element,Survey Resource,Hosted Governance Engine,Watch Metadata Element,Data Specification,Choose Path,Supporting Process,Configure Connector,Catalog Resource,Create Subscription,Uncatalog Resource,Related Information,Cancel Subscription


## Collection Id
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The unique identifier (qualified name or GUID) of the collection.


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

