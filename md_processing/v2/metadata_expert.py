"""
MetadataExpert processors for Dr.Egeria v2 (Advanced commands only).

Maintenance of Egeria's open metadata *type system* plus two raw metadata-element operations, all backed
by ``pyegeria/omvs/metadata_expert.py``:

- Create Type Def  -> add_type_def (entity, relationship or classification definition)
- Update Type Def  -> update_type_def   (Egeria rejects every patch today: ISSUE-124)
- Delete Type Def  -> delete_type_def
- Create Enum Def  -> add_enum_def
- Delete Enum Def  -> delete_enum_def   (Egeria returns a 500: ISSUE-125; enums cannot be removed)
- Count Metadata Elements   -> count_metadata_elements
- Publish Metadata Element  -> publish_metadata_element
- Create/Update/Delete Instance      -> create/update_metadata_element_properties/delete_metadata_element
- Link/Unlink Instances, Update Relationship -> create/delete/update_related_elements*
- Classify/Reclassify/Declassify Instance    -> classify/reclassify/declassify_metadata_element

Instance, relationship and classification properties are sent as typed property maps
(EntityElementProperties / RelationshipElementProperties / ClassificationElementProperties with a
propertyValueMap of PrimitiveTypePropertyValue), the shape shown in the SDK docstrings. NOT verified
against a live server (Egeria was read-only when these were written).

Like the Automation family these are actions, not create-or-update of a named element: no as-is lookup
and no Create<->Update rewrite.
"""
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from loguru import logger

from pyegeria import PyegeriaException
from md_processing.v2.processors import AsyncBaseCommandProcessor

PRIMITIVE_TYPES = {"string", "int", "long", "boolean", "date", "float", "double", "short", "byte", "char",
                   "bigint", "bigdecimal", "object"}
_CATEGORY_CLASS = {"entity": "OpenMetadataEntityDef", "relationship": "OpenMetadataRelationshipDef",
                   "classification": "OpenMetadataClassificationDef"}


def _v(attributes: Dict[str, Any], name: str, default=None):
    value = attributes.get(name, {}).get("value", default)
    return default if value in (None, "") else value


def _names(value: Any) -> List[str]:
    """A list-ish string (newline, comma or bullet separated) or list -> clean names."""
    if value is None:
        return []
    items = value if isinstance(value, list) else re.split(r"[\n,]", str(value))
    return [str(i).strip().lstrip("-*• ").strip() for i in items if str(i).strip().lstrip("-*• ").strip()]


def _bool(value: Any) -> Optional[bool]:
    if isinstance(value, bool) or value is None:
        return value
    text = str(value).strip().lower()
    return True if text in ("true", "yes", "y", "1") else False if text in ("false", "no", "n", "0") else None


def confirm_name(attributes: Dict[str, Any], name_attr: str, confirm_attr: str, what: str) -> str:
    """Platform-wide type system changes are refused unless the confirmation repeats the name exactly
    (case-sensitive, surrounding spaces ignored). Called before anything is sent to Egeria."""
    name = str(_v(attributes, name_attr, "")).strip()
    if not name:
        raise PyegeriaException(f"{name_attr} is required.")
    if str(_v(attributes, confirm_attr, "")).strip() != name:
        raise PyegeriaException(
            f"{what} changes the type system for every user and app on this platform. Repeat the name ({name}) "
            f"in {confirm_attr} to proceed; nothing was changed.")
    return name


# (name attribute, confirmation attribute) for the commands that change the type system
CONFIRMATIONS = (("Type Def Name", "Confirm Type Def Name"), ("Enum Def Name", "Confirm Enum Def Name"))


def _link(name: str) -> Dict[str, str]:
    return {"name": name}


def _attribute_type(type_name: str) -> Dict[str, str]:
    cls = "OpenMetadataPrimitiveDef" if type_name.lower() in PRIMITIVE_TYPES else "OpenMetadataEnumDef"
    return {"class": cls, "name": type_name}


