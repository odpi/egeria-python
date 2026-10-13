___

## Detach Valid Value Member
> Removes the ValidValueMember relationship.

### Valid Value Set
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The valid value set/definition that defines the allowed values for this element (ValidValuesAssignment relationship).

>	**Alternative Labels**: Valid Value Definition


### Member Value
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The value that is a member of the set (end 2 of ValidValueMember).


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Is Default Member
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: If true, this value is the set's default (isDefaultValue on the ValidValueMember relationship).

>	**Default Value**: false


### Member Ordinal
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: Position of the value within the set (ordinal on the ValidValueMember relationship).

>	**Default Value**: 0


___
