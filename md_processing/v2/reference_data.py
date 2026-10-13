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
from pyegeria.core.utils import body_slimmer
from md_processing.v2.processors import AsyncBaseCommandProcessor
from md_processing.md_processing_utils.common_md_utils import (
    async_add_note_in_dr_e,
    set_create_body,
    set_delete_rel_request_body,
    set_element_prop_body,
    set_rel_request_body,
    set_update_body,
    update_element_dictionary,
)


def _v(attributes: dict, name: str, default=None):
    return attributes.get(name, {}).get("value", default)


def _guid(attributes: dict, name: str):
    return attributes.get(name, {}).get("guid")


def _bool(value, default: Optional[bool] = None) -> Optional[bool]:
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "yes", "1", "on", "y"}


def _int(value, default: Optional[int] = None) -> Optional[int]:
    if value is None or value == "":
        return default
    try:
        return int(str(value).strip())
    except ValueError:
        return default


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
                         "strictRequirement": _bool(_v(attributes, "Strict Requirement"), default=True)}
                body = body_slimmer({"class": "NewRelationshipRequestBody", "properties": props,
                                     **_audit_fields(attributes)})
                await client._async_link_valid_values_assignment(subject_guid, vv_guid, body)
            else:
                body = {"class": "DeleteRelationshipRequestBody", **_audit_fields(attributes)}
                await client._async_detach_valid_values_assignment(subject_guid, vv_guid, body)

        elif om_type == "ReferenceValueAssignment":
            vv_guid = _guid(attributes, "Reference Value")
            if not vv_guid:
                raise PyegeriaException(f"{verb} {object_type}: 'Reference Value' is required")
            if is_link:
                props = {"class": "ReferenceValueAssignmentProperties",
                         "attributeName": _v(attributes, "Attribute Name"),
                         "confidence": _int(_v(attributes, "Confidence")),
                         "steward": _v(attributes, "Steward"),
                         "stewardTypeName": _v(attributes, "Steward Type Name"),
                         "stewardPropertyName": _v(attributes, "Steward Property Name"),
                         "notes": _v(attributes, "Notes")}
                body = body_slimmer({"class": "NewRelationshipRequestBody", "properties": props,
                                     **_audit_fields(attributes)})
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
            rows = _v(attributes, "Metadata Value Table") or []
            if verb == "Setup" and rows:
                done = []
                for row in rows:
                    cols = {str(k).strip().lower(): v for k, v in row.items()}
                    value = cols.get("preferred value") or cols.get("value")
                    if not value:
                        self._add_warning(f"Metadata Value Table row skipped -- no Preferred Value: {row}")
                        continue
                    body = {"displayName": cols.get("display name") or value,
                            "description": cols.get("description"),
                            "preferredValue": value}
                    await client._async_setup_valid_metadata_value(property_name, type_name, body)
                    done.append(value)
                self.add_related_result("Valid Metadata Values", message=f"Set up {len(done)}: {', '.join(done)}")
            elif verb == "Setup":
                if not preferred_value:
                    raise PyegeriaException(f"{verb} {object_type}: give a Preferred Value or a Metadata Value Table")
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


# ── Reference data authoring ─────────────────────────────────────────────────
# Sets and values are ReferenceDataSet / ReferenceDataValue elements, matching
# Egeria's own content (e.g. ReferenceDataSet::ContactType). The Reference Data
# view's finds default to ReferenceDataValue, so a plain ValidValueDefinition
# would be invisible to them -- these commands never create one.

_LINK_VERBS = ("Link", "Attach", "Add")
_DETACH_VERBS = ("Detach", "Unlink", "Remove")

# Value Table columns understood, lower-cased.
_VALUE_TABLE_COLUMNS = {"value", "preferred value", "display name", "description", "usage", "data type",
                        "is case sensitive", "default", "ordinal"}


def _valid_value_props(attributes: dict) -> dict:
    return {
        "preferredValue": _v(attributes, "Preferred Value"),
        "dataType": _v(attributes, "Data Type"),
        "usage": _v(attributes, "Usage"),
        "scope": _v(attributes, "Scope"),
        "namespacePath": _v(attributes, "Namespace Path"),
        "isCaseSensitive": _bool(_v(attributes, "Is Case Sensitive")),
        "ordinal": _int(_v(attributes, "Ordinal")),
    }


