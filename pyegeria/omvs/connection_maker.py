"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

The Connection Maker OMVS provides APIs for supporting the creation and editing of connections,
connectorTypes and endpoints.
"""

from pyegeria.core._server_client import ServerClient
from pyegeria.models.models import (
    NewElementRequestBody,
    UpdateElementRequestBody,
    DeleteElementRequestBody,
    TemplateRequestBody,
    FilterRequestBody,
    SearchStringRequestBody,
    GetRequestBody,
    NewRelationshipRequestBody,
    DeleteRelationshipRequestBody,
)
from typing import Optional, List, Union


class ConnectionMaker(ServerClient):
    """
    Client for the Connection Maker Open Metadata View Service (OMVS).
    """

    def __init__(
        self,
        server_name: str,
        platform_url: str,
        user_id: str,
        user_pwd: str,
        token: Optional[str] = None,
    ):
        super().__init__(server_name, platform_url, user_id, user_pwd, token)
        self.base_url = f"{self.platform_url}/servers/{self.server_name}/api/open-metadata/connection-maker"

    # --- Connections ---

    async def _async_create_connection(self, body: Union[NewElementRequestBody, dict]) -> str:
        url = f"{self.base_url}/connections"
        return await self._async_create_element_body_request(url, ["ConnectionProperties"], body)

    async def _async_create_connection_from_template(self, body: Union[TemplateRequestBody, dict]) -> str:
        url = f"{self.base_url}/connections/from-template"
        return await self._async_create_element_from_template(url, body)

    async def _async_update_connection(self, connection_guid: str, body: Union[UpdateElementRequestBody, dict]):
        url = f"{self.base_url}/connections/{connection_guid}/update"
        await self._async_make_request("POST", url, payload=body)

    async def _async_delete_connection(self, connection_guid: str, body: Union[DeleteElementRequestBody, dict]):
        url = f"{self.base_url}/connections/{connection_guid}/delete"
        await self._async_make_request("POST", url, payload=body)

    async def _async_get_connection_by_guid(self, connection_guid: str, body: Union[GetRequestBody, dict]) -> dict:
        url = f"{self.base_url}/connections/{connection_guid}/retrieve"
        resp = await self._async_make_request("POST", url, payload=body)
        return resp.json()

    async def _async_get_connections_by_name(self, body: Union[FilterRequestBody, dict]) -> List[dict]:
        url = f"{self.base_url}/connections/by-name"
        return await self._async_find_request(url, body)

    async def _async_find_connections(self, body: Union[SearchStringRequestBody, dict]) -> List[dict]:
        url = f"{self.base_url}/connections/by-search-string"
        return await self._async_find_request(url, body)

    # --- Connector Types ---

    async def _async_create_connector_type(self, body: Union[NewElementRequestBody, dict]) -> str:
        url = f"{self.base_url}/connector-types"
        return await self._async_create_element_body_request(url, ["ConnectorTypeProperties"], body)

    async def _async_create_connector_type_from_template(self, body: Union[TemplateRequestBody, dict]) -> str:
        url = f"{self.base_url}/connector-types/from-template"
        return await self._async_create_element_from_template(url, body)

    async def _async_update_connector_type(self, connector_type_guid: str, body: Union[UpdateElementRequestBody, dict]):
        url = f"{self.base_url}/connector-types/{connector_type_guid}/update"
        await self._async_make_request("POST", url, payload=body)

    async def _async_delete_connector_type(self, connector_type_guid: str, body: Union[DeleteElementRequestBody, dict]):
        url = f"{self.base_url}/connector-types/{connector_type_guid}/delete"
        await self._async_make_request("POST", url, payload=body)

    async def _async_get_connector_type_by_guid(self, connector_type_guid: str, body: Union[GetRequestBody, dict]) -> dict:
        url = f"{self.base_url}/connector-types/{connector_type_guid}/retrieve"
        resp = await self._async_make_request("POST", url, payload=body)
        return resp.json()

    async def _async_get_connector_types_by_name(self, body: Union[FilterRequestBody, dict]) -> List[dict]:
        url = f"{self.base_url}/connector-types/by-name"
        return await self._async_find_request(url, body)

    async def _async_find_connector_types(self, body: Union[SearchStringRequestBody, dict]) -> List[dict]:
        url = f"{self.base_url}/connector-types/by-search-string"
        return await self._async_find_request(url, body)

    # --- Endpoints ---

    async def _async_create_endpoint(self, body: Union[NewElementRequestBody, dict]) -> str:
        url = f"{self.base_url}/endpoints"
        return await self._async_create_element_body_request(url, ["EndpointProperties"], body)

    async def _async_create_endpoint_from_template(self, body: Union[TemplateRequestBody, dict]) -> str:
        url = f"{self.base_url}/endpoints/from-template"
        return await self._async_create_element_from_template(url, body)

    async def _async_update_endpoint(self, endpoint_guid: str, body: Union[UpdateElementRequestBody, dict]):
        url = f"{self.base_url}/endpoints/{endpoint_guid}/update"
        await self._async_make_request("POST", url, payload=body)

    async def _async_delete_endpoint(self, endpoint_guid: str, body: Union[DeleteElementRequestBody, dict]):
        url = f"{self.base_url}/endpoints/{endpoint_guid}/delete"
        await self._async_make_request("POST", url, payload=body)

    async def _async_get_endpoint_by_guid(self, endpoint_guid: str, body: Union[GetRequestBody, dict]) -> dict:
        url = f"{self.base_url}/endpoints/{endpoint_guid}/retrieve"
        resp = await self._async_make_request("POST", url, payload=body)
        return resp.json()

    async def _async_get_endpoints_by_name(self, body: Union[FilterRequestBody, dict]) -> List[dict]:
        url = f"{self.base_url}/endpoints/by-name"
        return await self._async_find_request(url, body)

    async def _async_get_endpoints_by_network_address(self, body: Union[FilterRequestBody, dict]) -> List[dict]:
        url = f"{self.base_url}/endpoints/by-network-address"
        return await self._async_find_request(url, body)

    async def _async_find_endpoints(self, body: Union[SearchStringRequestBody, dict]) -> List[dict]:
        url = f"{self.base_url}/endpoints/by-search-string"
        return await self._async_find_request(url, body)

    async def _async_get_endpoints_for_asset(self, asset_guid: str, body: Union[FilterRequestBody, dict]) -> List[dict]:
        url = f"{self.base_url}/assets/{asset_guid}/endpoints/retrieve"
        return await self._async_find_request(url, body)

    # --- Relationships ---

    async def _async_link_connection_connector_type(self, connection_guid: str, connector_type_guid: str, body: Union[NewRelationshipRequestBody, dict]):
        url = f"{self.base_url}/connections/{connection_guid}/connector-types/{connector_type_guid}/attach"
        await self._async_make_request("POST", url, payload=body)

    async def _async_detach_connection_connector_type(self, connection_guid: str, connector_type_guid: str, body: Union[DeleteRelationshipRequestBody, dict]):
        url = f"{self.base_url}/connections/{connection_guid}/connector-types/{connector_type_guid}/detach"
        await self._async_make_request("POST", url, payload=body)

    async def _async_link_connection_endpoint(self, connection_guid: str, endpoint_guid: str, body: Union[NewRelationshipRequestBody, dict]):
        url = f"{self.base_url}/connections/{connection_guid}/endpoints/{endpoint_guid}/attach"
        await self._async_make_request("POST", url, payload=body)

    async def _async_detach_connection_endpoint(self, connection_guid: str, endpoint_guid: str, body: Union[DeleteRelationshipRequestBody, dict]):
        url = f"{self.base_url}/connections/{connection_guid}/endpoints/{endpoint_guid}/detach"
        await self._async_make_request("POST", url, payload=body)

    async def _async_link_embedded_connection(self, connection_guid: str, embedded_connection_guid: str, body: Union[NewRelationshipRequestBody, dict]):
        url = f"{self.base_url}/connections/{connection_guid}/embedded-connections/{embedded_connection_guid}/attach"
        await self._async_make_request("POST", url, payload=body)

    async def _async_detach_embedded_connection(self, connection_guid: str, embedded_connection_guid: str, body: Union[DeleteRelationshipRequestBody, dict]):
        url = f"{self.base_url}/connections/{connection_guid}/embedded-connections/{embedded_connection_guid}/detach"
        await self._async_make_request("POST", url, payload=body)

    async def _async_link_asset_to_connection(self, asset_guid: str, connection_guid: str, body: Union[NewRelationshipRequestBody, dict]):
        url = f"{self.base_url}/assets/{asset_guid}/connections/{connection_guid}/attach"
        await self._async_make_request("POST", url, payload=body)

    async def _async_detach_asset_from_connection(self, asset_guid: str, connection_guid: str, body: Union[DeleteRelationshipRequestBody, dict]):
        url = f"{self.base_url}/assets/{asset_guid}/connections/{connection_guid}/detach"
        await self._async_make_request("POST", url, payload=body)

    async def _async_link_endpoint_to_it_asset(self, asset_guid: str, endpoint_guid: str, body: Union[NewRelationshipRequestBody, dict]):
        url = f"{self.base_url}/assets/{asset_guid}/endpoints/{endpoint_guid}/attach"
        await self._async_make_request("POST", url, payload=body)

    async def _async_detach_endpoint_from_it_asset(self, asset_guid: str, endpoint_guid: str, body: Union[DeleteRelationshipRequestBody, dict]):
        url = f"{self.base_url}/assets/{asset_guid}/endpoints/{endpoint_guid}/detach"
        await self._async_make_request("POST", url, payload=body)
