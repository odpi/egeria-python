"""
Action Author Processors for Dr.Egeria v2.

Handles the two Action Author link commands (Link First Process Step,
Link Next Process Step). These don't fit the generic governance
peer-link mechanism (GovernanceLinkProcessor / link_peer_definitions) --
they call the action_author OMVS client directly, with dedicated
relationship properties (guard/requestParameters/mandatoryGuard) that
the generic PeerDefinitionProperties body has no room for.
"""
from typing import Dict, Any, Optional
from loguru import logger

from md_processing.v2.processors import AsyncBaseCommandProcessor
from md_processing.md_processing_utils.common_md_utils import set_rel_request_body
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
