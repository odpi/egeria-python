# Adding more to the Egeria-Markdown Glossary

In the first two files created the Egeria-Markdown glossary with a few terms. In the second, we added a couple of
categories and then updated the existing terms to use them. In this installment, we will add a number of terms to the
glossary to make it a truly useful aid for the Dr.Egeria user. Once we have added the terms, we'll discuss how we can
continue to work with the terms using the `hey_egeria` commands.
___


# Update Term

## Term Name 

Display

## Aliases


## Summary
This is a processing directive to Dr.Egeria to request that the input text be processed for display only.

## Description
This is a processing directive to Dr.Egeria commands to request that the input text be processed and displaying. This is
useful to validate that the command processor is able to open the input text and shows that the environment is able to
process the text.

## Examples


## Usage


## Version Identifier


## Qualified Name
Term::Display

## Status
DRAFT

## In Glossary
Glossary::Egeria-Markdown

## Categories
Category::Processing Dr.Egeria Markdown

## Guid
5863f82d-e96f-41e6-a3bf-7fa4904401d3





# Update Term

## Term Name 

Validate

## Aliases


## Summary
A processing directive to Dr.Egeria to request that the input text be validated for conformance to Dr. Egeria syntax
with the results being displayed and, depending on results, an output file incorporating suggested changes will be produced.

## Description
A processing directive to Dr.Egeria to request that the input text be validated for conformance to Dr. Egeria syntax.
The results are displayed in the console, and include labeled messages. The labels may be:
* Info - just an information notice, for example, an optional field is empty.
* Warning - an issue was found, but we can automatically try to repair it or it doesn't prevent further processing.
* Error - A non-recoverable error input error was found - this command won't be processed further - for example if we encounter
a `Create Term` command and find that the term already exists.
Additional descriptive messages are also displayed. In some cases, for example if we detect a `Create` command for an
object that already exists, we will also produce an output file that replaces the `Create` with an `Update` command.

## Examples
Default values for key environment variables in the **Egeria Workspaces** environment:
* EGERIA_ROOT_PATH=/home/jovyan
* EGERIA_INBOX_PATH=loading-bay/dr-egeria-inbox
* EGERIA_OUTBOX_PATH=distribution-hub/dr-egeria-outbox
* EGERIA_LOCAL_QUALIFIER=EGERIA
So place input files in the `loading-bay/dr-egeria-inbox` folder and look for output files in `distribution-hub/dr-egeria-outbox`.

## Usage
The EGERIA_ROOT_PATH is generally going to be set depending on what kind of environment you are using. For **Egeria Workspaces**,
when using the Jupyter environment, it will be set to Jupyter's default, which is `/home/jovyan`.
* The location of the input file is based on the environment variables EGERIA_ROOT_PATH and EGERIA_INPUT_PATH.
* The output file will be written to the directory specified by the EGERIA_ROOT_PATH and EGERIA_OUTPUT_PATH environment
variables.

## Version Identifier
.1

## Qualified Name
Term::Validate::.1

## Status
DRAFT

## In Glossary
Glossary::Egeria-Markdown

## Categories
Category::Processing Dr.Egeria Markdown

## Guid
adc5f50f-0092-43e7-9049-fd39de7ff411



# Create Term

## Term Name

Process

## Owning Glossary

Glossary::Egeria-Markdown

## Categories

Processing Dr.Egeria Markdown

## Summary
The process directive indicates that we should apply the requested commands to Egeria if they are valid.

## Description
The process directive indicates that we should apply the requested commands to Egeria if they are valid. Informational
messages are provided on the console. A new file is produced that reflects the updates made and is designed to make
it easy to make further changes using the contents. For example, `Create` commands from the input file are written
out as `Update` statements in the output file. Qualified names and GUIDs generated during the create process are added
to the definitions in the output file.

## Abbreviation

## Examples
Default values for key environment variables in the **Egeria Workspaces** environment:
* EGERIA_ROOT_PATH=/home/jovyan
* EGERIA_INBOX_PATH=loading-bay/dr-egeria-inbox
* EGERIA_OUTBOX_PATH=distribution-hub/dr-egeria-outbox
* EGERIA_LOCAL_QUALIFIER=EGERIA

## Usage
During processing, informational messages will be displayed on the console. Please see the term entry for `Validate` for
further description.

The EGERIA_ROOT_PATH is generally going to be set depending on what kind of environment you are using. For **Egeria Workspaces**,
when using the Jupyter environment, it will be set to Jupyter's default, which is `/home/jovyan`.
* The location of the input file is based on the environment variables EGERIA_ROOT_PATH and EGERIA_INPUT_PATH.
* The output file will be written to the directory specified by the EGERIA_ROOT_PATH and EGERIA_OUTPUT_PATH environment
variables.

