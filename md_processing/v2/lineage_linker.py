"""
Lineage Linker Processor for Dr.Egeria v2.

Handles `Link Lineage Relationship`, `Update Lineage Relationship`, and
`Unlink Lineage Relationship` -- the Lineage Linker OMVS's seven relationship
types (DataFlow, ControlFlow, ProcessCall, LineageMapping, DataMapping,
UltimateSource, UltimateDestination; see pyegeria's
omvs/lineage_linker.py and egeria-project.org/types/2/0223-Data-Flows-And-
Control-Flows) modeled as ONE generic Link/Update/Unlink command triple with
a `Relationship Type` selector attribute, mirroring the OMVS client's own
generic `link_lineage(element_one, relationship_type_name, element_two,
body)` design -- rather than seven separate Link/Unlink command pairs, which
would just be fourteen thin wrappers around the same two endpoints.

DataFlow is the one exception: the OMVS exposes a *separate* dedicated
endpoint for it (`link_data_flow` -> .../from-elements/.../via/.../
to-elements/.../attach, distinct from link_lineage's .../elements/.../.../
attach), so `_link()` below routes to it specifically when Relationship Type
== "DataFlow"; every other type goes through the generic `link_lineage`.

Unlike Link (which resolves its two element ends via the framework's
standard Reference Name attribute-resolution pass -- see the "guid" key
convention CurationLinkProcessor also relies on), Update/Unlink identify the
relationship itself directly by its own GUID (as returned by Link's output)
-- `update_lineage`/`detach_lineage` take that relationship GUID, not the
two element ends, so there's no element resolution involved for those two
commands.
"""
from typing import Any, Dict, Optional

from loguru import logger

from md_processing.v2.processors import AsyncBaseCommandProcessor


def _v(attributes: Dict[str, Any], name: str, default=None):
    return attributes.get(name, {}).get("value", default)


def _guid(attributes: Dict[str, Any], name: str) -> Optional[str]:
    return attributes.get(name, {}).get("guid")


_RELATIONSHIP_PROPERTIES_CLASS = {
    "DataFlow": "DataFlowProperties",
    "ControlFlow": "ControlFlowProperties",
    "ProcessCall": "ProcessCallProperties",
    "LineageMapping": "LineageMappingProperties",
    "DataMapping": "DataMappingProperties",
    "UltimateSource": "UltimateSourceProperties",
    "UltimateDestination": "UltimateDestinationProperties",
}

# Which of the shared optional attributes actually apply to each relationship
# type -- see lineage_linker.py's *Properties classes in pyegeria. Attributes
# not listed for a given type are simply omitted from the properties body
# even if the user set them (no error -- matches how Report's execution
# params handle attributes that don't apply to every report spec).
_TYPE_SPECIFIC_ATTRS = {
    "DataFlow": ["Formula", "Formula Type"],
    "ControlFlow": ["Guard", "Mandatory Guard"],
    "ProcessCall": ["Formula", "Formula Type"],
    "LineageMapping": [],
    "DataMapping": ["Formula", "Formula Type", "Query ID", "Query", "Query Type"],
    "UltimateSource": [],
    "UltimateDestination": [],
}

_ATTR_TO_PROPERTY = {
    "Formula": "formula",
    "Formula Type": "formulaType",
    "Guard": "guard",
    "Mandatory Guard": "mandatoryGuard",
    "Query ID": "queryId",
    "Query": "query",
    "Query Type": "queryType",
}


def _build_relationship_properties(relationship_type: str, attributes: Dict[str, Any]) -> Dict[str, Any]:
    props: Dict[str, Any] = {
        "class": _RELATIONSHIP_PROPERTIES_CLASS[relationship_type],
        "iscQualifiedName": _v(attributes, "ISC Qualified Name"),
        "label": _v(attributes, "Label"),
        "description": _v(attributes, "Description"),
    }
    for attr_name in _TYPE_SPECIFIC_ATTRS[relationship_type]:
        value = _v(attributes, attr_name)
        if value is not None and value != "":
            props[_ATTR_TO_PROPERTY[attr_name]] = value
    return {k: v for k, v in props.items() if v is not None}


