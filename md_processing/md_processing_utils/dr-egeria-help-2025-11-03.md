# Generating glossary entries for the documented commands


            This file contains generated Dr.Egeria commands to generate glossary term entries describing
            each Dr.Egeria command. 

> Usage: Before executing this file, make sure you have a glossary named `Egeria-Markdown`
> already created. If you Need to create one, you can use the `hey_egeria tui` command.
# Create Term
## Term Name

Create Comment

## Description

Add a comment to an associated element.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | False | True | False | None | Name of the  Comment. | False |  | 
| Associated Element | True | True | False | None | The element the comment is attached to. To reply to a previous comment, you would use the ID of the previous comment as the associated element. | False |  | 
| Comment Text | True | True | False | None | The Comment text. | False |  | 
| Comment Type | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False | STANDARD_COMMENT; QUESTION; ANSWER; SUGGESTION; USAGE_EXPERIENCE; REQUIREMENT; OTHER | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Journal Entry

## Description

Allows a sequence of notes to be attached to an associated element.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Journal Name | True | True | False | None | Name of the  NoteLog or Journal. | False |  | 
| Associated Element | False | True | False | None | The element the NoteLog is attached to. | False |  | 
| Journal Description | False | True | False | None | Description of the NoteLog. | False |  | 
| Note Entry | True | True | False | None | The text of the journal entry. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Informal Tag

## Description

Creates an informal tag that can be attached to elements. 

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the informal tag. | False |  | 
| Description | False | True | False | None | Description of the Informal Tag. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Link Tag->Element

## Description

Used to attach an informal tag to an element.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Tag ID | True | True | False | None | Identity (usually qualified name) of the tag to attach. | False |  | 
| Element ID | True | True | False | None | Identity (usually qualified name) of the element you are tagging. | False |  | 


___

# Create Term
## Term Name

Create External Reference

## Description

Create or update External Reference Elements - or sub-types Related Media, Cited Documents, External Data Source and External Model Source.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the external reference. | False |  | 
| Description | False | True | False | None | Description of the contents of a product. | False |  | 
| Reference Title | False | True | False | None | Title of the external reference. | False |  | 
| Reference Abstract | False | True | False | None | Abstract for the remote reference. | False |  | 
| Authors | False | True | False | None | A list of authors. | False |  | 
| Organization | False | True | False | None | Organization owning the external reference. | False |  | 
| Sources | False | True | False | None | A map of source strings. | False |  | 
| License | False | True | False | None | The license associated with the external reference. | False |  | 
| Copyright | False | True | False | None | The copy right associated with the external reference. | False |  | 
| Attribution | False | True | False | None | Attribution string to describe the external reference. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create External Data Source

## Description

An external data source.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the External Data Source | False |  | 
| Description | False | True | False | None | Description of the contents of a product. | False |  | 
| Reference Title | False | True | False | None | Title of the external reference. | False |  | 
| Reference Abstract | False | True | False | None | Abstract for the remote reference. | False |  | 
| Authors | False | True | False | None | A list of authors. | False |  | 
| Organization | False | True | False | None | Organization owning the external reference. | False |  | 
| Sources | False | True | False | None | A map of source strings. | False |  | 
| License | False | True | False | None | The license associated with the external reference. | False |  | 
| Copyright | False | True | False | None | The copy right associated with the external reference. | False |  | 
| Attribution | False | True | False | None | Attribution string to describe the external reference. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create External Model Source

## Description

An external model.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the External Model Source | False |  | 
| Description | False | True | False | None | Description of the contents of a product. | False |  | 
| Reference Title | False | True | False | None | Title of the external reference. | False |  | 
| Reference Abstract | False | True | False | None | Abstract for the remote reference. | False |  | 
| Authors | False | True | False | None | A list of authors. | False |  | 
| Organization | False | True | False | None | Organization owning the external reference. | False |  | 
| Sources | False | True | False | None | A map of source strings. | False |  | 
| License | False | True | False | None | The license associated with the external reference. | False |  | 
| Copyright | False | True | False | None | The copy right associated with the external reference. | False |  | 
| Attribution | False | True | False | None | Attribution string to describe the external reference. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Related Media

## Description

Related external media.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the Related Media | False |  | 
| Description | False | True | False | None | Description of the contents of a product. | False |  | 
| Reference Title | False | True | False | None | Title of the external reference. | False |  | 
| Reference Abstract | False | True | False | None | Abstract for the remote reference. | False |  | 
| Authors | False | True | False | None | A list of authors. | False |  | 
| Organization | False | True | False | None | Organization owning the external reference. | False |  | 
| Sources | False | True | False | None | A map of source strings. | False |  | 
| License | False | True | False | None | The license associated with the external reference. | False |  | 
| Copyright | False | True | False | None | The copy right associated with the external reference. | False |  | 
| Attribution | False | True | False | None | Attribution string to describe the external reference. | False |  | 
| Media Type | False | True | False | None | Type of media. | False | IMAGE; AUDIO; DOCUMENT; VIDEO; OTHER | 
| Media Type Other Id | False | True | False | None | An id associated with the media type. | False |  | 
| Default Media Usage | False | True | False | None | How the media is being used. | False | ICON; THUMBNAIL; ILLUSTRATION; USAGE_GUIDANCE; OTHER | 
| default Media Usage Other Id | False | True | False | None | An id associated with the media usage. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Cited Document

## Description

A cited document

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the Cited Document | False |  | 
| Description | False | True | False | None | Description of the contents of a product. | False |  | 
| Reference Title | False | True | False | None | Title of the external reference. | False |  | 
| Reference Abstract | False | True | False | None | Abstract for the remote reference. | False |  | 
| Authors | False | True | False | None | A list of authors. | False |  | 
| Organization | False | True | False | None | Organization owning the external reference. | False |  | 
| Sources | False | True | False | None | A map of source strings. | False |  | 
| License | False | True | False | None | The license associated with the external reference. | False |  | 
| Copyright | False | True | False | None | The copy right associated with the external reference. | False |  | 
| Attribution | False | True | False | None | Attribution string to describe the external reference. | False |  | 
| Number of Pages | False | True | False | None | The number of pages in the document. | False |  | 
| Page Range | False | True | False | None | The range of pages cited. | False |  | 
| Publication Series | False | True | False | None | The series this publication is part of. | False |  | 
| Publication Series Volume | False | True | False | None | The volume in the series that contains the citation. | False |  | 
| Publisher | False | True | False | None | The name of the publisher. | False |  | 
| Edition | False | True | False | None | The edition being cited. | False |  | 
| First Publication Date | False | True | False | None | Date of first publication written as an ISO string - 2025-01-31 | False |  | 
| Publication Date | False | True | False | None | Publication date.  In ISO 8601 format - 2025-02-23. | False |  | 
| Publication City | False | True | False | None | City of publication. | False |  | 
| Publication Year | False | True | False | None | Year of publication. | False |  | 
| Publication Numbers | False | True | False | None | Identification numbers of the publication, if relevant. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Link External Reference Link

## Description

Link an external reference to a referenceable.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Element Name | True | True | False | None | A referenceable to link. | False |  | 
| External Reference | True | True | False | None | The external reference to link to. | False |  | 
| Label | False | True | False | None | Labels the link between the referenceable and the external reference. | False |  | 
| Description | False | True | False | None | A description of the link. | False |  | 


___

# Create Term
## Term Name

Link Media Reference Link

## Description