## Version
0.1
## Status

DRAFT

## Qualified Name

___

___



# Update Term

## Term Name 

Create Glossary

## Aliases


## Summary
Create a new Egeria glossary.

## Description
Create a new Egeria glossary with attributes for:
* Language
* Description
* Usage

## Examples


## Usage
| Attribute Name | Input Required? | Read Only | Generated/Default? | Unique? | Notes                                                                                                    |
|:---------------|:----------------|-----------|:-------------------|:--------|:---------------------------------------------------------------------------------------------------------|
| Glossary Name  | Yes             | No        | No                 | No      | A display name (informal name).                                                                          |
| Language       | No              | No        | No                 | No      | The primary language for the glossary.                                                                   |
| Description    | No              | No        | No                 | No      | A textual description of this glossary.                                                                  |
| Usage          | No              | No        | No                 | No      | How the glossary is meant to be used, and by whom.                                                       |
| Qualified Name | Maybe           | No        | Yes                | Yes     | The qualified name can either be provided by the user or generated. If generated, a pattern is followed. |
| GUID           | No              | Yes       | Yes                | Yes     | GUIDs are always generated by Egeria. They are meant for automation, not people.                         |

## Version Identifier
0.1

## Qualified Name
Term::Create Glossary::0.1

## Status
DRAFT

## In Glossary
Glossary::Egeria-Markdown

## Categories
Category::Writing Dr.Egeria Markdown

## Guid
b671c949-0914-4ab0-8899-f6db8ac1a31d




# Update Term

## Term Name 

Update Glossary

## Aliases


## Summary
Updates the definition of an existing Egeria glossary. The provided values **Replace** all original values.

## Description
This updates an existing Egeria glossary. The supplied attribute values are merged into the existing definition.

## Examples


## Usage
| Attribute Name | Input Required? | Read Only | Generated/Default? | Unique? | Notes                                                                                                    |
|:---------------|:----------------|-----------|:-------------------|:--------|:---------------------------------------------------------------------------------------------------------|
| Glossary Name  | Yes             | No        | No                 | No      | A display name (informal name).                                                                          |
| Language       | No              | No        | No                 | No      | The primary language for the glossary.                                                                   |
| Description    | No              | No        | No                 | No      | A textual description of this glossary.                                                                  |
| Usage          | No              | No        | No                 | No      | How the glossary is meant to be used, and by whom.                                                       |
| Qualified Name | Maybe           | No        | Yes                | Yes     | The qualified name can either be provided by the user or generated. If generated, a pattern is followed. |
| GUID           | No              | Yes       | Yes                | Yes     | GUIDs are always generated by Egeria. They are meant for automation, not people.                         |

## Version Identifier
0.1

## Qualified Name
Term::Update Glossary::0.1

## Status
DRAFT

## In Glossary
Glossary::Egeria-Markdown

## Categories
Category::Writing Dr.Egeria Markdown

## Guid
83117bf4-b74f-4411-8b19-a367c72b2acc




# Update Term

## Term Name 

Create Category

## Aliases


## Summary
Create a new glossary category in the specified glossary.

## Description
Creates a new glossary category in the specified glossary. Categories can be used to categorize glossary terms.
A category has an optional description.

## Examples


## Usage
Glossary categories have the following attributes:

| Attribute Name  | Input Required? | Read Only | Generated/Default? | Unique? | Notes                                                                                                    |
|:----------------|:----------------|-----------|:-------------------|:--------|:---------------------------------------------------------------------------------------------------------|
| Category Name   | Yes             | No        | No                 | No      | A display name (informal name).                                                                          |
| Owning Glossary | Yes             | No        | No                 | Yes     | This is the qualified name of the glossary that owns this category.                                      |
| Description     | No              | No        | No                 | No      | A textual description of this category                                                                   |
| Qualified Name  | No              | No        | Yes                | Yes     | The qualified name can either be provided by the user or generated. If generated, a pattern is followed. |
| GUID            | No              | Yes       | Yes                | Yes     | GUIDs are always generated by Egeria. They are meant for automation, not people.                         |
|

## Version Identifier
0.1

## Qualified Name
Term::Create Category::0.1

## Status
DRAFT

## In Glossary
Glossary::Egeria-Markdown

## Categories
Category::Writing Dr.Egeria Markdown

## Guid
2d39bc48-3ea3-41f8-b1c0-0326c06a501c




# Update Term

## Term Name 

Update Category

## Aliases


## Summary
Updates the definition of an existing Egeria category.

## Description
Updates the definition of an existing category. Currently the only field that can be updated is the `Description`.
The provided values **Replace** all original values.