def attribute_definitions(attributes: Dict[str, Any]) -> List[Dict[str, Any]]:
    """'Type Def Attributes' Dictionary (attributeName: typeName) -> attributeDefinitions."""
    return [{"attributeName": str(name), "attributeType": _attribute_type(str(type_name).strip())}
            for name, type_name in (_v(attributes, "Type Def Attributes") or {}).items()]


def type_def_body(attributes: Dict[str, Any]) -> Dict[str, Any]:
    category = str(_v(attributes, "Type Def Category", "Entity")).strip().lower()
    if category not in _CATEGORY_CLASS:
        raise PyegeriaException(f"Type Def Category must be Entity, Relationship or Classification, not '{category}'.")
    body: Dict[str, Any] = {"class": _CATEGORY_CLASS[category], "name": _v(attributes, "Type Def Name")}
    if _v(attributes, "Type Def Description"):
        body["description"] = _v(attributes, "Type Def Description")
    if _v(attributes, "Super Type"):
        body["superType"] = _link(_v(attributes, "Super Type"))
    if attribute_definitions(attributes):
        body["attributeDefinitions"] = attribute_definitions(attributes)
    if category == "classification":
        valid = _names(_v(attributes, "Valid Entity Types"))
        if valid:
            body["validEntityDefs"] = [_link(n) for n in valid]
        if _bool(_v(attributes, "Propagatable")) is not None:
            body["propagatable"] = _bool(_v(attributes, "Propagatable"))
    elif category == "relationship":
        # Literal attribute names (not f-strings) so the attribute-consumption audit can see them.
        for key, entity_attr, name_attr in (("endDef1", "End1 Entity Type", "End1 Attribute Name"),
                                            ("endDef2", "End2 Entity Type", "End2 Attribute Name")):
            entity, attr_name = _v(attributes, entity_attr), _v(attributes, name_attr)
            if not entity or not attr_name:
                raise PyegeriaException(f"A relationship definition needs {entity_attr} and {name_attr}.")
            body[key] = {"entityType": _link(entity), "attributeName": attr_name}
    return body


def enum_def_body(attributes: Dict[str, Any]) -> Dict[str, Any]:
    values = _v(attributes, "Enum Values") or {}
    if not values:
        raise PyegeriaException("Enum Values is required: one 'value: description' per line.")
    elements = [{"ordinal": i, "value": str(value), "description": str(description or "")}
                for i, (value, description) in enumerate(values.items())]
    default = _v(attributes, "Enum Default Value") or elements[0]["value"]
    matches = [e for e in elements if e["value"] == default]
    if not matches:
        raise PyegeriaException(f"Enum Default Value '{default}' is not one of the Enum Values.")
    body: Dict[str, Any] = {"class": "OpenMetadataEnumDef", "name": _v(attributes, "Enum Def Name"),
                            "elementDefs": elements, "defaultValue": matches[0]}
    if _v(attributes, "Enum Def Description"):
        body["description"] = _v(attributes, "Enum Def Description")
    return body


