# Create Data Grain
> Creates or updates a data grain — a defined granularity of data that can be associated with a data field or data lens.

# Required

## Display Name
>	**Input Required**: True

>	**Description**: The common name of an element.

>	**Alternative Labels**: "Term Name"


# Data Grain Properties

## Granularity Basis
>	**Input Required**: False

>	**Description**: The basis on which the granularity is defined (e.g. time period, geographic region, customer segment). UML type: string — no enum defined in Egeria open types.


## Grain Statement
>	**Input Required**: False

>	**Description**: A human-readable statement describing the granularity of the data grain (e.g. 'one row per customer per day').


## Interval
>	**Input Required**: False

>	**Description**: The time interval in milliseconds between data captures for time-based data grains.


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