Link a medial reference to a referenceable.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Element Name | True | True | False | None | A referenceable to link. | False |  | 
| Media Reference | True | True | False | None | The media reference to link to. | False |  | 
| Label | False | True | False | None | Labels the link between the referenceable and the media reference. | False |  | 
| Description | False | True | False | None | A description of the link. | False |  | 
| Media Id | False | True | False | None | An identifier of the media to link to. | False |  | 
| Media Usage | False | True | False | None | How the media is being used. | False | ICON; THUMBNAIL; ILLUSTRATION; USAGE_GUIDANCE; OTHER | 
| Media Usage Other Id | False | True | False | None | An id associated with the media usage. | False |  | 


___

# Create Term
## Term Name

Link Cited Document Link

## Description

Link a cited document reference to a referenceable.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Element Name | True | True | False | None | A referenceable to link. | False |  | 
| Cited Document | True | True | False | None | The cited document to link to. | False |  | 
| Label | False | True | False | None | Labels the link between the referenceable and the media reference. | False |  | 
| Description | False | True | False | None | A description of the link. | False |  | 
| Reference  Id | False | True | False | None | An identifier of the cited document to link to. | False |  | 
| Pages | False | True | False | None | The pages referenced. | False |  | 


___

# Create Term
## Term Name

Create Collection

## Description

Create or update a generic collection. While it can be used to create specific kinds of collections, you cannot set the collection-specific properties - so use the appropriate Dr.Egeria command to set all of the properties.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the digital product | False |  | 
| Description | False | True | False | None | Description of the contents of a product. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Digital Product Catalog

## Description

Create or update a Digital Product Catalog. 

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of a catalog of digital products. | False |  | 
| Description | False | True | False | None | Description of the contents of a product catalog. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Digital Product

## Description

A Digital Product represents artifacts that can be subscribed to and consumed by users.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the digital product | False |  | 
| Description | False | True | False | None | Description of the contents of a product. | False |  | 
| Product Name | False | True | False | None | The external name of the digital product. | False |  | 
| Identifier | False | True | False | None | User specified product identifier. | False |  | 
| Maturity | False | True | False | None | Product maturity - user defined. | False |  | 
| Service Life | False | True | False | None | Estimated service lifetime of the product. | False |  | 
| Introduction Date | False | True | False | None | Date of product introduction in ISO 8601 format. Either all of the dates (introduction, next version, withdrawal) dates need to be supplied or none of them. Otherwise an error will occur. | False |  | 
| Next Version Date | False | True | False | None | Date of  the next version,  in ISO 8601 format. Either all of the dates (introduction, next version, withdrawal) dates need to be supplied or none of them. Otherwise an error will occur. | False |  | 
| Withdrawal Date | False | True | False | None | Date of planned product withdrawal in ISO 8601 format. Either all of the dates (introduction, next version, withdrawal) dates need to be supplied or none of them. Otherwise an error will occur. | False |  | 
| Product Manager | False | True | False | None | Actors responsible for managing this product. Actors may be individuals, automations, etc. | False |  | 
| Agreements | False | True | False | None | A list of agreements associated with this product.  The agreements must already exist. | False |  | 
| Digital Subscriptions | False | True | False | None |  | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Link Product-Product

## Description

Link digital product dependency between two digital products.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Digital Product 1 | True | True | False | None | The  first product to link. | False |  | 
| Digital Product 2 | True | True | False | None | The  second product to link. | False |  | 
| Label | False | True | False | None | Labels the link between two digital products. | False |  | 
| Description | False | True | False | None | A description of the link. | False |  | 


___

# Create Term
## Term Name

Create Agreement

## Description

A kind of collection that represents an Agreement. This is for generic agreements. Specific kinds of agreements have their own commands.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  agreement. | False |  | 
| Description | False | True | False | None | Description of the contents of the agreement. | False |  | 
| Identifier | False | True | False | None | A user specified agreement identifier. | False |  | 
| Agreement Actors | False | True | False | None | A list of actors with responsibilities for the agreement. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Data Sharing Agreement

## Description

Create a new collection with the DataSharingAgreement classification. 

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  agreement. | False |  | 
| Description | False | True | False | None | Description of the contents of the agreement. | False |  | 
| Identifier | False | True | False | None | A user specified agreement identifier. | False |  | 
| Product Manager | False | True | False | None | An actor responsible for managing this product. Actors may be individuals, automations, etc. | False |  | 
| Digital Subscriptions | False | True | False | None |  | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Digital Subscription

## Description

A type of agreement for a digital subscription.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  agreement. | False |  | 
| Description | False | True | False | None | Description of the contents of the agreement. | False |  | 
| Identifier | False | True | False | None | A user specified agreement identifier. | False |  | 
| Support Level | False | True | False | None | Level of support agreed or requested. | False |  | 
| Service Levels | False | True | False | None | A dictionary of name:value pairs describing the service levels. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create CSV File

## Description

Create a CSV File asset

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the CSV File | False |  | 
| Description | False | True | False | None | Description of the CSV file. | False |  | 
| File Path | False | True | False | None | Path to the file including file name. File system name is pre-pended if set. | False |  | 
| File Encoding | False | True | False | None | Encoding of the file. | False |  | 
| File Extension | False | True | False | None | Typically CSV. | False |  | 
| File System Name | False | True | False | None | Optional  file system name to be prepended in front of the path name. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Link Agreement->Item

## Description

Attach or detach an agreement to an element referenced in its definition. Agreement item can be any referencable element.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Agreement Name | True | True | False | None | The name of the agreement to add an item to. Using qualified names is recommended. | False |  | 
| Item Name | True | True | False | None | The name of the referenceable  item to add to an agreement  Using qualified names is recommended. | False |  | 
| Agreement Item Id | False | True | False | None | A user specified agreement item identifier. | False |  | 
| Agreement Start | False | True | False | None | The start date of the agreement as an ISO 8601 string. | False |  | 
| Agreement End | False | True | False | None | The end date of the agreement as an ISO 8601 string. | False |  | 
| Restrictions | False | True | False | None | A dictionary of property:value pairs describing restrictions. | False |  | 
| Obligations | False | True | False | None | A dictionary of property:value pairs describing obligations. | False |  | 
| Entitlements | False | True | False | None | A dictionary of property:value pairs describing entitlements. | False |  | 
| Usage Measurements | False | True | False | None | A dictionary of property:value pairs describing usage measurements. | False |  | 


___

# Create Term
## Term Name

Link Contracts

## Description

Attach or detach an agreement to an element describing the location of the contract documents.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Contract Id | False | True | False | None | Contract identifier. | False |  | 
| Contract Liaison | False | True | False | None | Name of the liaison for the contract. | False |  | 
| Contract Liaison Type | False | True | False | None | type of liaison. | False |  | 
| Contract Liaison Property Name | False | True | False | None |  | False |  | 


___

# Create Term
## Term Name

Link Subscriber->Subscription

## Description

Attach or detach a subscriber to a subscription. Subscriber can be any type of element.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Subscriber Id | False | True | False | None |  identifier of a subscriber. Initially, will let this be an arbitrary string - could harden this to a qualified name later if needed. | False |  | 
| Subscription | True | True | False | None | Name of the  subscription agreement. Recommend using qualified name. | False |  | 


___

# Create Term
## Term Name

Link Collection->Resource

## Description