## Examples


## Usage
Glossary categories have the following attributes:

| Attribute Name  | Input Required? | Read Only | Generated/Default? | Unique? | Notes                                                                                                    |
|:----------------|:----------------|-----------|:-------------------|:--------|:---------------------------------------------------------------------------------------------------------|
| Category Name   | Yes             | No        | No                 | No      | A display name (informal name).                                                                          |
| Owning Glossary | Yes             | No        | No                 | Yes     | This is the qualified name of the glossary that owns this category.                                      |
| Description     | No              | No        | No                 | No      | A textual description of this category                                                                   |
| Qualified Name  | No              | No        | Yes                | Yes     | The qualified name can either be provided by the user or generated. If generated, a pattern is followed. |
| GUID            | No              | Yes       | Yes                | Yes     | GUIDs are always generated by Egeria. They are meant for automation, not people.                         |

## Version Identifier
0.1

## Qualified Name
Term::Update Category::0.1

## Status
DRAFT

## In Glossary
Glossary::Egeria-Markdown

## Categories
Category::Writing Dr.Egeria Markdown

## Guid
1bb93741-d146-4e96-a25d-062af5a62660




# Update Term

## Term Name 

Create Term

## Aliases


## Summary
Create a new glossary term with the given attributes in the specified Egeria glossary.

## Description
A glossary term represents a semantic definition. Most commonly business terminology and concepts. The flexibility and ability to structure
glossary terms leads to many more uses as well.

## Examples


## Usage
A glossary term has the following core attributes. Additional attributes, relationships and classifications can be added.

| Attribute Name     | Input Required? | Read Only | Generated/Default? | Unique? | Notes                                                                                                    |
|:-------------------|:----------------|:----------|:-------------------|:--------|:---------------------------------------------------------------------------------------------------------|
| Term Name          | Yes             | No        | No                 | No      | A display name (informal name).                                                                          |
| Owning Glossary    | Yes             | No        | No                 | Yes     | This is the qualified name of the glossary that owns this term.                                          |
| Aliases            | No              | No        | No                 | No      | Allows us to define aliases for a term name tha can be found with search.                                |
| Summary            | No              | No        | No                 | No      | A summary description of a term.                                                                         |
| Categories         | No              | No        | No                 | Yes     | This is the name of the category. Multiple categories can be assigned, separated by a `,` or line.       |
| Description        | No              | No        | No                 | No      | A textual description of this term.                                                                      |
| Examples           | No              | No        | No                 | No      | Examples demonstrating the term.                                                                         |
| Usage              | No              | No        | No                 | No      | Usage details for the term.                                                                              |
| Version Identifier | No              | No        | No                 | No      | A user specified version identifier useed in publishing a term version for usage.                        |
| Status             | No              | No        | Yes - DRAFT        | No      | Valid values are "DRAFT", "PREPARED", "PROPOSED", "APPROVED", "REJECTED", ACTIVE", "DEPRECATED", "OTHER" |
| Qualified Name     | No              | No        | No                 | Yes     | The qualified name can either be provided by the user or generated. If generated, a pattern is followed. |
| GUID               | No              | Yes       | Yes                | Yes     | GUIDs are always generated by Egeria. They are meant for automation, not people.                         |
| Update Description | No              | No        | No                 | No      | Updates can have an update description added to the term's note log.                                     |

## Version Identifier
0.1

## Qualified Name
Term::Create Term::0.1

## Status
DRAFT

## In Glossary
Glossary::Egeria-Markdown

## Categories
Category::Writing Dr.Egeria Markdown

## Guid
b98539d6-649a-4845-b772-a0d402b61e3f




# Update Term

## Term Name 

Update Term

## Aliases


## Summary
Updates the definition of an existing Egeria glossary term.

## Description
Updates an existing glossary term. The provided values **Replace** all original values.
A glossary term represents a semantic definition. Most commonly business terminology and concepts. The flexibility and ability to structure
glossary terms leads to many more uses as well.

## Examples


