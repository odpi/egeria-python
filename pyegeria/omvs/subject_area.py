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
    generate_output,
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
    ):
        super().__init__(view_server, platform_url, user_id, user_pwd, token)
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
        filter: Optional[str],
        element_type_name: Optional[str],
        output_format: str = "DICT",
        report_spec: dict | str = None,
    ) -> str | list[dict]:
        return generate_output(
            elements,
            filter,
            element_type_name,
            output_format,
            self._extract_subject_area_properties,
            None,
            report_spec,
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
        filter_string: Optional[str] = None,
        classification_names: Optional[list[str]] = None,
        body: Optional[dict | FilterRequestBody] = None,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: str | dict = "SubjectAreas",
    ) -> list | str:
        """Get subject areas by name. Async version.

        Parameters
        ----------
        filter_string : str, optional
            The string to find in the properties.
        classification_names : list[str], optional
            The list of classification names to filter by.
        body : dict | FilterRequestBody, optional
            The request body for the search.
        start_from : int, optional
            The starting index for paged results.
        page_size : int, optional
            The maximum number of results to return.
        output_format : str, optional
            The desired output format.
        report_spec : str | dict, optional
            The desired output columns/fields to include.

        Returns
        -------
        list | str
            The list of matching subject areas or a message if none found.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "FilterRequestBody",
          "filter" : "AreaName",
          "metadataElementTypeName": "SubjectAreaDefinition"
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/subject-area/governance-definitions/by-name"
        return await self._async_get_name_request(
            url,
            _type="SubjectArea",
            _gen_output=self._generate_subject_area_output,
            filter_string=filter_string,
            classification_names=classification_names,
            start_from=start_from,
            page_size=page_size,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )

    def get_subject_areas_by_name(
        self,
        filter_string: Optional[str] = None,
        classification_names: Optional[list[str]] = None,
        body: Optional[dict | FilterRequestBody] = None,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: str | dict = "SubjectAreas",
    ) -> list | str:
        """Get subject areas by name.

        Parameters
        ----------
        filter_string : str, optional
            The string to find in the properties.
        classification_names : list[str], optional
            The list of classification names to filter by.
        body : dict | FilterRequestBody, optional
            The request body for the search.
        start_from : int, optional
            The starting index for paged results.
        page_size : int, optional
            The maximum number of results to return.
        output_format : str, optional
            The desired output format.
        report_spec : str | dict, optional
            The desired output columns/fields to include.

        Returns
        -------
        list | str
            The list of matching subject areas or a message if none found.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "FilterRequestBody",
          "filter" : "AreaName",
          "metadataElementTypeName": "SubjectAreaDefinition"
        }
        ```
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_subject_areas_by_name(
                filter_string,
                classification_names,
                body,
                start_from,
                page_size,
                output_format,
                report_spec,
            )
        )

    @dynamic_catch
    async def _async_find_subject_areas(self, search_string: str = "*",
                                        starts_with: bool = True, ends_with: bool = False,
                                        ignore_case: bool = False,
                                        anchor_domain: Optional[str] = None,
                                        metadata_element_type: Optional[str] = None,
                                        metadata_element_subtypes: Optional[list[str]] = None,
                                        skip_relationships: Optional[list[str]] = None,
                                        include_only_relationships: Optional[list[str]] = None,
                                        skip_classified_elements: Optional[list[str]] = None,
                                        include_only_classified_elements: Optional[list[str]] = None,
                                        graph_query_depth: int = 3,
                                        governance_zone_filter: Optional[list[str]] = None, as_of_time: Optional[str] = None,
                                        effective_time: Optional[str] = None, relationship_page_size: int = 0,
                                        limit_results_by_status: Optional[list[str]] = None, sequencing_order: Optional[str] = None,
                                        sequencing_property: Optional[str] = None,
                                        output_format: str = "JSON",
                                        report_spec: str | dict = "Referenceable",
                                        start_from: int = 0, page_size: int = 100,
                                        property_names: Optional[list[str]] = None,
                                        body: Optional[dict | SearchStringRequestBody] = None) -> list | str:
        """ Retrieve the list of subject area metadata elements that contain the search string. Async Version.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all subject areas.
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
        report_spec: str | dict , optional, default = "Referenceable"
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
-------

        ValidationError
          If the client passes incorrect parameters on the request that don't conform to the data model.
        PyegeriaException
          Issues raised in communicating or server side processing.
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/subject-area/subject-areas/by-search-string"
        response = await self._async_find_request(url, _type="SubjectArea", _gen_output=self._generate_subject_area_output,
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
    def find_subject_areas(self, search_string: str = "*",
                           starts_with: bool = True, ends_with: bool = False,
                           ignore_case: bool = False,
                           anchor_domain: Optional[str] = None,
                           metadata_element_type: Optional[str] = None,
                           metadata_element_subtypes: Optional[list[str]] = None,
                           skip_relationships: Optional[list[str]] = None,
                           include_only_relationships: Optional[list[str]] = None,
                           skip_classified_elements: Optional[list[str]] = None,
                           include_only_classified_elements: Optional[list[str]] = None,
                           graph_query_depth: int = 3,
                           governance_zone_filter: Optional[list[str]] = None, as_of_time: Optional[str] = None,
                           effective_time: Optional[str] = None, relationship_page_size: int = 0,
                           limit_results_by_status: Optional[list[str]] = None, sequencing_order: Optional[str] = None,
                           sequencing_property: Optional[str] = None,
                           output_format: str = "JSON",
                           report_spec: str | dict = "Referenceable",
                           start_from: int = 0, page_size: int = 100,
                           property_names: Optional[list[str]] = None,
                           body: Optional[dict | SearchStringRequestBody] = None) -> list | str:
        """ Retrieve the list of subject area metadata elements that contain the search string.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all subject areas.
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
        report_spec: str | dict , optional, default = "Referenceable"
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
-------

        ValidationError
          If the client passes incorrect parameters on the request that don't conform to the data model.
        PyegeriaException
          Issues raised in communicating or server side processing.
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_find_subject_areas(search_string=search_string,
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

    @dynamic_catch
    async def _async_get_subject_area_by_guid(
        self,
        subject_area_guid: str,
        element_type: str = "SubjectArea",
        body: Optional[dict | GetRequestBody] = None,
        output_format: str = "JSON",
        report_spec: str | dict = "SubjectAreas",
    ) -> dict | str:
        """Get subject area by GUID. Async version.

        Parameters
        ----------
        subject_area_guid : str
            The unique identifier of the subject area.
        element_type : str, optional
            The type of metadata element.
        body : dict | GetRequestBody, optional
            The request body for the search.
        output_format : str, optional
            The desired output format.
        report_spec : str | dict, optional
            The desired output columns/fields to include.

        Returns
        -------
        dict | str
            The requested subject area or a message if not found.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "GetRequestBody",
          "forLineage" : false
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/subject-area/governance-definitions/{subject_area_guid}/retrieve"
        return await self._async_get_guid_request(
            url,
            _type=element_type,
            _gen_output=self._generate_subject_area_output,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )

    def get_subject_area_by_guid(
        self,
        subject_area_guid: str,
        element_type: str = "SubjectArea",
        body: Optional[dict | GetRequestBody] = None,
        output_format: str = "JSON",
        report_spec: str | dict = "SubjectAreas",
    ) -> dict | str:
        """Get subject area by GUID.

        Parameters
        ----------
        subject_area_guid : str
            The unique identifier of the subject area.
        element_type : str, optional
            The type of metadata element.
        body : dict | GetRequestBody, optional
            The request body for the search.
        output_format : str, optional
            The desired output format.
        report_spec : str | dict, optional
            The desired output columns/fields to include.

        Returns
        -------
        dict | str
            The requested subject area or a message if not found.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "GetRequestBody",
          "forLineage" : false
        }
        ```
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_subject_area_by_guid(
                subject_area_guid, element_type, body, output_format, report_spec
            )
        )