Connect an existing collection to an element using the ResourceList relationship.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Collection Id | True | True | False | None | An element of base type collection (e.g. collection, agreement; subscription, ...) | False |  | 
| Resource Id | True | True | False | None | The name of the resource to attach to. | False |  | 
| Resource Use | False | True | False | None | Describes the relationship between the resource and the collection. | False |  | 
| Resource Description | False | True | False | None | A description of the resource being attached. | False |  | 
| Resource Properties | False | True | False | None | A dictionary of name:value pairs describing properties of the resource use. | False |  | 


___

# Create Term
## Term Name

Add Member->Collection

## Description

Add/Remove a member to/from a collection.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Element Id | True | True | False | None | The name of the element to add to the collection. | False |  | 
| Collection Id | True | True | False | None | The name of the collection to link to. There are many collection types, including Digital Products, Agreements and Subscriptions. | False |  | 
| Membership Rationale | False | True | False | None | Rationale for membership. | False |  | 
| Membership Status | False | True | False | None | The status of adding a member to a collection. | False | UNKNOWN; DISCOVERED; PROPOSED; IMPORTED; VALIDATED; DEPRECATED; OBSOLETE; OTHER | 


___

# Create Term
## Term Name

Create Data Dictionary

## Description

A Data Dictionary is an organized and curated collection of data definitions that can serve as a reference for data professionals

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the Data Dictionary | False |  | 
| Description | False | True | False | None | A description of the Data Dictionary. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Data Specification

## Description

A Data Specification defines the data requirements for a project or initiative. This includes the data structures , data fields and data classes.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the Data Specification. | False |  | 
| Description | False | True | False | None | A description of the Data Specification. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Data Structure

## Description

A collection of data fields that for a data specification for a data source.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the data structure. | False |  | 
| Description | False | True | False | None | A description of the data structure. | False |  | 
| In Data Specification | False | True | False | None | The data specifications this structure is a member of. | False |  | 
| In Data Dictionary | False | True | False | None | What data dictionaries is this data structure in? | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Data Field

## Description

A data field is a fundamental building block for a data structure.

## Glossary

Egeria-Markdown

## Folders

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
| In Data Dictionary | False | True | False | None | What data dictionaries is this data field in? | False |  | 
| Data Class | False | True | False | None | The data class that values of this data field conform to. | False |  | 
| isNullable | False | True | False | None | Can the values within the dataclass be absent? | False |  | 
| Minimum Length | False | True | False | None |  | False |  | 
| Length | False | True | False | None | The length of a value for a field. | False |  | 
| Precision | False | True | False | None | The precision of a numeric | False |  | 
| Ordered Values | False | True | False | None | is this field in an ordered list? | False |  | 
| Units | False | True | False | None | An optional string indicating the units of the field. | False |  | 
| Default Value | False | True | False | None | Specify a default value for the data class. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Data Class

## Description

Describes the data values that may be stored in data fields. Can be used to configure quality validators and data field classifiers.

## Glossary

Egeria-Markdown

## Folders

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
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Information Supply Chain

## Description

The flow of a particular type of data across a digital landscape.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the Information Supply Chain | False |  | 
| Description | False | True | False | None | A description of the data structure. | False |  | 
| Scope | False | True | False | None | Scope of the supply chain. | False |  | 
| Purposes | False | True | False | None | A list of purposes. | False |  | 
| Nested Information Supply Chains | False | True | False | None | A list of supply chains that compose this supply chain. | False |  | 
| In Information Supply Chain | False | True | False | None | Supply chains that this supply chain is in. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Solution Blueprint

## Description

A solution blueprint describes the architecture of a digital service in terms of solution components.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the Information Supply Chain | False |  | 
| Description | False | True | False | None | A description of the data structure. | False |  | 
| Solution Components | False | True | False | None | Solution components that make up the blueprint. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Solution Component

## Description

A reusable solution component.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the solution component. | False |  | 
| Description | False | True | False | None | A description of the data structure. | False |  | 
| Solution Component Type | False | True | False | None | Type of solution component. | False |  | 
| Planned Deployed Implementation Type | False | True | False | None | The planned implementation type for deployment. | False |  | 
| In Solution Components | False | True | False | None | Solution components that include this one. | False |  | 
| In Solution Blueprints | False | True | False | None | Solution Blueprints that contain this component. | False |  | 
| In Information Supply Chains | False | True | False | None | The Information Supply Chains that this component is a member of. | False |  | 
| Actors | False | True | False | None | Actors associated with this component. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Link Solution Component Peers

## Description

This command can be used to link or unlink wires between components.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Component1 | True | True | False | None | The  first component to link. | False |  | 
| Component2 | True | True | False | None | The  second component to link. | False |  | 
| Wire Label | False | True | False | None | Labels the link between two components. | False |  | 
| Description | False | True | False | None | A description of the wire. | False |  | 


___

# Create Term
## Term Name

Create Solution Role

## Description

A collection of data fields that for a data specification for a data source.

## Glossary

Egeria-Markdown

## Folders

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
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Link Information Supply Chain Peers

## Description

This command can be used to link or unlink information supply chain segments.

## Glossary

Egeria-Markdown

## Folders

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

Create Glossary

## Description

A grouping of definitions.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | The name of the glossary to create or update. | False |  | 
| Description | False | True | False | None | A description of the Glossary. | False |  | 
| Language | False | True | False | None | The language of the glossary. Note that multilingual descriptions are supported. Please see web site for details. | False |  | 
| Usage | False | True | False | None | A description of how the glossary is to be used. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Glossary Term

## Description



## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | The name of the term to create or update. | False |  | 
| Glossary | False | True | False | None | Zeroor more existing glossaries that a term is a member of. | False |  | 
| Summary | False | True | False | None | A summary description of the term. | False |  | 
| Description | False | True | False | None | A description of the term. | False |  | 
| Folders | False | True | False | None | Exixting folder collections that you'd like to make the term a member of. | False |  | 
| Abbreviation | False | True | False | None | An abbreviation for the term. | False |  | 
| Example | False | True | False | None | An example of how the term is used. | False |  | 
| Usage | False | True | False | None | A description of how the term is to be used. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Link Term-Term Relationship

## Description

Create a relationship between terms.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Term 1 | True | True | False | None | The name of the first term term to connect. | False |  | 
| Term 2 | True | True | False | None | The name of the second term term to connect. | False |  | 
| Relationship | True | True | False | None | The type of relationship to connecting the two terms. | False | Synonym;  Translation;  PreferredTerm; TermISATYPEOFRelationship;  TermTYPEDBYRelationship;  Antonym; ReplacementTerm;  ValidValue; TermHASARelationship; RelatedTerm;   ISARelationship | 
| Description | False | True | False | None | A description of the Relationship. | False |  | 
| Status | False | True | False | None |  | False |  | 


___

# Create Term
## Term Name

Create Project

## Description

An organized set of work.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | The name of the project to create or update. | False |  | 
| Description | False | True | False | None | A description of the Project. | False |  | 
| Project Type | False | True | False | None | A string classifiying the project. Current;y supported values are Campaign, Task. PersonalProject and StudyProject. | False |  | 
| Identifier | False | True | False | None | A user asigned identifier. | False |  | 
| Mission | False | True | False | None | The project mission. | False |  | 
| Purposes | False | True | False | None | A list of  project purposes. | False |  | 
| Start Date | False | True | False | None | Project start date as an ISO 8601 string. | False |  | 
| Planned End Date | False | True | False | None | Planned project end date as an ISO 8601 string. | False |  | 
| Priority | False | True | False | None | An integer priority for the project. | False |  | 
| Project Phase | False | True | False | None | A string describing the phase of the project. | False |  | 
| Project Status | False | True | False | None | A string representing the project status. | False |  | 
| Project Health | False | True | False | None | A string representing the health of the project. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Campaign

