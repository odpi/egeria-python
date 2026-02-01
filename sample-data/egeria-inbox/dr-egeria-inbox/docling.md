[docling-Get your documents ready for gen AI](https://github.com/docling-project/docling) - Data Ingestion

Can be used standalone or in the context of the [[Data Prep Kit]]].

1. First we'll define an external references to the web pages for Docling.
2. Define an initial component for Docling - the issue seems to be that it can be deployed in many ways.


____
# Update Solution Component
>	A reusable solution component.

## Display Name
>	**Input Required**: True

>	**Description**: Name of the solution component.

>	**Alternative Labels**: Name; Display Name; Solution Component Name; Component Name

Docling-Component
## Qualified Name
>	**Input Required**: False

>	**Description**: A unique qualified name for the element. Generated using the qualified name pattern  if not user specified.

SolutionComponent::Docling::V1.0

## URL
https://docling-project.github.io/docling/

## Category
>	**Input Required**: False

>	**Description**: A user specified category name that can be used for example, to define product types or agreement types.

ML-OPs
## Description
>	**Input Required**: False

>	**Description**: A description of the data structure.

Docling simplifies document processing, parsing diverse formats — including advanced PDF understanding — and providing seamless integrations with the gen AI ecosystem.

## Status
>	**Input Required**: False

>	**Description**: The status of the solution component. There is a list of valid values that this conforms to.

>	**Valid Values**: DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED;  ACTIVE; DEPRECATED; OTHER

>	**Default Value**: ACTIVE

## Journal Entry
This is a first test to see if a journal entry appears for docling.

## Solution Component Type
>	**Input Required**: False

>	**Description**: Type of solution component.

>	**Alternative Labels**: Soln Component Type

Python Library
## Planned Deployed Implementation Type
>	**Input Required**: False

>	**Description**: The planned implementation type for deployment.

>	**Alternative Labels**: Planned Deployed Impl Type

DeployedSoftwareComponent
## User Defined Status
>	**Input Required**: False

>	**Description**: Supporting user managed lifecycle statuses. Only used if the Initial Status is set to OTHER.

>	**Default Value**: DRAFT


## Initial Status
>	**Input Required**: False

>	**Description**: Optional lifecycle status. If not specified, set to ACTIVE. If set to Other then the value in User Defined Status will be used.

>	**Valid Values**: DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; ACTIVE; DISABLED; DEPRECATED; OTHER

>	**Default Value**: ACTIVE


## In Solution Components
>	**Input Required**: False

>	**Description**: Solution components that include this one.

>	**Alternative Labels**: In Solution Component; In Component

SolutionComponent::Data-Prep-Kit::V1.0

## In Solution Blueprints
>	**Input Required**: False

>	**Description**: Solution Blueprints that contain this component.

>	**Alternative Labels**: In Solution Blueprints

SolutionBlueprint::Local-Data-Prep-Blueprint-for-ML-OPs::0.1, SolutionBlueprint::Data-Prep-Prod-Blueprint-for-ML-OPs::0.1
## In Information Supply Chains
>	**Input Required**: False

>	**Description**: The Information Supply Chains that this component is a member of.

>	**Alternative Labels**: In Supply Chains; In Supply Chain; In Information Supply Chain


## Actors
>	**Input Required**: False

>	**Description**: Actors associated with this component.


## GUID
>	**Input Required**: False

>	**Description**: A system generated unique identifier.

>	**Alternative Labels**: Guid; guid


## Effective Time
>	**Input Required**: False

>	**Description**: An ISO-8601 string representing the time to use for evaluating effectivity of the elements related to this one.


## Effective From
>	**Input Required**: False

>	**Description**: A string in ISO-8601 format that defines the when an element becomes effective (visible).


## Effective To
>	**Input Required**: False

>	**Description**: A string in ISO-8601 format that defines the when an element is no longer effective (visible).


## Merge Update
>	**Input Required**: False

>	**Description**: If true, only those attributes specified in the update will be updated; If false, any attributes not provided during the update will be set to None.

>	**Alternative Labels**: Merge

>	**Default Value**: True


## Additional Properties
>	**Input Required**: False

>	**Description**: Additional user defined values organized as name value pairs in a dictionary.


## Glossary Term
>	**Input Required**: False

>	**Description**: Term that provides meaning to this field.


## External Source GUID
>	**Input Required**: False

>	**Description**: Identifier of an external source that is associated with this element.


## External Source Name
>	**Input Required**: False

>	**Description**: Name of an external element that is associated with this element.

____

# Update Cited Document
>	A cited document

## Display Name
>	**Input Required**: True

>	**Description**: Name of the digital product

>	**Alternative Labels**: Name; Folder Name; Collection Name; Collection

Docling: An Efficient Open-Source Toolkit for AI-driven Document Conversion

## Description
>	**Input Required**: False

>	**Description**: Description of the contents of a product.

Embeddable or standalone tool to convert documents and images into an ML appropriate form.

## Category
>	**Input Required**: False

>	**Description**: A user specified category name that can be used for example, to define product types or agreement types.

>	**Alternative Labels**: Category Name

MLOPS

## Reference Title
>	**Input Required**: False

>	**Description**: Title of the external reference.

>	**Alternative Labels**: Title

Docling: An Efficient Open-Source Toolkit for AI-driven Document Conversion
## Reference Abstract
>	**Input Required**: False

>	**Description**: Abstract for the remote reference.

>	**Alternative Labels**: Abstract

