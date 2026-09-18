___

## Link Agreement Terms and Conditions
> Links an agreement to a terms and conditions definition with agreement-item-specific implementation details (item id, effective dates, usage measurements). Entitlements/Obligations/Restrictions live on the Terms and Conditions element itself, not on this relationship.
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


### Label
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A label used to identify or categorise a relationship link.

>	**Alternative Labels**: Wire Label


### Agreement Item Id
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A user specified agreement item identifier.


### Agreement Start Date
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Date when the agreement becomes effective, in ISO 8601 format.


### Agreement End Date
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Date when the agreement expires or was terminated, in ISO 8601 format.


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


### Usage Measurements
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: A dictionary of property:value pairs describing usage measurements.

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


___
