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
    async def _async_find_annotations(
        self,
        search_string: str = "*",
        classification_names: list[str] = None,
        metadata_element_subtypes: list[str] = None,
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = False,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: str | dict = "Referenceable",
        body: dict | SearchStringRequestBody = None,
    ) -> list | str:
        """Find annotations. Async version.

        Parameters
        ----------
        search_string : str, optional
            The string to search for.
        classification_names : list[str], optional
            The list of classification names to filter by.
        metadata_element_subtypes : list[str], optional
            The list of metadata element subtypes to filter by.
        starts_with : bool, optional
            Whether the search string must be at the start.
        ends_with : bool, optional
            Whether the search string must be at the end.
        ignore_case : bool, optional
            Whether to ignore case in the search.
        start_from : int, optional
            The starting index for paged results.
        page_size : int, optional
            The maximum number of results to return.
        output_format : str, optional
            The desired output format.
        report_spec : str | dict, optional
            The desired output columns/fields to include.
        body : dict | SearchStringRequestBody, optional
            The request body for the search.

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
          "class" : "SearchStringRequestBody",
          "searchString" : "Add value here",
          "startsWith" : true,
          "ignoreCase" : true
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/data-discovery/annotations/by-search-string"
        return await self._async_find_request(
            url,
            _type="Annotation",
            _gen_output=self._generate_annotation_output,
            search_string=search_string,
            classification_names=classification_names,
            metadata_element_subtypes=metadata_element_subtypes,
            starts_with=starts_with,
            ends_with=ends_with,
            ignore_case=ignore_case,
            start_from=start_from,
            page_size=page_size,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )

    def find_annotations(
        self,
        search_string: str = "*",
        classification_names: list[str] = None,
        metadata_element_subtypes: list[str] = None,
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = False,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: str | dict = "Referenceable",
        body: dict | SearchStringRequestBody = None,
    ) -> list | str:
        """Find annotations.

        Parameters
        ----------
        search_string : str, optional
            The string to search for.
        classification_names : list[str], optional
            The list of classification names to filter by.
        metadata_element_subtypes : list[str], optional
            The list of metadata element subtypes to filter by.
        starts_with : bool, optional
            Whether the search string must be at the start.
        ends_with : bool, optional
            Whether the search string must be at the end.
        ignore_case : bool, optional
            Whether to ignore case in the search.
        start_from : int, optional
            The starting index for paged results.
        page_size : int, optional
            The maximum number of results to return.
        output_format : str, optional
            The desired output format.
        report_spec : str | dict, optional
            The desired output columns/fields to include.
        body : dict | SearchStringRequestBody, optional
            The request body for the search.

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
          "class" : "SearchStringRequestBody",
          "searchString" : "Add value here",
          "startsWith" : true,
          "ignoreCase" : true
        }
        ```
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_find_annotations(
                search_string,
                classification_names,
                metadata_element_subtypes,
                starts_with,
                ends_with,
                ignore_case,
                start_from,
                page_size,
                output_format,
                report_spec,
                body,
            )
        )

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
