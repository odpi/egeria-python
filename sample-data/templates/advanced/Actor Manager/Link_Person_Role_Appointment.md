___

## Link Person Role Appointment
> Appoints a person to a person role with an expected time allocation percentage using PersonRoleAppointment relationship.

### Expected Time Allocation Percent
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: Expected percentage of the appointee's time to be allocated to this role appointment (0-100).


### Person
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: Qualified name of a Person.


### Person Role
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: Qualified name of a PersonRole.


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
