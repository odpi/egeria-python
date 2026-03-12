# Create Data Class
> Creates or updates a data class — a description of the values that may be stored in data fields. Supports composition via Containing Data Class and specialization via Specializes Data Class. Can be used to configure quality validators and data field classifiers.

# Required

## Display Name
>	**Input Required**: True

>	**Description**: The common name of an element.

>	**Alternative Labels**: "Term Name"


# Data Class Properties

## Is Case Sensitive
>	**Input Required**: False

>	**Description**: If true, values for this data class or field are case-sensitive.

>	**Default Value**: false


## Data Patterns
>	**Input Required**: False

>	**Description**: Regular expressions or patterns that describe the format of valid values for this data class.


## Is Nullable
>	**Input Required**: False

>	**Description**: If true, the field may hold null values.

>	**Default Value**: true


## Allow Duplicate Values
>	**Input Required**: False

>	**Description**: If true, the data class allows duplicate values in the data field.

>	**Default Value**: true


## Average Value
>	**Input Required**: False

>	**Description**: A typical or average value for the data class, used in data quality assessments.


## Sample Values
>	**Input Required**: False

>	**Description**: Representative example values that illustrate the expected content of this data class or field.


## Value List
>	**Input Required**: False

>	**Description**: An enumerated list of valid values for this data class.


## Value Range From
>	**Input Required**: False

>	**Description**: The lower bound of the valid value range for this data class.


## Value Range To
>	**Input Required**: False

>	**Description**: The upper bound of the valid value range for this data class.


## Containing Data Class
>	**Input Required**: False

>	**Description**: The data class that this data class is composed within (DataClassComposition relationship).


## Default Value
>	**Input Required**: False

>	**Description**: The default value assigned to this field or data class when no value is supplied.


# Common Properties

## Journal Entry
>	**Input Required**: False

>	**Description**: A text entry into a journal.


## Category
>	**Input Required**: False

>	**Description**: A user-defined category for the element, used to group related elements for display or search purposes.

>	**Alternative Labels**: Category Name


## Description
>	**Input Required**: False

>	**Description**: A description.


## Qualified Name
>	**Input Required**: False

>	**Description**: The unique, text name of an element.


## Content Status
>	**Input Required**: False

>	**Description**: The lifecycle status of an element.

>	**Valid Values**: DRAFT,PREPARED,PROPOSED,APPROVED,REJECTED,ACTIVE,DEPRECATED,OTHER

>	**Default Value**: ACTIVE


# Additional Properties

## Search Keywords
>	**Input Required**: False

>	**Description**: A list of search keywords.


## GUID
>	**Input Required**: False

>	**Description**: A unique identifier - typically of an element in this context.

>	**Alternative Labels**: Guid; guid


## Identifier
>	**Input Required**: False

>	**Description**: An identier


## URL
>	**Input Required**: False

>	**Description**: URL for further information.


## Version Identifier
>	**Input Required**: False

>	**Description**: The version of the element

>	**Alternative Labels**: Version

>	**Default Value**: 1.0


## Authors
>	**Input Required**: False

>	**Description**: The authors.

