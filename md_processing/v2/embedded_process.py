"""
Embedded Process Processor for Dr.Egeria v2.

Handles `Create Embedded Process` (and its Update transition) -- persists a
real Egeria `EmbeddedProcess` asset (EmbeddedProcess -> ActionProperties ->
ProcessProperties -> Asset -> Referenceable; see egeria-project.org/types/2/
0215-Software-Components and .../4/0463-Engine-Actions for the surrounding
Action model) documenting a child process running under the control of
another process -- e.g. one step of a larger pipeline, kept for lineage/
audit purposes distinct from the runtime EngineAction record Egeria's own
governance engines create automatically when they execute (see
engine_action.py).

No dedicated OMVS wrapper exists for EmbeddedProcess (it isn't a Collection
or Project subtype, so the generic COLLECTION_SUBTYPES/PROJECT_SUBTYPES
dispatcher fallback doesn't apply). EmbeddedProcess *is* an Asset subtype, so
this uses AssetMaker's generic asset endpoints (`_async_create_asset` /
`_async_update_asset`) exactly like report.py's ReportProcessor -- see that
module's docstring for why the generic endpoint is required here (Referenceable
elements need the flat NewElementRequestBody shape AssetMaker accepts, not
MetadataExpert's verbose typed ElementProperties/propertyValueMap shape).
"""
from typing import Any, Dict

from loguru import logger

from md_processing.v2.processors import AsyncBaseCommandProcessor
from md_processing.md_processing_utils.common_md_utils import (
    set_create_body, set_element_prop_body, update_element_dictionary,
)


def _embedded_process_extra_properties(attributes: Dict[str, Any]) -> Dict[str, Any]:
    """The ProcessProperties/ActionProperties fields set_element_prop_body's generic
    Referenceable-only shape doesn't cover -- see ProcessProperties.java (formula/
    formulaType/priority) and ActionProperties.java (situation isn't exposed here,
    see the compact command's description for why)."""
    extra: Dict[str, Any] = {}
    formula = attributes.get("Formula", {}).get("value")
    if formula:
        extra["formula"] = formula
    formula_type = attributes.get("Formula Type", {}).get("value")
    if formula_type:
        extra["formulaType"] = formula_type
    expected_behaviour = attributes.get("Expected Behaviour", {}).get("value")
    if expected_behaviour:
        extra["expectedBehaviour"] = expected_behaviour
    priority = attributes.get("Priority", {}).get("value")
    if priority is not None and priority != "":
        extra["priority"] = priority
    return extra


class EmbeddedProcessProcessor(AsyncBaseCommandProcessor):
    """Processor for Create Embedded Process (and its Update transition)."""

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output.get("qualified_name") or self.derive_qualified_name(attributes)
        display_name = attributes.get("Display Name", {}).get("value") or qualified_name

        props = set_element_prop_body("Embedded Process", qualified_name, attributes)
        props["class"] = "EmbeddedProcessProperties"
        props["typeName"] = "EmbeddedProcess"
        props.update(_embedded_process_extra_properties(attributes))

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
            create_body = set_create_body("Embedded Process", attributes)
            create_body["properties"] = props
            guid = await self.client._async_create_asset(["EmbeddedProcessProperties"], create_body)
            verb_word = "Created"

        self.parsed_output["guid"] = guid
        update_element_dictionary(qualified_name, {"guid": guid, "display_name": display_name})

        logger.success(f"{verb_word} Embedded Process '{display_name}' with GUID {guid}")
        return await self.render_result_markdown(guid)
