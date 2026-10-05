"""
Automation Processors for Dr.Egeria v2.

Handles the "Automation" command family -- requests that set Egeria's
governance engines running, rather than create or change metadata directly:

- Initiate Governance Action Process / Initiate Governance Action Type: run a
  process (or a single action type) through AutomatedCuration's
  initiate_gov_action_process / initiate_gov_action_type.
- Initiate Survey: run a survey governance action type against one resource.
  The action target name each survey expects (e.g. "postgresDatabase",
  "fileToSurvey") is read from the survey type's specification by
  AutomatedCuration._async_initiate_survey, unless Action Target Name is set.
- Initiate Subscription: Egeria has no "create subscription" call -- a digital
  product offers each subscription type as a SubscribingActionProcess
  ("ProvisioningActionProcess::<product>::Create Subscription::<type>") that
  already carries the product, its asset, license, service level objective and
  notification type. Running it with the two remaining action targets
  (digitalSubscriptionRequester, destinationDataSet) provisions the
  subscription (see Egeria-api-automated-curation.http and the notification
  manager's Egeria-baudot-*.http samples).
- Cancel Subscription: when a subscription is provisioned, Egeria creates a
  dedicated DeletingActionProcess for cancelling it and links it to the
  subscription through ResourceList with resourceUse "Cancel Subscription"
  (CreateSubscriptionGovernanceActionConnector). Cancelling runs that process.

Create Element (moved here from Asset Maker) keeps its AssetMakerProcessor.

Every command here is an action, not a create-or-update of a named element,
so there is no existing element to look up and no Create<->Update rewrite
(same shape as InitiateEngineActionProcessor in engine_action.py).
"""
import json
from typing import Any, Dict, List, Optional

from loguru import logger

from pyegeria import PyegeriaException
from md_processing.v2.processors import AsyncBaseCommandProcessor

CANCEL_SUBSCRIPTION_RESOURCE_USE = "Cancel Subscription"


def _v(attributes: Dict[str, Any], name: str, default=None):
    return attributes.get(name, {}).get("value", default)


def _guid(attributes: Dict[str, Any], name: str) -> Optional[str]:
    guid = attributes.get(name, {}).get("guid")
    return None if not guid or str(guid).startswith("(Planned:") else guid


def _guid_list(attributes: Dict[str, Any], name: str) -> List[str]:
    guid_list = attributes.get(name, {}).get("guid_list")
    if isinstance(guid_list, list):
        return [g for g in guid_list if g and not str(g).startswith("(Planned:")]
    return []


def _action_target(name: str, guid: str) -> Dict[str, str]:
    return {"class": "NewActionTarget", "actionTargetName": name, "actionTargetGUID": guid}


def _initiated(guid: Any) -> bool:
    return isinstance(guid, str) and bool(guid) and guid != "Action not initiated"


class AutomationProcessor(AsyncBaseCommandProcessor):
    """Shared behaviour for the Automation family's action commands."""

    def supports_target_element_lookup(self) -> bool:
        # An action, not a named element: no as-is lookup, no upsert rewrite.
        return False

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    async def _get_element(self, guid: str) -> Dict[str, Any]:
        client = self.client.classification_manager
        url = (f"{client.platform_url}/servers/{client.view_server}/api/open-metadata/"
               f"classification-explorer/elements/{guid}")
        response = await client._async_make_request("POST", url, json.dumps({"class": "GetRequestBody"}))
        return response.json().get("element") or {}

    async def _qualified_name(self, attributes: Dict[str, Any], attr_name: str) -> str:
        """The qualified name of a Reference Name attribute's element -- the initiate
        calls take qualified names, while the author may have given a display name or GUID."""
        guid = _guid(attributes, attr_name)
        if not guid:
            raise PyegeriaException(f"'{attr_name}' could not be resolved to an existing element.")
        qualified_name = (await self._get_element(guid)).get("properties", {}).get("qualifiedName")
        if not qualified_name:
            raise PyegeriaException(f"'{attr_name}' ({guid}) has no qualified name.")
        return qualified_name

    async def _action_targets(self, attributes: Dict[str, Any]) -> List[Dict[str, str]]:
        """'Action Targets' Dictionary (name: element per line) -> NewActionTarget list."""
        targets = []
        for name, ref in (_v(attributes, "Action Targets") or {}).items():
            guid = await self.resolve_element_guid(str(ref))
            if not guid or str(guid).startswith("(Planned:"):
                raise PyegeriaException(f"Action target '{name}': '{ref}' could not be resolved to an existing element.")
            targets.append(_action_target(str(name), guid))
        return targets

    def _result(self, what: str, guid: str) -> str:
        self.parsed_output["guid"] = guid
        logger.success(f"{self.command.verb} {self.command.object_type}: {what} ({guid})")
        return f"\n\n## {self.command.verb} {self.command.object_type}\n\n{what}: `{guid}`\n"


