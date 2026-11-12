"""
Report Processor for Dr.Egeria v2.

Handles `Create Report` (and its Update transition) -- persists a real
Egeria `Report` asset (DataSet -> Asset -> Referenceable; see
odpi/egeria-project.ai/types/2/0239-Reports) carrying a Report Spec
reference plus optional default execution parameters (Output Format,
Search String, and the rest of the same 22-attribute vocabulary
`View Report` already supports ad-hoc). Egeria 6.3 (odpi/egeria#9432) gives
Report a typed `outputFormat`, one `reportParameters` JSON document and the
`ReportTypeInstance` link from its spec; all three are written. The older
`additionalProperties` keys are still written for one release, because
today's Portal reads them. `Link Report to Dashboard Sheet` then references a
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

from pyegeria.core._exceptions import PyegeriaNotFoundException

from md_processing.v2.additional_properties import (
    AdditionalPropertiesUnreadable, merge_additional_properties, stored_additional_properties, unreadable_message,
)
from md_processing.v2.processors import AsyncBaseCommandProcessor
from md_processing.md_processing_utils.common_md_utils import (
    set_create_body, set_element_prop_body, update_element_dictionary,
)

# Report specs are held in Egeria under two qualified-name prefixes (pipeline note v5.5 §7a hazard):
# `ReportSpec::` from Create Report Spec, and `ReportType::` from the older report-type content.
REPORT_SPEC_QN_PREFIXES = ("ReportSpec::", "ReportType::")

# `Report Spec` / `Output Format` have typed homes; everything else in _REPORT_PARAM_ATTRS goes into the
# one reportParameters document.
_TYPED_REPORT_KEYS = {"reportSpec", "outputFormat"}

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


def _coerce_analytic_value(v: Any) -> Any:
    """Recover a value's real type before it's packed into the analyticParams
    JSON blob. parse_key_value() (md_processing/v2/utils.py) always produces
    plain strings, even for values the user typed as a JSON list/dict (e.g.
    `type_map: [["Projects", "Project"], ["Terms", "GlossaryTerm"]]`) or a
    number/bool (e.g. `points: 12`). Left as a bare str(), a value like that
    gets double-encoded -- the outer analyticParams JSON is valid, but a key's
    *value* is itself the literal string "[[...]]" or "12", not a real
    list/int -- so it comes back out via json.loads(raw_analytic_params) at
    execution time still a str, and the analytic function breaks trying to
    use it as its real type (`counts_by_type(type_map="[[...]]")` -> "not
    enough values to unpack"; `growth_series(points="3")` -> "unsupported
    operand type(s) for -: 'str' and 'int'"). Both confirmed live 2026-07-31
    (PYEGERIA_ISSUES.md ISSUE-20).

    Only applied here, not to the other additionalProperties keys in this
    module (_REPORT_PARAM_ATTRS, Report Parameters, Additional Properties) --
    those are genuinely Map<String,String> at the Egeria element level and
    must stay strings; analyticParams is a single JSON-encoded blob consumed
    purely by Python's own **kwargs at execution time, where real types
    matter and there's no Egeria-side string constraint to honor.
    """
    if not isinstance(v, str):
        return v
    try:
        return json.loads(v)
    except (ValueError, TypeError):
        # Not valid JSON (e.g. "Project", "6mo", "GlossaryTerm") -- it really
        # is meant to be a plain string; keep it as-is.
        return v


def _snake_to_camel(snake: str) -> str:
    """snake_case -> camelCase, the exact functional inverse of
    local-dashboards.html's JS snakeKey() (which does the reverse for
    display/execution) -- keep the two in sync if either changes."""
    parts = snake.split("_")
    return parts[0] + "".join(p[:1].upper() + p[1:] for p in parts[1:] if p)


def _camel_to_snake(camel: str) -> str:
    """camelCase -> snake_case (`searchString` -> `search_string`, `asOfTime` -> `as_of_time`)."""
    out = []
    for ch in camel:
        if ch.isupper():
            out.append("_" + ch.lower())
        else:
            out.append(ch)
    return "".join(out).lstrip("_")


def report_parameters_document(attributes: Dict[str, Any]) -> Dict[str, Any]:
    """The one parameter document a Report carries in Egeria 6.3's `reportParameters` (pipeline note §8d).

    Today's `Create Report` holds parameters three ways; they collapse into one JSON object of snake_case
    parameter names, which is what a spec's declared `required_params`/`optional_params` use:
      1. the common find attributes (`Search String`, `Page Size`, ...), authoring sugar;
      2. the `Report Parameters` map, as typed;
      3. the `Analytic Parameters` map.
    Later sources win on a clash. Attribute defaults the parser fills in (`Graph Query Depth`, ...) are not
    written: only what the author wrote is pinned. Values that are JSON (`25`, `true`, `[...]`) are decoded, so `Page Size 25`
    is the number 25, not the string "25". `Report Spec` and `Output Format` are not parameters: they have
    their own typed homes (`ReportTypeInstance`, `outputFormat`).
    """
    doc: Dict[str, Any] = {}
    for canonical_name, key in _REPORT_PARAM_ATTRS.items():
        if key in _TYPED_REPORT_KEYS:
            continue
        attr = attributes.get(canonical_name, {})
        if attr.get("is_default"):
            continue  # a spec default the author did not write: the report spec decides, not a pinned value
        value = attr.get("value")
        if value is not None and value != "":
            doc[_camel_to_snake(key)] = _coerce_analytic_value(value)
    for attr in ("Report Parameters", "Analytic Parameters"):
        value = attributes.get(attr, {}).get("value")
        if isinstance(value, dict):
            doc.update({str(k): _coerce_analytic_value(v) for k, v in value.items() if v is not None})
    return doc


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
            {str(k): _coerce_analytic_value(v) for k, v in analytic_params.items() if v is not None}
        )
    return merged


def _as_element(result: Any) -> Optional[Dict[str, Any]]:
    """An element dict from a lookup, or None for any not-found answer (a string, an empty list, None)."""
    if isinstance(result, dict) and result.get("elementHeader"):
        return result
    if isinstance(result, dict) and isinstance(result.get("element"), dict):
        return result["element"]
    return None


async def find_element_by_qualified_name(client: Any, qualified_name: str) -> Optional[Dict[str, Any]]:
    """One bounded exact lookup by qualifiedName (classification-explorer `by-unique-name`). None if absent.

    Never a type-wide query: the unique-name endpoint returns at most one element.
    """
    if not qualified_name:
        return None
    try:
        result = await client.classification_manager._async_get_element_by_unique_name(qualified_name)
    except PyegeriaNotFoundException:
        return None
    return _as_element(result)


async def find_report_spec_element(client: Any, spec_name: str) -> Optional[Dict[str, Any]]:
    """The Egeria element for a report spec named `spec_name`, looked up under both prefixes.

    Tries the name as a qualified name first (a caller may give `ReportSpec::X` or `ReportType::X`), then
    `ReportSpec::<name>`, then `ReportType::<name>` (§7a hazard: both exist live). None if no element holds
    the spec -- a spec held only in pyegeria has none.
    """
    if not spec_name:
        return None
    candidates = [spec_name] if spec_name.startswith(REPORT_SPEC_QN_PREFIXES) else []
    candidates += [f"{prefix}{spec_name}" for prefix in REPORT_SPEC_QN_PREFIXES]
    for qn in candidates:
        element = await find_element_by_qualified_name(client, qn)
        if element:
            return element
    return None


def _props_differ(desired: Dict[str, Any], current: Dict[str, Any]) -> bool:
    """True if any non-None desired property differs from the element's current value."""
    for key, value in desired.items():
        if key in ("class", "typeName") or value is None:
            continue
        if key == "additionalProperties" and isinstance(value, dict):
            # merged key by key on update, so only the keys given count (additional_properties.py)
            stored = current.get(key) or {}
            if any(stored.get(k) != v for k, v in value.items()):
                return True
            continue
        if current.get(key) != value:
            return True
    return False


