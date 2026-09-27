___

## Classify Data Field as Primary Key
> Record that a data field is (part of) the identifier for its records (PrimaryKey classification). Primary Key Name is stored as the classification's display name.

### Data Field
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: A data field  name. Preferably a qualified name.


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Primary Key Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Name of the primary key.


### Primary Key Pattern
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: Key pattern for this primary key.

>	**Valid Values**: LOCAL_KEY,RECYCLED_KEY,NATURAL_KEY,MIRROR_KEY,AGGREGATE_KEY,CALLERS_KEY,STABLE_KEY,OTHER

>	**Default Value**: LOCAL_KEY


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
