"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

    Client for the Governance Engine view service.

    A governance engine that runs engine actions outside of Egeria claims the engine actions that are approved to
    run on it, reports their progress and records their completion.  These operations lived on the Automated
    Curation view service until Egeria odpi/egeria#9371 moved them to
    ``/servers/{serverName}/api/open-metadata/governance-engine``.
"""

import asyncio
from typing import Optional

from pyegeria.core._exceptions import PyegeriaClientException
from pyegeria.core._globals import NO_ELEMENTS_FOUND
from pyegeria.core._server_client import ServerClient
from pyegeria.core._validators import validate_guid
from pyegeria.core.utils import body_slimmer, dynamic_catch
from pyegeria.core.async_runner import run_sync


class GovernanceEngine(ServerClient):
    """Claim, progress and complete engine actions for a governance engine.

    Parameters
    ----------
    view_server : str
        The name of the View Server to connect to.
    platform_url : str
        URL of the server platform to connect to.
    user_id : str
        Default user identity for calls.
    user_pwd : str, optional
        Password for the user_id. If a token is supplied, this may be None.
    legacy_fallback : bool, default False
        If True, an operation whose governance-engine URL answers HTTP 404 (an Egeria built before #9371, which
        served these operations from the automated-curation view service) is retried once on the old
        automated-curation URL. Only an HTTP 404 on the URL triggers this; an Egeria-reported error (such as an
        unknown engine action GUID) or any other failure is raised unchanged. Whichever URL family answered is
        remembered for the life of this client (once the new URL has answered, a later 404 is raised, not retried).
    """

    def __init__(
            self,
            view_server: str,
            platform_url: str,
            user_id: str,
            user_pwd: Optional[str] = None,
            token: Optional[str] = None,
            timeout: int = None,
            legacy_fallback: bool = False,
    ):
        ServerClient.__init__(self, view_server, platform_url, user_id, user_pwd, token=token, timeout=timeout)
        self.view_server = view_server
        self.platform_url = platform_url
        self.governance_engine_command_base = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/governance-engine"
        )
        self.command_root = self.governance_engine_command_base
        self._legacy_base = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/automated-curation"
        )
        self.legacy_fallback = legacy_fallback
        # None = not yet known, "new" or "legacy" once an attempt has succeeded / 404ed.
        self._url_family: Optional[str] = None

    async def _request(self, method: str, suffix: str, body: Optional[dict] = None, params: Optional[dict] = None):
        """Issue the request on the governance-engine URL, with the optional one-time 404 fallback."""

        async def call(base: str):
            url = f"{base}{suffix}"
            kwargs = {"params": params} if params is not None else {}
            if body is not None:
                return await self._async_make_request(method, url, body, **kwargs)
            return await self._async_make_request(method, url, **kwargs)

        if self._url_family == "legacy" and self.legacy_fallback:
            return await call(self._legacy_base)
        try:
            response = await call(self.governance_engine_command_base)
        except PyegeriaClientException as e:
            if not (self.legacy_fallback and self._url_family is None
                    and getattr(e, "response_code", None) == 404):
                raise
            response = await call(self._legacy_base)
            self._url_family = "legacy"
            return response
        self._url_family = "new"
        return response

    @dynamic_catch
    async def _async_get_approved_engine_actions(
            self, governance_engine_guid: str, start_from: int = 0, page_size: int = 0) -> list | str:
        """Retrieve the engine actions that are approved to run on a governance engine and that no engine has
        claimed yet. Async version.

        Parameters
        ----------
        governance_engine_guid : str
            The GUID of the governance engine.
        start_from : int, default 0
            The index from which to start fetching.
        page_size : int, default 0
            The maximum number to fetch in a single request (0 = server default).

        Returns
        -------
        list | str
            The engine actions, or NO_ELEMENTS_FOUND if there are none.

        Notes
        -----
        GET {base}/governance-engines/{governanceEngineGUID}/engine-actions/approved. There is no
        automated-curation equivalent, so this never falls back.
        For more information see: https://egeria-project.org/concepts/engine-action
        """
        validate_guid(governance_engine_guid)
        url = f"{self.governance_engine_command_base}/governance-engines/{governance_engine_guid}/engine-actions/approved"
        response = await self._async_make_request("GET", url, params={"startFrom": start_from, "pageSize": page_size})
        return response.json().get("elements", NO_ELEMENTS_FOUND)

    def get_approved_engine_actions(
            self, governance_engine_guid: str, start_from: int = 0, page_size: int = 0) -> list | str:
        """Retrieve the engine actions approved to run on a governance engine that no engine has claimed yet."""
        return run_sync(
            self._async_get_approved_engine_actions(governance_engine_guid, start_from, page_size))

    @dynamic_catch
    async def _async_claim_engine_action(self, engine_action_guid: str) -> None:
        """Request that execution of an engine action is allocated to the caller. Async version.

        POST {base}/engine-actions/{engineActionGUID}/claim (no body).
        """
        validate_guid(engine_action_guid)
        await self._request("POST", f"/engine-actions/{engine_action_guid}/claim")

    def claim_engine_action(self, engine_action_guid: str) -> None:
        """Request that execution of an engine action is allocated to the caller."""
        run_sync(self._async_claim_engine_action(engine_action_guid))

    @dynamic_catch
    async def _async_get_active_claimed_engine_actions(
            self, governance_engine_guid: str, start_from: int = 0, page_size: int = 0) -> list | str:
        """Retrieve the engine actions still in process that this caller's userId has claimed. Used when the
        caller restarts. Async version.

        GET {base}/governance-engines/{governanceEngineGUID}/engine-actions/active-claimed
        with startFrom / pageSize query parameters.
        """
        validate_guid(governance_engine_guid)
        response = await self._request(
            "GET", f"/governance-engines/{governance_engine_guid}/engine-actions/active-claimed",
            params={"startFrom": start_from, "pageSize": page_size})
        return response.json().get("elements", NO_ELEMENTS_FOUND)

    def get_active_claimed_engine_actions(
            self, governance_engine_guid: str, start_from: int = 0, page_size: int = 0) -> list | str:
        """Retrieve the engine actions still in process that this caller's userId has claimed."""
        return run_sync(
            self._async_get_active_claimed_engine_actions(governance_engine_guid, start_from, page_size))

    @dynamic_catch
    async def _async_update_engine_action_status(self, engine_action_guid: str, status: str,
                                                 body: Optional[dict] = None) -> None:
        """Update the status of the engine action - providing the caller is permitted. Async version.

        POST {base}/engine-actions/{engineActionGUID}/status/update with an EngineActionStatusRequestBody.

        Parameters
        ----------
        status : str
            An ActivityStatus value such as "REQUESTED", "APPROVED", "IN_PROGRESS", "COMPLETED", "FAILED".
        body : dict, optional
            Request body passed as-is; overrides `status`.
        """
        validate_guid(engine_action_guid)
        payload = body if body is not None else {"class": "EngineActionStatusRequestBody", "status": status}
        await self._request("POST", f"/engine-actions/{engine_action_guid}/status/update", payload)

    def update_engine_action_status(self, engine_action_guid: str, status: str,
                                    body: Optional[dict] = None) -> None:
        """Update the status of the engine action - providing the caller is permitted."""
        run_sync(self._async_update_engine_action_status(engine_action_guid, status, body))

    @dynamic_catch
    async def _async_update_action_target_status(
            self, action_target_guid: str, status: str,
            start_date: Optional[str] = None, completion_date: Optional[str] = None,
            completion_message: Optional[str] = None, body: Optional[dict] = None) -> None:
        """Update the status of a specific action target. Async version.

        POST {base}/engine-actions/action-targets/update with an ActionTargetStatusRequestBody
        (actionTargetGUID, status, startDate, completionDate, completionMessage).
        `body`, if given, is passed as-is and overrides the other parameters.
        """
        validate_guid(action_target_guid)
        payload = body if body is not None else {
            "class": "ActionTargetStatusRequestBody",
            "actionTargetGUID": action_target_guid,
            "status": status,
            "startDate": start_date,
            "completionDate": completion_date,
            "completionMessage": completion_message,
        }
        await self._request("POST", "/engine-actions/action-targets/update", body_slimmer(payload))

    def update_action_target_status(
            self, action_target_guid: str, status: str,
            start_date: Optional[str] = None, completion_date: Optional[str] = None,
            completion_message: Optional[str] = None, body: Optional[dict] = None) -> None:
        """Update the status of a specific action target."""
        run_sync(self._async_update_action_target_status(
            action_target_guid, status, start_date, completion_date, completion_message, body))

    @dynamic_catch
    async def _async_record_completion_status(
            self, engine_action_guid: str, status: str,
            request_parameters: Optional[dict] = None, output_guards: Optional[list[str]] = None,
            new_action_targets: Optional[list[dict]] = None, completion_message: Optional[str] = None,
            body: Optional[dict] = None) -> None:
        """Declare that all processing for the engine action is finished, and the status of the work. Async
        version.

        POST {base}/engine-actions/{engineActionGUID}/completion-status with a CompletionStatusRequestBody.
        If the engine action is part of a governance action process, the output guards decide which steps run
        next. `status` is one of "ACTIONED", "INVALID", "FAILED" or "OTHER".
        `body`, if given, is passed as-is and overrides the other parameters.
        """
        validate_guid(engine_action_guid)
        payload = body if body is not None else {
            "class": "CompletionStatusRequestBody",
            "status": status,
            "requestParameters": request_parameters,
            "outputGuards": output_guards,
            "newActionTargets": new_action_targets,
            "completionMessage": completion_message,
        }
        await self._request("POST", f"/engine-actions/{engine_action_guid}/completion-status",
                            body_slimmer(payload))

    def record_completion_status(
            self, engine_action_guid: str, status: str,
            request_parameters: Optional[dict] = None, output_guards: Optional[list[str]] = None,
            new_action_targets: Optional[list[dict]] = None, completion_message: Optional[str] = None,
            body: Optional[dict] = None) -> None:
        """Declare that all processing for the engine action is finished, and the status of the work."""
        run_sync(self._async_record_completion_status(
            engine_action_guid, status, request_parameters, output_guards, new_action_targets,
            completion_message, body))