async def upsert_dashboard_asset(client: Any, qualified_name: str, props: Dict[str, Any],
                                 existing: Optional[Dict[str, Any]], *, merge_update: bool = True,
                                 create_body: Optional[Dict[str, Any]] = None,
                                 filter_update: Any = None) -> tuple:
    """Create or update an Egeria 6.3 `Dashboard` asset. Returns (guid, verb_word, body_sent).

    The one implementation of the Dashboard asset write, used by `Create Dashboard` (DashboardProcessor)
    and by `Create Dashboard Sheet` / dashboard migration (dashboard_sheet.py). An existing Dashboard whose
    properties already match is left alone (verb_word "Unchanged", nothing sent), so re-running a document
    changes nothing.
    """
    if existing:
        guid = existing["elementHeader"]["guid"]
        if not _props_differ(props, existing.get("properties") or {}):
            return guid, "Unchanged", None
        update_props = filter_update(props, merge_update) if filter_update else props
        stored = stored_additional_properties(existing)
        if merge_update and update_props.get("additionalProperties") is not None:
            # Egeria replaces the map whole: send the stored keys too (md_processing/v2/additional_properties.py).
            if stored is None:
                raise AdditionalPropertiesUnreadable(unreadable_message(f"Dashboard '{qualified_name}'"))
            update_props = {**update_props, "additionalProperties": merge_additional_properties(
                stored, update_props["additionalProperties"])}
        update_body = {"class": "UpdateElementRequestBody", "properties": update_props,
                       "mergeUpdate": merge_update}
        await client._async_update_asset(guid, update_body)
        return guid, "Updated", update_body
    body = dict(create_body or {"class": "NewElementRequestBody"})
    body["properties"] = props
    raw_guid = await client._async_create_asset(["DashboardProperties"], body)
    return raw_guid, "Created", body


