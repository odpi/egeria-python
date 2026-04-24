___

## Create Campaign
> Creates or updates a campaign — a collection of related projects working towards a common goal. Sets the Campaign classification on the Project entity.

## Display Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The common name of an element.

>	**Alternative Labels**: "Term Name"


### Actual Completion Date
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The actual date the project completed as an ISO 8601 string.


### Actual Start Date
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The actual date the project started as an ISO 8601 string.


### Mission
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The project mission statement.


### Planned Completion Date
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Planned project end date as an ISO 8601 string.


### Planned Start Date
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Planned project start date as an ISO 8601 string.


### Priority
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: An integer priority for the project.


### Project Approach
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The methodology or approach used to achieve the project's goals (ProjectClassification attribute).


### Project Health
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A string representing the health of the project.


### Project Identifier
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A user-assigned identifier for the project.


### Project Management Style
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The management style for the project (ProjectClassification attribute). For example, experimental vs. formal product development.


### Project Phase
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A string describing the current phase of the project.


### Project Results Usage
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: How the results of the project are intended to be used (ProjectClassification attribute). For example: inform future projects, test a theory, develop a product.


### Project Scope
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The scope of the project — what is in and out of scope.


### Project Status
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A string representing the current status of the project.


### Project Type
>	**Input Required**: False

>	**Attribute Type**: Enum

>	**Description**: A string classifying the project. Supported values are Campaign, Task, PersonalProject and StudyProject.

>	**Valid Values**: Project,Campaign,Task,PersonalProject,StudyProject,Experiment

>	**Default Value**: Project


### Success Criteria
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: A list of criteria used to evaluate the success of the project.


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Category
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A user-defined category for the element, used to group related elements for display or search purposes.

>	**Alternative Labels**: Category Name


### Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


### Qualified Name
>	**Input Required**: False

>	**Attribute Type**: QN

>	**Description**: The unique, text name of an element.


### Content Status
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: The lifecycle status of an element.

>	**Valid Values**: DRAFT,PREPARED,PROPOSED,APPROVED,REJECTED,ACTIVE,DEPRECATED,OTHER

>	**Default Value**: ACTIVE


### Purposes
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: A list of purposes for this project (array&lt;string&gt;). Note: distinct from Collection.purpose (string, singular) which is a separate attribute on Collection Base.


## Search Keywords
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: A list of search keywords.


### GUID
>	**Input Required**: False

>	**Attribute Type**: GUID

>	**Description**: A unique identifier - typically of an element in this context.

>	**Alternative Labels**: guid; Guid


### URL
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: URL for further information.


### Version Identifier
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The version of the element

>	**Alternative Labels**: Version

>	**Default Value**: 1.0


### Authors
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: The authors.


___
