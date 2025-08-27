"""

SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Pydantic Models representing common request and response bodies.

"""
from datetime import datetime
from enum import Enum, StrEnum
from typing import Literal, Annotated, Any, Optional, Dict

from pydantic import BaseModel, Field, ConfigDict, root_validator, model_validator


class MembershipStatus(StrEnum):
    """
    Represents the various statuses of membership in a system.

    This class is an enumeration that defines possible states related to the
    membership lifecycle. These statuses are typically used to denote the
    state of an item, resource, or entity within a system, and they assist
    in workflow management or status tracking.

    Attributes:
        UNKNOWN (MembershipStatus): Status indicating that the current
            state is not known.
        DISCOVERED (MembershipStatus): Status indicating that the entity
            has been identified or uncovered in some way.
        PROPOSED (MembershipStatus): Status indicating that the entity
            has been suggested or submitted for consideration.
        IMPORTED (MembershipStatus): Status indicating that the entity
            has been brought into a system or context from an external
            source.
        VALIDATED (MembershipStatus): Status indicating that the entity
            has been verified or approved.
        DEPRECATED (MembershipStatus): Status indicating that the entity
            is no longer recommended for use and may be phased out.
        OBSOLETE (MembershipStatus): Status indicating that the entity
            is no longer in use and is considered outdated.
        OTHER (MembershipStatus): Status indicating an additional,
            unspecified, or alternate state not covered by the predefined
            statuses.
    """
    UNKNOWN = "UNKNOWN"
    DISCOVERED = "DISCOVERED"
    PROPOSED = "PROPOSED"
    IMPORTED = "IMPORTED"
    VALIDATED = "VALIDATED"
    DEPRECATED = "DEPRECATED"
    OBSOLETE = "OBSOLETE"
    OTHER = "OTHER"


class ValidStatusValues(StrEnum):
    """
    Defines a set of valid status values to represent various states or life-cycle stages.

    This enumeration is designed to provide a standardized set of named constants for indicating
    statuses related to developmental, operational, or administrative processes. It can be used
    across different domains where such statuses are required. Each value corresponds to a specific
    state and is represented by a meaningful string.

    Attributes:
        UNKNOWN: Represents an unknown state where the specific status is not defined.
        DRAFT: Indicates that the item or process is in draft mode and not finalized.
        PREPARED: Denotes readiness but not yet officially deployed or used.
        PROPOSED: Represents a state where an idea or plan has been proposed but not yet approved.
        APPROVED: Indicates official approval has been granted for the item or process.
        REJECTED: Refers to a state where approval was denied.
        APPROVED_CONCEPT: Marks approval at a conceptual level, potentially requiring further work.
        UNDER_DEVELOPMENT: Represents an active development stage.
        DEVELOPMENT_COMPLETE: Indicates development has been finalized.
        APPROVED_FOR_DEPLOYMENT: Denotes readiness and approval for deployment.
        STANDBY: Represents a state where the item is ready but not active.
        ACTIVE: Denotes that the item or process is currently in operation.
        FAILED: Indicates that the item or process has failed.
        DISABLED: Represents a state where the item has been intentionally turned off or made inactive.
        COMPLETE: Indicates that the item or process has been successfully completed.
        DEPRECATED: Represents a state where the item is considered obsolete or no longer recommended.
        OTHER: Refers to any state that is not explicitly defined within the enumeration.
        DELETED: Indicates removal or deletion of the item.
    """
    UNKNOWN = "UNKNOWN"
    DRAFT = "DRAFT"
    PREPARED = "PREPARED"
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    APPROVED_CONCEPT = "APPROVED_CONCEPT"
    UNDER_DEVELOPMENT = "UNDER_DEVELOPMENT"
    DEVELOPMENT_COMPLETE = "DEVELOPMENT_COMPLETE"
    APPROVED_FOR_DEPLOYMENT = "APPROVED_FOR_DEPLOYMENT"
    STANDBY = "STANDBY"
    ACTIVE = "ACTIVE"
    FAILED = "FAILED"
    DISABLED = "DISABLED"
    COMPLETE = "COMPLETE"
    DEPRECATED = "DEPRECATED"
    OTHER = "OTHER"
    DELETED = "DELETED"


