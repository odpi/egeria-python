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
from typing import Optional, List, Union, Any
import asyncio


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
        timeout: int = None):
        super().__init__(server_name, platform_url, user_id, user_pwd, token, timeout=timeout)
        self.base_url = f"{self.platform_url}/servers/{self.server_name}/api/open-metadata/connection-maker"

    # --- Connections ---

    async def _async_create_connection(self, body: Union[NewElementRequestBody, dict]) -> str:
        url = f"{self.base_url}/connections"
        return await self._async_create_element_body_request(url, ["ConnectionProperties"], body)

    def create_connection(self, body: Union[NewElementRequestBody, dict]) -> str:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_create_connection(body))

    async def _async_create_connection_from_template(self, body: Union[TemplateRequestBody, dict]) -> str:
        url = f"{self.base_url}/connections/from-template"
        return await self._async_create_element_from_template(url, body)

    def create_connection_from_template(self, body: Union[TemplateRequestBody, dict]) -> str:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_create_connection_from_template(body))

    async def _async_update_connection(self, connection_guid: str, body: Union[UpdateElementRequestBody, dict]):
        url = f"{self.base_url}/connections/{connection_guid}/update"
        await self._async_update_element_body_request(url, ["ConnectionProperties"], body)

    def update_connection(self, connection_guid: str, body: Union[UpdateElementRequestBody, dict]):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_update_connection(connection_guid, body))

    async def _async_delete_connection(self, connection_guid: str, body: Union[DeleteElementRequestBody, dict] = None):
        url = f"{self.base_url}/connections/{connection_guid}/delete"
        await self._async_delete_element_request(url, body)

    def delete_connection(self, connection_guid: str, body: Union[DeleteElementRequestBody, dict] = None):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_delete_connection(connection_guid, body))

    async def _async_get_connection_by_guid(
        self,
        guid: str,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        body: Union[GetRequestBody, dict] = None,
        **kwargs,
    ) -> dict | list | str:
        url = f"{self.base_url}/connections/{guid}/retrieve"
        return await self._async_get_guid_request(
            url,
            "Connection",
            self._generate_referenceable_output,
            include_only_relationships=include_only_relationships,
            skip_relationships=skip_relationships,
            graph_query_depth=graph_query_depth,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
            **kwargs,
        )

    def get_connection_by_guid(
        self,
        guid: str,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        body: Union[GetRequestBody, dict] = None,
        **kwargs,
    ) -> dict | list | str:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_connection_by_guid(
                guid=guid,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs
            )
        )

    async def _async_get_connections_by_name(
        self,
        name: str,
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        body: Union[FilterRequestBody, dict] = None,
        **kwargs,
    ) -> dict | list | str:
        url = f"{self.base_url}/connections/by-name"
        return await self._async_get_name_request(
            url,
            "Connection",
            self._generate_referenceable_output,
            filter_string=name,
            metadata_element_subtypes=metadata_element_subtypes,
            include_only_relationships=include_only_relationships,
            skip_relationships=skip_relationships,
            graph_query_depth=graph_query_depth,
            start_from=start_from,
            page_size=page_size,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
            **kwargs,
        )

    def get_connections_by_name(
        self,
        name: str,
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        body: Union[FilterRequestBody, dict] = None,
        **kwargs,
    ) -> dict | list | str:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_connections_by_name(
                name=name,
                metadata_element_subtypes=metadata_element_subtypes,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                start_from=start_from,
                page_size=page_size,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs
            )
        )

    async def _async_find_connections(
        self,
        search_string: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = True,
        metadata_element_type: str | None = None,
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        as_of_time: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 0,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        body: Union[SearchStringRequestBody, dict] = None,
        **kwargs,
    ) -> dict | list | str:
        url = f"{self.base_url}/connections/by-search-string"
        return await self._async_find_request(
            url,
            "Connection",
            self._generate_referenceable_output,
            search_string=search_string,
            starts_with=starts_with,
            ends_with=ends_with,
            ignore_case=ignore_case,
            metadata_element_type=metadata_element_type,
            metadata_element_subtypes=metadata_element_subtypes,
            include_only_relationships=include_only_relationships,
            skip_relationships=skip_relationships,
            graph_query_depth=graph_query_depth,
            as_of_time=as_of_time,
            start_from=start_from,
            page_size=page_size,
            sequencing_order=sequencing_order,
            sequencing_property=sequencing_property,
            body=body,
            output_format=output_format,
            report_spec=report_spec,
            **kwargs,
        )

    def find_connections(
        self,
        search_string: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = True,
        metadata_element_type: str | None = None,
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        as_of_time: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 0,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        body: Union[SearchStringRequestBody, dict] = None,
        **kwargs,
    ) -> dict | list | str:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_find_connections(
                search_string=search_string,
                starts_with=starts_with,
                ends_with=ends_with,
                ignore_case=ignore_case,
                metadata_element_type=metadata_element_type,
                metadata_element_subtypes=metadata_element_subtypes,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                as_of_time=as_of_time,
                start_from=start_from,
                page_size=page_size,
                sequencing_order=sequencing_order,
                sequencing_property=sequencing_property,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs
            )
        )

    # --- Connector Types ---

    async def _async_create_connector_type(self, body: Union[NewElementRequestBody, dict]) -> str:
        url = f"{self.base_url}/connector-types"
        return await self._async_create_element_body_request(url, ["ConnectorTypeProperties"], body)

    def create_connector_type(self, body: Union[NewElementRequestBody, dict]) -> str:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_create_connector_type(body))

    async def _async_create_connector_type_from_template(self, body: Union[TemplateRequestBody, dict]) -> str:
        url = f"{self.base_url}/connector-types/from-template"
        return await self._async_create_element_from_template(url, body)

    def create_connector_type_from_template(self, body: Union[TemplateRequestBody, dict]) -> str:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_create_connector_type_from_template(body))

    async def _async_update_connector_type(self, connector_type_guid: str, body: Union[UpdateElementRequestBody, dict]):
        url = f"{self.base_url}/connector-types/{connector_type_guid}/update"
        await self._async_update_element_body_request(url, ["ConnectorTypeProperties"], body)

    def update_connector_type(self, connector_type_guid: str, body: Union[UpdateElementRequestBody, dict]):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_update_connector_type(connector_type_guid, body))

    async def _async_delete_connector_type(self, connector_type_guid: str, body: Union[DeleteElementRequestBody, dict] = None):
        url = f"{self.base_url}/connector-types/{connector_type_guid}/delete"
        await self._async_delete_element_request(url, body)

    def delete_connector_type(self, connector_type_guid: str, body: Union[DeleteElementRequestBody, dict] = None):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_delete_connector_type(connector_type_guid, body))

    async def _async_get_connector_type_by_guid(
        self,
        guid: str,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        body: Union[GetRequestBody, dict] = None,
        **kwargs,
    ) -> dict | list | str:
        url = f"{self.base_url}/connector-types/{guid}/retrieve"
        return await self._async_get_guid_request(
            url,
            "ConnectorType",
            self._generate_referenceable_output,
            include_only_relationships=include_only_relationships,
            skip_relationships=skip_relationships,
            graph_query_depth=graph_query_depth,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
            **kwargs,
        )

    def get_connector_type_by_guid(
        self,
        guid: str,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        body: Union[GetRequestBody, dict] = None,
        **kwargs,
    ) -> dict | list | str:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_connector_type_by_guid(
                guid=guid,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs
            )
        )

    async def _async_get_connector_types_by_name(
        self,
        name: str,
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        body: Union[FilterRequestBody, dict] = None,
        **kwargs,
    ) -> dict | list | str:
        url = f"{self.base_url}/connector-types/by-name"
        return await self._async_get_name_request(
            url,
            "ConnectorType",
            self._generate_referenceable_output,
            filter_string=name,
            metadata_element_subtypes=metadata_element_subtypes,
            include_only_relationships=include_only_relationships,
            skip_relationships=skip_relationships,
            graph_query_depth=graph_query_depth,
            start_from=start_from,
            page_size=page_size,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
            **kwargs,
        )

    def get_connector_types_by_name(
        self,
        name: str,
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        body: Union[FilterRequestBody, dict] = None,
        **kwargs,
    ) -> dict | list | str:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_connector_types_by_name(
                name=name,
                metadata_element_subtypes=metadata_element_subtypes,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                start_from=start_from,
                page_size=page_size,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs
            )
        )

    async def _async_find_connector_types(
        self,
        search_string: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = True,
        metadata_element_type: str | None = None,
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        as_of_time: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 0,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        body: Union[SearchStringRequestBody, dict] = None,
        **kwargs,
    ) -> dict | list | str:
        url = f"{self.base_url}/connector-types/by-search-string"
        return await self._async_find_request(
            url,
            "ConnectorType",
            self._generate_referenceable_output,
            search_string=search_string,
            starts_with=starts_with,
            ends_with=ends_with,
            ignore_case=ignore_case,
            metadata_element_type=metadata_element_type,
            metadata_element_subtypes=metadata_element_subtypes,
            include_only_relationships=include_only_relationships,
            skip_relationships=skip_relationships,
            graph_query_depth=graph_query_depth,
            as_of_time=as_of_time,
            start_from=start_from,
            page_size=page_size,
            sequencing_order=sequencing_order,
            sequencing_property=sequencing_property,
            body=body,
            output_format=output_format,
            report_spec=report_spec,
            **kwargs,
        )

    def find_connector_types(
        self,
        search_string: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = True,
        metadata_element_type: str | None = None,
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        as_of_time: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 0,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        body: Union[SearchStringRequestBody, dict] = None,
        **kwargs,
    ) -> dict | list | str:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_find_connector_types(
                search_string=search_string,
                starts_with=starts_with,
                ends_with=ends_with,
                ignore_case=ignore_case,
                metadata_element_type=metadata_element_type,
                metadata_element_subtypes=metadata_element_subtypes,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                as_of_time=as_of_time,
                start_from=start_from,
                page_size=page_size,
                sequencing_order=sequencing_order,
                sequencing_property=sequencing_property,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs
            )
        )

    # --- Endpoints ---

    async def _async_create_endpoint(self, body: Union[NewElementRequestBody, dict]) -> str:
        url = f"{self.base_url}/endpoints"
        return await self._async_create_element_body_request(url, ["EndpointProperties"], body)

    def create_endpoint(self, body: Union[NewElementRequestBody, dict]) -> str:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_create_endpoint(body))

    async def _async_create_endpoint_from_template(self, body: Union[TemplateRequestBody, dict]) -> str:
        url = f"{self.base_url}/endpoints/from-template"
        return await self._async_create_element_from_template(url, body)

    def create_endpoint_from_template(self, body: Union[TemplateRequestBody, dict]) -> str:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_create_endpoint_from_template(body))

    async def _async_update_endpoint(self, endpoint_guid: str, body: Union[UpdateElementRequestBody, dict]):
        url = f"{self.base_url}/endpoints/{endpoint_guid}/update"
        await self._async_update_element_body_request(url, ["EndpointProperties"], body)

    def update_endpoint(self, endpoint_guid: str, body: Union[UpdateElementRequestBody, dict]):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_update_endpoint(endpoint_guid, body))

    async def _async_delete_endpoint(self, endpoint_guid: str, body: Union[DeleteElementRequestBody, dict] = None):
        url = f"{self.base_url}/endpoints/{endpoint_guid}/delete"
        await self._async_delete_element_request(url, body)

    def delete_endpoint(self, endpoint_guid: str, body: Union[DeleteElementRequestBody, dict] = None):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_delete_endpoint(endpoint_guid, body))

    async def _async_get_endpoint_by_guid(
        self,
        guid: str,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        body: Union[GetRequestBody, dict] = None,
        **kwargs,
    ) -> dict | list | str:
        url = f"{self.base_url}/endpoints/{guid}/retrieve"
        return await self._async_get_guid_request(
            url,
            "Endpoint",
            self._generate_referenceable_output,
            include_only_relationships=include_only_relationships,
            skip_relationships=skip_relationships,
            graph_query_depth=graph_query_depth,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
            **kwargs,
        )

    def get_endpoint_by_guid(
        self,
        guid: str,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        body: Union[GetRequestBody, dict] = None,
        **kwargs,
    ) -> dict | list | str:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_endpoint_by_guid(
                guid=guid,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs
            )
        )

    async def _async_get_endpoints_by_name(
        self,
        name: str,
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        body: Union[FilterRequestBody, dict] = None,
        **kwargs,
    ) -> dict | list | str:
        url = f"{self.base_url}/endpoints/by-name"
        return await self._async_get_name_request(
            url,
            "Endpoint",
            self._generate_referenceable_output,
            filter_string=name,
            metadata_element_subtypes=metadata_element_subtypes,
            include_only_relationships=include_only_relationships,
            skip_relationships=skip_relationships,
            graph_query_depth=graph_query_depth,
            start_from=start_from,
            page_size=page_size,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
            **kwargs,
        )

    def get_endpoints_by_name(
        self,
        name: str,
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        body: Union[FilterRequestBody, dict] = None,
        **kwargs,
    ) -> dict | list | str:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_endpoints_by_name(
                name=name,
                metadata_element_subtypes=metadata_element_subtypes,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                start_from=start_from,
                page_size=page_size,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs
            )
        )

    async def _async_get_endpoints_by_network_address(
        self,
        network_address: str,
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        body: Union[FilterRequestBody, dict] = None,
        **kwargs,
    ) -> dict | list | str:
        url = f"{self.base_url}/endpoints/by-network-address"
        return await self._async_get_name_request(
            url,
            "Endpoint",
            self._generate_referenceable_output,
            filter_string=network_address,
            metadata_element_subtypes=metadata_element_subtypes,
            include_only_relationships=include_only_relationships,
            skip_relationships=skip_relationships,
            graph_query_depth=graph_query_depth,
            start_from=start_from,
            page_size=page_size,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
            **kwargs,
        )

    def get_endpoints_by_network_address(
        self,
        network_address: str,
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        body: Union[FilterRequestBody, dict] = None,
        **kwargs,
    ) -> dict | list | str:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_endpoints_by_network_address(
                network_address=network_address,
                metadata_element_subtypes=metadata_element_subtypes,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                start_from=start_from,
                page_size=page_size,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs
            )
        )

    async def _async_find_endpoints(
        self,
        search_string: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = True,
        metadata_element_type: str | None = None,
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        as_of_time: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 0,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        body: Union[SearchStringRequestBody, dict] = None,
        **kwargs,
    ) -> dict | list | str:
        url = f"{self.base_url}/endpoints/by-search-string"
        return await self._async_find_request(
            url,
            "Endpoint",
            self._generate_referenceable_output,
            search_string=search_string,
            starts_with=starts_with,
            ends_with=ends_with,
            ignore_case=ignore_case,
            metadata_element_type=metadata_element_type,
            metadata_element_subtypes=metadata_element_subtypes,
            include_only_relationships=include_only_relationships,
            skip_relationships=skip_relationships,
            graph_query_depth=graph_query_depth,
            as_of_time=as_of_time,
            start_from=start_from,
            page_size=page_size,
            sequencing_order=sequencing_order,
            sequencing_property=sequencing_property,
            body=body,
            output_format=output_format,
            report_spec=report_spec,
            **kwargs,
        )

    def find_endpoints(
        self,
        search_string: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = True,
        metadata_element_type: str | None = None,
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        as_of_time: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 0,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        body: Union[SearchStringRequestBody, dict] = None,
        **kwargs,
    ) -> dict | list | str:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_find_endpoints(
                search_string=search_string,
                starts_with=starts_with,
                ends_with=ends_with,
                ignore_case=ignore_case,
                metadata_element_type=metadata_element_type,
                metadata_element_subtypes=metadata_element_subtypes,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                as_of_time=as_of_time,
                start_from=start_from,
                page_size=page_size,
                sequencing_order=sequencing_order,
                sequencing_property=sequencing_property,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs
            )
        )

    async def _async_get_endpoints_for_asset(
        self,
        asset_guid: str,
        name: str = "*",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        body: Union[FilterRequestBody, dict] = None,
        **kwargs,
    ) -> dict | list | str:
        url = f"{self.base_url}/assets/{asset_guid}/endpoints/retrieve"
        return await self._async_get_name_request(
            url,
            "Endpoint",
            self._generate_referenceable_output,
            filter_string=name,
            metadata_element_subtypes=metadata_element_subtypes,
            include_only_relationships=include_only_relationships,
            skip_relationships=skip_relationships,
            graph_query_depth=graph_query_depth,
            start_from=start_from,
            page_size=page_size,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
            **kwargs,
        )

    def get_endpoints_for_asset(
        self,
        asset_guid: str,
        name: str = "*",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        body: Union[FilterRequestBody, dict] = None,
        **kwargs,
    ) -> dict | list | str:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_endpoints_for_asset(
                asset_guid=asset_guid,
                name=name,
                metadata_element_subtypes=metadata_element_subtypes,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                start_from=start_from,
                page_size=page_size,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs
            )
        )

    # --- Relationships ---
    #

    async def _async_link_connection_connector_type(self, connection_guid: str, connector_type_guid: str, body: Union[NewRelationshipRequestBody, dict] = None):
        url = f"{self.base_url}/connections/{connection_guid}/connector-types/{connector_type_guid}/attach"
        await self._async_new_relationship_request(url, ["ConnectionConnectorType"], body)

    def link_connection_connector_type(self, connection_guid: str, connector_type_guid: str, body: Union[NewRelationshipRequestBody, dict] = None):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_link_connection_connector_type(connection_guid, connector_type_guid, body))

    async def _async_detach_connection_connector_type(self, connection_guid: str, connector_type_guid: str, body: Union[DeleteRelationshipRequestBody, dict] = None):
        url = f"{self.base_url}/connections/{connection_guid}/connector-types/{connector_type_guid}/detach"
        await self._async_delete_relationship_request(url, body)

    def detach_connection_connector_type(self, connection_guid: str, connector_type_guid: str, body: Union[DeleteRelationshipRequestBody, dict] = None):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_detach_connection_connector_type(connection_guid, connector_type_guid, body))

    async def _async_link_connection_endpoint(self, connection_guid: str, endpoint_guid: str, body: Union[NewRelationshipRequestBody, dict] = None):
        url = f"{self.base_url}/connections/{connection_guid}/endpoints/{endpoint_guid}/attach"
        await self._async_new_relationship_request(url, ["ConnectionEndpoint"], body)

    def link_connection_endpoint(self, connection_guid: str, endpoint_guid: str, body: Union[NewRelationshipRequestBody, dict] = None):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_link_connection_endpoint(connection_guid, endpoint_guid, body))

    async def _async_detach_connection_endpoint(self, connection_guid: str, endpoint_guid: str, body: Union[DeleteRelationshipRequestBody, dict] = None):
        url = f"{self.base_url}/connections/{connection_guid}/endpoints/{endpoint_guid}/detach"
        await self._async_delete_relationship_request(url, body)

    def detach_connection_endpoint(self, connection_guid: str, endpoint_guid: str, body: Union[DeleteRelationshipRequestBody, dict] = None):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_detach_connection_endpoint(connection_guid, endpoint_guid, body))

    async def _async_link_embedded_connection(self, connection_guid: str, embedded_connection_guid: str, body: Union[NewRelationshipRequestBody, dict] = None):
        url = f"{self.base_url}/connections/{connection_guid}/embedded-connections/{embedded_connection_guid}/attach"
        await self._async_new_relationship_request(url, ["EmbeddedConnection"], body)

    def link_embedded_connection(self, connection_guid: str, embedded_connection_guid: str, body: Union[NewRelationshipRequestBody, dict] = None):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_link_embedded_connection(connection_guid, embedded_connection_guid, body))

    async def _async_detach_embedded_connection(self, connection_guid: str, embedded_connection_guid: str, body: Union[DeleteRelationshipRequestBody, dict] = None):
        url = f"{self.base_url}/connections/{connection_guid}/embedded-connections/{embedded_connection_guid}/detach"
        await self._async_delete_relationship_request(url, body)

    def detach_embedded_connection(self, connection_guid: str, embedded_connection_guid: str, body: Union[DeleteRelationshipRequestBody, dict] = None):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_detach_embedded_connection(connection_guid, embedded_connection_guid, body))

    async def _async_link_asset_to_connection(self, asset_guid: str, connection_guid: str, body: Union[NewRelationshipRequestBody, dict] = None):
        url = f"{self.base_url}/assets/{asset_guid}/connections/{connection_guid}/attach"
        await self._async_new_relationship_request(url, ["AssetConnection"], body)

    def link_asset_to_connection(self, asset_guid: str, connection_guid: str, body: Union[NewRelationshipRequestBody, dict] = None):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_link_asset_to_connection(asset_guid, connection_guid, body))

    async def _async_detach_asset_from_connection(self, asset_guid: str, connection_guid: str, body: Union[DeleteRelationshipRequestBody, dict] = None):
        url = f"{self.base_url}/assets/{asset_guid}/connections/{connection_guid}/detach"
        await self._async_delete_relationship_request(url, body)

    def detach_asset_from_connection(self, asset_guid: str, connection_guid: str, body: Union[DeleteRelationshipRequestBody, dict] = None):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_detach_asset_from_connection(asset_guid, connection_guid, body))

    async def _async_link_endpoint_to_it_asset(self, asset_guid: str, endpoint_guid: str, body: Union[NewRelationshipRequestBody, dict] = None):
        url = f"{self.base_url}/assets/{asset_guid}/endpoints/{endpoint_guid}/attach"
        await self._async_new_relationship_request(url, ["ITAssetEndpoint"], body)

    def link_endpoint_to_it_asset(self, asset_guid: str, endpoint_guid: str, body: Union[NewRelationshipRequestBody, dict] = None):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_link_endpoint_to_it_asset(asset_guid, endpoint_guid, body))

    async def _async_detach_endpoint_from_it_asset(self, asset_guid: str, endpoint_guid: str, body: Union[DeleteRelationshipRequestBody, dict] = None):
        url = f"{self.base_url}/assets/{asset_guid}/endpoints/{endpoint_guid}/detach"
        await self._async_delete_relationship_request(url, body)

    def detach_endpoint_from_it_asset(self, asset_guid: str, endpoint_guid: str, body: Union[DeleteRelationshipRequestBody, dict] = None):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_detach_endpoint_from_it_asset(asset_guid, endpoint_guid, body))
