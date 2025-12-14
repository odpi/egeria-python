"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Community Matters OMVS client.

This module provides a lightweight client for the Community Matters View Service
endpoints as documented in Egeria-community-matters-omvs.http. It follows the
established patterns used by other OMVS clients (for example, location_arena.py
and project_manager.py), reusing the ServerClient helper methods for request
validation and transport.
"""

import asyncio
from typing import Any

from loguru import logger

from pyegeria._server_client import ServerClient
from pyegeria.models import (
    NewElementRequestBody,
    TemplateRequestBody,
    UpdateElementRequestBody,
    DeleteElementRequestBody,
    FilterRequestBody,
    SearchStringRequestBody,
    GetRequestBody,
)
from pyegeria.utils import dynamic_catch


class CommunityMatters(ServerClient):
    """Client for the Community Matters OMVS.

    Endpoints covered (POST semantics for all):
      - /communities                          -> create
      - /communities/from-template            -> create from template
      - /communities/{guid}/update            -> update
      - /communities/{guid}/delete            -> delete
      - /communities/by-name                  -> get by name
      - /communities/by-search-string         -> find
      - /communities/{guid}/retrieve          -> get by guid
    """

    def __init__(
        self,
        view_server: str,
        platform_url: str,
        user_id: str,
        user_pwd: str | None = None,
        token: str | None = None,
    ):
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd
        self.community_command_base: str = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/community-matters"
        )
        # url_marker only used by some generic helpers (e.g., update status) not used here
        self.url_marker = "community-matters"
        ServerClient.__init__(self, view_server, platform_url, user_id, user_pwd, token)

    # -----------------------------
    # Create
    # -----------------------------
    @dynamic_catch
    async def _async_create_community(self, body: dict | NewElementRequestBody = None) -> str:
        url = f"{self.community_command_base}/communities"
        return await self._async_create_element_body_request(url, ["CommunityProperties"], body)

    @dynamic_catch
    def create_community(self, body: dict | NewElementRequestBody = None) -> str:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_create_community(body))

    # -----------------------------
    # Create from template
    # -----------------------------
    @dynamic_catch
    async def _async_create_community_from_template(self, body: dict | TemplateRequestBody) -> str:
        url = f"{self.community_command_base}/communities/from-template"
        return await self._async_create_element_from_template(url, body)

    @dynamic_catch
    def create_community_from_template(self, body: dict | TemplateRequestBody) -> str:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_create_community_from_template(body))

    # -----------------------------
    # Update
    # -----------------------------
    @dynamic_catch
    async def _async_update_community(self, community_guid: str, body: dict | UpdateElementRequestBody) -> None:
        url = f"{self.community_command_base}/communities/{community_guid}/update"
        await self._async_update_element_body_request(url, ["CommunityProperties"], body)

    @dynamic_catch
    def update_community(self, community_guid: str, body: dict | UpdateElementRequestBody) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_update_community(community_guid, body))

    # -----------------------------
    # Delete
    # -----------------------------
    @dynamic_catch
    async def _async_delete_community(
        self,
        community_guid: str,
        body: dict | DeleteElementRequestBody = None,
        cascade: bool = False,
    ) -> None:
        url = f"{self.community_command_base}/communities/{community_guid}/delete"
        await self._async_delete_element_request(url, body, cascade)

    @dynamic_catch
    def delete_community(
        self,
        community_guid: str,
        body: dict | DeleteElementRequestBody = None,
        cascade: bool = False,
    ) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_delete_community(community_guid, body, cascade))

    # -----------------------------
    # Get by name
    # -----------------------------
    def _generate_community_output(
        self,
        elements: dict | list[dict],
        filter_or_search: str | None,
        element_type_name: str | None,
        output_format: str = "JSON",
        report_spec: dict | str | None = None,
    ) -> Any:
        # Minimal implementation: return JSON elements unchanged for now.
        # Extend later to provide markdown/DICT formatting with output_formatter if needed.
        return elements

    @dynamic_catch
    async def _async_get_communities_by_name(
        self,
        filter_string: str | None = None,
        body: dict | FilterRequestBody = None,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: str | dict | None = None,
    ) -> list | str:
        url = f"{self.community_command_base}/communities/by-name"
        response = await self._async_get_name_request(
            url,
            _type="Community",
            _gen_output=self._generate_community_output,
            filter_string=filter_string,
            start_from=start_from,
            page_size=page_size,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )
        return response

    @dynamic_catch
    def get_communities_by_name(
        self,
        filter_string: str | None = None,
        body: dict | FilterRequestBody = None,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: str | dict | None = None,
    ) -> list | str:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_communities_by_name(
                filter_string,
                body,
                start_from,
                page_size,
                output_format,
                report_spec,
            )
        )

    # -----------------------------
    # Find by search string
    # -----------------------------
    @dynamic_catch
    async def _async_find_communities(
        self,
        search_string: str = "*",
        body: dict | SearchStringRequestBody = None,
        starts_with: bool = False,
        ends_with: bool = False,
        ignore_case: bool = True,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: str | dict | None = None,
    ) -> list | str:
        url = f"{self.community_command_base}/communities/by-search-string"
        response = await self._async_find_request(url, _type="Community", _gen_output=self._generate_community_output,
                                                  search_string=search_string, starts_with=starts_with,
                                                  ends_with=ends_with, ignore_case=ignore_case, start_from=start_from,
                                                  page_size=page_size, output_format=output_format,
                                                  report_spec=report_spec, body=body)
        return response

    @dynamic_catch
    def find_communities(
        self,
        search_string: str = "*",
        body: dict | SearchStringRequestBody = None,
        starts_with: bool = False,
        ends_with: bool = False,
        ignore_case: bool = True,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: str | dict | None = None,
    ) -> list | str:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_find_communities(
                search_string,
                body,
                starts_with,
                ends_with,
                ignore_case,
                start_from,
                page_size,
                output_format,
                report_spec,
            )
        )

    # -----------------------------
    # Get by GUID
    # -----------------------------
    @dynamic_catch
    async def _async_get_community_by_guid(
        self,
        community_guid: str,
        body: dict | GetRequestBody = None,
        output_format: str = "JSON",
        report_spec: str | dict | None = None,
    ) -> dict | str:
        url = f"{self.community_command_base}/communities/{community_guid}/retrieve"
        response = await self._async_get_guid_request(
            url,
            _type="Community",
            _gen_output=self._generate_community_output,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )
        return response

    @dynamic_catch
    def get_community_by_guid(
        self,
        community_guid: str,
        body: dict | GetRequestBody = None,
        output_format: str = "JSON",
        report_spec: str | dict | None = None,
    ) -> dict | str:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_community_by_guid(
                community_guid,
                body,
                output_format,
                report_spec,
            )
        )
