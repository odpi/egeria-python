"""
Reference Data / Valid Values Link Processors for Dr.Egeria v2.

Handles the ValidValuesAssignment, ReferenceValueAssignment, and
SpecificationPropertyAssignment relationships across every family that
exposes a Link/Detach command for them (Glossary's "Link Question to Valid
Values", Data Designer's "Link Data Field to Valid Values", and Reference
Data's generic/annotation-oriented commands) -- one processor, dispatched by
OM_TYPE, mirroring CurationLinkProcessor's shape in md_processing/v2/curation.py.
"""
from typing import Any, Dict, Optional

from loguru import logger

from pyegeria import PyegeriaException
from md_processing.v2.processors import AsyncBaseCommandProcessor


def _v(attributes: dict, name: str, default=None):
    return attributes.get(name, {}).get("value", default)


def _guid(attributes: dict, name: str):
    return attributes.get(name, {}).get("guid")


def _audit_fields(attributes: dict) -> dict:
    return {
        "externalSourceGUID": attributes.get("External Source GUID", {}).get("guid"),
        "externalSourceName": _v(attributes, "External Source Name"),
        "effectiveTime": _v(attributes, "Effective Time"),
        "forLineage": _v(attributes, "For Lineage", False),
        "forDuplicateProcessing": _v(attributes, "For Duplicate Processing", False),
    }


# The three "subject"/consumer-side attributes used by the different Link
# commands that all resolve to a ValidValuesAssignment/ReferenceValueAssignment/
# SpecificationPropertyAssignment relationship -- "Term 1" (Glossary's Question
# flavor), "Linked Data Field 1" (Data Designer's Data Field flavor), "Element Id"
# (Reference Data's generic flavor).
_SUBJECT_ATTR_NAMES = ["Term 1", "Linked Data Field 1", "Element Id"]


def _subject_guid(attributes: dict) -> Optional[str]:
    for name in _SUBJECT_ATTR_NAMES:
        guid = _guid(attributes, name)
        if guid:
            return guid
    return None


class ReferenceDataLinkProcessor(AsyncBaseCommandProcessor):
    """Link/Detach commands for ValidValuesAssignment, ReferenceValueAssignment,
    and SpecificationPropertyAssignment (Glossary, Data Designer, and Reference
    Data families)."""

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    async def apply_changes(self) -> str:
        verb = self.command.verb
        object_type = self.canonical_object_type or self.command.object_type
        attributes = self.parsed_output.get("attributes", {})
        om_type = self.get_command_spec().get("OM_TYPE")
        is_link = verb in ("Link", "Attach", "Add")

        subject_guid = _subject_guid(attributes)
        if not subject_guid:
            raise PyegeriaException(
                f"{verb} {object_type}: could not resolve the subject element "
                f"(checked {', '.join(_SUBJECT_ATTR_NAMES)})"
            )

        client = self.client.reference_data

        if om_type == "ValidValuesAssignment":
            vv_guid = _guid(attributes, "Valid Value Set")
            if not vv_guid:
                raise PyegeriaException(f"{verb} {object_type}: 'Valid Value Set' is required")
            if is_link:
                props = {"class": "ValidValuesAssignmentProperties",
                         "strictRequirement": _v(attributes, "Strict Requirement")}
                body = {"class": "NewRelationshipRequestBody", "properties": props, **_audit_fields(attributes)}
                await client._async_link_valid_values_assignment(subject_guid, vv_guid, body)
            else:
                body = {"class": "DeleteRelationshipRequestBody", **_audit_fields(attributes)}
                await client._async_detach_valid_values_assignment(subject_guid, vv_guid, body)

        elif om_type == "ReferenceValueAssignment":
            vv_guid = _guid(attributes, "Reference Value")
            if not vv_guid:
                raise PyegeriaException(f"{verb} {object_type}: 'Reference Value' is required")
            if is_link:
                props = {"class": "ReferenceValueAssignmentProperties"}
                body = {"class": "NewRelationshipRequestBody", "properties": props, **_audit_fields(attributes)}
                await client._async_link_reference_value_assignment(subject_guid, vv_guid, body)
            else:
                body = {"class": "DeleteRelationshipRequestBody", **_audit_fields(attributes)}
                await client._async_detach_reference_value_assignment(subject_guid, vv_guid, body)

        elif om_type == "SpecificationPropertyAssignment":
            vv_guid = _guid(attributes, "Specification Property")
            if not vv_guid:
                raise PyegeriaException(f"{verb} {object_type}: 'Specification Property' is required")
            if is_link:
                props = {"class": "SpecificationPropertyAssignmentProperties",
                         "propertyName": _v(attributes, "Property Name")}
                body = {"class": "NewRelationshipRequestBody", "properties": props, **_audit_fields(attributes)}
                await self.client.valid_metadata._async_link_specification_property(subject_guid, vv_guid, body)
            else:
                body = {"class": "DeleteRelationshipRequestBody", **_audit_fields(attributes)}
                await self.client.valid_metadata._async_detach_specification_property(subject_guid, vv_guid, body)

        else:
            raise PyegeriaException(f"ReferenceDataLinkProcessor: unrecognized OM_TYPE '{om_type}' for {object_type}")

        logger.success(f"{verb} {object_type}: {subject_guid} <-> {om_type}")
        header = f"\n\n## {verb} {object_type}\n\nOperation completed.\n\n"
        return header


