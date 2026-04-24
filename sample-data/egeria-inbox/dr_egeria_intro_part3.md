### Adding more to the Egeria-Markdown Glossary

In the first two files created the Egeria-Markdown glossary with a few terms. In the second, we added a couple of
categories and then updated the existing terms to use them. In this installment, we will add a number of terms to the
glossary to make it a truly useful aid for the Dr.Egeria user. Once we have added the terms, we'll discuss how we can
continue to work with the terms using the `hey_egeria` commands.
___ 

## Create Term

### Display Name

Display

### Glossary Name

Glossary::Egeria-Markdown

### Folders

Processing Dr.Egeria Markdown

### Summary

This is a processing directive to Dr.Egeria to request that the input text be processed for display only.

### Description

This is a processing directive to Dr.Egeria commands to request that the input text be processed and displaying. This is
useful to validate that the command processor is able to open the input text and shows that the environment is able to
process the text.

### Abbreviation

### Examples

### Usage

### Version

### Content Status

DRAFT

### Qualified Name

___


## Create Term

### Display Name

Validate

### Glossary Name

Glossary::Egeria-Markdown

### Folders

Processing Dr.Egeria Markdown

### Summary
A processing directive to Dr.Egeria to request that the input text be validated for conformance to Dr. Egeria syntax
with the results being displayed and, depending on results, an output file incorporating suggested changes will be produced.
### Description
A processing directive to Dr.Egeria to request that the input text be validated for conformance to Dr. Egeria syntax. 

The results are displayed in the console, and include labeled messages. The labels may be:
* Info - just an information notice, for example, an optional field is empty.
* Warning - an issue was found, but we can automatically try to repair it or it doesn't prevent further processing.
* Error - A non-recoverable error input error was found - this command won't be processed further - for example if we encounter
a `Create Term` command and find that the term already exists.

Additional descriptive messages are also displayed. In some cases, for example if we detect a `Create` command for an 
object that already exists, we will also produce an output file that replaces the `Create` with an `Update` command.


### Abbreviation

### Examples
Default values for key environment variables in the **Egeria Workspaces** environment:
* EGERIA_ROOT_PATH=/home/jovyan
* EGERIA_INBOX_PATH=loading-bay/dr-egeria-inbox
* EGERIA_OUTBOX_PATH=distribution-hub/dr-egeria-outbox
* EGERIA_LOCAL_QUALIFIER=EGERIA

So place input files in the `loading-bay/dr-egeria-inbox` folder and look for output files in `distribution-hub/dr-egeria-outbox`.

### Usage
The EGERIA_ROOT_PATH is generally going to be set depending on what kind of environment you are using. For **Egeria Workspaces**,
when using the Jupyter environment, it will be set to Jupyter's default, which is `/home/jovyan`. 
* The location of the input file is based on the environment variables EGERIA_ROOT_PATH and EGERIA_INPUT_PATH.
* The output file will be written to the directory specified by the EGERIA_ROOT_PATH and EGERIA_OUTPUT_PATH environment
variables.

### Version Identifier
.1
### Content Status

DRAFT

### Qualified Name

___

## Create Term

### Display Name

Process

### Glossary Name

Glossary::Egeria-Markdown

### Folders

Processing Dr.Egeria Markdown

### Summary
The process directive indicates that we should apply the requested commands to Egeria if they are valid. 

### Description
The process directive indicates that we should apply the requested commands to Egeria if they are valid. Informational 
messages are provided on the console. A new file is produced that reflects the updates made and is designed to make
it easy to make further changes using the contents. For example, `Create` commands from the input file are written
out as `Update` statements in the output file. Qualified names and GUIDs generated during the create process are added
to the definitions in the output file.

### Abbreviation

### Examples
Default values for key environment variables in the **Egeria Workspaces** environment:
* EGERIA_ROOT_PATH=/home/jovyan
* EGERIA_INBOX_PATH=loading-bay/dr-egeria-inbox
* EGERIA_OUTBOX_PATH=distribution-hub/dr-egeria-outbox
* EGERIA_LOCAL_QUALIFIER=EGERIA

### Usage
During processing, informational messages will be displayed on the console. Please see the term entry for `Validate` for 
further description.

