"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

    Manage privacy and data processing purposes in Egeria.

"""

import asyncio
import json
from typing import Optional, Union, Any

from pyegeria.core._server_client import ServerClient
from pyegeria.models import (
    NewRelationshipRequestBody,
    DeleteRelationshipRequestBody,
)
from pyegeria.core.utils import dynamic_catch


class PrivacyOfficer(ServerClient):
    """
    Manage Privacy Officer operations in Egeria.

    This client provides methods to manage data processing purposes and actions,
    and their relationships to descriptions and targets.

    Parameters
    -----------
    view_server : str
        The name of the View Server to connect to.
    platform_url : str
        URL of the server platform to connect to.
    user_id : str
        Default user identity for calls (can be overridden per call).
    user_pwd : str, optional
        Password for the user_id. If a token is supplied, this may be None.
    token : str, optional
        Supply a token instead of using userId/password discovery.
    """

    def __init__(
        self,
        view_server: str = None,
        platform_url: str = None,
        user_id: str = None,
        user_pwd: Optional[str] = None,
        token: Optional[str] = None,
    ):
        ServerClient.__init__(self, view_server, platform_url, user_id, user_pwd, token)
        self.privacy_officer_base_url = (
            f"{self.platform_url}/servers/{self.server_name}/api/open-metadata/privacy-officer"
        )

    @dynamic_catch
    async def _async_link_permitted_processing(
        self,
        data_processing_purpose_guid: str,
        data_processing_description_guid: str,
        body: Union[dict, Any],
    ) -> None:
        """Link a data processing purpose to a data processing description. Async version."""
        url = (
            f"{self.privacy_officer_base_url}/data-processing-purposes/{data_processing_purpose_guid}"
            f"/permitted-processing/{data_processing_description_guid}/attach"
        )

        if hasattr(body, "model_dump_json"):
            payload = body.model_dump_json(exclude_none=True, by_alias=True)
        else:
            payload = json.dumps(body)

        await self._async_make_request("POST", url, payload)

    def link_permitted_processing(
        self,
        data_processing_purpose_guid: str,
        data_processing_description_guid: str,
        body: Union[dict, NewRelationshipRequestBody],
    ) -> None:
        """Link a data processing purpose to a data processing description."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_link_permitted_processing(
                data_processing_purpose_guid, data_processing_description_guid, body
            )
        )

    @dynamic_catch
    async def _async_detach_permitted_processing(
        self,
        data_processing_purpose_guid: str,
        data_processing_description_guid: str,
        body: Union[dict, Any],
    ) -> None:
        """Detach a data processing purpose from a data processing description. Async version."""
        url = (
            f"{self.privacy_officer_base_url}/data-processing-purposes/{data_processing_purpose_guid}"
            f"/permitted-processing/{data_processing_description_guid}/detach"
        )

        if hasattr(body, "model_dump_json"):
            payload = body.model_dump_json(exclude_none=True, by_alias=True)
        else:
            payload = json.dumps(body)

        await self._async_make_request("POST", url, payload)

    def detach_permitted_processing(
        self,
        data_processing_purpose_guid: str,
        data_processing_description_guid: str,
        body: Union[dict, DeleteRelationshipRequestBody],
    ) -> None:
        """Detach a data processing purpose from a data processing description."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_detach_permitted_processing(
                data_processing_purpose_guid, data_processing_description_guid, body
            )
        )

    @dynamic_catch
    async def _async_link_data_processing_target(
        self,
        data_processing_action_guid: str,
        target_guid: str,
        body: Union[dict, Any],
    ) -> None:
        """Link a data processing action to a target element. Async version."""
        url = (
            f"{self.privacy_officer_base_url}/data-processing-actions/{data_processing_action_guid}"
            f"/targets/{target_guid}/attach"
        )

        if hasattr(body, "model_dump_json"):
            payload = body.model_dump_json(exclude_none=True, by_alias=True)
        else:
            payload = json.dumps(body)

        await self._async_make_request("POST", url, payload)

    def link_data_processing_target(
        self,
        data_processing_action_guid: str,
        target_guid: str,
        body: Union[dict, NewRelationshipRequestBody],
    ) -> None:
        """Link a data processing action to a target element."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_link_data_processing_target(
                data_processing_action_guid, target_guid, body
            )
        )

    @dynamic_catch
    async def _async_detach_data_processing_target(
        self,
        data_processing_action_guid: str,
        target_guid: str,
        body: Union[dict, Any],
    ) -> None:
        """Detach a data processing action from a target element. Async version."""
        url = (
            f"{self.privacy_officer_base_url}/data-processing-actions/{data_processing_action_guid}"
            f"/targets/{target_guid}/detach"
        )

        if hasattr(body, "model_dump_json"):
            payload = body.model_dump_json(exclude_none=True, by_alias=True)
        else:
            payload = json.dumps(body)

        await self._async_make_request("POST", url, payload)

    def detach_data_processing_target(
        self,
        data_processing_action_guid: str,
        target_guid: str,
        body: Union[dict, DeleteRelationshipRequestBody],
    ) -> None:
        """Detach a data processing action from a target element."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_detach_data_processing_target(
                data_processing_action_guid, target_guid, body
            )
        )