def _member_body(attributes: dict, is_default: Optional[bool], ordinal: Optional[int]) -> dict:
    return body_slimmer({
        **set_rel_request_body("ValidValueMember", attributes),
        "properties": {"class": "ValidValueMemberProperties",
                       "isDefaultValue": bool(is_default), "ordinal": ordinal or 0},
    })


class ReferenceDataElementProcessor(AsyncBaseCommandProcessor):
    """Create/Update Reference Data Set and Reference Data Value.

    A set's members come from three attributes, combined in this order:
    Members (existing values), Values (one per line, created inline) and
    Value Table (created or updated inline with their own properties). When
    any of them is given, the set's membership is made to match: listed values
    are linked (re-linking updates isDefaultValue/ordinal in place) and members
    no longer listed are unlinked -- never deleted, since other sets or fields
    may use them. Inline values are named <set qualified name>::<value>, so a
    re-run finds and updates them instead of creating duplicates.
    """

    async def apply_changes(self) -> str:
        verb = self.command.verb
        object_type = getattr(self, "canonical_object_type", None) or self.command.object_type
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        display_name = _v(attributes, "Display Name", qualified_name)
        merge_update = _v(attributes, "Merge Update", True)
        journal_entry = _v(attributes, "Journal Entry")
        client = self.client.reference_data

        props = set_element_prop_body(object_type, qualified_name, attributes)
        props.update(_valid_value_props(attributes))

        if verb == "Update":
            guid = self.parsed_output.get("guid") or (
                self.as_is_element["elementHeader"]["guid"] if self.as_is_element else None)
            if not guid:
                return self.command.raw_block
            body = set_update_body(object_type, attributes)
            body["mergeUpdate"] = merge_update
            body["properties"] = self.filter_update_properties(props, merge_update)
            self.last_body = body = body_slimmer(body)
            await client._async_update_valid_value_definition(guid, body)
            known_new = False
        elif verb == "Create":
            body = set_create_body(object_type, attributes)
            body["properties"] = props
            self.last_body = body = body_slimmer(body)
            guid = self.extract_guid_or_raise(await client._async_create_valid_value_definition(body),
                                              f"Create {object_type}")
            known_new = True
        else:
            return self.command.raw_block

        self.parsed_output["guid"] = guid
        update_element_dictionary(qualified_name, {"guid": guid, "display_name": display_name})

        if props["class"] == "ReferenceDataSetProperties":
            await self._sync_set_members(guid, qualified_name, attributes, known_new)
        else:
            set_guid = _guid(attributes, "In Reference Data Set")
            if set_guid:
                await client._async_link_valid_value_member(
                    set_guid, guid, _member_body(attributes, _bool(_v(attributes, "Is Default Member")),
                                                 _int(_v(attributes, "Member Ordinal"))))
                self.add_related_result("Reference Data Set Membership", set_guid)

        if journal_entry:
            try:
                j_guid = await async_add_note_in_dr_e(self.client, qualified_name, display_name, journal_entry)
                if j_guid:
                    self.add_related_result("Journal Entry", j_guid)
            except Exception as e:  # noqa: BLE001
                self.add_related_result("Journal Entry", status="failure", message=str(e))

        logger.success(f"{verb}d {object_type} '{display_name}' with GUID {guid}")
        return await self.render_result_markdown(guid)

    async def _sync_set_members(self, set_guid: str, set_qn: str, attributes: dict, known_new: bool) -> None:
        member_attrs = ("Members", "Values", "Value Table")
        if not any(attributes.get(a, {}).get("value") for a in member_attrs):
            return
        default_member = _v(attributes, "Default Member")
        planned: Dict[str, tuple] = {}  # member guid -> (isDefaultValue, ordinal)
        position = 0

        members = attributes.get("Members", {})
        names = members.get("value") or []
        guids = members.get("guid_list") or ([members["guid"]] if members.get("guid") else [])
        if isinstance(names, str):
            names = [names]
        aligned = len(names) == len(guids)
        for i, g in enumerate(guids):
            position += 1
            planned[g] = (bool(default_member) and aligned and names[i] == default_member, position)

        for value in _v(attributes, "Values") or []:
            position += 1
            g = await self._upsert_value(set_qn, {"value": value}, attributes)
            planned[g] = (value == default_member, position)

        for row in _v(attributes, "Value Table") or []:
            cols = {str(k).strip().lower(): v for k, v in row.items()}
            unknown = set(cols) - _VALUE_TABLE_COLUMNS
            if unknown:
                self._add_warning(f"Value Table: unknown column(s) ignored: {', '.join(sorted(unknown))}")
            value = cols.get("value") or cols.get("preferred value")
            if not value:
                self._add_warning(f"Value Table row skipped -- no Value: {row}")
                continue
            position += 1
            g = await self._upsert_value(set_qn, cols | {"value": value}, attributes)
            planned[g] = (_bool(cols.get("default"), default=False) or value == default_member,
                          _int(cols.get("ordinal"), default=position))

        current = {} if known_new else await self._current_members(set_guid)
        client = self.client.reference_data
        linked, unlinked = [], []
        for g, (is_default, ordinal) in planned.items():
            if current.get(g) != (bool(is_default), ordinal or 0):
                await client._async_link_valid_value_member(set_guid, g, _member_body(attributes, is_default, ordinal))
                linked.append(g)
        for g in set(current) - set(planned):
            await client._async_detach_valid_value_member(
                set_guid, g, body_slimmer(set_delete_rel_request_body("ValidValueMember", attributes)))
            unlinked.append(g)
        self.add_related_result("Reference Data Set Members",
                                message=f"{len(planned)} listed; linked or updated {len(linked)}, "
                                        f"unlinked {len(unlinked)}")

    async def _upsert_value(self, set_qn: str, cols: dict, attributes: dict) -> str:
        value = str(cols["value"]).strip()
        qn = f"{set_qn}::{value}"
        props = body_slimmer({
            "class": "ReferenceDataValueProperties",
            "typeName": "ReferenceDataValue",
            "qualifiedName": qn,
            "displayName": cols.get("display name") or value,
            "preferredValue": value,
            "description": cols.get("description"),
            "usage": cols.get("usage"),
            "dataType": cols.get("data type"),
            "isCaseSensitive": _bool(cols.get("is case sensitive")),
        })
        client = self.client.reference_data
        existing = await self.resolve_element_guid(qn, tech_type="ReferenceDataValue")
        if existing and not str(existing).startswith("(Planned"):
            await client._async_update_valid_value_definition(existing, body_slimmer({
                **set_update_body("Reference Data Value", attributes), "mergeUpdate": True, "properties": props}))
            guid = existing
        else:
            body = set_create_body("Reference Data Value", attributes)
            body["properties"] = props
            guid = self.extract_guid_or_raise(await client._async_create_valid_value_definition(body_slimmer(body)),
                                              f"Create Reference Data Value {value}")
        update_element_dictionary(qn, {"guid": guid, "display_name": props["displayName"]})
        return guid

    async def _current_members(self, set_guid: str) -> Dict[str, tuple]:
        result = await self.client._async_get_related_metadata_elements(
            set_guid, "ValidValueMember", {"class": "ResultsRequestBody"}, starting_at_end=1, page_size=1000)
        items = result.get("elementList", []) if isinstance(result, dict) else (
            result if isinstance(result, list) else [])
        current = {}
        for item in items:
            guid = (item.get("element") or {}).get("elementGUID")
            if not guid:
                continue
            p = (item.get("relationshipProperties") or {}).get("propertiesAsStrings") or {}
            current[guid] = (_bool(p.get("isDefaultValue"), default=False), _int(p.get("ordinal"), default=0))
        return current