class MetadataExpertProcessor(AsyncBaseCommandProcessor):
    """Shared behaviour: actions with no as-is element and no upsert rewrite."""

    def supports_target_element_lookup(self) -> bool:
        return False

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    @property
    def expert(self):
        return self.client.metadata_expert

    def spec_flag(self, name: str, default: Any = None) -> Any:
        """A command-level flag from the compact spec (idempotent, chat_allowed)."""
        return (self.get_command_spec() or {}).get(name, default)

    async def validate_only(self) -> str:
        report = await super().validate_only()
        notes = []
        if self.spec_flag("idempotent", True) is False:
            notes.append("This command is **not idempotent**: it acts on Egeria every time it runs, so running the "
                         "document again repeats it (Create Instance and Link Instances make a new element or "
                         "relationship each time). Do not put it in a re-run or heal batch.")
        if self.spec_flag("chat_allowed", True) is False:
            notes.append("Advanced command, not for chat agents.")
        attributes = (self.parsed_output or {}).get("attributes", {})
        for name_attr, confirm_attr in CONFIRMATIONS:
            if confirm_attr in (self.get_command_spec() or {}).get("custom_attributes", []):
                given = str(_v(attributes, confirm_attr, "")).strip()
                expected = str(_v(attributes, name_attr, "")).strip()
                state = ("present and matches" if given and given == expected
                         else "missing" if not given else "does NOT match, so the command will be refused")
                notes.append(f"**Platform-wide change.** {confirm_attr} must repeat {name_attr} exactly; it is {state}. "
                             f"Validate mode writes nothing to Egeria.")
                guid_attr = name_attr.replace("Name", "GUID")
                supplied = _v(attributes, guid_attr)
                if supplied and given:
                    problem = await self.guid_mismatch(supplied, confirm_attr,
                                                       f"{self.command.verb} {self.command.object_type}",
                                                       enum=name_attr.startswith("Enum"))
                    notes.append(f"**{guid_attr} check failed:** {problem}" if problem
                                 else f"{guid_attr} {supplied} belongs to '{given}' (read-only check).")
        return report + ("\n\n> " + "\n> ".join(notes) + "\n" if notes else "")

    async def declared_properties(self, type_name: str) -> Dict[str, Any]:
        """property name -> (attribute type name, category) for a type and its super types."""
        declared: Dict[str, Any] = {}
        seen = set()
        current: Optional[str] = type_name
        while current and current not in seen:
            seen.add(current)
            definition = await self._type_def(current)
            for attribute in definition.get("attributeDefinitions") or []:
                attr_type = attribute.get("attributeType") or {}
                declared.setdefault(attribute.get("attributeName"), (attr_type.get("name"), attr_type.get("category")))
            current = (definition.get("superType") or {}).get("name")
        return declared

    async def type_name_of(self, result: Any, header_key: str, what: str) -> str:
        """The type name in an element/relationship read back from Egeria."""
        node = result[0] if isinstance(result, list) and result else result
        if isinstance(node, dict):
            for candidate in (node.get(header_key), node):
                name = ((candidate or {}).get("type") or {}).get("typeName")
                if name:
                    return name
        raise PyegeriaException(f"Could not read the type of {what} to check its properties.")

    def _result(self, what: str, detail: str = "") -> str:
        logger.success(f"{self.command.verb} {self.command.object_type}: {what}")
        text = f"\n\n## {self.command.verb} {self.command.object_type}\n\n{what}"
        return f"{text}: `{detail}`\n" if detail else f"{text}\n"

    async def _type_def(self, name: str) -> Dict[str, Any]:
        found = await self.client.valid_metadata._async_get_typedef_by_name(name)
        if not isinstance(found, dict) or not found.get("guid"):
            raise PyegeriaException(f"Type definition '{name}' was not found.")
        return found

    async def type_name_for_guid(self, guid: str, enum: bool = False) -> Optional[str]:
        """Name of the type or enum definition with this GUID, or None when it cannot be found.

        Egeria has no read-by-GUID for type definitions, so this lists them (reads only) and matches."""
        valid = self.client.valid_metadata
        if enum:
            sources = [valid._async_get_attribute_types(category="ENUM")]
        else:
            sources = [valid._async_get_all_entity_defs(), valid._async_get_all_relationship_defs(),
                       valid._async_get_all_classification_defs()]
        for source in sources:
            found = await source
            for item in found if isinstance(found, list) else []:
                if isinstance(item, dict) and item.get("guid") == guid:
                    return item.get("name")
        return None

    async def guid_mismatch(self, guid: str, echo_attr: str, what: str, enum: bool = False) -> Optional[str]:
        """Why a supplied GUID must not be used with this confirmation, or None when it matches.

        A wrong GUID with the right echo would change a different definition platform-wide. Reads only."""
        echo = str(_v(self.parsed_output["attributes"], echo_attr, "")).strip()
        actual = await self.type_name_for_guid(guid, enum)
        if actual is None:
            return (f"{what}: GUID {guid} was not found among the {'enum' if enum else 'type'} definitions, so it "
                    f"cannot be checked against {echo_attr} ({echo}); nothing was changed.")
        if actual != echo:
            return (f"{what}: GUID {guid} belongs to '{actual}', not '{echo}' ({echo_attr}). This would change a "
                    f"different definition for every user and app on this platform; nothing was changed.")
        return None

    async def check_guid_matches_echo(self, guid: str, echo_attr: str, what: str, enum: bool = False) -> None:
        problem = await self.guid_mismatch(guid, echo_attr, what, enum)
        if problem:
            raise PyegeriaException(problem)

    async def _enum_guid(self, name: str) -> str:
        found = await self.client.valid_metadata._async_get_attribute_types(category="ENUM")
        for item in found if isinstance(found, list) else []:
            if isinstance(item, dict) and item.get("name") == name and item.get("guid"):
                return item["guid"]
        raise PyegeriaException(f"Enum definition '{name}' was not found.")


