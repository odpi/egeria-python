BeeAI - Agentic Workflow

# Create Solution Component
>	A reusable solution component.

## Display Name
>	**Input Required**: True

>	**Description**: Name of the solution component.

>	**Alternative Labels**: Name; Display Name; Solution Component Name; Component Name
BeeAI Framework

## Qualified Name
>	**Input Required**: False

>	**Description**: A unique qualified name for the element. Generated using the qualified name pattern  if not user specified.


## Category
>	**Input Required**: False

>	**Description**: A user specified category name that can be used for example, to define product types or agreement types.

ML-OPS
## Description
>	**Input Required**: False

>	**Description**: A description of the data structure.
BeeAI Framework is an open-source framework for building production-grade multi-agent systems. It is hosted by the Linux Foundation under open governance, ensuring transparency, community-driven development, and enterprise-grade stability.
BeeAI goes beyond simple prompting by providing a lightweight yet powerful approach to reliable agent development, with built-in constraint enforcement and rule-based governance that preserves reasoning abilities while ensuring predictable behavior. The BeeAI Framework provides the flexibility and performance needed for scalable AI systems, supporting both Python and TypeScript with complete feature parity.
​


## Status
>	**Input Required**: False

>	**Description**: The status of the solution component. There is a list of valid values that this conforms to.

>	**Valid Values**: DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED;  ACTIVE; DEPRECATED; OTHER

>	**Default Value**: ACTIVE


## Solution Component Type
>	**Input Required**: False

>	**Description**: Type of solution component.

>	**Alternative Labels**: Soln Component Type

AI Framework
## Planned Deployed Implementation Type
>	**Input Required**: False

>	**Description**: The planned implementation type for deployment.

>	**Alternative Labels**: Planned Deployed Impl Type

Python
## User Defined Status
>	**Input Required**: False

>	**Description**: Supporting user managed lifecycle statuses. Only used if the Initial Status is set to OTHER.

>	**Default Value**: DRAFT


## Initial Status
>	**Input Required**: False

>	**Description**: Optional lifecycle status. If not specified, set to ACTIVE. If set to Other then the value in User Defined Status will be used.

>	**Valid Values**: DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; ACTIVE; DISABLED; DEPRECATED; OTHER

>	**Default Value**: ACTIVE


## In Solution Components
>	**Input Required**: False

>	**Description**: Solution components that include this one.

>	**Alternative Labels**: In Solution Component; In Component


## In Solution Blueprints
>	**Input Required**: False

>	**Description**: Solution Blueprints that contain this component.

>	**Alternative Labels**: In Solution Blueprints


## In Information Supply Chains
>	**Input Required**: False

>	**Description**: The Information Supply Chains that this component is a member of.

>	**Alternative Labels**: In Supply Chains; In Supply Chain; In Information Supply Chain


## Actors
>	**Input Required**: False

>	**Description**: Actors associated with this component.


## GUID
>	**Input Required**: False

>	**Description**: A system generated unique identifier.

>	**Alternative Labels**: Guid; guid


## Effective Time
>	**Input Required**: False

>	**Description**: An ISO-8601 string representing the time to use for evaluating effectivity of the elements related to this one.


## Effective From
>	**Input Required**: False

>	**Description**: A string in ISO-8601 format that defines the when an element becomes effective (visible).


## Effective To
>	**Input Required**: False

>	**Description**: A string in ISO-8601 format that defines the when an element is no longer effective (visible).


## Merge Update
>	**Input Required**: False

>	**Description**: If true, only those attributes specified in the update will be updated; If false, any attributes not provided during the update will be set to None.

>	**Alternative Labels**: Merge

>	**Default Value**: True


## Additional Properties
>	**Input Required**: False

>	**Description**: Additional user defined values organized as name value pairs in a dictionary.


## Glossary Term
>	**Input Required**: False

>	**Description**: Term that provides meaning to this field.


## External Source GUID
>	**Input Required**: False

>	**Description**: Identifier of an external source that is associated with this element.


## External Source Name
>	**Input Required**: False

>	**Description**: Name of an external element that is associated with this element.