class SequencingOrder(StrEnum):
    """
    Defines different types of sequencing orders for data handling and processing.

    This enumeration represents various possible orders for sequencing data. It
    can be used to determine how a set of data should be sorted or processed
    based on the specified order. The specific orders include universal identifiers
    (GUID), creation metadata (recent or oldest), update metadata (recent or oldest),
    and property-based sorting (ascending or descending).

    Attributes:
        ANY (str): Represents any sequencing order, providing no specific sorting.
        GUID (str): Sorts based on globally unique identifiers.
        CREATION_DATE_RECENT (str): Sorts by most recent creation date first.
        CREATION_DATE_OLDEST (str): Sorts by oldest creation date first.
        LAST_UPDATE_RECENT (str): Sorts by the most recent update date first.
        LAST_UPDATE_OLDEST (str): Sorts by the oldest update date first.
        PROPERTY_ASCENDING (str): Sorts by properties in ascending order.
        PROPERTY_DESCENDING (str): Sorts by properties in descending order.
    """
    ANY = "ANY"
    GUID = "GUID"
    CREATION_DATE_RECENT = "CREATION_DATE_RECENT"
    CREATION_DATE_OLDEST = "CREATION_DATE_OLDEST"
    LAST_UPDATE_RECENT = "LAST_UPDATE_RECENT"
    LAST_UPDATE_OLDEST = "LAST_UPDATE_OLDEST"
    PROPERTY_ASCENDING = "PROPERTY_ASCENDING"
    PROPERTY_DESCENDING = "PROPERTY_DESCENDING"


class DeleteMethod(StrEnum):
    LOOK_FOR_LINEAGE        = "LOOK_FOR_LINEAGE"
    ARCHIVE                 = "ARCHIVE"
    SOFT_DELETE             = "SOFT_DELETE"
    PURGE                   = "PURGE"



# Define the camelCase conversion function
def to_camel_case(snake_str: str) -> str:
    """
    Converts a snake_case string to camelCase, with a special rule
    to keep 'guid' (case-insensitive) as 'GUID' (all uppercase).
    """
    components = snake_str.split('_')
    # Use a list comprehension to process each component
    # The first component remains as is (lowercase)
    # Subsequent components are capitalized, unless they are 'guid'
    camel_case_components = []
    for i, word in enumerate(components):
        if word.lower() == 'guid':
            camel_case_components.append('GUID')  # Special case: always uppercase GUID
        elif i == 0:
            camel_case_components.append(word)  # First word remains lowercase
        else:
            camel_case_components.append(word.capitalize())  # Subsequent words are capitalized
    return ''.join(camel_case_components)


class PyegeriaModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel_case,
        serialize_by_alias=True,
        use_enum_values=True,
        populate_by_name=True,  # Allow input by either field name or alias
        extra='ignore',  
        str_strip_whitespace=True
        )


class OpenMetadataRootProperties(PyegeriaModel):
    effective_from: datetime| None = None
    effective_to: datetime | None = None
    type_name: str | None = None
    extended_properties: dict | None = None

    @model_validator(mode='before')
    @classmethod
    def preprocess_data(cls, values):
        """
        This model validator performs pre-processing on the entire
        input dictionary before field validation.
        It converts any empty tuples to None and ensures a metadata key exists.

        This is the modern equivalent of @root_validator(pre=True).
        """
        # Ensure the 'data' key exists before trying to access it.
        if 'data' in values and isinstance(values['data'], dict):
            # Convert empty tuples to None
            processed_data = {}
            for key, value in values['data'].items():
                if isinstance(value, tuple) and not value:
                    processed_data[key] = None
                else:
                    processed_data[key] = value
            values['data'] = processed_data

        # Ensure a 'metadata' key is always a dictionary.
        if 'metadata' not in values:
            values['metadata'] = {}

        return values


class RelationshipBeanProperties(PyegeriaModel):
    effective_from: datetime | None = None
    effective_to: datetime | None = None
    type_name: str = None
    extended_properties: dict | None = None


class ClassificationBeanProperties(PyegeriaModel):
    effective_from: datetime | None = None
    effective_to: datetime | None = None
    type_name: str = None
    extended_properties: dict | None = None


class ReferenceableProperties(OpenMetadataRootProperties):
    class_: str| None =  Field(alias="class"),
    qualified_name: str
    display_name: str
    version_identifier: str | None = None
    description: str | None = None
    category: str | None = None
    additional_properties: dict | None = None


class RequestBody(PyegeriaModel):
    external_source_guid: str | None = None
    external_source_name: str | None = None
    effective_time: datetime | None = None
    governance_zone_filter: list[str] | None = None
    for_lineage: bool | None = False
    for_duplicate_processing: bool | None = False


class NewRelationshipRequestBody(RequestBody):
    class_: Annotated[Literal["NewRelationshipRequestBody"], Field(alias="class")]
    make_anchor: bool | None = False
    anchor_scope_guid: str | None = None
    properties: dict | RelationshipBeanProperties | None = None


class DeleteRequestBody(RequestBody):
    class_: Annotated[Literal["DeleteRequestBody"], Field(alias="class")]
    cascaded_delete: bool | None = False
    delete_method: DeleteMethod = DeleteMethod.LOOK_FOR_LINEAGE
    archive_date: datetime | None = None
    archive_process: str | None = None
    archive_properties: dict | None = None