The EGERIA_ROOT_PATH is generally going to be set depending on what kind of environment you are using. For **Egeria Workspaces**,
when using the Jupyter environment, it will be set to Jupyter's default, which is `/home/jovyan`. 
* The location of the input file is based on the environment variables EGERIA_ROOT_PATH and EGERIA_INPUT_PATH.
* The output file will be written to the directory specified by the EGERIA_ROOT_PATH and EGERIA_OUTPUT_PATH environment
variables.

### Version Identifier
0.1
### Content Status

DRAFT

### Qualified Name

___

## Create Term

### Display Name

Create Glossary

### Glossary Name

Glossary::Egeria-Markdown

### Folders

Writing Dr.Egeria Markdown

### Summary
Create a new Egeria glossary.

### Description
Create a new Egeria glossary with attributes for:
* Language
* Description
* Usage

### Abbreviation

### Examples


### Usage

| Attribute Name     | Input Required? | Read Only | Generated/Default? | Unique? | Notes                                                                                                    |
|:-------------------|:----------------|-----------|:-------------------|:--------|:---------------------------------------------------------------------------------------------------------|
| Glossary Name      | Yes             | No        | No                 | No      | A display name (informal name).                                                                          |
| Language           | No              | No        | No                 | No      | The primary language for the glossary.                                                                   |
| Description        | No              | No        | No                 | No      | A textual description of this glossary.                                                                  |
| Usage              | No              | No        | No                 | No      | How the glossary is meant to be used, and by whom.                                                       |
| Purpose            | No              | No        | No                 | No      | An optional purpose for the glossary.                                                                    |
| Version Identifier | No              | No        | No                 | No      | An optional version identifier.                                                                          |
| Qualified Name     | Maybe           | No        | Yes                | Yes     | The qualified name can either be provided by the user or generated. If generated, a pattern is followed. |
| GUID               | No              | Yes       | Yes                | Yes     | GUIDs are always generated by Egeria. They are meant for automation, not people.                         |


### Version Identifier
0.1
### Content Status

DRAFT

### Qualified Name

___

## Create Term

### Display Name

Update Glossary

### Glossary Name

Glossary::Egeria-Markdown

### Folders

Writing Dr.Egeria Markdown

### Summary
Updates the definition of an existing Egeria glossary. The provided values **Replace** all original values.

### Description
This updates an existing Egeria glossary. The supplied attribute values are merged into the existing definition.

### Abbreviation

### Examples

### Usage


| Attribute Name | Input Required? | Read Only | Generated/Default? | Unique? | Notes                                                                                                    |
|:---------------|:----------------|-----------|:-------------------|:--------|:---------------------------------------------------------------------------------------------------------|
| Glossary Name  | Yes             | No        | No                 | No      | A display name (informal name).                                                                          |
| Language       | No              | No        | No                 | No      | The primary language for the glossary.                                                                   |
| Description    | No              | No        | No                 | No      | A textual description of this glossary.                                                                  |
| Usage          | No              | No        | No                 | No      | How the glossary is meant to be used, and by whom.                                                       |
| Qualified Name | Maybe           | No        | Yes                | Yes     | The qualified name can either be provided by the user or generated. If generated, a pattern is followed. |
| GUID           | No              | Yes       | Yes                | Yes     | GUIDs are always generated by Egeria. They are meant for automation, not people.                         |


### Version Identifier
0.1
### Content Status

DRAFT

### Qualified Name

___

## Create Term

### Display Name

Create Category

### Glossary Name

Glossary::Egeria-Markdown

### Folders

Writing Dr.Egeria Markdown

### Summary
Create a new glossary category in the specified glossary.

### Description
Creates a new glossary category in the specified glossary. Folders can be used to categorize glossary terms.
A category has an optional description.

### Abbreviation

### Examples

### Usage
Glossary categories have the following attributes:


| Attribute Name  | Input Required? | Read Only | Generated/Default? | Unique? | Notes                                                                                                    |
|:----------------|:----------------|-----------|:-------------------|:--------|:---------------------------------------------------------------------------------------------------------|
| Category Name   | Yes             | No        | No                 | No      | A display name (informal name).                                                                          |
| Glossary Name | Yes             | No        | No                 | Yes     | This is the qualified name of the glossary that owns this category.                                      |
| Description     | No              | No        | No                 | No      | A textual description of this category                                                                   |
| Qualified Name  | No              | No        | Yes                | Yes     | The qualified name can either be provided by the user or generated. If generated, a pattern is followed. |
| GUID            | No              | Yes       | Yes                | Yes     | GUIDs are always generated by Egeria. They are meant for automation, not people.                         |
                                                                                |

