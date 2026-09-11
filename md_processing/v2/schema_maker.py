"""
Schema Maker Processor for Dr.Egeria v2.

Wraps `pyegeria/omvs/schema_maker.py`: SchemaType/SchemaAttribute element
lifecycle (create/update, plus create-from-template), the family's ~15
relationship link/detach pairs, and its three classification add/remove
pairs (PrimaryKey, TypeEmbeddedAttribute, CalculatedValue).
"""
from typing import Any, Dict, Optional

from loguru import logger

from md_processing.v2.processors import AsyncBaseCommandProcessor
from md_processing.md_processing_utils.common_md_utils import update_element_dictionary


def _v(attributes: dict, name: str, default=None):
    return attributes.get(name, {}).get("value", default)


def _guid(attributes: dict, name: str):
    return attributes.get(name, {}).get("guid")


def _outer_body(attributes: dict, properties: dict) -> dict:
    """Build the NewElementRequestBody wrapper shared by Create Schema Type
    and Create Schema Attribute."""
    return {
        "class": "NewElementRequestBody",
        "anchorGUID": _guid(attributes, "Anchor ID"),
        "isOwnAnchor": _v(attributes, "Is Own Anchor", True),
        "anchorScopeGUIDs": attributes.get("Anchor Scope IDs", {}).get("guid_list"),
        "initialClassifications": _v(attributes, "Initial Classifications"),
        "parentGUID": _guid(attributes, "Parent ID"),
        "parentRelationshipTypeName": _v(attributes, "Parent Relationship Type Name"),
        "parentRelationshipProperties": _v(attributes, "Parent Relationship Attributes"),
        "parentAtEnd1": _v(attributes, "Parent at End1", True),
        "properties": properties,
    }


class SchemaElementProcessor(AsyncBaseCommandProcessor):
    """Processor for Create/Update Schema Type and Create/Update Schema
    Attribute (both participate in the standard Create<->Update upsert
    transition, like every other element-lifecycle processor)."""

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output.get("qualified_name") or self.derive_qualified_name(attributes)
        display_name = _v(attributes, "Display Name") or qualified_name
        om_type = self.get_command_spec().get("OM_TYPE")
        is_attribute = om_type == "SchemaAttribute"
        client = self.client.schema_maker

        props: Dict[str, Any] = {
            "class": "SchemaAttributeProperties" if is_attribute else "SchemaTypeProperties",
            "typeName": om_type,
            "qualifiedName": qualified_name,
            "displayName": display_name,
            "description": _v(attributes, "Description"),
            "category": _v(attributes, "Category"),
            "versionIdentifier": _v(attributes, "Version Identifier"),
            "url": _v(attributes, "URL"),
            "usage": _v(attributes, "Usage"),
            "contentStatus": _v(attributes, "Content Status"),
            "authors": _v(attributes, "Authors"),
            "additionalProperties": _v(attributes, "Additional Properties"),
            "effectiveFrom": _v(attributes, "Effective From"),
            "effectiveTo": _v(attributes, "Effective To"),
        }
        if is_attribute:
            props.update({
                "elementPosition": _v(attributes, "Element Position"),
                "minCardinality": _v(attributes, "Min Cardinality"),
                "maxCardinality": _v(attributes, "Max Cardinality"),
                "allowsDuplicateValues": _v(attributes, "Allows Duplicate Values"),
                "isOrderedValues": _v(attributes, "Is Ordered Values"),
                "defaultValueOverride": _v(attributes, "Default Value Override"),
            })
        else:
            props.update({
                "isDeprecated": _v(attributes, "Is Deprecated"),
                "author": _v(attributes, "Author"),
                "encodingStandard": _v(attributes, "Encoding Standard"),
                "namespace": _v(attributes, "Namespace"),
            })

        if self.as_is_element:
            guid = self.as_is_element["elementHeader"]["guid"]
            update_body = {
                "class": "UpdateElementRequestBody",
                "properties": self.filter_update_properties(props, _v(attributes, "Merge Update", True)),
                "mergeUpdate": _v(attributes, "Merge Update", True),
            }
            if is_attribute:
                await client._async_update_schema_attribute(guid, update_body)
            else:
                await client._async_update_schema_type(guid, update_body)
            verb_word = "Updated"
        else:
            create_body = _outer_body(attributes, props)
            if is_attribute:
                guid = await client._async_create_schema_attribute(create_body)
            else:
                guid = await client._async_create_schema_type(create_body)
            guid = self.extract_guid_or_raise(guid, f"Create {om_type}")
            verb_word = "Created"

        self.parsed_output["guid"] = guid
        update_element_dictionary(qualified_name, {"guid": guid, "display_name": display_name})
        logger.success(f"{verb_word} {om_type} '{display_name}' with GUID {guid}")
        return await self.render_result_markdown(guid)