## Description

An organized set of work.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | The name of the project to create or update. | False |  | 
| Description | False | True | False | None | A description of the Project. | False |  | 
| Project Type | False | True | False | None | A string classifiying the project. Current;y supported values are Campaign, Task. PersonalProject and StudyProject. | False |  | 
| Identifier | False | True | False | None | A user asigned identifier. | False |  | 
| Mission | False | True | False | None | The project mission. | False |  | 
| Purposes | False | True | False | None | A list of  project purposes. | False |  | 
| Start Date | False | True | False | None | Project start date as an ISO 8601 string. | False |  | 
| Planned End Date | False | True | False | None | Planned project end date as an ISO 8601 string. | False |  | 
| Priority | False | True | False | None | An integer priority for the project. | False |  | 
| Project Phase | False | True | False | None | A string describing the phase of the project. | False |  | 
| Project Status | False | True | False | None | A string representing the project status. | False |  | 
| Project Health | False | True | False | None | A string representing the health of the project. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Task

## Description

A smaller  set of work.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | The name of the project to create or update. | False |  | 
| Description | False | True | False | None | A description of the Project. | False |  | 
| Project Type | False | True | False | None | A string classifiying the project. Current;y supported values are Campaign, Task. PersonalProject and StudyProject. | False |  | 
| Identifier | False | True | False | None | A user asigned identifier. | False |  | 
| Mission | False | True | False | None | The project mission. | False |  | 
| Purposes | False | True | False | None | A list of  project purposes. | False |  | 
| Start Date | False | True | False | None | Project start date as an ISO 8601 string. | False |  | 
| Planned End Date | False | True | False | None | Planned project end date as an ISO 8601 string. | False |  | 
| Priority | False | True | False | None | An integer priority for the project. | False |  | 
| Project Phase | False | True | False | None | A string describing the phase of the project. | False |  | 
| Project Status | False | True | False | None | A string representing the project status. | False |  | 
| Project Health | False | True | False | None | A string representing the health of the project. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Personal Project

## Description

A personal project.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | The name of the project to create or update. | False |  | 
| Description | False | True | False | None | A description of the Project. | False |  | 
| Project Type | False | True | False | None | A string classifiying the project. Current;y supported values are Campaign, Task. PersonalProject and StudyProject. | False |  | 
| Identifier | False | True | False | None | A user asigned identifier. | False |  | 
| Mission | False | True | False | None | The project mission. | False |  | 
| Purposes | False | True | False | None | A list of  project purposes. | False |  | 
| Start Date | False | True | False | None | Project start date as an ISO 8601 string. | False |  | 
| Planned End Date | False | True | False | None | Planned project end date as an ISO 8601 string. | False |  | 
| Priority | False | True | False | None | An integer priority for the project. | False |  | 
| Project Phase | False | True | False | None | A string describing the phase of the project. | False |  | 
| Project Status | False | True | False | None | A string representing the project status. | False |  | 
| Project Health | False | True | False | None | A string representing the health of the project. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Study Project

## Description

A personal project.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | The name of the project to create or update. | False |  | 
| Description | False | True | False | None | A description of the Project. | False |  | 
| Project Type | False | True | False | None | A string classifiying the project. Current;y supported values are Campaign, Task. PersonalProject and StudyProject. | False |  | 
| Identifier | False | True | False | None | A user asigned identifier. | False |  | 
| Mission | False | True | False | None | The project mission. | False |  | 
| Purposes | False | True | False | None | A list of  project purposes. | False |  | 
| Start Date | False | True | False | None | Project start date as an ISO 8601 string. | False |  | 
| Planned End Date | False | True | False | None | Planned project end date as an ISO 8601 string. | False |  | 
| Priority | False | True | False | None | An integer priority for the project. | False |  | 
| Project Phase | False | True | False | None | A string describing the phase of the project. | False |  | 
| Project Status | False | True | False | None | A string representing the project status. | False |  | 
| Project Health | False | True | False | None | A string representing the health of the project. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Link Project Hierarchy

## Description

Links or unlinks a parent project and child project.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Parent Project | True | True | False | None | The id of the parent project | False |  | 
| Child Project | True | True | False | None | The id of the child project | False |  | 
| Description | False | True | False | None | A description of the relationship.. | False |  | 
| Label | False | True | False | None | A user asigned label for this relationship. | False |  | 


___

# Create Term
## Term Name

Link Project Dependency

## Description

Links or unlinks a  project and dependent project.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Parent Project | True | True | False | None | The id of the project being depended on. | False |  | 
| Child Project | True | True | False | None | The id of the dependent project. | False |  | 
| Description | False | True | False | None | A description of the relationship. | False |  | 
| Label | False | True | False | None | A user asigned label for this relationship. | False |  | 


___

# Create Term
## Term Name

Create Governance Driver

## Description

A motivating topic leading to governance work.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Usage | False | True | False | None | How the governance definition will be used. | False |  | 
| Summary | False | True | False | None | Summary of the definition. | False |  | 
| Scope | False | True | False | None | Scope of the definition. | False |  | 
| Results | False | True | False | None | A list of expected results. | False |  | 
| Outcomes | False | True | False | None | List of desired outcomes. | False |  | 
| Importance | False | True | False | None | Importance of the definition. | False |  | 
| Implications | False | True | False | None | List of implications. | False |  | 
| Identifier | False | True | False | None | A user supplied identifier for the governance definition. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Governance Strategy

## Description

The strategy used in the development of the governance domains activities. How the governance domain supports the business strategy.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  | 
| Summary | False | True | False | None | Summary of the definition. | False |  | 
| Description | False | True | False | None | Description of the contents of the definition. | False |  | 
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  | 
| Identifier | False | True | False | None | A user supplied identifier for the governance definition. | False |  | 
| Usage | False | True | False | None | How the governance definition will be used. | False |  | 
| Scope | False | True | False | None | Scope of the definition. | False |  | 
| Importance | False | True | False | None | Importance of the definition. | False |  | 
| Implications | False | True | False | None | List of implications. | False |  | 
| Outcomes | False | True | False | None | List of desired outcomes. | False |  | 
| Results | False | True | False | None | A list of expected results. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Business Imperative

## Description

The BusinessImperative entity defines a business goal that is critical to the success of the organization.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  | 
| Summary | False | True | False | None | Summary of the definition. | False |  | 
| Description | False | True | False | None | Description of the contents of the definition. | False |  | 
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  | 
| Identifier | False | True | False | None | A user supplied identifier for the governance definition. | False |  | 
| Usage | False | True | False | None | How the governance definition will be used. | False |  | 
| Scope | False | True | False | None | Scope of the definition. | False |  | 
| Importance | False | True | False | None | Importance of the definition. | False |  | 
| Implications | False | True | False | None | List of implications. | False |  | 
| Outcomes | False | True | False | None | List of desired outcomes. | False |  | 
| Results | False | True | False | None | A list of expected results. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Regulation

## Description

Defines a relevant legal regulation that the business operation must comply with. Often regulations are divided into regulation articles.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  | 
| Summary | False | True | False | None | Summary of the definition. | False |  | 
| Description | False | True | False | None | Description of the contents of the definition. | False |  | 
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  | 
| Identifier | False | True | False | None | A user supplied identifier for the governance definition. | False |  | 
| Usage | False | True | False | None | How the governance definition will be used. | False |  | 
| Scope | False | True | False | None | Scope of the definition. | False |  | 
| Importance | False | True | False | None | Importance of the definition. | False |  | 
| Regulation Source | False | True | False | None |  The source of the regulation - often, an authority. | False |  | 
| Regulators | False | True | False | None | A list of regulators. | False |  | 
| Implications | False | True | False | None | List of implications. | False |  | 
| Outcomes | False | True | False | None | List of desired outcomes. | False |  | 
| Results | False | True | False | None | A list of expected results. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Regulation Article