def _member_link_props(attributes: dict) -> dict:
    return {"isDefaultValue": bool(_bool(_v(attributes, "Is Default Member"), default=False)),
            "ordinal": _int(_v(attributes, "Member Ordinal"), default=0)}


def _no_props(attributes: dict) -> dict:
    return {}


def _association_props(attributes: dict) -> dict:
    return {"associationName": _v(attributes, "Association Name"),
            "associationType": _v(attributes, "Association Type"),
            "additionalProperties": _v(attributes, "Additional Properties")}


def _mapping_props(attributes: dict) -> dict:
    return {"associationDescription": _v(attributes, "Association Description"),
            "confidence": _int(_v(attributes, "Confidence")),
            "steward": _v(attributes, "Steward"),
            "stewardTypeName": _v(attributes, "Steward Type Name"),
            "stewardPropertyName": _v(attributes, "Steward Property Name"),
            "notes": _v(attributes, "Notes")}


def _implementation_props(attributes: dict) -> dict:
    return {"symbolicName": _v(attributes, "Symbolic Name"),
            "implementationValue": _v(attributes, "Implementation Value"),
            "additionalValues": _v(attributes, "Additional Values")}


# OM_TYPE -> (end1 attribute, end2 attribute, link method, detach method, relationship properties builder).
# Each ReferenceDataManager method takes (end1_guid, end2_guid, body).
VALID_VALUE_LINKS: Dict[str, tuple] = {
    "ValidValueMember": ("Valid Value Set", "Member Value",
                         "_async_link_valid_value_member", "_async_detach_valid_value_member", _member_link_props),
    "ConsistentValidValues": ("Valid Value 1", "Valid Value 2",
                              "_async_link_consistent_valid_values", "_async_detach_consistent_valid_values",
                              _no_props),
    "ValidValueAssociation": ("Valid Value 1", "Valid Value 2",
                              "_async_link_associated_valid_values", "_async_detach_associated_valid_values",
                              _association_props),
    "ValidValuesMapping": ("Valid Value 1", "Valid Value 2",
                           "_async_link_mapped_valid_values", "_async_detach_mapped_valid_values", _mapping_props),
    "ValidValuesImplementation": ("Valid Value", "Implementation Element",
                                  "_async_link_valid_value_implementation",
                                  "_async_detach_valid_value_implementation", _implementation_props),
}


