# Generating glossary entries for the documented commands


            This file contains generated Dr.Egeria commands to generate glossary term entries describing
            each command represented in the `commands.json` file.
# Create Term
## Term Name

Create Data Dictionary

## Description

A Data Dictionary is an organized and curated collection of data definitions that can serve as a reference for data professionals

## Owning Glossary

Egeria-Markdown

## Categories

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the Data Dictionary | False |  | 
| Description | False | True | False | None | A description of the Data Dictionary. | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 


___

# Create Term
## Term Name

Create Data Specification

## Description

A Data Specification defines the data requirements for a project or initiative. This includes the data structures , data fields and data classes.

## Owning Glossary

Egeria-Markdown

## Categories

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the Data Specification. | False |  | 
| Description | False | True | False | None | A description of the Data Specification. | False |  | 
| Collection Type | False | True | False | None | A user supplied collection type. | False |  | 
| Qualified Name | True | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 


___

# Create Term
## Term Name

Create Data Structure

## Description

A collection of data fields that for a data specification for a data source.

## Owning Glossary

Egeria-Markdown

## Categories

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the data structure. | False |  | 
| Description | False | True | False | None | A description of the data structure. | False |  | 
| In Data Specification | False | True | False | None | The data specifications this structure is a member of. | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 


___

# Create Term
## Term Name

Create Data Field

## Description

A data field is a fundamental building block for a data structure.

## Owning Glossary

Egeria-Markdown

## Categories

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the Data Field | False |  | 
| Description | False | True | False | None | A description of the Data Field | False |  | 
| Data Type | True | True | False | None | The data type of the data field. Point to data type valid value list if exists. | False | string; int; long; date; boolean; char; byte; float; double; biginteger; bigdecimal; array<string>; array<int>; map<string,string>; map<string, boolean>; map<string, int>; map<string, long>; map<string,double>; map<string, date> map<string, object>; short; map<string, array<string>>; other | 
| Position | False | True | False | None | Position of the data field in the data structure. If 0, position is irrelevant. | False |  | 
| Minimum Cardinality | False | True | False | None | The minimum cardinality for a data element. | False |  | 
| Maximum Cardinality | False | True | False | None | The maximum cardinality for a data element. | False |  | 
| In Data Structure | False | True | False | None | The data structure this field is a member of. If display name is not unique, use qualified name. | False |  | 
| Data Class | False | True | False | None | The data class that values of this data field conform to. | False |  | 
| Glossary Term | False | True | False | None | Term that provides meaning to this field. | False |  | 
| isNullable | False | True | False | None | Can the values within the dataclass be absent? | False |  | 
| Minimum Length | False | True | False | None |  | False |  | 
| Length | False | True | False | None | The length of a value for a field. | False |  | 
| Precision | False | True | False | None | The precision of a numeric | False |  | 
| Ordered Values | False | True | False | None | is this field in an ordered list? | False |  | 
| Units | False | True | False | None | An optional string indicating the units of the field. | False |  | 
| Default Value | False | True | False | None | Specify a default value for the data class. | False |  | 
| Version Identifier | False | True | False | None | A user supplied version identifier. | False |  | 
| In Data Dictionary | False | True | False | None | What data dictionaries is this data field in? | False |  | 
| Parent Data Field | False | True | False | None | Optional parent field if this is a nested field. | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 


___

# Create Term
## Term Name

Create Data Class

## Description

Describes the data values that may be stored in data fields. Can be used to configure quality validators and data field classifiers.

## Owning Glossary

Egeria-Markdown

