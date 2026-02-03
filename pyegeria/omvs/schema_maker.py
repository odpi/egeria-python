"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module contains the Schema Maker View Service client.
"""

import asyncio
from typing import Annotated, Literal, Optional

from pydantic import Field

from pyegeria.core._server_client import ServerClient
from pyegeria.models import (
    NewElementRequestBody,
    DeleteElementRequestBody,
    UpdateElementRequestBody,
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


class SchemaTypeProperties(ReferenceableProperties):
    class_: Annotated[Literal["SchemaTypeProperties"], Field(alias="class")]
    is_deprecated: Optional[bool] = None
    author: Optional[str] = None
    usage: Optional[str] = None
    encoding_standard: Optional[str] = None
    namespace: Optional[str] = None


class SchemaAttributeProperties(ReferenceableProperties):
    class_: Annotated[Literal["SchemaAttributeProperties"], Field(alias="class")]
    element_position: Optional[int] = None
    min_cardinality: Optional[int] = None
    max_cardinality: Optional[int] = None
    allows_duplicate_values: Optional[bool] = None
    is_ordered_values: Optional[bool] = None
    default_value_override: Optional[str] = None
    anchor_guid: Optional[str] = None


class SchemaMaker(ServerClient):
    """
    Client for the Schema Maker View Service.

    The Schema Maker View Service provides methods to manage schema types and schema attributes.

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
        self.url_marker = "schema-maker"

    def _extract_schema_properties(self, element: dict, columns_struct: dict) -> dict:
        col_data = populate_common_columns(element, columns_struct)
        props = element.get("properties", {})
        overlay_additional_values(col_data, props)
        return col_data

    def _generate_schema_output(
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
            self._extract_schema_properties,
            None,
            report_spec,
        )

    # Schema Types

    @dynamic_catch
    async def _async_create_schema_type(self, body: dict | NewElementRequestBody) -> str:
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/schema-types"
        return await self._async_create_element_body_request(url, "SchemaTypeProperties", body)

    def create_schema_type(self, body: dict | NewElementRequestBody) -> str:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_create_schema_type(body))

    @dynamic_catch
    async def _async_update_schema_type(
        self, schema_type_guid: str, body: dict | UpdateElementRequestBody
    ) -> None:
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/schema-types/{schema_type_guid}/update"
        await self._async_update_element_body_request(url, body)

    def update_schema_type(self, schema_type_guid: str, body: dict | UpdateElementRequestBody) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_update_schema_type(schema_type_guid, body))

    @dynamic_catch
    async def _async_delete_schema_type(
        self, schema_type_guid: str, body: dict | DeleteElementRequestBody
    ) -> None:
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/schema-types/{schema_type_guid}/delete"
        await self._async_delete_element_body_request(url, body)

    def delete_schema_type(self, schema_type_guid: str, body: dict | DeleteElementRequestBody) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_delete_schema_type(schema_type_guid, body))

    # Schema Attributes

    @dynamic_catch
    async def _async_create_schema_attribute(self, body: dict | NewElementRequestBody) -> str:
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/schema-attributes"
        return await self._async_create_element_body_request(url, "SchemaAttributeProperties", body)

    def create_schema_attribute(self, body: dict | NewElementRequestBody) -> str:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_create_schema_attribute(body))

    @dynamic_catch
    async def _async_update_schema_attribute(
        self, schema_attribute_guid: str, body: dict | UpdateElementRequestBody
    ) -> None:
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/schema-attributes/{schema_attribute_guid}/update"
        await self._async_update_element_body_request(url, body)

    def update_schema_attribute(
        self, schema_attribute_guid: str, body: dict | UpdateElementRequestBody
    ) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_update_schema_attribute(schema_attribute_guid, body))

    @dynamic_catch
    async def _async_delete_schema_attribute(
        self, schema_attribute_guid: str, body: dict | DeleteElementRequestBody
    ) -> None:
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/schema-attributes/{schema_attribute_guid}/delete"
        await self._async_delete_element_body_request(url, body)

    def delete_schema_attribute(
        self, schema_attribute_guid: str, body: dict | DeleteElementRequestBody
    ) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_delete_schema_attribute(schema_attribute_guid, body))

    @dynamic_catch
    async def _async_find_schema_types(
        self,
        search_string: str = "*",
        body: Optional[dict | SearchStringRequestBody] = None,
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = False,
        start_from: int = 0,
        page_size: int = 100,
        output_format: str = "JSON",
        report_spec: str | dict = "Referenceable",
        **kwargs
    ) -> list | str:
        """ Retrieve the list of schema type metadata elements that contain the search string. Async Version.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all schema types.
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
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/schema-types/by-search-string"
        
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
        
        response = await self._async_find_request(
            url,
            _type="SchemaType",
            _gen_output=self._generate_schema_output,
            **params
        )

        return response

    @dynamic_catch
    def find_schema_types(
        self,
        search_string: str = "*",
        body: Optional[dict | SearchStringRequestBody] = None,
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = False,
        start_from: int = 0,
        page_size: int = 100,
        output_format: str = "JSON",
        report_spec: str | dict = "Referenceable",
        **kwargs
    ) -> list | str:
        """ Retrieve the list of schema type metadata elements that contain the search string.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all schema types.
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
        return loop.run_until_complete(
            self._async_find_schema_types(
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

    @dynamic_catch
    async def _async_get_schema_type_by_guid(
        self,
        schema_type_guid: str,
        element_type: str = "SchemaType",
        body: Optional[dict | GetRequestBody] = None,
        output_format: str = "JSON",
        report_spec: str | dict = "SchemaTypes",
    ) -> dict | str:
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/schema-types/{schema_type_guid}/retrieve"
        return await self._async_get_guid_request(
            url,
            _type=element_type,
            _gen_output=self._generate_schema_output,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )

    def get_schema_type_by_guid(
        self,
        schema_type_guid: str,
        element_type: str = "SchemaType",
        body: Optional[dict | GetRequestBody] = None,
        output_format: str = "JSON",
        report_spec: str | dict = "SchemaTypes",
    ) -> dict | str:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_schema_type_by_guid(
                schema_type_guid, element_type, body, output_format, report_spec
            )
        )
