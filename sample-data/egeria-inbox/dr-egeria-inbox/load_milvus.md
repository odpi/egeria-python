Load Data to Milvus

Lets assume for the nonce that data prepared from the Data-Prep-Kit will be loaded to Milvus. 
We will represent this by wiring them together here.

____

# Link Solution Components
>	This command can be used to link or unlink wires between components.

## Component1
>	**Input Required**: True

>	**Description**: The  first component to link.

>	**Alternative Labels**: Solution Component 1; Comp 1

SolutionComponent::Data-Prep-Kit::V1.0
## Component2
>	**Input Required**: True

>	**Description**: The  second component to link.

>	**Alternative Labels**: Solution Component 2; Comp 2

SolutionComponent::Milvus::V1.0
## Wire Label
>	**Input Required**: False

>	**Description**: Labels the link between two components.

>	**Alternative Labels**: Label

Loads
## Description
>	**Input Required**: False

>	**Description**: A description of the wire.

DPK loads the prepared data into Milvus?

## Effective Time
>	**Input Required**: False

>	**Description**: An ISO-8601 string representing the time to use for evaluating effectivity of the elements related to this one.


## Effective From
>	**Input Required**: False

>	**Description**: A string in ISO-8601 format that defines the when an element becomes effective (visible).


## Effective To
>	**Input Required**: False

>	**Description**: A string in ISO-8601 format that defines the when an element is no longer effective (visible).


## Additional Properties
>	**Input Required**: False

>	**Description**: Additional user defined values organized as name value pairs in a dictionary.


## Glossary Term
>	**Input Required**: False

>	**Description**: Term that provides meaning to this field.

