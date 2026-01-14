"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides access to the Product Manager OMVS module.

The Product Manager OMVS provides APIs for managing digital products and their
relationships, including product dependencies and product managers.
"""

import asyncio
from typing import Optional

from pyegeria.omvs.collection_manager import CollectionManager
from pyegeria.core._server_client import ServerClient
from pyegeria.core.config import settings as app_settings
from pyegeria.models import (
    NewElementRequestBody,
    UpdateElementRequestBody,
    NewRelationshipRequestBody,
    DeleteRelationshipRequestBody,
    DeleteElementRequestBody,
)
from pyegeria.core.utils import dynamic_catch, body_slimmer
from loguru import logger

EGERIA_LOCAL_QUALIFIER = app_settings.User_Profile.egeria_local_qualifier


class ProductManager(CollectionManager):
    """
    Manage digital products, digital product catalogs, and their relationships.

    This client provides methods to create, update, and manage digital products and
    digital product catalogs, including linking product dependencies and product manager roles.

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
    create_digital_product(body)
        Create a new digital product collection.
    update_digital_product(digital_product_guid, body)
        Update the properties of a digital product.
    delete_digital_product(digital_product_guid, body, cascade)
        Delete a digital product.
    get_digital_product_by_guid(digital_product_guid, body, output_format, report_spec)
        Return the properties of a specific digital product by GUID.
    get_digital_products_by_name(filter_string, body, start_from, page_size, output_format, report_spec)
        Returns the list of digital products with a particular name.
    find_digital_products(search_string, starts_with, ends_with, ignore_case, start_from, page_size, output_format, report_spec, body)
        Returns the list of digital products matching the search string.
    create_digital_product_catalog(body)
        Create a new digital product catalog collection.
    update_digital_product_catalog(digital_product_catalog_guid, body)
        Update the properties of a digital product catalog.
    delete_digital_product_catalog(digital_product_catalog_guid, body, cascade)
        Delete a digital product catalog.
    get_digital_product_catalog_by_guid(digital_product_catalog_guid, body, output_format, report_spec)
        Return the properties of a specific digital product catalog by GUID.
    get_digital_product_catalogs_by_name(filter_string, body, start_from, page_size, output_format, report_spec)
        Returns the list of digital product catalogs with a particular name.
    find_digital_product_catalogs(search_string, starts_with, ends_with, ignore_case, start_from, page_size, output_format, report_spec, body)
        Returns the list of digital product catalogs matching the search string.
    link_digital_product_dependency(consumer_product_guid, consumed_product_guid, body)
        Link two dependent digital products.
    detach_digital_product_dependency(consumer_product_guid, consumed_product_guid, body)
        Unlink dependent digital products.
    link_product_manager(digital_product_guid, product_manager_role_guid, body)
        Attach a product manager role to a digital product.
    detach_product_manager(digital_product_guid, product_manager_role_guid, body)
        Detach a product manager from a digital product.
    """

    def __init__(
        self,
        view_server: str,
        platform_url: str,
        user_id: str,
        user_pwd: Optional[str] = None,
        token: Optional[str] = None,
    ):
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd
        self.product_manager_command_root: str = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/product-manager"
        )
        ServerClient.__init__(self, view_server, platform_url, user_id, user_pwd, token)

    def _prepare_body(self, body: Optional[dict | NewElementRequestBody | UpdateElementRequestBody | 
                                           NewRelationshipRequestBody | DeleteRelationshipRequestBody]) -> dict:
        """Convert Pydantic models to dict and slim the body."""
        if body is None:
            return {}
        if isinstance(body, dict):
            return body_slimmer(body)
        # It's a Pydantic model
        return body_slimmer(body.model_dump(mode='json', by_alias=True, exclude_none=True))

    #
    # Digital Product Management
    #

    @dynamic_catch
    async def _async_create_digital_product(
        self,
        body: Optional[dict | NewElementRequestBody] = None,
    ) -> str:
        """Create a new digital product collection. Async version.

        Parameters
        ----------
        body : dict | NewElementRequestBody, optional
            Request body containing digital product properties.

        Returns
        -------
        str
            The GUID of the created digital product.

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
        Sample JSON body:
        ```json
        {
          "class" : "NewElementRequestBody",
          "isOwnAnchor" : true,
          "properties": {
            "class" : "DigitalProductProperties",
            "qualifiedName": "DigitalProduct::Product Name",
            "displayName" : "Product Display Name",
            "description" : "Description of the product",
            "identifier" : "Product ID",
            "productName" : "Product Name",
            "introductionDate" : "2024-01-01T00:00:00.000+00:00"
          }
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/product-manager/collections"
        return await self._async_create_element_body_request(url, ["DigitalProductProperties"], body)

    def create_digital_product(
        self,
        body: Optional[dict | NewElementRequestBody] = None,
    ) -> str:
        """Create a new digital product collection.

        Parameters
        ----------
        body : dict | NewElementRequestBody, optional
            Request body containing digital product properties.

        Returns
        -------
        str
            The GUID of the created digital product.

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
          "isOwnAnchor" : true,
          "properties": {
            "class" : "DigitalProductProperties",
            "qualifiedName": "DigitalProduct::Product Name",
            "displayName" : "Product Display Name",
            "description" : "Description of the product",
            "identifier" : "Product ID",
            "productName" : "Product Name",
            "introductionDate" : "2024-01-01T00:00:00.000+00:00"
          }
        }
        ```
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_create_digital_product(body))

    @dynamic_catch
    async def _async_update_digital_product(
        self,
        digital_product_guid: str,
        body: Optional[dict | UpdateElementRequestBody] = None,
    ) -> None:
        """Update the properties of a digital product. Async version.

        Parameters
        ----------
        digital_product_guid : str
            The GUID of the digital product to update.
        body : dict | UpdateElementRequestBody, optional
            Request body containing updated properties.

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
            "class" : "DigitalProductProperties",
            "displayName" : "New Display Name"
          }
        }
        ```
        """
        url = f"{self.product_manager_command_root}/collections/{digital_product_guid}/update"
        await self._async_update_element_body_request(url, ["DigitalProductProperties"], body)

    def update_digital_product(
        self,
        digital_product_guid: str,
        body: Optional[dict | UpdateElementRequestBody] = None,
    ) -> None:
        """Update the properties of a digital product.

        Parameters
        ----------
        digital_product_guid : str
            The GUID of the digital product to update.
        body : dict | UpdateElementRequestBody, optional
            Request body containing updated properties.

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
            "class" : "DigitalProductProperties",
            "displayName" : "New Display Name"
          }
        }
        ```
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_digital_product(digital_product_guid, body)
        )

    @dynamic_catch
    async def _async_delete_digital_product(
        self,
        digital_product_guid: str,
        body: Optional[dict | DeleteElementRequestBody] = None,
        cascade: bool = False,
    ) -> None:
        """Delete a digital product. Async version.

        Parameters
        ----------
        digital_product_guid : str
            The GUID of the digital product to delete.
        body : dict | DeleteElementRequestBody, optional
            Request body for deletion.
        cascade : bool, optional, default=False
            If true, performs a cascade delete.

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
          "class": "DeleteElementRequestBody",
          "cascadedDelete": false
        }
        ```
        """
        if body is None:
            body = {"class": "DeleteElementRequestBody"}
        url = f"{self.product_manager_command_root}/collections/{digital_product_guid}/delete"
        await self._async_delete_element_request(url, body, cascade)
        logger.info(f"Deleted digital product {digital_product_guid} with cascade {cascade}")

    def delete_digital_product(
        self,
        digital_product_guid: str,
        body: Optional[dict | DeleteElementRequestBody] = None,
        cascade: bool = False,
    ) -> None:
        """Delete a digital product.

        Parameters
        ----------
        digital_product_guid : str
            The GUID of the digital product to delete.
        body : dict | DeleteElementRequestBody, optional
            Request body for deletion.
        cascade : bool, optional, default=False
            If true, performs a cascade delete.

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
          "class": "DeleteElementRequestBody",
          "cascadedDelete": false
        }
        ```
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_delete_digital_product(digital_product_guid, body, cascade)
        )

    @dynamic_catch
    async def _async_get_digital_product_by_guid(
        self,
        digital_product_guid: str,
        body: Optional[dict] = None,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
    ) -> dict | str:
        """Return the properties of a specific digital product. Async version.

        Parameters
        ----------
        digital_product_guid : str
            Unique identifier of the digital product.
        body : dict, optional
            Full request body.
        output_format : str, default="JSON"
            One of "JSON", "DICT", "MD", "FORM", "REPORT", or "MERMAID".
        report_spec : str | dict, optional
            The desired output columns/fields to include.

        Returns
        -------
        dict | str
            A JSON dict representing the specified digital product.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Body sample:
        {
          "class": "GetRequestBody",
          "asOfTime": "{{$isoTimestamp}}",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """
        url = f"{self.product_manager_command_root}/collections/{digital_product_guid}/retrieve"
        response = await self._async_get_guid_request(
            url,
            _type="DigitalProduct",
            _gen_output=self._generate_collection_output,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )
        return response

    def get_digital_product_by_guid(
        self,
        digital_product_guid: str,
        body: Optional[dict] = None,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
    ) -> dict | str:
        """Return the properties of a specific digital product. Sync version.

        Parameters
        ----------
        digital_product_guid : str
            Unique identifier of the digital product.
        body : dict, optional
            Full request body.
        output_format : str, default="JSON"
            One of "JSON", "DICT", "MD", "FORM", "REPORT", or "MERMAID".
        report_spec : str | dict, optional
            The desired output columns/fields to include.

        Returns
        -------
        dict | str
            A JSON dict representing the specified digital product.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_digital_product_by_guid(
                digital_product_guid, body, output_format, report_spec
            )
        )

    @dynamic_catch
    async def _async_get_digital_products_by_name(
        self,
        filter_string: str,
        classification_names: Optional[list[str]] = None,
        body: Optional[dict] = None,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
    ) -> list | str:
        """Returns the list of digital products with a particular name. Async version.

        Parameters
        ----------
        filter_string : str
            Name to use to find matching digital products.
        classification_names : list[str], optional
            List of classification names to filter on.
        body : dict, optional
            Provides a full request body. If specified, supersedes the filter_string parameter.
        start_from : int, default=0
            When multiple pages of results are available, the page number to start from.
        page_size : int, default=0
            The number of items to return in a single page.
        output_format : str, default="JSON"
            One of "JSON", "DICT", "MD", "FORM", "REPORT", or "MERMAID".
        report_spec : str | dict, optional
            The desired output columns/fields to include.

        Returns
        -------
        list | str
            A list of digital products matching the name.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        url = f"{self.product_manager_command_root}/collections/by-name"
        response = await self._async_get_name_request(
            url,
            _type="DigitalProduct",
            _gen_output=self._generate_collection_output,
            filter_string=filter_string,
            classification_names=classification_names,
            start_from=start_from,
            page_size=page_size,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )
        return response

    def get_digital_products_by_name(
        self,
        filter_string: str,
        classification_names: Optional[list[str]] = None,
        body: Optional[dict] = None,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
    ) -> list | str:
        """Returns the list of digital products with a particular name. Sync version.

        Parameters
        ----------
        filter_string : str
            Name to use to find matching digital products.
        classification_names : list[str], optional
            List of classification names to filter on.
        body : dict, optional
            Provides a full request body. If specified, supersedes the filter_string parameter.
        start_from : int, default=0
            When multiple pages of results are available, the page number to start from.
        page_size : int, default=0
            The number of items to return in a single page.
        output_format : str, default="JSON"
            One of "JSON", "DICT", "MD", "FORM", "REPORT", or "MERMAID".
        report_spec : str | dict, optional
            The desired output columns/fields to include.

        Returns
        -------
        list | str
            A list of digital products matching the name.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_digital_products_by_name(
                filter_string, classification_names, body, start_from, page_size, output_format, report_spec
            )
        )

    @dynamic_catch
    async def _async_find_digital_products(
        self,
        search_string: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = False,
        anchor_domain: Optional[str] = None,
        metadata_element_type: Optional[str] = None,
        metadata_element_subtype: Optional[list[str]] = None,
        skip_relationships: Optional[list[str]] = None,
        include_only_relationships: Optional[list[str]] = None,
        skip_classified_elements: Optional[list[str]] = None,
        include_only_classified_elements: Optional[list[str]] = None,
        graph_query_depth: int = 3,
        governance_zone_filter: Optional[list[str]] = None,
        as_of_time: Optional[str] = None,
        effective_time: Optional[str] = None,
        relationship_page_size: int = 0,
        limit_results_by_status: Optional[list[str]] = None,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 100,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        property_names: Optional[list[str]] = None,
        body: Optional[dict] = None,
    ) -> list | str:
        """Returns the list of digital products matching the search string. Async version.

        Parameters
        ----------
        search_string : str, default="*"
            Search string to match against. '*' matches all digital products.
        starts_with : bool, default=True
            Starts with the supplied string.
        ends_with : bool, default=False
            Ends with the supplied string.
        ignore_case : bool, default=False
            Ignore case when searching.
        anchor_domain : str, optional
            Anchor domain to filter on.
        metadata_element_type : str, optional
            Metadata element type name to filter on.
        metadata_element_subtype : list[str], optional
            List of metadata element subtypes to filter on.
        skip_relationships : list[str], optional
            List of relationship types to skip.
        include_only_relationships : list[str], optional
            List of relationship types to include only.
        skip_classified_elements : list[str], optional
            List of classification names to skip.
        include_only_classified_elements : list[str], optional
            List of classification names to include only.
        graph_query_depth : int, default=3
            Depth of graph query.
        governance_zone_filter : list[str], optional
            List of governance zones to filter on.
        as_of_time : str, optional
            Time for historical queries.
        effective_time : str, optional
            Effective time for the query.
        relationship_page_size : int, default=0
            Page size for relationships.
        limit_results_by_status : list[str], optional
            List of statuses to limit results by.
        sequencing_order : str, optional
            Sequencing order for results.
        sequencing_property : str, optional
            Property to sequence by.
        start_from : int, default=0
            When multiple pages of results are available, the page number to start from.
        page_size : int, default=100
            The number of items to return in a single page.
        output_format : str, default="JSON"
            One of "JSON", "DICT", "MD", "FORM", "REPORT", or "MERMAID".
        report_spec : str | dict, optional
            The desired output columns/fields to include.
        property_names: list[str], optional
            The names of properties to search for.
        body : dict, optional
            If provided, the search parameters in the body supersede other attributes.

        Returns
        -------
        list | str
            Output depends on the output format specified.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        if metadata_element_subtype is None:
            metadata_element_subtype = ["DigitalProduct"]

        url = f"{self.product_manager_command_root}/collections/by-search-string"
        response = await self._async_find_request(
            url,
            _type="DigitalProduct",
            _gen_output=self._generate_collection_output,
            search_string=search_string,
            starts_with=starts_with,
            ends_with=ends_with,
            ignore_case=ignore_case,
            anchor_domain=anchor_domain,
            metadata_element_type=metadata_element_type,
            metadata_element_subtypes=metadata_element_subtype,
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
            start_from=start_from,
            page_size=page_size,
            output_format=output_format,
            report_spec=report_spec,
            property_names=property_names,
            body=body,
        )
        return response

    def find_digital_products(
        self,
        search_string: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = False,
        anchor_domain: Optional[str] = None,
        metadata_element_type: Optional[str] = None,
        metadata_element_subtype: Optional[list[str]] = None,
        skip_relationships: Optional[list[str]] = None,
        include_only_relationships: Optional[list[str]] = None,
        skip_classified_elements: Optional[list[str]] = None,
        include_only_classified_elements: Optional[list[str]] = None,
        graph_query_depth: int = 3,
        governance_zone_filter: Optional[list[str]] = None,
        as_of_time: Optional[str] = None,
        effective_time: Optional[str] = None,
        relationship_page_size: int = 0,
        limit_results_by_status: Optional[list[str]] = None,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 100,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        property_names: Optional[list[str]] = None,
        body: Optional[dict] = None,
    ) -> list | str:
        """Returns the list of digital products matching the search string. Sync version.

        Parameters
        ----------
        search_string : str, default="*"
            Search string to match against. '*' matches all digital products.
        starts_with : bool, default=True
            Starts with the supplied string.
        ends_with : bool, default=False
            Ends with the supplied string.
        ignore_case : bool, default=False
            Ignore case when searching.
        anchor_domain : str, optional
            Anchor domain to filter on.
        metadata_element_type : str, optional
            Metadata element type name to filter on.
        metadata_element_subtype : list[str], optional
            List of metadata element subtypes to filter on.
        skip_relationships : list[str], optional
            List of relationship types to skip.
        include_only_relationships : list[str], optional
            List of relationship types to include only.
        skip_classified_elements : list[str], optional
            List of classification names to skip.
        include_only_classified_elements : list[str], optional
            List of classification names to include only.
        graph_query_depth : int, default=3
            Depth of graph query.
        governance_zone_filter : list[str], optional
            List of governance zones to filter on.
        as_of_time : str, optional
            Time for historical queries.
        effective_time : str, optional
            Effective time for the query.
        relationship_page_size : int, default=0
            Page size for relationships.
        limit_results_by_status : list[str], optional
            List of statuses to limit results by.
        sequencing_order : str, optional
            Sequencing order for results.
        sequencing_property : str, optional
            Property to sequence by.
        start_from : int, default=0
            When multiple pages of results are available, the page number to start from.
        page_size : int, default=100
            The number of items to return in a single page.
        output_format : str, default="JSON"
            One of "JSON", "DICT", "MD", "FORM", "REPORT", or "MERMAID".
        report_spec : str | dict, optional
            The desired output columns/fields to include.
        property_names: list[str], optional
            The names of properties to search for.
        body : dict, optional
            If provided, the search parameters in the body supersede other attributes.

        Returns
        -------
        list | str
            Output depends on the output format specified.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_find_digital_products(
                search_string,
                starts_with,
                ends_with,
                ignore_case,
                anchor_domain,
                metadata_element_type,
                metadata_element_subtype,
                skip_relationships,
                include_only_relationships,
                skip_classified_elements,
                include_only_classified_elements,
                graph_query_depth,
                governance_zone_filter,
                as_of_time,
                effective_time,
                relationship_page_size,
                limit_results_by_status,
                sequencing_order,
                sequencing_property,
                start_from,
                page_size,
                output_format,
                report_spec,
                property_names,
                body,
            )
        )

    #
    # Digital Product Dependency Management
    #

    @dynamic_catch
    async def _async_link_digital_product_dependency(
        self,
        consumer_product_guid: str,
        consumed_product_guid: str,
        body: Optional[dict | NewRelationshipRequestBody] = None,
    ) -> None:
        """Link two dependent digital products. Async version.

        Parameters
        ----------
        consumer_product_guid : str
            The GUID of the digital product that consumes another.
        consumed_product_guid : str
            The GUID of the digital product being consumed.
        body : dict | NewRelationshipRequestBody, optional
            Request body containing relationship properties.

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
            "class": "DigitalProductDependencyProperties",
            "label": "add label here",
            "description": "add description here"
          }
        }
        ```
        """
        url = (
            f"{self.product_manager_command_root}/digital-products/"
            f"{consumer_product_guid}/product-dependencies/{consumed_product_guid}/attach"
        )
        await self._async_new_relationship_request(url, ["DigitalProductDependencyProperties"], body)
        logger.info(f"Linked {consumed_product_guid} -> {consumer_product_guid}")

    def link_digital_product_dependency(
        self,
        consumer_product_guid: str,
        consumed_product_guid: str,
        body: Optional[dict | NewRelationshipRequestBody] = None,
    ) -> None:
        """Link two dependent digital products.

        Parameters
        ----------
        consumer_product_guid : str
            The GUID of the digital product that consumes another.
        consumed_product_guid : str
            The GUID of the digital product being consumed.
        body : dict | NewRelationshipRequestBody, optional
            Request body containing relationship properties.

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
            "class": "DigitalProductDependencyProperties",
            "label": "add label here",
            "description": "add description here"
          }
        }
        ```
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_link_digital_product_dependency(
                consumer_product_guid, consumed_product_guid, body
            )
        )

    @dynamic_catch
    async def _async_detach_digital_product_dependency(
        self,
        consumer_product_guid: str,
        consumed_product_guid: str,
        body: Optional[dict | DeleteRelationshipRequestBody] = None,
    ) -> None:
        """Unlink dependent digital products. Async version.

        Parameters
        ----------
        consumer_product_guid : str
            The GUID of the consumer digital product.
        consumed_product_guid : str
            The GUID of the consumed digital product to detach.
        body : dict | DeleteRelationshipRequestBody, optional
            Request body for deletion.

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
        url = (
            f"{self.product_manager_command_root}/digital-products/"
            f"{consumer_product_guid}/product-dependencies/{consumed_product_guid}/detach"
        )
        await self._async_delete_relationship_request(url, body)
        logger.info(f"Detached digital product dependency {consumer_product_guid} -> {consumed_product_guid}")

    def detach_digital_product_dependency(
        self,
        consumer_product_guid: str,
        consumed_product_guid: str,
        body: Optional[dict | DeleteRelationshipRequestBody] = None,
    ) -> None:
        """Unlink dependent digital products.

        Parameters
        ----------
        consumer_product_guid : str
            The GUID of the consumer digital product.
        consumed_product_guid : str
            The GUID of the consumed digital product to detach.
        body : dict | DeleteRelationshipRequestBody, optional
            Request body for deletion.

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
            self._async_detach_digital_product_dependency(
                consumer_product_guid, consumed_product_guid, body
            )
        )

    #
    # Product Manager Role Management
    #

    @dynamic_catch
    async def _async_link_product_manager(
        self,
        digital_product_guid: str,
        product_manager_role_guid: str,
        body: Optional[dict | NewRelationshipRequestBody] = None,
    ) -> None:
        """Attach a product manager role to a digital product. Async version.

        Parameters
        ----------
        digital_product_guid : str
            The GUID of the digital product.
        product_manager_role_guid : str
            The GUID of the product manager role.
        body : dict | NewRelationshipRequestBody, optional
            Request body containing relationship properties.

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
          "class": "NewRelationshipRequestBody",
          "properties": {
              "class" : "AssignmentScopeProperties",
              "assignmentType": "Product Manager",
              "description": "The person or role responsible for the product"
          }
        }
        ```
        """
        url = (
            f"{self.product_manager_command_root}/digital-products/"
            f"{digital_product_guid}/product-managers/{product_manager_role_guid}/attach"
        )
        await self._async_new_relationship_request(url, ["AssignmentScopeProperties"], body)
        logger.info(f"Attached digital product manager {digital_product_guid} -> {product_manager_role_guid}")

    def link_product_manager(
        self,
        digital_product_guid: str,
        product_manager_role_guid: str,
        body: Optional[dict | NewRelationshipRequestBody] = None,
    ) -> None:
        """Attach a product manager role to a digital product.

        Parameters
        ----------
        digital_product_guid : str
            The GUID of the digital product.
        product_manager_role_guid : str
            The GUID of the product manager role.
        body : dict | NewRelationshipRequestBody, optional
            Request body containing relationship properties.

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
          "class": "NewRelationshipRequestBody",
          "properties": {
              "class" : "AssignmentScopeProperties",
              "assignmentType": "Product Manager",
              "description": "The person or role responsible for the product"
          }
        }
        ```
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_link_product_manager(
                digital_product_guid, product_manager_role_guid, body
            )
        )

    @dynamic_catch
    async def _async_detach_product_manager(
        self,
        digital_product_guid: str,
        product_manager_role_guid: str,
        body: Optional[dict | DeleteRelationshipRequestBody] = None,
    ) -> None:
        """Detach a product manager from a digital product. Async version.

        Parameters
        ----------
        digital_product_guid : str
            The GUID of the digital product.
        product_manager_role_guid : str
            The GUID of the product manager role to detach.
        body : dict | DeleteRelationshipRequestBody, optional
            Request body for deletion.

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
        url = (
            f"{self.product_manager_command_root}/digital-products/"
            f"{digital_product_guid}/product-managers/{product_manager_role_guid}/detach"
        )
        await self._async_delete_relationship_request(url, body)
        logger.info(f"Detached digital product manager {digital_product_guid} -> {product_manager_role_guid}")

    def detach_product_manager(
        self,
        digital_product_guid: str,
        product_manager_role_guid: str,
        body: Optional[dict | DeleteRelationshipRequestBody] = None,
    ) -> None:
        """Detach a product manager from a digital product.

        Parameters
        ----------
        digital_product_guid : str
            The GUID of the digital product.
        product_manager_role_guid : str
            The GUID of the product manager role to detach.
        body : dict | DeleteRelationshipRequestBody, optional
            Request body for deletion.

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
            self._async_detach_product_manager(
                digital_product_guid, product_manager_role_guid, body
            )
        )

    #
    # Digital Product Catalog Management
    #

    @dynamic_catch
    async def _async_create_digital_product_catalog(
        self,
        body: Optional[dict | NewElementRequestBody] = None,
    ) -> str:
        """Create a new digital product catalog collection. Async version.

        Parameters
        ----------
        body : dict | NewElementRequestBody, optional
            Request body containing digital product catalog properties.

        Returns
        -------
        str
            The GUID of the created digital product catalog.

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
              "typeName": "DigitalProductCatalog",
              "isOwnAnchor" : true,
              "anchorScopeGUID" : "optional GUID of search scope",
              "parentGUID" : "xxx",
              "parentRelationshipTypeName" : "CollectionMembership",
              "parentAtEnd1": true,
              "properties": {
                "class" : "CatalogProperties",
                "qualifiedName": "DigitalProductCatalog::Add catalog name here",
                "displayName" : "Catalog name",
                "description" : "Add description of catalog here",
                "additionalProperties": {
                  "property1Name" : "property1Value",
                  "property2Name" : "property2Value"
                }
              },
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime" : "timestamp",
              "forLineage" : false,
              "forDuplicateProcessing" : false,
            }
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/product-manager/collections"
        return await self._async_create_element_body_request(url, ["CatalogProperties"], body)

    def create_digital_product_catalog(
        self,
        body: Optional[dict | NewElementRequestBody] = None,
    ) -> str:
        """Create a new digital product catalog collection. Sync version.

        Parameters
        ----------
        body : dict | NewElementRequestBody, optional
            Request body containing digital product catalog properties.

        Returns
        -------
        str
            The GUID of the created digital product catalog.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        body = self._prepare_body(body)
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_create_digital_product_catalog(body))

    @dynamic_catch
    async def _async_update_digital_product_catalog(
        self,
        digital_product_catalog_guid: str,
        body: Optional[dict | UpdateElementRequestBody] = None,
    ) -> None:
        """Update the properties of a digital product catalog. Async version.

        Parameters
        ----------
        digital_product_catalog_guid : str
            The GUID of the digital product catalog to update.
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
        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
            f"product-manager/collections/{digital_product_catalog_guid}/update"
        )
        await self._async_update_element_body_request(url, ["CatalogProperties"], body)

    def update_digital_product_catalog(
        self,
        digital_product_catalog_guid: str,
        body: Optional[dict | UpdateElementRequestBody] = None,
    ) -> None:
        """Update the properties of a digital product catalog. Sync version.

        Parameters
        ----------
        digital_product_catalog_guid : str
            The GUID of the digital product catalog to update.
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
        digital_product_catalog_guid = str(digital_product_catalog_guid)
        body = self._prepare_body(body)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_digital_product_catalog(digital_product_catalog_guid, body)
        )

    @dynamic_catch
    async def _async_delete_digital_product_catalog(
        self,
        digital_product_catalog_guid: str,
        body: Optional[dict | DeleteElementRequestBody] = None,
        cascade: bool = False,
    ) -> None:
        """Delete a digital product catalog. Async version.

        Parameters
        ----------
        digital_product_catalog_guid : str
            The GUID of the digital product catalog to delete.
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
        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
            f"product-manager/collections/{digital_product_catalog_guid}/delete"
        )
        await self._async_delete_element_request(url, body, cascade)

    def delete_digital_product_catalog(
        self,
        digital_product_catalog_guid: str,
        body: Optional[dict | DeleteElementRequestBody] = None,
        cascade: bool = False,
    ) -> None:
        """Delete a digital product catalog. Sync version.

        Parameters
        ----------
        digital_product_catalog_guid : str
            The GUID of the digital product catalog to delete.
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
        digital_product_catalog_guid = str(digital_product_catalog_guid)
        body = self._prepare_body(body)
        cascade = bool(cascade)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_delete_digital_product_catalog(digital_product_catalog_guid, body, cascade)
        )

    @dynamic_catch
    async def _async_get_digital_product_catalog_by_guid(
        self,
        digital_product_catalog_guid: str,
        body: Optional[dict] = None,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
    ) -> dict | str:
        """Return the properties of a specific digital product catalog by GUID. Async version.

        Parameters
        ----------
        digital_product_catalog_guid : str
            The GUID of the digital product catalog to retrieve.
        body : dict, optional
            Request body (typically empty for retrieval).
        output_format : str, optional
            Format for output. Defaults to "JSON".
        report_spec : str | dict, optional
            Report specification for formatting.

        Returns
        -------
        dict | str
            The digital product catalog properties.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        PyegeriaNotFoundException
            If the digital product catalog is not found.
        PyegeriaNotAuthorizedException
            If the user is not authorized for the requested action.
        """
        url = f"{self.product_manager_command_root}/collections/{digital_product_catalog_guid}/retrieve"
        response = await self._async_get_guid_request(
            url,
            _type="DigitalProductCatalog",
            _gen_output=None,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )
        return response

    def get_digital_product_catalog_by_guid(
        self,
        digital_product_catalog_guid: str,
        body: Optional[dict] = None,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
    ) -> dict | str:
        """Return the properties of a specific digital product catalog by GUID. Sync version.

        Parameters
        ----------
        digital_product_catalog_guid : str
            The GUID of the digital product catalog to retrieve.
        body : dict, optional
            Request body (typically empty for retrieval).
        output_format : str, optional
            Format for output. Defaults to "JSON".
        report_spec : str | dict, optional
            Report specification for formatting.

        Returns
        -------
        dict | str
            The digital product catalog properties.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_digital_product_catalog_by_guid(
                digital_product_catalog_guid, body, output_format, report_spec
            )
        )

    @dynamic_catch
    async def _async_get_digital_product_catalogs_by_name(
        self,
        filter_string: Optional[str] = None,
        classification_names: Optional[list[str]] = None,
        body: Optional[dict] = None,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
    ) -> list | str:
        """Returns the list of digital product catalogs with a particular name. Async version.

        Parameters
        ----------
        filter_string : str, optional
            Filter string to match against catalog names.
        classification_names : list[str], optional
            List of classification names to filter by.
        body : dict, optional
            Request body for additional filtering.
        start_from : int, optional
            Starting index for pagination. Defaults to 0.
        page_size : int, optional
            Number of results per page. Defaults to 0 (no limit).
        output_format : str, optional
            Format for output. Defaults to "JSON".
        report_spec : str | dict, optional
            Report specification for formatting.

        Returns
        -------
        list | str
            List of digital product catalogs matching the criteria.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        url = f"{self.product_manager_command_root}/collections/by-name"
        response = await self._async_get_name_request(
            url,
            _type="DigitalProductCatalog",
            _gen_output=None,
            filter_string=filter_string,
            classification_names=classification_names,
            start_from=start_from,
            page_size=page_size,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )
        return response

    def get_digital_product_catalogs_by_name(
        self,
        filter_string: Optional[str] = None,
        classification_names: Optional[list[str]] = None,
        body: Optional[dict] = None,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
    ) -> list | str:
        """Returns the list of digital product catalogs with a particular name. Sync version.

        Parameters
        ----------
        filter_string : str, optional
            Filter string to match against catalog names.
        classification_names : list[str], optional
            List of classification names to filter by.
        body : dict, optional
            Request body for additional filtering.
        start_from : int, optional
            Starting index for pagination. Defaults to 0.
        page_size : int, optional
            Number of results per page. Defaults to 0 (no limit).
        output_format : str, optional
            Format for output. Defaults to "JSON".
        report_spec : str | dict, optional
            Report specification for formatting.

        Returns
        -------
        list | str
            List of digital product catalogs matching the criteria.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_digital_product_catalogs_by_name(
                filter_string, classification_names, body, start_from, page_size, output_format, report_spec
            )
        )

    @dynamic_catch
    async def _async_find_digital_product_catalogs(
        self,
        search_string: str = "*",
        starts_with: bool = False,
        ends_with: bool = False,
        ignore_case: bool = True,
        anchor_domain: Optional[str] = None,
        metadata_element_type: Optional[str] = None,
        metadata_element_subtype: Optional[str] = None,
        skip_relationships: Optional[list[str]] = None,
        include_only_relationships: Optional[list[str]] = None,
        skip_classified_elements: Optional[list[str]] = None,
        include_only_classified_elements: Optional[list[str]] = None,
        graph_query_depth: int = 0,
        governance_zone_filter: Optional[list[str]] = None,
        as_of_time: Optional[str] = None,
        effective_time: Optional[str] = None,
        relationship_page_size: int = 0,
        limit_results_by_status: Optional[list[str]] = None,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        property_names: Optional[list[str]] = None,
        body: Optional[dict] = None,
    ) -> list | str:
        """Returns the list of digital product catalogs matching the search string. Async version.

        Parameters
        ----------
        search_string : str, optional
            Search string to match. Defaults to "*" (all).
        starts_with : bool, optional
            Whether to match from the start. Defaults to False.
        ends_with : bool, optional
            Whether to match at the end. Defaults to False.
        ignore_case : bool, optional
            Whether to ignore case. Defaults to True.
        anchor_domain : str, optional
            Domain to anchor the search.
        metadata_element_type : str, optional
            Type of metadata element to search for.
        metadata_element_subtype : str, optional
            Subtype of metadata element.
        skip_relationships : list[str], optional
            Relationships to skip in the graph.
        include_only_relationships : list[str], optional
            Only include these relationships.
        skip_classified_elements : list[str], optional
            Skip elements with these classifications.
        include_only_classified_elements : list[str], optional
            Only include elements with these classifications.
        graph_query_depth : int, optional
            Depth of graph query. Defaults to 0.
        governance_zone_filter : list[str], optional
            Filter by governance zones.
        as_of_time : str, optional
            Historical time for the query.
        effective_time : str, optional
            Effective time for the query.
        relationship_page_size : int, optional
            Page size for relationships. Defaults to 0.
        limit_results_by_status : list[str], optional
            Limit results by status values.
        sequencing_order : str, optional
            Order for sequencing results.
        sequencing_property : str, optional
            Property to sequence by.
        start_from : int, optional
            Starting index for pagination. Defaults to 0.
        page_size : int, optional
            Number of results per page. Defaults to 0 (no limit).
        output_format : str, optional
            Format for output. Defaults to "JSON".
        report_spec : str | dict, optional
            Report specification for formatting.
        property_names: list[str], optional
            The names of properties to search for.
        body : dict, optional
            Request body for additional parameters.

        Returns
        -------
        list | str
            List of digital product catalogs matching the search criteria.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        url = f"{self.product_manager_command_root}/collections/by-search-string"
        response = await self._async_find_request(
            url,
            _type="DigitalProductCatalog",
            _gen_output=None,
            search_string=search_string,
            starts_with=starts_with,
            ends_with=ends_with,
            ignore_case=ignore_case,
            anchor_domain=anchor_domain,
            metadata_element_type=metadata_element_type,
            metadata_element_subtypes=metadata_element_subtype,
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
            start_from=start_from,
            page_size=page_size,
            output_format=output_format,
            report_spec=report_spec,
            property_names=property_names,
            body=body,
        )
        return response

    def find_digital_product_catalogs(
        self,
        search_string: str = "*",
        starts_with: bool = False,
        ends_with: bool = False,
        ignore_case: bool = True,
        anchor_domain: Optional[str] = None,
        metadata_element_type: Optional[str] = None,
        metadata_element_subtype: Optional[str] = None,
        skip_relationships: Optional[list[str]] = None,
        include_only_relationships: Optional[list[str]] = None,
        skip_classified_elements: Optional[list[str]] = None,
        include_only_classified_elements: Optional[list[str]] = None,
        graph_query_depth: int = 0,
        governance_zone_filter: Optional[list[str]] = None,
        as_of_time: Optional[str] = None,
        effective_time: Optional[str] = None,
        relationship_page_size: int = 0,
        limit_results_by_status: Optional[list[str]] = None,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        property_names: Optional[list[str]] = None,
        body: Optional[dict] = None,
    ) -> list | str:
        """Returns the list of digital product catalogs matching the search string. Sync version.

        Parameters
        ----------
        search_string : str, optional
            Search string to match. Defaults to "*" (all).
        starts_with : bool, optional
            Whether to match from the start. Defaults to False.
        ends_with : bool, optional
            Whether to match at the end. Defaults to False.
        ignore_case : bool, optional
            Whether to ignore case. Defaults to True.
        anchor_domain : str, optional
            Domain to anchor the search.
        metadata_element_type : str, optional
            Type of metadata element to search for.
        metadata_element_subtype : str, optional
            Subtype of metadata element.
        skip_relationships : list[str], optional
            Relationships to skip in the graph.
        include_only_relationships : list[str], optional
            Only include these relationships.
        skip_classified_elements : list[str], optional
            Skip elements with these classifications.
        include_only_classified_elements : list[str], optional
            Only include elements with these classifications.
        graph_query_depth : int, optional
            Depth of graph query. Defaults to 0.
        governance_zone_filter : list[str], optional
            Filter by governance zones.
        as_of_time : str, optional
            Historical time for the query.
        effective_time : str, optional
            Effective time for the query.
        relationship_page_size : int, optional
            Page size for relationships. Defaults to 0.
        limit_results_by_status : list[str], optional
            Limit results by status values.
        sequencing_order : str, optional
            Order for sequencing results.
        sequencing_property : str, optional
            Property to sequence by.
        start_from : int, optional
            Starting index for pagination. Defaults to 0.
        page_size : int, optional
            Number of results per page. Defaults to 0 (no limit).
        output_format : str, optional
            Format for output. Defaults to "JSON".
        report_spec : str | dict, optional
            Report specification for formatting.
        property_names: list[str], optional
            The names of properties to search for.
        body : dict, optional
            Request body for additional parameters.

        Returns
        -------
        list | str
            List of digital product catalogs matching the search criteria.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_find_digital_product_catalogs(
                search_string, starts_with, ends_with, ignore_case, anchor_domain,
                metadata_element_type, metadata_element_subtype, skip_relationships,
                include_only_relationships, skip_classified_elements, include_only_classified_elements,
                graph_query_depth, governance_zone_filter, as_of_time, effective_time,
                relationship_page_size, limit_results_by_status, sequencing_order,
                sequencing_property, start_from, page_size, output_format, report_spec,
                property_names, body
            )
        )