## Description

A RegulationArticle entity is an article in a regulation. Dividing a regulation  simplifies planning and execution.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  | 
| Summary | False | True | False | None | Summary of the definition. | False |  | 
| Description | False | True | False | None | Description of the contents of the definition. | False |  | 
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  | 
| Identifier | False | True | False | None | A user supplied identifier for the governance definition. | False |  | 
| Usage | False | True | False | None | How the governance definition will be used. | False |  | 
| Scope | False | True | False | None | Scope of the definition. | False |  | 
| Importance | False | True | False | None | Importance of the definition. | False |  | 
| Implications | False | True | False | None | List of implications. | False |  | 
| Outcomes | False | True | False | None | List of desired outcomes. | False |  | 
| Results | False | True | False | None | A list of expected results. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Threat Definition

## Description

The Threat entity describes a particular threat to the organization's operations that must either be guarded against or accommodated to reduce its impact.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  | 
| Summary | False | True | False | None | Summary of the definition. | False |  | 
| Description | False | True | False | None | Description of the contents of the definition. | False |  | 
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  | 
| Identifier | False | True | False | None | A user supplied identifier for the governance definition. | False |  | 
| Usage | False | True | False | None | How the governance definition will be used. | False |  | 
| Scope | False | True | False | None | Scope of the definition. | False |  | 
| Importance | False | True | False | None | Importance of the definition. | False |  | 
| Implications | False | True | False | None | List of implications. | False |  | 
| Outcomes | False | True | False | None | List of desired outcomes. | False |  | 
| Results | False | True | False | None | A list of expected results. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Governance Policy

## Description

Policies  created in response to governance drivers. There are several types of policies.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  | 
| Summary | False | True | False | None | Summary of the definition. | False |  | 
| Description | False | True | False | None | Description of the contents of the definition. | False |  | 
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  | 
| Identifier | False | True | False | None | A user supplied identifier for the governance definition. | False |  | 
| Usage | False | True | False | None | How the governance definition will be used. | False |  | 
| Scope | False | True | False | None | Scope of the definition. | False |  | 
| Importance | False | True | False | None | Importance of the definition. | False |  | 
| Implications | False | True | False | None | List of implications. | False |  | 
| Outcomes | False | True | False | None | List of desired outcomes. | False |  | 
| Results | False | True | False | None | A list of expected results. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Governance Principle

## Description

The GovernancePrinciple entity defines a policy that describes an end state that the organization aims to achieve. 

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  | 
| Summary | False | True | False | None | Summary of the definition. | False |  | 
| Description | False | True | False | None | Description of the contents of the definition. | False |  | 
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  | 
| Identifier | False | True | False | None | A user supplied identifier for the governance definition. | False |  | 
| Usage | False | True | False | None | How the governance definition will be used. | False |  | 
| Scope | False | True | False | None | Scope of the definition. | False |  | 
| Importance | False | True | False | None | Importance of the definition. | False |  | 
| Implications | False | True | False | None | List of implications. | False |  | 
| Outcomes | False | True | False | None | List of desired outcomes. | False |  | 
| Results | False | True | False | None | A list of expected results. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Governance Obligation

## Description

The GovernanceObligation entity defines a policy that describes a requirement that must be met.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  | 
| Summary | False | True | False | None | Summary of the definition. | False |  | 
| Description | False | True | False | None | Description of the contents of the definition. | False |  | 
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  | 
| Identifier | False | True | False | None | A user supplied identifier for the governance definition. | False |  | 
| Usage | False | True | False | None | How the governance definition will be used. | False |  | 
| Scope | False | True | False | None | Scope of the definition. | False |  | 
| Importance | False | True | False | None | Importance of the definition. | False |  | 
| Implications | False | True | False | None | List of implications. | False |  | 
| Outcomes | False | True | False | None | List of desired outcomes. | False |  | 
| Results | False | True | False | None | A list of expected results. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Governance Approach

## Description

The GovernanceApproach entity defines a policy that describes a method that should be used for a particular activity.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  | 
| Summary | False | True | False | None | Summary of the definition. | False |  | 
| Description | False | True | False | None | Description of the contents of the definition. | False |  | 
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  | 
| Identifier | False | True | False | None | A user supplied identifier for the governance definition. | False |  | 
| Usage | False | True | False | None | How the governance definition will be used. | False |  | 
| Scope | False | True | False | None | Scope of the definition. | False |  | 
| Importance | False | True | False | None | Importance of the definition. | False |  | 
| Implications | False | True | False | None | List of implications. | False |  | 
| Outcomes | False | True | False | None | List of desired outcomes. | False |  | 
| Results | False | True | False | None | A list of expected results. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Governance Control

## Description

A governance control describes how a particular governance policy should be implemented. There are many types of controls.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  | 
| Summary | False | True | False | None | Summary of the definition. | False |  | 
| Description | False | True | False | None | Description of the contents of the definition. | False |  | 
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  | 
| Identifier | False | True | False | None | A user supplied identifier for the governance definition. | False |  | 
| Usage | False | True | False | None | How the governance definition will be used. | False |  | 
| Scope | False | True | False | None | Scope of the definition. | False |  | 
| Importance | False | True | False | None | Importance of the definition. | False |  | 
| Implications | False | True | False | None | List of implications. | False |  | 
| Outcomes | False | True | False | None | List of desired outcomes. | False |  | 
| Results | False | True | False | None | A list of expected results. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Governance Metric

## Description

A governance control describes how a particular governance policy should be implemented. There are many types of controls.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  | 
| Summary | False | True | False | None | Summary of the definition. | False |  | 
| Description | False | True | False | None | Description of the contents of the definition. | False |  | 
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  | 
| Identifier | False | True | False | None | A user supplied identifier for the governance definition. | False |  | 
| Usage | False | True | False | None | How the governance definition will be used. | False |  | 
| Scope | False | True | False | None | Scope of the definition. | False |  | 
| Importance | False | True | False | None | Importance of the definition. | False |  | 
| measurement | False | True | False | None | A measurement for a governance metric. | False |  | 
| target | False | True | False | None | Target values for a measurement. | False |  | 
| Implications | False | True | False | None | List of implications. | False |  | 
| Outcomes | False | True | False | None | List of desired outcomes. | False |  | 
| Results | False | True | False | None | A list of expected results. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Governance Action

## Description

An executable action, or sequence of actions to support a governance requirement.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  | 
| Summary | False | True | False | None | Summary of the definition. | False |  | 
| Description | False | True | False | None | Description of the contents of the definition. | False |  | 
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  | 
| Identifier | False | True | False | None | A user supplied identifier for the governance definition. | False |  | 
| Usage | False | True | False | None | How the governance definition will be used. | False |  | 
| Scope | False | True | False | None | Scope of the definition. | False |  | 
| Importance | False | True | False | None | Importance of the definition. | False |  | 
| Implications | False | True | False | None | List of implications. | False |  | 
| Outcomes | False | True | False | None | List of desired outcomes. | False |  | 
| Results | False | True | False | None | A list of expected results. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Data Processing Purpose

## Description

