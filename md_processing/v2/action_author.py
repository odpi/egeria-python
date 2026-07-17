"""
Action Author Processors for Dr.Egeria v2.

Handles the Action Author link commands (Link First Process Step,
Link Next Process Step, Link Action to Action Executor, Link Action
to Target). These don't fit the generic governance peer-link mechanism
(GovernanceLinkProcessor / link_peer_definitions) -- they call the
action_author OMVS client directly, with dedicated relationship
properties (guard/requestParameters/mandatoryGuard,
requestType/requestParameterFilter/requestParameterMap/
actionTargetFilter/actionTargetMap, actionTargetName) that the generic
PeerDefinitionProperties body has no room for.
"""
from typing import Dict, Any, Optional
from loguru import logger

from md_processing.v2.processors import AsyncBaseCommandProcessor
from md_processing.md_processing_utils.common_md_utils import set_rel_request_body, set_delete_rel_request_body
from pyegeria.core.utils import body_slimmer


class ActionProcessStepLinkProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Link First Process Step (GovernanceActionProcessFlow) and
    Link Next Process Step (NextGovernanceActionProcessStep).
    """

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    def _normalize_guid(self, value: Any) -> Optional[str]:
        if not value:
            return None
        if isinstance(value, str):
            if value.startswith("(Planned: "):
                return value
            # Basic GUID regex check
            import re
            if re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', value.lower()):
                return value
        return None

    def _resolve_relationship_guid(self, object_type: str, attributes: Dict[str, Any]) -> Optional[str]:
        guid_sources = [
            self.parsed_output.get("guid") if self.parsed_output else None,
            (attributes.get("GUID") or {}).get("guid"),
            (attributes.get("GUID") or {}).get("value"),
            (attributes.get("Relationship GUID") or {}).get("value"),
        ]

        for raw in guid_sources:
            guid = self._normalize_guid(raw)
            if guid:
                return guid
        return None

    async def apply_changes(self) -> str:
        verb = self.command.verb
        object_type = getattr(self, 'canonical_object_type', self.command.object_type)
        attributes = self.parsed_output["attributes"]
        spec = self.get_command_spec()
        om_type = spec.get("OM_TYPE")

        is_first_step = om_type == "GovernanceActionProcessFlow"

        if is_first_step:
            process_guid = attributes.get('Governance Action Process', {}).get('guid')
            step_guid = attributes.get('Governance Action Process Step', {}).get('guid')
            if not (process_guid and step_guid):
                missing = []
                if not process_guid: missing.append("'Governance Action Process'")
                if not step_guid: missing.append("'Governance Action Process Step'")
                raise ValueError(f"Cannot link process step: resolution failed for {', '.join(missing)}")

            if verb in ["Link", "Attach", "Add"]:
                body = set_rel_request_body(om_type, attributes)
                body["properties"] = {
                    "class": "GovernanceActionProcessFlowProperties",
                    "guard": attributes.get('Guard', {}).get('value'),
                    "requestParameters": attributes.get('Request Parameters', {}).get('value'),
                }
                self.last_body = body = body_slimmer(body)
                await self.client._async_setup_first_action_process_step(process_guid, step_guid, body)
                logger.success(f"Linked {step_guid} as first process step of {process_guid}")
                return f"\n\n## {verb} {object_type}\n\nLinked {step_guid} as first process step of {process_guid}"

            elif verb in ["Detach", "Unlink", "Remove"]:
                await self.client._async_remove_first_action_process_step(process_guid)
                logger.success(f"Removed first-process-step link from {process_guid}")
                return f"\n\n## {verb} {object_type}\n\nRemoved first-process-step link from {process_guid}"

        else:
            step_guid = attributes.get('Governance Action Process Step', {}).get('guid')
            next_step_guid = attributes.get('Next Governance Action Process Step', {}).get('guid')
            if not (step_guid and next_step_guid):
                missing = []
                if not step_guid: missing.append("'Governance Action Process Step'")
                if not next_step_guid: missing.append("'Next Governance Action Process Step'")
                raise ValueError(f"Cannot link next process step: resolution failed for {', '.join(missing)}")

            if verb in ["Link", "Attach", "Add"]:
                body = set_rel_request_body(om_type, attributes)
                body["properties"] = {
                    "class": "NextGovernanceActionProcessStepProperties",
                    "guard": attributes.get('Guard', {}).get('value'),
                    "mandatoryGuard": attributes.get('Mandatory Guard', {}).get('value', False),
                }
                self.last_body = body = body_slimmer(body)
                await self.client._async_setup_next_action_process_step(step_guid, next_step_guid, body)
                logger.success(f"Linked {next_step_guid} as next process step after {step_guid}")
                return f"\n\n## {verb} {object_type}\n\nLinked {next_step_guid} as next process step after {step_guid}"

            elif verb in ["Detach", "Unlink", "Remove"]:
                relationship_guid = self._resolve_relationship_guid(object_type, attributes)
                if not relationship_guid:
                    raise ValueError("Cannot remove Next Process Step link: no relationship GUID resolved. Provide 'Relationship GUID' or 'GUID'.")
                await self.client._async_remove_next_action_process_step(relationship_guid)
                logger.success(f"Removed next-process-step link {relationship_guid}")
                return f"\n\n## {verb} {object_type}\n\nRemoved next-process-step link {relationship_guid}"

        return self.command.raw_block


class ActionExecutorTargetLinkProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Link Action to Action Executor (GovernanceActionExecutor) and
    Link Action to Target (TargetForGovernanceAction). Unlike Link Next Process
    Step, detach for both of these takes the same two element GUIDs as attach
    (mirroring link_governance_action_executor/link_target_for_governance_action's
    own attach/detach signatures) rather than a single relationship GUID.
    """

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    async def apply_changes(self) -> str:
        verb = self.command.verb
        object_type = getattr(self, 'canonical_object_type', self.command.object_type)
        attributes = self.parsed_output["attributes"]
        spec = self.get_command_spec()
        om_type = spec.get("OM_TYPE")

        if om_type == "GovernanceActionExecutor":
            type_guid = attributes.get('Governance Action Type', {}).get('guid')
            engine_guid = attributes.get('Governance Engine', {}).get('guid')
            if not (type_guid and engine_guid):
                missing = []
                if not type_guid: missing.append("'Governance Action Type'")
                if not engine_guid: missing.append("'Governance Engine'")
                raise ValueError(f"Cannot link action executor: resolution failed for {', '.join(missing)}")

            if verb in ["Link", "Attach", "Add"]:
                body = set_rel_request_body(om_type, attributes)
                body["properties"] = {
                    "class": "GovernanceActionExecutorProperties",
                    "requestType": attributes.get('Request Type', {}).get('value'),
                    "requestParameters": attributes.get('Request Parameters', {}).get('value'),
                    "requestParameterFilter": attributes.get('Request Parameter Filter', {}).get('value'),
                    "requestParameterMap": attributes.get('Request Parameter Map', {}).get('value'),
                    "actionTargetFilter": attributes.get('Action Target Filter', {}).get('value'),
                    "actionTargetMap": attributes.get('Action Target Map', {}).get('value'),
                }
                self.last_body = body = body_slimmer(body)
                await self.client._async_link_governance_action_executor(type_guid, engine_guid, body)
                logger.success(f"Linked {engine_guid} as executor of {type_guid}")
                return f"\n\n## {verb} {object_type}\n\nLinked {engine_guid} as executor of {type_guid}"

            elif verb in ["Detach", "Unlink", "Remove"]:
                body = set_delete_rel_request_body(om_type, attributes)
                await self.client._async_detach_governance_action_executor(type_guid, engine_guid, body)
                logger.success(f"Removed executor link between {type_guid} and {engine_guid}")
                return f"\n\n## {verb} {object_type}\n\nRemoved executor link between {type_guid} and {engine_guid}"

        elif om_type == "TargetForGovernanceAction":
            action_guid = attributes.get('Governance Action', {}).get('guid')
            element_guid = attributes.get('Element Id', {}).get('guid')
            if not (action_guid and element_guid):
                missing = []
                if not action_guid: missing.append("'Governance Action'")
                if not element_guid: missing.append("'Element Id'")
                raise ValueError(f"Cannot link action target: resolution failed for {', '.join(missing)}")

            if verb in ["Link", "Attach", "Add"]:
                body = set_rel_request_body(om_type, attributes)
                body["properties"] = {
                    "class": "TargetForGovernanceActionProperties",
                    "actionTargetName": attributes.get('Action Target Name', {}).get('value'),
                }
                self.last_body = body = body_slimmer(body)
                await self.client._async_link_target_for_governance_action(action_guid, element_guid, body)
                logger.success(f"Linked {element_guid} as target of {action_guid}")
                return f"\n\n## {verb} {object_type}\n\nLinked {element_guid} as target of {action_guid}"

            elif verb in ["Detach", "Unlink", "Remove"]:
                body = set_delete_rel_request_body(om_type, attributes)
                await self.client._async_detach_target_for_governance_action(action_guid, element_guid, body)
                logger.success(f"Removed target link between {action_guid} and {element_guid}")
                return f"\n\n## {verb} {object_type}\n\nRemoved target link between {action_guid} and {element_guid}"

        return self.command.raw_block
