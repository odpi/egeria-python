"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module contains the Schema Maker View Service client.
"""

import asyncio
from typing import Annotated, Literal, Optional

from pydantic import Field

from loguru import logger

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
    MetadataSourceRequestBody,
    NewRelationshipRequestBody,
    DeleteRelationshipRequestBody,
    NewClassificationRequestBody,
    DeleteClassificationRequestBody,
)
from pyegeria.view.output_formatter import (
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
        timeout: int = None):
        super().__init__(view_server, platform_url, user_id, user_pwd, token, timeout=timeout)
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
        filter_string: Optional[str] = None,
        element_type_name: Optional[str] = None,
        output_format: str = "DICT",
        report_spec: dict | str | None = None,
        **kwargs,
    ) -> str | list[dict]:
        return self._generate_formatted_output(
            elements=elements,
            query_string=filter_string,
            element_type_name=element_type_name or "SchemaType",
            output_format=output_format,
            report_spec=report_spec,
            extract_properties_func=self._extract_schema_properties,
            **kwargs,
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
        self, schema_type_guid: str, body: dict | MetadataSourceRequestBody
    ) -> None:
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/schema-types/{schema_type_guid}/delete"
        await self._async_metadata_source_body_request(url, body)

    def delete_schema_type(self, schema_type_guid: str, body: dict | MetadataSourceRequestBody) -> None:
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
        self, schema_attribute_guid: str, body: dict | MetadataSourceRequestBody
    ) -> None:
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/schema-attributes/{schema_attribute_guid}/delete"
        await self._async_metadata_source_body_request(url, body)

    def delete_schema_attribute(
        self, schema_attribute_guid: str, body: dict | MetadataSourceRequestBody
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
        graph_query_depth: int = 3, output_format: str = "JSON",
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
            'graph_query_depth': graph_query_depth,
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
        
        response = await self._async_find_request(url, _type="SchemaType", _gen_output=self._generate_schema_output,
                                                  **params)

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
        graph_query_depth: int = 3, output_format: str = "JSON",
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
                graph_query_depth=graph_query_depth,
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
    @dynamic_catch
    async def _async_get_schema_type_by_guid(
        self,
        guid: str,
        element_type: str = "SchemaType",
        body: Optional[dict | GetRequestBody] = None,
        graph_query_depth: int = 3, output_format: str = "JSON",
        report_spec: str | dict = "SchemaTypes",
        **kwargs,
    ) -> dict | str:
        if guid is None and "schema_type_guid" in kwargs:
            guid = kwargs.pop("schema_type_guid")

        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/schema-types/{guid}/retrieve"
        
        params = {
            'graph_query_depth': graph_query_depth,
            'output_format': output_format,
            'report_spec': report_spec,
            'body': body
        }
        params.update(kwargs)
        params = {k: v for k, v in params.items() if v is not None}

        return await self._async_get_guid_request(
            url,
            _type=element_type,
            _gen_output=self._generate_schema_output,
            **params,
        )

    def get_schema_type_by_guid(
        self,
        guid: str,
        element_type: str = "SchemaType",
        body: Optional[dict | GetRequestBody] = None,
        graph_query_depth: int = 3, output_format: str = "JSON",
        report_spec: str | dict = "SchemaTypes",
        **kwargs,
    ) -> dict | str:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_schema_type_by_guid(
                graph_query_depth=graph_query_depth,
                guid=guid, element_type=element_type, body=body, output_format=output_format, report_spec=report_spec,
                **kwargs,
            )
        )

    @dynamic_catch
    async def _async_create_schema_type_from_template(self, body: dict | TemplateRequestBody) -> str:
        """Create a schema type from a template. Async version."""
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/schema-types/from-template"
        return await self._async_create_element_from_template(url, body)

    def create_schema_type_from_template(self, body: dict | TemplateRequestBody) -> str:
        """Create a schema type from a template."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_create_schema_type_from_template(body))

    @dynamic_catch
    async def _async_create_schema_attribute_from_template(self, body: dict | TemplateRequestBody) -> str:
        """Create a schema attribute from a template. Async version."""
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/schema-attributes/from-template"
        return await self._async_create_element_from_template(url, body)

    def create_schema_attribute_from_template(self, body: dict | TemplateRequestBody) -> str:
        """Create a schema attribute from a template."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_create_schema_attribute_from_template(body))

    @dynamic_catch
    async def _async_get_schema_types_by_name(self, name: str, start_from: int = 0, page_size: int = 100, **kwargs) -> list | str:
        """Get schema types by name. Async version."""
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/schema-types/by-name"
        return await self._async_get_name_request(url, _type="SchemaType", _gen_output=self._generate_schema_output, name=name, start_from=start_from, page_size=page_size, **kwargs)

    def get_schema_types_by_name(self, name: str, start_from: int = 0, page_size: int = 100, **kwargs) -> list | str:
        """Get schema types by name."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_get_schema_types_by_name(name, start_from, page_size, **kwargs))

    @dynamic_catch
    async def _async_get_schema_attributes_by_name(self, name: str, start_from: int = 0, page_size: int = 100, **kwargs) -> list | str:
        """Get schema attributes by name. Async version."""
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/schema-attributes/by-name"
        return await self._async_get_name_request(url, _type="SchemaAttribute", _gen_output=self._generate_schema_output, name=name, start_from=start_from, page_size=page_size, **kwargs)

    def get_schema_attributes_by_name(self, name: str, start_from: int = 0, page_size: int = 100, **kwargs) -> list | str:
        """Get schema attributes by name."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_get_schema_attributes_by_name(name, start_from, page_size, **kwargs))

    @dynamic_catch
    async def _async_find_schema_attributes(self, search_string: str = "*", start_from: int = 0, page_size: int = 100, **kwargs) -> list | str:
        """Find schema attributes. Async version."""
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/schema-attributes/by-search-string"
        return await self._async_find_request(url, _type="SchemaAttribute", _gen_output=self._generate_schema_output, search_string=search_string, start_from=start_from, page_size=page_size, **kwargs)

    def find_schema_attributes(self, search_string: str = "*", start_from: int = 0, page_size: int = 100, **kwargs) -> list | str:
        """Find schema attributes."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_find_schema_attributes(search_string, start_from, page_size, **kwargs))

    @dynamic_catch
    async def _async_get_schema_attribute_by_guid(self, guid: str, **kwargs) -> dict | str:
        """Get schema attribute by GUID. Async version."""
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/schema-attributes/{guid}/retrieve"
        return await self._async_get_guid_request(url, _type="SchemaAttribute", _gen_output=self._generate_schema_output, **kwargs)

    def get_schema_attribute_by_guid(self, guid: str, **kwargs) -> dict | str:
        """Get schema attribute by GUID."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_get_schema_attribute_by_guid(guid, **kwargs))

    #
    # Relationship and classification maintenance - added to close the gap
    # found by scripts/omvs_audit.py against the schema-maker .http ground
    # truth (2026-08-21). Every pair below follows the same shape as
    # DataDesigner._async_link_nested_data_field/_async_detach_nested_data_field.
    #

    @dynamic_catch
    async def _async_link_nested_schema_attribute(self, schema_attribute_guid: str, nested_schema_attribute_guid: str,
                                                   body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach a nested schema attribute to its parent schema attribute (NestedSchemaAttribute relationship). Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"schema-attributes/{schema_attribute_guid}/nested-schema-attributes/{nested_schema_attribute_guid}/attach")
        await self._async_new_relationship_request(url, ["NestedSchemaAttributeProperties"], body)
        logger.info(f"Nested schema attribute {nested_schema_attribute_guid} linked to parent {schema_attribute_guid}.")

    @dynamic_catch
    def link_nested_schema_attribute(self, schema_attribute_guid: str, nested_schema_attribute_guid: str,
                                     body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach a nested schema attribute to its parent schema attribute (NestedSchemaAttribute relationship)."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_nested_schema_attribute(schema_attribute_guid, nested_schema_attribute_guid, body))

    @dynamic_catch
    async def _async_detach_nested_schema_attribute(self, schema_attribute_guid: str, nested_schema_attribute_guid: str,
                                                     body: Optional[dict | DeleteRelationshipRequestBody] = None,
                                                     cascade_delete: bool = False) -> None:
        """Detach a nested schema attribute from its parent schema attribute. Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"schema-attributes/{schema_attribute_guid}/nested-schema-attributes/{nested_schema_attribute_guid}/detach")
        await self._async_delete_relationship_request(url, body, cascade_delete)
        logger.info(f"Nested schema attribute {nested_schema_attribute_guid} detached from parent {schema_attribute_guid}.")

    @dynamic_catch
    def detach_nested_schema_attribute(self, schema_attribute_guid: str, nested_schema_attribute_guid: str,
                                       body: Optional[dict | DeleteRelationshipRequestBody] = None,
                                       cascade_delete: bool = False) -> None:
        """Detach a nested schema attribute from its parent schema attribute."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_nested_schema_attribute(
            schema_attribute_guid, nested_schema_attribute_guid, body, cascade_delete))

    @dynamic_catch
    async def _async_link_attribute_for_schema(self, schema_type_guid: str, schema_attribute_guid: str,
                                               body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach a schema attribute to the schema type that it belongs to (AttributeForSchema relationship). Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"schema-types/{schema_type_guid}/attribute-for-schema/{schema_attribute_guid}/attach")
        await self._async_new_relationship_request(url, ["AttributeForSchemaProperties"], body)
        logger.info(f"Schema attribute {schema_attribute_guid} linked to schema type {schema_type_guid}.")

    @dynamic_catch
    def link_attribute_for_schema(self, schema_type_guid: str, schema_attribute_guid: str,
                                  body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach a schema attribute to the schema type that it belongs to (AttributeForSchema relationship)."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_attribute_for_schema(schema_type_guid, schema_attribute_guid, body))

    @dynamic_catch
    async def _async_detach_attribute_for_schema(self, schema_type_guid: str, schema_attribute_guid: str,
                                                 body: Optional[dict | DeleteRelationshipRequestBody] = None,
                                                 cascade_delete: bool = False) -> None:
        """Detach a schema attribute from the schema type that it belongs to. Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"schema-types/{schema_type_guid}/attribute-for-schema/{schema_attribute_guid}/detach")
        await self._async_delete_relationship_request(url, body, cascade_delete)
        logger.info(f"Schema attribute {schema_attribute_guid} detached from schema type {schema_type_guid}.")

    @dynamic_catch
    def detach_attribute_for_schema(self, schema_type_guid: str, schema_attribute_guid: str,
                                    body: Optional[dict | DeleteRelationshipRequestBody] = None,
                                    cascade_delete: bool = False) -> None:
        """Detach a schema attribute from the schema type that it belongs to."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_attribute_for_schema(
            schema_type_guid, schema_attribute_guid, body, cascade_delete))

    @dynamic_catch
    async def _async_link_foreign_key(self, primary_key_column_guid: str, foreign_key_column_guid: str,
                                      body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach a foreign key column to the primary key column that it refers to (ForeignKey relationship). Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"schema-attributes/{primary_key_column_guid}/foreign-keys/{foreign_key_column_guid}/attach")
        await self._async_new_relationship_request(url, ["ForeignKeyProperties"], body)
        logger.info(f"Foreign key column {foreign_key_column_guid} linked to primary key column {primary_key_column_guid}.")

    @dynamic_catch
    def link_foreign_key(self, primary_key_column_guid: str, foreign_key_column_guid: str,
                         body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach a foreign key column to the primary key column that it refers to (ForeignKey relationship)."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_foreign_key(primary_key_column_guid, foreign_key_column_guid, body))

    @dynamic_catch
    async def _async_detach_foreign_key(self, primary_key_column_guid: str, foreign_key_column_guid: str,
                                        body: Optional[dict | DeleteRelationshipRequestBody] = None,
                                        cascade_delete: bool = False) -> None:
        """Detach a foreign key column from the primary key column that it refers to. Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"schema-attributes/{primary_key_column_guid}/foreign-keys/{foreign_key_column_guid}/detach")
        await self._async_delete_relationship_request(url, body, cascade_delete)
        logger.info(f"Foreign key column {foreign_key_column_guid} detached from primary key column {primary_key_column_guid}.")

    @dynamic_catch
    def detach_foreign_key(self, primary_key_column_guid: str, foreign_key_column_guid: str,
                           body: Optional[dict | DeleteRelationshipRequestBody] = None,
                           cascade_delete: bool = False) -> None:
        """Detach a foreign key column from the primary key column that it refers to."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_foreign_key(
            primary_key_column_guid, foreign_key_column_guid, body, cascade_delete))

    @dynamic_catch
    async def _async_link_external_schema_type(self, schema_element_guid: str, schema_type_guid: str,
                                                body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach a schema element to a reusable, externally-defined schema type (LinkedExternalSchemaType relationship). Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"schema-elements/{schema_element_guid}/linked-external-schema-types/{schema_type_guid}/attach")
        await self._async_new_relationship_request(url, ["LinkedExternalSchemaTypeProperties"], body)
        logger.info(f"External schema type {schema_type_guid} linked to schema element {schema_element_guid}.")

    @dynamic_catch
    def link_external_schema_type(self, schema_element_guid: str, schema_type_guid: str,
                                  body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach a schema element to a reusable, externally-defined schema type (LinkedExternalSchemaType relationship)."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_external_schema_type(schema_element_guid, schema_type_guid, body))

    @dynamic_catch
    async def _async_detach_external_schema_type(self, schema_element_guid: str, schema_type_guid: str,
                                                  body: Optional[dict | DeleteRelationshipRequestBody] = None,
                                                  cascade_delete: bool = False) -> None:
        """Detach a schema element from a reusable, externally-defined schema type. Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"schema-elements/{schema_element_guid}/linked-external-schema-types/{schema_type_guid}/detach")
        await self._async_delete_relationship_request(url, body, cascade_delete)
        logger.info(f"External schema type {schema_type_guid} detached from schema element {schema_element_guid}.")

    @dynamic_catch
    def detach_external_schema_type(self, schema_element_guid: str, schema_type_guid: str,
                                    body: Optional[dict | DeleteRelationshipRequestBody] = None,
                                    cascade_delete: bool = False) -> None:
        """Detach a schema element from a reusable, externally-defined schema type."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_external_schema_type(
            schema_element_guid, schema_type_guid, body, cascade_delete))

    @dynamic_catch
    async def _async_link_map_from_schema_type(self, schema_element_guid: str, schema_type_guid: str,
                                                body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach the 'from' end of a map schema type (MapFromElementType relationship). Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"schema-elements/{schema_element_guid}/map-from-element-types/{schema_type_guid}/attach")
        await self._async_new_relationship_request(url, ["MapFromElementTypeProperties"], body)
        logger.info(f"Map-from schema type {schema_type_guid} linked to schema element {schema_element_guid}.")

    @dynamic_catch
    def link_map_from_schema_type(self, schema_element_guid: str, schema_type_guid: str,
                                  body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach the 'from' end of a map schema type (MapFromElementType relationship)."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_map_from_schema_type(schema_element_guid, schema_type_guid, body))

    @dynamic_catch
    async def _async_detach_map_from_schema_type(self, schema_element_guid: str, schema_type_guid: str,
                                                  body: Optional[dict | DeleteRelationshipRequestBody] = None,
                                                  cascade_delete: bool = False) -> None:
        """Detach the 'from' end of a map schema type. Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"schema-elements/{schema_element_guid}/map-from-element-types/{schema_type_guid}/detach")
        await self._async_delete_relationship_request(url, body, cascade_delete)
        logger.info(f"Map-from schema type {schema_type_guid} detached from schema element {schema_element_guid}.")

    @dynamic_catch
    def detach_map_from_schema_type(self, schema_element_guid: str, schema_type_guid: str,
                                    body: Optional[dict | DeleteRelationshipRequestBody] = None,
                                    cascade_delete: bool = False) -> None:
        """Detach the 'from' end of a map schema type."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_map_from_schema_type(
            schema_element_guid, schema_type_guid, body, cascade_delete))

    @dynamic_catch
    async def _async_link_map_to_schema_type(self, schema_element_guid: str, schema_type_guid: str,
                                              body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach the 'to' end of a map schema type (MapToElementType relationship). Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"schema-elements/{schema_element_guid}/map-to-element-types/{schema_type_guid}/attach")
        await self._async_new_relationship_request(url, ["MapToElementTypeProperties"], body)
        logger.info(f"Map-to schema type {schema_type_guid} linked to schema element {schema_element_guid}.")

    @dynamic_catch
    def link_map_to_schema_type(self, schema_element_guid: str, schema_type_guid: str,
                                body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach the 'to' end of a map schema type (MapToElementType relationship)."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_map_to_schema_type(schema_element_guid, schema_type_guid, body))

    @dynamic_catch
    async def _async_detach_map_to_schema_type(self, schema_element_guid: str, schema_type_guid: str,
                                                body: Optional[dict | DeleteRelationshipRequestBody] = None,
                                                cascade_delete: bool = False) -> None:
        """Detach the 'to' end of a map schema type. Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"schema-elements/{schema_element_guid}/map-to-element-types/{schema_type_guid}/detach")
        await self._async_delete_relationship_request(url, body, cascade_delete)
        logger.info(f"Map-to schema type {schema_type_guid} detached from schema element {schema_element_guid}.")

    @dynamic_catch
    def detach_map_to_schema_type(self, schema_element_guid: str, schema_type_guid: str,
                                  body: Optional[dict | DeleteRelationshipRequestBody] = None,
                                  cascade_delete: bool = False) -> None:
        """Detach the 'to' end of a map schema type."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_map_to_schema_type(
            schema_element_guid, schema_type_guid, body, cascade_delete))

    @dynamic_catch
    async def _async_link_graph_edge(self, graph_edge_guid: str, graph_vertex_guid: str,
                                     body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach a graph edge to one of the vertices it connects (GraphEdgeLink relationship). Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"graph-edges/{graph_edge_guid}/graph-vertices/{graph_vertex_guid}/attach")
        await self._async_new_relationship_request(url, ["GraphEdgeLinkProperties"], body)
        logger.info(f"Graph edge {graph_edge_guid} linked to graph vertex {graph_vertex_guid}.")

    @dynamic_catch
    def link_graph_edge(self, graph_edge_guid: str, graph_vertex_guid: str,
                        body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach a graph edge to one of the vertices it connects (GraphEdgeLink relationship)."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_graph_edge(graph_edge_guid, graph_vertex_guid, body))

    @dynamic_catch
    async def _async_detach_graph_edge(self, graph_edge_guid: str, graph_vertex_guid: str,
                                       body: Optional[dict | DeleteRelationshipRequestBody] = None,
                                       cascade_delete: bool = False) -> None:
        """Detach a graph edge from one of the vertices it connects. Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"graph-edges/{graph_edge_guid}/graph-vertices/{graph_vertex_guid}/detach")
        await self._async_delete_relationship_request(url, body, cascade_delete)
        logger.info(f"Graph edge {graph_edge_guid} detached from graph vertex {graph_vertex_guid}.")

    @dynamic_catch
    def detach_graph_edge(self, graph_edge_guid: str, graph_vertex_guid: str,
                          body: Optional[dict | DeleteRelationshipRequestBody] = None,
                          cascade_delete: bool = False) -> None:
        """Detach a graph edge from one of the vertices it connects."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_graph_edge(
            graph_edge_guid, graph_vertex_guid, body, cascade_delete))

    @dynamic_catch
    async def _async_link_query_target(self, schema_element_guid: str, query_target_schema_element_guid: str,
                                       body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach a query target to a derived schema element (DerivedSchemaTypeQueryTarget relationship). Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"schema-elements/{schema_element_guid}/query-targets/{query_target_schema_element_guid}/attach")
        await self._async_new_relationship_request(url, ["DerivedSchemaTypeQueryTargetProperties"], body)
        logger.info(f"Query target {query_target_schema_element_guid} linked to schema element {schema_element_guid}.")

    @dynamic_catch
    def link_query_target(self, schema_element_guid: str, query_target_schema_element_guid: str,
                          body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach a query target to a derived schema element (DerivedSchemaTypeQueryTarget relationship)."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_query_target(schema_element_guid, query_target_schema_element_guid, body))

    @dynamic_catch
    async def _async_detach_query_target(self, schema_element_guid: str, query_target_schema_element_guid: str,
                                         body: Optional[dict | DeleteRelationshipRequestBody] = None,
                                         cascade_delete: bool = False) -> None:
        """Detach a query target from a derived schema element. Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"schema-elements/{schema_element_guid}/query-targets/{query_target_schema_element_guid}/detach")
        await self._async_delete_relationship_request(url, body, cascade_delete)
        logger.info(f"Query target {query_target_schema_element_guid} detached from schema element {schema_element_guid}.")

    @dynamic_catch
    def detach_query_target(self, schema_element_guid: str, query_target_schema_element_guid: str,
                            body: Optional[dict | DeleteRelationshipRequestBody] = None,
                            cascade_delete: bool = False) -> None:
        """Detach a query target from a derived schema element."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_query_target(
            schema_element_guid, query_target_schema_element_guid, body, cascade_delete))

    @dynamic_catch
    async def _async_link_schema(self, element_guid: str, schema_type_guid: str,
                                 body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach a schema type to the element it describes (SchemaTypeAssociation relationship). Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"elements/{element_guid}/schema-types/{schema_type_guid}/attach")
        await self._async_new_relationship_request(url, ["SchemaProperties"], body)
        logger.info(f"Schema type {schema_type_guid} linked to element {element_guid}.")

    @dynamic_catch
    def link_schema(self, element_guid: str, schema_type_guid: str,
                    body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach a schema type to the element it describes (SchemaTypeAssociation relationship)."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_schema(element_guid, schema_type_guid, body))

    @dynamic_catch
    async def _async_detach_schema(self, element_guid: str, schema_type_guid: str,
                                   body: Optional[dict | DeleteRelationshipRequestBody] = None,
                                   cascade_delete: bool = False) -> None:
        """Detach a schema type from the element it describes. Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"elements/{element_guid}/schema-types/{schema_type_guid}/detach")
        await self._async_delete_relationship_request(url, body, cascade_delete)
        logger.info(f"Schema type {schema_type_guid} detached from element {element_guid}.")

    @dynamic_catch
    def detach_schema(self, element_guid: str, schema_type_guid: str,
                      body: Optional[dict | DeleteRelationshipRequestBody] = None,
                      cascade_delete: bool = False) -> None:
        """Detach a schema type from the element it describes."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_schema(
            element_guid, schema_type_guid, body, cascade_delete))

    @dynamic_catch
    async def _async_link_relational_db_schema(self, database_schema_type_list_guid: str, relational_db_schema_type_guid: str,
                                               body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach a relational database schema to the schema type list it belongs to (RelationalDBSchema relationship). Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"relational-db-schema-type-lists/{database_schema_type_list_guid}/relational-db-schemas/{relational_db_schema_type_guid}/attach")
        await self._async_new_relationship_request(url, ["RelationalDBSchemaProperties"], body)
        logger.info(f"Relational DB schema {relational_db_schema_type_guid} linked to schema type list {database_schema_type_list_guid}.")

    @dynamic_catch
    def link_relational_db_schema(self, database_schema_type_list_guid: str, relational_db_schema_type_guid: str,
                                  body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach a relational database schema to the schema type list it belongs to (RelationalDBSchema relationship)."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_relational_db_schema(
            database_schema_type_list_guid, relational_db_schema_type_guid, body))

    @dynamic_catch
    async def _async_detach_relational_db_schema(self, database_schema_type_list_guid: str, relational_db_schema_type_guid: str,
                                                  body: Optional[dict | DeleteRelationshipRequestBody] = None,
                                                  cascade_delete: bool = False) -> None:
        """Detach a relational database schema from the schema type list it belongs to. Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"relational-db-schema-type-lists/{database_schema_type_list_guid}/relational-db-schemas/{relational_db_schema_type_guid}/detach")
        await self._async_delete_relationship_request(url, body, cascade_delete)
        logger.info(f"Relational DB schema {relational_db_schema_type_guid} detached from schema type list {database_schema_type_list_guid}.")

    @dynamic_catch
    def detach_relational_db_schema(self, database_schema_type_list_guid: str, relational_db_schema_type_guid: str,
                                    body: Optional[dict | DeleteRelationshipRequestBody] = None,
                                    cascade_delete: bool = False) -> None:
        """Detach a relational database schema from the schema type list it belongs to."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_relational_db_schema(
            database_schema_type_list_guid, relational_db_schema_type_guid, body, cascade_delete))

    @dynamic_catch
    async def _async_link_api_operations(self, api_schema_type_guid: str, api_operation_guid: str,
                                         body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach an API operation to the API schema type it belongs to (APIOperations relationship). Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"api-schema-types/{api_schema_type_guid}/api-operations/{api_operation_guid}/attach")
        await self._async_new_relationship_request(url, ["APIOperationsProperties"], body)
        logger.info(f"API operation {api_operation_guid} linked to API schema type {api_schema_type_guid}.")

    @dynamic_catch
    def link_api_operations(self, api_schema_type_guid: str, api_operation_guid: str,
                            body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach an API operation to the API schema type it belongs to (APIOperations relationship)."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_api_operations(api_schema_type_guid, api_operation_guid, body))

    @dynamic_catch
    async def _async_detach_api_operations(self, api_schema_type_guid: str, api_operation_guid: str,
                                           body: Optional[dict | DeleteRelationshipRequestBody] = None,
                                           cascade_delete: bool = False) -> None:
        """Detach an API operation from the API schema type it belongs to. Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"api-schema-types/{api_schema_type_guid}/api-operations/{api_operation_guid}/detach")
        await self._async_delete_relationship_request(url, body, cascade_delete)
        logger.info(f"API operation {api_operation_guid} detached from API schema type {api_schema_type_guid}.")

    @dynamic_catch
    def detach_api_operations(self, api_schema_type_guid: str, api_operation_guid: str,
                              body: Optional[dict | DeleteRelationshipRequestBody] = None,
                              cascade_delete: bool = False) -> None:
        """Detach an API operation from the API schema type it belongs to."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_api_operations(
            api_schema_type_guid, api_operation_guid, body, cascade_delete))

    @dynamic_catch
    async def _async_link_api_header(self, api_operation_guid: str, schema_type_guid: str,
                                     body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach a schema type as the header for an API operation (APIHeader relationship). Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"api-operations/{api_operation_guid}/api-headers/{schema_type_guid}/attach")
        await self._async_new_relationship_request(url, ["APIHeaderProperties"], body)
        logger.info(f"API header schema type {schema_type_guid} linked to API operation {api_operation_guid}.")

    @dynamic_catch
    def link_api_header(self, api_operation_guid: str, schema_type_guid: str,
                        body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach a schema type as the header for an API operation (APIHeader relationship)."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_api_header(api_operation_guid, schema_type_guid, body))

    @dynamic_catch
    async def _async_detach_api_header(self, api_operation_guid: str, schema_type_guid: str,
                                       body: Optional[dict | DeleteRelationshipRequestBody] = None,
                                       cascade_delete: bool = False) -> None:
        """Detach a schema type as the header for an API operation. Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"api-operations/{api_operation_guid}/api-headers/{schema_type_guid}/detach")
        await self._async_delete_relationship_request(url, body, cascade_delete)
        logger.info(f"API header schema type {schema_type_guid} detached from API operation {api_operation_guid}.")

    @dynamic_catch
    def detach_api_header(self, api_operation_guid: str, schema_type_guid: str,
                          body: Optional[dict | DeleteRelationshipRequestBody] = None,
                          cascade_delete: bool = False) -> None:
        """Detach a schema type as the header for an API operation."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_api_header(
            api_operation_guid, schema_type_guid, body, cascade_delete))

    @dynamic_catch
    async def _async_link_api_request(self, api_operation_guid: str, schema_type_guid: str,
                                      body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach a schema type as the request for an API operation (APIRequest relationship). Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"api-operations/{api_operation_guid}/api-requests/{schema_type_guid}/attach")
        await self._async_new_relationship_request(url, ["APIRequestProperties"], body)
        logger.info(f"API request schema type {schema_type_guid} linked to API operation {api_operation_guid}.")

    @dynamic_catch
    def link_api_request(self, api_operation_guid: str, schema_type_guid: str,
                         body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach a schema type as the request for an API operation (APIRequest relationship)."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_api_request(api_operation_guid, schema_type_guid, body))

    @dynamic_catch
    async def _async_detach_api_request(self, api_operation_guid: str, schema_type_guid: str,
                                        body: Optional[dict | DeleteRelationshipRequestBody] = None,
                                        cascade_delete: bool = False) -> None:
        """Detach a schema type as the request for an API operation. Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"api-operations/{api_operation_guid}/api-requests/{schema_type_guid}/detach")
        await self._async_delete_relationship_request(url, body, cascade_delete)
        logger.info(f"API request schema type {schema_type_guid} detached from API operation {api_operation_guid}.")

    @dynamic_catch
    def detach_api_request(self, api_operation_guid: str, schema_type_guid: str,
                           body: Optional[dict | DeleteRelationshipRequestBody] = None,
                           cascade_delete: bool = False) -> None:
        """Detach a schema type as the request for an API operation."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_api_request(
            api_operation_guid, schema_type_guid, body, cascade_delete))

    @dynamic_catch
    async def _async_link_api_response(self, api_operation_guid: str, schema_type_guid: str,
                                       body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach a schema type as the response for an API operation (APIResponse relationship). Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"api-operations/{api_operation_guid}/api-responses/{schema_type_guid}/attach")
        await self._async_new_relationship_request(url, ["APIResponseProperties"], body)
        logger.info(f"API response schema type {schema_type_guid} linked to API operation {api_operation_guid}.")

    @dynamic_catch
    def link_api_response(self, api_operation_guid: str, schema_type_guid: str,
                          body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach a schema type as the response for an API operation (APIResponse relationship)."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_api_response(api_operation_guid, schema_type_guid, body))

    @dynamic_catch
    async def _async_detach_api_response(self, api_operation_guid: str, schema_type_guid: str,
                                         body: Optional[dict | DeleteRelationshipRequestBody] = None,
                                         cascade_delete: bool = False) -> None:
        """Detach a schema type as the response for an API operation. Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"api-operations/{api_operation_guid}/api-responses/{schema_type_guid}/detach")
        await self._async_delete_relationship_request(url, body, cascade_delete)
        logger.info(f"API response schema type {schema_type_guid} detached from API operation {api_operation_guid}.")

    @dynamic_catch
    def detach_api_response(self, api_operation_guid: str, schema_type_guid: str,
                            body: Optional[dict | DeleteRelationshipRequestBody] = None,
                            cascade_delete: bool = False) -> None:
        """Detach a schema type as the response for an API operation."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_api_response(
            api_operation_guid, schema_type_guid, body, cascade_delete))

    @dynamic_catch
    async def _async_link_schema_type_option(self, schema_element_guid: str, schema_type_guid: str,
                                             body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach an optional schema type to a schema element (SchemaTypeOption relationship). Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"schema-elements/{schema_element_guid}/schema-type-options/{schema_type_guid}/attach")
        await self._async_new_relationship_request(url, ["SchemaTypeOptionProperties"], body)
        logger.info(f"Schema type option {schema_type_guid} linked to schema element {schema_element_guid}.")

    @dynamic_catch
    def link_schema_type_option(self, schema_element_guid: str, schema_type_guid: str,
                                body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach an optional schema type to a schema element (SchemaTypeOption relationship)."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_schema_type_option(schema_element_guid, schema_type_guid, body))

    @dynamic_catch
    async def _async_detach_schema_type_option(self, schema_element_guid: str, schema_type_guid: str,
                                               body: Optional[dict | DeleteRelationshipRequestBody] = None,
                                               cascade_delete: bool = False) -> None:
        """Detach an optional schema type from a schema element. Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"schema-elements/{schema_element_guid}/schema-type-options/{schema_type_guid}/detach")
        await self._async_delete_relationship_request(url, body, cascade_delete)
        logger.info(f"Schema type option {schema_type_guid} detached from schema element {schema_element_guid}.")

    @dynamic_catch
    def detach_schema_type_option(self, schema_element_guid: str, schema_type_guid: str,
                                  body: Optional[dict | DeleteRelationshipRequestBody] = None,
                                  cascade_delete: bool = False) -> None:
        """Detach an optional schema type from a schema element."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_schema_type_option(
            schema_element_guid, schema_type_guid, body, cascade_delete))

    @dynamic_catch
    async def _async_add_primary_key_classification(self, relational_column_guid: str,
                                                     body: Optional[dict | NewClassificationRequestBody] = None) -> None:
        """Classify a relational column as a primary key. Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"relational-columns/{relational_column_guid}/primary-key")
        if body is None:
            body = {"class": "NewClassificationRequestBody", "properties": {"class": "PrimaryKeyProperties"}}
        await self._async_new_classification_request(url, ["PrimaryKeyProperties"], body)
        logger.info(f"Added PrimaryKey classification to {relational_column_guid}.")

    @dynamic_catch
    def add_primary_key_classification(self, relational_column_guid: str,
                                       body: Optional[dict | NewClassificationRequestBody] = None) -> None:
        """Classify a relational column as a primary key."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_add_primary_key_classification(relational_column_guid, body))

    @dynamic_catch
    async def _async_remove_primary_key_classification(self, relational_column_guid: str,
                                                        body: Optional[dict | DeleteClassificationRequestBody] = None,
                                                        cascade_delete: bool = False) -> None:
        """Remove the PrimaryKey classification from a relational column. Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"relational-columns/{relational_column_guid}/primary-key/remove")
        await self._async_delete_classification_request(url, body, cascade_delete)
        logger.info(f"Removed PrimaryKey classification from {relational_column_guid}.")

    @dynamic_catch
    def remove_primary_key_classification(self, relational_column_guid: str,
                                          body: Optional[dict | DeleteClassificationRequestBody] = None,
                                          cascade_delete: bool = False) -> None:
        """Remove the PrimaryKey classification from a relational column."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_remove_primary_key_classification(
            relational_column_guid, body, cascade_delete))

    @dynamic_catch
    async def _async_add_type_embedded_attribute(self, schema_attribute_guid: str,
                                                  body: Optional[dict | NewClassificationRequestBody] = None) -> None:
        """Classify a schema attribute as having its type embedded rather than linked (TypeEmbeddedAttribute). Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"schema-attributes/{schema_attribute_guid}/type-embedded-attribute")
        if body is None:
            body = {"class": "NewClassificationRequestBody", "properties": {"class": "TypeEmbeddedAttributeProperties"}}
        await self._async_new_classification_request(url, ["TypeEmbeddedAttributeProperties"], body)
        logger.info(f"Added TypeEmbeddedAttribute classification to {schema_attribute_guid}.")

    @dynamic_catch
    def add_type_embedded_attribute(self, schema_attribute_guid: str,
                                    body: Optional[dict | NewClassificationRequestBody] = None) -> None:
        """Classify a schema attribute as having its type embedded rather than linked (TypeEmbeddedAttribute)."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_add_type_embedded_attribute(schema_attribute_guid, body))

    @dynamic_catch
    async def _async_remove_type_embedded_attribute(self, schema_attribute_guid: str,
                                                     body: Optional[dict | DeleteClassificationRequestBody] = None,
                                                     cascade_delete: bool = False) -> None:
        """Remove the TypeEmbeddedAttribute classification from a schema attribute. Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"schema-attributes/{schema_attribute_guid}/type-embedded-attribute/remove")
        await self._async_delete_classification_request(url, body, cascade_delete)
        logger.info(f"Removed TypeEmbeddedAttribute classification from {schema_attribute_guid}.")

    @dynamic_catch
    def remove_type_embedded_attribute(self, schema_attribute_guid: str,
                                       body: Optional[dict | DeleteClassificationRequestBody] = None,
                                       cascade_delete: bool = False) -> None:
        """Remove the TypeEmbeddedAttribute classification from a schema attribute."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_remove_type_embedded_attribute(
            schema_attribute_guid, body, cascade_delete))

    @dynamic_catch
    async def _async_add_calculated_value(self, schema_attribute_guid: str,
                                          body: Optional[dict | NewClassificationRequestBody] = None) -> None:
        """Classify a schema attribute as holding a calculated (derived) value. Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"schema-attributes/{schema_attribute_guid}/calculated-value")
        if body is None:
            body = {"class": "NewClassificationRequestBody", "properties": {"class": "CalculatedValueProperties"}}
        await self._async_new_classification_request(url, ["CalculatedValueProperties"], body)
        logger.info(f"Added CalculatedValue classification to {schema_attribute_guid}.")

    @dynamic_catch
    def add_calculated_value(self, schema_attribute_guid: str,
                             body: Optional[dict | NewClassificationRequestBody] = None) -> None:
        """Classify a schema attribute as holding a calculated (derived) value."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_add_calculated_value(schema_attribute_guid, body))

    @dynamic_catch
    async def _async_remove_calculated_value(self, schema_attribute_guid: str,
                                             body: Optional[dict | DeleteClassificationRequestBody] = None,
                                             cascade_delete: bool = False) -> None:
        """Remove the CalculatedValue classification from a schema attribute. Async version."""
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/schema-maker/"
               f"schema-attributes/{schema_attribute_guid}/calculated-value/remove")
        await self._async_delete_classification_request(url, body, cascade_delete)
        logger.info(f"Removed CalculatedValue classification from {schema_attribute_guid}.")

    @dynamic_catch
    def remove_calculated_value(self, schema_attribute_guid: str,
                                body: Optional[dict | DeleteClassificationRequestBody] = None,
                                cascade_delete: bool = False) -> None:
        """Remove the CalculatedValue classification from a schema attribute."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_remove_calculated_value(
            schema_attribute_guid, body, cascade_delete))