class TypeDefProcessor(MetadataExpertProcessor):
    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        name = _v(attributes, "Type Def Name")
        if not name:
            raise PyegeriaException("Type Def Name is required.")
        verb = self.command.verb
        if verb in ("Update", "Delete"):
            confirm_name(attributes, "Type Def Name", "Confirm Type Def Name", f"{verb} Type Def")
        if verb == "Create":
            guid = await self.expert._async_add_type_def(type_def_body(attributes))
            self.parsed_output["guid"] = guid if isinstance(guid, str) else None
            return self._result(f"Added type definition '{name}'", guid if isinstance(guid, str) else "")
        supplied = _v(attributes, "Type Def GUID")
        if supplied:
            await self.check_guid_matches_echo(supplied, "Confirm Type Def Name", f"{verb} Type Def")
        guid = supplied or (await self._type_def(name))["guid"]
        if verb == "Delete":
            await self.expert._async_delete_type_def(guid, name)
            return self._result(f"Deleted type definition '{name}'", guid)
        if verb == "Update":
            patch = {"class": "OpenMetadataTypeDefPatch", "typeDefGUID": guid, "typeDefName": name,
                     "applyToVersion": int(_v(attributes, "Apply To Version"))}
            if _v(attributes, "Type Def Description"):
                patch["description"] = _v(attributes, "Type Def Description")
            if attribute_definitions(attributes):
                patch["attributeDefinitions"] = attribute_definitions(attributes)
            await self.expert._async_update_type_def(patch)
            return self._result(f"Updated type definition '{name}'", guid)
        raise PyegeriaException(f"Unsupported verb '{verb}' for Type Def.")


class EnumDefProcessor(MetadataExpertProcessor):
    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        name = _v(attributes, "Enum Def Name")
        if not name:
            raise PyegeriaException("Enum Def Name is required.")
        if self.command.verb == "Create":
            guid = await self.expert._async_add_enum_def(enum_def_body(attributes))
            self.parsed_output["guid"] = guid if isinstance(guid, str) else None
            return self._result(f"Added enum definition '{name}'", guid if isinstance(guid, str) else "")
        if self.command.verb == "Delete":
            confirm_name(attributes, "Enum Def Name", "Confirm Enum Def Name", "Delete Enum Def")
            supplied = _v(attributes, "Enum Def GUID")
            if supplied:
                await self.check_guid_matches_echo(supplied, "Confirm Enum Def Name", "Delete Enum Def", enum=True)
            guid = supplied or await self._enum_guid(name)
            await self.expert._async_delete_enum_def(guid, name)
            return self._result(f"Deleted enum definition '{name}'", guid)
        raise PyegeriaException(f"Unsupported verb '{self.command.verb}' for Enum Def.")