Privacy regulations such as  (GDPR) require data subjects to agree the processing that is permitted on their data. 

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  | 
| Summary | False | True | False | None | Summary of the definition. | False |  | 
| Description | False | True | False | None | Description of the contents of the definition. | False |  | 
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  | 
| Identifier | False | True | False | None | A user supplied identifier for the governance definition. | False |  | 
| Usage | False | True | False | None | How the governance definition will be used. | False |  | 
| Scope | False | True | False | None | Scope of the definition. | False |  | 
| Importance | False | True | False | None | Importance of the definition. | False |  | 
| Implications | False | True | False | None | List of implications. | False |  | 
| Outcomes | False | True | False | None | List of desired outcomes. | False |  | 
| Results | False | True | False | None | A list of expected results. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Governance Rule

## Description

An executable rule that can be deployed at particular points in the operations.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  | 
| Summary | False | True | False | None | Summary of the definition. | False |  | 
| Description | False | True | False | None | Description of the contents of the definition. | False |  | 
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  | 
| Document Identifier | False | True | False | None | A user supplied identifier for the governance document. | False |  | 
| Scope | False | True | False | None | Scope of the definition. | False |  | 
| Importance | False | True | False | None | Importance of the definition. | False |  | 
| Implementation Description | False | True | False | None | Describes how this governance control is implemnted. | False |  | 
| Supports Policies | False | True | False | None | The policies that this governance control supports. | False |  | 
| Implications | False | True | False | None | List of implications. | False |  | 
| Outcomes | False | True | False | None | List of desired outcomes. | False |  | 
| Results | False | True | False | None | A list of expected results. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Service Level Objectives

## Description

Defines the performance, availability and quality levels expected by the element attached.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  | 
| Summary | False | True | False | None | Summary of the definition. | False |  | 
| Description | False | True | False | None | Description of the contents of the definition. | False |  | 
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  | 
| Document Identifier | False | True | False | None | A user supplied identifier for the governance document. | False |  | 
| Scope | False | True | False | None | Scope of the definition. | False |  | 
| Importance | False | True | False | None | Importance of the definition. | False |  | 
| Implementation Description | False | True | False | None | Describes how this governance control is implemnted. | False |  | 
| Supports Policies | False | True | False | None | The policies that this governance control supports. | False |  | 
| Implications | False | True | False | None | List of implications. | False |  | 
| Outcomes | False | True | False | None | List of desired outcomes. | False |  | 
| Results | False | True | False | None | A list of expected results. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Governance Responsibility

## Description

A responsibility assigned to an actor or team. It could be a requirement to take a certain action in specific circumstances or to make decisions or give approvals for actions.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  | 
| Summary | False | True | False | None | Summary of the definition. | False |  | 
| Description | False | True | False | None | Description of the contents of the definition. | False |  | 
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  | 
| Document Identifier | False | True | False | None | A user supplied identifier for the governance document. | False |  | 
| Scope | False | True | False | None | Scope of the definition. | False |  | 
| Importance | False | True | False | None | Importance of the definition. | False |  | 
| Implementation Description | False | True | False | None | Describes how this governance control is implemnted. | False |  | 
| Supports Policies | False | True | False | None | The policies that this governance control supports. | False |  | 
| Implications | False | True | False | None | List of implications. | False |  | 
| Outcomes | False | True | False | None | List of desired outcomes. | False |  | 
| Results | False | True | False | None | A list of expected results. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Governance Procedure

## Description

A manual procedure that is performed under certain circumstances.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  | 
| Summary | False | True | False | None | Summary of the definition. | False |  | 
| Summary | False | True | False | None | Summary of the definition. | False |  | 
| Description | False | True | False | None | Description of the contents of the definition. | False |  | 
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  | 
| Document Identifier | False | True | False | None | A user supplied identifier for the governance document. | False |  | 
| Scope | False | True | False | None | Scope of the definition. | False |  | 
| Importance | False | True | False | None | Importance of the definition. | False |  | 
| Implementation Description | False | True | False | None | Describes how this governance control is implemnted. | False |  | 
| Supports Policies | False | True | False | None | The policies that this governance control supports. | False |  | 
| Implications | False | True | False | None | List of implications. | False |  | 
| Outcomes | False | True | False | None | List of desired outcomes. | False |  | 
| Results | False | True | False | None | A list of expected results. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Security Access Control

## Description

A technical control that defines the access control lists that an actor must belong to be entitled to perform a specific action.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  | 
| Summary | False | True | False | None | Summary of the definition. | False |  | 
| Description | False | True | False | None | Description of the contents of the definition. | False |  | 
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  | 
| Identifier | False | True | False | None | A user supplied identifier for the governance definition. | False |  | 
| Usage | False | True | False | None | How the governance definition will be used. | False |  | 
| Scope | False | True | False | None | Scope of the definition. | False |  | 
| Importance | False | True | False | None | Importance of the definition. | False |  | 
| Implications | False | True | False | None | List of implications. | False |  | 
| Outcomes | False | True | False | None | List of desired outcomes. | False |  | 
| Results | False | True | False | None | A list of expected results. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Governance Zone

## Description

A collection of assets that are used or processed in a specific way. Policies and controls can be attached to zones using the GovernedBy relationship.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  | 
| Summary | False | True | False | None | Summary of the definition. | False |  | 
| Description | False | True | False | None | Description of the contents of the definition. | False |  | 
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  | 
| Identifier | False | True | False | None | A user supplied identifier for the governance definition. | False |  | 
| Usage | False | True | False | None | How the governance definition will be used. | False |  | 
| Scope | False | True | False | None | Scope of the definition. | False |  | 
| Importance | False | True | False | None | Importance of the definition. | False |  | 
| criteria | False | True | False | None | The criteria for membership in a governance zone. | False |  | 
| Implications | False | True | False | None | List of implications. | False |  | 
| Outcomes | False | True | False | None | List of desired outcomes. | False |  | 
| Results | False | True | False | None | A list of expected results. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Security Group

## Description

A group of actors that need to be given the same access to a specific set of resources.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  | 
| Summary | False | True | False | None | Summary of the definition. | False |  | 
| Description | False | True | False | None | Description of the contents of the definition. | False |  | 
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  | 
| Identifier | False | True | False | None | A user supplied identifier for the governance definition. | False |  | 
| Usage | False | True | False | None | How the governance definition will be used. | False |  | 
| Scope | False | True | False | None | Scope of the definition. | False |  | 
| Importance | False | True | False | None | Importance of the definition. | False |  | 
| Implications | False | True | False | None | List of implications. | False |  | 
| Outcomes | False | True | False | None | List of desired outcomes. | False |  | 
| Results | False | True | False | None | A list of expected results. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create Naming Standard Rule

## Description

A standard for naming specific kinds of resources.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  | 
| Summary | False | True | False | None | Summary of the definition. | False |  | 
| Description | False | True | False | None | Description of the contents of the definition. | False |  | 
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  | 
| Document Identifier | False | True | False | None | A user supplied identifier for the governance document. | False |  | 
| Scope | False | True | False | None | Scope of the definition. | False |  | 
| Importance | False | True | False | None | Importance of the definition. | False |  | 
| Implementation Description | False | True | False | None | Describes how this governance control is implemnted. | False |  | 
| Supports Policies | False | True | False | None | The policies that this governance control supports. | False |  | 
| Name Patterns | False | True | False | None | List of implications. | False |  | 
| Outcomes | False | True | False | None | List of desired outcomes. | False |  | 
| Results | False | True | False | None | A list of expected results. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Link Terms & Conditions