## Usage
A glossary term has the following core attributes. Additional attributes, relationships and classifications can be added.
| Attribute Name     | Input Required? | Read Only | Generated/Default? | Unique? | Notes                                                                                                    |
|:-------------------|:----------------|:----------|:-------------------|:--------|:---------------------------------------------------------------------------------------------------------|
| Term Name          | Yes             | No        | No                 | No      | A display name (informal name).                                                                          |
| Owning Glossary    | Yes             | No        | No                 | Yes     | This is the qualified name of the glossary that owns this term.                                          |
| Aliases            | No              | No        | No                 | No      | Allows us to define aliases for a term name tha can be found with search.                                |
| Summary            | No              | No        | No                 | No      | A summary description of a term.                                                                         |
| Categories         | No              | No        | No                 | Yes     | This is the name of the category. Multiple categories can be assigned, separated by a `,` or line.       |
| Description        | No              | No        | No                 | No      | A textual description of this term.                                                                      |
| Examples           | No              | No        | No                 | No      | Examples demonstrating the term.                                                                         |
| Usage              | No              | No        | No                 | No      | Usage details for the term.                                                                              |
| Version Identifier | No              | No        | No                 | No      | A user specified version identifier useed in publishing a term version for usage.                        |
| Status             | No              | No        | Yes - DRAFT        | No      | Valid values are "DRAFT", "PREPARED", "PROPOSED", "APPROVED", "REJECTED", ACTIVE", "DEPRECATED", "OTHER" |
| Qualified Name     | No              | No        | No                 | Yes     | The qualified name can either be provided by the user or generated. If generated, a pattern is followed. |
| GUID               | No              | Yes       | Yes                | Yes     | GUIDs are always generated by Egeria. They are meant for automation, not people.                         |
| Update Description | No              | No        | No                 | No      | Updates can have an update description added to the term's note log.                                     |

## Version Identifier
0.1

## Qualified Name
Term::Update Term::0.1

## Status
DRAFT

## In Glossary
Glossary::Egeria-Markdown

## Categories
Category::Writing Dr.Egeria Markdown

## Guid
790bc752-189c-4ae7-a03e-b2c280de55a1




# Update Term

## Term Name 

Provenance

## Aliases


## Summary
The `Provenance` command is used by Dr.Egeria to indicate the history of the Dr.Egeria input file.

## Description
When a Dr.Egeria input file is processed, it will look for a `Provenance` command. If one is not found,
a new `Provenance` section will be created. Processing information (name of the file and timestamp) are appended
to this section. If a Dr.Egeria file is processed multiple times, a history of this processing will be created (presuming
the text is not deleted by the user). This simple, informal mechanism can be useful for basic scenarios. More sophisticated
scenarios would make use of more robust mechanisms such as version control and document management systems.
Additionally, it is important to note that Egeria automatically maintains an audit history for each element. Additional
features for maintaining an update journal are also planned for Dr.Egeria.

## Examples


## Usage
Provenancce information is filled out automatically by Dr.Egeria.

## Version Identifier
0.1

## Qualified Name
Term::Provenance::0.1

## Status
DRAFT

## In Glossary
Glossary::Egeria-Markdown

## Categories
Category::Processing Dr.Egeria Markdown

## Guid
008fe9ed-c0d7-4f44-906f-23dd3454f346




# Update Term

## Term Name 

Create Personal Project

## Aliases


## Summary
This command defines a new personal project within Egeria.

## Description
As the name suggests, personal projects are used by individuals to help projects that only involve them. While Egeria supports
several kinds of project, personal projects may be of particular interest to data scientists looking to track their
experiments.

## Examples


## Usage
Dr.Egeria processes uses the following attributes for a personal project:
| Attribute Name     | Input Required? | Read Only | Generated/Default? | Unique? | Notes                                                                                                    |
|:-------------------|:----------------|-----------|:-------------------|:--------|:---------------------------------------------------------------------------------------------------------|
| Project Name       | Yes             | No        | No                 | No      | A display name (informal name) of the project.                                                           |
| Project Identifier | No              | No        | No                 | No      | An optional shorthand name for the project.                                                              |
| Project Status     | No              | No        | No                 | No      | Status of the project, often from a list of Valid Values.                                                |
| Description        | No              | No        | No                 | No      | A textual description of this project.                                                                   |
| Project Phase      | No              | No        | No                 | No      | Phase of the project, often from a list of Valid Values.                                                 |
| Project Health     | No              | No        | No                 | No      | Health of the project, often from a list of Valid Values.                                                |
| Start Date         | No              | No        | No                 | No      | Start date in the form YYYY-MM-DD                                                                        |
| Planned End Date   | No              | No        | No                 | No      | Planned completion date of the form YYY-MM-DD                                                            |
| Qualified Name     | No              | No        | Yes                | Yes     | The qualified name can either be provided by the user or generated. If generated, a pattern is followed. |
| GUID               | No              | Yes       | Yes                | Yes     | GUIDs are always generated by Egeria. They are meant for automation, not people.                         |

## Version Identifier
0.1

## Qualified Name
Term::Create Personal Project::0.1

## Status
DRAFT

## In Glossary
Glossary::Egeria-Markdown

## Categories
Category::Writing Dr.Egeria Markdown

## Guid
96226ff1-d168-4e56-adab-9b16496e7882




# Update Term

## Term Name 

