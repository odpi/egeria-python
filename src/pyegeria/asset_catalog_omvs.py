"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

 Asset Catalog View Service Methods - Search for assets, retrieve their properties, lineage and related glossary
 information.

 This file is in active development...

"""
import asyncio
from datetime import datetime
import json

from httpx import Response

from pyegeria import Client, max_paging_size, body_slimmer
from pyegeria._exceptions import (
    InvalidParameterException,
)
from ._validators import validate_name, validate_guid, validate_search_string


class AssetCatalog(Client):
    """ Set up and maintain automation services in Egeria.

    Attributes:
        server_name : str
            The name of the View Server to use.
        platform_url : str
            URL of the server platform to connect to
        user_id : str
            The identity of the user calling the method - this sets a default optionally used by the methods
            when the user doesn't pass the user_id on a method call.
        user_pwd: str
            The password associated with the user_id. Defaults to None
        verify_flag: bool
            Flag to indicate if SSL Certificates should be verified in the HTTP requests.
            Defaults to False.

    """

    def __init__(
            self,
            server_name: str,
            platform_url: str,
            user_id: str,
            user_pwd: str = None,
            verify_flag: bool = False,
    ):
        Client.__init__(self, server_name, platform_url, user_id, user_pwd, verify_flag)
        self.cur_command_root = f"{platform_url}/servers/"


    async def _async_create_element_from_template(self, body: dict, server: str = None) -> str:
        """ Create a new metadata element from a template.  Async version.
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

        server = self.server_name if server is None else server

        url = f"{self.platform_url}/servers/{server}/api/open-metadata/automated-curation/catalog-templates/new-element"
        response = await self._async_make_request("POST", url, body)
        return response.json().get("guid", "GUID failed to be returned")

    def create_element_from_template(self, body: dict, server: str = None) -> str:
        """ Create a new metadata element from a template.  Async version.
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
            self._async_create_element_from_template(body, server)
        )
        return response

    async def _async_create_kafka_server_element_from_template(self, kafka_server: str, host_name: str, port: str,
                                                               server: str = None) -> str:
        """ Create a Kafka server element from a template. Async version.

            Parameters
            ----------
            kafka_server : str
                The name of the Kafka server.

            host_name : str
                The host name of the Kafka server.

            port : str
                The port number of the Kafka server.

            server : str, optional
                The name of the view server to use. Default uses the client instance.

            Returns
            -------
            str
                The GUID of the Kafka server element.
        """

        body = {
            "templateGUID": "5e1ff810-5418-43f7-b7c4-e6e062f9aff7",
            "isOwnAnchor": 'true',
            "placeholderPropertyValues": {
                "serverName": kafka_server,
                "hostIdentifier": host_name,
                "portNumber": port
            }
        }
        response = await self._async_create_element_from_template(body, server)
        return response

    def create_kafka_server_element_from_template(self, kafka_server: str, host_name: str, port: str,
                                                  server: str = None) -> str:
        """ Create a Kafka server element from a template.

            Parameters
            ----------
            kafka_server : str
                The name of the Kafka server.

            host_name : str
                The host name of the Kafka server.

            port : str
                The port number of the Kafka server.

            server : str, optional
                The name of the view server to use. Default uses the client instance.

            Returns
            -------
            str
                The GUID of the Kafka server element.
            """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_kafka_server_element_from_template(kafka_server, host_name, port, server)
        )
        return response

    async def _async_create_postgres_server_element_from_template(self, postgres_server: str, host_name: str, port: str,
                                                                  db_user: str, db_pwd: str, server: str = None) -> str:
        """ Create a Postgres server element from a template. Async version.

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

            server : str, optional
                The name of the view server to use. Default uses the client instance.

            Returns
            -------
            str
                The GUID of the Kafka server element.
        """
        body = {
            "templateGUID": "542134e6-b9ce-4dce-8aef-22e8daf34fdb",
            "isOwnAnchor": 'true',
            "placeholderPropertyValues": {
                "serverName": postgres_server,
                "hostIdentifier": host_name,
                "portNumber": port,
                "databaseUserId": db_user,
                "databasePassword": db_pwd
            }
        }
        response = await self._async_create_element_from_template(body, server)
        return response

    def create_postgres_server_element_from_template(self, postgres_server: str, host_name: str, port: str,
                                                     db_user: str, db_pwd: str, server: str = None) -> str:
        """ Create a Postgres server element from a template.

            Parameters
            ----------
            postgres_server : str
                The name of the Postgres server.

            host_name : str
                The host name of the Postgres server.

            port : str
                The port number of the Postgres server.

            server : str, optional
                The name of the view server to use. Default uses the client instance.

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
            self._async_create_postgres_server_element_from_template(postgres_server, host_name,
                                                                     port, db_user, db_pwd, server)
        )
        return response

    #
    # Engine Actions
    #

    async def _async_find_assets_in_domain(self, search_string: str, start_from: int = 0,
                                          page_size: int = max_paging_size, starts_with: bool = True,
                                          ends_with: bool = False, ignore_case: bool = True,
                                          server: str =  None) -> list | str:
        """ Retrieve the list of engine action metadata elements that contain the search string. Async Version.
        Parameters
        ----------
        search_string : str
            The string used for searching engine actions by name.

        server : str, optional
            The name of the server. If None, will use the default server specified in the instance will be used.

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
        server = self.server_name if server is None else server
        validate_search_string(search_string)
        if search_string == "*":
            search_string = None
        starts_with_s = str(starts_with).lower()
        ends_with_s = str(ends_with).lower()
        ignore_case_s = str(ignore_case).lower()

        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/asset-catalog/assets/in-domain/"
               f"by-search-string?startFrom={start_from}&pageSize={page_size}&startsWith={starts_with_s}&"
               f"endWith={ends_with_s}&ignoreCase={ignore_case_s}"
               )
        body = {
            "filter": search_string
        }
        response = await self._async_make_request("POST", url, body)
        return response.json().get("searchMatches", "no assets found")

    def find_assets_in_domain(self, search_string: str, start_from: int = 0,
                                          page_size: int = max_paging_size, starts_with: bool = True,
                                          ends_with: bool = False, ignore_case: bool = True,
                                          server: str =  None) -> list | str:
        """ Retrieve the list of engine action metadata elements that contain the search string. Async Version.
        Parameters
        ----------
        search_string : str
            The string used for searching engine actions by name.

        server : str, optional
            The name of the server. If None, will use the default server specified in the instance will be used.

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
            self._async_find_assets_in_domain(search_string,  start_from,page_size,
                                              starts_with, ends_with, ignore_case, server)
        )
        return response


    async def _async_get_asset_graph(self, asset_guid:str, server: str = None, start_from: int = 0,
                                     page_size: int = max_paging_size) -> str| dict:
        """ Return all the elements that are anchored to an asset plus relationships between these elements and to
            other elements. Async Version.
           Parameters
           ----------
           asset_guid : str
               The unique identity of the asset to get the graph for.

           server : str, optional
               The name of the server. If None, will use the default server specified in the instance will be used.

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
        server = self.server_name if server is None else server

        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/asset-catalog/assets/{asset_guid}/"
               f"as-graph?startFrom={start_from}&pageSize={page_size}")

        response = await self._async_make_request("GET", url)
        return response.json().get("assetGraph", "no asset found")

    def get_asset_graph(self, asset_guid: str, server: str = None, start_from: int = 0,
                               page_size: int = max_paging_size) -> str | dict:
        """ Return all the elements that are anchored to an asset plus relationships between these elements and to
            other elements.
           Parameters
           ----------
           asset_guid : str
               The unique identity of the asset to get the graph for.

           server : str, optional
               The name of the server. If None, will use the default server specified in the instance will be used.

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
            self._async_get_asset_graph(asset_guid, server,start_from, page_size)
        )
        return response

    async def _async_get_assets_by_metadata_collection_id(self, metadata_collection_id:str, type_name: str = None,
                                                          effective_time: str = None, server: str = None,
                                                          start_from: int = 0, page_size: int = max_paging_size) -> str| list:
        """ Return a list of assets that come from the requested metadata collection. Can optionally
            specify an type name as a filter and an effective time. Async Version.

            Parameters
            ----------
            metadata_collection_id : str
               The unique identity of the metadata collection to return assets from.

            type_name: str, optional
                An asset type to optionally filter on. If not specified, all assets in the collection will be returned.

            effective_time: str, optional
                The effective time to filter on. If not specified, the current time is used.

            server : str, optional
               The name of the server. If None, will use the default server specified in the instance will be used.

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
        server = self.server_name if server is None else server

        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/asset-catalog/assets/by-metadata-collection-id/"
               f"{metadata_collection_id}?startFrom={start_from}&pageSize={page_size}")

        body = {
            "filter": type_name,
            "effectiveTime": effective_time
        }
        body_s = body_slimmer(body)
        print(json.dumps(body_s))
        response = await self._async_make_request("POST", url, body_s)
        return response.json().get("assets", "no assets found")

    def get_assets_by_metadata_collection_id(self, metadata_collection_id: str, type_name: str = None,
                                                    effective_time: str = None, server: str = None,
                                                    start_from: int = 0,
                                                    page_size: int = max_paging_size) -> str | list:
        """ Return a list of assets that come from the requested metadata collection. Can optionally
            specify an type name as a filter and an effective time. Async Version.

            Parameters
            ----------
            metadata_collection_id : str
               The unique identity of the metadata collection to return assets from.

            type_name: str, optional
                An asset type to optionally filter on. If not specified, all assets in the collection will be returned.

            effective_time: str, optional
                The effective time to filter on. If not specified, the current time is used.

            server : str, optional
               The name of the server. If None, will use the default server specified in the instance will be used.

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
            self._async_get_assets_by_metadata_collection_id(metadata_collection_id, type_name,
                                                             effective_time,server,start_from,
                                                             page_size)
        )
        return response

    async def _async_get_asset_catalog_types(self, server: str = None) -> str| dict:
        """ Return all the elements that are anchored to an asset plus relationships between these elements and to
            other elements. Async Version.
           Parameters
           ----------
           asset_guid : str
               The unique identity of the asset to get the graph for.

           server : str, optional
               The name of the server. If None, will use the default server specified in the instance will be used.

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
        server = self.server_name if server is None else server

        url = f"{self.platform_url}/servers/{server}/api/open-metadata/asset-catalog/assets/types"

        response = await self._async_make_request("GET", url)

        return response.json().get('types',"No assets found")

    def get_asset_catalog_types(self, server: str = None) -> str | dict:
        """ Return all the elements that are anchored to an asset plus relationships between these elements and to
            other elements.
           Parameters
           ----------
           asset_guid : str
               The unique identity of the asset to get the graph for.

           server : str, optional
               The name of the server. If None, will use the default server specified in the instance will be used.

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
            self._async_get_asset_catalog_types(server)
        )
        return response

if __name__ == "__main__":
    p = AssetCatalog("active-metadata-store", "https://127.0.0.1:9443", "garygeeke", verify_flag=False)
    response = p.get_assets_by_metadata_collection_id()
    out = response.json()
    print(out)
