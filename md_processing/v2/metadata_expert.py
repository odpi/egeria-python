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

    def _result(self, what: str, detail: str = "") -> str:
        logger.success(f"{self.command.verb} {self.command.object_type}: {what}")
        text = f"\n\n## {self.command.verb} {self.command.object_type}\n\n{what}"
        return f"{text}: `{detail}`\n" if detail else f"{text}\n"

    async def _type_def(self, name: str) -> Dict[str, Any]:
        found = await self.client.valid_metadata._async_get_typedef_by_name(name)
        if not isinstance(found, dict) or not found.get("guid"):
            raise PyegeriaException(f"Type definition '{name}' was not found.")
        return found

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
        if verb == "Create":
            guid = await self.expert._async_add_type_def(type_def_body(attributes))
            self.parsed_output["guid"] = guid if isinstance(guid, str) else None
            return self._result(f"Added type definition '{name}'", guid if isinstance(guid, str) else "")
        guid = _v(attributes, "Type Def GUID") or (await self._type_def(name))["guid"]
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
            guid = _v(attributes, "Enum Def GUID") or await self._enum_guid(name)
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

def _primitive(value: Any) -> Dict[str, Any]:
    """Infer a PrimitiveTypePropertyValue from an authored string: true/false -> boolean,
    whole number -> int, anything else -> string."""
    text = str(value).strip()
    if text.lower() in ("true", "false"):
        return {"class": "PrimitiveTypePropertyValue", "typeName": "boolean", "primitiveValue": text.lower() == "true"}
    if re.fullmatch(r"-?\d+", text):
        return {"class": "PrimitiveTypePropertyValue", "typeName": "int", "primitiveValue": int(text)}
    return {"class": "PrimitiveTypePropertyValue", "typeName": "string", "primitiveValue": text}


def element_properties(properties: Optional[Dict[str, Any]], class_name: str) -> Optional[Dict[str, Any]]:
    """'name: value' Dictionary -> {"class": class_name, "propertyValueMap": {...}}; None when empty."""
    if not properties:
        return None
    return {"class": class_name, "propertyValueMap": {str(k): _primitive(v) for k, v in properties.items()}}


def _require(attributes: Dict[str, Any], name: str) -> Any:
    value = _v(attributes, name)
    if value is None:
        raise PyegeriaException(f"{name} is required.")
    return value


def _delete_method(attributes: Dict[str, Any]) -> str:
    return str(_v(attributes, "Delete Method", "SOFT_DELETE")).strip().upper()


def new_instance_body(attributes: Dict[str, Any]) -> Dict[str, Any]:
    body: Dict[str, Any] = {"class": "NewOpenMetadataElementRequestBody",
                            "typeName": _require(attributes, "Instance Type Name")}
    props = element_properties(_v(attributes, "Instance Properties"), "EntityElementProperties")
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
                           attributes: Dict[str, Any]) -> Dict[str, Any]:
    props = element_properties(properties, class_name)
    if not props:
        raise PyegeriaException("At least one property is required.")
    return {"class": "UpdatePropertiesRequestBody", "properties": props,
            "replaceProperties": bool(_bool(_v(attributes, "Replace Properties")))}


def related_elements_body(attributes: Dict[str, Any]) -> Dict[str, Any]:
    body: Dict[str, Any] = {"class": "NewRelatedElementsRequestBody",
                            "typeName": _require(attributes, "Relationship Type Name"),
                            "metadataElement1GUID": _require(attributes, "Element 1 GUID"),
                            "metadataElement2GUID": _require(attributes, "Element 2 GUID")}
    props = element_properties(_v(attributes, "Relationship Properties"), "RelationshipElementProperties")
    if props:
        body["properties"] = props
    return body


class InstanceProcessor(MetadataExpertProcessor):
    """Create / Update / Delete Instance."""

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        verb = self.command.verb
        if verb == "Create":
            guid = await self.expert._async_create_metadata_element(new_instance_body(attributes))
            self.parsed_output["guid"] = guid if isinstance(guid, str) else None
            return self._result(f"Created {_v(attributes, 'Instance Type Name')} instance", guid if isinstance(guid, str) else "")
        guid = _require(attributes, "Metadata Element GUID")
        self.parsed_output["guid"] = guid
        if verb == "Update":
            await self.expert._async_update_metadata_element_properties(
                guid, update_properties_body(_v(attributes, "Instance Properties"), "EntityElementProperties", attributes))
            return self._result("Updated instance", guid)
        if verb == "Delete":
            await self.expert._async_delete_metadata_element(
                guid, {"class": "DeleteElementRequestBody", "deleteMethod": _delete_method(attributes)})
            return self._result("Deleted instance", guid)
        raise PyegeriaException(f"Unsupported verb '{verb}' for Instance.")


class InstanceRelationshipProcessor(MetadataExpertProcessor):
    """Link / Unlink Instances and Update Relationship."""

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        verb, object_type = self.command.verb, self.command.object_type
        if verb == "Link":
            guid = await self.expert._async_create_related_elements(related_elements_body(attributes))
            self.parsed_output["guid"] = guid if isinstance(guid, str) else None
            return self._result("Created relationship", guid if isinstance(guid, str) else "")
        guid = _require(attributes, "Relationship GUID")
        self.parsed_output["guid"] = guid
        if verb == "Unlink":
            await self.expert._async_delete_related_elements(
                guid, {"class": "DeleteRelationshipRequestBody", "deleteMethod": _delete_method(attributes)})
            return self._result("Deleted relationship", guid)
        if verb == "Update" and object_type == "Relationship":
            await self.expert._async_update_related_elements_properties(
                guid, update_properties_body(_v(attributes, "Relationship Properties"),
                                             "RelationshipElementProperties", attributes))
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
            cls_props = element_properties(props, "ClassificationElementProperties")
            if cls_props:
                body["properties"] = cls_props
            await self.expert._async_classify_metadata_element(guid, name, body)
            return self._result(f"Classified as {name}", guid)
        if verb == "Reclassify":
            await self.expert._async_reclassify_metadata_element(
                guid, name, update_properties_body(props, "ClassificationElementProperties", attributes))
            return self._result(f"Reclassified {name}", guid)
        if verb == "Declassify":
            await self.expert._async_declassify_metadata_element(guid, name)
            return self._result(f"Removed classification {name}", guid)
        raise PyegeriaException(f"Unsupported verb '{verb}' for Instance classification.")
