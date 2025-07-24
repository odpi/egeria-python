
# Family: Solution Architect

## **Create Information Supply Chain**
>	The flow of a particular type of data across a digital landscape.
### **Display Name**
>	**Input Required**: True

>	**Description**: Name of the Information Supply Chain

>	**Alternative Labels**: Name; Display Name; Supply Chain; Supply Chain Name


### **Description**
>	**Input Required**: False

>	**Description**: A description of the data structure.


### **Scope**
>	**Input Required**: False

>	**Description**: Scope of the supply chain.


### **Purposes**
>	**Input Required**: False

>	**Description**: A list of purposes.

>	**Alternative Labels**: Purpose, Purposes


### **Nested Information Supply Chains**
>	**Input Required**: False

>	**Description**: A list of supply chains that compose this supply chain.

>	**Alternative Labels**: Nested Supply Chains


### **In Information Supply Chain**
>	**Input Required**: False

>	**Description**: Supply chains that this supply chain is in.

>	**Alternative Labels**: In Supply Chain; In Supply Chains; In Information Supply Chains


### **Qualified Name**
>	**Input Required**: False

>	**Description**: A unique qualified name for the element. Generated using the qualified name pattern  if not user specified.


### **GUID**
>	**Input Required**: False

>	**Description**: A system generated unique identifier.

>	**Alternative Labels**: Guid; guid


### **Merge Update**
>	**Input Required**: False

>	**Description**: If true, only those attributes specified in the update will be updated; If false, any attributes not provided during the update will be set to None.

>	**Alternative Labels**: Merge

>	**Default Value**: True


___

## **Create Solution Blueprint**
>	A solution blueprint describes the architecture of a digital service in terms of solution components.
### **Display Name**
>	**Input Required**: True

>	**Description**: Name of the Information Supply Chain

>	**Alternative Labels**: Name; Display Name; Blueprint; Blueprint Name


### **Description**
>	**Input Required**: False

>	**Description**: A description of the data structure.


### **Version Identifier**
>	**Input Required**: False

>	**Description**: A user supplied version identifier.


### **Solution Components**
>	**Input Required**: False

>	**Description**: Solution components that make up the blueprint.

>	**Alternative Labels**: Components; Solution Component; Component


### **Qualified Name**
>	**Input Required**: False

>	**Description**: A unique qualified name for the element. Generated using the qualified name pattern  if not user specified.


### **GUID**
>	**Input Required**: False

>	**Description**: A system generated unique identifier.

>	**Alternative Labels**: Guid; guid


___

## **Create Solution Component**
>	A reusable solution component.
### **Display Name**
>	**Input Required**: True

>	**Description**: Name of the solution component.

>	**Alternative Labels**: Name; Display Name; Solution Component Name; Component Name


### **Qualified Name**
>	**Input Required**: False

>	**Description**: A unique qualified name for the element. Generated using the qualified name pattern  if not user specified.


### **Description**
>	**Input Required**: False

>	**Description**: A description of the data structure.


### **Solution Component Type**
>	**Input Required**: False

>	**Description**: Type of solution component.

>	**Alternative Labels**: Soln Component Type


### **Planned Deployed Implementation Type**
>	**Input Required**: False

>	**Description**: The planned implementation type for deployment.

>	**Alternative Labels**: Planned Deployed Impl Type


### **Initial Status**
>	**Input Required**: False

>	**Description**: Optional lifecycle status. If not specified, set to ACTIVE. If set to Other then the value in User Defined Status will be used.

>	**Valid Values**: DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; ACTIVE; DISABLED; DEPRECATED; OTHER

>	**Default Value**: ACTIVE


### **In Solution Components**
>	**Input Required**: False

>	**Description**: Solution components that include this one.

>	**Alternative Labels**: In Solution Component; In Component


### **In Solution Blueprints**
>	**Input Required**: False

>	**Description**: Solution Blueprints that contain this component.

>	**Alternative Labels**: In Solution Blueprints


### **In Information Supply Chains**
>	**Input Required**: False

>	**Description**: The Information Supply Chains that this component is a member of.

>	**Alternative Labels**: In Supply Chains; In Supply Chain; In Information Supply Chain


### **Actors**
>	**Input Required**: False

>	**Description**: Actors associated with this component.


### **GUID**
>	**Input Required**: False

>	**Description**: A system generated unique identifier.

>	**Alternative Labels**: Guid; guid


### **Merge Update**
>	**Input Required**: False

>	**Description**: If true, only those attributes specified in the update will be updated; If false, any attributes not provided during the update will be set to None.

>	**Alternative Labels**: Merge

>	**Default Value**: True


___

## **Create Solution Role**
>	A collection of data fields that for a data specification for a data source.
### **Name**
>	**Input Required**: True

>	**Description**: Name of the role.