Update Personal Project

## Aliases


## Summary
Update an existing Egeria personal project.

## Description
Update an en existing Egeria personal project.

## Examples


## Usage
Dr.Egeria processes uses the following attributes for a personal project:
| Attribute Name     | Input Required? | Read Only | Generated/Default? | Unique? | Notes                                                                                                    |
|:-------------------|:----------------|-----------|:-------------------|:--------|:---------------------------------------------------------------------------------------------------------|
| Project Name       | Yes             | No        | No                 | No      | A display name (informal name) of the project.                                                           |
| Project Identifier | No              | No        | No                 | No      | An optional shorthand name for the project.                                                              |
| Project Status     | No              | No        | No                 | No      | Status of the project, often from a list of Valid Values.                                                |
| Description        | No              | No        | No                 | No      | A textual description of this project.                                                                   |
| Project Phase      | No              | No        | No                 | No      | Phase of the project, often from a list of Valid Values.                                                 |
| Project Health     | No              | No        | No                 | No      | Health of the project, often from a list of Valid Values.                                                |
| Start Date         | No              | No        | No                 | No      | Start date in the form YYYY-MM-DD                                                                        |
| Planned End Date   | No              | No        | No                 | No      | Planned completion date of the form YYY-MM-DD                                                            |
| Qualified Name     | No              | No        | Yes                | Yes     | The qualified name can either be provided by the user or generated. If generated, a pattern is followed. |
| GUID               | No              | Yes       | Yes                | Yes     | GUIDs are always generated by Egeria. They are meant for automation, not people.                         |

## Version Identifier
0.2

## Qualified Name
Term::Update Personal Project::0.2

## Status
DRAFT

## In Glossary
Glossary::Egeria-Markdown

## Categories
Category::Writing Dr.Egeria Markdown

## Guid
bcd12bf2-b13e-4df1-87ee-e3c26507be4b




# Update Term

## Term Name 

Create Term-Term Relationship

## Aliases


## Summary
Creates a relationship between two terms.

## Description
Creates a relationship between two terms. Supported relationship types are:\n
- `Synonym` - A term is a synonym of another term.
- `Antonym` - A term is an antonym of another term.
- `Translation` - A term is a translation of another term.
- `RelatedTerm` - A term is related to another term.
- `ReplacementTerm` - A term is a replacement for another term.
- `ValidValue` - A term is a valid value for another term.
- `TermISATYPEOFRelationship` - A term is a type of relationship defined by another term.
- `TermTYPEDBYRelationship` - A term is typed by another term.
- `TermHASARelationship` - A term HASA another term.
- `TermISARelationship` - A term is a relationship defined by another term.
- `ISARelationship` - A relationship is defined by another term.,
- `TermHASARelationship` - A term HASA another term.
- `TermISARelationship` - A term is a relationship defined by another term.
- `ISARelationship` - A term ISA another term.

## Examples


## Usage
Dr.Egeria processes uses the following attributes for a personal project:
| Attribute Name    | Input Required? | Read Only | Generated/Default? | Unique? | Notes                                                                                                     |
|:------------------|:----------------|-----------|:-------------------|:--------|:----------------------------------------------------------------------------------------------------------|
| Term 1 Name       | Yes             | No        | No                 | No      | The name of the first term.                                                                               |
| Term 2 Name       | Yes             | No        | No                 | No      | The name of the second term.                                                                              |
| Relationship Type | Yes             | No        | No                 | No      | The type of relationship between the two terms.                                                           |

## Version Identifier


## Qualified Name
Term::Create Term-Term Relationship

## Status
DRAFT

## In Glossary
Glossary::Egeria-Markdown

## Categories
Category::Writing Dr.Egeria Markdown

## Guid
8eedf217-20c3-4162-bbcc-982ab5cdce7c




# Update Term

## Term Name 

List Glossaries

## Aliases


## Summary
List the glossaries that are defined in Egeria.

## Description
List the glossaries that are defined in Egeria.

## Examples


## Usage
List Gloosaries has the following attributes:
| Attribute Name | Input Required? | Read Only? | Generated/Default?               | Unique? | Notes                                     |
|----------------|-----------------|------------|----------------------------------|---------|-------------------------------------------|
| Search String  | No              | No         | default is All glossaries        | No      |                                           |
| Output Format  | No              | No         | default is Markdown List (table) | No      | options are: LIST, DICT, MD, FORM, REPORT |
Lets describe the output formats a bit further:
* LIST - This is the default format. It returns a markdown table of the glossaries.
* DICT - This returns a python dictionary (or JSON representation) of the glossaries.
* MD - This returns markdown text of the glossaries.
* FORM - This returns a Dr.Egeria markdown form designed to be used as a starting point for updating the glossary definitions.
* REPORT - This returns markdown text of the glossaries that is designed to be more readable and perhaps suitable to be used in a report.

