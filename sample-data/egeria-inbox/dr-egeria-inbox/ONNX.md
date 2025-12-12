 [ONNX Runtime](https://onnxruntime.ai/)- Machine Learning Runtime

1. First we'll define an external references to the web pages for ONNX.
2. Define an initial component for ONNX.

____

# Create External Reference
>	Create or update External Reference Elements - or sub-types Related Media, Cited Documents, External Data Source and External Model Source.

## Display Name
>	**Input Required**: True

>	**Description**: Name of the digital product

>	**Alternative Labels**: Name; Folder Name; Collection Name; Collection

ONNX
## Description
>	**Input Required**: False

>	**Description**: Description of the contents of a product.

Production-grade AI engine to speed up training and inferencing in your existing technology stack.
## Category
>	**Input Required**: False

>	**Description**: A user specified category name that can be used for example, to define product types or agreement types.

>	**Alternative Labels**: Category Name

ML-OPs

## Reference Title
>	**Input Required**: False

>	**Description**: Title of the external reference.

>	**Alternative Labels**: Title


## Reference Abstract
>	**Input Required**: False

>	**Description**: Abstract for the remote reference.

>	**Alternative Labels**: Abstract

Integrate the power of Generative AI and Large language Models (LLMs) in your apps and services with ONNX Runtime. No matter what language you develop in or what platform you need to run on, you can make use of state-of-the-art models for image synthesis, text generation, and more.
## Authors
>	**Input Required**: False

>	**Description**: A list of authors.

>	**Alternative Labels**: Author


## Organization
>	**Input Required**: False

>	**Description**: Organization owning the external reference.

Microsoft
## URL
>	**Input Required**: False

>	**Description**: URL to access the external reference.

https://onnxruntime.ai/

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


## Attribution
>	**Input Required**: False

>	**Description**: Attribution string to describe the external reference.


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

ExtRef::ONNX

## GUID
>	**Input Required**: False

>	**Description**: A system generated unique identifier.

>	**Alternative Labels**: Guid; guid


## Additional Properties
>	**Input Required**: False

>	**Description**: Additional user defined values organized as name value pairs in a dictionary.


____

# Create Solution Component
>	A reusable solution component.

## Display Name
>	**Input Required**: True

>	**Description**: Name of the solution component.

>	**Alternative Labels**: Name; Display Name; Solution Component Name; Component Name

ONNX
## Qualified Name
>	**Input Required**: False

>	**Description**: A unique qualified name for the element. Generated using the qualified name pattern  if not user specified.

SolutionComponent::ONNX::V1.0
## Category
>	**Input Required**: False

>	**Description**: A user specified category name that can be used for example, to define product types or agreement types.

ML-OPs
## Description
>	**Input Required**: False

>	**Description**: A description of the data structure.

**ONNX Runtime is a cross-platform inference and training machine-learning accelerator**.

**ONNX Runtime inference** can enable faster customer experiences and lower costs, supporting models from deep learning frameworks such as PyTorch and TensorFlow/Keras as well as classical machine learning libraries such as scikit-learn, LightGBM, XGBoost, etc. ONNX Runtime is compatible with different hardware, drivers, and operating systems, and provides optimal performance by leveraging hardware accelerators where applicable alongside graph optimizations and transforms. [Learn more →](https://www.onnxruntime.ai/docs/#onnx-runtime-for-inferencing)

**ONNX Runtime training** can accelerate the model training time on multi-node NVIDIA GPUs for transformer models with a one-line addition for existing PyTorch training scripts. [Learn more →](https://www.onnxruntime.ai/docs/#onnx-runtime-for-training)
## Status
>	**Input Required**: False

>	**Description**: The status of the solution component. There is a list of valid values that this conforms to.

>	**Valid Values**: DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED;  ACTIVE; DEPRECATED; OTHER

>	**Default Value**: ACTIVE


## Solution Component Type
>	**Input Required**: False

>	**Description**: Type of solution component.

>	**Alternative Labels**: Soln Component Type

AnalyticsEngine
## Planned Deployed Implementation Type
>	**Input Required**: False

>	**Description**: The planned implementation type for deployment.

>	**Alternative Labels**: Planned Deployed Impl Type

AnalyticsEngine
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

SolutionBlueprint::Initial-Data-Prep-Blueprint-for-ML-OPs::0.1
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

# Link External Reference
>	Link an external reference to a referenceable.

## Element Name
>	**Input Required**: True

>	**Description**: A referenceable to link.

>	**Alternative Labels**: Referenceable

SolutionComponent::ONNX::V1.0
## External Reference
>	**Input Required**: True

>	**Description**: The external reference to link to.

ExtRef::ONNX

## Label
>	**Input Required**: False

>	**Description**: Labels the link between the referenceable and the external reference.


## Description
>	**Input Required**: False

>	**Description**: A description of the link.

Documentation on ONNX.