async def sync_report_type_instance(client: Any, report_guid: str, spec_name: str) -> Optional[str]:
    """Link the Report to its spec's element by `ReportTypeInstance`; return a note when that cannot be done.

    - Spec element found (under `ReportSpec::` or `ReportType::`): link it if not already linked, and detach
      links to any other report type (a report runs one spec).
    - No element (a spec held only in pyegeria): nothing is written, and the note says so -- the report
      still runs from pyegeria's own spec registry.
    """
    spec_element = await find_report_spec_element(client, spec_name)
    if not spec_element:
        return (f"Report Spec '{spec_name}' has no Egeria element (looked for "
                f"{' and '.join(p + spec_name for p in REPORT_SPEC_QN_PREFIXES)}): no ReportTypeInstance was "
                f"written. The report still runs from pyegeria's own spec.")
    spec_guid = spec_element["elementHeader"]["guid"]
    current = await client.classification_manager._async_get_related_elements(
        report_guid, "ReportTypeInstance", start_at_end=2, page_size=25, graph_query_depth=0)
    linked = [e["elementHeader"]["guid"] for e in (current if isinstance(current, list) else [])
              if isinstance(e, dict) and e.get("elementHeader")]
    for other in linked:
        if other != spec_guid:
            await client.data_designer._async_detach_report_type_instance(other, report_guid)
    if spec_guid not in linked:
        await client.data_designer._async_link_report_type_instance(spec_guid, report_guid)
    return None


class ReportProcessor(AsyncBaseCommandProcessor):
    """Processor for Create Report (and its Update transition).

    Egeria 6.3 (odpi/egeria#9432) writes, beside the additionalProperties keys today's Portal reads (kept
    for one release):
      - `reportParameters`: ONE JSON document (report_parameters_document), not three parameter homes;
      - the typed `outputFormat`;
      - `ReportTypeInstance` from the named spec's element, found under `ReportSpec::` or `ReportType::`;
        a spec with no element gets a note saying no link was written, not silence.
    """

    # The report parameters are additionalProperties keys, so every update sends the map: the base
    # processor merges the stored keys in first (_prepare_additional_properties).
    WRITES_ADDITIONAL_PROPERTIES = True

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output.get("qualified_name") or self.derive_qualified_name(attributes)
        display_name = attributes.get("Display Name", {}).get("value") or qualified_name

        spec_name = attributes.get("Report Spec", {}).get("value")
        if not spec_name:
            raise ValueError("Report Spec is required.")

        props = set_element_prop_body("Report", qualified_name, attributes)
        props["additionalProperties"] = _report_additional_properties(attributes)
        props["outputFormat"] = attributes.get("Output Format", {}).get("value")
        parameters = report_parameters_document(attributes)
        if parameters:
            props["reportParameters"] = json.dumps(parameters, sort_keys=True)
        props["deployedImplementationType"] = attributes.get("Deployed Implementation Type", {}).get("value")
        props["resourceName"] = attributes.get("Resource Name", {}).get("value")

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

        note = await sync_report_type_instance(self.client, guid, spec_name)
        if note:
            self._add_warning(note)

        logger.success(f"{verb_word} Report '{display_name}' with GUID {guid}")
        result = await self.render_result_markdown(guid)
        return f"{result}\n\n> {note}\n" if note else result


class DashboardProcessor(AsyncBaseCommandProcessor):
    """Processor for Create Dashboard (and its Update transition): an Egeria 6.3 `Dashboard` asset
    (DataSet subtype, sibling of Report; odpi/egeria#9432). Same AssetMaker path as ReportProcessor.

    Its sheets and placements are DisplayDataContainers / DisplayDataFields (Schema Maker family);
    Egeria has no separate DashboardPlacement type. The asset write itself is `upsert_dashboard_asset`,
    which `Create Dashboard Sheet` (dashboard_sheet.py) also uses for its Dashboard.
    """

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output.get("qualified_name") or self.derive_qualified_name(attributes)
        display_name = attributes.get("Display Name", {}).get("value") or qualified_name

        props = set_element_prop_body("Dashboard", qualified_name, attributes)
        props["deployedImplementationType"] = attributes.get("Deployed Implementation Type", {}).get("value")
        props["resourceName"] = attributes.get("Resource Name", {}).get("value")
        props["aliases"] = attributes.get("Aliases", {}).get("value")
        # refreshTimeInterval is a long, in minutes (Egeria's REFRESH_TIME_INTERVAL property).
        props["refreshTimeInterval"] = attributes.get("Refresh Time Interval", {}).get("value")
        props["layoutStyle"] = attributes.get("Layout Style", {}).get("value")

        guid, verb_word, body = await upsert_dashboard_asset(
            self.client, qualified_name, props, self.as_is_element,
            merge_update=attributes.get("Merge Update", {}).get("value", True),
            create_body=set_create_body("Dashboard", attributes),
            filter_update=self.filter_update_properties)
        if body is not None:
            self.last_body = body
        if verb_word == "Created":
            guid = self.extract_guid_or_raise(guid, "Create Dashboard")

        self.parsed_output["guid"] = guid
        update_element_dictionary(qualified_name, {"guid": guid, "display_name": display_name})

        logger.success(f"{verb_word} Dashboard '{display_name}' with GUID {guid}")
        return await self.render_result_markdown(guid)