## Version Identifier


## Qualified Name
Term::List Glossaries

## Status
DRAFT

## In Glossary
Glossary::Egeria-Markdown

## Categories
Category::Writing Dr.Egeria Markdown

## Guid
ac337ff3-efe7-42a3-82f2-6afcc2c66dd2




# Update Term

## Term Name 

List Categories

## Aliases
List Glossary Categories

## Summary
List the categories that are defined in a glossary.

## Description
List the categories that are defined in Egeria. Optionally filter based on a search string.

## Examples


## Usage
List Categories has the following attributes:
| Attribute Name | Input Required? | Read Only? | Generated/Default?               | Unique? | Notes                                     |
|----------------|-----------------|------------|----------------------------------|---------|-------------------------------------------|
| Search String  | No              | No         | default is All glossaries        | No      |                                           |
| Output Format  | No              | No         | default is Markdown List (table) | No      | options are: LIST, DICT, MD, FORM, REPORT |
Lets describe the output formats a bit further:
* LIST - This is the default format. It returns a markdown table of the categories.
* DICT - This returns a python dictionary (or JSON representation) of the categories.
* MD - This returns markdown text of the categories.
* FORM - This returns a Dr.Egeria markdown form designed to be used as a starting point for updating the category definitions.
* REPORT - This returns markdown text of the categories that is designed to be more readable and perhaps suitable to be used in a report.

## Version Identifier


## Qualified Name
Term::List Categories

## Status
DRAFT

## In Glossary
Glossary::Egeria-Markdown

## Categories
Category::Writing Dr.Egeria Markdown

## Guid
e2b386d7-0edd-47e9-9dc1-5969b01fc5b9






# Update Term

## Term Name 

List Terms

## Aliases
List Glossary Terms

## Summary
List the terms that are defined in a glossary. O

## Description
List the terms that are defined in Egeria. optionally filter based on a search string and glossary name.

## Examples


## Usage
List Categories has the following attributes:
| Attribute Name | Input Required? | Read Only? | Generated/Default?               | Unique? | Notes                                     |
|----------------|-----------------|------------|----------------------------------|---------|-------------------------------------------|
| Search String  | No              | No         | default is All glossaries        | No      |                                           |
| Output Format  | No              | No         | default is Markdown List (table) | No      | options are: LIST, DICT, MD, FORM, REPORT |
Lets describe the output formats a bit further:
* LIST - This is the default format. It returns a markdown table of the categories.
* DICT - This returns a python dictionary (or JSON representation) of the categories.
* MD - This returns markdown text of the categories.
* FORM - This returns a Dr.Egeria markdown form designed to be used as a starting point for updating the category definitions.
* REPORT - This returns markdown text of the categories that is designed to be more readable and perhaps suitable to be used in a report.

## Version Identifier


## Qualified Name
Term::List Terms

## Status
DRAFT

## In Glossary
Glossary::Egeria-Markdown

## Categories
Category::Writing Dr.Egeria Markdown

## Guid
5c560000-70d6-42e9-ba64-db5467212b7d


# Create Term

## Qualified Name
Term::List Categories

## GUID
e2b386d7-0edd-47e9-9dc1-5969b01fc5b9

## Term Name

List Categories

## Owning Glossary

Glossary::Egeria-Markdown

## Categories

Writing Dr.Egeria Markdown

## Summary

List the categories that are defined in a glossary.

## Description
List the categories that are defined in Egeria. Optionally filter based on a search string.

## Alias
List Glossary Categories

## Abbreviation

## Examples

## Usage

List Categories has the following attributes:


| Attribute Name | Input Required? | Read Only? | Generated/Default?               | Unique? | Notes                                     |
|----------------|-----------------|------------|----------------------------------|---------|-------------------------------------------|
| Search String  | No              | No         | default is All glossaries        | No      |                                           |
| Output Format  | No              | No         | default is Markdown List (table) | No      | options are: LIST, DICT, MD, FORM, REPORT |

Lets describe the output formats a bit further:

* LIST - This is the default format. It returns a markdown table of the categories.
* DICT - This returns a python dictionary (or JSON representation) of the categories.
* MD - This returns markdown text of the categories.
* FORM - This returns a Dr.Egeria markdown form designed to be used as a starting point for updating the category definitions.
* REPORT - This returns markdown text of the categories that is designed to be more readable and perhaps suitable to be used in a report.


___




# Update Term

## Term Name 

List Term History

## Aliases
Term History

## Summary
List the version history of a term.

