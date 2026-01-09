"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module contains the Jacquard Data Sets View Service client.
"""

import asyncio

from pyegeria.core._server_client import ServerClient
from pyegeria.models import (
    SearchStringRequestBody,
)
from pyegeria.core.utils import dynamic_catch


class JacquardDataSets(ServerClient):
    """
    Client for the Jacquard Data Sets View Service.

    The Jacquard Data Sets View Service provides methods to manage and retrieve tabular data sets.
    Note: Many of these methods are implemented in the Data Engineer View Service.

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
        user_pwd: str = None,
        token: str = None,
    ):
        super().__init__(view_server, platform_url, user_id, user_pwd, token)
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd
        self.url_marker = "data-engineer"

    @dynamic_catch
    async def _async_find_tabular_data_sets(
        self,
        search_string: str = "*",
        body: dict | SearchStringRequestBody = None,
    ) -> list | str:
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/data-engineer/assets/by-search-string"
        if body is None:
            body = {
                "class": "SearchStringRequestBody",
                "searchString": search_string,
                "metadataElementTypeName": "TabularDataSet",
                "skipClassifiedElements": ["Template"],
            }
        response = await self._async_make_request("POST", url, body)
        return response.json().get("elements")

    def find_tabular_data_sets(
        self,
        search_string: str = "*",
        body: dict | SearchStringRequestBody = None,
    ) -> list | str:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_find_tabular_data_sets(search_string, body))

    @dynamic_catch
    async def _async_get_tabular_data_set_report(
        self,
        guid: str,
        start_from_row: int = 0,
        max_row_count: int = 5000,
    ) -> dict | str:
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/data-engineer/tabular-data-sets/{guid}/report?startFromRow={start_from_row}&maxRowCount={max_row_count}"
        response = await self._async_make_request("GET", url)
        return response.json()

    def get_tabular_data_set_report(
        self,
        guid: str,
        start_from_row: int = 0,
        max_row_count: int = 5000,
    ) -> dict | str:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_tabular_data_set_report(guid, start_from_row, max_row_count)
        )

    @dynamic_catch
    async def _async_find_assets_by_name(
        self,
        filter_string: str,
        metadata_element_type_name: str = "ReferenceCodeTable",
        start_from: int = 0,
        page_size: int = 10,
    ) -> list | str:
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/asset-maker/assets/by-name"
        body = {
            "class": "FilterRequestBody",
            "metadataElementTypeName": metadata_element_type_name,
            "filter": filter_string,
            "startFrom": start_from,
            "pageSize": page_size,
        }
        response = await self._async_make_request("POST", url, body)
        return response.json().get("elements")

    def find_assets_by_name(
        self,
        filter_string: str,
        metadata_element_type_name: str = "ReferenceCodeTable",
        start_from: int = 0,
        page_size: int = 10,
    ) -> list | str:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_find_assets_by_name(
                filter_string, metadata_element_type_name, start_from, page_size
            )
        )
