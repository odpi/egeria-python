"""
Pydantic models representing collection-related JSON structures from Egeria.

These models represent a subset of the JSON payload structure found in the Egeria API responses,
focusing on collections and their related components.
"""

from datetime import datetime
from typing import List, Dict, Optional, Any, Literal

from pydantic import BaseModel, Field

from pyegeria.models import PyegeriaModel


# --- Basic Type Models ---

class TypeInfo(PyegeriaModel):
    """Represents type information for an element."""
    type_id: str
    type_name: str
    super_type_names: Optional[List[str]] = None
    type_version: int
    type_description: str
    type_category: str


class OriginInfo(PyegeriaModel):
    """Represents origin information for an element."""
    source_server: str
    origin_category: str
    home_metadata_collection_id: str
    home_metadata_collection_name: str
    license: Optional[str] = None


class VersionInfo(PyegeriaModel):
    """Represents version information for an element."""
    created_by: str
    updated_by: str
    create_time: datetime
    update_time: datetime
    version: int


# --- Classification Models ---

class ClassificationProperties(PyegeriaModel):
    """Base model for classification properties."""
    pass


class AnchorClassificationProperties(ClassificationProperties):
    """Properties for Anchors classification."""
    anchor_type_name: str
    anchor_domain_name: str
    anchor_guid: Optional[str] = None
    anchor_scope_guid: Optional[str] = None


class SubjectAreaClassificationProperties(ClassificationProperties):
    """Properties for SubjectArea classification."""
    display_name: Optional[str] = None
    subject_area_name: Optional[str] = None


class CanonicalVocabularyClassificationProperties(ClassificationProperties):
    """Properties for CanonicalVocabulary classification."""
    scope: str


class ConnectorTypeDirectoryClassificationProperties(ClassificationProperties):
    """Properties for ConnectorTypeDirectory classification."""
    pass


class ElementClassification(PyegeriaModel):
    """Represents a classification applied to an element."""
    class_: str = Field(alias="class")
    header_version: int
    status: str
    type_: TypeInfo = Field(alias="type")
    origin: OriginInfo
    versions: VersionInfo
    classification_origin: str
    classification_name: str
    classification_properties: Optional[Dict[str, Any]] = None


# --- Properties Models ---

class CollectionProperties(PyegeriaModel):
    """Represents the properties of a Collection."""
    class_: str = Field(alias="class")
    type_name: str
    extended_properties: Optional[Dict[str, Any]] = {}
    qualified_name: str
    display_name: str
    description: Optional[str] = None


class GlossaryProperties(PyegeriaModel):
    """Represents the properties of a Glossary."""
    display_name: str
    qualified_name: str
    usage: Optional[List[str]] = None
    description: Optional[List[str]] = None
    language: Optional[List[str]] = None


# --- Header Models ---

class ElementHeader(PyegeriaModel):
    """Represents the header information for an element."""
    class_: str = Field(alias="class")
    header_version: int
    status: str
    type_: TypeInfo = Field(alias="type")
    origin: OriginInfo
    versions: VersionInfo
    guid: str
    anchor: Optional[ElementClassification] = None
    subject_area: Optional[ElementClassification] = Field(None, alias="subjectArea")
    other_classifications: Optional[List[ElementClassification]] = Field([], alias="otherClassifications")
    collection_categories: Optional[List[ElementClassification]] = Field(None, alias="collectionCategories")


# --- Relationship Models ---

class RelationshipHeader(ElementHeader):
    """Represents the header information for a relationship."""
    pass


class RelatedElement(PyegeriaModel):
    """Represents a related element in a relationship."""
    element_header: ElementHeader = Field(alias="elementHeader")
    properties: GlossaryProperties


class AssociatedGlossaryItem(PyegeriaModel):
    """Represents an associated glossary item."""
    relationship_header: RelationshipHeader = Field(alias="relationshipHeader")
    related_element: RelatedElement = Field(alias="relatedElement")
    related_element_at_end1: Optional[bool] = Field(None, alias="relatedElementAtEnd1")


class CollectionMember(PyegeriaModel):
    """Represents a member of a collection."""
    relationship_header: RelationshipHeader = Field(alias="relationshipHeader")
    related_element: RelatedElement = Field(alias="relatedElement")
    related_element_at_end1: Optional[bool] = Field(None, alias="relatedElementAtEnd1")


# --- Root Models ---

class OpenMetadataRootElement(PyegeriaModel):
    """Represents the root element in the JSON payload."""
    class_: str = Field(alias="class")
    element_header: ElementHeader = Field(alias="elementHeader")
    associated_glossaries: Optional[List[AssociatedGlossaryItem]] = Field(None, alias="associatedGlossaries")
    collection_members: Optional[List[CollectionMember]] = Field(None, alias="collectionMembers")
    mermaid_graph: Optional[str] = Field(None, alias="mermaidGraph")
    properties: CollectionProperties


# --- Overall Payload Type ---
CollectionPayload = List[OpenMetadataRootElement]