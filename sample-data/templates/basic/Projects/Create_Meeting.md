___

## Create Meeting
> Create a Meeting person action via the generic asset-maker/actions endpoint (ActionRequestBody, properties.class=MeetingProperties). No named create_meeting wrapper exists yet in pyegeria — uses the same mechanism as my_profile.create_my_todo.

### Display Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The common name of an element.

>	**Alternative Labels**: "Term Name"


### Situation
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Describe the notification (title/summary)


### Objective
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The intended outcome/goal of a Meeting, ToDo, or Review person action.


### Priority
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: An integer priority for the project.


### Requested Start Time
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Requested start date/time for a Meeting, ToDo, or Review person action.


### Due Time
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Due date/time for a Meeting, ToDo, or Review person action.


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


### Category
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A user specified category name that can be used for example, to define product types or agreement types.

>	**Alternative Labels**: Category Name


### Qualified Name
>	**Input Required**: False

>	**Attribute Type**: QN

>	**Description**: A unique qualified name for the element. Generated using the qualified name pattern  if not user specified.


### Activity Status
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: The status of an activity - one of an enumerated set of values.

>	**Valid Values**: REQUESTED,APPROVED,WAITING,ACTIVATING,IN_PROGRESS,PAUSED,COMPLETED,INVALID,IGNORED,FAILED,CANCELLED,ABANDONED,OTHER

>	**Default Value**: REQUESTED


### Version Identifier
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Published product version identifier.

>	**Alternative Labels**: Version

>	**Default Value**: 1.0


### Identifier
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: role identifier

>	**Alternative Labels**: ID


### GUID
>	**Input Required**: False

>	**Attribute Type**: GUID

>	**Description**: A system generated unique identifier.

>	**Alternative Labels**: Guid; guid


### URL
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Link to supporting information


### Search Keywords
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Keywords to facilitate finding the element


___
