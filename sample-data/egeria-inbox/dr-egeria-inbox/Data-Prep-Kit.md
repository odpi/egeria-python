[data-prep-kit](https://github.com/data-prep-kit/data-prep-kit)- Data Prep

1. First we'll define an external references to the web pages for Data Prep Kit, Git, and papers.
2. Define an initial component for DPK - the issue seems to be that it can run stand-alone, on spark or on ray.


# Don't Update Cited Document
>	A cited document

## Display Name
>	**Input Required**: True

>	**Description**: Name of the digital product

>	**Alternative Labels**: Name; Folder Name; Collection Name; Collection

Data Prep Kit

## Description
>	**Input Required**: False

>	**Description**: Description of the contents of a product.

Data Prep Kit accelerates unstructured data preparation for LLM app developers. Developers can use Data Prep Kit to cleanse, transform, and enrich use case-specific unstructured data to pre-train LLMs, fine-tune LLMs, instruct-tune LLMs, or build retrieval augmented generation (RAG) applications for LLMs. Data Prep Kit can readily scale from a commodity laptop all the way to data center scale.
## Category
>	**Input Required**: False

>	**Description**: A user specified category name that can be used for example, to define product types or agreement types.

>	**Alternative Labels**: Category Name

ML-OPs
## Journal Entry
Puddy says meow

## Reference Title
>	**Input Required**: False

>	**Description**: Title of the external reference.

>	**Alternative Labels**: Title

Data-Prep-Kit: getting your data ready for LLM application development
## Reference Abstract
>	**Input Required**: False

>	**Description**: Abstract for the remote reference.

>	**Alternative Labels**: Abstract

**Data preparation is the first and a very important**

**step towards any Large Language Model (LLM) development.**

**This paper introduces an easy-to-use, extensible, and scale-flexible**

**open-source data preparation toolkit called** **_Data Prep Kit_** **(****_DPK_****).**

**_DPK_** **is architected and designed to enable users to scale their data**

**preparation to their needs. With DPK they can prepare data on a**

**local machine or effortlessly scale to run on a cluster with**

**thousands of CPU Cores. DPK comes with a highly scalable, yet**

**extensible set of modules that transform natural language and**

**code data. If the user needs additional transforms, they can be**

**easily developed using extensive DPK support for transform**

**creation. These modules can be used independently or pipelined to**

**perform a series of operations. In this paper, we describe DPK**

**architecture and show its performance from a small scale to a very**

**large number of CPUs. The modules from** **_DPK_** **have been used for**

**the preparation of Granite Models [1] [2].** **We believe DPK is a**

**valuable contribution to the AI community to easily prepare data**

**to enhance the performance of their LLM models or to fine-tune**

**models with Retrieval-Augmented Generation (RAG).**
## Authors
>	**Input Required**: False

>	**Description**: A list of authors.

>	**Alternative Labels**: Author

IBM Research
## Organization
>	**Input Required**: False

>	**Description**: Organization owning the external reference.

>	**Alternative Labels**: Category Name


## URL
>	**Input Required**: False

>	**Description**: URL to access the external reference.

https://arxiv.org/pdf/2409.18164
## Sources
>	**Input Required**: False

>	**Description**: A map of source strings.

>	**Alternative Labels**: Reference Sources


## License
>	**Input Required**: False

>	**Description**: The license associated with the external reference.


## Copyright
>	**Input Required**: False

>	**Description**: The copy right associated with the external reference.

IBM Research

## Attribution
>	**Input Required**: False

>	**Description**: Attribution string to describe the external reference.

@misc{wood2024dataprepkitgettingdataready,
      title={Data-Prep-Kit: getting your data ready for LLM application development}, 
      author={David Wood and Boris Lublinsky and Alexy Roytman and Shivdeep Singh 
      and Constantin Adam and Abdulhamid Adebayo and Sungeun An and Yuan Chi Chang 
      and Xuan-Hong Dang and Nirmit Desai and Michele Dolfi and Hajar Emami-Gohari 
      and Revital Eres and Takuya Goto and Dhiraj Joshi and Yan Koyfman 
      and Mohammad Nassar and Hima Patel and Paramesvaran Selvam and Yousaf Shah  
      and Saptha Surendran and Daiki Tsuzuku and Petros Zerfos and Shahrokh Daijavad},
      year={2024},
      eprint={2409.18164},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2409.18164}, 
}

## Number of Pages
>	**Input Required**: False

>	**Description**: The number of pages in the document.
10

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

ExtRef::Data-Prep-Kit
## GUID
>	**Input Required**: False

>	**Description**: A system generated unique identifier.

>	**Alternative Labels**: Guid; guid



____

# Create Solution Component
>	A reusable solution component.

## Display Name
>	**Input Required**: True

>	**Description**: Name of the solution component.

>	**Alternative Labels**: Name; Display Name; Solution Component Name; Component Name

Data-Prep-Kit
## Qualified Name
>	**Input Required**: False

>	**Description**: A unique qualified name for the element. Generated using the qualified name pattern  if not user specified.

SolutionComponent::Data-Prep-Kit::V1.0
## Category
>	**Input Required**: False

>	**Description**: A user specified category name that can be used for example, to define product types or agreement types.

ML-OPs
## Description
>	**Input Required**: False

>	**Description**: A description of the data structure.

Data Prep Kit accelerates unstructured data preparation for LLM app developers. Developers can use Data Prep Kit to cleanse, transform, and enrich use case-specific unstructured data to pre-train LLMs, fine-tune LLMs, instruct-tune LLMs, or build [Retrieval Augmented Generation (RAG)](https://github.com/data-prep-kit/data-prep-kit/blob/dev/examples/rag-html-1/README.md) applications for LLMs

Data Prep Kit can readily scale from a commodity laptop all the way to data center scale.

## Status
>	**Input Required**: False

>	**Description**: The status of the solution component. There is a list of valid values that this conforms to.

>	**Valid Values**: DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED;  ACTIVE; DEPRECATED; OTHER

>	**Default Value**: ACTIVE



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


## In Solution Blueprints
>	**Input Required**: False

>	**Description**: Solution Blueprints that contain this component.

>	**Alternative Labels**: In Solution Blueprints

SolutionBlueprint::Data-Prep-Prod-Blueprint-for-ML-OPs::0.1
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

# Don't Link External Reference Link

## Element Name

SolutionComponent::Data-Prep-Kit::V1.0

## External Reference
ExtRef::Data-Prep-Kit

## Label
Link to Paper

