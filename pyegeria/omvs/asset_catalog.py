"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

 Asset Catalog View Service Methods - Search for assets, retrieve their properties, lineage and related glossary
 information.

 This file is in active development...

"""

import asyncio

from loguru import logger

from pyegeria.core._server_client import ServerClient
from pyegeria.view.base_report_formats import select_report_format, get_report_spec_match
from pyegeria.models import SearchStringRequestBody, ResultsRequestBody
from pyegeria.view.output_formatter import populate_columns_from_properties, _extract_referenceable_properties, \
    get_required_relationships
from pyegeria.core.utils import body_slimmer, dynamic_catch
from pyegeria.core._globals import max_paging_size
from pyegeria.core._globals import NO_ELEMENTS_FOUND, NO_ASSETS_FOUND
from typing import Any, Optional

class AssetCatalog(ServerClient):
    """
    Client for the Asset Catalog View Service.

    The Asset Catalog View Service provides methods to search for assets,
    retrieve their properties, lineage, and related glossary information.

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

    def __init__(self, view_server: str, platform_url: str, user_id: str, user_pwd: Optional[str] = None,
                 token: str = None, time_out: int = None):
        super().__init__(view_server, platform_url, user_id, user_pwd, token, time_out=time_out)
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd

    #
    # Output helpers
    #

    def _extract_asset_properties(self, element: dict, columns_struct: dict) -> dict:
        col_data = populate_columns_from_properties(element, columns_struct)
        columns_list = col_data.get("formats", {}).get("attributes", [])
        header_props = _extract_referenceable_properties(element)
        for col in columns_list:
            key = col.get("key")
            if key in header_props:
                col["value"] = header_props.get(key)
            elif isinstance(key, str) and key.lower() == "guid":
                col["value"] = header_props.get("GUID")
        # GAP specifics: processStatus, elementTypeName, stepCount
        proc_status = (
            element.get("properties", {}).get("processStatus")
            or element.get("elementProperties", {}).get("processStatus")
            or element.get("processStatus")
        )
        step_count = (
            element.get("properties", {}).get("stepCount")
            or element.get("elementProperties", {}).get("stepCount")
            or element.get("stepCount")
        )
        for col in columns_list:
            key = col.get("key")
            if key in ("process_status", "processStatus"):
                col["value"] = proc_status
            elif key == "stepCount":
                col["value"] = step_count
        col_data = get_required_relationships(element, col_data)
        mermaid_val = element.get("mermaidGraph", "") or ""
        for col in columns_list:
            if col.get("key") == "mermaid":
                col["value"] = mermaid_val
                break
        return col_data

    def _generate_asset_output(self, elements: dict | list[dict], filter_string: Optional[str] = None,
                                            element_type_name: Optional[str] = None, output_format: str = "DICT",
                                            report_spec: dict | str | None = None, **kwargs) -> str | list[dict]:
        return self._generate_formatted_output(
            elements=elements,
            query_string=filter_string,
            entity_type=element_type_name or "Asset",
            output_format=output_format,
            extract_properties_func=self._extract_asset_properties,
            report_spec=report_spec,
            **kwargs
        )

    @dynamic_catch
    async def _async_find_in_asset_domain(
            self,
            search_string: str = "*",
            starts_with: bool = True,
            ends_with: bool = False,
            ignore_case: bool = True,
            metadata_element_type_name: Optional[str] = None,
            metadata_element_subtypes: Optional[list[str]] = None,
            include_only_relationships: Optional[list[str]] = None,
            skip_relationships: Optional[list[str]] = None,
            graph_query_depth: int = 3,
            start_from: int = 0,
            page_size: int = 100,
            output_format: str = "JSON",
            report_spec: Optional[str | dict] = "Referenceable",
            body: Optional[dict | SearchStringRequestBody] = None,
            **kwargs
    ) -> list | str:
        """ Retrieve the list of asset metadata elements that contain the search string. Async Version.

        Parameters
        ----------
        search_string : str, default "*"
            Search string to match against - None or '*' indicate match against all assets.
        starts_with : bool, default True
            Starts with the supplied string.
        ends_with : bool, default False
            Ends with the supplied string.
        ignore_case : bool, default True
            Ignore case when searching.
        metadata_element_type_name : str, optional
            Specific metadata element type to filter on.
        metadata_element_subtypes : list[str], optional
            List of metadata element subtypes to filter on.
        include_only_relationships : list[str], optional
            Only include these relationship types.
        skip_relationships : list[str], optional
            Relationship types to skip.
        graph_query_depth : int, default 3
            Depth of graph traversal.
        start_from : int, default 0
            Starting index for pagination.
        page_size : int, default 100
            Number of items to return in a single page.
        output_format : str, default "JSON"
            Output format: "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON".
        report_spec : str | dict, default "Referenceable"
            Report specification for output formatting.
        body : dict | SearchStringRequestBody, optional
            Request body. If provided, overrides other parameters.
        **kwargs : dict, optional
            Additional parameters supported by the underlying find request.

        Returns
        -------
        list | str
            List of assets in the requested format.

        Raises
        ------
        ValidationError
            If the client passes incorrect parameters on the request that don't conform to the data model.
        PyegeriaException
            Issues raised in communicating or server side processing.
        NotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action.
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/asset-catalog/assets/in-domain/by-search-string"
        
        metadata_element_type = kwargs.pop("metadata_element_type", metadata_element_type_name)

        # Merge explicit parameters with kwargs
        params = {
            'search_string': search_string,
            'body': body,
            'starts_with': starts_with,
            'ends_with': ends_with,
            'ignore_case': ignore_case,
            'metadata_element_type': metadata_element_type,
            'metadata_element_subtypes': metadata_element_subtypes,
            'include_only_relationships': include_only_relationships,
            'skip_relationships': skip_relationships,
            'graph_query_depth': graph_query_depth,
            'start_from': start_from,
            'page_size': page_size,
            'output_format': output_format,
            'report_spec': report_spec
        }
        params.update(kwargs)
        
        # Filter out None values, but keep search_string even if None (it's required)
        params = {k: v for k, v in params.items() if v is not None or k == 'search_string'}
        
        response = await self._async_find_request(url, _type="Asset", _gen_output=self._generate_asset_output, **params)
        return response

    @dynamic_catch
    def find_in_asset_domain(
            self,
            search_string: str = "*",
            starts_with: bool = True,
            ends_with: bool = False,
            ignore_case: bool = True,
            metadata_element_type_name: Optional[str] = None,
            metadata_element_subtypes: Optional[list[str]] = None,
            include_only_relationships: Optional[list[str]] = None,
            skip_relationships: Optional[list[str]] = None,
            graph_query_depth: int = 3,
            start_from: int = 0,
            page_size: int = 100,
            output_format: str = "JSON",
            report_spec: Optional[str | dict] = "Referenceable",
            body: Optional[dict | SearchStringRequestBody] = None,
            **kwargs
    ) -> list | str:
        """ Retrieve the list of asset metadata elements that contain the search string.

        Parameters
        ----------
        search_string : str, default "*"
            Search string to match against - None or '*' indicate match against all assets.
        starts_with : bool, default True
            Starts with the supplied string.
        ends_with : bool, default False
            Ends with the supplied string.
        ignore_case : bool, default True
            Ignore case when searching.
        metadata_element_type_name : str, optional
            Specific metadata element type to filter on.
        metadata_element_subtypes : list[str], optional
            List of metadata element subtypes to filter on.
        include_only_relationships : list[str], optional
            Only include these relationship types.
        skip_relationships : list[str], optional
            Relationship types to skip.
        graph_query_depth : int, default 3
            Depth of graph traversal.
        start_from : int, default 0
            Starting index for pagination.
        page_size : int, default 100
            Number of items to return in a single page.
        output_format : str, default "JSON"
            Output format: "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON".
        report_spec : str | dict, default "Referenceable"
            Report specification for output formatting.
        body : dict | SearchStringRequestBody, optional
            Request body. If provided, overrides other parameters.
        **kwargs : dict, optional
            Additional parameters supported by the underlying find request.

        Returns
        -------
        list | str
            List of assets in the requested format.

        Raises
        ------
        ValidationError
            If the client passes incorrect parameters on the request that don't conform to the data model.
        PyegeriaException
            Issues raised in communicating or server side processing.
        NotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action.
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_find_in_asset_domain(
                search_string=search_string,
                starts_with=starts_with,
                ends_with=ends_with,
                ignore_case=ignore_case,
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
                **kwargs
            )
        )

    async def _async_get_asset_graph_by_guid(
        self,
        guid: str,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "MERMAID",
        report_spec: str | dict = "Common-Mermaid",
        body: Optional[dict | ResultsRequestBody] = None,
        **kwargs,
    ) -> str | dict:
        """Return all the elements that are anchored to an asset plus relationships between these elements and to
        other elements.

        Async version.

        Parameters
        ----------
        guid : str
            The unique identity of the asset to get the graph for.
        start_from : int, default 0
            The index from which to start fetching.
        page_size : int, default 0
            The maximum number of items to fetch.
        output_format : str, default "MERMAID"
            The desired output format. One of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID", or "JSON".
        report_spec : str | dict, default "Common-Mermaid"
            The desired output columns/fields to include.
        body : dict | ResultsRequestBody, optional
            If provided, the search parameters in the body will supersede other attributes.
        **kwargs : dict, optional
            Additional query parameters.

        Returns
        -------
        str | dict
            The asset graph in the requested format.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        PyegeriaNotAuthorizedException
            The principle specified by the user_id does not have authorization.
        """

        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/asset-catalog/assets/{guid}/as-graph"
        response = await self._async_get_results_body_request(
            url=url,
            _type="Asset",
            _gen_output=self._generate_asset_output,
            start_from=start_from,
            page_size=page_size,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
            **kwargs,
        )
        return response

    def get_asset_graph_by_guid(
        self,
        guid: str,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "MERMAID",
        report_spec: str | dict = "Common-Mermaid",
        body: Optional[dict | ResultsRequestBody] = None,
        **kwargs,
    ) -> str | dict:
        """Return all the elements that are anchored to an asset plus relationships between these elements and to
        other elements.

        Parameters
        ----------
        guid : str
            The unique identity of the asset to get the graph for.
        start_from : int, default 0
            The index from which to start fetching.
        page_size : int, default 0
            The maximum number of items to fetch.
        output_format : str, default "MERMAID"
            The desired output format. One of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID", or "JSON".
        report_spec : str | dict, default "Common-Mermaid"
            The desired output columns/fields to include.
        body : dict | ResultsRequestBody, optional
            If provided, the search parameters in the body will supersede other attributes.
        **kwargs : dict, optional
            Additional query parameters.

        Returns
        -------
        str | dict
            The asset graph in the requested format.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        PyegeriaNotAuthorizedException
            The principle specified by the user_id does not have authorization.
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_asset_graph_by_guid(
                guid=guid,
                start_from=start_from,
                page_size=page_size,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs,
            )
        )
        return response

    def get_asset_mermaid_graph(
        self,
        guid: str,
        start_from: int = 0,
        page_size: int = 0,
    ) -> str:
        """Return the asset graph as mermaid markdown string.

        Parameters
        ----------
        guid : str
            The unique identity of the asset to get the graph for.
        start_from : int, default 0
            The index from which to start fetching.
        page_size : int, default 0
            The maximum number of items to fetch.

        Returns
        -------
        str
            A mermaid string representing the asset graph.

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        PyegeriaNotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action.
        """

        asset_graph = self.get_asset_graph_by_guid(guid=guid, start_from=start_from, page_size=page_size)
        return asset_graph[0]

    async def _async_get_asset_lineage_graph_by_guid(
        self,
        guid: str,
        effective_time: Optional[str] = None,
        as_of_time: Optional[str] = None,
        relationship_types: Optional[list[str]] = None,
        limit_to_isc_q_name: Optional[str] = None,
        hilight_isc_q_name: Optional[str] = None,
        all_anchors: bool = False,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "DICT",
        report_spec: str | dict = "Common-Mermaid",
        **kwargs,
    ) -> str | dict:
        """Return the asset lineage including a mermaid markdown string.

        Async version.

        Parameters
        ----------
        guid : str
            The unique identity of the asset to get the graph for.
        effective_time : str, optional
            Effective time to query on. If not specified, the current time is used.
        as_of_time : str, optional
            As-of time to query on. If not specified, the current time is used.
        relationship_types : list[str], optional
            Relationship types to include in the lineage graph. If not specified, all relationship types are included.
        limit_to_isc_q_name : str, optional
            If specified, filters results to only include information supply chains with the given qualified name.
        hilight_isc_q_name : str, optional
            If specified, highlights the information supply chain with the given qualified name.
        all_anchors : bool, default False
            Whether to include all anchors.
        start_from : int, default 0
            The index from which to start fetching.
        page_size : int, default 0
            The maximum number of items to fetch.
        output_format : str, default "DICT"
            The desired output format.
        report_spec : str | dict, default "Common-Mermaid"
            The desired output columns/fields to include.
        **kwargs : dict, optional
            Additional query parameters.

        Returns
        -------
        str | dict
            A dictionary of the asset graph that includes a mermaid markdown string.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """

        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/asset-catalog/assets/{guid}/as-lineage-graph"
        body = {
            "class": "AssetLineageGraphRequestBody",
            "effectiveTime": effective_time,
            "asOfTime": as_of_time,
            "relationshipTypes": relationship_types,
            "limitToISCQualifiedName": limit_to_isc_q_name,
            "highlightISCQualifiedName": hilight_isc_q_name,
            "allAnchors": all_anchors,
            "startFrom": start_from,
            "pageSize": page_size,
            "queryGraphDepth": 5,
        }

        response = await self._async_make_request("POST", url, body_slimmer(body))
        element = response.json().get("element", NO_ASSETS_FOUND)
        if isinstance(element, str):
            logger.info(NO_ELEMENTS_FOUND)
            return NO_ELEMENTS_FOUND

        if output_format != "JSON":  # return a simplified markdown representation
            logger.info(
                f"Found elements, output format: {output_format} and report_spec: {report_spec}"
            )
            return self._generate_asset_output(
                element, None, "Asset", output_format, report_spec
            )
        return element

    def get_asset_lineage_graph_by_guid(
        self,
        guid: str,
        effective_time: Optional[str] = None,
        as_of_time: Optional[str] = None,
        relationship_types: Optional[list[str]] = None,
        limit_to_isc_q_name: Optional[str] = None,
        hilight_isc_q_name: Optional[str] = None,
        all_anchors: bool = False,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "DICT",
        report_spec: str | dict = "Common-Mermaid",
        **kwargs,
    ) -> str | dict:
        """Return the asset lineage including a mermaid markdown string.

        Parameters
        ----------
        guid : str
            The unique identity of the asset to get the graph for.
        effective_time : str, optional
            Effective time to query on. If not specified, the current time is used.
        as_of_time : str, optional
            As-of time to query on. If not specified, the current time is used.
        relationship_types : list[str], optional
            Relationship types to include in the lineage graph. If not specified, all relationship types are included.
        limit_to_isc_q_name : str, optional
            If specified, filters results to only include information supply chains with the given qualified name.
        hilight_isc_q_name : str, optional
            If specified, highlights the information supply chain with the given qualified name.
        all_anchors : bool, default False
            Whether to include all anchors.
        start_from : int, default 0
            The index from which to start fetching.
        page_size : int, default 0
            The maximum number of items to fetch.
        output_format : str, default "DICT"
            The desired output format.
        report_spec : str | dict, default "Common-Mermaid"
            The desired output columns/fields to include.
        **kwargs : dict, optional
            Additional query parameters.

        Returns
        -------
        str | dict
            A dictionary of the asset graph that includes a mermaid markdown string.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_asset_lineage_graph_by_guid(
                guid=guid,
                effective_time=effective_time,
                as_of_time=as_of_time,
                relationship_types=relationship_types,
                limit_to_isc_q_name=limit_to_isc_q_name,
                hilight_isc_q_name=hilight_isc_q_name,
                all_anchors=all_anchors,
                start_from=start_from,
                page_size=page_size,
                output_format=output_format,
                report_spec=report_spec,
                **kwargs,
            )
        )
        return response

    def get_asset_lineage_mermaid_graph(
        self,
        guid: str,
        effective_time: Optional[str] = None,
        as_of_time: Optional[str] = None,
        relationship_types: Optional[list[str]] = None,
        limit_to_isc_q_name: Optional[str] = None,
        hilight_isc_q_name: Optional[str] = None,
        all_anchors: bool = False,
        start_from: int = 0,
        page_size: int = 0,
    ) -> str:
        """Return the asset lineage including a mermaid markdown string.

        Parameters
        ----------
        guid : str
            The unique identity of the asset to get the graph for.
        effective_time : str, optional
            Effective time to query on. If not specified, the current time is used.
        as_of_time : str, optional
            As-of time to query on. If not specified, the current time is used.
        relationship_types : list[str], optional
            Relationship types to include in the lineage graph. If not specified, all relationship types are included.
        limit_to_isc_q_name : str, optional
            If specified, filters results to only include information supply chains with the given qualified name.
        hilight_isc_q_name : str, optional
            If specified, highlights the information supply chain with the given qualified name.
        all_anchors : bool, default False
            Whether to include all anchors.
        start_from : int, default 0
            The index from which to start fetching.
        page_size : int, default 0
            The maximum number of items to fetch.

        Returns
        -------
        str
            A mermaid string representing the lineage.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        PyegeriaNotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action.
        """

        asset_graph = self.get_asset_lineage_graph_by_guid(
            guid=guid,
            effective_time=effective_time,
            as_of_time=as_of_time,
            relationship_types=relationship_types,
            limit_to_isc_q_name=limit_to_isc_q_name,
            hilight_isc_q_name=hilight_isc_q_name,
            all_anchors=all_anchors,
            start_from=start_from,
            page_size=page_size,
            output_format="JSON",
        )
        return asset_graph.get("mermaidGraph")


    async def _async_get_assets_by_metadata_collection_id(
        self,
        metadata_collection_id: str,
        metadata_element_type_name: Optional[str] = None,
        include_only_relationships: Optional[list[str]] = None,
        skip_relationships: Optional[list[str]] = None,
        graph_query_depth: int = 3,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Referenceable",
        body: Optional[dict] = None,
        **kwargs,
    ) -> str | list:
        """Return a list of assets from the requested metadata collection. Async version.

        Parameters
        ----------
        metadata_collection_id : str
            The unique identity of the metadata collection to return assets from.
        metadata_element_type_name : str, optional
            An asset type to filter on. If not specified, all assets in the collection are returned.
        include_only_relationships : list[str], optional
            Only include these relationship types.
        skip_relationships : list[str], optional
            Relationship types to skip.
        graph_query_depth : int, default 3
            Depth of graph traversal.
        start_from : int, optional
            The index from which to start fetching. Default is 0.
        page_size : int, optional
            The maximum number of assets to fetch in a single request. Default is 0 (all).
        output_format : str, optional
            The desired output format. Default is "JSON".
        report_spec : str | dict, optional
            The desired output columns/fields to include. Default is "Referenceable".
        body : dict, optional
            Request body to pass to Egeria.
        **kwargs : dict, optional
            Additional query parameters.

        Returns
        -------
        list | str
            A list of assets or a string if an error occurs or no assets are found.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        type_name = kwargs.pop("type_name", metadata_element_type_name)
        kwargs.pop("effective_time", None)

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/asset-catalog/assets/by-metadata-collection-id/"
            f"{metadata_collection_id}"
        )

        if body is None:
            body = {
                "filter": type_name,
                "startFrom": start_from,
                "pageSize": page_size,
            }
        body_s = body_slimmer(body)
        response = await self._async_make_request("POST", url, body_s)
        elements =  response.json().get("elements", "NO_ASSETS_FOUND")
        if type(elements) is str:
            logger.info(NO_ELEMENTS_FOUND)
            return NO_ELEMENTS_FOUND

        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format} and report_spec: {report_spec}")
            return self._generate_asset_output(elements, None, "Asset",
                                               output_format, report_spec)
        return elements

    def get_assets_by_metadata_collection_id(
        self,
        metadata_collection_id: str,
        metadata_element_type_name: Optional[str] = None,
        include_only_relationships: Optional[list[str]] = None,
        skip_relationships: Optional[list[str]] = None,
        graph_query_depth: int = 3,
        start_from: int = 0,
        page_size: int = max_paging_size,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Referenceable",
        body: Optional[dict] = None,
        **kwargs,
    ) -> str | list:
        """Return a list of assets from the requested metadata collection.

        Parameters
        ----------
        metadata_collection_id : str
            The unique identity of the metadata collection to return assets from.
        metadata_element_type_name : str, optional
            An asset type to filter on. If not specified, all assets in the collection are returned.
        include_only_relationships : list[str], optional
            Only include these relationship types.
        skip_relationships : list[str], optional
            Relationship types to skip.
        graph_query_depth : int, default 3
            Depth of graph traversal.
        start_from : int, optional
            The index from which to start fetching. Default is 0.
        page_size : int, optional
            The maximum number of assets to fetch in a single request. Default is `max_paging_size`.
        output_format : str, optional
            The desired output format. Default is "JSON".
        report_spec : str | dict, optional
            The desired output columns/fields to include. Default is "Referenceable".
        body : dict, optional
            Request body to pass to Egeria.
        **kwargs : dict, optional
            Additional query parameters.

        Returns
        -------
        list | str
            A list of assets or a string if an error occurs or no assets are found.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_assets_by_metadata_collection_id(
                metadata_collection_id=metadata_collection_id,
                metadata_element_type_name=metadata_element_type_name,
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
        return response




    async def _async_get_asset_types(self) -> list | str:
        """Return the list of asset types supported by the Asset Catalog View Service. Async version.

        Returns
        -------
        list | str
            A list of asset types or NO_ASSETS_FOUND.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """

        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/asset-catalog/assets/types"

        response = await self._async_make_request("GET", url)

        return response.json().get("types", "NO_ASSETS_FOUND")

    def get_asset_types(self) -> list | str:
        """Return the list of asset types supported by the Asset Catalog View Service.

        Returns
        -------
        list | str
            A list of asset types or NO_ASSETS_FOUND.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_asset_types())
        return response


if __name__ == "__main__":
    print("Main-asset-catalog")
