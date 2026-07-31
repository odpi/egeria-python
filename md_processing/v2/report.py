"""
Report Processor for Dr.Egeria v2.

Handles `Create Report` (and its Update transition) -- persists a real
Egeria `Report` asset (DataSet -> Asset -> Referenceable; see
odpi/egeria-project.ai/types/2/0239-Reports) carrying a Report Spec
reference plus optional default execution parameters (Output Format,
Search String, and the rest of the same 22-attribute vocabulary
`View Report` already supports ad-hoc). Short-term design: everything
beyond the base Referenceable properties lands in `additionalProperties`
-- no dedicated `ReportDefinition` subtype yet (see egeria-workspaces-fs
BACKLOG.md NEXT-14). `Link Report to Dashboard Sheet` then references a
Report by its `Report Name` instead of a bare Report Spec name, giving a
Dashboard Sheet placement a concrete, parameterized instance to run
instead of an unparameterized template.

No dedicated OMVS wrapper exists for `Report` (it isn't a Collection or
Project subtype, so the generic COLLECTION_SUBTYPES/PROJECT_SUBTYPES
dispatcher fallback doesn't apply either). Report *is* an Asset subtype
(Report -> DataSet -> Asset -> Referenceable), so this uses AssetMaker's
generic asset endpoints (`_async_create_asset` / `_async_update_asset`,
`asset-maker/assets`) rather than MetadataExpert's raw metadata-store
endpoint -- verified live: MetadataExpert's `_async_create_metadata_element`
expects the verbose typed `ElementProperties`/`propertyValueMap` body shape
(confirmed against a real 400 error -- "qualifiedName parameter ... is
null" when passed the same flat properties dict `set_element_prop_body`
produces), whereas AssetMaker's `NewElementRequestBody`-based endpoint
accepts flat properties directly, matching every other processor in this
codebase (`set_create_body`/`set_element_prop_body` -> a bespoke `_async_create_*`
call). Both subclients are available transparently via `self.client`
(EgeriaTech proxies to instantiated subclients via `__getattr__`).
"""
import json
from typing import Any, Dict, Optional

from loguru import logger

from md_processing.v2.processors import AsyncBaseCommandProcessor
from md_processing.md_processing_utils.common_md_utils import (
    set_create_body, set_element_prop_body, update_element_dictionary,
)

# The 22 report-execution-parameter attributes (same set View Report exposes
# ad-hoc) -- short-term, all of these land in additionalProperties rather
# than typed Report fields. camelCase keys distinguish them from anything a
# user puts in their own "Additional Properties" dict.
_REPORT_PARAM_ATTRS = {
    "Report Spec": "reportSpec",
    "Output Format": "outputFormat",
    "Search String": "searchString",
    "Starts With": "startsWith",
    "Ends With": "endsWith",
    "Ignore Case": "ignoreCase",
    "Limit Result by Status": "limitResultByStatus",
    "Metadata Element Type Name": "metadataElementTypeName",
    "Metadata Element Subtype Names": "metadataElementSubtypeNames",
    "Skip Relationships": "skipRelationships",
    "Include Only Relationships": "includeOnlyRelationships",
    "Skip Classified Elements": "skipClassifiedElements",
    "Include Only Classified Elements": "includeOnlyClassifiedElements",
    "Governance Zone Filter": "governanceZoneFilter",
    "Graph Query Depth": "graphQueryDepth",
    "Effective Time": "effectiveTime",
    "AsOfTime": "asOfTime",
    "Output Sort Order": "outputSortOrder",
    "Order Property Name": "orderPropertyName",
    "Page Size": "pageSize",
    "Start From": "startFrom",
    "Anchor Scope ID": "anchorScopeId",
}


def _snake_to_camel(snake: str) -> str:
    """snake_case -> camelCase, the exact functional inverse of
    local-dashboards.html's JS snakeKey() (which does the reverse for
    display/execution) -- keep the two in sync if either changes."""
    parts = snake.split("_")
    return parts[0] + "".join(p[:1].upper() + p[1:] for p in parts[1:] if p)


