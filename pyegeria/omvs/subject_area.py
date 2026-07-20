"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module contains the Subject Area View Service client.
"""

import asyncio
from typing import Annotated, Literal, Optional

from pydantic import Field

from pyegeria.core._server_client import ServerClient
from pyegeria.models import (
    NewElementRequestBody,
    DeleteElementRequestBody,
    UpdateElementRequestBody,
    TemplateRequestBody,
    FilterRequestBody,
    SearchStringRequestBody,
    GetRequestBody,
    NewRelationshipRequestBody,
    DeleteRelationshipRequestBody,
    ReferenceableProperties,
    RelationshipBeanProperties,
)
from pyegeria.view.output_formatter import (
    populate_common_columns,
    overlay_additional_values,
)
from pyegeria.core.utils import dynamic_catch


class SubjectAreaProperties(ReferenceableProperties):
    class_: Annotated[Literal["SubjectAreaProperties"], Field(alias="class")]
    usage: Optional[str] = None
    scope: Optional[str] = None
    domain_identifier: Optional[int] = None


class SubjectAreaHierarchyProperties(RelationshipBeanProperties):
    class_: Annotated[Literal["SubjectAreaHierarchyProperties"], Field(alias="class")]


class SubjectArea(ServerClient):
    """
    Client for the Subject Area View Service.

    The Subject Area View Service provides methods to manage subject areas and their hierarchies.

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
        timeout: int = None):
        super().__init__(view_server, platform_url, user_id, user_pwd, token, timeout=timeout)
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd
        self.url_marker = "subject-area"

    def _extract_subject_area_properties(self, element: dict, columns_struct: dict) -> dict:
        col_data = populate_common_columns(element, columns_struct)
        props = element.get("properties", {})
        overlay_additional_values(col_data, props)
        return col_data

    def _generate_subject_area_output(
        self,
        elements: dict | list[dict],
        query_string: Optional[str] = None,
        element_type_name: Optional[str] = None,
        output_format: str = "DICT",
        report_spec: dict | str = None,
        **kwargs
    ) -> str | list[dict]:
        return self._generate_formatted_output(
            elements=elements,
            query_string=query_string,
            entity_type=element_type_name or "SubjectArea",
            output_format=output_format,
            extract_properties_func=self._extract_subject_area_properties,
            report_spec=report_spec,
            **kwargs
        )

    @dynamic_catch
    async def _async_create_subject_area(self, body: dict | NewElementRequestBody) -> str:
        """Create a subject area. Async version.

        Parameters
        ----------
        body : dict | NewElementRequestBody
            The properties for the subject area.

        Returns
        -------
        str
            The unique identifier of the newly created subject area.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "NewElementRequestBody",
          "properties": {
            "class" : "SubjectAreaProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "subjectAreaName": "add short name here",
            "description": "add description here",
            "usage": "add usage of this subject area",
            "scope": "add scope of this subject area"
          }
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/subject-area/governance-definitions"
        return await self._async_create_element_body_request(url, "SubjectAreaProperties", body)

    def create_subject_area(self, body: dict | NewElementRequestBody) -> str:
        """Create a subject area.

        Parameters
        ----------
        body : dict | NewElementRequestBody
            The properties for the subject area.

        Returns
        -------
        str
            The unique identifier of the newly created subject area.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "NewElementRequestBody",
          "properties": {
            "class" : "SubjectAreaProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "subjectAreaName": "add short name here",
            "description": "add description here",
            "usage": "add usage of this subject area",
            "scope": "add scope of this subject area"
          }
        }
        ```
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_create_subject_area(body))

    @dynamic_catch
    async def _async_create_subject_area_from_template(self, body: dict | TemplateRequestBody) -> str:
        """Create a subject area from a template. Async version.

        Parameters
        ----------
        body : dict | TemplateRequestBody
            The properties for the new subject area, including the template GUID.

        Returns
        -------
        str
            The unique identifier of the newly created subject area.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "TemplateRequestBody",
          "templateGUID": "add guid here",
          "replacementProperties": {
            "class": "ElementProperties",
            "propertyValueMap" : {
              "description" : {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveValue" : "New description"
              }
            }
          }
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/subject-area/governance-definitions/from-template"
        return await self._async_create_element_body_request(url, "SubjectAreaProperties", body)

    def create_subject_area_from_template(self, body: dict | TemplateRequestBody) -> str:
        """Create a subject area from a template.

        Parameters
        ----------
        body : dict | TemplateRequestBody
            The properties for the new subject area, including the template GUID.

        Returns
        -------
        str
            The unique identifier of the newly created subject area.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "TemplateRequestBody",
          "templateGUID": "add guid here",
          "replacementProperties": {
            "class": "ElementProperties",
            "propertyValueMap" : {
              "description" : {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveValue" : "New description"
              }
            }
          }
        }
        ```
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_create_subject_area_from_template(body))

    @dynamic_catch
    async def _async_update_subject_area(
        self, subject_area_guid: str, body: dict | UpdateElementRequestBody
    ) -> None:
        """Update a subject area. Async version.

        Parameters
        ----------
        subject_area_guid : str
            The unique identifier of the subject area.
        body : dict | UpdateElementRequestBody
            The properties to update.

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
          "class" : "UpdateElementRequestBody",
          "mergeUpdate" : true,
          "properties": {
            "class" : "SubjectAreaProperties",
            "displayName": "Updated Name"
          }
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/subject-area/governance-definitions/{subject_area_guid}/update"
        await self._async_update_element_body_request(url, body)

    def update_subject_area(self, subject_area_guid: str, body: dict | UpdateElementRequestBody) -> None:
        """Update a subject area.

        Parameters
        ----------
        subject_area_guid : str
            The unique identifier of the subject area.
        body : dict | UpdateElementRequestBody
            The properties to update.

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
          "class" : "UpdateElementRequestBody",
          "mergeUpdate" : true,
          "properties": {
            "class" : "SubjectAreaProperties",
            "displayName": "Updated Name"
          }
        }
        ```
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_update_subject_area(subject_area_guid, body))

    @dynamic_catch
    async def _async_delete_subject_area(
        self, subject_area_guid: str, body: dict | DeleteElementRequestBody
    ) -> None:
        """Delete a subject area. Async version.

        Parameters
        ----------
        subject_area_guid : str
            The unique identifier of the subject area.
        body : dict | DeleteElementRequestBody
            The request body for the delete operation.

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
          "class" : "DeleteElementRequestBody",
          "externalSourceName": "add qualified name here"
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/subject-area/governance-definitions/{subject_area_guid}/delete"
        await self._async_delete_element_body_request(url, body)

    def delete_subject_area(self, subject_area_guid: str, body: dict | DeleteElementRequestBody) -> None:
        """Delete a subject area.

        Parameters
        ----------
        subject_area_guid : str
            The unique identifier of the subject area.
        body : dict | DeleteElementRequestBody
            The request body for the delete operation.

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
          "class" : "DeleteElementRequestBody",
          "externalSourceName": "add qualified name here"
        }
        ```
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_delete_subject_area(subject_area_guid, body))

    @dynamic_catch
    async def _async_link_subject_area_hierarchy(
        self,
        parent_subject_area_guid: str,
        nested_subject_area_guid: str,
        body: dict | NewRelationshipRequestBody,
    ) -> None:
        """Link subject areas in a hierarchy. Async version.

        Parameters
        ----------
        parent_subject_area_guid : str
            The unique identifier of the parent subject area.
        nested_subject_area_guid : str
            The unique identifier of the nested subject area.
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
            "class": "SubjectAreaHierarchyProperties"
          }
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/subject-area/subject-areas/{parent_subject_area_guid}/subject-area-hierarchies/{nested_subject_area_guid}/attach"
        await self._async_new_relationship_request(url, ["SubjectAreaHierarchyProperties"], body)

    def link_subject_area_hierarchy(
        self,
        parent_subject_area_guid: str,
        nested_subject_area_guid: str,
        body: dict | NewRelationshipRequestBody,
    ) -> None:
        """Link subject areas in a hierarchy.

        Parameters
        ----------
        parent_subject_area_guid : str
            The unique identifier of the parent subject area.
        nested_subject_area_guid : str
            The unique identifier of the nested subject area.
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
            "class": "SubjectAreaHierarchyProperties"
          }
        }
        ```
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_link_subject_area_hierarchy(
                parent_subject_area_guid, nested_subject_area_guid, body
            )
        )

    @dynamic_catch
    async def _async_detach_subject_area_hierarchy(
        self,
        parent_subject_area_guid: str,
        nested_subject_area_guid: str,
        body: dict | DeleteRelationshipRequestBody,
    ) -> None:
        """Detach subject areas from a hierarchy. Async version.

        Parameters
        ----------
        parent_subject_area_guid : str
            The unique identifier of the parent subject area.
        nested_subject_area_guid : str
            The unique identifier of the nested subject area.
        body : dict | DeleteRelationshipRequestBody
            The request body for the detach operation.

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
          "class" : "DeleteRelationshipRequestBody"
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/subject-area/subject-areas/{parent_subject_area_guid}/subject-area-hierarchies/{nested_subject_area_guid}/detach"
        await self._async_delete_relationship_request(url, body)

    def detach_subject_area_hierarchy(
        self,
        parent_subject_area_guid: str,
        nested_subject_area_guid: str,
        body: dict | DeleteRelationshipRequestBody,
    ) -> None:
        """Detach subject areas from a hierarchy.

        Parameters
        ----------
        parent_subject_area_guid : str
            The unique identifier of the parent subject area.
        nested_subject_area_guid : str
            The unique identifier of the nested subject area.
        body : dict | DeleteRelationshipRequestBody
            The request body for the detach operation.

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
          "class" : "DeleteRelationshipRequestBody"
        }
        ```
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_detach_subject_area_hierarchy(
                parent_subject_area_guid, nested_subject_area_guid, body
            )
        )

    @dynamic_catch
    async def _async_get_subject_areas_by_name(
        self,
        name: str = None,
        metadata_element_type_name: str | None = "SubjectArea",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "SubjectAreas",
        body: Optional[dict | FilterRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Get subject areas by name. Async version.

        Parameters
        ----------
        name : str, optional
            The string to find in the properties.
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
        start_from : int, optional
            The starting index for paged results.
        page_size : int, optional
            The maximum number of results to return.
        output_format : str, optional
            The desired output format.
        report_spec : str | dict, optional
            The desired output columns/fields to include.
        body : dict | FilterRequestBody, optional
            The request body for the search.

        Returns
        -------
        list | str
            The list of matching subject areas or a message if none found.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        # Handle backward-compatible positional or keyword args
        if name is not None and not isinstance(name, str):
            body = name
            name = None

        if name is None:
            name = kwargs.pop("filter_string", None)

        if name is None and body is None:
            name = "*"
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/subject-area/governance-definitions/by-name"
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
            _type="SubjectArea",
            _gen_output=self._generate_subject_area_output,
            **params,
        )

    def get_subject_areas_by_name(
        self,
        name: str = None,
        metadata_element_type_name: str | None = "SubjectArea",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "SubjectAreas",
        body: Optional[dict | FilterRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Get subject areas by name.

        Parameters
        ----------
        name : str, optional
            The string to find in the properties.
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
        start_from : int, optional
            The starting index for paged results.
        page_size : int, optional
            The maximum number of results to return.
        output_format : str, optional
            The desired output format.
        report_spec : str | dict, optional
            The desired output columns/fields to include.
        body : dict | FilterRequestBody, optional
            The request body for the search.

        Returns
        -------
        list | str
            The list of matching subject areas or a message if none found.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
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
            self._async_get_subject_areas_by_name(
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
    async def _async_find_subject_areas(
        self,
        search_string: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = True,
        metadata_element_type_name: str | None = "SubjectArea",
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
        report_spec: Optional[str | dict] = "SubjectAreas",
        body: Optional[dict | SearchStringRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Retrieve the list of subject area metadata elements that contain the search string. Async Version.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all subject areas.
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
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/subject-area/subject-areas/by-search-string"

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
            _type="SubjectArea",
            _gen_output=self._generate_subject_area_output,
            **params,
        )
        return response

    def find_subject_areas(
        self,
        search_string: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = True,
        metadata_element_type_name: str | None = "SubjectArea",
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
        report_spec: Optional[str | dict] = "SubjectAreas",
        body: Optional[dict | SearchStringRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Retrieve the list of subject area metadata elements that contain the search string.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all subject areas.
        starts_with : bool, [default=True], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=True], optional
            Ignore case when searching
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
            self._async_find_subject_areas(
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

    @dynamic_catch
    async def _async_get_subject_area_by_guid(
        self,
        guid: str,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "SubjectAreas",
        body: Optional[dict | GetRequestBody] = None,
        **kwargs,
    ) -> dict | str:
        """Get subject area by GUID. Async version.

        Parameters
        ----------
        guid : str
            The unique identifier of the subject area.
        include_only_relationships : list[str], optional
            The list of relationship type names to include.
        skip_relationships : list[str], optional
            The list of relationship type names to skip.
        graph_query_depth : int, optional
            The query depth for relationships.
        output_format : str, optional
            The desired output format.
        report_spec : str | dict, optional
            The desired output columns/fields to include.
        body : dict | GetRequestBody, optional
            The request body for the search.

        Returns
        -------
        dict | str
            The requested subject area or a message if not found.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/subject-area/governance-definitions/{guid}/retrieve"
        params = {
            "include_only_relationships": include_only_relationships,
            "skip_relationships": skip_relationships,
            "graph_query_depth": graph_query_depth,
            "output_format": output_format,
            "report_spec": report_spec,
            "body": body,
        }
        params.update(kwargs)
        params = {k: v for k, v in params.items() if v is not None}

        return await self._async_get_guid_request(
            url,
            _type="SubjectArea",
            _gen_output=self._generate_subject_area_output,
            **params,
        )

    def get_subject_area_by_guid(
        self,
        guid: str,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "SubjectAreas",
        body: Optional[dict | GetRequestBody] = None,
        **kwargs,
    ) -> dict | str:
        """Get subject area by GUID.

        Parameters
        ----------
        guid : str
            The unique identifier of the subject area.
        include_only_relationships : list[str], optional
            The list of relationship type names to include.
        skip_relationships : list[str], optional
            The list of relationship type names to skip.
        graph_query_depth : int, optional
            The query depth for relationships.
        output_format : str, optional
            The desired output format.
        report_spec : str | dict, optional
            The desired output columns/fields to include.
        body : dict | GetRequestBody, optional
            The request body for the search.

        Returns
        -------
        dict | str
            The requested subject area or a message if not found.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_subject_area_by_guid(
                guid=guid,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs,
            )
        )
