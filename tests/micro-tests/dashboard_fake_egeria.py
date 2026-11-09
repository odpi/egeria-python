# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
An in-memory Egeria for the dashboard-sheet tests: entities and relationships, answering the handful of
client calls the dashboard-sheet writer and reader make, with the response shapes checked live on
2026-11-09 (related elements come back as {elementHeader, relatedBy: {relationshipHeader,
relationshipProperties}, properties}).

Every subclient name (schema_maker, asset_maker, classification_manager, ...) is this same object, as
EgeriaTech proxies them. Every write is recorded in `writes` as (method, *args) so tests can assert "the
second run wrote nothing" and "no Report was deleted". An unknown method raises AttributeError, so a call
the fake does not model fails loudly instead of silently succeeding.

Not a test module (no test_ prefix); tests load it with load_fake().
"""
from __future__ import annotations

import importlib.util
import pathlib
import uuid
from typing import Any, Dict, List, Optional

from pyegeria.omvs.asset_maker import resolve_placement_reports

SUPERTYPES = {
    "Dashboard": ["DataSet", "Asset", "Referenceable"],
    "Report": ["DataSet", "Asset", "Referenceable"],
    "ReportSpec": ["Collection", "Referenceable"],
    "ReportType": ["Referenceable"],
    "Perspective": ["Referenceable"],
    "DisplayDataSchemaType": ["RootSchemaType", "ComplexSchemaType", "SchemaType", "Referenceable"],
    "DisplayDataContainer": ["SchemaAttribute", "Referenceable"],
    "DisplayDataField": ["SchemaAttribute", "Referenceable"],
}

SUBCLIENTS = ("schema_maker", "asset_maker", "classification_manager", "collection_manager", "data_designer",
              "collections", "class_mgr", "metadata_expert")


class FakeEgeria:
    def __init__(self):
        self.entities: Dict[str, Dict[str, Any]] = {}
        self.relationships: List[Dict[str, Any]] = []
        self.writes: List[tuple] = []
        self._n = 0

    def __getattr__(self, name):
        if name in SUBCLIENTS:
            return self
        raise AttributeError(name)

    # ---------------------------------------------------------------- seeding / inspection

    def _new_guid(self) -> str:
        self._n += 1
        return str(uuid.UUID(int=self._n))

    def add_entity(self, type_name: str, qualified_name: str, display_name: Optional[str] = None,
                   **props) -> str:
        guid = self._new_guid()
        self.entities[guid] = {"type": type_name, "props": {"qualifiedName": qualified_name,
                                                            "displayName": display_name or qualified_name,
                                                            **props}}
        return guid

    def by_qn(self, qualified_name: str) -> Optional[str]:
        return next((g for g, e in self.entities.items() if e["props"].get("qualifiedName") == qualified_name), None)

    def of_type(self, type_name: str) -> List[str]:
        return [g for g, e in self.entities.items() if e["type"] == type_name]

    def rels(self, type_name: str) -> List[Dict[str, Any]]:
        return [r for r in self.relationships if r["type"] == type_name]

    def write_names(self) -> List[str]:
        return [w[0] for w in self.writes]

    # ---------------------------------------------------------------- element shapes

    def _header(self, guid: str) -> Dict[str, Any]:
        e = self.entities[guid]
        return {"class": "ElementHeader", "guid": guid,
                "type": {"typeName": e["type"], "superTypeNames": SUPERTYPES.get(e["type"], [])}}

    def element(self, guid: str) -> Dict[str, Any]:
        e = self.entities[guid]
        return {"class": "OpenMetadataRootElement", "elementHeader": self._header(guid),
                "properties": {"typeName": e["type"], **{k: v for k, v in e["props"].items() if v is not None}}}

    def _related_shape(self, guid: str, rel: Dict[str, Any]) -> Dict[str, Any]:
        out = self.element(guid)
        out["relatedBy"] = {"relationshipHeader": {"guid": rel["guid"], "type": {"typeName": rel["type"]}},
                            "relationshipProperties": {"typeName": rel["type"], **rel["props"]}}
        return out

    # ---------------------------------------------------------------- reads

    async def _async_get_element_by_unique_name(self, name, property_name=None, **kwargs):
        guid = self.by_qn(name)
        return self.element(guid) if guid else "No elements found"

    async def _async_get_element_by_guid_(self, guid, **kwargs):
        return self.element(guid) if guid in self.entities else "No elements found"

    async def __async_get_guid__(self, guid=None, display_name=None, property_name="qualifiedName",
                                 qualified_name=None, tech_type=None, **kwargs):
        if guid:
            return guid
        hits = []
        for g, e in self.entities.items():
            if tech_type and tech_type not in (e["type"], *SUPERTYPES.get(e["type"], [])):
                continue
            if e["props"].get("qualifiedName") == qualified_name or e["props"].get("displayName") == display_name:
                hits.append(g)
        if len(hits) > 1:
            from pyegeria.core._exceptions import PyegeriaException
            raise PyegeriaException(context={"reason": "Multiple elements found"})
        return hits[0] if hits else "No elements found"

    async def _async_get_related_elements(self, element_guid, relationship_type=None, start_at_end=1,
                                          start_from=0, page_size=0, **kwargs):
        out = []
        for rel in self.relationships:
            if relationship_type and rel["type"] != relationship_type:
                continue
            if start_at_end == 1 and rel["end1"] == element_guid:
                out.append(self._related_shape(rel["end2"], rel))
            elif start_at_end == 2 and rel["end2"] == element_guid:
                out.append(self._related_shape(rel["end1"], rel))
        page = out[start_from:start_from + page_size] if page_size else out[start_from:]
        return page if page else "No elements found"

    async def _async_find_elements_by_property_value(self, property_value, property_names, metadata_element_type=None,
                                                     starts_with=True, start_from=0, page_size=0, **kwargs):
        hits = []
        for g, e in self.entities.items():
            if metadata_element_type and e["type"] != metadata_element_type:
                continue
            for prop in property_names:
                value = str(e["props"].get(prop) or "")
                # live Egeria: starts_with=False is a contains match, not an exact one
                if (value.startswith(property_value) if starts_with else property_value in value):
                    hits.append(self.element(g))
                    break
        page = hits[start_from:start_from + page_size] if page_size else hits[start_from:]
        return page if page else "No elements found"

    async def _async_get_elements_by_property_value(self, property_value, property_names, metadata_element_type=None,
                                                    start_from=0, page_size=0, **kwargs):
        """Exact match (classification-explorer by-exact-property-value)."""
        hits = [self.element(g) for g, e in self.entities.items()
                if (not metadata_element_type or e["type"] == metadata_element_type)
                and any(e["props"].get(p) == property_value for p in property_names)]
        page = hits[start_from:start_from + page_size] if page_size else hits[start_from:]
        return page if page else "No elements found"

    async def _async_get_placement_reports(self, dashboard_guid, placement_qualified_names, **kwargs):
        element = self.element(dashboard_guid)
        links = []
        for rel in self.rels("DataSetContent"):
            if rel["end1"] == dashboard_guid:
                links.append({"relationshipHeader": {"guid": rel["guid"]},
                              "relationshipProperties": rel["props"],
                              "relatedElement": self.element(rel["end2"])})
        if links:
            element["dataSetContent"] = links
        return resolve_placement_reports(element, placement_qualified_names)

    # ---------------------------------------------------------------- writes

    def _link(self, rel_type: str, end1: str, end2: str, props: Optional[Dict[str, Any]] = None) -> str:
        assert end1 in self.entities and end2 in self.entities, (rel_type, end1, end2)
        guid = self._new_guid()
        clean = {k: v for k, v in (props or {}).items() if k not in ("class",) and v is not None}
        self.relationships.append({"guid": guid, "type": rel_type, "end1": end1, "end2": end2, "props": clean})
        return guid

    def _unlink(self, rel_type: str, end1: str, end2: str) -> None:
        self.relationships = [r for r in self.relationships
                              if not (r["type"] == rel_type and r["end1"] == end1 and r["end2"] == end2)]

    def _create(self, body: Dict[str, Any]) -> str:
        props = dict(body["properties"])
        type_name = props.pop("typeName")
        props.pop("class", None)
        assert self.by_qn(props["qualifiedName"]) is None, f"duplicate qualifiedName {props['qualifiedName']}"
        guid = self._new_guid()
        self.entities[guid] = {"type": type_name, "props": props, "anchor": body.get("anchorGUID")}
        return guid

    def _update(self, guid: str, body: Dict[str, Any]) -> None:
        props = {k: v for k, v in body["properties"].items() if k not in ("class", "typeName")}
        if body.get("mergeUpdate", True):
            self.entities[guid]["props"].update({k: v for k, v in props.items() if v is not None})
        else:
            self.entities[guid]["props"] = props

    def _delete(self, guid: str) -> None:
        del self.entities[guid]
        self.relationships = [r for r in self.relationships if guid not in (r["end1"], r["end2"])]

    async def _async_create_asset(self, prop_classes, body):
        self.writes.append(("create_asset", body["properties"]["qualifiedName"]))
        return self._create(body)

    async def _async_update_asset(self, guid, body):
        self.writes.append(("update_asset", guid))
        self._update(guid, body)

    async def _async_delete_asset(self, guid, body=None):
        self.writes.append(("delete_asset", self.entities[guid]["type"], guid))
        self._delete(guid)

    async def _async_create_schema_type(self, body):
        self.writes.append(("create_schema_type", body["properties"]["qualifiedName"]))
        return self._create(body)

    async def _async_create_schema_attribute(self, body):
        self.writes.append(("create_schema_attribute", body["properties"]["qualifiedName"]))
        return self._create(body)

    async def _async_update_schema_attribute(self, guid, body):
        self.writes.append(("update_schema_attribute", guid))
        self._update(guid, body)

    async def _async_delete_schema_attribute(self, guid, body=None, cascade_delete=False):
        self.writes.append(("delete_schema_attribute", self.entities[guid]["type"], guid))
        self._delete(guid)

    async def _async_delete_schema_type(self, guid, body=None, cascade_delete=False):
        self.writes.append(("delete_schema_type", self.entities[guid]["type"], guid))
        self._delete(guid)

    async def _async_link_schema(self, element_guid, schema_type_guid, body=None):
        self.writes.append(("link_schema", element_guid, schema_type_guid))
        return self._link("Schema", element_guid, schema_type_guid)

    async def _async_link_attribute_for_schema(self, schema_type_guid, attribute_guid, body=None):
        self.writes.append(("link_attribute_for_schema", schema_type_guid, attribute_guid))
        return self._link("AttributeForSchema", schema_type_guid, attribute_guid, (body or {}).get("properties"))

    async def _async_link_nested_schema_attribute(self, parent_guid, child_guid, body=None):
        self.writes.append(("link_nested_schema_attribute", parent_guid, child_guid))
        return self._link("NestedSchemaAttribute", parent_guid, child_guid, (body or {}).get("properties"))

    async def _async_link_placement_report(self, dashboard_guid, report_guid, placement_qualified_name, body=None):
        self.writes.append(("link_placement_report", dashboard_guid, report_guid, placement_qualified_name))
        return self._link("DataSetContent", dashboard_guid, report_guid,
                          {"queryId": placement_qualified_name, "queryType": "placement"})

    async def _async_detach_placement_report(self, dashboard_guid, placement_qualified_name, body=None):
        self.writes.append(("detach_placement_report", dashboard_guid, placement_qualified_name))
        before = len(self.relationships)
        self.relationships = [r for r in self.relationships
                              if not (r["type"] == "DataSetContent" and r["end1"] == dashboard_guid
                                      and r["props"].get("queryId") == placement_qualified_name)]
        return before - len(self.relationships)

    async def _async_add_scope_to_element(self, scoped_by_guid, element_guid, body=None):
        self.writes.append(("add_scope", scoped_by_guid, element_guid))
        return self._link("ScopedBy", scoped_by_guid, element_guid)

    async def _async_clear_scope_from_element(self, scoped_by_guid, element_guid, body=None, cascade_delete=False):
        self.writes.append(("clear_scope", scoped_by_guid, element_guid))
        self._unlink("ScopedBy", scoped_by_guid, element_guid)

    async def _async_attach_data_description(self, element_guid, collection_guid, body=None):
        self.writes.append(("attach_data_description", element_guid, collection_guid))
        return self._link("DataDescription", element_guid, collection_guid)

    async def _async_detach_data_description(self, element_guid, collection_guid, body=None):
        self.writes.append(("detach_data_description", element_guid, collection_guid))
        self._unlink("DataDescription", element_guid, collection_guid)

    async def _async_link_report_type_instance(self, report_type_guid, report_guid, body=None):
        self.writes.append(("link_report_type_instance", report_type_guid, report_guid))
        return self._link("ReportTypeInstance", report_type_guid, report_guid)

    async def _async_detach_report_type_instance(self, report_type_guid, report_guid, body=None,
                                                 cascade_delete=False):
        self.writes.append(("detach_report_type_instance", report_type_guid, report_guid))
        self._unlink("ReportTypeInstance", report_type_guid, report_guid)


# The 12 Perspective:: elements Trellis creates (checked live, read only, 2026-11-09).
TRELLIS_PERSPECTIVES = ["Financial", "Privacy", "Governance", "App/AI Builder", "Data Expert", "Architecture",
                        "Owner", "Community", "Consumer", "Administration", "Security", "Steward"]


def seed_perspectives(fake: FakeEgeria) -> None:
    for name in TRELLIS_PERSPECTIVES:
        fake.add_entity("Perspective", f"Perspective::{name}", f"{name.upper()}-PERSPECTIVE")


def load_fake():
    """Import this module by path (micro-tests is not an importable package name)."""
    spec = importlib.util.spec_from_file_location("dashboard_fake_egeria", pathlib.Path(__file__))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
