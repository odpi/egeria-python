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

from pyegeria import Client, max_paging_size, body_slimmer, TEMPLATE_GUIDS
from pyegeria._exceptions import (
    InvalidParameterException,
)
from ._validators import validate_search_string


class AssetCatalog(Client):
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

    def __init__(
        self,
        view_server: str,
        platform_url: str,
        user_id: str,
        user_pwd: str = None,
        token: str = None,
    ):
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd
        Client.__init__(self, view_server, platform_url, user_id, user_pwd, token=token)

    async def _async_create_element_from_template(self, body: dict) -> str:
        """Create a new metadata element from a template.  Async version.
        Parameters
        ----------
        body : str
            The json body used to instantiate the template.

        Returns
        -------
        Response
           The guid of the resulting element

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        See also: https://egeria-project.org/features/templated-cataloguing/overview/
        The full description of the body is shown below:
           {
             "typeName" : "",
             "initialStatus" : "",
             "initialClassifications" : "",
             "anchorGUID" : "",
             "isOwnAnchor" : "",
             "effectiveFrom" : "",
             "effectiveTo" : "",
             "templateGUID" : "",
             "templateProperties" : {},
             "placeholderPropertyValues" : {
               "placeholderPropertyName1" : "placeholderPropertyValue1",
               "placeholderPropertyName2" : "placeholderPropertyValue2"
             },
             "parentGUID" : "",
             "parentRelationshipTypeName" : "",
             "parentRelationshipProperties" : "",
             "parentAtEnd1" : "",
             "effectiveTime" : ""
           }
        """

        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/automated-curation/catalog-templates/new-element"
        response = await self._async_make_request("POST", url, body)
        return response.json().get("guid", "GUID failed to be returned")

    def create_element_from_template(self, body: dict) -> str:
        """Create a new metadata element from a template.  Async version.
        Parameters
        ----------
        body : str
             The json body used to instantiate the template.
        server : str, optional
            The name of the view server to use. If not provided, the default server name will be used.

        Returns
        -------
        Response
            The guid of the resulting element

         Raises
         ------
         InvalidParameterException
         PropertyServerException
         UserNotAuthorizedException

         Notes
         -----
         See also: https://egeria-project.org/features/templated-cataloguing/overview/
         The full description of the body is shown below:
             {
               "typeName" : "",
               "initialStatus" : "",
               "initialClassifications" : "",
               "anchorGUID" : "",
               "isOwnAnchor" : "",
               "effectiveFrom" : "",
               "effectiveTo" : "",
               "templateGUID" : "",
               "templateProperties" : {},
               "placeholderPropertyValues" : {
                 "placeholderPropertyName1" : "placeholderPropertyValue1",
                 "placeholderPropertyName2" : "placeholderPropertyValue2"
               },
               "parentGUID" : "",
               "parentRelationshipTypeName" : "",
               "parentRelationshipProperties" : "",
               "parentAtEnd1" : "",
               "effectiveTime" : ""
             }
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_element_from_template(body)
        )
        return response

    async def _async_create_kafka_server_element_from_template(
        self, kafka_server: str, host_name: str, port: str
    ) -> str:
        """Create a Kafka server element from a template. Async version.

        Parameters
        ----------
        kafka_server : str
            The name of the Kafka server.

        host_name : str
            The host name of the Kafka server.

        port : str
            The port number of the Kafka server.

        Returns
        -------
        str
            The GUID of the Kafka server element.
        """

        body = {
            "templateGUID": TEMPLATE_GUIDS["Apache Kafka Server"],
            "isOwnAnchor": "true",
            "placeholderPropertyValues": {
                "serverName": kafka_server,
                "hostIdentifier": host_name,
                "portNumber": port,
            },
        }
        response = await self._async_create_element_from_template(body)
        return response

    def create_kafka_server_element_from_template(
        self, kafka_server: str, host_name: str, port: str
    ) -> str:
        """Create a Kafka server element from a template.

        Parameters
        ----------
        kafka_server : str
            The name of the Kafka server.

        host_name : str
            The host name of the Kafka server.

        port : str
            The port number of the Kafka server.

        Returns
        -------
        str
            The GUID of the Kafka server element.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_kafka_server_element_from_template(
                kafka_server, host_name, port
            )
        )
        return response

    async def _async_create_postgres_server_element_from_template(
        self,
        postgres_server: str,
        host_name: str,
        port: str,
        db_user: str,
        db_pwd: str,
    ) -> str:
        """Create a Postgres server element from a template. Async version.

        Parameters
        ----------
        postgres_server : str
            The name of the Postgres server.

        host_name : str
            The host name of the Postgres server.

        port : str
            The port number of the Postgres server.

        db_user: str
            User name to connect to the database

        db_pwd: str
            User password to connect to the database

        Returns
        -------
        str
            The GUID of the Kafka server element.
        """
        body = {
            "templateGUID": TEMPLATE_GUIDS["PostgreSQL Server"],
            "isOwnAnchor": "true",
            "placeholderPropertyValues": {
                "serverName": postgres_server,
                "hostIdentifier": host_name,
                "portNumber": port,
                "databaseUserId": db_user,
                "databasePassword": db_pwd,
            },
        }
        response = await self._async_create_element_from_template(body)
        return response

    def create_postgres_server_element_from_template(
        self,
        postgres_server: str,
        host_name: str,
        port: str,
        db_user: str,
        db_pwd: str,
    ) -> str:
        """Create a Postgres server element from a template.

        Parameters
        ----------
        postgres_server : str
            The name of the Postgres server.

        host_name : str
            The host name of the Postgres server.

        port : str
            The port number of the Postgres server.

        db_user: str
            User name to connect to the database

        db_pwd: str
            User password to connect to the database

        Returns
        -------
        str
            The GUID of the Postgres server element.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_postgres_server_element_from_template(
                postgres_server, host_name, port, db_user, db_pwd
            )
        )
        return response

    #
    # Engine Actions
    #

    async def _async_find_in_asset_domain(
        self,
        search_string: str,
        start_from: int = 0,
        page_size: int = max_paging_size,
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = True,
        time_out: int = 60,
    ) -> list | str:
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

        Returns
        -------
        List[dict] or str
            A list of dictionaries representing the engine actions found based on the search query.
            If no actions are found, returns the string "no actions".

        Raises:
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        For more information see: https://egeria-project.org/concepts/engine-action
        """

        validate_search_string(search_string)

        starts_with_s = str(starts_with).lower()
        ends_with_s = str(ends_with).lower()
        ignore_case_s = str(ignore_case).lower()

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/asset-catalog/assets/in-domain/"
            f"by-search-string?startFrom={start_from}&pageSize={page_size}&startsWith={starts_with_s}&"
            f"endWith={ends_with_s}&ignoreCase={ignore_case_s}"
        )
        body = {"filter": search_string}
        response = await self._async_make_request("POST", url, body, time_out=time_out)
        return response.json().get("searchMatches", "no assets found")

    def find_in_asset_domain(
        self,
        search_string: str,
        start_from: int = 0,
        page_size: int = max_paging_size,
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = True,
        time_out: int = 60,
    ) -> list | str:
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

        Returns
        -------
        List[dict] or str
            A list of dictionaries representing the engine actions found based on the search query.
            If no actions are found, returns the string "no actions".

        Raises:
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        For more information see: https://egeria-project.org/concepts/engine-action
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_in_asset_domain(
                search_string,
                start_from,
                page_size,
                starts_with,
                ends_with,
                ignore_case,
                time_out,
            )
        )
        return response

    async def _async_get_asset_graph(
        self,
        asset_guid: str,
        start_from: int = 0,
        page_size: int = max_paging_size,
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

         Returns
         -------
        dict or str
             A dictionary of the asset graph.

         Raises:
         ------
         InvalidParameterException
         PropertyServerException
         UserNotAuthorizedException

        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/asset-catalog/assets/{asset_guid}/"
            f"as-graph?startFrom={start_from}&pageSize={page_size}"
        )

        response = await self._async_make_request("GET", url)
        return response.json().get("assetGraph", "no asset found")

    def get_asset_graph(
        self,
        asset_guid: str,
        start_from: int = 0,
        page_size: int = max_paging_size,
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

         Returns
         -------
        dict or str
             A dictionary of the asset graph.

         Raises:
         ------
         InvalidParameterException
         PropertyServerException
         UserNotAuthorizedException

        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_asset_graph(asset_guid, start_from, page_size)
        )
        return response

    def get_asset_mermaid_graph(
        self,
        asset_guid: str,
        start_from: int = 0,
        page_size: int = max_paging_size,
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

         Raises:
         ------
         InvalidParameterException
         PropertyServerException
         UserNotAuthorizedException

        """

        asset_graph = self.get_asset_graph(asset_guid, start_from, page_size)
        return asset_graph.get("mermaidGraph")

    async def _async_get_asset_lineage_graph(
        self,
        asset_guid: str,
        start_from: int = 0,
        page_size: int = max_paging_size,
    ) -> str | dict:
        """Return the asset lineage including a mermaid markdown string. Async Version.
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
        str | dict
             A dictionary of the asset graph that includes a mermaid markdown string.

         Raises:
         ------
         InvalidParameterException
         PropertyServerException
         UserNotAuthorizedException

        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/asset-catalog/assets/{asset_guid}/"
            f"as-lineage-graph?startFrom={start_from}&pageSize={page_size}"
        )

        response = await self._async_make_request("POST", url)
        return response.json().get("assetLineageGraph", "no asset found")

    def get_asset_lineage_graph(
        self,
        asset_guid: str,
        start_from: int = 0,
        page_size: int = max_paging_size,
    ) -> str | dict:
        """Return the asset lineage including a mermaid markdown string. Async Version.
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
        dict or str
             A dictionary of the asset graph.

         Raises:
         ------
         InvalidParameterException
         PropertyServerException
         UserNotAuthorizedException

        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_asset_lineage_graph(asset_guid, start_from, page_size)
        )
        return response

    def get_asset_lineage_mermaid_graph(
        self,
        asset_guid: str,
        start_from: int = 0,
        page_size: int = max_paging_size,
    ) -> str:
        """Return the lineage as mermaid markdown string. Async Version.
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
             A mermaid string representing the lineage.

         Raises:
         ------
         InvalidParameterException
         PropertyServerException
         UserNotAuthorizedException

        """

        asset_graph = self.get_asset_lineage_graph(asset_guid, start_from, page_size)
        return asset_graph.get("mermaidGraph")

    async def _async_get_assets_by_metadata_collection_id(
        self,
        metadata_collection_id: str,
        type_name: str = None,
        effective_time: str = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
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
         InvalidParameterException
         PropertyServerException
         UserNotAuthorizedException

        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/asset-catalog/assets/by-metadata-collection-id/"
            f"{metadata_collection_id}?startFrom={start_from}&pageSize={page_size}"
        )

        body = {"filter": type_name, "effectiveTime": effective_time}
        body_s = body_slimmer(body)
        response = await self._async_make_request("POST", url, body_s)
        return response.json().get("assets", "no assets found")

    def get_assets_by_metadata_collection_id(
        self,
        metadata_collection_id: str,
        type_name: str = None,
        effective_time: str = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
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
         InvalidParameterException
         PropertyServerException
         UserNotAuthorizedException

        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_assets_by_metadata_collection_id(
                metadata_collection_id,
                type_name,
                effective_time,
                start_from,
                page_size,
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

        Raises:
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """

        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/asset-catalog/assets/types"

        response = await self._async_make_request("GET", url)

        return response.json().get("types", "No assets found")

    def get_asset_catalog_types(self) -> str | dict:
        """Return all the elements that are anchored to an asset plus relationships between these elements and to
          other elements.
         Parameters
         ----------

         Returns
         -------
        dict or str
             A dictionary of the asset graph.

         Raises:
         ------
         InvalidParameterException
         PropertyServerException
         UserNotAuthorizedException

        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_asset_types())
        return response


if __name__ == "__main__":
    print("Main-asset-catalog")