## Description

Attach or detach an agreement to a defined set of terms and conditions.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Terms and Conditions are a form of governance control. | False |  | 
| Identifier | False | True | False | None | A user supplied identifier for the governance definition. | False |  | 
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  | 
| Summary | False | True | False | None | Summary of the definition. | False |  | 
| Scope | False | True | False | None | Scope of the definition. | False |  | 
| Usage | False | True | False | None | How the governance definition will be used. | False |  | 
| Importance | False | True | False | None | Importance of the definition. | False |  | 
| Implications | False | True | False | None | List of implications. | False |  | 
| Outcomes | False | True | False | None | List of desired outcomes. | False |  | 
| Results | False | True | False | None | A list of expected results. | False |  | 
| Description | False | True | False | None | Description of the contents of the definition. | False |  | 
| Identifier | False | True | False | None | A user specified  identifier. | False |  | 
| Domain Identifier | False | True | False | None | The governance domain of the governance definition. | False |  | 
| Restrictions | False | True | False | None | A dictionary of property:value pairs describing restrictions. | False |  | 
| Obligations | False | True | False | None | A dictionary of property:value pairs describing obligations. | False |  | 
| Entitlements | False | True | False | None | A dictionary of property:value pairs describing entitlements. | False |  | 


___

# Create Term
## Term Name

Create Certification Type

## Description

A type of certification.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  | 
| Summary | False | True | False | None | Summary of the definition. | False |  | 
| Description | False | True | False | None | Description of the contents of the definition. | False |  | 
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  | 
| Document Identifier | False | True | False | None | A user supplied identifier for the governance document. | False |  | 
| Scope | False | True | False | None | Scope of the definition. | False |  | 
| Usage | False | True | False | None | How the governance definition will be used. | False |  | 
| Importance | False | True | False | None | Importance of the definition. | False |  | 
| Details | False | True | False | None | Details of the certification. | False |  | 
| Implications | False | True | False | None | List of implications. | False |  | 
| Outcomes | False | True | False | None | List of desired outcomes. | False |  | 
| Results | False | True | False | None | A list of expected results. | False |  | 
| Restrictions | False | True | False | None | A dictionary of property:value pairs describing restrictions. | False |  | 
| Obligations | False | True | False | None | A dictionary of property:value pairs describing obligations. | False |  | 
| Entitlements | False | True | False | None | A dictionary of property:value pairs describing entitlements. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Create License Type

## Description

A type of license.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  | 
| Document Identifier | False | True | False | None | A user supplied identifier for the governance document. | False |  | 
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  | 
| Summary | False | True | False | None | Summary of the definition. | False |  | 
| Scope | False | True | False | None | Scope of the definition. | False |  | 
| Usage | False | True | False | None | How the governance definition will be used. | False |  | 
| Importance | False | True | False | None | Importance of the definition. | False |  | 
| Implications | False | True | False | None | List of implications. | False |  | 
| Outcomes | False | True | False | None | List of desired outcomes. | False |  | 
| Results | False | True | False | None | A list of expected results. | False |  | 
| Description | False | True | False | None | Description of the contents of the definition. | False |  | 
| Details | False | True | False | None | Details of the license. | False |  | 
| Restrictions | False | True | False | None | A dictionary of property:value pairs describing restrictions. | False |  | 
| Obligations | False | True | False | None | A dictionary of property:value pairs describing obligations. | False |  | 
| Entitlements | False | True | False | None | A dictionary of property:value pairs describing entitlements. | False |  | 
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  | 
| Category | False | True | False | None | A user specified category name that can be used for example, to define product types or agreement types. | False |  | 
| Version Identifier | False | True | False | None | Published product version identifier. | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Identifier | False | True | False | None | role identifier | False |  | 
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  | 
| GUID | False | False | True | None | A system generated unique identifier. | True |  | 
| Journal Entry | False | True | False | None |  | False |  | 
| URL | False | True | False | None | Link to supporting information | False |  | 
| Search Keywords | False | True | False | None | Keywords to facilitate finding the element | False |  | 


___

# Create Term
## Term Name

Link Governed By

## Description

A referenceable element can be governed by one or more governance definitions. 

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Governance Definition | True | True | False | None | The governance definition providing governance. | False |  | 
| Referenceable | True | True | False | None | The object being governed. | False |  | 
| Link Label | False | True | False | None | Labels the link between two elements. | False |  | 
| Description | False | True | False | None | A description of the relationship. | False |  | 


___

# Create Term
## Term Name

Link License

## Description

A license relationship between a license type and a Referencable element.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| License Type | True | True | False | None | The license type being used for the license. | False |  | 
| Referenceable | True | True | False | None | The object being licensed. | False |  | 
| License GUID | False | True | False | None | Unique identifier of the license. | True |  | 
| Start Date | False | True | False | None | Date at which the license takes effect. | False |  | 
| End Date | False | True | False | None | Date at which the license expires. | False |  | 
| Conditions | False | True | False | None | License conditions. | False |  | 
| Licensed By | False | True | False | None |  | False |  | 
| Licensed By Type Name | False | True | False | None |  | False |  | 
| Licensed By Property Name | False | True | False | None |  | False |  | 
| Custodian | False | True | False | None | Custodian of the license. | False |  | 
| Custodian Type Name | False | True | False | None |  | False |  | 
| Custodian Property Name | False | True | False | None |  | False |  | 
| Licensee | False | True | False | None | The licensee. | False |  | 
| Licensee Type Name | False | True | False | None |  | False |  | 
| Licensee Property Name | False | True | False | None |  | False |  | 
| Entitlements | False | True | False | None | What the license grants to the licensee. | False |  | 
| Restrictions | False | True | False | None | Restrictions imposed by the license. | False |  | 
| Obligations | False | True | False | None | Obligations defined by the license. | False |  | 
| Notes | False | True | False | None | Notes about the license. | False |  | 


___

# Create Term
## Term Name

Link Certification

## Description

A certification relationship between a certification type and a referenceable element.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Certification Type | True | True | False | None | The license type being used for the license. | False |  | 
| Referenceable | True | True | False | None | The object being certified. | False |  | 
| Certificate GUID | False | True | False | None | Unique identifier of the certificate. | True |  | 
| Start Date | False | True | False | None | Date at which the certification takes effect. | False |  | 
| End Date | False | True | False | None | Date at which the certification expires. | False |  | 
| Conditions | False | True | False | None | Certification conditions. | False |  | 
| Certified By | False | True | False | None |  | False |  | 
| Certified By Type Name | False | True | False | None |  | False |  | 
| Certified By Property Name | False | True | False | None |  | False |  | 
| Custodian | False | True | False | None | Custodian of the certification. | False |  | 
| Custodian Type Name | False | True | False | None |  | False |  | 
| Custodian Property Name | False | True | False | None |  | False |  | 
| Recipient | False | True | False | None | The receiver of the certification. | False |  | 
| Recipient Type Name | False | True | False | None |  | False |  | 
| Recipient Property Name | False | True | False | None |  | False |  | 
| Notes | False | True | False | None | Notes about the certification. | False |  | 


___

# Create Term
## Term Name

Link Regulation Certification Type

## Description

A certification type addressing a specific regulation.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Certification Type | True | True | False | None | The license type being used for the license. | False |  | 
| Regulation | True | True | False | None | The regulation that a certification type addresses. | False |  | 


___

# Create Term
## Term Name

Link Agreement->T&C

## Description

