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
from typing import Any, Optional

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
    async def _async_create_community(self, body: Optional[dict | NewElementRequestBody] = None) -> str:
        url = f"{self.community_command_base}/communities"
        return await self._async_create_element_body_request(url, ["CommunityProperties"], body)

    @dynamic_catch
    def create_community(self, body: Optional[dict | NewElementRequestBody] = None) -> str:
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
        body: Optional[dict | DeleteElementRequestBody] = None,
        cascade: bool = False,
    ) -> None:
        url = f"{self.community_command_base}/communities/{community_guid}/delete"
        await self._async_delete_element_request(url, body, cascade)

    @dynamic_catch
    def delete_community(
        self,
        community_guid: str,
        body: Optional[dict | DeleteElementRequestBody] = None,
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
        search_string: Optional[str] = None,
        element_type_name: Optional[str] = None,
        output_format: str = "JSON",
        report_spec: dict | str | None = None,
        **kwargs
    ) -> Any:
        return self._generate_formatted_output(
            elements=elements,
            query_string=search_string,
            entity_type=element_type_name or "Community",
            output_format=output_format,
            extract_properties_func=self._extract_referenceable_properties,
            report_spec=report_spec,
            **kwargs
        )

    @dynamic_catch
    async def _async_get_communities_by_name(
        self,
        filter_string: str | None = None,
        body: Optional[dict | FilterRequestBody] = None,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: str | dict | None = None,
    ) -> list | str:
        url = f"{self.community_command_base}/communities/by-name"
        response = await self._async_get_name_request(url, _type="Community",
                                                      _gen_output=self._generate_community_output,
                                                      filter_string=filter_string, start_from=start_from,
                                                      page_size=page_size, output_format=output_format,
                                                      report_spec=report_spec, body=body)
        return response

    @dynamic_catch
    def get_communities_by_name(
        self,
        filter_string: str | None = None,
        body: Optional[dict | FilterRequestBody] = None,
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
        body: Optional[dict | SearchStringRequestBody] = None,
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = False,
        start_from: int = 0,
        page_size: int = 100,
        output_format: str = "JSON",
        report_spec: str | dict = None,
        **kwargs
    ) -> list | str:
        """Retrieve the list of community metadata elements that contain the search string. Async Version.

        Parameters
        ----------
        search_string : str, default="*"
            Search string to match against. Use '*' to match all communities.
        body : dict | SearchStringRequestBody, optional
            Request body containing search parameters. If provided, overrides other search parameters.
        starts_with : bool, default=True
            Whether to match communities starting with the search string.
        ends_with : bool, default=False
            Whether to match communities ending with the search string.
        ignore_case : bool, default=False
            Whether to ignore case when searching.
        start_from : int, default=0
            Page number to start from when paginating results.
        page_size : int, default=100
            Number of items to return per page.
        output_format : str, default="JSON"
            Format of the output. Options: "JSON", "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID".
        report_spec : str | dict, optional
            Specification for custom report output columns/fields.
        **kwargs : dict, optional
            Additional parameters supported by the find request:
            
            - anchor_domain (str): The anchor domain to search in
            - metadata_element_type (str): The type of metadata element to search for
            - metadata_element_subtypes (list[str]): The subtypes of metadata element to search for
            - skip_relationships (list[str]): Relationship types to skip
            - include_only_relationships (list[str]): Relationship types to include exclusively
            - skip_classified_elements (list[str]): Classified element types to skip
            - include_only_classified_elements (list[str]): Classified element types to include exclusively
            - graph_query_depth (int): Depth of the graph query (default=3)
            - governance_zone_filter (list[str]): Governance zones to filter by
            - as_of_time (str): Historical time for the query
            - effective_time (str): Effective time for the query
            - relationship_page_size (int): Page size for relationships (default=0)
            - limit_results_by_status (list[str]): Element statuses to filter by
            - sequencing_order (str): Order for sequencing results
            - sequencing_property (str): Property to use for sequencing
            - property_names (list[str]): Property names to search for

        Returns
        -------
        list | str
            List of community metadata elements or formatted string, depending on output_format.

        Raises
        ------
        ValidationError
            If parameters don't conform to the data model.
        PyegeriaException
            If there are issues communicating with the server or processing the request.
        NotAuthorizedException
            If the user is not authorized to perform the requested action.

        """
        url = f"{self.community_command_base}/communities/by-search-string"
        
        # Merge explicit parameters with kwargs
        params = {
            'search_string': search_string,
            'body': body,
            'starts_with': starts_with,
            'ends_with': ends_with,
            'ignore_case': ignore_case,
            'start_from': start_from,
            'page_size': page_size,
            'output_format': output_format,
            'report_spec': report_spec
        }
        params.update(kwargs)
        
        # Filter out None values, but keep search_string even if None (it's required)
        params = {k: v for k, v in params.items() if v is not None or k == 'search_string'}
        
        response = await self._async_find_request(url, _type="Community", _gen_output=self._generate_community_output,
                                                  **params)
        
        return response

    @dynamic_catch
    def find_communities(
        self,
        search_string: str = "*",
        body: Optional[dict | SearchStringRequestBody] = None,
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = False,
        start_from: int = 0,
        page_size: int = 100,
        output_format: str = "JSON",
        report_spec: str | dict = None,
        **kwargs
    ) -> list | str:
        """Retrieve the list of community metadata elements that contain the search string.

        Parameters
        ----------
        search_string : str, default="*"
            Search string to match against. Use '*' to match all communities.
        body : dict | SearchStringRequestBody, optional
            Request body containing search parameters. If provided, overrides other search parameters.
        starts_with : bool, default=True
            Whether to match communities starting with the search string.
        ends_with : bool, default=False
            Whether to match communities ending with the search string.
        ignore_case : bool, default=False
            Whether to ignore case when searching.
        start_from : int, default=0
            Page number to start from when paginating results.
        page_size : int, default=100
            Number of items to return per page.
        output_format : str, default="JSON"
            Format of the output. Options: "JSON", "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID".
        report_spec : str | dict, optional
            Specification for custom report output columns/fields.
        **kwargs : dict, optional
            Additional parameters supported by the find request:
            
            - anchor_domain (str): The anchor domain to search in
            - metadata_element_type (str): The type of metadata element to search for
            - metadata_element_subtypes (list[str]): The subtypes of metadata element to search for
            - skip_relationships (list[str]): Relationship types to skip
            - include_only_relationships (list[str]): Relationship types to include exclusively
            - skip_classified_elements (list[str]): Classified element types to skip
            - include_only_classified_elements (list[str]): Classified element types to include exclusively
            - graph_query_depth (int): Depth of the graph query (default=3)
            - governance_zone_filter (list[str]): Governance zones to filter by
            - as_of_time (str): Historical time for the query
            - effective_time (str): Effective time for the query
            - relationship_page_size (int): Page size for relationships (default=0)
            - limit_results_by_status (list[str]): Element statuses to filter by
            - sequencing_order (str): Order for sequencing results
            - sequencing_property (str): Property to use for sequencing
            - property_names (list[str]): Property names to search for

        Returns
        -------
        list | str
            List of community metadata elements or formatted string, depending on output_format.

        Raises
        ------
        ValidationError
            If parameters don't conform to the data model.
        PyegeriaException
            If there are issues communicating with the server or processing the request.
        NotAuthorizedException
            If the user is not authorized to perform the requested action.

        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_find_communities(
                search_string=search_string,
                body=body,
                starts_with=starts_with,
                ends_with=ends_with,
                ignore_case=ignore_case,
                start_from=start_from,
                page_size=page_size,
                output_format=output_format,
                report_spec=report_spec,
                **kwargs
            )
        )

    # -----------------------------
    # Get by GUID
    # -----------------------------
    @dynamic_catch
    async def _async_get_community_by_guid(
        self,
        community_guid: str,
        body: Optional[dict | GetRequestBody] = None,
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
        body: Optional[dict | GetRequestBody] = None,
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
