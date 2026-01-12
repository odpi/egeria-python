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

from pyegeria.core._server_client import ServerClient
from pyegeria.models import (
    NewElementRequestBody,
    TemplateRequestBody,
    UpdateElementRequestBody,
    DeleteElementRequestBody,
    FilterRequestBody,
    SearchStringRequestBody,
    GetRequestBody,
)
from pyegeria.core.utils import dynamic_catch


class CommunityMatters(ServerClient):
    """
    Client for the Community Matters View Service.

    The Community Matters View Service provides methods to create and manage communities.

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
    async def _async_find_communities(self, search_string: str = "*",
                                      starts_with: bool = True, ends_with: bool = False,
                                      ignore_case: bool = False,
                                      anchor_domain: str = None,
                                      metadata_element_type: str = None,
                                      metadata_element_subtypes: list[str] = None,
                                      skip_relationships: list[str] = None,
                                      include_only_relationships: list[str] = None,
                                      skip_classified_elements: list[str] = None,
                                      include_only_classified_elements: list[str] = None,
                                      graph_query_depth: int = 3,
                                      governance_zone_filter: list[str] = None, as_of_time: str = None,
                                      effective_time: str = None, relationship_page_size: int = 0,
                                      limit_results_by_status: list[str] = None, sequencing_order: str = None,
                                      sequencing_property: str = None,
                                      output_format: str = "JSON",
                                      report_spec: str | dict = None,
                                      start_from: int = 0, page_size: int = 100,
                                      property_names: list[str] = None,
                                      body: dict | SearchStringRequestBody = None) -> list | str:
        """ Retrieve the list of community metadata elements that contain the search string. Async Version.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all communities.
        starts_with : bool, [default=True], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        anchor_domain: str, optional
            The anchor domain to search in.
        metadata_element_type: str, optional
            The type of metadata element to search for.
        metadata_element_subtypes: list[str], optional
            The subtypes of metadata element to search for.
        skip_relationships: list[str], optional
            The types of relationships to skip.
        include_only_relationships: list[str], optional
            The types of relationships to include.
        skip_classified_elements: list[str], optional
            The types of classified elements to skip.
        include_only_classified_elements: list[str], optional
            The types of classified elements to include.
        graph_query_depth: int, [default=3], optional
            The depth of the graph query.
        governance_zone_filter: list[str], optional
            The governance zones to search in.
        as_of_time: str, optional
            The time to search as of.
        effective_time: str, optional
            The effective time to search at.
        relationship_page_size: int, [default=0], optional
            The page size for relationships.
        limit_results_by_status: list[str], optional
            The statuses to limit results by.
        sequencing_order: str, optional
            The order to sequence results by.
        sequencing_property: str, optional
            The property to sequence results by.
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
        report_spec: str | dict , optional, default = None
            - The desired output columns/fields to include.
        start_from: int, [default=0], optional
            When multiple pages of results are available, the page number to start from.
        page_size: int, [default=100]
            The number of items to return in a single page.
        property_names: list[str], optional
            The names of properties to search for.
        body: dict | SearchStringRequestBody, optional, default = None
            - if provided, the search parameters in the body will supercede other attributes, such as "search_string"

        Returns
        -------
        List | str

        Output depends on the output format specified.

        Raises
        ------

        ValidationError
          If the client passes incorrect parameters on the request that don't conform to the data model.
        PyegeriaException
          Issues raised in communicating or server side processing.
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        url = f"{self.community_command_base}/communities/by-search-string"
        response = await self._async_find_request(url, _type="Community", _gen_output=self._generate_community_output,
                                                  search_string=search_string, starts_with=starts_with,
                                                  ends_with=ends_with, ignore_case=ignore_case,
                                                  anchor_domain=anchor_domain,
                                                  metadata_element_type=metadata_element_type,
                                                  metadata_element_subtypes=metadata_element_subtypes,
                                                  skip_relationships=skip_relationships,
                                                  include_only_relationships=include_only_relationships,
                                                  skip_classified_elements=skip_classified_elements,
                                                  include_only_classified_elements=include_only_classified_elements,
                                                  graph_query_depth=graph_query_depth,
                                                  governance_zone_filter=governance_zone_filter,
                                                  as_of_time=as_of_time, effective_time=effective_time,
                                                  relationship_page_size=relationship_page_size,
                                                  limit_results_by_status=limit_results_by_status,
                                                  sequencing_order=sequencing_order,
                                                  sequencing_property=sequencing_property,
                                                  output_format=output_format, report_spec=report_spec,
                                                  start_from=start_from, page_size=page_size,
                                                  property_names=property_names, body=body)

        return response

    @dynamic_catch
    def find_communities(self, search_string: str = "*",
                         starts_with: bool = True, ends_with: bool = False,
                         ignore_case: bool = False,
                         anchor_domain: str = None,
                         metadata_element_type: str = None,
                         metadata_element_subtypes: list[str] = None,
                         skip_relationships: list[str] = None,
                         include_only_relationships: list[str] = None,
                         skip_classified_elements: list[str] = None,
                         include_only_classified_elements: list[str] = None,
                         graph_query_depth: int = 3,
                         governance_zone_filter: list[str] = None, as_of_time: str = None,
                         effective_time: str = None, relationship_page_size: int = 0,
                         limit_results_by_status: list[str] = None, sequencing_order: str = None,
                         sequencing_property: str = None,
                         output_format: str = "JSON",
                         report_spec: str | dict = None,
                         start_from: int = 0, page_size: int = 100,
                         property_names: list[str] = None,
                         body: dict | SearchStringRequestBody = None) -> list | str:
        """ Retrieve the list of community metadata elements that contain the search string.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all communities.
        starts_with : bool, [default=True], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        anchor_domain: str, optional
            The anchor domain to search in.
        metadata_element_type: str, optional
            The type of metadata element to search for.
        metadata_element_subtypes: list[str], optional
            The subtypes of metadata element to search for.
        skip_relationships: list[str], optional
            The types of relationships to skip.
        include_only_relationships: list[str], optional
            The types of relationships to include.
        skip_classified_elements: list[str], optional
            The types of classified elements to skip.
        include_only_classified_elements: list[str], optional
            The types of classified elements to include.
        graph_query_depth: int, [default=3], optional
            The depth of the graph query.
        governance_zone_filter: list[str], optional
            The governance zones to search in.
        as_of_time: str, optional
            The time to search as of.
        effective_time: str, optional
            The effective time to search at.
        relationship_page_size: int, [default=0], optional
            The page size for relationships.
        limit_results_by_status: list[str], optional
            The statuses to limit results by.
        sequencing_order: str, optional
            The order to sequence results by.
        sequencing_property: str, optional
            The property to sequence results by.
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
        report_spec: str | dict , optional, default = None
            - The desired output columns/fields to include.
        start_from: int, [default=0], optional
            When multiple pages of results are available, the page number to start from.
        page_size: int, [default=100]
            The number of items to return in a single page.
        property_names: list[str], optional
            The names of properties to search for.
        body: dict | SearchStringRequestBody, optional, default = None
            - if provided, the search parameters in the body will supercede other attributes, such as "search_string"

        Returns
-------
        List | str

        Output depends on the output format specified.

        Raises
        ------

        ValidationError
          If the client passes incorrect parameters on the request that don't conform to the data model.
        PyegeriaException
          Issues raised in communicating or server side processing.
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_find_communities(search_string=search_string,
                                                                    starts_with=starts_with,
                                                                    ends_with=ends_with,
                                                                    ignore_case=ignore_case,
                                                                    anchor_domain=anchor_domain,
                                                                    metadata_element_type=metadata_element_type,
                                                                    metadata_element_subtypes=metadata_element_subtypes,
                                                                    skip_relationships=skip_relationships,
                                                                    include_only_relationships=include_only_relationships,
                                                                    skip_classified_elements=skip_classified_elements,
                                                                    include_only_classified_elements=include_only_classified_elements,
                                                                    graph_query_depth=graph_query_depth,
                                                                    governance_zone_filter=governance_zone_filter,
                                                                    as_of_time=as_of_time,
                                                                    effective_time=effective_time,
                                                                    relationship_page_size=relationship_page_size,
                                                                    limit_results_by_status=limit_results_by_status,
                                                                    sequencing_order=sequencing_order,
                                                                    sequencing_property=sequencing_property,
                                                                    output_format=output_format,
                                                                    report_spec=report_spec,
                                                                    start_from=start_from,
                                                                    page_size=page_size,
                                                                    property_names=property_names,
                                                                    body=body))

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