## Categories

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the data structure. | False |  | 
| Description | False | True | False | None | A description of the data class. | False |  | 
| Namespace | False | True | False | None | Optional namespace that scopes the field. | False |  | 
| Match Property Names | False | True | True | None | Names of the properties that are set. | False |  | 
| Match Threshold | False | True | False | None | Percent of values that must match the data class specification. | False |  | 
| IsCaseSensitive | False | True | False | None | Are field values case sensitive? | False |  | 
| Data Type | True | True | False | None | Data type for the data class. | False | string; int; long; date; boolean; char; byte; float; double; biginteger; bigdecimal; array<string>; array<int>; map<string,string>; map<string, boolean>; map<string, int>; map<string, long>; map<string,double>; map<string, date> map<string, object>; short; map<string, array<string>>; other | 
| Allow Duplicate Values | False | True | False | None | Allow duplicate values within the data class? | False |  | 
| isNullable | False | True | False | None | Can the values within the dataclass be absent? | False |  | 
| isCaseSensitive | False | True | False | None | Indicates if the values in a  data class are case sensitive. | False |  | 
| Default Value | False | True | False | None | Specify a default value for the data class. | False |  | 
| Average Value | False | True | False | None | Average value for the data class. | False |  | 
| Value List | False | True | False | None |  | False |  | 
| Value Range From | False | True | False | None | Beginning range of legal values. | False |  | 
| Value Range To | False | True | False | None | End of valid range for value. | False |  | 
| Sample Values | False | True | False | None | Sample values of the data class. | False |  | 
| Data Patterns | False | True | False | None | prescribed format of a data field - e.g. credit card numbers. Often expressed as a regular expression. | False |  | 
| In Data Dictionary | False | True | False | None | What data dictionaries is this data field in? | False |  | 
| Containing Data Class | False | True | False | None | Data classes this is part of. | False |  | 
| Specializes Data Class | False | True | False | None | Specializes a parent  data class. | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 


___

# Create Term
## Term Name

View Data Fields

## Description

Return the data fields, optionally filtered by the search string.

## Owning Glossary

Egeria-Markdown

## Categories

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Search String | False | True | False | None | An optional search string to filter results by. | False |  | 
| Output Format | False | True | False | None | Optional specification of output format for the query. | False | LIST; FORM; REPORT; MERMAID; DICT | 
| Starts With | False | True | False | None | If true, look for matches with the search string starting from the beginning of  a field. | False |  | 
| Ends With | False | True | False | None | If true, look for matches with the search string starting from the end of  a field. | False |  | 
| Ignore Case | False | True | False | None | If true, ignore the difference between upper and lower characters when matching the search string. | False |  | 
| AsOfTime | False | True | False | None | An ISO-8601 string representing the time to view the state of the repository. | False |  | 
| Sort Order | False | True | False | None | How to order the results. The sort order can be selected from a list of valid value. | False | ANY; CREATION_DATE_RECENT; CREATION_DATA_OLDEST; LAST_UPDATE_RECENT; LAST_UPDATE_OLDEST; PROPERTY_ASCENDING; PROPERTY_DESCENDING | 
| Page Size | False | True | False | None | The number of elements returned per page. | False |  | 
| Start From | False | True | False | None | When paging through results, the starting point of the results to return. | False |  | 


___

# Create Term
## Term Name

View Data Classes

## Description

Return the data classes, optionally filtered by the search string.

## Owning Glossary

Egeria-Markdown

## Categories

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Search String | False | True | False | None | An optional search string to filter results by. | False |  | 
| Output Format | False | True | False | None | Optional specification of output format for the query. | False | LIST; FORM; REPORT; MERMAID; DICT | 
| Starts With | False | True | False | None | If true, look for matches with the search string starting from the beginning of  a field. | False |  | 
| Ends With | False | True | False | None | If true, look for matches with the search string starting from the end of  a field. | False |  | 
| Ignore Case | False | True | False | None | If true, ignore the difference between upper and lower characters when matching the search string. | False |  | 
| AsOfTime | False | True | False | None | An ISO-8601 string representing the time to view the state of the repository. | False |  | 
| Sort Order | False | True | False | None | How to order the results. The sort order can be selected from a list of valid value. | False | ANY; CREATION_DATE_RECENT; CREATION_DATA_OLDEST; LAST_UPDATE_RECENT; LAST_UPDATE_OLDEST; PROPERTY_ASCENDING; PROPERTY_DESCENDING | 
| Page Size | False | True | False | None | The number of elements returned per page. | False |  | 
| Start From | False | True | False | None | When paging through results, the starting point of the results to return. | False |  | 


___

# Create Term
## Term Name

View Data Structures

## Description

Return the data structures, optionally filtered by the search string.

## Owning Glossary

Egeria-Markdown