### Version Identifier
0.1
### Content Status

DRAFT

### Qualified Name

___

## Create Term

### Display Name

Update Category

### Glossary Name

Glossary::Egeria-Markdown

### Folders

Writing Dr.Egeria Markdown

### Summary
Updates the definition of an existing Egeria category.


### Description
Updates the definition of an existing category. Currently the only field that can be updated is the `Description`.
The provided values **Replace** all original values.
### Abbreviation

### Examples

### Usage
Glossary categories have the following attributes:


| Attribute Name  | Input Required? | Read Only | Generated/Default? | Unique? | Notes                                                                                                    |
|:----------------|:----------------|-----------|:-------------------|:--------|:---------------------------------------------------------------------------------------------------------|
| Category Name   | Yes             | No        | No                 | No      | A display name (informal name).                                                                          |
| Glossary Name | Yes             | No        | No                 | Yes     | This is the qualified name of the glossary that owns this category.                                      |
| Description     | No              | No        | No                 | No      | A textual description of this category                                                                   |
| Qualified Name  | No              | No        | Yes                | Yes     | The qualified name can either be provided by the user or generated. If generated, a pattern is followed. |
| GUID            | No              | Yes       | Yes                | Yes     | GUIDs are always generated by Egeria. They are meant for automation, not people.                         |

### Version Identifier
0.1
### Content Status

DRAFT

### Qualified Name

___

## Create Term

### Display Name

Create Term

### Glossary Name

Glossary::Egeria-Markdown

### Folders

Writing Dr.Egeria Markdown

### Summary
Create a new glossary term with the given attributes in the specified Egeria glossary.

### Description
A glossary term represents a semantic definition. Most commonly business terminology and concepts. The flexibility and ability to structure
 glossary terms leads to many more uses as well.

### Abbreviation

### Examples

### Usage
A glossary term has the following core attributes. Additional attributes, relationships and classifications can be added.


| Attribute Name     | Input Required? | Read Only | Generated/Default? | Unique? | Notes                                                                                                    |
|:-------------------|:----------------|:----------|:-------------------|:--------|:---------------------------------------------------------------------------------------------------------|
| Display Name          | Yes             | No        | No                 | No      | A display name (informal name).                                                                          |
| Glossary Name    | Yes             | No        | No                 | Yes     | This is the qualified name of the glossary that owns this term.                                          |
| Aliases            | No              | No        | No                 | No      | Allows us to define aliases for a term name tha can be found with search.                                |
| Summary            | No              | No        | No                 | No      | A summary description of a term.                                                                         |
| Folders         | No              | No        | No                 | Yes     | This is the name of the category. Multiple categories can be assigned, separated by a `,` or line.       | 
| Description        | No              | No        | No                 | No      | A textual description of this term.                                                                      |
| Examples           | No              | No        | No                 | No      | Examples demonstrating the term.                                                                         |
| Usage              | No              | No        | No                 | No      | Usage details for the term.                                                                              |
| Version Identifier | No              | No        | No                 | No      | A user specified version identifier useed in publishing a term version for usage.                        |
| Content Status             | No              | No        | Yes - DRAFT        | No      | Valid values are "DRAFT", "PREPARED", "PROPOSED", "APPROVED", "REJECTED", ACTIVE", "DEPRECATED", "OTHER" |
| Qualified Name     | No              | No        | No                 | Yes     | The qualified name can either be provided by the user or generated. If generated, a pattern is followed. |
| GUID               | No              | Yes       | Yes                | Yes     | GUIDs are always generated by Egeria. They are meant for automation, not people.                         |
| Update Description | No              | No        | No                 | No      | Updates can have an update description added to the term's note log.                                     |

### Version Identifier
0.1
### Content Status

DRAFT

### Qualified Name

___

## Create Term

### Display Name

Update Term

### Glossary Name

Glossary::Egeria-Markdown

### Folders

Writing Dr.Egeria Markdown

### Summary
Updates the definition of an existing Egeria glossary term.