class SchemaTemplateProcessor(AsyncBaseCommandProcessor):
    """Processor for Create Schema Type/Attribute From Template -- pure
    create-from-template, no update path (matches Asset Maker's own
    template-based commands)."""

    def supports_target_element_lookup(self) -> bool:
        return False

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    async def apply_changes(self) -> str:
        attributes = self.parsed_output.get("attributes", {})
        om_type = self.get_command_spec().get("OM_TYPE")
        client = self.client.schema_maker

        body = {
            "class": "TemplateRequestBody",
            "templateGUID": _guid(attributes, "Template GUID") or _v(attributes, "Template GUID"),
            "placeholderPropertyValues": _v(attributes, "Placeholder Property Values") or {},
            "replacementProperties": _v(attributes, "Template Properties"),
        }
        if om_type == "SchemaAttribute":
            guid = await client._async_create_schema_attribute_from_template(body)
        else:
            guid = await client._async_create_schema_type_from_template(body)
        guid = self.extract_guid_or_raise(guid, f"Create {om_type} From Template")

        self.parsed_output["guid"] = guid
        logger.success(f"Created {om_type} from template with GUID {guid}")
        return await self.render_result_markdown(guid)


# ---------------------------------------------------------------- relationships

# command noun -> (link method name, detach method name, end1 attr, end2 attr)
_LINK_SPECS = {
    "NestedSchemaAttribute": ("_async_link_nested_schema_attribute", "_async_detach_nested_schema_attribute",
                               "Schema Attribute GUID", "Nested Schema Attribute GUID"),
    "AttributeForSchema": ("_async_link_attribute_for_schema", "_async_detach_attribute_for_schema",
                            "Schema Type GUID", "Schema Attribute GUID"),
    "ForeignKey": ("_async_link_foreign_key", "_async_detach_foreign_key",
                   "Primary Key Column GUID", "Foreign Key Column GUID"),
    "LinkedExternalSchemaType": ("_async_link_external_schema_type", "_async_detach_external_schema_type",
                                 "Schema Element GUID", "External Schema Type GUID"),
    "MapFromElementType": ("_async_link_map_from_schema_type", "_async_detach_map_from_schema_type",
                           "Schema Element GUID", "Schema Type GUID"),
    "MapToElementType": ("_async_link_map_to_schema_type", "_async_detach_map_to_schema_type",
                         "Schema Element GUID", "Schema Type GUID"),
    "GraphEdgeLink": ("_async_link_graph_edge", "_async_detach_graph_edge",
                      "Graph Edge GUID", "Graph Vertex GUID"),
    "DerivedSchemaTypeQueryTarget": ("_async_link_query_target", "_async_detach_query_target",
                                     "Schema Element GUID", "Query Target Schema Element GUID"),
    "Schema": ("_async_link_schema", "_async_detach_schema",
               "Schema Element GUID", "Schema Type GUID"),
    "RelationalDBSchema": ("_async_link_relational_db_schema", "_async_detach_relational_db_schema",
                           "Database Schema Type List GUID", "Relational DB Schema Type GUID"),
    "APIOperations": ("_async_link_api_operations", "_async_detach_api_operations",
                      "API Schema Type GUID", "API Operation GUID"),
    "APIHeader": ("_async_link_api_header", "_async_detach_api_header",
                 "API Operation GUID", "Schema Type GUID"),
    "APIRequest": ("_async_link_api_request", "_async_detach_api_request",
                  "API Operation GUID", "Schema Type GUID"),
    "APIResponse": ("_async_link_api_response", "_async_detach_api_response",
                    "API Operation GUID", "Schema Type GUID"),
    "SchemaTypeOption": ("_async_link_schema_type_option", "_async_detach_schema_type_option",
                        "Schema Element GUID", "Schema Type GUID"),
}