## Categories

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Search String | False | True | False | None | An optional search string to filter results by. | False |  | 
| Output Format | False | True | False | None | Optional specification of output format for the query. | False | List; Form; Report; Dict | 
| Starts With | False | True | False | None | If true, look for matches with the search string starting from the beginning of  a field. | False |  | 
| Ends With | False | True | False | None | If true, look for matches with the search string starting from the end of  a field. | False |  | 
| Ignore Case | False | True | False | None | If true, ignore the difference between upper and lower characters when matching the search string. | False |  | 
| AsOfTime | False | True | False | None | An ISO-8601 string representing the time to view the state of the repository. | False |  | 
| Sort Order | False | True | False | None | How to order the results. The sort order can be selected from a list of valid value. | False | ANY; CREATION_DATE_RECENT; CREATION_DATA_OLDEST; LAST_UPDATE_RECENT; LAST_UPDATE_OLDEST; PROPERTY_ASCENDING; PROPERTY_DESCENDING | 
| Page Size | False | True | False | None | The number of elements returned per page. | False |  | 
| Start From | False | True | False | None | When paging through results, the starting point of the results to return. | False |  | 


___

# Create Term
## Term Name

View Data Specifications

## Description

Return the data specifications, optionally filtered by the search string.

## Owning Glossary

Egeria-Markdown

## Categories

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Search String | False | True | False | None | An optional search string to filter results by. | False |  | 
| Output Format | False | True | False | None | Optional specification of output format for the query. | False | LIST; FORM; DICT; MD; MERMAID; REPORT | 
| Starts With | False | True | False | None | If true, look for matches with the search string starting from the beginning of  a field. | False |  | 
| Ends With | False | True | False | None | If true, look for matches with the search string starting from the end of  a field. | False |  | 
| Ignore Case | False | True | False | None | If true, ignore the difference between upper and lower characters when matching the search string. | False |  | 
| AsOfTime | False | True | False | None | An ISO-8601 string representing the time to view the state of the repository. | False |  | 
| Sort Order | False | True | False | None | How to order the results. The sort order can be selected from a list of valid value. | False | ANY; CREATION_DATE_RECENT; CREATION_DATA_OLDEST; LAST_UPDATE_RECENT; LAST_UPDATE_OLDEST; PROPERTY_ASCENDING; PROPERTY_DESCENDING | 
| Page Size | False | True | False | None | The number of elements returned per page. | False |  | 
| Start From | False | True | False | None | When paging through results, the starting point of the results to return. | False |  | 


___

# Create Term
## Term Name

View Data Dictionaries

## Description

Return the data dictionaries, optionally filtered by the search string.

## Owning Glossary

Egeria-Markdown

## Categories

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Search String | False | True | False | None | An optional search string to filter results by. | False |  | 
| Output Format | False | True | False | None | Optional specification of output format for the query. | False | LIST; FORM; DICT; MD; MERMAID; REPORT | 
| Starts With | False | True | False | None | If true, look for matches with the search string starting from the beginning of  a field. | False |  | 
| Ends With | False | True | False | None | If true, look for matches with the search string starting from the end of  a field. | False |  | 
| Ignore Case | False | True | False | None | If true, ignore the difference between upper and lower characters when matching the search string. | False |  | 
| Page Size | False | True | False | None | The number of elements returned per page. | False |  | 
| Start From | False | True | False | None | When paging through results, the starting point of the results to return. | False |  | 
| AsOfTime | False | True | False | None | An ISO-8601 string representing the time to view the state of the repository. | False |  | 
| Sort Order | False | True | False | None | How to order the results. The sort order can be selected from a list of valid value. | False | ANY; CREATION_DATE_RECENT; CREATION_DATA_OLDEST; LAST_UPDATE_RECENT; LAST_UPDATE_OLDEST; PROPERTY_ASCENDING; PROPERTY_DESCENDING | 


___

# Create Term
## Term Name

Create Information Supply Chain

## Description

The flow of a particular type of data across a digital landscape.

## Owning Glossary

Egeria-Markdown