## Description
List the terms that are defined in Egeria. optionally filter based on a search string and glossary name.

## Examples


## Usage
List Term History has the following attributes:
| Attribute Name | Input Required? | Read Only? | Generated/Default?               | Unique? | Notes                                     |
|----------------|-----------------|------------|----------------------------------|---------|-------------------------------------------|
| Term Name      | Yes             | No         | No                               | No      | can be qualified name or display name     |
| Output Format  | No              | No         | default is Markdown List (table) | No      | options are: LIST, DICT |
Lets describe the output formats a bit further:
* LIST - This is the default format. It returns a markdown table of the categories.
* DICT - This returns a python dictionary (or JSON representation) of the categories.

## Version Identifier


## Qualified Name
Term::List Term History

## Status
DRAFT

## In Glossary
Glossary::Egeria-Markdown

## Categories
Category::Writing Dr.Egeria Markdown

## Guid
08a4cb1e-b3e5-4369-8bbe-dbd0a155896d





# Update Term

## Term Name 

List Term Revision History

## Aliases
List Term Update History

## Summary
List the note log documenting the revision history of a term.

## Description
Lis the note log documenting the revision history of a term. Entries in the note log are created when a term is updated and
the `Update Description` attribute is set.

## Examples


## Usage
List Term Revision History has the following attributes:
| Attribute Name | Input Required? | Read Only? | Generated/Default?               | Unique? | Notes                                 |
|----------------|-----------------|------------|----------------------------------|---------|---------------------------------------|
| Term Name      | Yes             | No         | No                               | No      | can be qualified name or display name |
| Output Format  | No              | No         | default is Markdown List (table) | No      | options are: LIST, DICT & MD          |
Lets describe the output formats a bit further:
* LIST - This is the default format. It returns a markdown table of the categories.
* DICT - This returns a python dictionary (or JSON representation) of the categories.
* MD - This returns markdown text of the revision history.

## Version Identifier


## Qualified Name
Term::List Term Revision History

## Status
DRAFT

## In Glossary
Glossary::Egeria-Markdown

## Categories
Category::Writing Dr.Egeria Markdown

## Guid
0c55f322-b519-47c4-a690-1a69053355f7





# Update Term

## Term Name 

List Term Details

## Aliases


## Summary
List the details of a term, including related terms.

## Description
List the details of a term, including related terms.

## Examples


## Usage
List Term Details has the following attributes:
| Attribute Name | Input Required? | Read Only? | Generated/Default?               | Unique? | Notes                                 |
|----------------|-----------------|------------|----------------------------------|---------|---------------------------------------|
| Term Name      | Yes             | No         | No                               | No      | can be qualified name or display name |
| Output Format  | No              | No         | default is Markdown List (table) | No      | options are: DICT & REPORT            |
Lets describe the output formats a bit further:
* DICT - This returns a python dictionary (or JSON representation) of the categories.
* REPORT - This returns markdown text of the term details in a report format.

## Version Identifier


## Qualified Name
Term::List Term Details

## Status
DRAFT

## In Glossary
Glossary::Egeria-Markdown

## Categories
Category::Writing Dr.Egeria Markdown

## Guid
00585a82-0f7d-45ef-9b87-7078665917a9




# Update Term

## Term Name 

List Glossary Structure

## Aliases


## Summary
List the category structure of a glossary.

## Description
List the category structure of a glossary.

## Examples


## Usage
List Glossary Structure has the following attributes:

| Attribute Name | Input Required? | Read Only? | Generated/Default?               | Unique? | Notes                                 |
|----------------|-----------------|------------|----------------------------------|---------|---------------------------------------|
| Glossary Name  | Yes             | No         | No                               | No      | can be qualified name or display name |
| Output Format  | No              | No         | default is Markdown List (table) | No      | options are: DICT, LIST & REPORT      |
Lets describe the output formats a bit further:
* DICT - This returns a python dictionary (or JSON representation) of the categories.
* REPORT - This returns markdown text of the term details in a report format with category nesting shown.
* LIST - This returns a markdown table of the glossary structure.

## Version Identifier


## Qualified Name
Term::List Glossary Structure

## Status
DRAFT

## In Glossary
Glossary::Egeria-Markdown

## Categories
Category::Writing Dr.Egeria Markdown

## Guid
c55d28e6-a04e-448e-9bcc-60dce8b17fe5




# All Glossary Commands have Terms created.

Whew! Getting to be quite a number of glossary commands. There will be more in the future but this gives us a robust start
for creating and managing glossaries. Note that while Dr.Egeria supports creation and updates, we have chosen to leave
deletions to explicit `hey_egeria` commands and `pyegeria` method calls - for safety.