class SchemaLinkProcessor(AsyncBaseCommandProcessor):
    """Processor for every Link/Detach relationship command in the Schema
    Maker family. Dispatches on OM_TYPE to the matching schema_maker.py
    link_/detach_ method pair."""

    def supports_target_element_lookup(self) -> bool:
        return False

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    async def apply_changes(self) -> str:
        attributes = self.parsed_output.get("attributes", {})
        om_type = self.get_command_spec().get("OM_TYPE")
        spec = _LINK_SPECS.get(om_type)
        if not spec:
            raise ValueError(f"SchemaLinkProcessor: unrecognized relationship OM_TYPE {om_type!r}")
        link_method, detach_method, attr1, attr2 = spec

        end1 = _guid(attributes, attr1)
        end2 = _guid(attributes, attr2)
        is_link = self.command.verb in ("Link", "Attach", "Add")

        if is_link:
            props: Dict[str, Any] = {}
            label = _v(attributes, "Link Label")
            desc = _v(attributes, "Link Description")
            if label is not None:
                props["label"] = label
            if desc is not None:
                props["description"] = desc
            body = {"class": "NewRelationshipRequestBody", "properties": props} if props else None
            await getattr(self.client.schema_maker, link_method)(end1, end2, body)
            verb_word = "Linked"
        else:
            await getattr(self.client.schema_maker, detach_method)(end1, end2, None)
            verb_word = "Detached"

        self.add_related_result(f"{om_type} ({attr1} -> {attr2})", guid=end1)
        logger.success(f"{verb_word} {om_type} between {end1} and {end2}")
        return await self.display_only()


# ---------------------------------------------------------------- classifications

# command noun -> (add method, remove method, target attr, extra props: {json_key: attr_name})
_CLASSIFICATION_SPECS = {
    "PrimaryKey": ("_async_add_primary_key_classification", "_async_remove_primary_key_classification",
                   "Relational Column GUID",
                   {"name": "Primary Key Name", "keyPattern": "Primary Key Pattern"}),
    "TypeEmbeddedAttribute": ("_async_add_type_embedded_attribute", "_async_remove_type_embedded_attribute",
                              "Schema Attribute GUID",
                              {"dataType": "Embedded Data Type", "defaultValue": "Embedded Default Value",
                               "fixedValue": "Embedded Fixed Value"}),
    "CalculatedValue": ("_async_add_calculated_value", "_async_remove_calculated_value",
                        "Schema Attribute GUID",
                        {"formula": "Formula", "formulaType": "Formula Type"}),
}


class SchemaClassificationProcessor(AsyncBaseCommandProcessor):
    """Processor for Add/Remove PrimaryKey, TypeEmbeddedAttribute, and
    CalculatedValue classifications on a schema attribute/column."""

    def supports_target_element_lookup(self) -> bool:
        return False

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    async def apply_changes(self) -> str:
        attributes = self.parsed_output.get("attributes", {})
        om_type = self.get_command_spec().get("OM_TYPE")
        spec = _CLASSIFICATION_SPECS.get(om_type)
        if not spec:
            raise ValueError(f"SchemaClassificationProcessor: unrecognized classification OM_TYPE {om_type!r}")
        add_method, remove_method, target_attr, prop_map = spec
        target_guid = _guid(attributes, target_attr)
        is_add = self.command.verb in ("Add", "Classify")

        if is_add:
            props = {"class": f"{om_type}Properties"}
            for json_key, attr_name in prop_map.items():
                val = _v(attributes, attr_name)
                if val is not None:
                    props[json_key] = val
            body = {"class": "NewClassificationRequestBody", "properties": props}
            await getattr(self.client.schema_maker, add_method)(target_guid, body)
            verb_word = "Added"
        else:
            await getattr(self.client.schema_maker, remove_method)(target_guid, None)
            verb_word = "Removed"

        self.add_related_result(f"{om_type} classification", guid=target_guid)
        logger.success(f"{verb_word} {om_type} classification on {target_guid}")
        return await self.display_only()