def _report_additional_properties(attributes: Dict[str, Any]) -> Dict[str, str]:
    """Merge the user's own 'Additional Properties' dict (if any) with the
    report-execution params, stringified (additionalProperties is
    Map<String,String> in the Egeria type model)."""
    merged: Dict[str, str] = {}
    user_extra = attributes.get("Additional Properties", {}).get("value")
    if isinstance(user_extra, dict):
        merged.update({str(k): str(v) for k, v in user_extra.items() if v is not None})

    # Arbitrary report-spec-specific params (e.g. {"collection_guid": "..."}
    # for the "Collection Members" report) that aren't part of the standard
    # 22-key find/search vocabulary in _REPORT_PARAM_ATTRS. Merged FLAT
    # (unlike analyticParams below, which is JSON-encoded under its own key)
    # because the consumption side (egeria-workspaces-fs's
    # local_dashboards_handler.py:_find_report_by_name) already passes
    # through any additionalProperties key not in
    # {"reportSpec","outputFormat","analyticParams"} as a flat params dict.
    #
    # Stored camelCase (like every _REPORT_PARAM_ATTRS key), NOT the raw
    # snake_case the user typed in the Dr.Egeria markdown -- found live
    # 2026-07-31: local-dashboards.html's camelKey()/snakeKey() round-trip
    # (its own comment: "additionalProperties uses camelCase keys... matches
    # ReportProcessor's _REPORT_PARAM_ATTRS") assumes EVERY additionalProperties
    # key is camelCase and converts accordingly when checking
    # `required_params` are present and when building the execute-time params
    # dict. Storing collection_guid unconverted made camelKey('collection_guid')
    # -> 'collectionGuid' not match the stored 'collection_guid' key, so the
    # placement reported it as missing even though it was set. Converting here
    # (rather than changing local-dashboards.html to special-case Report
    # Parameters) keeps additionalProperties internally consistent -- one
    # convention for every key, not two -- and needs no JS change, since the
    # existing round-trip already un-camelCases correctly before the final
    # /api/report-specs/execute call (format_set_executor.py's params[key]
    # lookup there still sees the original snake_case name the report spec's
    # required_params/optional_params expect).
    report_params = attributes.get("Report Parameters", {}).get("value")
    if isinstance(report_params, dict):
        merged.update({_snake_to_camel(str(k)): str(v) for k, v in report_params.items() if v is not None})

    for canonical_name, key in _REPORT_PARAM_ATTRS.items():
        value = attributes.get(canonical_name, {}).get("value")
        if value is not None and value != "":
            merged[key] = value if isinstance(value, str) else str(value)

    # Arbitrary parameters for a report spec's analytic_function (extra_find)
    # -- e.g. {"window": "90d", "points": "12"} for a growth_series-backed
    # spec. Kept under its own distinct key rather than merged flat into the
    # 22 find-oriented keys above, so a consumer can tell "analytic params"
    # from "find params" unambiguously without guessing by key name. No
    # fixed set of expected keys here by design -- see ActionParameter's
    # docstring in _output_format_models.py.
    analytic_params = attributes.get("Analytic Parameters", {}).get("value")
    if isinstance(analytic_params, dict) and analytic_params:
        merged["analyticParams"] = json.dumps(
            {str(k): str(v) for k, v in analytic_params.items() if v is not None}
        )
    return merged


class ReportProcessor(AsyncBaseCommandProcessor):
    """Processor for Create Report (and its Update transition)."""

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output.get("qualified_name") or self.derive_qualified_name(attributes)
        display_name = attributes.get("Display Name", {}).get("value") or qualified_name

        if not attributes.get("Report Spec", {}).get("value"):
            raise ValueError("Report Spec is required.")

        props = set_element_prop_body("Report", qualified_name, attributes)
        props["additionalProperties"] = _report_additional_properties(attributes)

        if self.as_is_element:
            guid = self.as_is_element["elementHeader"]["guid"]
            update_body = {
                "class": "UpdateElementRequestBody",
                "properties": props,
                "mergeUpdate": attributes.get("Merge Update", {}).get("value", True),
            }
            await self.client._async_update_asset(guid, update_body)
            verb_word = "Updated"
        else:
            create_body = set_create_body("Report", attributes)
            create_body["properties"] = props
            guid = await self.client._async_create_asset(["ReportProperties"], create_body)
            verb_word = "Created"

        self.parsed_output["guid"] = guid
        update_element_dictionary(qualified_name, {"guid": guid, "display_name": display_name})

        logger.success(f"{verb_word} Report '{display_name}' with GUID {guid}")
        return await self.render_result_markdown(guid)
