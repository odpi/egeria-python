___

## Reclassify Instance
> Change the properties of a classification already on a metadata element.

### Metadata Element GUID
>	**Input Required**: True

>	**Attribute Type**: GUID

>	**Description**: GUID of the metadata element.


### Classification Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: Open metadata type name of the classification.


### Classification Properties
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: One property per line as 'name: value' (same typing rules as Instance Properties).

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


### Replace Properties
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: True: the supplied properties replace all existing ones. False (default): they are merged.


___