## Categories

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the Information Supply Chain | False |  | 
| Description | False | True | False | None | A description of the data structure. | False |  | 
| Scope | False | True | False | None | Scope of the supply chain. | False |  | 
| Purposes | False | True | False | None | A list of purposes. | False |  | 
| Information Supply Chain Segments | False | True | False | None | A list of supply chain segments that make up the supply chain. | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 


___

# Create Term
## Term Name

Create Information Supply Chain Segment

## Description

A collection of data fields that for a data specification for a data source.

## Owning Glossary

Egeria-Markdown

## Categories

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the Information Supply Chain | False |  | 
| Description | False | True | False | None | A description of the data structure. | False |  | 
| Scope | False | True | False | None | Scope of the supply chain. | False |  | 
| Integration Style | False | True | False | None | Style of integration connecting this segment. | False |  | 
| Estimated Volumetrics | False | True | False | None | Estimated volumetrics for rough analysis and planning. | False |  | 
| Information Supply Chain | False | True | False | None | The owning information supply chain for this segment. | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 


___

# Create Term
## Term Name

Create Solution Blueprint

## Description

A solution blueprint describes the architecture of a digital service in terms of solution components.

## Owning Glossary

Egeria-Markdown

## Categories

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the Information Supply Chain | False |  | 
| Description | False | True | False | None | A description of the data structure. | False |  | 
| Version Identifier | False | True | False | None | A user supplied version identifier. | False |  | 
| Solution Components | False | True | False | None | Solution components that make up the blueprint. | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 


___

# Create Term
## Term Name

Create Solution Component

## Description

A reusable solution component.

## Owning Glossary

Egeria-Markdown

## Categories

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the solution component. | False |  | 
| Description | False | True | False | None | A description of the data structure. | False |  | 
| Solution Component Type | False | True | False | None | Type of solution component. | False |  | 
| Planned Deployed Implementation Type | False | True | False | None | The planned implementation type for deployment. | False |  | 
| Solution SubComponents | False | True | False | None | Solution components that include this one. | False |  | 
| Solution Blueprints | False | True | False | None | Solution Blueprints that contain this component. | False |  | 
| Actors | False | True | False | None | Actors associated with this component. | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Merge Update | False | True | False | None | If true, only those attributes specified in the update will be updated; If false, any attributes not provided during the update will be set to None. | False |  | 


___

# Create Term
## Term Name

Create Solution Role

## Description

A collection of data fields that for a data specification for a data source.

## Owning Glossary

Egeria-Markdown

## Categories

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Name | True | True | False | None | Name of the role. | False |  | 
| Description | False | True | False | None | A description of the data structure. | False |  | 
| Title | False | True | False | None | Title of the role. | False |  | 
| Scope | False | True | False | None | Scope of the role. | False |  | 
| identifier | False | True | False | None | role identifier | False |  | 
| Domain Identifier | False | True | False | None | Governance domain identifier | False |  | 
| Role Type | False | True | False | None | Type of the role.  Currently must be GovernanceRole. | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 


___

# Create Term
## Term Name

Attach Information Supply Chain Segments

## Description



## Owning Glossary

Egeria-Markdown

## Categories

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Segment1 | True | True | False | None | The  first segment to link. | False |  | 
| Segment2 | True | True | False | None | The  second segment to link. | False |  | 
| Link Label | False | True | False | None | Labels the link between two information supply chain segments. | False |  | 
| Description | False | True | False | None | A description of the data structure. | False |  | 


___

# Create Term
## Term Name

View Information Supply Chains

## Description

Return information supply chains filtered by the search string.

## Owning Glossary

Egeria-Markdown

## Categories

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Search String | False | True | False | None | An optional search string to filter results by. | False |  | 
| Output Format | False | True | False | None | Optional specification of output format for the query. | False | List; Form; Report; Dict | 
| Detailed | False | True | False | None | If true a more detailed set of attributes will be returned. | False |  | 


___

# Create Term
## Term Name

View Supply Chain Segments

## Description

Return the data structure details, optionally filtered by the search string.

## Owning Glossary

Egeria-Markdown

## Categories

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Search String | False | True | False | None | An optional search string to filter results by. | False |  | 
| Output Format | False | True | False | None | Optional specification of output format for the query. | False | List; Form; Report; Dict | 
| Detailed | False | True | False | None | If true a more detailed set of attributes will be returned. | False |  | 


