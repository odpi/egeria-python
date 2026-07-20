"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides access to the Digital Business OMVS module.

The Digital Business OMVS provides APIs for managing business capabilities and their
relationships to digital resources.
"""

import asyncio
from typing import Optional

from pyegeria.omvs.collection_manager import CollectionManager
from pyegeria.core._server_client import ServerClient
from pyegeria.models import (
    NewElementRequestBody,
    UpdateElementRequestBody,
    DeleteElementRequestBody,
    NewRelationshipRequestBody,
    DeleteRelationshipRequestBody,
    NewClassificationRequestBody,
    DeleteClassificationRequestBody,
    SearchStringRequestBody
)

from pyegeria.core.utils import dynamic_catch, body_slimmer


class DigitalBusiness(CollectionManager):
    """
    Manage business capabilities, their lifecycle, and their digital support relationships.

    This client provides methods to create, update, and manage business capabilities,
    link business capabilities with their dependencies and digital support elements,
    as well as manage business significance classifications.

    Attributes
    ----------
    view_server : str
        The name of the View Server to connect to.
    platform_url : str
        URL of the server platform to connect to.
    user_id : str
        The identity of the user calling the method - this sets a default optionally
        used by the methods when the user doesn't pass the user_id on a method call.
    user_pwd : str, optional
        The password associated with the user_id. Defaults to None.
    token : str, optional
        An optional bearer token for authentication.

    Methods
    -------
    create_business_capability(body)
        Create a new business capability collection.
    update_business_capability(business_capability_guid, body)
        Update the properties of a business capability.
    delete_business_capability(business_capability_guid, body, cascade)
        Delete a business capability.
    get_business_capability_by_guid(business_capability_guid, body, output_format, report_spec)
        Return the properties of a specific business capability by GUID.
    get_business_capabilities_by_name(filter_string, body, start_from, page_size, output_format, report_spec)
        Returns the list of business capabilities with a particular name.
    find_business_capabilities(search_string, starts_with, ends_with, ignore_case, start_from, page_size, output_format, report_spec, body)
        Returns the list of business capabilities matching the search string.
    link_business_capability_dependency(business_capability_guid, supporting_capability_guid, body)
        Link dependent business capabilities.
    detach_business_capability_dependency(business_capability_guid, supporting_capability_guid, body)
        Detach dependent business capabilities.
    link_digital_support(business_capability_guid, element_guid, body)
        Attach a business capability to an element that provides digital support.
    detach_digital_support(business_capability_guid, element_guid, body)
        Detach a business capability from digital support.
    set_business_significant(element_guid, body)
        Classify an element as business significant.
    clear_business_significance(element_guid, body)
        Remove the business significant classification.
    """

    def __init__(
        self,
        view_server: str = None,
        platform_url: str = None,
        user_id: str = None,
        user_pwd: Optional[str] = None,
        token: Optional[str] = None,
        timeout: int = None):
        ServerClient.__init__(self, view_server, platform_url, user_id, user_pwd, token, timeout=timeout)
        self.view_server = self.server_name
        self.platform_url = self.platform_url
        self.user_id = self.user_id
        self.user_pwd = self.user_pwd
        self.digital_business_command_root: str = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/digital-business"
        )

    def _prepare_body(self, body: Optional[dict | NewElementRequestBody | UpdateElementRequestBody |
                                           DeleteElementRequestBody | NewRelationshipRequestBody |
                                           DeleteRelationshipRequestBody | NewClassificationRequestBody |
                                           DeleteClassificationRequestBody]) -> dict | None:
        """Convert Pydantic models to dict and slim the body."""
        if body is None:
            return None
        if isinstance(body, dict):
            return body_slimmer(body)
        # It's a Pydantic model
        return body_slimmer(body.model_dump(mode='json', by_alias=True, exclude_none=True))

    #
    # Business Capability Lifecycle Management
    #

    @dynamic_catch
    async def _async_create_business_capability(
        self,
        body: Optional[dict | NewElementRequestBody],
    ) -> str:
        """Create a new business capability collection. Async version.

        Parameters
        ----------
        body : dict | NewElementRequestBody
            Request body containing business capability properties.

        Returns
        -------
        str
            The GUID of the created business capability.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        ValidationError
            If the body does not conform to NewElementRequestBody.
        PyegeriaNotAuthorizedException
            If the user is not authorized for the requested action.

        Notes
        -----
            JSON Structure looks like:
            {
              "class" : "NewElementRequestBody",
              "typeName": "BusinessCapability",
              "isOwnAnchor" : true,
              "properties": {
                "class" : "BusinessCapabilityProperties",
                "qualifiedName": "BusinessCapability::Add capability name here",
                "displayName" : "Capability name",
                "description" : "Add description of capability here",
                "identifier" : "Add capability identifier here",
                "businessCapabilityType" : "Add type here",
                "additionalProperties": {
                  "property1Name" : "property1Value"
                }
              },
              "effectiveTime" : "timestamp",
              "forLineage" : false,
              "forDuplicateProcessing" : false,
            }
        """
        url = f"{self.digital_business_command_root}/collections"
        return await self._async_create_element_body_request(url, ["BusinessCapabilityProperties"], body)

    def create_business_capability(
        self,
        body: Optional[dict | NewElementRequestBody],
    ) -> str:
        """Create a new business capability collection. Sync version.

        Parameters
        ----------
        body : dict | NewElementRequestBody
            Request body containing business capability properties.

        Returns
        -------
        str
            The GUID of the created business capability.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        body = self._prepare_body(body)
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_create_business_capability(body))

    @dynamic_catch
    async def _async_update_business_capability(
        self,
        business_capability_guid: str,
        body: Optional[dict | UpdateElementRequestBody] = None,
    ) -> None:
        """Update the properties of a business capability. Async version.

        Parameters
        ----------
        business_capability_guid : str
            The GUID of the business capability to update.
        body : dict | UpdateElementRequestBody, optional
            Request body containing updated properties.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        ValidationError
            If the body does not conform to UpdateElementRequestBody.
        PyegeriaNotAuthorizedException
            If the user is not authorized for the requested action.
        """
        url = f"{self.digital_business_command_root}/collections/{business_capability_guid}/update"
        await self._async_update_element_body_request(url, ["BusinessCapabilityProperties"], body)

    def update_business_capability(
        self,
        business_capability_guid: str,
        body: Optional[dict | UpdateElementRequestBody] = None,
    ) -> None:
        """Update the properties of a business capability. Sync version.

        Parameters
        ----------
        business_capability_guid : str
            The GUID of the business capability to update.
        body : dict | UpdateElementRequestBody, optional
            Request body containing updated properties.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        business_capability_guid = str(business_capability_guid)
        body = self._prepare_body(body)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_business_capability(business_capability_guid, body)
        )

    @dynamic_catch
    async def _async_delete_business_capability(
        self,
        business_capability_guid: str,
        body: Optional[dict | DeleteElementRequestBody] = None,
        cascade: bool = False,
    ) -> None:
        """Delete a business capability. Async version.

        Parameters
        ----------
        business_capability_guid : str
            The GUID of the business capability to delete.
        body : dict | DeleteElementRequestBody, optional
            Request body for deletion.
        cascade : bool, optional
            Whether to cascade the delete. Defaults to False.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        ValidationError
            If the body does not conform to DeleteElementRequestBody.
        PyegeriaNotAuthorizedException
            If the user is not authorized for the requested action.
        """
        url = f"{self.digital_business_command_root}/collections/{business_capability_guid}/delete"
        await self._async_delete_element_request(url, body, cascade)

    def delete_business_capability(
        self,
        business_capability_guid: str,
        body: Optional[dict | DeleteElementRequestBody] = None,
        cascade: bool = False,
    ) -> None:
        """Delete a business capability. Sync version.

        Parameters
        ----------
        business_capability_guid : str
            The GUID of the business capability to delete.
        body : dict | DeleteElementRequestBody, optional
            Request body for deletion.
        cascade : bool, optional
            Whether to cascade the delete. Defaults to False.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        business_capability_guid = str(business_capability_guid)
        body = self._prepare_body(body)
        cascade = bool(cascade)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_delete_business_capability(business_capability_guid, body, cascade)
        )

    @dynamic_catch
    async def _async_get_business_capability_by_guid(
        self,
        guid: str,
        graph_query_depth: int = 3, output_format: str = "JSON",
        report_spec: Optional[str | dict] = "BusinessCapabilities",
        body: Optional[dict] = None,
        **kwargs,
    ) -> dict | str:
        """Return the properties of a specific business capability by GUID. Async version.

        Parameters
        ----------
        guid : str
            The GUID of the business capability to retrieve.
        output_format : str, optional
            Format for output. Defaults to "JSON".
        report_spec : str | dict, optional
            Report specification for formatting.
        body : dict, optional
            Request body (typically empty for retrieval).

        Returns
        -------
        dict | str
            The business capability properties.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        PyegeriaNotFoundException
            If the business capability is not found.
        PyegeriaNotAuthorizedException
            If the user is not authorized for the requested action.
        """
        url = f"{self.digital_business_command_root}/collections/{guid}/retrieve"
        params = {
            'graph_query_depth': graph_query_depth,
            "output_format": output_format,
            "report_spec": report_spec,
            "body": body,
        }
        params.update(kwargs)
        params = {k: v for k, v in params.items() if v is not None}
        response = await self._async_get_guid_request(
            url,
            _type="BusinessCapability",
            _gen_output=self._generate_collection_output,
            **params,
        )
        return response

    def get_business_capability_by_guid(
        self,
        guid: str,
        graph_query_depth: int = 3, output_format: str = "JSON",
        report_spec: Optional[str | dict] = "BusinessCapabilities",
        body: Optional[dict] = None,
        **kwargs,
    ) -> dict | str:
        """Return the properties of a specific business capability by GUID. Sync version.

        Parameters
        ----------
        guid : str
            The GUID of the business capability to retrieve.
        output_format : str, optional
            Format for output. Defaults to "JSON".
        report_spec : str | dict, optional
            Report specification for formatting.
        body : dict, optional
            Request body (typically empty for retrieval).

        Returns
        -------
        dict | str
            The business capability properties.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_business_capability_by_guid(
                guid=guid,
                graph_query_depth=graph_query_depth,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs,
            )
        )

    @dynamic_catch
    async def _async_get_business_capabilities_by_name(
        self,
        name: str = None,
        metadata_element_type_name: str | None = "BusinessCapability",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "BusinessCapabilities",
        body: Optional[dict] = None,
        **kwargs,
    ) -> list | str:
        """Returns the list of business capabilities with a particular name. Async version.

        Parameters
        ----------
        name: str, optional
            name to use to find matching business capabilities.
        metadata_element_type_name : str, optional
            The type of metadata element.
        metadata_element_subtypes : list[str], optional
            The list of subtypes to filter by.
        include_only_relationships : list[str], optional
            The list of relationship type names to include.
        skip_relationships : list[str], optional
            The list of relationship type names to skip.
        graph_query_depth : int, optional
            The query depth for relationships.
        start_from: int, [default=0], optional
            When multiple pages of results are available, the page number to start from.
        page_size: int, [default=0]
            The number of items to return in a single page.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
        report_spec: dict, optional, default = "BusinessCapabilities"
            The desired output columns/fields to include.
        body: dict, optional
            Provides a full request body. If specified, the body supercedes other attributes.

        Returns
        -------
        list | str
        """
        # Handle backward-compatible positional or keyword args
        if name is not None and not isinstance(name, str):
            body = name
            name = None

        if name is None:
            name = kwargs.pop("filter_string", None)

        if name is None and body is None:
            name = "*"

        url = f"{self.digital_business_command_root}/collections/by-name"
        params = {
            "filter_string": name,
            "metadata_element_type": metadata_element_type_name,
            "metadata_element_subtypes": metadata_element_subtypes,
            "include_only_relationships": include_only_relationships,
            "skip_relationships": skip_relationships,
            "graph_query_depth": graph_query_depth,
            "start_from": start_from,
            "page_size": page_size,
            "output_format": output_format,
            "report_spec": report_spec,
            "body": body,
        }
        params.update(kwargs)
        params = {k: v for k, v in params.items() if v is not None or k == "filter_string"}

        return await self._async_get_name_request(
            url,
            _type="BusinessCapability",
            _gen_output=self._generate_collection_output,
            **params,
        )

    def get_business_capabilities_by_name(
        self,
        name: str = None,
        metadata_element_type_name: str | None = "BusinessCapability",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "BusinessCapabilities",
        body: Optional[dict] = None,
        **kwargs,
    ) -> list | str:
        """Returns the list of business capabilities with a particular name. Sync version.

        Parameters
        ----------
        name: str, optional
            name to use to find matching business capabilities.
        metadata_element_type_name : str, optional
            The type of metadata element.
        metadata_element_subtypes : list[str], optional
            The list of subtypes to filter by.
        include_only_relationships : list[str], optional
            The list of relationship type names to include.
        skip_relationships : list[str], optional
            The list of relationship type names to skip.
        graph_query_depth : int, optional
            The query depth for relationships.
        start_from: int, [default=0], optional
            When multiple pages of results are available, the page number to start from.
        page_size: int, [default=0]
            The number of items to return in a single page.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
        report_spec: dict, optional, default = "BusinessCapabilities"
            The desired output columns/fields to include.
        body: dict, optional
            Provides a full request body. If specified, the body supercedes other attributes.

        Returns
        -------
        list | str
        """
        # Handle backward-compatible positional or keyword args
        if name is not None and not isinstance(name, str):
            body = name
            name = None

        if name is None:
            name = kwargs.pop("filter_string", None)

        if name is None and body is None:
            name = "*"

        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_business_capabilities_by_name(
                name=name,
                metadata_element_type_name=metadata_element_type_name,
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
        )

    @dynamic_catch
    async def _async_find_business_capabilities(
        self,
        search_string: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = True,
        metadata_element_type_name: str | None = "BusinessCapability",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        as_of_time: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 100,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "BusinessCapabilities",
        body: Optional[dict | SearchStringRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Retrieve the list of business capability metadata elements that contain the search string. Async Version.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all capabilities.
        starts_with : bool, [default=True], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=True], optional
            Ignore case when searching
        metadata_element_type_name: str, optional
            The type of metadata element to search for.
        metadata_element_subtypes: list[str], optional
            The subtypes of metadata element to search for.
        include_only_relationships: list[str], optional
            The types of relationships to include.
        skip_relationships: list[str], optional
            The types of relationships to skip.
        graph_query_depth: int, [default=3], optional
            The depth of the graph query.
        as_of_time: str, optional
            The time to search as of.
        start_from: int, [default=0], optional
            When paged results are available, the starting index.
        page_size: int, [default=100]
            The number of items to return.
        sequencing_order: str, optional
            The order to sequence results by.
        sequencing_property: str, optional
            The property to sequence results by.
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
        report_spec: str | dict, optional
            - The desired output columns/fields to include.
        body: dict | SearchStringRequestBody, optional
            - if provided, the search parameters in the body will supercede other attributes.

        Returns
        -------
        list | str
        """
        url = f"{self.digital_business_command_root}/collections/by-search-string"

        params = {
            "search_string": search_string,
            "starts_with": starts_with,
            "ends_with": ends_with,
            "ignore_case": ignore_case,
            "metadata_element_type": metadata_element_type_name,
            "metadata_element_subtypes": metadata_element_subtypes,
            "include_only_relationships": include_only_relationships,
            "skip_relationships": skip_relationships,
            "graph_query_depth": graph_query_depth,
            "as_of_time": as_of_time,
            "start_from": start_from,
            "page_size": page_size,
            "sequencing_order": sequencing_order,
            "sequencing_property": sequencing_property,
            "output_format": output_format,
            "report_spec": report_spec,
            "body": body,
        }
        params.update(kwargs)
        params = {k: v for k, v in params.items() if v is not None or k == "search_string"}

        response = await self._async_find_request(
            url,
            _type="BusinessCapability",
            _gen_output=self._generate_collection_output,
            **params,
        )
        return response

    def find_business_capabilities(
        self,
        search_string: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = True,
        metadata_element_type_name: str | None = "BusinessCapability",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        as_of_time: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 100,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "BusinessCapabilities",
        body: Optional[dict | SearchStringRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Returns the list of business capabilities matching the search string. Sync version.

        Parameters
        ----------
        search_string : str, optional
            Search string to match. Defaults to "*" (all).
        starts_with : bool, optional
            Whether to match from the start. Defaults to True.
        ends_with : bool, optional
            Whether to match at the end. Defaults to False.
        ignore_case : bool, optional
            Whether to ignore case. Defaults to True.
        metadata_element_type_name : str, optional
            The type of metadata element.
        metadata_element_subtypes : list[str], optional
            The subtypes to filter by.
        include_only_relationships : list[str], optional
            Only include these relationships.
        skip_relationships : list[str], optional
            Relationships to skip in the graph.
        graph_query_depth : int, optional
            The query depth for relationships.
        as_of_time : str, optional
            Historical time for the query.
        start_from : int, optional
            Starting index for pagination. Defaults to 0.
        page_size : int, optional
            Number of results per page. Defaults to 100.
        sequencing_order : str, optional
            Order for sequencing results.
        sequencing_property : str, optional
            Property to sequence by.
        output_format : str, optional
            Format for output. Defaults to "JSON".
        report_spec : str | dict, optional
            Report specification for formatting.
        body : dict, optional
            Request body for additional parameters.

        Returns
        -------
        list | str
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_find_business_capabilities(
                search_string=search_string,
                starts_with=starts_with,
                ends_with=ends_with,
                ignore_case=ignore_case,
                metadata_element_type_name=metadata_element_type_name,
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
                **kwargs,
            )
        )

    #
    # Business Capability Dependency Management
    #

    @dynamic_catch
    async def _async_link_business_capability_dependency(
        self,
        business_capability_guid: str,
        supporting_capability_guid: str,
        body: Optional[dict | NewRelationshipRequestBody] = None,
    ) -> None:
        """Link dependent business capabilities. Async version.

        Parameters
        ----------
        business_capability_guid : str
            The GUID of the business capability that depends on another.
        supporting_capability_guid : str
            The GUID of the supporting business capability.
        body : dict | NewRelationshipRequestBody, optional
            Request body containing relationship properties.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        ValidationError
            If the body does not conform to NewRelationshipRequestBody.
        PyegeriaNotAuthorizedException
            If the user is not authorized for the requested action.
        """
        url = (
            f"{self.digital_business_command_root}/business-capabilities/"
            f"{business_capability_guid}/dependencies/{supporting_capability_guid}/attach"
        )
        await self._async_new_relationship_request(url=url, prop=['BusinessCapabilityDependencyProperties'],body=body)

    def link_business_capability_dependency(
        self,
        business_capability_guid: str,
        supporting_capability_guid: str,
        body: Optional[dict | NewRelationshipRequestBody] = None,
    ) -> None:
        """Link dependent business capabilities. Sync version.

        Parameters
        ----------
        business_capability_guid : str
            The GUID of the business capability that depends on another.
        supporting_capability_guid : str
            The GUID of the supporting business capability.
        body : dict | NewRelationshipRequestBody, optional
            Request body containing relationship properties.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_link_business_capability_dependency(
                business_capability_guid, supporting_capability_guid, body
            )
        )

    @dynamic_catch
    async def _async_detach_business_capability_dependency(
        self,
        business_capability_guid: str,
        supporting_capability_guid: str,
        body: Optional[dict | DeleteRelationshipRequestBody] = None,
        cascade: bool = False,
    ) -> None:
        """Detach dependent business capabilities. Async version.

        Parameters
        ----------
        business_capability_guid : str
            The GUID of the business capability.
        supporting_capability_guid : str
            The GUID of the supporting business capability to detach.
        body : dict | DeleteRelationshipRequestBody, optional
            Request body for deletion.
        cascade : bool, optional, default=False
            Whether to cascade delete dependent elements.
        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        """
        url = (
            f"{self.digital_business_command_root}/business-capabilities/"
            f"{business_capability_guid}/dependencies/{supporting_capability_guid}/detach"
        )
        await self._async_delete_relationship_request(url=url, body=body, cascade_delete=cascade)

    def detach_business_capability_dependency(
        self,
        business_capability_guid: str,
        supporting_capability_guid: str,
        body: Optional[dict | DeleteRelationshipRequestBody] = None,
        cascade: bool = False,
    ) -> None:
        """Detach dependent business capabilities. Sync version.

        Parameters
        ----------
        business_capability_guid : str
            The GUID of the business capability.
        supporting_capability_guid : str
            The GUID of the supporting business capability to detach.
        body : dict | DeleteRelationshipRequestBody, optional
            Request body for deletion.
        cascade : bool, optional, default=False
            Whether to cascade delete dependent elements.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_detach_business_capability_dependency(business_capability_guid, supporting_capability_guid,
                                                              body, cascade)
        )

    #
    # Digital Support Management
    #

    @dynamic_catch
    async def _async_link_digital_support(
        self,
        business_capability_guid: str,
        element_guid: str,
        body: Optional[dict | NewRelationshipRequestBody] = None,
    ) -> None:
        """Attach a business capability to an element that provides digital support. Async version.

        Parameters
        ----------
        business_capability_guid : str
            The GUID of the business capability.
        element_guid : str
            The GUID of the element providing digital support.
        body : dict | NewRelationshipRequestBody, optional
            Request body containing relationship properties.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        url = (
            f"{self.digital_business_command_root}/business-capabilities/"
            f"{business_capability_guid}/digital-support/{element_guid}/attach"
        )
        await self._async_new_relationship_request(url=url, prop=['DigitalSupportProperties'],body=body)

    def link_digital_support(
        self,
        business_capability_guid: str,
        element_guid: str,
        body: Optional[dict | NewRelationshipRequestBody] = None,
    ) -> None:
        """Attach a business capability to an element that provides digital support. Sync version.

        Parameters
        ----------
        business_capability_guid : str
            The GUID of the business capability.
        element_guid : str
            The GUID of the element providing digital support.
        body : dict | NewRelationshipRequestBody, optional
            Request body containing relationship properties.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_link_digital_support(business_capability_guid, element_guid, body)
        )

    @dynamic_catch
    async def _async_detach_digital_support(
        self,
        business_capability_guid: str,
        element_guid: str,
        body: Optional[dict | DeleteRelationshipRequestBody] = None,
        cascade: bool = False,
    ) -> None:
        """Detach a business capability from digital support. Async version.

        Parameters
        ----------
        business_capability_guid : str
            The GUID of the business capability.
        element_guid : str
            The GUID of the digital support element to detach.
        body : dict | DeleteRelationshipRequestBody, optional
            Request body for deletion.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Args:
            cascade ():
        """
        url = (
            f"{self.digital_business_command_root}/business-capabilities/"
            f"{business_capability_guid}/digital-support/{element_guid}/detach"
        )
        await self._async_delete_relationship_request(url, self._prepare_body(body), cascade)

    def detach_digital_support(
        self,
        business_capability_guid: str,
        element_guid: str,
        body: Optional[dict | DeleteRelationshipRequestBody] = None,
        cascade: bool = False,
    ) -> None:
        """Detach a business capability from digital support. Sync version.

        Parameters
        ----------
        business_capability_guid : str
            The GUID of the business capability.
        element_guid : str
            The GUID of the digital support element to detach.
        body : dict | DeleteRelationshipRequestBody, optional
            Request body for deletion.
        cascade: bool, default False
            If true, will perform a cascade delete.
        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.


        Args:
            cascade ():
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_detach_digital_support(business_capability_guid, element_guid, body, cascade)
        )

    #
    # Business Significance Classification
    #

    @dynamic_catch
    async def _async_set_business_significant(
        self,
        element_guid: str,
        body: Optional[dict | NewClassificationRequestBody] = None,
    ) -> None:
        """Classify an element as business significant. Async version.

        Parameters
        ----------
        element_guid : str
            The GUID of the element to classify.
        body : dict | NewClassificationRequestBody, optional
            Request body containing classification properties.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        url = f"{self.digital_business_command_root}/elements/{element_guid}/business-significant"
        await self._async_new_classification_request(url=url, prop = ['BusinessSignificantProperties'],body=body)

    def set_business_significant(
        self,
        element_guid: str,
        body: Optional[dict | NewClassificationRequestBody] = None,
    ) -> None:
        """Classify an element as business significant. Sync version.

        Parameters
        ----------
        element_guid : str
            The GUID of the element to classify.
        body : dict | NewClassificationRequestBody, optional
            Request body containing classification properties.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_set_business_significant(element_guid, body))

    @dynamic_catch
    async def _async_clear_business_significance(
        self,
        element_guid: str,
        body: Optional[dict | DeleteClassificationRequestBody] = None,
    ) -> None:
        """Remove the business significant classification. Async version.

        Parameters
        ----------
        element_guid : str
            The GUID of the element to declassify.
        body : dict | DeleteClassificationRequestBody, optional
            Request body for deletion.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        url = f"{self.digital_business_command_root}/elements/{element_guid}/business-significant/remove"
        await self._async_delete_classification_request(url=url,body=body,)

    def clear_business_significance(
        self,
        element_guid: str,
        body: Optional[dict | DeleteClassificationRequestBody] = None,
    ) -> None:
        """Remove the business significant classification. Sync version.

        Parameters
        ----------
        element_guid : str
            The GUID of the element to declassify.
        body : dict | DeleteClassificationRequestBody, optional
            Request body for deletion.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_clear_business_significance(element_guid, body))