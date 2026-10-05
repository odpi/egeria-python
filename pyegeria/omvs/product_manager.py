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
from pyegeria.models import (
    NewElementRequestBody,
    UpdateElementRequestBody,
    NewRelationshipRequestBody,
    DeleteRelationshipRequestBody,
    UpdateRelationshipRequestBody,
    DeleteElementRequestBody,
    NewSubscriptionTypeRequestBody,
)
from pyegeria.core._globals import NO_ELEMENTS_FOUND
from pyegeria.core.utils import dynamic_catch, body_slimmer
from loguru import logger


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
        self.product_manager_command_root: str = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/product-manager"
        )

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
        guid: str = None,
        body: Optional[dict] = None,
        graph_query_depth: int = 3, output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        **kwargs,
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
        if guid is None and "digital_product_guid" in kwargs:
            guid = kwargs.pop("digital_product_guid")
        url = f"{self.product_manager_command_root}/collections/{guid}/retrieve"
        params = {
            'graph_query_depth': graph_query_depth,
            'output_format': output_format,
            'report_spec': report_spec,
            'body': body
        }
        params.update(kwargs)
        params = {k: v for k, v in params.items() if v is not None}
        response = await self._async_get_guid_request(
            url,
            _type="DigitalProduct",
            _gen_output=self._generate_collection_output,
            **params,
        )
        return response

    def get_digital_product_by_guid(
        self,
        guid: str = None,
        body: Optional[dict] = None,
        graph_query_depth: int = 3, output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        **kwargs,
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
                graph_query_depth=graph_query_depth,
                guid=guid, body=body, output_format=output_format, report_spec=report_spec, **kwargs
            )
        )

    @dynamic_catch
    async def _async_get_digital_products_by_name(
        self,
        name: Optional[str] = None,
        classification_names: Optional[list[str]] = None,
        body: Optional[dict] = None,
        start_from: int = 0,
        page_size: int = 0,
        graph_query_depth: int = 3, output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        **kwargs,
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
        if "filter_string" in kwargs:
            name = kwargs.pop("filter_string")
        url = f"{self.product_manager_command_root}/collections/by-name"
        response = await self._async_get_name_request(url, _type="DigitalProduct",
                                                      _gen_output=self._generate_collection_output,
                                                      filter_string=name,
                                                      classification_names=classification_names, start_from=start_from,
                                                      page_size=page_size, graph_query_depth=graph_query_depth,
                                                      output_format=output_format,
                                                      report_spec=report_spec, body=body)
        return response

    def get_digital_products_by_name(
        self,
        name: Optional[str] = None,
        classification_names: Optional[list[str]] = None,
        body: Optional[dict] = None,
        start_from: int = 0,
        page_size: int = 0,
        graph_query_depth: int = 3, output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        **kwargs,
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
                graph_query_depth=graph_query_depth,
                name=name, classification_names=classification_names, body=body, start_from=start_from, page_size=page_size, output_format=output_format, report_spec=report_spec, **kwargs
            )
        )

    @dynamic_catch
    async def _async_find_digital_products(
        self,
        search_string: str = "*",
        body: Optional[dict] = None,
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = False,
        start_from: int = 0,
        page_size: int = 100,
        graph_query_depth: int = 3, output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        metadata_element_subtype: Optional[list[str]] = None,
        **kwargs
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
            'report_spec': report_spec,
            'metadata_element_subtypes': metadata_element_subtype
        }
        params.update(kwargs)
        
        # Filter out None values, but keep search_string even if None (it's required)
        params = {k: v for k, v in params.items() if v is not None or k == 'search_string'}
        
        response = await self._async_find_request(url, _type="DigitalProduct",
                                                  _gen_output=self._generate_collection_output, **params)
        return response

    def find_digital_products(
        self,
        search_string: str = "*",
        body: Optional[dict] = None,
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = False,
        start_from: int = 0,
        page_size: int = 100,
        graph_query_depth: int = 3, output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        metadata_element_subtype: Optional[list[str]] = None,
        **kwargs
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
                metadata_element_subtype=metadata_element_subtype,
                **kwargs
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
    ) -> Optional[str]:
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
        str | None
            The GUID of the newly created DigitalProductDependency relationship
            (DigitalProductDependency is MULTI_LINK -- see
            pyegeria.core.relationship_multiplicity -- more than one dependency
            relationship can exist between the same product pair, so this GUID
            is needed to target this specific instance later via
            _async_detach_digital_product_dependency_by_id). None if the server
            didn't return one.

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
        guid = await self._async_new_relationship_request(url, ["DigitalProductDependencyProperties"], body)
        logger.info(f"Linked {consumed_product_guid} -> {consumer_product_guid}")
        return guid

    def link_digital_product_dependency(
        self,
        consumer_product_guid: str,
        consumed_product_guid: str,
        body: Optional[dict | NewRelationshipRequestBody] = None,
    ) -> Optional[str]:
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
        str | None
            The GUID of the newly created DigitalProductDependency relationship.
            None if the server didn't return one.

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
        return loop.run_until_complete(
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
        if body is not None:
            body = self._prepare_body(body)
        cascade = bool(cascade)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_delete_digital_product_catalog(digital_product_catalog_guid, body, cascade)
        )

    @dynamic_catch
    async def _async_get_digital_product_catalog_by_guid(
        self,
        guid: str = None,
        body: Optional[dict] = None,
        graph_query_depth: int = 3, output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        **kwargs,
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
        if guid is None and "digital_product_catalog_guid" in kwargs:
            guid = kwargs.pop("digital_product_catalog_guid")
        url = f"{self.product_manager_command_root}/collections/{guid}/retrieve"
        params = {
            'graph_query_depth': graph_query_depth,
            'output_format': output_format,
            'report_spec': report_spec,
            'body': body
        }
        params.update(kwargs)
        params = {k: v for k, v in params.items() if v is not None}
        response = await self._async_get_guid_request(
            url,
            _type="DigitalProductCatalog",
            _gen_output=None,
            **params,
        )
        return response

    def get_digital_product_catalog_by_guid(
        self,
        guid: str = None,
        body: Optional[dict] = None,
        graph_query_depth: int = 3, output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        **kwargs,
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
                graph_query_depth=graph_query_depth,
                guid=guid, body=body, output_format=output_format, report_spec=report_spec, **kwargs
            )
        )

    @dynamic_catch
    async def _async_get_digital_product_catalogs_by_name(
        self,
        name: Optional[str] = None,
        classification_names: Optional[list[str]] = None,
        body: Optional[dict] = None,
        start_from: int = 0,
        page_size: int = 0,
        graph_query_depth: int = 3, output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        **kwargs,
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
        if "filter_string" in kwargs:
            name = kwargs.pop("filter_string")
        url = f"{self.product_manager_command_root}/collections/by-name"
        response = await self._async_get_name_request(url, _type="DigitalProductCatalog", _gen_output=None,
                                                      filter_string=name,
                                                      classification_names=classification_names, start_from=start_from,
                                                      page_size=page_size, graph_query_depth=graph_query_depth,
                                                      output_format=output_format,
                                                      report_spec=report_spec, body=body)
        return response

    def get_digital_product_catalogs_by_name(
        self,
        name: Optional[str] = None,
        classification_names: Optional[list[str]] = None,
        body: Optional[dict] = None,
        start_from: int = 0,
        page_size: int = 0,
        graph_query_depth: int = 3, output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        **kwargs,
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
                graph_query_depth=graph_query_depth,
                name=name, classification_names=classification_names, body=body, start_from=start_from, page_size=page_size, output_format=output_format, report_spec=report_spec, **kwargs
            )
        )

    @dynamic_catch
    async def _async_find_digital_product_catalogs(
        self,
        search_string: str = "*",
        body: Optional[dict] = None,
        starts_with: bool = False,
        ends_with: bool = False,
        ignore_case: bool = True,
        start_from: int = 0,
        page_size: int = 0,
        graph_query_depth: int = 3, output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        **kwargs
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
        
        response = await self._async_find_request(url, _type="DigitalProductCatalog", _gen_output=None, **params)
        return response

    def find_digital_product_catalogs(
        self,
        search_string: str = "*",
        body: Optional[dict] = None,
        starts_with: bool = False,
        ends_with: bool = False,
        ignore_case: bool = True,
        start_from: int = 0,
        page_size: int = 0,
        graph_query_depth: int = 3, output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        **kwargs
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
    #
    # Additional relationship maintenance - added to close the gap found by
    # scripts/omvs_audit.py against the product-manager .http ground truth
    # (2026-08-21).
    #

    @dynamic_catch
    async def _async_update_digital_product_dependency(self, digital_product_dependency_relationship_guid: str,
                                                        body: Optional[dict | UpdateRelationshipRequestBody] = None) -> None:
        """Update the properties of a DigitalProductDependency relationship, identified by its own relationship GUID. Async version."""
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/product-manager/digital-product-dependencies/{digital_product_dependency_relationship_guid}/update"
        await self._async_update_relationship_request(url, ["DigitalProductDependencyProperties"], body)

    @dynamic_catch
    def update_digital_product_dependency(self, digital_product_dependency_relationship_guid: str,
                                          body: Optional[dict | UpdateRelationshipRequestBody] = None) -> None:
        """Update the properties of a DigitalProductDependency relationship, identified by its own relationship GUID."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_update_digital_product_dependency(digital_product_dependency_relationship_guid, body))

    @dynamic_catch
    async def _async_detach_digital_product_dependency_by_id(self, digital_product_dependency_relationship_guid: str,
                                                              body: Optional[dict | DeleteRelationshipRequestBody] = None) -> None:
        """Detach one specific DigitalProductDependency relationship, identified by its own relationship GUID. Async version."""
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/product-manager/digital-product-dependencies/{digital_product_dependency_relationship_guid}/detach"
        await self._async_delete_relationship_request(url, body)

    @dynamic_catch
    def detach_digital_product_dependency_by_id(self, digital_product_dependency_relationship_guid: str,
                                                 body: Optional[dict | DeleteRelationshipRequestBody] = None) -> None:
        """Detach one specific DigitalProductDependency relationship, identified by its own relationship GUID."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_digital_product_dependency_by_id(digital_product_dependency_relationship_guid, body))

    #
    # Subscription types, and Open Data Contract / Product Standard (ODCS / ODPS) documents.
    #

    async def _async_new_subscription_type(self, digital_product_guid: str, kind: str,
                                           body: Optional[dict | NewSubscriptionTypeRequestBody]) -> Optional[str]:
        """POST a (optional) NewSubscriptionTypeRequestBody to .../subscription-types/{kind}; return the GUID of
        the governance action process that creates a subscription of this type."""
        url = (f"{self.product_manager_command_root}/digital-products/"
               f"{digital_product_guid}/subscription-types/{kind}")
        payload = None
        if isinstance(body, NewSubscriptionTypeRequestBody):
            payload = body.model_dump_json(indent=2, exclude_none=True)
        elif isinstance(body, dict):
            validated = self._validate_body(NewSubscriptionTypeRequestBody.model_validate,
                                            {"class": "NewSubscriptionTypeRequestBody", **body})
            payload = validated.model_dump_json(indent=2, exclude_none=True)
        response = await self._async_make_request("POST", url, payload)
        guid = response.json().get("guid")
        logger.info(f"Added {kind} subscription type to {digital_product_guid}: {guid}")
        return guid

    @dynamic_catch
    async def _async_create_one_time_subscription(
        self, digital_product_guid: str, body: Optional[dict | NewSubscriptionTypeRequestBody] = None
    ) -> Optional[str]:
        """Add a one-time subscription type to a digital product: subscribers receive a single notification, and
        so a single delivery of the product's data (typically to evaluate it). Async version.

        Parameters
        ----------
        digital_product_guid : str
            The digital product.
        body : dict | NewSubscriptionTypeRequestBody, optional
            Every field is optional: subscriptionManagerGUID defaults to the Baudot subscription manager;
            identifier to ONE-TIME-SUBSCRIPTION; licenseTypeGUID and serviceLevelObjectiveGUID to those the
            product is governed by.

        Returns
        -------
        str | None
            The GUID of the governance action process that creates a subscription of this type.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "NewSubscriptionTypeRequestBody",
          "identifier" : "EVALUATION-SUBSCRIPTION",
          "displayName" : "Evaluation subscription",
          "description" : "Delivers the data once to allow an evaluation of the product data."
        }
        ```
        """
        return await self._async_new_subscription_type(digital_product_guid, "one-time", body)

    @dynamic_catch
    def create_one_time_subscription(
        self, digital_product_guid: str, body: Optional[dict | NewSubscriptionTypeRequestBody] = None
    ) -> Optional[str]:
        """Add a one-time subscription type to a digital product. Returns the GUID of the governance action
        process that creates a subscription of this type."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_create_one_time_subscription(digital_product_guid, body))

    @dynamic_catch
    async def _async_create_periodic_subscription(
        self, digital_product_guid: str, body: Optional[dict | NewSubscriptionTypeRequestBody] = None
    ) -> Optional[str]:
        """Add a periodic subscription type to a digital product: subscribers receive a notification, and so a
        delivery of the product's data, every `notificationInterval` minutes. A product offering more than one
        periodic subscription type (daily and weekly, say) needs a distinct `identifier` for each. Async version.

        Returns
        -------
        str | None
            The GUID of the governance action process that creates a subscription of this type.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "NewSubscriptionTypeRequestBody",
          "identifier" : "DAILY-REFRESH-SUBSCRIPTION",
          "displayName" : "Daily refresh subscription",
          "description" : "Delivers the data once a day.",
          "notificationInterval" : 1440
        }
        ```
        """
        return await self._async_new_subscription_type(digital_product_guid, "periodic", body)

    @dynamic_catch
    def create_periodic_subscription(
        self, digital_product_guid: str, body: Optional[dict | NewSubscriptionTypeRequestBody] = None
    ) -> Optional[str]:
        """Add a periodic subscription type to a digital product. Returns the GUID of the governance action
        process that creates a subscription of this type."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_create_periodic_subscription(digital_product_guid, body))

    @dynamic_catch
    async def _async_create_ongoing_update_subscription(
        self, digital_product_guid: str, body: Optional[dict | NewSubscriptionTypeRequestBody] = None
    ) -> Optional[str]:
        """Add an ongoing-update subscription type to a digital product: subscribers receive a notification, and
        so a delivery of the product's data, whenever one of the `monitoredResourceGUIDs` changes - but no more
        often than every `notificationInterval` minutes. The monitored resource is typically the product's
        asset. Async version.

        Returns
        -------
        str | None
            The GUID of the governance action process that creates a subscription of this type.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "NewSubscriptionTypeRequestBody",
          "identifier" : "ONGOING-UPDATE-SUBSCRIPTION",
          "displayName" : "Ongoing update subscription",
          "description" : "Delivers data updates within an hour of receiving the new data.",
          "monitoredResourceGUIDs" : [ "add asset guid here" ],
          "notificationInterval" : 10
        }
        ```
        """
        return await self._async_new_subscription_type(digital_product_guid, "ongoing-update", body)

    @dynamic_catch
    def create_ongoing_update_subscription(
        self, digital_product_guid: str, body: Optional[dict | NewSubscriptionTypeRequestBody] = None
    ) -> Optional[str]:
        """Add an ongoing-update subscription type to a digital product. Returns the GUID of the governance
        action process that creates a subscription of this type."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_create_ongoing_update_subscription(digital_product_guid, body))

    async def _async_post_document(self, url: str, document: str | dict) -> Optional[str]:
        """POST a data contract / data product document and return the "guid" the server answers with, if any.
        A str (YAML or JSON text) is sent as text/plain; a dict (the ODCS / ODPS bean) as JSON."""
        if isinstance(document, str):
            response = await self._async_make_request("POST", url, document, as_text=True)
        elif isinstance(document, dict):
            response = await self._async_make_request("POST", url, document)
        else:
            raise ValueError("document must be a str (YAML or JSON text) or a dict")
        payload = response.json()
        return payload.get("guid") if isinstance(payload, dict) else None

    @dynamic_catch
    async def _async_publish_data_contract_string(self, integration_daemon_guid: str, document: str) -> None:
        """Send an Open Data Contract Standard (ODCS) data contract, as YAML or JSON text, to an integration
        daemon, which passes it on to its Bitol listeners. Async version."""
        url = (f"{self.product_manager_command_root}/integration-daemons/"
               f"{integration_daemon_guid}/data-contracts/publish-document-string")
        await self._async_post_document(url, document)

    @dynamic_catch
    def publish_data_contract_string(self, integration_daemon_guid: str, document: str) -> None:
        """Send an ODCS data contract (YAML or JSON text) to an integration daemon for its Bitol listeners."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_publish_data_contract_string(integration_daemon_guid, document))

    @dynamic_catch
    async def _async_publish_data_product_string(self, integration_daemon_guid: str, document: str) -> None:
        """Send an Open Data Product Standard (ODPS) data product, as YAML or JSON text, to an integration
        daemon, which passes it on to its Bitol listeners. Async version."""
        url = (f"{self.product_manager_command_root}/integration-daemons/"
               f"{integration_daemon_guid}/data-products/publish-document-string")
        await self._async_post_document(url, document)

    @dynamic_catch
    def publish_data_product_string(self, integration_daemon_guid: str, document: str) -> None:
        """Send an ODPS data product (YAML or JSON text) to an integration daemon for its Bitol listeners."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_publish_data_product_string(integration_daemon_guid, document))

    @dynamic_catch
    async def _async_import_data_contract_string(self, document: str) -> Optional[str]:
        """Catalog an ODCS data contract, supplied as YAML or JSON text, directly in open metadata as an
        Agreement classified as a DataSharingAgreement. Returns the new agreement's GUID. Async version."""
        url = f"{self.product_manager_command_root}/data-contracts/import-document-string"
        return await self._async_post_document(url, document)

    @dynamic_catch
    def import_data_contract_string(self, document: str) -> Optional[str]:
        """Catalog an ODCS data contract (YAML or JSON text) as a DataSharingAgreement. Returns its GUID."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_import_data_contract_string(document))

    @dynamic_catch
    async def _async_import_data_contract(self, data_contract: dict) -> Optional[str]:
        """Catalog an ODCS data contract bean (a dict with apiVersion, kind, id, name, version, status, ...)
        directly in open metadata as an Agreement classified as a DataSharingAgreement. Returns the new
        agreement's GUID. Async version."""
        url = f"{self.product_manager_command_root}/data-contracts/import-document"
        return await self._async_post_document(url, data_contract)

    @dynamic_catch
    def import_data_contract(self, data_contract: dict) -> Optional[str]:
        """Catalog an ODCS data contract bean as a DataSharingAgreement. Returns its GUID."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_import_data_contract(data_contract))

    @dynamic_catch
    async def _async_import_data_product_string(self, document: str) -> Optional[str]:
        """Catalog an ODPS data product, supplied as YAML or JSON text, directly in open metadata as a
        DigitalProduct. Returns the new product's GUID. Async version."""
        url = f"{self.product_manager_command_root}/data-products/import-document-string"
        return await self._async_post_document(url, document)

    @dynamic_catch
    def import_data_product_string(self, document: str) -> Optional[str]:
        """Catalog an ODPS data product (YAML or JSON text) as a DigitalProduct. Returns its GUID."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_import_data_product_string(document))

    @dynamic_catch
    async def _async_import_data_product(self, data_product: dict) -> Optional[str]:
        """Catalog an ODPS data product bean (a dict with apiVersion, kind, id, name, version, status, ...)
        directly in open metadata as a DigitalProduct. Returns the new product's GUID. Async version."""
        url = f"{self.product_manager_command_root}/data-products/import-document"
        return await self._async_post_document(url, data_product)

    @dynamic_catch
    def import_data_product(self, data_product: dict) -> Optional[str]:
        """Catalog an ODPS data product bean as a DigitalProduct. Returns its GUID."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_import_data_product(data_product))

    @dynamic_catch
    async def _async_generate_data_contract(self, agreement_guid: str) -> dict | str:
        """Generate the ODCS document that describes an agreement (typically one classified as a
        DataSharingAgreement). Returns the document as a dict, or NO_ELEMENTS_FOUND. Async version."""
        url = f"{self.product_manager_command_root}/agreements/{agreement_guid}/data-contract-document"
        response = await self._async_make_request("GET", url)
        return response.json().get("dataContract") or NO_ELEMENTS_FOUND

    @dynamic_catch
    def generate_data_contract(self, agreement_guid: str) -> dict | str:
        """Generate the ODCS document that describes an agreement."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_generate_data_contract(agreement_guid))

    @dynamic_catch
    async def _async_generate_data_product(self, digital_product_guid: str) -> dict | str:
        """Generate the ODPS document that describes a digital product, including the contracts referenced by
        its ports. Returns the document as a dict, or NO_ELEMENTS_FOUND. Async version."""
        url = f"{self.product_manager_command_root}/digital-products/{digital_product_guid}/data-product-document"
        response = await self._async_make_request("GET", url)
        return response.json().get("dataProduct") or NO_ELEMENTS_FOUND

    @dynamic_catch
    def generate_data_product(self, digital_product_guid: str) -> dict | str:
        """Generate the ODPS document that describes a digital product."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_generate_data_product(digital_product_guid))

    @dynamic_catch
    async def _async_get_governance_action_processes_by_name(
        self,
        name: str,
        body: Optional[dict] = None,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        **kwargs,
    ) -> list | str:
        """Retrieve the governance action processes with a matching qualified or display name, from the Product
        Catalog view service (`/product-catalog/governance-definitions/by-name`). A digital product's
        subscription types are such processes -- qualified name
        `ProvisioningActionProcess::<product>::Create Subscription::<type>` -- so this finds the process that
        Dr.Egeria's `Initiate Subscription` runs. Async version.

        There is no separate Product Catalog client: the view service is the read-only side of the product
        manager's, so this lives here, with its own URL.

        Parameters
        ----------
        name : str
            Qualified or display name to match.
        body : dict, optional
            A full FilterRequestBody; supersedes `name`.
        start_from, page_size : int
            Paging.
        output_format : str, default="JSON"
            One of "JSON", "DICT", "MD", "FORM", "REPORT", or "MERMAID".
        report_spec : str | dict, optional
            The desired output columns/fields.

        Returns
        -------
        list | str
            The matching governance action processes, or NO_ELEMENTS_FOUND.
        """
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
               f"product-catalog/governance-definitions/by-name")
        return await self._async_get_name_request(
            url, _type="GovernanceActionProcess", _gen_output=self._generate_referenceable_output,
            filter_string=name, start_from=start_from, page_size=page_size,
            output_format=output_format, report_spec=report_spec, body=body, **kwargs)

    @dynamic_catch
    def get_governance_action_processes_by_name(
        self,
        name: str,
        body: Optional[dict] = None,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        **kwargs,
    ) -> list | str:
        """Retrieve the governance action processes with a matching qualified or display name (for example a
        digital product's subscription types)."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_get_governance_action_processes_by_name(
            name, body=body, start_from=start_from, page_size=page_size, output_format=output_format,
            report_spec=report_spec, **kwargs))