class InitiateGovernanceActionProcessProcessor(AutomationProcessor):
    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        process_qn = await self._qualified_name(attributes, "Governance Action Process")
        guid = await self.client._async_initiate_gov_action_process(
            process_qn,
            request_source_guids=_guid_list(attributes, "Request Source Elements") or None,
            action_targets=await self._action_targets(attributes) or None,
            request_parameters=_v(attributes, "Request Parameters") or None,
        )
        if not _initiated(guid):
            raise PyegeriaException(f"Egeria did not start governance action process '{process_qn}'.")
        return self._result(f"Started governance action process `{process_qn}`", guid)


class InitiateGovernanceActionTypeProcessor(AutomationProcessor):
    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        action_type_qn = await self._qualified_name(attributes, "Governance Action Type")
        guid = await self.client._async_initiate_gov_action_type(
            action_type_qn,
            _guid_list(attributes, "Request Source Elements") or None,
            await self._action_targets(attributes) or None,
            request_parameters=_v(attributes, "Request Parameters") or None,
        )
        if not _initiated(guid):
            raise PyegeriaException(f"Egeria did not start governance action type '{action_type_qn}'.")
        return self._result(f"Started engine action for `{action_type_qn}`", guid)


class InitiateSurveyProcessor(AutomationProcessor):
    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        survey_qn = await self._qualified_name(attributes, "Survey Type")
        resource_guid = _guid(attributes, "Resource to Survey")
        if not resource_guid:
            raise PyegeriaException("'Resource to Survey' could not be resolved to an existing element.")
        guid = await self.client._async_initiate_survey(
            survey_qn, resource_guid,
            request_parameters=_v(attributes, "Request Parameters") or None,
            action_target_name=_v(attributes, "Action Target Name") or None,
        )
        if not _initiated(guid):
            raise PyegeriaException(f"Egeria did not start survey '{survey_qn}'.")
        return self._result(f"Started survey `{survey_qn}`", guid)


class InitiateSubscriptionProcessor(AutomationProcessor):
    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        process_qn = await self._qualified_name(attributes, "Subscription Type")
        requester = _guid(attributes, "Subscription Requester")
        destination = _guid(attributes, "Destination Data Set")
        if not requester or not destination:
            raise PyegeriaException("Subscription Requester and Destination Data Set must both resolve to existing elements.")
        guid = await self.client._async_initiate_gov_action_process(
            process_qn,
            action_targets=[_action_target("digitalSubscriptionRequester", requester),
                            _action_target("destinationDataSet", destination)],
            request_parameters=_v(attributes, "Request Parameters") or None,
        )
        if not _initiated(guid):
            raise PyegeriaException(f"Egeria did not start subscription process '{process_qn}'.")
        return self._result(f"Started subscription process `{process_qn}`", guid)


class CancelSubscriptionProcessor(AutomationProcessor):
    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        subscription_guid = _guid(attributes, "Digital Subscription")
        if not subscription_guid:
            raise PyegeriaException("'Digital Subscription' could not be resolved to an existing element.")
        subscription = await self._get_element(subscription_guid)
        cancel_qn = None
        for entry in subscription.get("resourceList") or []:
            use = ((entry.get("relationshipProperties") or {}).get("resourceUse") or "").strip()
            if use.lower() == CANCEL_SUBSCRIPTION_RESOURCE_USE.lower():
                cancel_qn = ((entry.get("relatedElement") or {}).get("properties") or {}).get("qualifiedName")
                break
        if not cancel_qn:
            raise PyegeriaException(
                f"Subscription {subscription_guid} has no '{CANCEL_SUBSCRIPTION_RESOURCE_USE}' process in its "
                f"resource list -- it was probably not created by a subscription process, so it cannot be "
                f"cancelled this way.")
        guid = await self.client._async_initiate_gov_action_process(cancel_qn)
        if not _initiated(guid):
            raise PyegeriaException(f"Egeria did not start cancel process '{cancel_qn}'.")
        return self._result(f"Started cancel process `{cancel_qn}`", guid)