class CountMetadataElementsProcessor(MetadataExpertProcessor):
    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        body: Dict[str, Any] = {"class": "FindRequestBody"}
        if _v(attributes, "Count Element Type Name"):
            body["metadataElementTypeName"] = _v(attributes, "Count Element Type Name")
        if _v(attributes, "Count Search String"):
            body["searchString"] = _v(attributes, "Count Search String")
        count = await self.expert._async_count_metadata_elements(
            body, push_down=_bool(_v(attributes, "Count Push Down")))
        return self._result("Matching metadata elements", str(count))


class PublishMetadataElementProcessor(MetadataExpertProcessor):
    async def apply_changes(self) -> str:
        guid = self.parsed_output["attributes"].get("Metadata Element GUID", {}).get("value")
        if not guid:
            raise PyegeriaException("Metadata Element GUID is required.")
        await self.expert._async_publish_metadata_element(guid)
        self.parsed_output["guid"] = guid
        return self._result("Published metadata element", guid)


# --- instances, relationships and classifications -------------------------------------------------

_INTEGER_TYPES = {"int", "long", "short", "byte", "bigint"}
_DECIMAL_TYPES = {"float", "double", "bigdecimal"}


def _primitive(property_name: str, value: Any, type_name: str) -> Dict[str, Any]:
    """Coerce an authored value to the primitive type the type definition declares for the property.

    The declared type decides, never the text: "007" stays "007" in a string property. Anything that is
    not a plain scalar is refused in words rather than flattened with str()."""
    if isinstance(value, (dict, list, tuple, set)):
        raise PyegeriaException(
            f"Property '{property_name}' was given a map/list value; only single primitive values are supported here.")
    text = str(value).strip()
    kind = type_name.lower()

    def refuse(expected: str) -> PyegeriaException:
        return PyegeriaException(f"Property '{property_name}' is declared {kind} but '{text}' is not {expected}.")

    if kind == "string":
        parsed: Any = str(value)
    elif kind == "boolean":
        if text.lower() not in ("true", "false"):
            raise refuse("true or false")
        parsed = text.lower() == "true"
    elif kind in _INTEGER_TYPES:
        if not re.fullmatch(r"[+-]?\d+", text):
            raise refuse("a whole number")
        parsed = int(text)
    elif kind in _DECIMAL_TYPES:
        try:
            parsed = float(text)
        except ValueError:
            raise refuse("a number") from None
    elif kind == "char":
        if len(text) != 1:
            raise refuse("a single character")
        parsed = text
    elif kind == "date":
        if re.fullmatch(r"\d+", text):
            parsed = int(text)  # epoch milliseconds, as Egeria stores dates
        else:
            try:
                parsed = int(datetime.fromisoformat(text).timestamp() * 1000)
            except ValueError:
                raise refuse("epoch milliseconds or an ISO-8601 date") from None
    else:
        raise PyegeriaException(f"Property '{property_name}' has primitive type '{type_name}', which this family does not support.")
    return {"class": "PrimitiveTypePropertyValue", "typeName": kind, "primitiveValue": parsed}


def _declared_type(property_name: str, declared: Dict[str, Any], type_name: str) -> str:
    """The primitive type name for a property, or a refusal for unknown, enum, map and array properties."""
    if property_name not in declared:
        raise PyegeriaException(f"'{property_name}' is not a property of {type_name} (or its super types).")
    attr_type, category = declared[property_name]
    category_text = str(category or "").upper()
    if "ENUM" in category_text:
        raise PyegeriaException(
            f"Property '{property_name}' of {type_name} is an enum ({attr_type}); enum properties are not supported by this family yet.")
    if "COLLECTION" in category_text or str(attr_type).lower().startswith(("map", "array")):
        raise PyegeriaException(
            f"Property '{property_name}' of {type_name} is a {attr_type} (map/array); not supported by this family yet.")
    return str(attr_type)


