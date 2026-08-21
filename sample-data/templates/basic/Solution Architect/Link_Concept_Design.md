___

## Link Concept Design
> Attach an element to the concept model element that designs it.

### Element Id
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The unique identifier (qualified name or GUID) of the element being referenced.

>	**Alternative Labels**: Element Name; Member Id


### Concept Model Element
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The ConceptModel container that this element is designed by (ConceptDesign relationship, 0571). Note: ConceptModel has no dedicated Dr.Egeria create command yet -- create one via pyegeria/the Egeria REST API directly before using this command.


### Label
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A label used to identify or categorise a relationship link.

>	**Alternative Labels**: Wire Label


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


___