### Description

Updates an existing glossary term. The provided values **Replace** all original values.
A glossary term represents a semantic definition. Most commonly business terminology and concepts. The flexibility and ability to structure
 glossary terms leads to many more uses as well.

### Abbreviation

### Examples

### Usage
A glossary term has the following core attributes. Additional attributes, relationships and classifications can be added.



| Attribute Name     | Input Required? | Read Only | Generated/Default? | Unique? | Notes                                                                                                    |
|:-------------------|:----------------|:----------|:-------------------|:--------|:---------------------------------------------------------------------------------------------------------|
| Display Name          | Yes             | No        | No                 | No      | A display name (informal name).                                                                          |
| Glossary Name    | Yes             | No        | No                 | Yes     | This is the qualified name of the glossary that owns this term.                                          |
| Aliases            | No              | No        | No                 | No      | Allows us to define aliases for a term name tha can be found with search.                                |
| Summary            | No              | No        | No                 | No      | A summary description of a term.                                                                         |
| Folders         | No              | No        | No                 | Yes     | This is the name of the category. Multiple categories can be assigned, separated by a `,` or line.       | 
| Description        | No              | No        | No                 | No      | A textual description of this term.                                                                      |
| Examples           | No              | No        | No                 | No      | Examples demonstrating the term.                                                                         |
| Usage              | No              | No        | No                 | No      | Usage details for the term.                                                                              |
| Version Identifier | No              | No        | No                 | No      | A user specified version identifier useed in publishing a term version for usage.                        |
| Content Status             | No              | No        | Yes - DRAFT        | No      | Valid values are "DRAFT", "PREPARED", "PROPOSED", "APPROVED", "REJECTED", ACTIVE", "DEPRECATED", "OTHER" |
| Qualified Name     | No              | No        | No                 | Yes     | The qualified name can either be provided by the user or generated. If generated, a pattern is followed. |
| GUID               | No              | Yes       | Yes                | Yes     | GUIDs are always generated by Egeria. They are meant for automation, not people.                         |
| Update Description | No              | No        | No                 | No      | Updates can have an update description added to the term's note log.                                     |


### Version Identifier
0.1
### Content Status

DRAFT

### Qualified Name


___

## Create Term

### Display Name

Provenance

### Glossary Name

Glossary::Egeria-Markdown

### Folders

Processing Dr.Egeria Markdown

### Summary
The `Provenance` command is used by Dr.Egeria to indicate the history of the Dr.Egeria input file.

### Description
When a Dr.Egeria input file is processed, it will look for a `Provenance` command. If one is not found, 
a new `Provenance` section will be created. Processing information (name of the file and timestamp) are appended
to this section. If a Dr.Egeria file is processed multiple times, a history of this processing will be created (presuming
the text is not deleted by the user). This simple, informal mechanism can be useful for basic scenarios. More sophisticated
scenarios would make use of more robust mechanisms such as version control and document management systems. 

Additionally, it is important to note that Egeria automatically maintains an audit history for each element. Additional
features for maintaining an update journal are also planned for Dr.Egeria.

### Abbreviation

### Examples


### Usage
Provenancce information is filled out automatically by Dr.Egeria.

### Version Identifier
0.1
### Content Status

DRAFT

### Qualified Name


___

## Create Term

### Display Name

Create Personal Project

### Glossary Name

Glossary::Egeria-Markdown

### Folders

Writing Dr.Egeria Markdown

### Summary

This command defines a new personal project within Egeria. 
### Description
As the name suggests, personal projects are used by individuals to help projects that only involve them. While Egeria supports
several kinds of project, personal projects may be of particular interest to data scientists looking to track their
experiments.

### Abbreviation

### Examples

### Usage
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
                                                                                    

### Version Identifier
0.1
### Content Status

DRAFT

### Qualified Name

___

## Create Term

### Display Name

Update Personal Project

### Glossary Name

Glossary::Egeria-Markdown

### Folders

Writing Dr.Egeria Markdown

### Summary

Update an existing Egeria personal project.

### Description

Update an en existing Egeria personal project.

### Abbreviation

### Examples

### Usage
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

### Version Identifier
0.2
### Content Status

DRAFT

___

## Create Term

### Display Name

Create Term-Term Relationship

### Glossary Name

