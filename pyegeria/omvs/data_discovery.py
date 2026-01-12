"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module contains the Data Discovery View Service client.
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
    ReferenceableProperties,
)
from pyegeria.view.output_formatter import (
    generate_output,
    populate_common_columns,
    overlay_additional_values,
)
from pyegeria.core.utils import dynamic_catch


class AnnotationProperties(ReferenceableProperties):
    class_: Annotated[Literal["AnnotationProperties"], Field(alias="class")]
    annotation_type: Optional[str] = None
    summary: Optional[str] = None
    confidence_level: Optional[int] = None
    expression: Optional[str] = None
    explanation: Optional[str] = None
    analysis_step: Optional[str] = None
    json_properties: Optional[str] = None


class DataDiscovery(ServerClient):
    """
    Client for the Data Discovery View Service.

    The Data Discovery View Service provides methods to manage annotations and analysis reports.

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
        self.url_marker = "data-discovery"

    def _extract_annotation_properties(self, element: dict, columns_struct: dict) -> dict:
        col_data = populate_common_columns(element, columns_struct)
        props = element.get("properties", {})
        overlay_additional_values(col_data, props)
        return col_data

    def _generate_annotation_output(
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
            self._extract_annotation_properties,
            None,
            report_spec,
        )

    @dynamic_catch
    async def _async_create_annotation(self, body: dict | NewElementRequestBody) -> str:
        """Create an annotation. Async version.

        Parameters
        ----------
        body : dict | NewElementRequestBody
            The properties for the annotation.

        Returns
        -------
        str
            The unique identifier of the newly created annotation.

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
            "class" : "AnnotationProperties",
            "typeName" : "Annotation",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here"
          }
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/data-discovery/annotations"
        return await self._async_create_element_body_request(url, "AnnotationProperties", body)

    def create_annotation(self, body: dict | NewElementRequestBody) -> str:
        """Create an annotation.

        Parameters
        ----------
        body : dict | NewElementRequestBody
            The properties for the annotation.

        Returns
        -------
        str
            The unique identifier of the newly created annotation.

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
            "class" : "AnnotationProperties",
            "typeName" : "Annotation",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here"
          }
        }
        ```
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_create_annotation(body))

    @dynamic_catch
    async def _async_create_annotation_from_template(self, body: dict | TemplateRequestBody) -> str:
        """Create an annotation from a template. Async version.

        Parameters
        ----------
        body : dict | TemplateRequestBody
            The properties for the new annotation, including the template GUID.

        Returns
        -------
        str
            The unique identifier of the newly created annotation.

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
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/data-discovery/annotations/from-template"
        return await self._async_create_element_body_request(url, "AnnotationProperties", body)

    def create_annotation_from_template(self, body: dict | TemplateRequestBody) -> str:
        """Create an annotation from a template.

        Parameters
        ----------
        body : dict | TemplateRequestBody
            The properties for the new annotation, including the template GUID.

        Returns
        -------
        str
            The unique identifier of the newly created annotation.

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
        return loop.run_until_complete(self._async_create_annotation_from_template(body))

    @dynamic_catch
    async def _async_update_annotation(
        self, annotation_guid: str, body: dict | UpdateElementRequestBody
    ) -> None:
        """Update an annotation. Async version.

        Parameters
        ----------
        annotation_guid : str
            The unique identifier of the annotation.
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
          "mergeUpdate": true,
          "properties": {
            "class" : "AnnotationProperties",
            "displayName": "Updated Name"
          }
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/data-discovery/annotations/{annotation_guid}/update"
        await self._async_update_element_body_request(url, body)

    def update_annotation(self, annotation_guid: str, body: dict | UpdateElementRequestBody) -> None:
        """Update an annotation.

        Parameters
        ----------
        annotation_guid : str
            The unique identifier of the annotation.
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
          "mergeUpdate": true,
          "properties": {
            "class" : "AnnotationProperties",
            "displayName": "Updated Name"
          }
        }
        ```
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_update_annotation(annotation_guid, body))

    @dynamic_catch
    async def _async_delete_annotation(
        self, annotation_guid: str, body: dict | DeleteElementRequestBody
    ) -> None:
        """Delete an annotation. Async version.

        Parameters
        ----------
        annotation_guid : str
            The unique identifier of the annotation.
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
          "cascadedDelete" : false
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/data-discovery/annotations/{annotation_guid}/delete"
        await self._async_delete_element_body_request(url, body)

    def delete_annotation(self, annotation_guid: str, body: dict | DeleteElementRequestBody) -> None:
        """Delete an annotation.

        Parameters
        ----------
        annotation_guid : str
            The unique identifier of the annotation.
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
          "cascadedDelete" : false
        }
        ```
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_delete_annotation(annotation_guid, body))

    @dynamic_catch
    async def _async_get_annotations_by_name(
        self,
        filter_string: str = None,
        classification_names: list[str] = None,
        body: dict | FilterRequestBody = None,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: str | dict = "Annotations",
    ) -> list | str:
        """Get annotations by name. Async version.

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
            The list of matching annotations or a message if none found.

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
          "filter" : "AnnotationName",
          "startFrom": 0,
          "pageSize": 10
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/data-discovery/annotations/by-name"
        return await self._async_get_name_request(
            url,
            _type="Annotation",
            _gen_output=self._generate_annotation_output,
            filter_string=filter_string,
            classification_names=classification_names,
            start_from=start_from,
            page_size=page_size,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )

    def get_annotations_by_name(
        self,
        filter_string: str = None,
        classification_names: list[str] = None,
        body: dict | FilterRequestBody = None,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: str | dict = "Annotations",
    ) -> list | str:
        """Get annotations by name.

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
            The list of matching annotations or a message if none found.

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
          "filter" : "AnnotationName",
          "startFrom": 0,
          "pageSize": 10
        }
        ```
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_annotations_by_name(
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
    async def _async_find_annotations(self, search_string: str = "*",
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
                                      report_spec: str | dict = "Referenceable",
                                      start_from: int = 0, page_size: int = 100,
                                      property_names: list[str] = None,
                                      body: dict | SearchStringRequestBody = None) -> list | str:
        """ Retrieve the list of annotation metadata elements that contain the search string. Async Version.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all annotations.
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
        ------

        ValidationError
          If the client passes incorrect parameters on the request that don't conform to the data model.
        PyegeriaException
          Issues raised in communicating or server side processing.
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/data-discovery/annotations/by-search-string"
        response = await self._async_find_request(url, _type="Annotation", _gen_output=self._generate_annotation_output,
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
    def find_annotations(self, search_string: str = "*",
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
                         report_spec: str | dict = "Referenceable",
                         start_from: int = 0, page_size: int = 100,
                         property_names: list[str] = None,
                         body: dict | SearchStringRequestBody = None) -> list | str:
        """ Retrieve the list of annotation metadata elements that contain the search string.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all annotations.
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
        return loop.run_until_complete(self._async_find_annotations(search_string=search_string,
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
    async def _async_get_annotation_by_guid(
        self,
        annotation_guid: str,
        element_type: str = "Annotation",
        body: dict | GetRequestBody = None,
        output_format: str = "JSON",
        report_spec: str | dict = "Annotations",
    ) -> dict | str:
        """Get annotation by GUID. Async version.

        Parameters
        ----------
        annotation_guid : str
            The unique identifier of the required element.
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
            The requested annotation or a message if not found.

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
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/data-discovery/annotations/{annotation_guid}/retrieve"
        return await self._async_get_guid_request(
            url,
            _type=element_type,
            _gen_output=self._generate_annotation_output,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )

    def get_annotation_by_guid(
        self,
        annotation_guid: str,
        element_type: str = "Annotation",
        body: dict | GetRequestBody = None,
        output_format: str = "JSON",
        report_spec: str | dict = "Annotations",
    ) -> dict | str:
        """Get annotation by GUID.

        Parameters
        ----------
        annotation_guid : str
            The unique identifier of the required element.
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
            The requested annotation or a message if not found.

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
            self._async_get_annotation_by_guid(
                annotation_guid, element_type, body, output_format, report_spec
            )
        )