def element_properties(properties: Optional[Dict[str, Any]], class_name: str,
                       declared: Optional[Dict[str, Any]] = None, type_name: str = "") -> Optional[Dict[str, Any]]:
    """'name: value' Dictionary -> {"class": class_name, "propertyValueMap": {...}}; None when empty.

    declared maps each property name to (attribute type name, attribute type category), read from the
    instance type's type definition and its super types. It is required whenever properties are given."""
    if not properties:
        return None
    if declared is None:
        raise PyegeriaException(f"Cannot send properties for {type_name or 'this type'} without its type definition.")
    return {"class": class_name,
            "propertyValueMap": {str(k): _primitive(str(k), v, _declared_type(str(k), declared, type_name))
                                 for k, v in properties.items()}}


def _require(attributes: Dict[str, Any], name: str) -> Any:
    value = _v(attributes, name)
    if value is None:
        raise PyegeriaException(f"{name} is required.")
    return value


DESTRUCTIVE_DELETE_METHODS = {"PURGE", "HARD_DELETE"}


def _delete_method(attributes: Dict[str, Any], guid: Optional[str] = None) -> str:
    """The delete method (default SOFT_DELETE). PURGE / HARD_DELETE cannot be undone, so they are refused
    unless Confirm Delete GUID repeats the GUID being deleted."""
    method = str(_v(attributes, "Delete Method", "SOFT_DELETE")).strip().upper()
    if method in DESTRUCTIVE_DELETE_METHODS:
        confirm = str(_v(attributes, "Confirm Delete GUID", "")).strip()
        if not guid or confirm != str(guid).strip():
            raise PyegeriaException(
                f"{method} is permanent. Repeat the GUID being deleted ({guid}) in Confirm Delete GUID to proceed; "
                f"it only works on an item that was already soft deleted.")
    return method


