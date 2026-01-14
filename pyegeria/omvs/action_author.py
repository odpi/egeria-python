"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module contains the Action Author View Service client.
"""

import asyncio
from typing import Annotated, Literal, Optional

from pydantic import Field

from pyegeria.core._server_client import ServerClient
from pyegeria.models import (
    NewRelationshipRequestBody,
    DeleteRelationshipRequestBody,
    UpdateRelationshipRequestBody,
    RelationshipBeanProperties,
)
from pyegeria.core.utils import dynamic_catch


class GovernanceActionExecutorProperties(RelationshipBeanProperties):
    class_: Annotated[Literal["GovernanceActionExecutorProperties"], Field(alias="class")]
    request_type: Optional[str] = None
    request_parameters: Optional[dict] = None
    request_parameter_filter: Optional[list] = None
    request_parameter_map: Optional[dict] = None
    action_target_filter: Optional[list] = None
    action_target_map: Optional[dict] = None


class TargetForGovernanceActionProperties(RelationshipBeanProperties):
    class_: Annotated[Literal["TargetForGovernanceActionProperties"], Field(alias="class")]
    action_target_name: Optional[str] = None


class GovernanceActionProcessFlowProperties(RelationshipBeanProperties):
    class_: Annotated[Literal["GovernanceActionProcessFlowProperties"], Field(alias="class")]
    guard: Optional[str] = None
    request_parameters: Optional[dict] = None
    mandatory_guard: Optional[bool] = None


class NextGovernanceActionProcessStepProperties(RelationshipBeanProperties):
    class_: Annotated[Literal["NextGovernanceActionProcessStepProperties"], Field(alias="class")]
    guard: Optional[str] = None
    mandatory_guard: Optional[bool] = None


class ActionAuthor(ServerClient):
    """
    Client for the Action Author View Service.

    The Action Author View Service provides methods to manage governance actions,
    governance action processes and their steps.

    Attributes
    ----------
    view_server : str
        The name of the View Server to use.
    platform_url : str
        URL of the server platform to connect to.
    user_id : str
        The identity of the user calling the method.
    user_pwd : str
        The password associated with the user_id. Defaults to None.
    """

    def __init__(
        self,
        view_server: str,
        platform_url: str,
        user_id: str,
        user_pwd: Optional[str] = None,
        token: Optional[str] = None,
    ):
        super().__init__(view_server, platform_url, user_id, user_pwd, token)
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd
        self.url_marker = "action-author"

    @dynamic_catch
    async def _async_link_governance_action_executor(
        self,
        governance_action_type_guid: str,
        governance_engine_guid: str,
        body: dict | NewRelationshipRequestBody,
    ) -> None:
        """Link a governance action type to a governance engine. Async version.

        Parameters
        ----------
        governance_action_type_guid : str
            The unique identifier of the governance action type.
        governance_engine_guid : str
            The unique identifier of the governance engine.
        body : dict | NewRelationshipRequestBody
            The properties for the relationship.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "NewRelationshipRequestBody",
          "properties": {
            "class": "GovernanceActionExecutorProperties",
            "requestType": "add label here",
            "requestParameters": {},
            "requestParameterFilter": [],
            "requestParameterMap": {},
            "actionTargetFilter": [],
            "actionTargetMap": {}
          }
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/action-author/governance-action-types/{governance_action_type_guid}/governance-engine-executor/{governance_engine_guid}/attach"
        await self._async_new_relationship_request(url, ["GovernanceActionExecutorProperties"], body)

    def link_governance_action_executor(
        self,
        governance_action_type_guid: str,
        governance_engine_guid: str,
        body: dict | NewRelationshipRequestBody,
    ) -> None:
        """Link a governance action type to a governance engine.

        Parameters
        ----------
        governance_action_type_guid : str
            The unique identifier of the governance action type.
        governance_engine_guid : str
            The unique identifier of the governance engine.
        body : dict | NewRelationshipRequestBody
            The properties for the relationship.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "NewRelationshipRequestBody",
          "properties": {
            "class": "GovernanceActionExecutorProperties",
            "requestType": "add label here",
            "requestParameters": {},
            "requestParameterFilter": [],
            "requestParameterMap": {},
            "actionTargetFilter": [],
            "actionTargetMap": {}
          }
        }
        ```
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_link_governance_action_executor(
                governance_action_type_guid, governance_engine_guid, body
            )
        )

    @dynamic_catch
    async def _async_detach_governance_action_executor(
        self,
        governance_action_type_guid: str,
        governance_engine_guid: str,
        body: dict | DeleteRelationshipRequestBody,
    ) -> None:
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/action-author/governance-action-types/{governance_action_type_guid}/governance-engine-executor/{governance_engine_guid}/detach"
        await self._async_delete_relationship_request(url, body)

    def detach_governance_action_executor(
        self,
        governance_action_type_guid: str,
        governance_engine_guid: str,
        body: dict | DeleteRelationshipRequestBody,
    ) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_detach_governance_action_executor(
                governance_action_type_guid, governance_engine_guid, body
            )
        )

    @dynamic_catch
    async def _async_link_target_for_governance_action(
        self,
        governance_action_guid: str,
        element_guid: str,
        body: dict | NewRelationshipRequestBody,
    ) -> None:
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/action-author/governance-actions/{governance_action_guid}/action-targets/{element_guid}/attach"
        await self._async_new_relationship_request(url, ["TargetForGovernanceActionProperties"], body)

    def link_target_for_governance_action(
        self,
        governance_action_guid: str,
        element_guid: str,
        body: dict | NewRelationshipRequestBody,
    ) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_link_target_for_governance_action(governance_action_guid, element_guid, body)
        )

    @dynamic_catch
    async def _async_detach_target_for_governance_action(
        self,
        governance_action_guid: str,
        element_guid: str,
        body: dict | DeleteRelationshipRequestBody,
    ) -> None:
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/action-author/governance-actions/{governance_action_guid}/action-targets/{element_guid}/detach"
        await self._async_delete_relationship_request(url, body)

    def detach_target_for_governance_action(
        self,
        governance_action_guid: str,
        element_guid: str,
        body: dict | DeleteRelationshipRequestBody,
    ) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_detach_target_for_governance_action(
                governance_action_guid, element_guid, body
            )
        )

    @dynamic_catch
    async def _async_setup_first_action_process_step(
        self,
        process_guid: str,
        process_step_guid: str,
        body: dict | NewRelationshipRequestBody,
    ) -> None:
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/action-author/governance-action-processes/{process_guid}/first-process-step/{process_step_guid}/attach"
        await self._async_new_relationship_request(url, ["GovernanceActionProcessFlowProperties"], body)

    def setup_first_action_process_step(
        self,
        process_guid: str,
        process_step_guid: str,
        body: dict | NewRelationshipRequestBody,
    ) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_setup_first_action_process_step(process_guid, process_step_guid, body)
        )

    @dynamic_catch
    async def _async_remove_first_action_process_step(
        self,
        process_guid: str,
    ) -> None:
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/action-author/governance-action-processes/{process_guid}/first-process-step/detach"
        await self._async_make_request("POST", url)

    def remove_first_action_process_step(
        self,
        process_guid: str,
    ) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_remove_first_action_process_step(process_guid))

    @dynamic_catch
    async def _async_setup_next_action_process_step(
        self,
        process_step_guid: str,
        next_process_step_guid: str,
        body: dict | NewRelationshipRequestBody,
    ) -> None:
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/action-author/governance-action-process-steps/{process_step_guid}/next-process-steps/{next_process_step_guid}/attach"
        await self._async_new_relationship_request(url, ["NextGovernanceActionProcessStepProperties"], body)

    def setup_next_action_process_step(
        self,
        process_step_guid: str,
        next_process_step_guid: str,
        body: dict | NewRelationshipRequestBody,
    ) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_setup_next_action_process_step(
                process_step_guid, next_process_step_guid, body
            )
        )

    @dynamic_catch
    async def _async_update_next_action_process_step(
        self,
        relationship_guid: str,
        body: dict | UpdateRelationshipRequestBody,
    ) -> None:
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/action-author/governance-action-process-steps/next-process-steps/{relationship_guid}/update"
        await self._async_update_relationship_body_request(url, body)

    def update_next_action_process_step(
        self,
        relationship_guid: str,
        body: dict | UpdateRelationshipRequestBody,
    ) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_next_action_process_step(relationship_guid, body)
        )

    @dynamic_catch
    async def _async_remove_next_action_process_step(
        self,
        relationship_guid: str,
    ) -> None:
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/action-author/governance-action-process-steps/next-process-step/{relationship_guid}/detach"
        await self._async_make_request("POST", url)

    def remove_next_action_process_step(
        self,
        relationship_guid: str,
    ) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_remove_next_action_process_step(relationship_guid))