Now lets take a look at our handiwork by listing the commands in the `Egeria-Markdown` glossary.

___


# Term List for search string: `*`

# Terms Table

Terms found from the search string: `All`

| Term Name | Qualified Name | Aliases | Summary | Glossary | Categories | 
|-------------|-------------|-------------|-------------|-------------|-------------|
| List Glossaries | Term::List Glossaries |  | List the glossaries that are defined in Egeria. | Glossary::Egeria-Markdown | Writing Dr.Egeria Markdown | 
| Update Glossary | Term::Update Glossary::0.1 |  | Updates the definition of an existing Egeria glossary. The provided values **Replace** all original values. | Glossary::Egeria-Markdown | Writing Dr.Egeria Markdown | 
| List Term Revision History | Term::List Term Revision History | List Term Update History | List the note log documenting the revision history of a term. | Glossary::Egeria-Markdown | Writing Dr.Egeria Markdown | 
| List Terms | Term::List Terms | List Glossary Terms | List the terms that are defined in a glossary. O | Glossary::Egeria-Markdown | Writing Dr.Egeria Markdown | 
| List Glossary Structure | Term::List Glossary Structure |  | List the category structure of a glossary. | Glossary::Egeria-Markdown | Writing Dr.Egeria Markdown | 
| List Term History | Term::List Term History | Term History | List the version history of a term. | Glossary::Egeria-Markdown | Writing Dr.Egeria Markdown | 
| Provenance | Term::Provenance::0.1 |  | The `Provenance` command is used by Dr.Egeria to indicate the history of the Dr.Egeria input file. | Glossary::Egeria-Markdown | Processing Dr.Egeria Markdown | 
| Update Category | Term::Update Category::0.1 |  | Updates the definition of an existing Egeria category. | Glossary::Egeria-Markdown | Writing Dr.Egeria Markdown | 
| Validate | Term::Validate::.1 |  | A processing directive to Dr.Egeria to request that the input text be validated for conformance to Dr. Egeria syntax with the results being displayed and, depending on results, an output file incorporating suggested changes will be produced. | Glossary::Egeria-Markdown | Processing Dr.Egeria Markdown | 
| Create Category | Term::Create Category::0.1 |  | Create a new glossary category in the specified glossary. | Glossary::Egeria-Markdown | Writing Dr.Egeria Markdown | 
| Create Personal Project | Term::Create Personal Project::0.1 |  | This command defines a new personal project within Egeria. | Glossary::Egeria-Markdown | Writing Dr.Egeria Markdown | 
| Source | Term::Source::0.2 |  | Source of the markdown content. | Glossary::Egeria-Markdown | --- | 
| Create Term-Term Relationship | Term::Create Term-Term Relationship |  | Creates a relationship between two terms. | Glossary::Egeria-Markdown | Writing Dr.Egeria Markdown | 
| Directive | Term::Directive::0.1 |  | A directive defines how the command is to be processed. | Glossary::Egeria-Markdown | Processing Dr.Egeria Markdown | 
| Create Term | Term::Create Term::0.1 |  | Create a new glossary term with the given attributes in the specified Egeria glossary. | Glossary::Egeria-Markdown | Writing Dr.Egeria Markdown | 
| Command | Term::Command::0.2 |  | Commands are how a user of the Dr.Egeria markdown language requests an action. | Glossary::Egeria-Markdown | Processing Dr.Egeria Markdown, Writing Dr.Egeria Markdown | 
| Create Glossary | Term::Create Glossary::0.1 |  | Create a new Egeria glossary. | Glossary::Egeria-Markdown | Writing Dr.Egeria Markdown | 
| List Categories | Term::List Categories | List Glossary Categories | List the categories that are defined in a glossary. | Glossary::Egeria-Markdown | Writing Dr.Egeria Markdown | 
| Update Personal Project | Term::Update Personal Project::0.2 |  | Update an existing Egeria personal project. | Glossary::Egeria-Markdown | Writing Dr.Egeria Markdown | 
| Display | Term::Display |  | This is a processing directive to Dr.Egeria to request that the input text be processed for display only. | Glossary::Egeria-Markdown | Processing Dr.Egeria Markdown | 
| List Term Details | Term::List Term Details |  | List the details of a term, including related terms. | Glossary::Egeria-Markdown | Writing Dr.Egeria Markdown | 
| Update Term | Term::Update Term::0.1 |  | Updates the definition of an existing Egeria glossary term. | Glossary::Egeria-Markdown | Writing Dr.Egeria Markdown | 


# Next steps

In our next installment we will create a category hierarchy and update some terms to use it.






# Provenance:
 
* Derived from processing file dr_egeria_intro_part3.md on 2025-04-24 20:19
