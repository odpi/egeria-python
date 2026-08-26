"""
Saved Query Processor for Dr.Egeria v2.

Handles `Create Saved Query` (and its Update transition) -- persists a real
Egeria `SavedQuery` asset (DataSet -> Asset -> Referenceable; Egeria PR
#9200, 0725 Smart Collections: https://egeria-project.org/types/7/0725-Smart-Collections/)
carrying the REST URL + request body of a saved query, so a `ResultsSet`
collection can later be linked to it via the `SmartQuery` relationship
(see `Link Saved Query to Results Set` below).

No dedicated OMVS wrapper exists for `SavedQuery` -- same situation as
`Report` (see `md_processing/v2/report.py`'s module docstring for the full
rationale). `SavedQuery` is a `DataSet` -> `Asset` subtype, so this uses
`AssetMaker`'s generic asset endpoints (`_async_create_asset`/
`_async_update_asset`) exactly like `ReportProcessor` does.

Only `queryURL`/`queryRequestBody` are set as typed properties -- confirmed
against the current Egeria source (`SavedQueryProperties.java`) that
`queryType` has no field on this bean at all (it's a pre-existing,
unrelated `OpenMetadataProperty` used elsewhere), so a `Query Type`
Dr.Egeria attribute was deliberately NOT added; setting it would silently
be a no-op.

Live-verified 2026-08-09 against qs-view-server: `SavedQuery` creation
itself round-trips correctly (typeName, qualifiedName, displayName,
description). `queryURL`/`queryRequestBody` did NOT round-trip on that
server build -- traced to a deployed-binary lag behind the local `egeria`
source checkout (PR #9201 "Complete OMF Bean Implementation" adds the
builder/converter code that reads/writes these two fields, and that code
*is* present in source at the checkout's HEAD) -- expected to resolve once
that server is rebuilt; re-verify then (see PYEGERIA_ISSUES.md and project
memory for the tracking note).
"""
from typing import Any, Dict

from loguru import logger

from md_processing.v2.processors import AsyncBaseCommandProcessor
from md_processing.md_processing_utils.common_md_utils import (
    set_create_body, set_element_prop_body, update_element_dictionary,
)


class SavedQueryProcessor(AsyncBaseCommandProcessor):
    """Processor for Create Saved Query (and its Update transition)."""

    async def apply_changes(self) -> str:
        attributes: Dict[str, Any] = self.parsed_output["attributes"]
        qualified_name = self.parsed_output.get("qualified_name") or self.derive_qualified_name(attributes)
        display_name = attributes.get("Display Name", {}).get("value") or qualified_name

        props = set_element_prop_body("SavedQuery", qualified_name, attributes)
        props["queryURL"] = attributes.get("Query URL", {}).get("value")
        props["queryRequestBody"] = attributes.get("Query Request Body", {}).get("value")

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
            create_body = set_create_body("SavedQuery", attributes)
            create_body["properties"] = props
            guid = await self.client._async_create_asset(["SavedQueryProperties"], create_body)
            verb_word = "Created"

        self.parsed_output["guid"] = guid
        update_element_dictionary(qualified_name, {"guid": guid, "display_name": display_name})

        logger.success(f"{verb_word} Saved Query '{display_name}' with GUID {guid}")
        return await self.render_result_markdown(guid)


class SmartQueryLinkProcessor(AsyncBaseCommandProcessor):
    """Processor for `Link Saved Query to Results Set` (OM_TYPE: SmartQuery).

    Connects an existing `SavedQuery` to an existing `ResultsSet` via the
    generic `CollectionManager._async_link_saved_query_to_results_set`/
    `_async_detach_saved_query_from_results_set` methods (added for this
    purpose -- SmartQuery has no bespoke view-service endpoint, see
    `pyegeria/omvs/collection_manager.py`).
    """

    async def fetch_as_is(self):
        return None

    async def apply_changes(self) -> str:
        attributes: Dict[str, Any] = self.parsed_output["attributes"]
        verb = self.command.verb
        results_set_guid = attributes.get("Results Set", {}).get("guid")
        saved_query_guid = attributes.get("Saved Query", {}).get("guid")
        if not results_set_guid:
            raise ValueError("Results Set could not be resolved to a GUID.")
        if not saved_query_guid:
            raise ValueError("Saved Query could not be resolved to a GUID.")

        if verb in ("Link", "Attach", "Add"):
            relationship_guid = await self.client.collection_manager._async_link_saved_query_to_results_set(
                results_set_guid, saved_query_guid)
            logger.success(f"Linked Saved Query {saved_query_guid} to Results Set {results_set_guid} "
                            f"via SmartQuery relationship {relationship_guid}")
            return f"\n\n## {verb} Saved Query to Results Set\n\nLinked {saved_query_guid} to {results_set_guid}."
        else:
            found = await self.client.metadata_expert._async_find_relationships_between_elements(
                {
                    "class": "FindRelationshipRequestBody",
                    "relationshipTypeName": "SmartQuery",
                }
            )
            relationship_guid = None
            for rel in (found if isinstance(found, list) else []):
                if not isinstance(rel, dict):
                    continue
                end1 = rel.get("elementGUIDAtEnd1")
                end2 = rel.get("elementGUIDAtEnd2")
                if end1 == results_set_guid and end2 == saved_query_guid:
                    relationship_guid = rel.get("relationshipGUID")
                    break
            if not relationship_guid:
                raise ValueError(
                    f"No SmartQuery relationship found between Results Set {results_set_guid} "
                    f"and Saved Query {saved_query_guid} to unlink."
                )
            await self.client.collection_manager._async_detach_saved_query_from_results_set(relationship_guid)
            logger.success(f"Detached SmartQuery relationship {relationship_guid}")
            return f"\n\n## {verb} Saved Query to Results Set\n\nUnlinked {saved_query_guid} from {results_set_guid}."