Attach or detach an agreement to a defined set of terms and conditions.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Agreement Name | True | True | False | None | The name of the agreement to add an item to. Using qualified names is recommended. | False |  | 
| Identifier | False | True | False | None | A user specified  identifier. | False |  | 
| Domain Identifier | False | True | False | None | The governance domain of the governance definition. | False |  | 
| T&C Definition Name | True | True | False | None | The name of the Terms and Conditions definition that governans an agreement.  Using qualified names is recommended. | False |  | 
| Implementation Description | False | True | False | None | How the Terms and Conditions are implemented. | False |  | 
| Agreement Start | False | True | False | None | The start date of the agreement as an ISO 8601 string. | False |  | 
| Agreement End | False | True | False | None | The end date of the agreement as an ISO 8601 string. | False |  | 
| Restrictions | False | True | False | None | A dictionary of property:value pairs describing restrictions. | False |  | 
| Obligations | False | True | False | None | A dictionary of property:value pairs describing obligations. | False |  | 
| Entitlements | False | True | False | None | A dictionary of property:value pairs describing entitlements. | False |  | 
| Usage Measurements | False | True | False | None | A dictionary of property:value pairs describing usage measurements. | False |  | 


___

# Create Term
## Term Name

Link Governance Drivers

## Description

Link peer governance drivers with the GovernanceDriverLink relationship. Drivers are: GovernanceStrategy, BusinessImperitive, Regulation, RegulationArticle, Threat.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Definition 1 | True | True | False | None | The  first governance driver to link. | False |  | 
| Definition 2 | True | True | False | None | The  second governance driver to link. | False |  | 
| Link Label | False | True | False | None | Labels the link between two governance defninitions. | False |  | 
| Description | False | True | False | None | A description of the relationship. | False |  | 


___

# Create Term
## Term Name

Link Governance Response

## Description

Links Policies as a response to governance Drivers.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Definition 1 | True | True | False | None | The  first governance driver to link. | False |  | 
| Definition 2 | True | True | False | None | The  second governance driver to link. | False |  | 
| Link Label | False | True | False | None | Labels the link between two governance defninitions. | False |  | 
| Description | False | True | False | None | A description of the relationship. | False |  | 
| Rationale | False | True | False | None | The rationale for using this control to  support this policy. | False |  | 


___

# Create Term
## Term Name

Link Security Group -> Security Access Control

## Description

Establishes that a Security Access Control applies to this Security Group.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Definition 1 | True | True | False | None | The  first governance policy to link. | False |  | 
| Definition 2 | True | True | False | None | The  second governance policy to link. | False |  | 
| Link Label | False | True | False | None | Labels the link between two governance defninitions. | False |  | 
| Description | False | True | False | None | A description of the relationship. | False |  | 
| Operation Name | False | True | False | None | The name of the operation controled by the SecurityAccessControl. | False |  | 


___

# Create Term
## Term Name

Link Governance Policies

## Description

Link peer governance policies with the GovernancePolicyLink relationship. Policies types are: GovernancePrinciple, GovernanceObligation, GovernanceApproach.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Definition 1 | True | True | False | None | The  first governance policy to link. | False |  | 
| Definition 2 | True | True | False | None | The  second governance policy to link. | False |  | 
| Link Label | False | True | False | None | Labels the link between two governance defninitions. | False |  | 
| Description | False | True | False | None | A description of the relationship. | False |  | 


___

# Create Term
## Term Name

Link Governance Mechanism

## Description

Link a governance policy to a governance control that supports it. The GovernanceMechanism relationship is used.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Definition 1 | True | True | False | None | The  first governance policy to link. | False |  | 
| Definition 2 | True | True | False | None | The  second governance policy to link. | False |  | 
| Link Label | False | True | False | None | Labels the link between two governance defninitions. | False |  | 
| Description | False | True | False | None | A description of the relationship. | False |  | 
| Rationale | False | True | False | None | The rationale for using this control to  support this policy. | False |  | 


___

# Create Term
## Term Name

Link Governance Controls

## Description

Link peer governance controls with the GovernanceControlLink relationship. Controls types are: GovernanceRule, GovernanceProcess, GovernanceResponsibility, GovernanceProcedure, SecurityAccessControl, SecurityGroup.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Control Definition 1 | True | True | False | None | The  first governance control to link. | False |  | 
| Control Definition 2 | True | True | False | None | The  fsecond governance control to link. | False |  | 
| Link Label | False | True | False | None | Labels the link between two governance defninitions. | False |  | 
| Description | False | True | False | None | A description of the relationship. | False |  | 


___

# Create Term
## Term Name

Link Zone->Zone

## Description

Links child governance zones to parent governance zone.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Control Definition 1 | True | True | False | None | The  first governance control to link. | False |  | 
| Control Definition 2 | True | True | False | None | The  fsecond governance control to link. | False |  | 
| Link Label | False | True | False | None | Labels the link between two governance defninitions. | False |  | 
| Description | False | True | False | None | A description of the relationship. | False |  | 


___

# Create Term
## Term Name

View Report

## Description

This can be used to produce a report using any output format set.

## Glossary

Egeria-Markdown

## Folders

Writing Dr.Egeria Markdown

## Usage

| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Search String | False | True | False | None | An optional search string to filter results by. | False |  | 
| Output Format | False | True | False | None | Optional specification of output format for the query. | False | LIST; FORM; REPORT; MERMAID; DICT | 
| Output Format Set | True | True | False | None | Optional specification of an output format set that defines the attributes/columns that will be returned. | False |  | 
| Starts With | False | True | False | None | If true, look for matches with the search string starting from the beginning of  a field. | False |  | 
| Ends With | False | True | False | None | If true, look for matches with the search string starting from the end of  a field. | False |  | 
| Ignore Case | False | True | False | None | If true, ignore the difference between upper and lower characters when matching the search string. | False |  | 
| Metadata Element Subtype Names | False | True | False | None | Filter results by the list of metadata elements. If none are provided, then no status filtering will be performed. | False |  | 
| Metadata Element Type Name | False | True | False | None | Optionally filter results by the type of metadata element. | False |  | 
| Skip Relationshjps | False | True | False | None | Allow listed relationships to be skipped in the output returned. | False |  | 
| Include Only Relationships | False | True | False | None | Include information only about specified relationships. | False |  | 
| Skip Classified Elements | False | True | False | None | Skip elements with the any of the specified classifications. | False |  | 
| Include Only Classified Elements | False | True | False | None | Include only elements with the specified classifications. | False |  | 
| Governance Zone Filter | False | True | False | None | Include only elements in one of the specified governance zones. | False |  | 
| Graph Query Depth | False | True | False | None | The depth of the hierarchy to return. Default is 5. Specifying 0 returns only the top level attributes.  | False |  | 
| AsOfTime | False | True | False | None | An ISO-8601 string representing the time to view the state of the repository. | False |  | 
| Sort Order | False | True | False | None | How to order the results. The sort order can be selected from a list of valid value. | False | ANY; CREATION_DATE_RECENT; CREATION_DATA_OLDEST; LAST_UPDATE_RECENT; LAST_UPDATE_OLDEST; PROPERTY_ASCENDING; PROPERTY_DESCENDING | 
| Order Property Name | False | True | False | None | The property to use for sorting if the sort_order_property is PROPERTY_ASCENDING or PROPERTY_DESCENDING | False |  | 
| Page Size | False | True | False | None | The number of elements returned per page. | False |  | 
| Start From | False | True | False | None | When paging through results, the starting point of the results to return. | False |  | 


___