>	**Alternative Labels**: Role; Solution Role; Solution Role Name; Role Name


### **Description**
>	**Input Required**: False

>	**Description**: A description of the data structure.


### **Title**
>	**Input Required**: False

>	**Description**: Title of the role.


### **Scope**
>	**Input Required**: False

>	**Description**: Scope of the role.


### **identifier**
>	**Input Required**: False

>	**Description**: role identifier


### **Domain Identifier**
>	**Input Required**: False

>	**Description**: Governance domain identifier

>	**Default Value**: 0


### **Role Type**
>	**Input Required**: False

>	**Description**: Type of the role.  Currently must be GovernanceRole.

>	**Alternative Labels**: Role Type Name

>	**Default Value**: GovernanceRole


### **Qualified Name**
>	**Input Required**: False

>	**Description**: A unique qualified name for the element. Generated using the qualified name pattern  if not user specified.


### **GUID**
>	**Input Required**: False

>	**Description**: A system generated unique identifier.

>	**Alternative Labels**: Guid; guid


___

## **Link Information Supply Chain Peers**
>	This command can be used to link or unlink information supply chain segments.
### **Segment1**
>	**Input Required**: True

>	**Description**: The  first segment to link.

>	**Alternative Labels**: Segment 1; Information Supply Chain Segment 1; Info Supply Chain Segment 1


### **Segment2**
>	**Input Required**: True

>	**Description**: The  second segment to link.

>	**Alternative Labels**: Segment 2; Information Supply Chain Segment 2; Info Supply Chain Segment 2


### **Link Label**
>	**Input Required**: False

>	**Description**: Labels the link between two information supply chain segments.

>	**Alternative Labels**: Label


### **Description**
>	**Input Required**: False

>	**Description**: A description of the data structure.


___

## **Link Solution Component Peers**
>	This command can be used to link or unlink wires between components.
### **Component1**
>	**Input Required**: True

>	**Description**: The  first component to link.

>	**Alternative Labels**: Solution Component 1; Comp 1


### **Component2**
>	**Input Required**: True

>	**Description**: The  second component to link.

>	**Alternative Labels**: Solution Component 2; Comp 2


### **Wire Label**
>	**Input Required**: False

>	**Description**: Labels the link between two components.

>	**Alternative Labels**: Label


### **Description**
>	**Input Required**: False

>	**Description**: A description of the wire.


___

## **View Information Supply Chains**
>	Return information supply chains filtered by the search string.
### **Search String**
>	**Input Required**: False

>	**Description**: An optional search string to filter results by.

>	**Alternative Labels**: Filter

>	**Default Value**: *


### **Output Format**
>	**Input Required**: False

>	**Description**: Optional specification of output format for the query.

>	**Alternative Labels**: Format

>	**Valid Values**: LIST; FORM; MD; REPORT; MERMAID; LIST; DICT; HTML

>	**Default Value**: List


### **Detailed**
>	**Input Required**: False

>	**Description**: If true a more detailed set of attributes will be returned.

>	**Default Value**: True


___

## **View Solution Blueprints**
>	Return the data structure details, optionally filtered by the search string.
### **Search String**
>	**Input Required**: False

>	**Description**: An optional search string to filter results by.

>	**Alternative Labels**: Filter

>	**Default Value**: *


### **Output Format**
>	**Input Required**: False

>	**Description**: Optional specification of output format for the query.

>	**Alternative Labels**: Format

>	**Valid Values**: List; Form; Report; Dict

>	**Default Value**: List


### **Detailed**
>	**Input Required**: False

>	**Description**: If true a more detailed set of attributes will be returned.

>	**Default Value**: True


___

## **View Solution Components**
>	Return the data structure details, optionally filtered by the search string.
### **Search String**
>	**Input Required**: False

>	**Description**: An optional search string to filter results by.

>	**Alternative Labels**: Filter

>	**Default Value**: *


### **Output Format**
>	**Input Required**: False

>	**Description**: Optional specification of output format for the query.

>	**Alternative Labels**: Format

>	**Valid Values**: List; Form; Report; Dict

>	**Default Value**: List


### **Detailed**
>	**Input Required**: False

>	**Description**: If true a more detailed set of attributes will be returned.

>	**Default Value**: True


___

## **View Solution Roles**
>	Return the data structure details, optionally filtered by the search string.
### **Search String**
>	**Input Required**: False

>	**Description**: An optional search string to filter results by.

>	**Alternative Labels**: Filter

>	**Default Value**: *


### **Output Format**
>	**Input Required**: False

>	**Description**: Optional specification of output format for the query.

>	**Alternative Labels**: Format

>	**Valid Values**: List; Form; Report; Dict

>	**Default Value**: List


### **Detailed**
>	**Input Required**: False

>	**Description**: If true a more detailed set of attributes will be returned.

>	**Default Value**: True


___