class ValidValueLinkProcessor(AsyncBaseCommandProcessor):
    """Link/Detach for the relationships between valid values (member, consistent,
    associated, mapped) and from a valid value to its implementation, driven by
    the command's OM_TYPE through VALID_VALUE_LINKS. Branches on the verb, since
    registering "Link X" also routes "Detach X" here."""

    def supports_target_element_lookup(self) -> bool:
        return False

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    async def apply_changes(self) -> str:
        verb = self.command.verb
        object_type = getattr(self, "canonical_object_type", None) or self.command.object_type
        attributes = self.parsed_output["attributes"]
        om_type = (self.get_command_spec() or {}).get("OM_TYPE")
        link_spec = VALID_VALUE_LINKS.get(om_type)
        if not link_spec:
            raise PyegeriaException(f"No valid value relationship mapping for OM_TYPE '{om_type}' ({object_type})")
        end1_attr, end2_attr, link_method, detach_method, props_fn = link_spec

        end1_guid, end2_guid = _guid(attributes, end1_attr), _guid(attributes, end2_attr)
        if not (end1_guid and end2_guid):
            missing = [f"'{a}'" for a, g in ((end1_attr, end1_guid), (end2_attr, end2_guid)) if not g]
            raise ValueError(f"Cannot {verb.lower()} {object_type}: resolution failed for {', '.join(missing)}")

        client = self.client.reference_data
        if verb in _DETACH_VERBS:
            self.last_body = body = body_slimmer(set_delete_rel_request_body(om_type, attributes))
            await getattr(client, detach_method)(end1_guid, end2_guid, body)
            logger.success(f"Detached {om_type} between {end1_guid} and {end2_guid}")
            return (f"\n\n## {verb} {object_type}\n\n"
                    f"Detached the {om_type} relationship between {end1_guid} and {end2_guid}")
        if verb not in _LINK_VERBS:
            return self.command.raw_block

        body = set_rel_request_body(om_type, attributes)
        body["properties"] = {"class": f"{om_type}Properties", **props_fn(attributes)}
        self.last_body = body = body_slimmer(body)
        await getattr(client, link_method)(end1_guid, end2_guid, body)
        logger.success(f"Linked {end1_guid} to {end2_guid} with {om_type}")
        return f"\n\n## {verb} {object_type}\n\nLinked {end1_guid} to {end2_guid} ({om_type})"

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        return None
