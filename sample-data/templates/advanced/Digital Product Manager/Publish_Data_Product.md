___

## Publish Data Product
> Send an ODPS data product file to an integration daemon, which passes it on to the integration connectors that registered a Bitol listener.

### Integration Daemon
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The integration daemon (a SoftwareServer) whose Bitol listeners receive the document.


### Document File
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: Path to a file holding the document (YAML or JSON): an Open Data Contract Standard (ODCS) data contract or an Open Data Product Standard (ODPS) data product. A relative path is resolved against the directory of the markdown file being processed.


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


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