def new_instance_body(attributes: Dict[str, Any], declared: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    type_name = _require(attributes, "Instance Type Name")
    body: Dict[str, Any] = {"class": "NewOpenMetadataElementRequestBody", "typeName": type_name}
    props = element_properties(_v(attributes, "Instance Properties"), "EntityElementProperties", declared, type_name)
    if props:
        body["properties"] = props
    if _v(attributes, "Anchor GUID"):
        body["anchorGUID"] = _v(attributes, "Anchor GUID")
    if _bool(_v(attributes, "Is Own Anchor")) is not None:
        body["isOwnAnchor"] = _bool(_v(attributes, "Is Own Anchor"))
    if _v(attributes, "Parent GUID"):
        if not _v(attributes, "Parent Relationship Type Name"):
            raise PyegeriaException("Parent Relationship Type Name is required when Parent GUID is given.")
        body["parentGUID"] = _v(attributes, "Parent GUID")
        body["parentRelationshipTypeName"] = _v(attributes, "Parent Relationship Type Name")
        at_end_1 = _bool(_v(attributes, "Parent at End1"))
        body["parentAtEnd1"] = True if at_end_1 is None else at_end_1
    return body


def update_properties_body(properties: Optional[Dict[str, Any]], class_name: str,
                           attributes: Dict[str, Any], declared: Optional[Dict[str, Any]] = None,
                           type_name: str = "") -> Dict[str, Any]:
    props = element_properties(properties, class_name, declared, type_name)
    if not props:
        raise PyegeriaException("At least one property is required.")
    return {"class": "UpdatePropertiesRequestBody", "properties": props,
            "replaceProperties": bool(_bool(_v(attributes, "Replace Properties")))}


def related_elements_body(attributes: Dict[str, Any], declared: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    type_name = _require(attributes, "Relationship Type Name")
    body: Dict[str, Any] = {"class": "NewRelatedElementsRequestBody",
                            "typeName": type_name,
                            "metadataElement1GUID": _require(attributes, "Element 1 GUID"),
                            "metadataElement2GUID": _require(attributes, "Element 2 GUID")}
    props = element_properties(_v(attributes, "Relationship Properties"), "RelationshipElementProperties",
                               declared, type_name)
    if props:
        body["properties"] = props
    return body


class InstanceProcessor(MetadataExpertProcessor):
    """Create / Update / Delete Instance."""

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        verb = self.command.verb
        if verb == "Create":
            type_name = _require(attributes, "Instance Type Name")
            declared = await self.declared_properties(type_name) if _v(attributes, "Instance Properties") else None
            guid = await self.expert._async_create_metadata_element(new_instance_body(attributes, declared))
            self.parsed_output["guid"] = guid if isinstance(guid, str) else None
            return self._result(f"Created {_v(attributes, 'Instance Type Name')} instance", guid if isinstance(guid, str) else "")
        guid = _require(attributes, "Metadata Element GUID")
        self.parsed_output["guid"] = guid
        if verb == "Update":
            type_name = await self.type_name_of(
                await self.expert._async_get_metadata_element_by_guid(guid), "elementHeader", f"element {guid}")
            declared = await self.declared_properties(type_name)
            await self.expert._async_update_metadata_element_properties(
                guid, update_properties_body(_v(attributes, "Instance Properties"), "EntityElementProperties",
                                             attributes, declared, type_name))
            return self._result("Updated instance", guid)
        if verb == "Delete":
            await self.expert._async_delete_metadata_element(
                guid, {"class": "DeleteElementRequestBody", "deleteMethod": _delete_method(attributes, guid)})
            return self._result("Deleted instance", guid)
        raise PyegeriaException(f"Unsupported verb '{verb}' for Instance.")


class InstanceRelationshipProcessor(MetadataExpertProcessor):
    """Link / Unlink Instances and Update Relationship."""

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        verb, object_type = self.command.verb, self.command.object_type
        if verb == "Link":
            type_name = _require(attributes, "Relationship Type Name")
            declared = await self.declared_properties(type_name) if _v(attributes, "Relationship Properties") else None
            guid = await self.expert._async_create_related_elements(related_elements_body(attributes, declared))
            self.parsed_output["guid"] = guid if isinstance(guid, str) else None
            return self._result("Created relationship", guid if isinstance(guid, str) else "")
        guid = _require(attributes, "Relationship GUID")
        self.parsed_output["guid"] = guid
        if verb == "Unlink":
            await self.expert._async_delete_related_elements(
                guid, {"class": "DeleteRelationshipRequestBody", "deleteMethod": _delete_method(attributes, guid)})
            return self._result("Deleted relationship", guid)
        if verb == "Update" and object_type == "Relationship":
            type_name = await self.type_name_of(
                await self.expert._async_get_relationship_by_guid(guid), "relationshipHeader", f"relationship {guid}")
            declared = await self.declared_properties(type_name)
            await self.expert._async_update_related_elements_properties(
                guid, update_properties_body(_v(attributes, "Relationship Properties"),
                                             "RelationshipElementProperties", attributes, declared, type_name))
            return self._result("Updated relationship", guid)
        raise PyegeriaException(f"Unsupported command '{verb} {object_type}'.")


class InstanceClassificationProcessor(MetadataExpertProcessor):
    """Classify / Reclassify / Declassify Instance."""

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        guid = _require(attributes, "Metadata Element GUID")
        name = _require(attributes, "Classification Name")
        self.parsed_output["guid"] = guid
        props = _v(attributes, "Classification Properties")
        verb = self.command.verb
        if verb == "Classify":
            body: Dict[str, Any] = {"class": "NewClassificationRequestBody"}
            declared = await self.declared_properties(name) if props else None
            cls_props = element_properties(props, "ClassificationElementProperties", declared, name)
            if cls_props:
                body["properties"] = cls_props
            await self.expert._async_classify_metadata_element(guid, name, body)
            return self._result(f"Classified as {name}", guid)
        if verb == "Reclassify":
            declared = await self.declared_properties(name)
            await self.expert._async_reclassify_metadata_element(
                guid, name, update_properties_body(props, "ClassificationElementProperties", attributes,
                                                   declared, name))
            return self._result(f"Reclassified {name}", guid)
        if verb == "Declassify":
            await self.expert._async_declassify_metadata_element(guid, name)
            return self._result(f"Removed classification {name}", guid)
        raise PyegeriaException(f"Unsupported verb '{verb}' for Instance classification.")
