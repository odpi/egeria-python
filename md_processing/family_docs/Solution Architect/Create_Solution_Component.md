# **Create Solution Component**
>	A reusable solution component.

## **Display Name**
>	**Input Required**: True

>	**Description**: Name of the solution component.

>	**Alternative Labels**: Name; Display Name; Solution Component Name; Component Name


## **Qualified Name**
>	**Input Required**: False

>	**Description**: A unique qualified name for the element. Generated using the qualified name pattern  if not user specified.


## **Description**
>	**Input Required**: False

>	**Description**: A description of the data structure.


## **Solution Component Type**
>	**Input Required**: False

>	**Description**: Type of solution component.

>	**Alternative Labels**: Soln Component Type


## **Planned Deployed Implementation Type**
>	**Input Required**: False

>	**Description**: The planned implementation type for deployment.

>	**Alternative Labels**: Planned Deployed Impl Type


## **Initial Status**
>	**Input Required**: False

>	**Description**: Optional lifecycle status. If not specified, set to ACTIVE. If set to Other then the value in User Defined Status will be used.

>	**Valid Values**: DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; ACTIVE; DISABLED; DEPRECATED; OTHER

>	**Default Value**: ACTIVE


## **In Solution Components**
>	**Input Required**: False

>	**Description**: Solution components that include this one.

>	**Alternative Labels**: In Solution Component; In Component


## **In Solution Blueprints**
>	**Input Required**: False

>	**Description**: Solution Blueprints that contain this component.

>	**Alternative Labels**: In Solution Blueprints


## **In Information Supply Chains**
>	**Input Required**: False

>	**Description**: The Information Supply Chains that this component is a member of.

>	**Alternative Labels**: In Supply Chains; In Supply Chain; In Information Supply Chain


## **Actors**
>	**Input Required**: False

>	**Description**: Actors associated with this component.


## **GUID**
>	**Input Required**: False

>	**Description**: A system generated unique identifier.

>	**Alternative Labels**: Guid; guid


## **Merge Update**
>	**Input Required**: False

>	**Description**: If true, only those attributes specified in the update will be updated; If false, any attributes not provided during the update will be set to None.

>	**Alternative Labels**: Merge

>	**Default Value**: True

