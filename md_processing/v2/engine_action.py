"""
Engine Action Processor for Dr.Egeria v2.

Handles `Initiate Engine Action` and `Cancel Engine Action` -- ad-hoc runtime
requests against a governance engine, distinct from the design-time
Governance Action Process/Type/Step definitions the rest of the Action
Author family manages (see egeria-project.org/concepts/engine-action).

Both commands call pyegeria's `AutomatedCuration` client directly
(`initiate_engine_action` / `cancel_engine_action`) rather than going through
the generic AssetMaker/Referenceable create path: `initiate_engine_action`'s
request body (qualifiedName/domainIdentifier/requestSourceGUIDs/
actionTargets/receivedGuards/requestType/requestParameters/processName/...)
is its own bespoke shape (`GovernanceActionRequestBody`), not a
NewElementRequestBody-wrapped Properties object, and the element it creates
is populated entirely server-side as the engine runs -- there is nothing to
declare beyond the initiation request itself. `cancel_engine_action` takes
only the target engine action's own GUID.

Both are `fetch_as_is -> None` action commands (same shape as
CurationLinkProcessor) -- neither "initiate" nor "cancel" is a create-or-
update-by-qualified-name operation the base class's fuzzy-duplicate-name
transition logic is meant for, so apply_changes always performs its action
directly rather than branching on self.command.verb's Create/Update rewrite.
pyegeria's own initiate_engine_action already appends a start-time
timestamp to whatever qualified_name it's given, so true uniqueness in
Egeria is guaranteed regardless of what the framework derives.
"""
from typing import Any, Dict, List, Optional

from loguru import logger

from md_processing.v2.processors import AsyncBaseCommandProcessor


def _v(attributes: Dict[str, Any], name: str, default=None):
    return attributes.get(name, {}).get("value", default)


def _guid(attributes: Dict[str, Any], name: str) -> Optional[str]:
    return attributes.get(name, {}).get("guid")


def _guid_list(attributes: Dict[str, Any], name: str) -> List[str]:
    """Reference Name List style attribute -> list of resolved guids, skipping
    any entries the framework couldn't resolve to a real element. The base
    processor's generic reference-resolution pass (processors.py) stores
    these under 'guid_list', not 'guid' (singular, for Reference Name)."""
    entry = attributes.get(name, {})
    guid_list = entry.get("guid_list")
    if isinstance(guid_list, list):
        return [g for g in guid_list if g and not str(g).startswith("(Planned:")]
    return []


class InitiateEngineActionProcessor(AsyncBaseCommandProcessor):
    """Processor for Initiate Engine Action."""

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output.get("qualified_name") or self.derive_qualified_name(attributes)
        display_name = _v(attributes, "Display Name") or qualified_name
        description = _v(attributes, "Description")

        domain_identifier_raw = _v(attributes, "Domain Identifier")
        try:
            domain_identifier = int(domain_identifier_raw) if domain_identifier_raw not in (None, "", "All Domains") else 0
        except (TypeError, ValueError):
            domain_identifier = 0

        action_target_guids = _guid_list(attributes, "Action Target Elements")
        action_targets = [
            {"class": "NewActionTarget", "actionTargetName": "actionTarget", "actionTargetGUID": g}
            for g in action_target_guids
        ]
        request_source_guids = _guid_list(attributes, "Request Source Elements")
        received_guards = _v(attributes, "Received Guards") or []
        if isinstance(received_guards, str):
            received_guards = [g.strip() for g in received_guards.split(",") if g.strip()]

        governance_engine_name = _v(attributes, "Governance Engine Name")
        if not governance_engine_name:
            raise ValueError("Governance Engine Name is required.")

        guid = await self.client._async_initiate_engine_action(
            governance_engine_name=governance_engine_name,
            qualified_name=qualified_name,
            domain_identifier=domain_identifier,
            display_name=display_name,
            description=description,
            request_source_guids=request_source_guids,
            action_targets=action_targets,
            received_guards=received_guards,
            request_type=_v(attributes, "Request Type"),
            request_parameters=_v(attributes, "Request Parameters"),
            process_name=_v(attributes, "Process Name"),
        )

        self.parsed_output["guid"] = guid
        logger.success(f"Initiated Engine Action '{display_name}' with GUID {guid}")
        return await self.render_result_markdown(guid)


class CancelEngineActionProcessor(AsyncBaseCommandProcessor):
    """Processor for Cancel Engine Action."""

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        engine_action_guid = _guid(attributes, "Engine Action")
        if not engine_action_guid:
            raise ValueError("Engine Action could not be resolved to an existing element -- check the name/GUID.")

        await self.client._async_cancel_engine_action(engine_action_guid)

        self.parsed_output["guid"] = engine_action_guid
        logger.success(f"Cancelled Engine Action with GUID {engine_action_guid}")
        return await self.render_result_markdown(engine_action_guid)