Glossary::Egeria-Markdown

### Folders

Writing Dr.Egeria Markdown

### Summary

Creates a relationship between two terms.

### Description

Creates a relationship between two terms. Supported relationship types are:\n
- `Synonym` - A term is a synonym of another term.
- `Antonym` - A term is an antonym of another term.
- `Translation` - A term is a translation of another term.
- `RelatedTerm` - A term is related to another term.
- `ReplacementTerm` - A term is a replacement for another term.
- `ValidValue` - A term is a valid value for another term.
- `ISA` or `IS A` - A term is a subtype of another term.
- `HASA` or `HAS A` - A term has another term as a component or attribute.
- `TYPED BY` - A term is typed by another term.
- `TYPE OF` - A term is a type of relationship defined by another term.

### Abbreviation

### Examples

### Usage
Dr.Egeria processes uses the following attributes for a personal project:


| Attribute Name    | Input Required? | Read Only | Generated/Default? | Unique? | Notes                                                                                                     |
|:------------------|:----------------|-----------|:-------------------|:--------|:----------------------------------------------------------------------------------------------------------|
| Term 1 Name       | Yes             | No        | No                 | No      | The name of the first term.                                                                               |
| Term 2 Name       | Yes             | No        | No                 | No      | The name of the second term.                                                                              |
| Relationship Type | Yes             | No        | No                 | No      | The type of relationship between the two terms.                                                           |


___

## Create Term

### Display Name

List Glossaries

### Glossary Name

Glossary::Egeria-Markdown

### Folders

Writing Dr.Egeria Markdown

### Summary

List the glossaries that are defined in Egeria.

### Description
List the glossaries that are defined in Egeria.
### Abbreviation

### Examples

### Usage
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


___

## Create Term

### Display Name

List Folders

### Glossary Name

Glossary::Egeria-Markdown

### Folders

Writing Dr.Egeria Markdown

### Summary

List the categories that are defined in a glossary.

### Description
List the categories that are defined in Egeria. Optionally filter based on a search string.

### Aliases
List Glossary Folders

### Abbreviation

### Examples

### Usage
List Folders has the following attributes:


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


___

## Create Term

### Display Name

List Terms

### Glossary Name

Glossary::Egeria-Markdown

### Folders

Writing Dr.Egeria Markdown

### Summary

List the terms that are defined in a glossary. O

### Description
List the terms that are defined in Egeria. optionally filter based on a search string and glossary name.

### Aliases
List Glossary Terms

### Abbreviation

### Examples

### Usage

List Folders has the following attributes:


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


## Create Term

### Display Name

List Folders

### Glossary Name

Glossary::Egeria-Markdown

### Folders

Writing Dr.Egeria Markdown

### Summary

List the categories that are defined in a glossary.

### Description
List the categories that are defined in Egeria. Optionally filter based on a search string.

### Aliases
List Glossary Folders

### Abbreviation

### Examples

### Usage

List Folders has the following attributes:


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


___

## Create Term

### Display Name

List Term History

### Glossary Name

Glossary::Egeria-Markdown

### Folders

Writing Dr.Egeria Markdown

### Summary

List the version history of a term.

### Description
List the terms that are defined in Egeria. optionally filter based on a search string and glossary name.

### Aliases
Term History

### Abbreviation

### Examples

### Usage

List Term History has the following attributes:


| Attribute Name | Input Required? | Read Only? | Generated/Default?               | Unique? | Notes                                     |
|----------------|-----------------|------------|----------------------------------|---------|-------------------------------------------|
| Display Name      | Yes             | No         | No                               | No      | can be qualified name or display name     |
| Output Format  | No              | No         | default is Markdown List (table) | No      | options are: LIST, DICT |

Lets describe the output formats a bit further:

* LIST - This is the default format. It returns a markdown table of the categories.
* DICT - This returns a python dictionary (or JSON representation) of the categories. 

___


## Create Term

### Display Name

List Term Revision History

### Glossary Name

Glossary::Egeria-Markdown

### Folders

Writing Dr.Egeria Markdown

### Summary

List the note log documenting the revision history of a term.

### Description
Lis the note log documenting the revision history of a term. Entries in the note log are created when a term is updated and
the `Update Description` attribute is set.

### Aliases
List Term Update History

