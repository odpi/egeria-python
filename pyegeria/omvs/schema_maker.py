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
        user_pwd: str = None,
        token: str = None,
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
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/schema-types/by-search-string"
        return await self._async_find_request(
            url,
            _type="SchemaType",
            _gen_output=self._generate_schema_output,
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

    def find_schema_types(
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
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_find_schema_types(
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
    async def _async_get_schema_type_by_guid(
        self,
        schema_type_guid: str,
        element_type: str = "SchemaType",
        body: dict | GetRequestBody = None,
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
        body: dict | GetRequestBody = None,
        output_format: str = "JSON",
        report_spec: str | dict = "SchemaTypes",
    ) -> dict | str:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_schema_type_by_guid(
                schema_type_guid, element_type, body, output_format, report_spec
            )
        )