class InitialClassifications(PyegeriaModel):
    class_: str = Field(alias="class"),
    other_props: Dict[str, Any] | None = None

    @model_validator(mode="before")
    @classmethod
    def capture_other_props(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        captured_props = data.copy()

        class_value = captured_props.pop("class", None)
        other_props_dict = captured_props if captured_props else None
        return {
            "class_": class_value,
            "other_props": other_props_dict
            }


class NewElementRequestBody(RequestBody):
    class_: Annotated[Literal["NewElementRequestBody"], Field(alias="class")]
    anchor_guid: str | None = None
    is_own_anchor: bool | None = True
    anchor_scope_guid: str | None = None
    initial_classifications:  Dict[str, InitialClassifications] | None = None
    initial_status: ValidStatusValues | str= ValidStatusValues.ACTIVE
    parent_guid: str | None = None
    parent_relationship_type_name: str | None = None
    parent_at_end_1: bool | None = True
    properties: dict | None = None


class NewClassificationRequestBody(RequestBody):
    class_: Annotated[Literal["NewClassificationRequestBody"], Field(alias="class")]
    properties: dict | None = None


class UpdateClassificationRequestBody(RequestBody):
    class_: Annotated[Literal["UpdateClassificationRequestBody"], Field(alias="class")]
    properties: dict | None = None
    merge_update: bool | None = True


class UpdateRelationshipRequestBody(RequestBody):
    class_: Annotated[Literal["UpdateRelationshipRequestBody"], Field(alias="class")]
    properties: dict | None = None
    merge_update: bool | None = True


class TemplateRequestBody(PyegeriaModel):
    class_: Annotated[Literal["TemplateRequestBody"], Field(alias="class")]
    anchor_guid: str | None = None
    is_own_anchor: bool | None = True
    anchor_scope_guid: str | None = None
    initial_classifications: dict | None = None  # unsure
    parent_guid: str | None = None
    parent_relationship_type_name: str | None = None
    parent_at_end_1: bool | None = True
    template_guid: str
    replacement_properties: dict[str, Any] = {}
    placeholder_properties: dict[str, Any] = {}
    deep_copy: bool | None = False
    effective_from: datetime | None = None
    effective_to: datetime | None = None
    template_substitute: bool | None = False
    allow_retrieve: bool | None = True


class UpdateElementRequestBody(PyegeriaModel):
    class_: Annotated[Literal["UpdateElementRequestBody"], Field(alias="class")]
    properties: dict[str, Any] = {}
    merge_update: bool | None = True
    external_source_guid: str | None = None
    external_source_name: str | None = None
    effective_time: datetime | None = None
    for_lineage: bool | None = False
    for_duplicate_processing: bool | None = False


class UpdateStatusRequestBody(PyegeriaModel):
    class_: Annotated[Literal["UpdateStatusRequestBody"], Field(alias="class")]
    new_status: str
    external_source_guid: str | None = None
    external_source_name: str | None = None
    effective_time: datetime | None = None
    for_lineage: bool | None = False
    for_duplicate_processing: bool | None = False


class GetRequestBody(PyegeriaModel):
    class_: Annotated[Literal["GetRequestBody"], Field(alias="class")]
    metadata_element_type_name: str | None = None
    metadata_element_subtype_names: list[str] | None = None
    skip_relationships: list[str] | None = None
    include_only_relationships: list[str] | None = None
    skip_classified_elements: list[str] | None = None
    include_only_classified_elements: list[str] | None = None
    graph_query_depth: int | None = None
    governance_zone_filter: list[str]  | None= None
    as_of_time: datetime | None = None
    effective_time: datetime | None = None
    for_lineage: bool | None = False
    for_duplicate_processing: bool | None = False
    relationship_page_size: int | None = None


class ResultsRequestBody(GetRequestBody):
    class_: Annotated[Literal["ResultsRequestBody"], Field(alias="class")]
    limit_results_by_status: list[ValidStatusValues] | None= None
    anchor_guid: str | None = None
    sequencing_order: SequencingOrder | None = None
    sequencing_property: str | None = None
    start_from: int = 0
    page_size: int = 0

class FilterRequestBody(ResultsRequestBody):
    class_: Annotated[Literal["FilterRequestBody"], Field(alias="class")]
    filter: str


class SearchStringRequestBody(ResultsRequestBody):
    class_: Annotated[Literal["SearchStringRequestBody"], Field(alias="class")]
    search_string: str | None = None
    starts_with: bool = True
    ends_with: bool = False
    ignore_case: bool = False



#######
# This gets only the fields in the most specific model
def get_defined_fields(model):
    return {
        field_name: field
        for field_name, field in model.__fields__.items()
        if field_name in model.__annotations__  # Only fields defined in the current model
    }

def get_defined_field_values(model_instance):
    # Extract the subset of the model's fields
    defined_fields = get_defined_fields(model_instance.__class__).keys()
    # Return only the defined fields with their values
    return {field: getattr(model_instance, field) for field in defined_fields}



#######

# --- Custom Base Model for JSON Key Conversion ---


# --- Innermost Models ---

class TypeInfo(PyegeriaModel):
    """Represents the 'type' subsection."""
    type_id: str
    type_name: str
    supertype__names: list[str] = None
    type_version: int
    type_description: str
    type_category: str

class OriginInfo(PyegeriaModel):
    """Represents the 'origin' subsection."""
    source_server: str
    origin_category: str
    home_metadata_collection_id: str
    home_metadata_collection_name: str
    license: list[str] = None # 'license' is optional in some origins

class VersionInfo(PyegeriaModel):
    """Represents the 'versions' subsection."""
    created_by: str
    updated_by: str
    create_time: datetime
    update_time: datetime
    version: int

class AnchorClassificationProperties(PyegeriaModel):
    """Represents 'classificationProperties' for Anchor."""
    anchortype__name: str
    anchor_domain_name: str
    anchor_scope_guid: list[str] = None # Varies between anchor and anchorScopeGUID
    anchor_guid: list[str] = None # Used in Glossary anchor

class SubjectAreaClassificationProperties(PyegeriaModel):
    """Represents 'classificationProperties' for SubjectArea."""
    display_name: list[str] = None
    subject_area_name: list[str] = None

class CanonicalVocabularyClassificationProperties(PyegeriaModel):
    """Represents 'classificationProperties' for CanonicalVocabulary."""
    scope: list[str] = None

# Using Any for classificationProperties due to varying schemas, or a Union if all types are known
class ElementClassification(PyegeriaModel):
    """Represents 'ElementClassification' (used for anchor, subjectArea, otherClassifications)."""
    class_: str = Field(alias="class") # Alias 'class' as it's a Python keyword
    header_version: int
    status: str
    type_: TypeInfo = Field(alias="type") # Alias 'type' as it's a Python keyword
    origin: OriginInfo
    versions: VersionInfo
    classification_origin: str
    classification_name: str
    # Use Any or a Union of specific property models if all types are known
    classification_properties: Optional[Any] = None

class CollectionProperties(PyegeriaModel):
    """Represents the 'properties' subsection for GlossaryCategory."""
    class_: str = Field(alias="class")
    type_name: str
    extended_properties: Optional[dict[str, Any]] = None
    qualified_name: str
    display_name: str
    description: list[str] = None

class GlossaryProperties(PyegeriaModel):
    """Represents the 'properties' subsection for Glossary."""
    display_name: str
    qualified_name: str
    usage: list[str] = None
    description: list[str] = None
    language: list[str] = None

# --- Intermediate Models ---

class ElementHeader(PyegeriaModel):
    """Represents the 'elementHeader' and 'relationshipHeader' subsections."""
    class_: str = Field(alias="class")
    header_version: int
    status: str
    type_: TypeInfo = Field(alias="type")
    origin: OriginInfo
    versions: VersionInfo
    guid: str
    anchor: Optional[ElementClassification] = None
    subject_area: Optional[ElementClassification] = Field(alias="subjectArea")
    otherclass_ifications: list[ElementClassification] = Field(alias="otherClassifications")

class RelatedElement(PyegeriaModel):
    """Represents the 'relatedElement' subsection."""
    element_header: ElementHeader = Field(alias="elementHeader")
    properties: GlossaryProperties

class AssociatedGlossaryItem(PyegeriaModel):
    """Represents an item within the 'associatedGlossaries' list."""
    relationship_header: ElementHeader = Field(alias="relationshipHeader")
    related_element: RelatedElement = Field(alias="relatedElement")
    related_element_at_end1: Optional[bool] = Field(alias="relatedElementAtEnd1")

# --- Root Model ---

class OpenMetadataRootElement(PyegeriaModel):
    """Represents the main object in the JSON array."""
    class_: str = Field(alias="class")
    element_header: ElementHeader = Field(alias="elementHeader")
    associated_glossaries: list[AssociatedGlossaryItem] = Field(alias="associatedGlossaries")
    mermaid_graph: list[str] = Field(alias="mermaidGraph")
    properties: CollectionProperties

# --- Overall Payload Type ---
# The entire JSON is a list of OpenMetadataRootElement
OpenMetadataPayload = list[OpenMetadataRootElement]