### Abbreviation

### Examples

### Usage

List Term Revision History has the following attributes:


| Attribute Name | Input Required? | Read Only? | Generated/Default?               | Unique? | Notes                                 |
|----------------|-----------------|------------|----------------------------------|---------|---------------------------------------|
| Display Name      | Yes             | No         | No                               | No      | can be qualified name or display name |
| Output Format  | No              | No         | default is Markdown List (table) | No      | options are: LIST, DICT & MD          |

Lets describe the output formats a bit further:

* LIST - This is the default format. It returns a markdown table of the categories.
* DICT - This returns a python dictionary (or JSON representation) of the categories. 
* MD - This returns markdown text of the revision history.

___


## Create Term

### Display Name

List Term Details

### Glossary Name

Glossary::Egeria-Markdown

### Folders

Writing Dr.Egeria Markdown

### Summary

List the details of a term, including related terms.

### Description
List the details of a term, including related terms.

### Aliases

### Abbreviation

### Examples

### Usage

List Term Details has the following attributes:


| Attribute Name | Input Required? | Read Only? | Generated/Default?               | Unique? | Notes                                 |
|----------------|-----------------|------------|----------------------------------|---------|---------------------------------------|
| Display Name      | Yes             | No         | No                               | No      | can be qualified name or display name |
| Output Format  | No              | No         | default is Markdown List (table) | No      | options are: DICT & REPORT            |

Lets describe the output formats a bit further:

* DICT - This returns a python dictionary (or JSON representation) of the categories. 
* REPORT - This returns markdown text of the term details in a report format.

___

## Create Term

### Display Name

List Glossary Structure

### Glossary Name

Glossary::Egeria-Markdown

### Folders

Writing Dr.Egeria Markdown

### Summary

List the category structure of a glossary.

### Description
List the category structure of a glossary.

### Aliases

### Abbreviation

### Examples

### Usage

List Glossary Structure has the following attributes:


| Attribute Name | Input Required? | Read Only? | Generated/Default?               | Unique? | Notes                                 |
|----------------|-----------------|------------|----------------------------------|---------|---------------------------------------|
| Glossary Name  | Yes             | No         | No                               | No      | can be qualified name or display name |
| Output Format  | No              | No         | default is Markdown List (table) | No      | options are: DICT, LIST & REPORT      |

Lets describe the output formats a bit further:

* DICT - This returns a python dictionary (or JSON representation) of the categories. 
* REPORT - This returns markdown text of the term details in a report format with category nesting shown.
* LIST - This returns a markdown table of the glossary structure.

___


# All Glossary Commands have Terms created.

Whew! Getting to be quite a number of glossary commands. There will be more in the future but this gives us a robust start
for creating and managing glossaries. Note that while Dr.Egeria supports creation and updates, we have chosen to leave
deletions to explicit `hey_egeria` commands and `pyegeria` method calls - for safety.

Now lets take a look at our handiwork by listing the commands in the `Egeria-Markdown` glossary.

___

# List Terms
### Glossary Name
Egeria-Markdown

___

# Next steps

While this is just a short introduction to Dr.Egeria, you can see that it is already quite powerful. 
You can create and update glossaries, categories and terms, and you can list them in a variety of formats.
This is just a small sample of what you can do. Dr.Egeria currently supports over 120 different commands across
10 different categories:

* Collections - for working with collections of elements, collections are used throughout Egeria as an organizing principle.
* Data Designer - for defining data dictionaries, specifications, structures, structures, and more.
* Digital Products - for defining digital products for reuse of metadata, assets, and insight. 
* External References - Link external artifacts into Egeria.
* Feedback - Allows users to add comments, ratings blogs, and other feedback to Egeria elements.
* Glossary - for working with glossaries and terms.
* Governance Officer - Enables a broad range of governance definitions and actions.
* Project - Define and manage projects in Egeria.
* Report - for executing an extensible set of reports over Egeria elements, in a variety of output types.
* Solution Architect - Enables definition of Solution Blueprints, Information Supply Chains and Solution Components..

This is an ever growing list - new commands are being added frequently. To help you find and use Dr.Egeria commands, 
we you can find commands with dr_egeria_help or you can view templates for each command in the Templates directory. 
Subsequent tutorials will cover both of these features.

## Provenance

