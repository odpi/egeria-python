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
    get_required_relationships, generate_output
from pyegeria.core.utils import body_slimmer
from pyegeria.core._globals import max_paging_size
from pyegeria.core._globals import NO_ELEMENTS_FOUND, NO_ASSETS_FOUND


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

    def __init__(self, view_server: str, platform_url: str, user_id: str, user_pwd: str = None,
                 token: str = None):
        super().__init__(view_server, platform_url, user_id, user_pwd, token)
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

    def _generate_asset_output(self, elements: dict | list[dict], filter: str | None,
                                            element_type_name: str | None, output_format: str = "DICT",
                                            report_spec: dict | str | None = None) -> str | list[dict]:
        entity_type = element_type_name
        get_additional_props_func = None
        if report_spec:
            if isinstance(report_spec, str):
                output_formats = select_report_format(report_spec, output_format)
            else:
                output_formats = get_report_spec_match(report_spec, output_format)
        elif element_type_name:
            output_formats = select_report_format(element_type_name, output_format)
        else:
            output_formats = select_report_format(entity_type, output_format)
        if output_formats is None:
            output_formats = select_report_format("Default", output_format)
        return generate_output(
            elements,
            filter,
            entity_type,
            output_format,
            self._extract_asset_properties,
            None,
            output_formats,
        )

    async def _async_find_in_asset_domain(self, search_string: str, classification_names: list[str] = None,
                                          metadata_element_subtypes: list[str] = None, start_from: int = 0,
                                          page_size: int = max_paging_size, starts_with: bool = True,
                                          ends_with: bool = False, ignore_case: bool = True, output_format: str="JSON",
                                          report_spec:str="Referenceable",
                                          body: dict | SearchStringRequestBody = None) -> list | str:
        """Locate string value in elements that are anchored to assets.  Async Version.
        Asset: https: // egeria - project.org / concepts / asset /

        Parameters
        ----------
        search_string : str
            The string used for searching engine actions by name.

        starts_with : bool, optional
            Whether to search engine actions that start with the given search string. Default is False.

        ends_with : bool, optional
            Whether to search engine actions that end with the given search string. Default is False.

        ignore_case : bool, optional
            Whether to ignore case while searching engine actions. Default is False.

        start_from : int, optional
            The index from which to start fetching the engine actions. Default is 0.

        page_size : int, optional
            The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
        report_spec: str | dict , optional, default = None
            - The desired output columns/fields to include.
        body: dict | SearchStringRequestBody, optional, default = None
            - if provided, the search parameters in the body will supercede other attributes, such as "search_string"


        Returns
        -------
        List[dict] or str
            A list of dictionaries representing the engine actions found based on the search query.
            If no actions are found, returns the string "no actions".

        Args:
            classification_names ():
            output_format ():
            report_spec ():

        Raises:
        ------
        PyegeriaException

        Notes
        -----

        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/asset-catalog/assets/in-domain/"
            f"by-search-string"
        )
        response = await self._async_find_request(url, _type="ExternalReference",
                                                  _gen_output=self._generate_asset_output, search_string=search_string,
                                                  output_format="JSON", page_size=0, body=body)

        return response

    def find_in_asset_domain(self, search_string: str, classification_names: list[str] = None,
                                          metadata_element_subtypes: list[str] = None, start_from: int = 0,
                                          page_size: int = max_paging_size, starts_with: bool = True,
                                          ends_with: bool = False, ignore_case: bool = True, output_format: str="JSON",
                                          report_spec:str="Referenceable",
                                          body: dict | SearchStringRequestBody = None)-> list | str:

        """Retrieve the list of assets that contain the search string.

        Parameters
        ----------
        search_string : str
            The string used for searching assets.
        classification_names : list[str], optional
            A list of classification names to filter by.
        metadata_element_subtypes : list[str], optional
            A list of metadata element subtypes to filter by.
        start_from : int, optional
            The index from which to start fetching the assets. Default is 0.
        page_size : int, optional
            The maximum number of assets to fetch in a single request. Default is `max_paging_size`.
        starts_with : bool, optional
            Whether to search assets that start with the given search string. Default is True.
        ends_with : bool, optional
            Whether to search assets that end with the given search string. Default is False.
        ignore_case : bool, optional
            Whether to ignore case while searching. Default is True.
        output_format : str, default = "JSON"
            The desired output format. One of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID", or "JSON".
        report_spec : str | dict, optional
            The desired output columns/fields to include. Default is "Referenceable".
        body : dict | SearchStringRequestBody, optional
            If provided, the search parameters in the body will supersede other attributes.

        Returns
        -------
        list[dict] or str
            A list of dictionaries representing the assets found.
            If no assets are found, returns NO_ASSETS_FOUND.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        PyegeriaNotAuthorizedException
            The principle specified by the user_id does not have authorization.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_in_asset_domain(search_string, classification_names,
                                             metadata_element_subtypes, start_from, page_size,
                                             starts_with, ends_with, ignore_case,
                                             output_format, report_spec, body)
        )
        return response

    async def _async_get_asset_graph(
        self,
        asset_guid: str,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "MERMAID",
        report_spec: str = "Common-Mermaid",
        body: dict | ResultsRequestBody = None
    ) -> str | dict:
        """Return all the elements that are anchored to an asset plus relationships between these elements and to
        other elements. Async version.

        Parameters
        ----------
        asset_guid : str
            The unique identity of the asset to get the graph for.
        start_from : int, optional
            The index from which to start fetching. Default is 0.
        page_size : int, optional
            The maximum number of items to fetch. Default is 0 (all).
        output_format : str, default = "MERMAID"
            The desired output format. One of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID", or "JSON".
        report_spec : str | dict, optional
            The desired output columns/fields to include. Default is "Common-Mermaid".
        body : dict | ResultsRequestBody, optional
            If provided, the search parameters in the body will supersede other attributes.

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

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/asset-catalog/assets/{asset_guid}/"
            f"as-graph"
        )
        response = await self._async_get_results_body_request(url, "Asset", self._generate_asset_output,
                                                        start_from, page_size, output_format, report_spec, body)
        return response

    def get_asset_graph(
        self,
        asset_guid: str,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "MERMAID",
        report_spec: str = "Common-Mermaid",
        body: dict | ResultsRequestBody = None
    ) -> str | dict:
        """Return all the elements that are anchored to an asset plus relationships between these elements and to
        other elements.

        Parameters
        ----------
        asset_guid : str
            The unique identity of the asset to get the graph for.
        start_from : int, optional
            The index from which to start fetching. Default is 0.
        page_size : int, optional
            The maximum number of items to fetch. Default is 0 (all).
        output_format : str, default = "MERMAID"
            The desired output format. One of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID", or "JSON".
        report_spec : str | dict, optional
            The desired output columns/fields to include. Default is "Common-Mermaid".
        body : dict | ResultsRequestBody, optional
            If provided, the search parameters in the body will supersede other attributes.

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
            self._async_get_asset_graph(asset_guid, start_from, page_size, output_format,
                                        report_spec, body)
        )
        return response

    def get_asset_mermaid_graph(
        self,
        asset_guid: str,
        start_from: int = 0,
        page_size: int = 0,
    ) -> str:
        """Return the asset graph as mermaid markdown string.
         Parameters
         ----------
         asset_guid : str
             The unique identity of the asset to get the graph for.

         start_from : int, optional
             The index from which to start fetching the engine actions. Default is 0.

         page_size : int, optional
             The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

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
             The principle specified by the user_id does not have authorization for the requested action

        """

        asset_graph = self.get_asset_graph(asset_guid, start_from, page_size)
        return asset_graph[0]

    async def _async_get_asset_lineage_graph(
        self,
        asset_guid: str,
        effective_time: str = None,
        as_of_time: str = None,
        relationship_types: [str] = None,
        limit_to_isc_q_name: str = None,
        hilight_isc_q_name: str = None,
        all_anchors: bool = False,
        start_from: int = 0,
        page_size: int =0,
        output_format: str = "DICT",
        report_spec: str = "Common-Mermaid",

    ) -> str | dict:
        """Return the asset lineage including a mermaid markdown string. Async version.

        Parameters
        ----------
        asset_guid : str
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
        all_anchors : bool, optional
            Whether to include all anchors. Default is False.
        start_from : int, optional
            The index from which to start fetching. Default is 0.
        page_size : int, optional
            The maximum number of items to fetch. Default is 0 (all).
        output_format : str, optional
            The desired output format. Default is "DICT".
        report_spec : str, optional
            The desired output columns/fields to include. Default is "Common-Mermaid".

        Returns
        -------
        str | dict
            A dictionary of the asset graph that includes a mermaid markdown string.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/asset-catalog/assets/{asset_guid}/"
            f"as-lineage-graph"
        )
        body = {
            "class": "AssetLineageGraphRequestBody",
            "effectiveTime": effective_time,
            "asOfTime": as_of_time,
            "relationshipTypes": relationship_types,
            "limitToISCQualifiedName": limit_to_isc_q_name,
            "highlightISCQualifiedName": hilight_isc_q_name,
            "allAnchors": all_anchors,
            "startFrom": start_from,
            "pageSize": page_size
            }

        response = await self._async_make_request("POST", url, body_slimmer(body))
        element = response.json().get("element",NO_ASSETS_FOUND)
        if type(element) is str:
            logger.info(NO_ELEMENTS_FOUND)
            return NO_ELEMENTS_FOUND

        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format} and report_spec: {report_spec}")
            return self._generate_asset_output(element, None, "Asset",
                               output_format, report_spec)
        return element


    def get_asset_lineage_graph(
        self,
        asset_guid: str,
        effective_time: str = None,
        as_of_time: str = None,
        relationship_types: [str] = None,
        limit_to_isc_q_name: str = None,
        hilight_isc_q_name: str = None,
        all_anchors: bool = False,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "DICT",
        report_spec: str = "Common-Mermaid",
        ) -> str | dict:
        """Return the asset lineage including a mermaid markdown string.

        Parameters
        ----------
        asset_guid : str
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
        all_anchors : bool, optional
            Whether to include all anchors. Default is False.
        start_from : int, optional
            The index from which to start fetching. Default is 0.
        page_size : int, optional
            The maximum number of items to fetch. Default is 0 (all).
        output_format : str, optional
            The desired output format. Default is "DICT".
        report_spec : str, optional
            The desired output columns/fields to include. Default is "Common-Mermaid".

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
            self._async_get_asset_lineage_graph(asset_guid, effective_time, as_of_time, relationship_types,
                                                limit_to_isc_q_name, hilight_isc_q_name, all_anchors,
                                                start_from, page_size, output_format, report_spec)
        )
        return response

    def get_asset_lineage_mermaid_graph(
        self,
        asset_guid: str,
        effective_time: str = None,
        as_of_time: str = None,
        relationship_types: [str] = None,
        limit_to_isc_q_name: str = None,
        hilight_isc_q_name: str = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        ) -> str:
        """Return the asset lineage including a mermaid markdown string. Async Version.
         Parameters
         ----------
         asset_guid : str
             The unique identity of the asset to get the graph for.
        effective_time: str, default is None
            Effective time to query on. If not specified, the current time is used.
        as_of_time: str = None
            as_of_time to query on. If not specified, the current time is used.
        relationship_types: [str], default is None,
            relationship types to include in the lineage graph. If not specified, all relationship types are included.
        limit_to_isc_q_name: str = None,
            if specified, filters results to only include information supply chains with the given name.
        hilight_isc_q_name: str = None,
            if specified, highlights the information supply chain with the given name.

         start_from : int, optional
             The index from which to start fetching the engine actions. Default is 0.

         page_size : int, optional
             The maximum number of elements to fetch in a single request.
             Default is `max_paging_size`.

        Returns
         -------
        str
             A mermaid string representing the lineage.

         Raises:
         ------
         PyegeriaInvalidParameterException
         PyegeriaAPIException
         PyegeriaUnauthorizedException

    """

        asset_graph = self.get_asset_lineage_graph(asset_guid, effective_time,
                                                   as_of_time, relationship_types,
                                                   limit_to_isc_q_name, hilight_isc_q_name,
                                                   start_from, page_size, "JSON")
        return asset_graph.get("mermaidGraph")


    async def _async_get_assets_by_metadata_collection_id(
        self,
        metadata_collection_id: str,
        type_name: str = None,
        effective_time: str = None,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: str = "Referenceable",
    ) -> str | list:
        """Return a list of assets from the requested metadata collection. Async version.

        Parameters
        ----------
        metadata_collection_id : str
            The unique identity of the metadata collection to return assets from.
        type_name : str, optional
            An asset type to filter on. If not specified, all assets in the collection are returned.
        effective_time : str, optional
            The effective time to filter on. If not specified, the current time is used.
        start_from : int, optional
            The index from which to start fetching. Default is 0.
        page_size : int, optional
            The maximum number of assets to fetch in a single request. Default is 0 (all).
        output_format : str, optional
            The desired output format. Default is "JSON".
        report_spec : str, optional
            The desired output columns/fields to include. Default is "Referenceable".

        Returns
        -------
        list | str
            A list of assets or a string if an error occurs or no assets are found.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/asset-catalog/assets/by-metadata-collection-id/"
            f"{metadata_collection_id}"
        )

        body = {"filter": type_name,
                "effectiveTime": effective_time,
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
        type_name: str = None,
        effective_time: str = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        output_format: str = "JSON",
        report_spec: str = "Referenceable",
    ) -> str | list:
        """Return a list of assets from the requested metadata collection.

        Parameters
        ----------
        metadata_collection_id : str
            The unique identity of the metadata collection to return assets from.
        type_name : str, optional
            An asset type to filter on. If not specified, all assets in the collection are returned.
        effective_time : str, optional
            The effective time to filter on. If not specified, the current time is used.
        start_from : int, optional
            The index from which to start fetching. Default is 0.
        page_size : int, optional
            The maximum number of assets to fetch in a single request. Default is `max_paging_size`.
        output_format : str, optional
            The desired output format. Default is "JSON".
        report_spec : str, optional
            The desired output columns/fields to include. Default is "Referenceable".

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
                metadata_collection_id,
                type_name,
                effective_time,
                start_from,
                page_size,
                output_format,
                report_spec,
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
