"""
Lineage Linker Processors for Dr.Egeria v2.

Handles `Link <Type>`, `Update <Type>`, and `Unlink Lineage Relationship` --
the Lineage Linker OMVS's seven relationship types (DataFlow, ControlFlow,
ProcessCall, LineageMapping, DataMapping, UltimateSource,
UltimateDestination; see pyegeria's omvs/lineage_linker.py and
egeria-project.org/types/2/0223-Data-Flows-And-Control-Flows). Split
2026-09-16 into one dedicated Link/Update command pair per relationship type
(Link Data Flow, Update Data Flow, Link Control Flow, ...) rather than one
generic command with a "Lineage Relationship Type" selector attribute -- the
generic form let a user pick, say, DataFlow and then be offered every other
type's attributes too (Guard/Mandatory Guard, Query/Query ID/Query Type,
...), none of which apply. Each command's own `OM_TYPE` in the compact spec
now says which relationship type it builds, so LineageLinkProcessor /
UpdateLineageRelationshipProcessor read that instead of a user-supplied
selector -- one class per verb still handles all seven types, just routed by
command identity rather than by attribute value.

DataFlow is the one exception: the OMVS exposes a *separate* dedicated
endpoint for it (`link_data_flow` -> .../from-elements/.../via/.../
to-elements/.../attach, distinct from link_lineage's .../elements/.../.../
attach), so `_link()` below routes to it specifically when OM_TYPE ==
"DataFlow"; every other type goes through the generic `link_lineage`.

Unlike Link (which resolves its two element ends via the framework's
standard Reference Name attribute-resolution pass -- see the "guid" key
convention CurationLinkProcessor also relies on), Update/Unlink identify the
relationship itself directly by its own GUID (as returned by Link's output)
-- `update_lineage`/`detach_lineage` take that relationship GUID, not the
two element ends, so there's no element resolution involved for those two
commands. Unlink stays a single generic command (not split per type) since
detaching a relationship only needs its GUID -- no type-specific properties
are involved.

Full attribute set per type, confirmed against
open-metadata-framework/.../properties/lineage/*.java (the compact JSON's
prior attribute set was missing One Way/Integration Style/Protocol/
Frequency/Data Exchanged for every DataLineageRelationshipProperties
subtype, and Line Number for ProcessCall -- these are real fields on the
Java DTOs, just never wired into Dr.Egeria; the reused attribute
definitions -- One Way/Integration Style/Protocol/Frequency/Data Exchanged
-- come from Solution Architect's SolutionLinkingWire commands, which
already modeled the same DataLineageRelationshipProperties shape):
  DataFlow:             ISC Qualified Name, Label, Description, One Way,
                         Integration Style, Protocol, Frequency,
                         Data Exchanged, Formula, Formula Type
  ControlFlow:           ISC Qualified Name, Label, Description, Guard,
                         Mandatory Guard
  ProcessCall:           DataFlow's set + Line Number
  LineageMapping:        DataFlow's set minus Formula/Formula Type
  DataMapping:           ISC Qualified Name, Label, Description, Formula,
                         Formula Type, Query ID, Query, Query Type
  UltimateSource/
  UltimateDestination:   same as LineageMapping (LineageBoundaryProperties
                         also carries a system-computed `hops` map, not
                         exposed here -- not user-authored)
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
# type -- see lineage_linker.py's *Properties classes in pyegeria, and the
# Java DTO hierarchy in the module docstring above. Attributes not listed for
# a given type are simply omitted from the properties body even if somehow
# present (no error -- matches how Report's execution params handle
# attributes that don't apply to every report spec).
_DATA_LINEAGE_ATTRS = ["One Way", "Integration Style", "Protocol", "Frequency", "Data Exchanged"]

_TYPE_SPECIFIC_ATTRS = {
    "DataFlow": _DATA_LINEAGE_ATTRS + ["Formula", "Formula Type"],
    "ControlFlow": ["Guard", "Mandatory Guard"],
    "ProcessCall": _DATA_LINEAGE_ATTRS + ["Formula", "Formula Type", "Line Number"],
    "LineageMapping": _DATA_LINEAGE_ATTRS,
    "DataMapping": ["Formula", "Formula Type", "Query ID", "Query", "Query Type"],
    "UltimateSource": _DATA_LINEAGE_ATTRS,
    "UltimateDestination": _DATA_LINEAGE_ATTRS,
}

_ATTR_TO_PROPERTY = {
    "Formula": "formula",
    "Formula Type": "formulaType",
    "Guard": "guard",
    "Mandatory Guard": "mandatoryGuard",
    "Query ID": "queryId",
    "Query": "query",
    "Query Type": "queryType",
    "One Way": "oneWay",
    "Integration Style": "integrationStyle",
    "Protocol": "protocol",
    "Frequency": "frequency",
    "Data Exchanged": "dataExchanged",
    "Line Number": "lineNumber",
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
    """Processor for every `Link <Type>` AND `Unlink Lineage Relationship` command.

    One class handles both verbs -- not a design choice, a requirement: the
    compact-spec tooling's build_command_variants() treats every LINK_VERBS
    member (Link/Attach/Add/Detach/Unlink/Remove) as synonyms of the SAME
    underlying command for variant-registration purposes (see
    md_processing_constants._expand_command_phrase), so "Link Data Flow" and
    an "Unlink Data Flow" variant name would generate a variant set
    containing *each other's* exact name. Registering them to two different
    processor classes means whichever reg() call runs later silently wins
    the dispatcher slot for both. CurationLinkProcessor (curation.py) hits
    the same constraint and resolves it the same way -- branch on
    self.command.verb inside one class -- so this follows that established
    pattern rather than inventing a new one.
    """

    def supports_target_element_lookup(self) -> bool:
        # Relationship-only processor -- see
        # GovernanceLinkProcessor.supports_target_element_lookup (ISSUE-68
        # follow-up) for why this override matters.
        return False

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

            relationship_type = self.get_command_spec().get("OM_TYPE")
            if relationship_type not in _RELATIONSHIP_PROPERTIES_CLASS:
                raise ValueError(f"Command spec OM_TYPE must be one of {sorted(_RELATIONSHIP_PROPERTIES_CLASS)}.")

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
    """Processor for every `Update <Type>` command."""

    def supports_target_element_lookup(self) -> bool:
        # Relationship-only processor. Without this override,
        # AsyncBaseCommandProcessor.execute()'s step-5 Create<->Update
        # upsert-transition logic (as_is_element always None here + no
        # qualified_name to plan against) silently rewrites every "Update
        # <Type>" command to "Create <Type>" instead of calling
        # apply_changes() with verb="Update" -- confirmed live (ISSUE-68
        # follow-up) on the predecessor generic command; carried forward
        # into the per-type split unchanged.
        return False

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        relationship_guid = _v(attributes, "Lineage Relationship")
        if not relationship_guid:
            raise ValueError("Lineage Relationship (GUID) is required.")

        relationship_type = self.get_command_spec().get("OM_TYPE")
        if relationship_type not in _RELATIONSHIP_PROPERTIES_CLASS:
            raise ValueError(f"Command spec OM_TYPE must be one of {sorted(_RELATIONSHIP_PROPERTIES_CLASS)}.")

        properties = _build_relationship_properties(relationship_type, attributes)
        body = {"class": "UpdateRelationshipRequestBody", "properties": properties, "mergeUpdate": True}

        await self.client._async_update_lineage(relationship_guid, body)

        self.parsed_output["guid"] = relationship_guid
        logger.success(f"Updated {relationship_type} relationship {relationship_guid}")
        return await self.render_result_markdown(relationship_guid)