class LineageLinkProcessor(AsyncBaseCommandProcessor):
    """Processor for Link Lineage Relationship AND Unlink Lineage Relationship.

    One class handles both verbs -- not a design choice, a requirement: the
    compact-spec tooling's build_command_variants() treats every LINK_VERBS
    member (Link/Attach/Add/Detach/Unlink/Remove) as synonyms of the SAME
    underlying command for variant-registration purposes (see
    md_processing_constants._expand_command_phrase), so "Link Lineage
    Relationship" and "Unlink Lineage Relationship" both generate a variant
    set containing *each other's* exact name. Registering them to two
    different processor classes means whichever reg() call runs later
    silently wins the dispatcher slot for both. CurationLinkProcessor
    (curation.py) hits the same constraint and resolves it the same way --
    branch on self.command.verb inside one class -- so this follows that
    established pattern rather than inventing a new one.
    """

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        is_link = self.command.verb in ("Link", "Attach", "Add")

        if is_link:
            element_one_guid = _guid(attributes, "Element One")
            element_two_guid = _guid(attributes, "Element Two")
            if not element_one_guid or not element_two_guid:
                raise ValueError("Element One and Element Two must both resolve to existing elements.")

            relationship_type = _v(attributes, "Lineage Relationship Type")
            if relationship_type not in _RELATIONSHIP_PROPERTIES_CLASS:
                raise ValueError(f"Relationship Type must be one of {sorted(_RELATIONSHIP_PROPERTIES_CLASS)}.")

            properties = _build_relationship_properties(relationship_type, attributes)
            body = {"class": "NewRelationshipRequestBody", "properties": properties}

            if relationship_type == "DataFlow":
                guid = await self.client._async_link_data_flow(element_one_guid, relationship_type, element_two_guid, body)
            else:
                guid = await self.client._async_link_lineage(element_one_guid, relationship_type, element_two_guid, body)

            self.parsed_output["guid"] = guid
            logger.success(f"Linked {relationship_type} relationship with GUID {guid}")
            return await self.render_result_markdown(guid)

        # Unlink / Detach / Remove
        relationship_guid = _v(attributes, "Lineage Relationship")
        if not relationship_guid:
            raise ValueError("Lineage Relationship (GUID) is required.")

        # Explicit deleteMethod override required -- confirmed live 2026-08-17:
        # Egeria's deleteRelationshipInStore rejects its own server-side default
        # (LookForLineage, OMAG-COMMON-400-032) for relationship deletes, so an
        # explicit valid value must always be sent. SOFT_DELETE (Egeria's
        # DeleteMethod enum, not PURGE) so an accidental unlink stays
        # recoverable, consistent with the rest of this codebase's delete
        # conventions elsewhere (soft-delete by default, no hard-delete verb
        # exposed without an explicit cascade/purge opt-in).
        body = {"class": "DeleteRelationshipRequestBody", "deleteMethod": "SOFT_DELETE"}
        await self.client._async_detach_lineage(relationship_guid, body=body)

        self.parsed_output["guid"] = relationship_guid
        logger.success(f"Unlinked lineage relationship {relationship_guid}")
        return await self.render_result_markdown(relationship_guid)


class UpdateLineageRelationshipProcessor(AsyncBaseCommandProcessor):
    """Processor for Update Lineage Relationship."""

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        relationship_guid = _v(attributes, "Lineage Relationship")
        if not relationship_guid:
            raise ValueError("Lineage Relationship (GUID) is required.")

        relationship_type = _v(attributes, "Lineage Relationship Type")
        if relationship_type not in _RELATIONSHIP_PROPERTIES_CLASS:
            raise ValueError(f"Relationship Type must be one of {sorted(_RELATIONSHIP_PROPERTIES_CLASS)}.")

        properties = _build_relationship_properties(relationship_type, attributes)
        body = {"class": "UpdateRelationshipRequestBody", "properties": properties, "mergeUpdate": True}

        await self.client._async_update_lineage(relationship_guid, body)

        self.parsed_output["guid"] = relationship_guid
        logger.success(f"Updated lineage relationship {relationship_guid}")
        return await self.render_result_markdown(relationship_guid)