class ValidMetadataValueProcessor(AsyncBaseCommandProcessor):
    """Setup/Clear commands for the Valid Metadata Value registry (a type-system-level
    admin feature -- not to be confused with ValidValueDefinition elements), plus
    Set Consistent Metadata Values (Reference Data family)."""

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    async def apply_changes(self) -> str:
        verb = self.command.verb
        object_type = self.canonical_object_type or self.command.object_type
        attributes = self.parsed_output.get("attributes", {})
        display_name = attributes.get("Display Name", {}).get("value") or object_type
        client = self.client.valid_metadata

        if display_name == "Consistent Metadata Values" or "Consistent" in object_type:
            await client._async_set_consistent_metadata_values(
                _v(attributes, "Metadata Property Name"),
                _v(attributes, "Type Name"),
                _v(attributes, "Map Name"),
                _v(attributes, "Preferred Value"),
                _v(attributes, "Metadata Property Name 2"),
                _v(attributes, "Type Name 2"),
                _v(attributes, "Map Name 2"),
                _v(attributes, "Preferred Value 2"),
            )

        elif "Map Value" in object_type:
            property_name = _v(attributes, "Metadata Property Name")
            type_name = _v(attributes, "Type Name")
            map_name = _v(attributes, "Map Name")
            preferred_value = _v(attributes, "Preferred Value")
            if verb == "Setup":
                body = {
                    "displayName": _v(attributes, "Metadata Display Name"),
                    "description": _v(attributes, "Metadata Description"),
                    "preferredValue": preferred_value,
                }
                await client._async_setup_valid_metadata_map_value(property_name, map_name, type_name, body)
            else:
                await client._async_clear_valid_metadata_map_value(property_name, type_name, map_name, preferred_value)

        elif "Map Name" in object_type:
            property_name = _v(attributes, "Metadata Property Name")
            type_name = _v(attributes, "Type Name")
            if verb == "Setup":
                body = {
                    "displayName": _v(attributes, "Metadata Display Name"),
                    "description": _v(attributes, "Metadata Description"),
                    "preferredValue": _v(attributes, "Preferred Value"),
                }
                await client._async_setup_valid_metadata_map_name(property_name, type_name, body)
            else:
                await client._async_clear_valid_metadata_map_name(property_name, type_name, _v(attributes, "Preferred Value"))

        else:
            property_name = _v(attributes, "Metadata Property Name")
            type_name = _v(attributes, "Type Name")
            preferred_value = _v(attributes, "Preferred Value")
            if verb == "Setup":
                body = {
                    "displayName": _v(attributes, "Metadata Display Name"),
                    "description": _v(attributes, "Metadata Description"),
                    "preferredValue": preferred_value,
                }
                await client._async_setup_valid_metadata_value(property_name, type_name, body)
            else:
                await client._async_clear_valid_metadata_value(property_name, type_name, preferred_value)

        logger.success(f"{verb} {object_type}")
        return f"\n\n## {verb} {object_type}\n\nOperation completed.\n\n"
