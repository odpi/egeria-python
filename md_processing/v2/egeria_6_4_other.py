# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Dr.Egeria commands for the rest of the Egeria 6.4 additions (odpi/egeria#9463).

- Link/Detach Project Target (Projects family) -> ProjectManager.setup_project_target / clear_project_target
  (ProjectTarget: Project -> any element, uni-link).
- Link/Detach Supported Variable Type (Schema Maker family) -> SchemaMaker.link_supported_variable_type /
  detach_supported_variable_type (SupportedVariableType: element -> SchemaType, uni-link), with Position (0 means
  unset), Min Cardinality and Max Cardinality, each a whole number.
- Set/Clear Branch (Devops Pipeline family) -> DevopsPipeline.set_element_as_branch / clear_element_as_branch (the
  Branch classification, BranchProperties: displayName, scope, purpose, url; it has no label or description).

Every command is gated on Egeria 6.4 (md_processing.v2.egeria_6_4).
"""
from __future__ import annotations

from typing import Any, Dict, List

from pyegeria.core import egeria_6_4_names as e64
from pyegeria.core.utils import body_slimmer
from md_processing.v2.egeria_6_4 import (
    EMPTY, Egeria64LinkProcessor, delete_relationship_body, int_value, new_relationship_body, value)


class ProjectTargetProcessor(Egeria64LinkProcessor):
    """Link Project Target / Detach Project Target."""

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        project, target = self.ends(attributes, "Project", "Target Element")
        pm = self.client.project_manager
        what = f"{self.command.verb} {self.command.object_type}"
        if self.command.verb in self.DETACH_VERBS:
            body = delete_relationship_body(attributes)
            self.last_body = body
            await self.e64(pm._async_clear_project_target(project, target, body))
            return f"\n\n# {what}\n\nProject {project} no longer targets {target}.\n"
        body = new_relationship_body(e64.PROJECT_TARGET, attributes)
        self.last_body = body
        await self.e64(pm._async_setup_project_target(project, target, body))
        return f"\n\n# {what}\n\nProject {project} now targets {target}.\n"


#: SupportedVariableType attributes and the property each fills (each a whole number).
VARIABLE_TYPE_FIELDS = {"Position": "position", "Min Cardinality": "minCardinality",
                        "Max Cardinality": "maxCardinality"}


class SupportedVariableTypeProcessor(Egeria64LinkProcessor):
    """Link Supported Variable Type / Detach Supported Variable Type."""

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        element, schema_type = self.ends(attributes, "Element", "Schema Type")
        sm = self.client.schema_maker
        what = f"{self.command.verb} {self.command.object_type}"
        if self.command.verb in self.DETACH_VERBS:
            body = delete_relationship_body(attributes)
            self.last_body = body
            await self.e64(sm._async_detach_supported_variable_type(element, schema_type, body))
            return f"\n\n# {what}\n\nDetached schema type {schema_type} from {element}.\n"
        # Only values the document gives are sent (Position's spec default, 0, means unset).
        extra = {key: int_value(attributes, name) for name, key in VARIABLE_TYPE_FIELDS.items()
                 if not (attributes.get(name) or {}).get("is_default")}
        body = new_relationship_body(e64.SUPPORTED_VARIABLE_TYPE, attributes, extra,
                                     {k: n for n, k in VARIABLE_TYPE_FIELDS.items()})
        self.last_body = body
        await self.e64(sm._async_link_supported_variable_type(element, schema_type, body))
        return f"\n\n# {what}\n\nLinked schema type {schema_type} to {element} as a supported variable type.\n"


#: Branch attributes and the BranchProperties key each fills.
BRANCH_FIELDS = {"Display Name": "displayName", "Scope": "scope", "Purpose": "purpose", "URL": "url"}


class BranchProcessor(Egeria64LinkProcessor):
    """Set Branch / Clear Branch (a classification: no element of its own to look up)."""

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        [element] = self.ends(attributes, "Target Element")
        dp = self.client.devops_pipeline
        what = f"{self.command.verb} {self.command.object_type}"
        source = {
            "externalSourceGUID": (attributes.get("External Source GUID") or {}).get("guid"),
            "externalSourceName": value(attributes, "External Source Name"),
            "effectiveTime": value(attributes, "Effective Time"),
            "forLineage": value(attributes, "For Lineage") or False,
            "forDuplicateProcessing": value(attributes, "For Duplicate Processing") or False,
        }
        if self.command.verb == "Clear":
            body = body_slimmer({"class": "MetadataSourceRequestBody", **source})
            self.last_body = body
            await self.e64(dp._async_clear_element_as_branch(element, body))
            return f"\n\n# {what}\n\nRemoved the Branch classification from {element}.\n"
        props = {key: value(attributes, name) for name, key in BRANCH_FIELDS.items()}
        props = {k: v for k, v in props.items() if v not in EMPTY}
        body = body_slimmer({"class": "NewClassificationRequestBody", **source,
                             "properties": {"class": e64.BRANCH_PROPERTIES, **props} if props else None})
        self.last_body = body
        await self.e64(dp._async_set_element_as_branch(element, body))
        return f"\n\n# {what}\n\nClassified {element} as a Branch.\n"


def register_other_6_4_processors(reg) -> List[str]:
    """Register the B3 commands; returns their names."""
    names = {
        "Link Project Target": ProjectTargetProcessor, "Detach Project Target": ProjectTargetProcessor,
        "Link Supported Variable Type": SupportedVariableTypeProcessor,
        "Detach Supported Variable Type": SupportedVariableTypeProcessor,
        "Set Branch": BranchProcessor, "Clear Branch": BranchProcessor,
    }
    for name, cls in names.items():
        reg(name, cls)
    return list(names)