We introduce Docling, an easy-to-use, self-contained, MIT-licensed, open-source toolkit for document conversion, that can parse several types of popular document formats into a unified, richly structured representation. It is powered by state-of-the-art specialized AI models for layout analysis (DocLayNet) and table structure recognition (TableFormer), and runs efficiently on commodity hardware in a small resource budget. Docling is released as a Python package and can be used as a Python API or as a CLI tool. Docling's modular architecture and efficient document representation make it easy to implement extensions, new features, models, and customizations. Docling has been already integrated in other popular open-source frameworks (e.g., LangChain, LlamaIndex, spaCy), making it a natural fit for the processing of documents and the development of high-end applications. The open-source community has fully engaged in using, promoting, and developing for Docling, which gathered 10k stars on GitHub in less than a month and was reported as the No. 1 trending repository in GitHub worldwide in November 2024.

## Authors
>	**Input Required**: False

>	**Description**: A list of authors.

>	**Alternative Labels**: Author
[Nikolaos Livathinos](https://arxiv.org/search/cs?searchtype=author&query=Livathinos), [Christoph Auer](https://arxiv.org/search/cs?searchtype=author&query=Auer), [Maksym Lysak](https://arxiv.org/search/cs?searchtype=author&query=Lysak), [Ahmed Nassar](https://arxiv.org/search/cs?searchtype=author&query=Nassar), [Michele Dolfi](https://arxiv.org/search/cs?searchtype=author&query=Dolfi), [Panos Vagenas](https://arxiv.org/search/cs?searchtype=author&query=Vagenas), [Cesar Berrospi Ramis](https://arxiv.org/search/cs?searchtype=author&query=Ramis), [Matteo Omenetti](https://arxiv.org/search/cs?searchtype=author&query=Omenetti), [Kasper Dinkla](https://arxiv.org/search/cs?searchtype=author&query=Dinkla), [Yusik Kim](https://arxiv.org/search/cs?searchtype=author&query=Kim), [Shubham Gupta](https://arxiv.org/search/cs?searchtype=author&query=Gupta), [Rafael Teixeira de Lima](https://arxiv.org/search/cs?searchtype=author&query=de+Lima), [Valery Weber](https://arxiv.org/search/cs?searchtype=author&query=Weber), [Lucas Morin](https://arxiv.org/search/cs?searchtype=author&query=Morin), [Ingmar Meijer](https://arxiv.org/search/cs?searchtype=author&query=Meijer), [Viktor Kuropiatnyk](https://arxiv.org/search/cs?searchtype=author&query=Kuropiatnyk), [Peter W. J. Staar](https://arxiv.org/search/cs?searchtype=author&query=Staar)  

## Organization
>	**Input Required**: False

>	**Description**: Organization owning the external reference.

>	**Alternative Labels**: Category Name


## URL
>	**Input Required**: False

>	**Description**: URL to access the external reference.

https://arxiv.org/abs/2501.17887
## Sources
>	**Input Required**: False

>	**Description**: A map of source strings.

>	**Alternative Labels**: Reference Sources


## License
>	**Input Required**: False

>	**Description**: The license associated with the external reference.

MIT License

## Copyright
>	**Input Required**: False

>	**Description**: The copy right associated with the external reference.

2025
## Attribution
>	**Input Required**: False

>	**Description**: Attribution string to describe the external reference.


## Number of Pages
>	**Input Required**: False

>	**Description**: The number of pages in the document.
8

## Page Range
>	**Input Required**: False

>	**Description**: The range of pages cited.


## Publication Series
>	**Input Required**: False

>	**Description**: The series this publication is part of.

>	**Alternative Labels**: Series


## Publication Series Volume
>	**Input Required**: False

>	**Description**: The volume in the series that contains the citation.


## Publisher
>	**Input Required**: False

>	**Description**: The name of the publisher.


## Edition
>	**Input Required**: False

>	**Description**: The edition being cited.


## First Publication Date
>	**Input Required**: False

>	**Description**: Date of first publication written as an ISO string - 2025-01-31


## Publication Date
>	**Input Required**: False

>	**Description**: Publication date.  In ISO 8601 format - 2025-02-23.


## Publication City
>	**Input Required**: False

>	**Description**: City of publication.


## Publication Year
>	**Input Required**: False

>	**Description**: Year of publication.


## Publication Numbers
>	**Input Required**: False

>	**Description**: Identification numbers of the publication, if relevant.


## Version Identifier
>	**Input Required**: False

>	**Description**: Published product version identifier.

>	**Default Value**: 1.0


## Classifications
>	**Input Required**: False

>	**Description**: Optionally specify the initial classifications for a collection. Multiple classifications can be specified. 

>	**Alternative Labels**: classification


## Qualified Name
>	**Input Required**: False

>	**Description**: A unique qualified name for the element. Generated using the qualified name pattern  if not user specified.


## GUID
>	**Input Required**: False

>	**Description**: A system generated unique identifier.

>	**Alternative Labels**: Guid; guid

____

# Link Cited Document Link
>	Link a cited document reference to a referenceable.

## Element Name
>	**Input Required**: True

>	**Description**: A referenceable to link.

>	**Alternative Labels**: Referenceable

SolutionComponent::Docling::V1.0

## Cited Document
>	**Input Required**: True

>	**Description**: The cited document to link to.

Docling: An Efficient Open-Source Toolkit for AI-driven Document Conversion

## Label
>	**Input Required**: False

>	**Description**: Labels the link between the referenceable and the media reference.


## Description
>	**Input Required**: False

>	**Description**: A description of the link.


## Reference  Id
>	**Input Required**: False

>	**Description**: An identifier of the cited document to link to.


## Pages
>	**Input Required**: False

>	**Description**: The pages referenced.

