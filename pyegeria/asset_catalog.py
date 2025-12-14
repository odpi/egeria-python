"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

 Asset Catalog View Service Methods - Search for assets, retrieve their properties, lineage and related glossary
 information.

 This file is in active development...

"""

import asyncio
import json

from httpx import Response
from loguru import logger

from pyegeria import ServerClient
from pyegeria.base_report_formats import select_report_format, get_report_spec_match
from pyegeria.models import NewElementRequestBody, TemplateRequestBody, SearchStringRequestBody, ResultsRequestBody
from pyegeria.output_formatter import populate_columns_from_properties, _extract_referenceable_properties, \
    get_required_relationships, generate_output
from pyegeria.utils import body_slimmer
from pyegeria._globals import TEMPLATE_GUIDS, max_paging_size
from pyegeria._globals import NO_ELEMENTS_FOUND, NO_ASSETS_FOUND
from ._validators import validate_search_string


class AssetCatalog(ServerClient):
    """Set up and maintain automation services in Egeria.

    Attributes:
        view_server : str
            The name of the View Server to use.
        platform_url : str
            URL of the server platform to connect to
        user_id : str
            The identity of the user calling the method - this sets a default optionally used by the methods
            when the user doesn't pass the user_id on a method call.
        user_pwd: str
            The password associated with the user_id. Defaults to None

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
                                                  include_only_classification_names=classification_names,
                                                  metadata_element_subtypes=metadata_element_subtypes,
                                                  starts_with=starts_with, ends_with=ends_with, ignore_case=ignore_case,
                                                  start_from=start_from, page_size=page_size,
                                                  output_format=output_format, report_spec=report_spec, body=body)

        return response

    def find_in_asset_domain(self, search_string: str, classification_names: list[str] = None,
                                          metadata_element_subtypes: list[str] = None, start_from: int = 0,
                                          page_size: int = max_paging_size, starts_with: bool = True,
                                          ends_with: bool = False, ignore_case: bool = True, output_format: str="JSON",
                                          report_spec:str="Referenceable",
                                          body: dict | SearchStringRequestBody = None)-> list | str:

        """Retrieve the list of engine action metadata elements that contain the search string. Async Version.
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

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        PyegeriaNotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        For more information see: https://egeria-project.org/concepts/engine-action
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
          other elements. Async Version.
         Parameters
         ----------
         asset_guid : str
             The unique identity of the asset to get the graph for.

         start_from : int, optional
             The index from which to start fetching the engine actions. Default is 0.

         page_size : int, optional
             The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
        report_spec: str | dict , optional, default = None
            - The desired output columns/fields to include.

         Returns
         -------
        dict or str
             A dictionary of the asset graph.

         Raises
         ------
         PyegeriaException
             One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
             Egeria errors.
         PyegeriaNotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action

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
             The index from which to start fetching the engine actions. Default is 0.

         page_size : int, optional
             The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.
        output_format: str, default = "JSON"
            one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
        report_spec: str | dict , optional, default = None
            The desired output columns/fields to include.

         Returns
         -------
        dict or str
             A dictionary of the asset graph.

         Args:
             body ():

         Raises
         ------
         PyegeriaException
             One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
             Egeria errors.
         PyegeriaNotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action

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
             The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

         Returns
         -------
        str | dict
             A dictionary of the asset graph that includes a mermaid markdown string.

         Raises
         ------
         PyegeriaInvalidParameterException
             One of the parameters is null or invalid (for example, bad URL or invalid values).
         PyegeriaAPIException
             The server reported an error while processing a valid request.
         PyegeriaUnauthorizedException
             The requesting user is not authorized to issue this request.

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
            if speficied, highlights the information supply chain with the given name.

         start_from : int, optional
             The index from which to start fetching the engine actions. Default is 0.

         page_size : int, optional
             The maximum number of elements to fetch in a single request. Default is `max_paging_size`.

         Returns
         -------
        dict or str
             A dictionary of the asset graph.

         Raises
         ------
         PyegeriaInvalidParameterException
             One of the parameters is null or invalid (for example, bad URL or invalid values).
         PyegeriaAPIException
             The server reported an error while processing a valid request.
         PyegeriaUnauthorizedException
             The requesting user is not authorized to issue this request.

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
        """Return a list of assets that come from the requested metadata collection. Can optionally
         specify an type name as a filter and an effective time. Async Version.

         Parameters
         ----------
         metadata_collection_id : str
            The unique identity of the metadata collection to return assets from.

         type_name: str, optional
             An asset type to optionally filter on. If not specified, all assets in the collection will be returned.

         effective_time: str, optional
             The effective time to filter on. If not specified, the current time is used.

         start_from : int, optional
            The index from which to start fetching the engine actions. Default is 0.

         page_size : int, optional
            The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

         Returns
         -------
        list or str
            A list of assets in a [dict].

         Raises:
         ------
         PyegeriaInvalidParameterException
         PyegeriaAPIException
         PyegeriaUnauthorizedException

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
        """Return a list of assets that come from the requested metadata collection. Can optionally
         specify an type name as a filter and an effective time. Async Version.

         Parameters
         ----------
         metadata_collection_id : str
            The unique identity of the metadata collection to return assets from.

         type_name: str, optional
             An asset type to optionally filter on. If not specified, all assets in the collection will be returned.

         effective_time: str, optional
             The effective time to filter on. If not specified, the current time is used.

         start_from : int, optional
            The index from which to start fetching the engine actions. Default is 0.

         page_size : int, optional
            The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

         Returns
         -------
        list or str
            A list of assets in a [dict].

         Raises:
         ------
         PyegeriaInvalidParameterException
         PyegeriaAPIException
         PyegeriaUnauthorizedException

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




    async def _async_get_asset_types(self) -> str | dict:
        """Return all the elements that are anchored to an asset plus relationships between these elements and to
         other elements. Async Version.
        Parameters
        ----------

        Returns
        -------
        dict or str
            A dictionary of the asset graph.

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        PyegeriaNotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action

        """

        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/asset-catalog/assets/types"

        response = await self._async_make_request("GET", url)

        return response.json().get("types", "NO_ASSETS_FOUND")

    def get_asset_types(self) -> str | dict:
        """Return all the elements that are anchored to an asset plus relationships between these elements and to
          other elements.
         Parameters
         ----------

         Returns
         -------
        dict or str
             A dictionary of the asset graph.

         Raises
         ------
         PyegeriaException
             One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
             Egeria errors.
         PyegeriaNotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action

         """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_asset_types())
        return response


if __name__ == "__main__":
    print("Main-asset-catalog")
