___

## Link Agreement Terms and Conditions
> Links an agreement to terms and conditions definition with implementation details.
>
>	**Alternative Names**: Agreement T&C; Agreement Terms & Conditions

### Terms & Conditions Id
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: A reference to a TermsAndConditions element - may also be a subtype.


### Agreement Name
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The name of the agreement to add an item to. Using qualified names is recommended.


### Membership Rationale
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Rationale for membership.


### Membership Status
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: The status of adding a member to a collection.

>	**Valid Values**: UNKNOWN,DISCOVERED,PROPOSED,IMPORTED,VALIDATED,DEPRECATED,OBSOLETE,OTHER

>	**Default Value**: PROPOSED


### Notes
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Notes and observations about the element.


### Anchor Scope IDs
>	**Input Required**: False

>	**Attribute Type**: Reference Name List

>	**Description**: A list of IDs that are anchor scopes for this element.


### Confidence
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: A percent confidence in the proposed adding of the member.


### Expression
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: An expression describing a membership, relationship or classification.


### Make Anchor
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Is the element at end2 an anchor to end1?

>	**Default Value**: false


### Source
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The source of the information.


### Steward
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The identifier of the steward responsible for the element.


### Steward Property Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Property name used to identify the type of the steward.


### Steward Type Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The type name of the steward element.


### User Defined Status
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A user-defined status value. Only valid when the primary status is set to OTHER.


### Effective Time
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: An ISO-8601 string representing the time to use for evaluating effectivity of the elements related to this one.


### Effective From
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A string in ISO-8601 format that defines the when an element becomes effective (visible).


### Effective To
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A string in ISO-8601 format that defines the when an element is no longer effective (visible).


___