___

# Create Term
## Term Name

View Solution Components

## Description

Return the data structure details, optionally filtered by the search string.

## Owning Glossary

Egeria-Markdown

## Categories

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Search String | False | True | False | None | An optional search string to filter results by. | False |  | 
| Output Format | False | True | False | None | Optional specification of output format for the query. | False | List; Form; Report; Dict | 
| Detailed | False | True | False | None | If true a more detailed set of attributes will be returned. | False |  | 


___

# Create Term
## Term Name

View Solution Blueprints

## Description

Return the data structure details, optionally filtered by the search string.

## Owning Glossary

Egeria-Markdown

## Categories

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Search String | False | True | False | None | An optional search string to filter results by. | False |  | 
| Output Format | False | True | False | None | Optional specification of output format for the query. | False | List; Form; Report; Dict | 
| Detailed | False | True | False | None | If true a more detailed set of attributes will be returned. | False |  | 


___

# Create Term
## Term Name

View Solution Roles

## Description

Return the data structure details, optionally filtered by the search string.

## Owning Glossary

Egeria-Markdown

## Categories

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Search String | False | True | False | None | An optional search string to filter results by. | False |  | 
| Output Format | False | True | False | None | Optional specification of output format for the query. | False | List; Form; Report; Dict | 
| Detailed | False | True | False | None | If true a more detailed set of attributes will be returned. | False |  | 


___

# Create Term
## Term Name

Create Glossary

## Description

A grouping of definitions.

## Owning Glossary

Egeria-Markdown

## Categories

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Glossary Name | True | True | False | None | The name of the glossary to create or update. | False |  | 
| Description | False | True | False | None | A description of the Glossary. | False |  | 
| Language | False | True | False | None | The language of the glossary. Note that multilingual descriptions are supported. Please see web site for details. | False |  | 
| Usage | False | True | False | None | A description of how the glossary is to be used. | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 


___

# Create Term
## Term Name

Create Category

## Description

A group of terms that are useful to collect together.

## Owning Glossary

Egeria-Markdown

## Categories

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Category Name | True | True | False | None | The name of a category. | False |  | 
| Description | False | True | False | None | A description of the Category. | False |  | 
| In Glossary | True | True | False | None | The name of the glossary that contains the Category. Recommend using the Qualified Name of the Glossary, if known. | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 


___

# Create Term
## Term Name

 Term

## Description



## Owning Glossary

Egeria-Markdown

## Categories

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Term Name | True | True | False | None | The name of the term to create or update. | False |  | 
| Summary | False | True | False | None | A summary description of the term. | False |  | 
| Description | False | True | False | None | A description of the term. | False |  | 
| Abbreviation | False | True | False | None | An abbreviation for the term. | False |  | 
| Example | False | True | False | None | An example of how the term is used. | False |  | 
| Usage | False | True | False | None | A description of how the term is to be used. | False |  | 
| Status | False | True | False | None | The lifecycle status of a term. | False | DRAFT; ACTIVE, DEPRECATED; OBSOLETE; OTHER | 
| Published Version Identifier | False | True | False | None |  | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 


___

# Create Term
## Term Name

Attach Category Parent

## Description

Attaches a parent category to a child category.

## Owning Glossary

Egeria-Markdown

## Categories

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Category Name | True | True | False | None | The name of a category. | False |  | 
| Parent Category | True | True | False | None | The name of the parent category to attach to. | False |  | 


___

# Create Term
## Term Name

Attach Term-Term Relationship

## Description

Create a relationship between terms.

## Owning Glossary

Egeria-Markdown

## Categories

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Term  1 | True | True | False | None | The name of the first term term to connect. | False |  | 
| Term  2 | No | No | No | None |  | No | [] | 
| Relationship | True | True | False | None | The type of relationship to connecting the two terms. | False | Synonym;  Translation;  PreferredTerm; TermISATYPEOFRelationship;  TermTYPEDBYRelationship;  Antonym; ReplacementTerm;  ValidValue; TermHASARelationship; RelatedTerm;   ISARelationship | 


___

