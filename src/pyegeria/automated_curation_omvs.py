"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

 Automated Curation View Service Methods - this file is in active development...

"""
import asyncio
from datetime import datetime

from httpx import Response

from pyegeria import Client, max_paging_size, body_slimmer
from pyegeria._exceptions import (
    InvalidParameterException,
)
from ._validators import validate_name, validate_guid, validate_search_string


class AutomatedCuration(Client):
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
    async def _async_get_engine_actions(self, server: str = None, start_from: int = 0,
                                        page_size: int = max_paging_size) -> list:
        """ Retrieve the engine actions that are known to the server. Async version.
        Parameters
        ----------
        server : str, optional
            The name of the server. If not provided, it uses the default server name.
        start_from : int, optional
            The starting index of the actions to retrieve. Default is 0.
        page_size : int, optional
            The maximum number of actions to retrieve per page. Default is the global maximum paging size.

        Returns
        -------
        [dict]
            A list of engine action descriptions as JSON.

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        For more information see: https://egeria-project.org/concepts/engine-action
        """
        server = self.server_name if server is None else server

        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/automated-curation/engine-actions?"
               f"startFrom={start_from}&pageSize={page_size}")

        response = await self._async_make_request("GET", url)
        return response.json().get("elements", "No elements")

    def get_engine_actions(self, server: str = None, start_from: int = 0, page_size: int = max_paging_size) -> list:
        """ Retrieve the engine actions that are known to the server.
            Parameters
            ----------
            server : str, optional
                The name of the server. If not provided, it uses the default server name.
            start_from : int, optional
                The starting index of the actions to retrieve. Default is 0.
            page_size : int, optional
                The maximum number of actions to retrieve per page. Default is the global maximum paging size.

            Returns
            -------
            [dict]
                A list of engine action descriptions as JSON.

            Raises
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
            self._async_get_engine_actions(server, start_from, page_size)
        )
        return response

    async def _async_get_engine_action(self, engine_action_guid: str, server: str = None) -> dict:
        """ Request the status and properties of an executing engine action request. Async version.
        Parameters
        ----------
        engine_action_guid : str
            The GUID of the engine action to retrieve.

        server : str, optional
            The name of the server. If not provided, the default server name will be used.

        Returns
        -------
        dict
            The JSON representation of the engine action.

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        For more information see: https://egeria-project.org/concepts/engine-action
        """
        server = self.server_name if server is None else server

        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/automated-curation/engine-actions/"
               f"{engine_action_guid}")

        response = await self._async_make_request("GET", url)
        return response.json().get("element", "No element found")

    def get_engine_action(self, engine_action_guid: str, server: str = None) -> dict:
        """ Request the status and properties of an executing engine action request.
            Parameters
            ----------
            engine_action_guid : str
                The GUID of the engine action to retrieve.

            server : str, optional
                The name of the server. If not provided, the default server name will be used.

            Returns
            -------
            dict
                The JSON representation of the engine action.

            Raises
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
            self._async_get_engine_action(engine_action_guid, server)
        )
        return response

    async def _async_cancel_engine_action(self, engine_action_guid: str, server: str = None) -> None:
        """ Request that an engine action request is cancelled and any running governance service is stopped. Async Ver.
            Parameters
            ----------
            engine_action_guid : str
                The GUID of the engine action to retrieve.

            server : str, optional
                The name of the server. If not provided, the default server name will be used.

            Returns
            -------
            dict
                The JSON representation of the engine action.

            Raises
            ------
            InvalidParameterException
            PropertyServerException
            UserNotAuthorizedException

            Notes
            -----
            For more information see: https://egeria-project.org/concepts/engine-action
        """
        server = self.server_name if server is None else server
        validate_guid(engine_action_guid)

        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/automated-curation/engine-actions/"
               f"{engine_action_guid}/cancel")

        await self._async_make_request("POST", url)

    def cancel_engine_action(self, engine_action_guid: str, server: str = None) -> None:
        """ Request that an engine action request is cancelled and any running governance service is stopped.
            Parameters
            ----------
            engine_action_guid : str
                The GUID of the engine action to retrieve.

            server : str, optional
                The name of the server. If not provided, the default server name will be used.

            Returns
            -------
            dict
                The JSON representation of the engine action.

            Raises
            ------
            InvalidParameterException
            PropertyServerException
            UserNotAuthorizedException

            Notes
            -----
            For more information see: https://egeria-project.org/concepts/engine-action
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_cancel_engine_action(engine_action_guid, server))
        return

    async def _async_get_active_engine_actions(self, server: str = None, start_from: int = 0,
                                               page_size: int = max_paging_size) -> list | str:
        """ Retrieve the engine actions that are still in process. Async Version.

            Parameters:
            ----------
            server : str, optional
                The name of the server. If not provided, it uses the default server name.
            start_from : int, optional
                The starting index of the actions to retrieve. Default is 0.
            page_size : int, optional
                The maximum number of actions to retrieve per page. Default is the global maximum paging size.

            Returns:
            -------
                List[dict]: A list of JSON representations of governance action processes matching the provided name.

            Raises:
            ------
                InvalidParameterException: If the API response indicates an error (non-200 status code),
                this exception is raised with details from the response content.

            Notes
            -----
            For more information see: https://egeria-project.org/concepts/engine-action

        """
        server = self.server_name if server is None else server

        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/automated-curation/engine-actions/active?"
               f"startFrom={start_from}&pageSize={page_size}")

        response = await self._async_make_request("GET", url)
        return response.json().get("elements", "no actions")

    def get_active_engine_actions(self, server: str = None, start_from: int = 0, page_size: int = 0) -> list | str:
        """ Retrieve the engine actions that are still in process.

        Parameters:
        ----------
        server : str, optional
            The name of the server. If not provided, it uses the default server name.
        start_from : int, optional
            The starting index of the actions to retrieve. Default is 0.
        page_size : int, optional
            The maximum number of actions to retrieve per page. Default is the global maximum paging size.

        Returns
        -------
            List[dict]: A list of JSON representations of governance action processes matching the provided name.

        Raises
        ------
            InvalidParameterException: If the API response indicates an error (non-200 status code),
            this exception is raised with details from the response content.
        Notes
        -----
        For more information see: https://egeria-project.org/concepts/engine-action

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_active_engine_actions(server, start_from, page_size)
        )
        return response

    async def _async_get_engine_actions_by_name(self, name: str, server: str = None, start_from: int = 0,
                                                page_size: int = max_paging_size) -> list | str:
        """ Retrieve the list of engine action metadata elements with a matching qualified or display name.
        There are no wildcards supported on this request. Async Version.
        Parameters
        ----------
        name : str
            The name of the engine action to retrieve.
        server : str, optional
             The name of the server to retrieve the engine action from. If not provided, the default server specified in
             the instance will be used.
        start_from : int, optional
            The index to start retrieving engine actions from. If not provided, the default value will be used.
        page_size : int, optional
            The maximum number of engine actions to retrieve in a single request. If not provided, the default global
            maximum paging size will be used.

        Returns
        -------
        list of dict | str
            A list of dictionaries representing the retrieved engine actions, or "no actions" if no engine actions were
             found with the given name.
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
        validate_name(name)

        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/automated-curation/engine-actions/by-name?"
               f"startFrom={start_from}&pageSize={page_size}")
        body = {
            "string": name
        }
        response = await self._async_make_request("POST", url, body)
        return response.json().get("elements", "no actions")

    def get_engine_actions_by_name(self, name: str, server: str = None, start_from: int = 0,
                                   page_size: int = max_paging_size) -> list | str:
        """ Retrieve the list of engine action metadata elements with a matching qualified or display name.
        There are no wildcards supported on this request.

        Parameters
        ----------
        name : str
            The name of the engine action to retrieve.
        server : str, optional
            The name of the server to retrieve the engine action from. If not provided, the default server specified in
            the instance will be used.
        start_from : int, optional
            The index to start retrieving engine actions from. If not provided, the default value will be used.
        page_size : int, optional
            The maximum number of engine actions to retrieve in a single request. If not provided, the default global
             maximum paging size will be used.

        Returns
        -------
        list of dict | str
            A list of dictionaries representing the retrieved engine actions, or "no actions" if no engine actions were
            found with the given name.
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
            self._async_get_engine_actions_by_name(name, server, start_from, page_size)
        )
        return response

    async def _async_find_engine_actions(self, search_string: str, server: str = None, starts_with: bool = False,
                                         ends_with: bool = False, ignore_case: bool = False, start_from: int = 0,
                                         page_size: int = max_paging_size) -> list | str:
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

        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/automated-curation/engine-actions/"
               f"by-search-string?startFrom={start_from}&pageSize={page_size}&startsWith={starts_with_s}&"
               f"endsWith={ends_with_s}&ignoreCase={ignore_case_s}"
               )
        body = {
            "class": "SearchStringRequestBody",
            "name": search_string
        }
        response = await self._async_make_request("POST", url, body)
        return response.json().get("elements", "no actions")

    def find_engine_actions(self, search_string: str = "*", server: str = None, starts_with: bool = False,
                            ends_with: bool = False, ignore_case: bool = False, start_from: int = 0,
                            page_size: int = max_paging_size) -> list | str:
        """ Retrieve the list of engine action metadata elements that contain the search string.
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
            self._async_find_engine_actions(search_string, server, starts_with,
                                            ends_with, ignore_case, start_from,
                                            page_size)
        )
        return response

    #
    # Governance action processes
    #

    async def _async_get_governance_action_process_by_guid(self, process_guid: str, server: str = None) -> dict | str:
        """ Retrieve the governance action process metadata element with the supplied unique identifier. Async Version.

            Parameters:
            ----------
                process_guid: str
                  The GUID (Globally Unique Identifier) of the governance action process.
                server: str, optional
                    The name of the server. If None, will use the default server specified in the instance will be used.

            Returns:
            -------
                dict: The JSON representation of the governance action process element.

            Raises:
            ------
                InvalidParameterException: If the API response indicates an error (non-200 status code),
                this exception is raised with details from the response content.
                PropertyServerException: If the API response indicates a server side error.
                UserNotAuthorizedException:
            """

        server = self.server_name if server is None else server
        validate_guid(process_guid)

        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/automated-curation/"
               f"governance-action-processes/{process_guid}")

        response = await self._async_make_request("GET", url)
        return response.json().get("element", "no actions")

    def get_governance_action_process_by_guid(self, process_guid: str, server: str = None) -> dict | str:
        """ Retrieve the governance action process metadata element with the supplied unique identifier.

            Parameters:
            ----------
                process_guid: str
                  The GUID (Globally Unique Identifier) of the governance action process.
                server: str, optional
                    The name of the server. If None, will use the default server specified in the instance will be used.
            Returns:
            -------
                dict: The JSON representation of the governance action process element.

            Raises:
            ------
                InvalidParameterException: If the API response indicates an error (non-200 status code),
                this exception is raised with details from the response content.
                PropertyServerException: If the API response indicates a server side error.
                UserNotAuthorizedException:
            """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_governance_action_process_by_guid(process_guid, server)
        )
        return response

    async def _async_gov_action_process_graph(self, process_guid: str, server: str = None) -> dict | str:
        """ Retrieve the governance action process metadata element with the supplied unique
            identifier along with the flow definition describing its implementation. Async Version.
        Parameters
        ----------
        process_guid : str
            The process GUID to retrieve the graph for.
        server : str, optional
            The name of the server to retrieve the graph from. If not provided, the default server name will be used.

        Returns
        -------
        dict or str
            A dictionary representing the graph of the governance action process, or the string "no actions"
            if no actions are found.
        Raises:
        ------
            InvalidParameterException: If the API response indicates an error (non-200 status code),
            this exception is raised with details from the response content.
            PropertyServerException: If the API response indicates a server side error.
            UserNotAuthorizedException:

        """
        server = self.server_name if server is None else server
        validate_guid(process_guid)

        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/automated-curation/"
               f"governance-action-processes/{process_guid}/graph")

        response = await self._async_make_request("GET", url)
        return response.json().get("element", "no actions")

    def gov_action_process_graph(self, process_guid: str, server: str = None) -> dict | str:
        """ Retrieve the governance action process metadata element with the supplied unique
            identifier along with the flow definition describing its implementation.
           Parameters
           ----------
           process_guid : str
               The process GUID to retrieve the graph for.
           server : str, optional
               The name of the server to retrieve the graph from. If not provided, the default server name will be used.

           Returns
           -------
           dict or str
               A dictionary representing the graph of the governance action process, or the string "no actions"
               if no actions are found.
           Raises:
           ------
               InvalidParameterException: If the API response indicates an error (non-200 status code),
               this exception is raised with details from the response content.
               PropertyServerException: If the API response indicates a server side error.
               UserNotAuthorizedException:

       """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_gov_action_process_graph(process_guid, server)
        )
        return response

    async def _async_get_gov_action_processes_by_name(self, name: str, server: str = None, start_from: int = None,
                                                      page_size: int = max_paging_size) -> list | str:
        """ Retrieve the list of governance action process metadata elements with a matching qualified or display name.
            There are no wildcards supported on this request. Async Version.

           Parameters
           ----------
           name : str
               The name of the engine action to retrieve.
           server : str, optional
               The name of the server to retrieve the engine action from. If not provided, the default server specified
               in the instance will be used.
           start_from : int, optional
               The index to start retrieving engine actions from. If not provided, the default value will be used.
           page_size : int, optional
               The maximum number of engine actions to retrieve in a single request. If not provided, the default
               global maximum paging size will be used.

           Returns
           -------
           list of dict | str
               A list of dictionaries representing the retrieved engine actions,
               or "no actions" if no engine actions were found with the given name.
           Raises:
           ------
           InvalidParameterException
           PropertyServerException
           UserNotAuthorizedException
       """
        server = self.server_name if server is None else server
        validate_name(name)

        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/automated-curation/governance-action-processes/"
               f"by-name?startFrom={start_from}&pageSize={page_size}")
        body = {
            "class": "NameRequestBody",
            "name": name
        }
        response = await self._async_make_request("GET", url, body)
        return response.json().get("elements", "no actions")

    def get_gov_action_processes_by_name(self, name: str, server: str = None, start_from: int = 0,
                                         page_size: int = max_paging_size) -> list | str:
        """ Retrieve the list of governance action process metadata elements with a matching qualified or display name.
            There are no wildcards supported on this request.

           Parameters
           ----------
           name : str
               The name of the engine action to retrieve.
           server : str, optional
               The name of the server to retrieve the engine action from. If not provided, the default server specified
               in the instance will be used.
           start_from : int, optional
               The index to start retrieving engine actions from. If not provided, the default value will be used.
           page_size : int, optional
               The maximum number of engine actions to retrieve in a single request. If not provided, the default global
                maximum paging size will be used.

           Returns
           -------
           list of dict | str
               A list of dictionaries representing the retrieved engine actions,
               or "no actions" if no engine actions were found with the given name.
           Raises:
           ------
           InvalidParameterException
           PropertyServerException
           UserNotAuthorizedException
           """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_gov_action_processes_by_name(name, server, start_from, page_size)
        )
        return response

    async def _async_find_gov_action_processes(self, search_string: str, server: str = None, starts_with: bool = False,
                                               ends_with: bool = False, ignore_case: bool = False, start_from: int = 0,
                                               page_size: int = max_paging_size) -> list | str:
        """ Retrieve the list of governance action process metadata elements that contain the search string. Async ver.

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
            A list of dictionaries representing the governance action processes found based on the search query.
            If no actions are found, returns the string "no actions".

        Raises:
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException
        """
        server = self.server_name if server is None else server
        validate_search_string(search_string)
        if search_string == "*":
            search_string = None
        starts_with_s = str(starts_with).lower()
        ends_with_s = str(ends_with).lower()
        ignore_case_s = str(ignore_case).lower()

        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/automated-curation/governance-action-process/"
               f"by-search-string?startFrom={start_from}&pageSize={page_size}&startsWith={starts_with_s}&"
               f"endsWith={ends_with_s}&ignoreCase={ignore_case_s}"
               )
        body = {
            "class": "SearchStringRequestBody",
            "name": search_string
        }
        response = await self._async_make_request("GET", url, body)
        return response.json().get("elements", "no actions")

    def find_gov_action_processes(self, search_string: str = "*", server: str = None, starts_with: bool = False,
                                  ends_with: bool = False, ignore_case: bool = False, start_from: int = 0,
                                  page_size: int = max_paging_size) -> list | str:
        """ Retrieve the list of governance action process metadata elements that contain the search string.

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
            A list of dictionaries representing the governance action processes found based on the search query.
            If no actions are found, returns the string "no actions".

        Raises:
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_gov_action_processes(search_string, server, starts_with, ends_with, ignore_case,
                                                  start_from, page_size)
        )
        return response

    async def _async_initiate_gov_action_process(self, action_type_qualified_name: str, request_source_guids: [str],
                                                 action_targets: list, start_time: datetime, request_parameters: dict,
                                                 orig_service_name: str, orig_engine_name: str,
                                                 server: str = None) -> str:
        """ Using the named governance action process as a template, initiate a chain of engine actions. Async version.

        Parameters
        ----------
        action_type_qualified_name: str
            - unique name for the governance process
        request_source_guids: [str]
            - request source elements for the resulting governance action service
        action_targets: [str]
            -list of action target names to GUIDs for the resulting governance action service
        start_time: datetime
            - time to start the process
        request_parameters: [str]
            - parameters passed into the process
        orig_service_name: str
            - unique name of the requesting governance service (if initiated by a governance engine)
        orig_engine_name: str
            - optional unique name of the governance engine (if initiated by a governance engine).

        Returns
        -------
        Unique id (guid) of the newly started governance engine process

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """
        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/automated-curation/governance-action-processes/"
               f"initiate")
        body = {
            "class": "GovernanceActionProcessRequestBody",
            "processQualifiedName": action_type_qualified_name,
            "requestSourceGUIDs": request_source_guids,
            "actionTargets": action_targets,
            "startTime": int(start_time.timestamp() * 1000),
            "requestParameters": request_parameters,
            "originatorServiceName": orig_service_name,
            "originatorEngineName": orig_engine_name
        }
        new_body = body_slimmer(body)
        response = await self._async_make_request("POST", url, new_body)
        return response.json().get("guid", "Action not initiated")

    def initiate_governance_action_process(self, action_type_qualified_name: str, request_source_guids: [str],
                                           action_targets: [str], start_time: datetime, request_parameters: dict,
                                           orig_service_name: str, orig_engine_name: str, server: str = None) -> str:
        """ Using the named governance action process as a template, initiate a chain of engine actions.

        Parameters
        ----------
        action_type_qualified_name: str
            - unique name for the governance process
        request_source_guids: [str]
            - request source elements for the resulting governance action service
        action_targets: [str]
            -list of action target names to GUIDs for the resulting governance action service
        start_time: datetime
            - time to start the process
        request_parameters: [str]
            - parameters passed into the process
        orig_service_name: str
            - unique name of the requesting governance service (if initiated by a governance engine)
        orig_engine_name: str
            - optional unique name of the governance engine (if initiated by a governance engine).
        server: str, optional
            - if not specified, the server from the class instance will be used

        Returns
        -------
        Unique id (guid) of the newly started governance engine process

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_initiate_gov_action_process(action_type_qualified_name, request_source_guids,
                                                    action_targets, start_time, request_parameters,
                                                    orig_service_name, orig_engine_name, server)
        )
        return response

    async def _async_get_gov_action_type_by_guid(self, gov_action_type_guid: str, server: str = None) -> dict | str:
        """ Retrieve the governance action type metadata element with the supplied unique identifier. Async version.

        Parameters:
        ----------
            gov_action_type_guid: str
              The GUID (Globally Unique Identifier) of the governance action type to retrieve.
            server: str, optional
                The name of the server. If None, will use the default server specified in the instance will be used.
        Returns:
        -------
            dict: The JSON representation of the governance action type element.

        Raises:
        ------
            InvalidParameterException: If the API response indicates an error (non-200 status code),
                                       this exception is raised with details from the response content.
            PropertyServerException: If the API response indicates a server side error.
            UserNotAuthorizedException:
        """
        server = self.server_name if server is None else server
        validate_guid(gov_action_type_guid)

        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/automated-curation/"
               f"governance-action-types/{gov_action_type_guid}")

        response = await self._async_make_request("GET", url)
        return response.json().get("element", "no actions")

    def get_gov_action_type_by_guid(self, gov_action_type_guid: str, server: str = None) -> dict | str:
        """ Retrieve the governance action type metadata element with the supplied unique identifier.

        Parameters:
        ----------
            gov_action_type_guid: str
              The GUID (Globally Unique Identifier) of the governance action type to retrieve.
            server: str, optional
                The name of the server. If None, will use the default server specified in the instance will be used.
        Returns:
        -------
            dict: The JSON representation of the governance action type element.

        Raises:
        ------
            InvalidParameterException: If the API response indicates an error (non-200 status code),
                                       this exception is raised with details from the response content.
            PropertyServerException: If the API response indicates a server side error.
            UserNotAuthorizedException:
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_gov_action_type_by_guid(gov_action_type_guid, server)
        )
        return response

    async def _async_get_gov_action_types_by_name(self, action_type_name, server: str = None,
                                                  start_from: int = 0, page_size: int = max_paging_size) -> list | str:
        """ Retrieve the list of governance action type metadata elements with a matching qualified or display name.
            There are no wildcards supported on this request. Async version.

                Parameters:
                ----------
                    action_type_name: str
                      The name of the governance action type to retrieve.
                    server: str, optional
                        The name of the server. If None, will use the default server specified in the instance
                        will be used.
                Returns:
                -------
                    dict: The JSON representation of the governance action type element.

                Raises:
                ------
                    InvalidParameterException: If the API response indicates an error (non-200 status code),
                                               this exception is raised with details from the response content.
                    PropertyServerException: If the API response indicates a server side error.
                    UserNotAuthorizedException:
        """
        server = self.server_name if server is None else server
        validate_name(action_type_name)

        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/automated-curation/"
               f"governance-action-types/by-name?startFrom={start_from}&pageSize={page_size}")

        body = {
            "class": "NameRequestBody",
            "name": action_type_name
        }

        response = await self._async_make_request("POST", url, body)
        return response.json().get("elements", "no actions")

    def get_gov_action_types_by_name(self, action_type_name, server: str = None,
                                     start_from: int = 0, page_size: int = max_paging_size) -> list | str:
        """ Retrieve the list of governance action type metadata elements with a matching qualified or display name.
            There are no wildcards supported on this request. Async version.

            Parameters:
            ----------
                action_type_name: str
                  The name of the governance action type to retrieve.
                server: str, optional
                    The name of the server. If None, will use the default server specified in the instance will be used.
            Returns:
            -------
                dict: The JSON representation of the governance action type element.

            Raises:
            ------
                InvalidParameterException: If the API response indicates an error (non-200 status code),
                                           this exception is raised with details from the response content.
                PropertyServerException: If the API response indicates a server side error.
                UserNotAuthorizedException:
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_gov_action_types_by_name(action_type_name, server,
                                                     start_from, page_size)
        )
        return response

    async def _async_find_gov_action_types(self, search_string: str = "*", server: str = None,
                                           starts_with: bool = False,
                                           ends_with: bool = False, ignore_case: bool = False, start_from: int = 0,
                                           page_size: int = max_paging_size) -> list | str:
        """ Retrieve the list of governance action type metadata elements that contain the search string.
            Async Version.

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
               A list of dictionaries representing the governance action types found based on the search query.
               If no actions are found, returns the string "no action types".

           Raises
           ------
           InvalidParameterException
           PropertyServerException
           UserNotAuthorizedException

        """

        server = self.server_name if server is None else server
        validate_search_string(search_string)
        if search_string == "*":
            search_string = None
        starts_with_s = str(starts_with).lower()
        ends_with_s = str(ends_with).lower()
        ignore_case_s = str(ignore_case).lower()

        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/automated-curation/governance-action-types/"
               f"by-search-string?startFrom={start_from}&pageSize={page_size}&startsWith={starts_with_s}&"
               f"endsWith={ends_with_s}&ignoreCase={ignore_case_s}"
               )
        body = {
            "class": "SearchStringRequestBody",
            "name": search_string
        }
        response = await self._async_make_request("GET", url, body)
        return response.json().get("elements", "no action types")

    def find_gov_action_types(self, search_string: str = "*", server: str = None, starts_with: bool = False,
                              ends_with: bool = False, ignore_case: bool = False, start_from: int = 0,
                              page_size: int = max_paging_size) -> list | str:
        """ Retrieve the list of governance action type metadata elements that contain the search string.

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
               A list of dictionaries representing the governance action types found based on the search query.
               If no actions are found, returns the string "no action types".

           Raises
           ------
           InvalidParameterException
           PropertyServerException
           UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_gov_action_types(search_string, server, starts_with, ends_with,
                                              ignore_case, start_from, page_size)
        )
        return response

    async def _async_initiate_gov_action_type(self, action_type_qualified_name: str, request_source_guids: [str],
                                              action_targets: list, start_time: datetime = None,
                                              request_parameters: dict = None,
                                              orig_service_name: str = None, orig_engine_name: str = None,
                                              server: str = None) -> str:
        """ Using the named governance action type as a template, initiate an engine action. Async version.

        Parameters
        ----------
        action_type_qualified_name: str
            - unique name for the governance process
        request_source_guids: [str]
            - request source elements for the resulting governance action service
        action_targets: [str]
            -list of action target names to GUIDs for the resulting governance action service
        start_time: datetime
            - time to start the process
        request_parameters: [str]
            - parameters passed into the process
        orig_service_name: str
            - unique name of the requesting governance service (if initiated by a governance engine)
        orig_engine_name: str
            - optional unique name of the governance engine (if initiated by a governance engine).
        server : str, optional
            - The name of the server. If None, will use the default server specified in the instance will be used.

        Returns
        -------
        Unique id (guid) of the newly started governance engine process

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """
        server = self.server_name if server is None else server
        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/automated-curation/governance-action-types/"
               f"initiate")
        body = {
            "class": "InitiateGovernanceActionTypeRequestBody",
            "governanceActionTypeQualifiedName": action_type_qualified_name,
            "requestSourceGUIDs": request_source_guids,
            "actionTargets": action_targets,
            "startDate": int(start_time.timestamp() * 1000),
            "requestParameters": request_parameters,
            "originatorServiceName": orig_service_name,
            "originatorEngineName": orig_engine_name
        }
        new_body = body_slimmer(body)
        response = await self._async_make_request("POST", url, new_body)
        return response.json().get("guid", "Action not initiated")

    def initiate_gov_action_type(self, action_type_qualified_name: str, request_source_guids: [str],
                                 action_targets: list, start_time: datetime, request_parameters: dict,
                                 orig_service_name: str, orig_engine_name: str, server: str = None) -> str:
        """ Using the named governance action type as a template, initiate an engine action.

        Parameters
        ----------
        action_type_qualified_name: str
            - unique name for the governance process
        request_source_guids: [str]
            - request source elements for the resulting governance action service
        action_targets: [str]
            -list of action target names to GUIDs for the resulting governance action service
        start_time: datetime
            - time to start the process
        request_parameters: [str]
            - parameters passed into the process
        orig_service_name: str
            - unique name of the requesting governance service (if initiated by a governance engine)
        orig_engine_name: str
            - optional unique name of the governance engine (if initiated by a governance engine).
        server : str, optional
            - The name of the server. If None, will use the default server specified in the instance will be used.

        Returns
        -------
        Unique id (guid) of the newly started governance engine process

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_initiate_gov_action_type(action_type_qualified_name, request_source_guids,
                                                 action_targets, start_time, request_parameters,
                                                 orig_service_name, orig_engine_name, server)
        )
        return response

    async def _async_initiate_postgres_server_survey(self, postgres_server_guid: str, server: str = None) -> str:
        server = self.server_name if server is None else server
        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/automated-curation/governance-action-types/"
               f"initiate")

        body = {
            "class": "InitiateGovernanceActionTypeRequestBody",
            "governanceActionTypeQualifiedName": "Egeria:GovernanceActionType:2adeb8f1-0f59-4970-b6f2-6cc25d4d2402survey-postgres-server",
            "actionTargets": [{
                "class": "NewActionTarget",
                "actionTargetName": "serverToSurvey",
                "actionTargetGUID": postgres_server_guid
            }]
        }
        response = await self._async_make_request("POST", url, body)
        return response.json().get("guid", "Action not initiated")
        # Create/Retrieve the Postgres Server Element

        # Run the survey using the information and return the engine action to monitor

    def initiate_postgres_server_survey(self, postgres_server_guid: str, server: str = None) -> str:
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_initiate_postgres_server_survey(postgres_server_guid, server)
        )
        return response

    async def _async_initiate_file_folder_survey(self, file_folder_guid: str,
                                                 server: str = None) -> str:
        server = self.server_name if server is None else server
        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/automated-curation/governance-action-types/"
               f"initiate")

        body = {
            "class": "InitiateGovernanceActionTypeRequestBody",
            "governanceActionTypeQualifiedName":
                "Egeria:GovernanceActionType:2adeb8f1-0f59-4970-b6f2-6cc25d4d2402survey-folder",
            "actionTargets": [{
                "class": "NewActionTarget",
                "actionTargetName": "folderToSurvey",
                "actionTargetGUID": file_folder_guid
            }]
        }
        response = await self._async_make_request("POST", url, body)
        return response.json().get("guid", "Action not initiated")

    def initiate_file_folder_survey(self, file_folder_guid: str, server: str = None) -> str:
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_initiate_file_folder_survey(file_folder_guid, server)
        )
        return response

    async def _async_initiate_kafka_server_survey(self, kafka_server_guid: str, server: str = None) -> str:
        server = self.server_name if server is None else server
        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/automated-curation/governance-action-types/"
               f"initiate")

        body = {
            "class": "InitiateGovernanceActionTypeRequestBody",
            "governanceActionTypeQualifiedName":
                "Egeria:GovernanceActionType:2adeb8f1-0f59-4970-b6f2-6cc25d4d2402survey-kafka-server",
            "actionTargets": [{
                "class": "NewActionTarget",
                "actionTargetName": "serverToSurvey",
                "actionTargetGUID": kafka_server_guid
            }]
        }
        response = await self._async_make_request("POST", url, body)
        return response.json().get("guid", "Action not initiated")

    def initiate_kafka_server_survey(self, kafka_server_guid: str, server: str = None) -> str:
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_initiate_file_folder_survey(kafka_server_guid, server)
        )
        return response

    async def run_gov_action_postgres_server_survey(self, postgres_server: str, host_name: str, port: str, ):
        pass
        # New combo process to do
        # run a process the creates the postgres server catalog entry, runs the server survey
        # creates a survey report
        # adds a to-do list element when done

    async def _async_initiate_engine_action(self, qualified_name: str, domain_identifier: int, display_name: str,
                                            description: str, request_source_guids: str, action_targets: str,
                                            received_guards: [str], start_time: datetime, gov_engine_name: str,
                                            request_type: str, request_parameters: dict, process_name: str,
                                            request_src_name: str = None, originator_svc_name: str = None,
                                            originator_eng_name: str = None, server: str = None) -> str:
        """ Create an engine action in the metadata store that will trigger the governance service associated with
            the supplied request type. The engine action remains to act as a record of the actions taken for auditing.
            Async version.

            Parameters
            ----------
                qualified_name (str): The qualified name of the governance action.
                domain_identifier (int): The domain identifier for the governance action.
                display_name (str): The display name of the governance action.
                description (str): The description of the governance action.
                request_source_guids (str): GUIDs of the sources initiating the request.
                action_targets (str): Targets of the governance action.
                received_guards (List[str]): List of guards received for the action.
                start_time (datetime): The start time for the governance action.
                gov_engine_name (str): The name of the governance engine associated with the action.
                request_type (str): The type of the governance action request.
                request_parameters (dict): Additional parameters for the governance action.
                process_name (str): The name of the associated governance action process.
                request_src_name (str, optional): The name of the request source. Defaults to None.
                originator_svc_name (str, optional): The name of the originator service. Defaults to None.
                originator_eng_name (str, optional): The name of the originator engine. Defaults to None.

            Returns
            -------
                str: The GUID (Globally Unique Identifier) of the initiated governance action.

            Raises
            ------
                InvalidParameterException: If the API response indicates an error (non-200 status code),
                this exception is raised with details from the response content.

            Note
            ----
                The `start_time` parameter should be a `datetime` object representing the start time of the governance action.


        """
        server = self.server_name if server is None else server
        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/automated-curation/governance-engines/"
               f"engine-actions/initiate")
        body = {
            "class": "GovernanceActionRequestBody",
            "qualifiedName": qualified_name + str(int(start_time.timestamp())),
            "domainIdentifier": domain_identifier,
            "displayName": display_name,
            "description": description,
            "requestSourceGUIDs": request_source_guids,
            "actionTargets": action_targets,
            "receivedGuards": received_guards,
            "startTime": int(start_time.timestamp() * 1000),
            "requestType": request_type,
            "requestParameters": request_parameters,
            "processName": process_name,
            "requestSourceName": request_src_name,
            "originatorServiceName": originator_svc_name,
            "originatorEngineName": originator_eng_name
        }
        new_body = body_slimmer(body)
        response = await self._async_make_request("POST", url, new_body)
        return response.json().get("guid", "Action not initiated")

    def initiate_engine_action(self, qualified_name: str, domain_identifier: int, display_name: str,
                               description: str, request_source_guids: str, action_targets: str,
                               received_guards: [str], start_time: datetime, gov_engine_name: str,
                               request_type: str, request_parameters: dict, process_name: str,
                               request_src_name: str = None, originator_svc_name: str = None,
                               originator_eng_name: str = None, server: str = None) -> str:
        """ Create an engine action in the metadata store that will trigger the governance service associated with
            the supplied request type. The engine action remains to act as a record of the actions taken for auditing.

            Parameters
            ----------
                qualified_name (str): The qualified name of the governance action.
                domain_identifier (int): The domain identifier for the governance action.
                display_name (str): The display name of the governance action.
                description (str): The description of the governance action.
                request_source_guids (str): GUIDs of the sources initiating the request.
                action_targets (str): Targets of the governance action.
                received_guards (List[str]): List of guards received for the action.
                start_time (datetime): The start time for the governance action.
                gov_engine_name (str): The name of the governance engine associated with the action.
                request_type (str): The type of the governance action request.
                request_parameters (dict): Additional parameters for the governance action.
                process_name (str): The name of the associated governance action process.
                request_src_name (str, optional): The name of the request source. Defaults to None.
                originator_svc_name (str, optional): The name of the originator service. Defaults to None.
                originator_eng_name (str, optional): The name of the originator engine. Defaults to None.

            Returns
            -------
                str: The GUID (Globally Unique Identifier) of the initiated governance action.

            Raises
            ------
                InvalidParameterException: If the API response indicates an error (non-200 status code),
                this exception is raised with details from the response content.

            Note
            ----
                The `start_time` parameter should be a `datetime` object representing the start time of the governance action.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_initiate_engine_action(qualified_name, domain_identifier, display_name,
                                               description, request_source_guids, action_targets,
                                               received_guards, start_time, gov_engine_name,
                                               request_type, request_parameters, process_name,
                                               request_src_name, originator_svc_name,
                                               originator_eng_name, server)
        )
        return response

    async def _async_get_catalog_targets(self, integ_connector_guid: str, server: str = None,
                                         start_from: int = 0, page_size: int = max_paging_size) -> list | str:
        """ Retrieve the details of the metadata elements identified as catalog targets with an integration connector.
            Async version.

            Parameters:
            ----------
                integ_connector_guid: str
                  The GUID (Globally Unique Identifier) of the integration connector used to retrieve catalog targets.
                server: str, optional
                    The name of the server. If None, will use the default server specified in the instance will be used.
            Returns:
            -------
                [dict]: The list of catalog targets JSON objects.

            Raises:
            ------
                InvalidParameterException: If the API response indicates an error (non-200 status code),
                                           this exception is raised with details from the response content.
                PropertyServerException: If the API response indicates a server side error.
                UserNotAuthorizedException:
            """
        server = self.server_name if server is None else server
        validate_guid(integ_connector_guid)

        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/automated-curation/integration-connectors/"
               f"{integ_connector_guid}/catalog-targets?startFrom={start_from}&pageSize={page_size}")

        response = await self._async_make_request("GET", url)
        return response.json().get("elements", "no actions")

    def get_catalog_targets(self, integ_connector_guid: str, server: str = None,
                            start_from: int = 0, page_size: int = max_paging_size) -> list | str:
        """ Retrieve the details of the metadata elements identified as catalog targets with an integration connector.

        Parameters:
        ----------
            integ_connector_guid: str
              The GUID (Globally Unique Identifier) of the integration connector used to retrieve catalog targets.
            server: str, optional
                The name of the server. If None, will use the default server specified in the instance will be used.
        Returns:
        -------
            [dict]: The list of catalog targets JSON objects.

        Raises:
        ------
            InvalidParameterException: If the API response indicates an error (non-200 status code),
                                       this exception is raised with details from the response content.
            PropertyServerException: If the API response indicates a server side error.
            UserNotAuthorizedException:
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_catalog_targets(integ_connector_guid, server,
                                            start_from, page_size)
        )
        return response

    async def _async_get_catalog_target(self, integ_connector_guid: str, metadata_element_guid: str,
                                        server: str = None) -> dict | str:
        """ Retrieve a specific catalog target associated with an integration connector.
            Async version.

            Parameters:
            ----------
                integ_connector_guid: str
                    The GUID (Globally Unique Identifier) of the integration connector used to retrieve catalog targets.
                metadata_element_guid: str
                    The specific metadata element target we want to retrieve.
                server: str, optional
                    The name of the server. If None, will use the default server specified in the instance will be used.
            Returns:
            -------
                dict: JSON structure of the catalog target.

            Raises:
            ------
                InvalidParameterException: If the API response indicates an error (non-200 status code),
                                           this exception is raised with details from the response content.
                PropertyServerException: If the API response indicates a server side error.
                UserNotAuthorizedException:
            """
        server = self.server_name if server is None else server
        validate_guid(integ_connector_guid)
        validate_guid(metadata_element_guid)

        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/automated-curation/integration-connectors/"
               f"{integ_connector_guid}/catalog-targets/{metadata_element_guid}")

        response = await self._async_make_request("GET", url)
        return response.json().get("element", "no actions")

    def get_catalog_target(self, integ_connector_guid: str, metadata_element_guid: str,
                           server: str = None) -> dict | str:
        """ Retrieve a specific catalog target associated with an integration connector.

            Parameters:
            ----------
                integ_connector_guid: str
                    The GUID (Globally Unique Identifier) of the integration connector used to retrieve catalog targets.
                metadata_element_guid: str
                    The specific metadata element target we want to retrieve.
                server: str, optional
                    The name of the server. If None, will use the default server specified in the instance will be used.
            Returns:
            -------
                dict: JSON structure of the catalog target.

            Raises:
            ------
                InvalidParameterException: If the API response indicates an error (non-200 status code),
                                           this exception is raised with details from the response content.
                PropertyServerException: If the API response indicates a server side error.
                UserNotAuthorizedException:
            """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_catalog_target(integ_connector_guid, metadata_element_guid,
                                           server)
        )
        return response

    async def _async_add_catalog_target(self, integ_connector_guid: str, metadata_element_guid: str,
                                        catalog_target_name: str, metadata_src_qual_name: str, config_properties: dict
                                        , server: str = None) -> None:
        """ Add a catalog target to an integration connector.
            Async version.

            Parameters:
            ----------
            integ_connector_guid: str
                The GUID (Globally Unique Identifier) of the integration connector used to retrieve catalog targets.
            metadata_element_guid: str
                The specific metadata element target we want to retrieve.
            catalog_target_name : dict
                Name of the catalog target to add.
            metadata_src_qual_name: str
                The qualified name of the metadata source for the catalog target
            config_properties: dict
                Configuration properties for the catalog target
            server: str, optional
                The name of the server. If None, will use the default server specified in the instance will be used.
            Returns:
            -------
                None

            Raises:
            ------
            InvalidParameterException: If the API response indicates an error (non-200 status code),
                                       this exception is raised with details from the response content.
            PropertyServerException: If the API response indicates a server side error.
            UserNotAuthorizedException:
            """
        server = self.server_name if server is None else server
        validate_guid(integ_connector_guid)
        validate_guid(metadata_element_guid)

        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/automated-curation/integration-connectors/"
               f"{integ_connector_guid}/catalog-targets/{metadata_element_guid}")
        body = {
            "catalogTargetName": catalog_target_name,
            "metadataSourceQualifiedName": metadata_src_qual_name,
            "configProperties": config_properties
        }
        await self._async_make_request("POST", url, body)
        return

    def add_catalog_target(self, integ_connector_guid: str, metadata_element_guid: str, catalog_target_name: str,
                           metadata_src_qual_name: str, config_properties: dict, server: str = None) -> None:
        """ Add a catalog target to an integration connector.

            Parameters:
            ----------
            integ_connector_guid: str
                The GUID (Globally Unique Identifier) of the integration connector used to retrieve catalog targets.
            metadata_element_guid: str
                The specific metadata element target we want to retrieve.
            catalog_target_name : dict
                Name of the catalog target to add.
            metadata_src_qual_name: str
                The qualified name of the metadata source for the catalog target
            config_properties: dict
                Configuration properties for the catalog target
            server: str, optional
                The name of the server. If None, will use the default server specified in the instance will be used.
            Returns:
            -------
                None

            Raises:
            ------
            InvalidParameterException: If the API response indicates an error (non-200 status code),
                                       this exception is raised with details from the response content.
            PropertyServerException: If the API response indicates a server side error.
            UserNotAuthorizedException:
            """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_add_catalog_target(integ_connector_guid, metadata_element_guid,
                                           metadata_src_qual_name, metadata_src_qual_name,
                                           config_properties, server)
        )
        return

    async def _async_remove_catalog_target(self, integ_connector_guid: str, metadata_element_guid: str,
                                           catalog_target_name: str, server: str = None) -> None:
        """ Remove a catalog target to an integration connector. Async version.

            Parameters:
            ----------
            integ_connector_guid: str
                The GUID (Globally Unique Identifier) of the integration connector used to retrieve catalog targets.
            metadata_element_guid: str
                The specific metadata element target we want to retrieve.
            server: str, optional
                The name of the server. If None, will use the default server specified in the instance will be used.
            Returns:
            -------
                None

            Raises:
            ------
            InvalidParameterException: If the API response indicates an error (non-200 status code),
                                       this exception is raised with details from the response content.
            PropertyServerException: If the API response indicates a server side error.
            UserNotAuthorizedException:
            """
        server = self.server_name if server is None else server
        validate_guid(integ_connector_guid)
        validate_guid(metadata_element_guid)

        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/automated-curation/integration-connectors/"
               f"{integ_connector_guid}/catalog-targets/{metadata_element_guid}/remove")

        await self._async_make_request("POST", url)
        return

    def remove_catalog_target(self, integ_connector_guid: str, metadata_element_guid: str,
                              catalog_target_name: str, server: str = None) -> None:
        """ Remove a catalog target to an integration connector.

            Parameters:
            ----------
            integ_connector_guid: str
                The GUID (Globally Unique Identifier) of the integration connector used to retrieve catalog targets.
            metadata_element_guid: str
                The specific metadata element target we want to retrieve.
            server: str, optional
                The name of the server. If None, will use the default server specified in the instance will be used.
            Returns:
            -------
                None

            Raises:
            ------
            InvalidParameterException: If the API response indicates an error (non-200 status code),
                                       this exception is raised with details from the response content.
            PropertyServerException: If the API response indicates a server side error.
            UserNotAuthorizedException:
            """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_remove_catalog_target(integ_connector_guid, metadata_element_guid,
                                              server)
        )
        return

    #
    #   Get information about technologies
    #

    async def _async_get_tech_types_for_open_metadata_type(self, type_name: str, tech_name: str, server: str = None,
                                                           start_from: int = 0,
                                                           page_size: int = max_paging_size) -> list | str:
        """ Retrieve the list of deployed implementation type metadata elements linked to a particular
            open metadata type.. Async version.

            Parameters:
            ----------
            type_name: str
                The technology type we are looking for.
            tech_name: str
                The technology name we are looking for.
            server: str, optional
                The name of the server. If None, will use the default server specified in the instance will be used.
            Returns:
            -------
                [dict] | str: List of elements describing the technology - or "no tech found" if not found.

            Raises:
            ------
            InvalidParameterException: If the API response indicates an error (non-200 status code),
                                       this exception is raised with details from the response content.
            PropertyServerException: If the API response indicates a server side error.
            UserNotAuthorizedException:

            Notes
            -----
            More information can be found at: https://egeria-project.org/types
        """
        server = self.server_name if server is None else server
        # validate_name(type_name)
        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/automated-curation/open-metadata-types/"
               f"{type_name}/technology-types?startFrom={start_from}&pageSize={page_size}")
        body = {
            "string": tech_name
        }

        response = await self._async_make_request("GET", url, body)
        return response.json().get("elements", "no tech found")

    def get_tech_types_for_open_metadata_type(self, type_name: str, tech_name: str, server: str = None,
                                              start_from: int = 0, page_size: int = max_paging_size) -> list | str:
        """ Retrieve the list of deployed implementation type metadata elements linked to a particular
            open metadata type.

            Parameters:
            ----------
            type_name: str
                The technology type we are looking for.
            tech_name: str
                The technology name we are looking for.
            server: str, optional
                The name of the server. If None, will use the default server specified in the instance will be used.
            Returns:
            -------
                [dict] | str: List of elements describing the technology - or "no tech found" if not found.

            Raises:
            ------
            InvalidParameterException: If the API response indicates an error (non-200 status code),
                                       this exception is raised with details from the response content.
            PropertyServerException: If the API response indicates a server side error.
            UserNotAuthorizedException:

            Notes
            -----
            More information can be found at: https://egeria-project.org/types
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_tech_types_for_open_metadata_type(type_name, tech_name, server,
                                                              start_from, page_size)
        )
        return response

    async def _async_get_technology_type_detail(self, type_name: str, server: str = None) -> list | str:
        """ Retrieve the details of the named technology type. This name should be the name of the technology type
            and contain no wild cards. Async version.
        Parameters
        ----------
        type_name : str
            The name of the technology type to retrieve detailed information for.
        server : str, optional
            The name of the server to fetch the technology type from. If not provided, the default server name will be used.

        Returns
        -------
        list[dict] | str
            A list of dictionaries containing the detailed information for the specified technology type.
            If the technology type is not found, returns the string "no type found".
        Raises
        ------
        InvalidParameterException: If the API response indicates an error (non-200 status code),
                                   this exception is raised with details from the response content.
        PropertyServerException: If the API response indicates a server side error.
        UserNotAuthorizedException:

        Notes
        -----
        More information can be found at: https://egeria-project.org/concepts/deployed-implementation-type
        """
        server = self.server_name if server is None else server
        validate_name(type_name)
        url = f"{self.platform_url}/servers/{server}/api/open-metadata/automated-curation/technology-types/by-name"

        body = {"string": type_name}

        response = await self._async_make_request("POST", url, body)
        return response.json().get("element", "no type found")

    def get_technology_type_detail(self, type_name: str, server: str = None) -> list | str:
        """ Retrieve the details of the named technology type. This name should be the name of the technology type
            and contain no wild cards.
            Parameters
            ----------
            type_name : str
                The name of the technology type to retrieve detailed information for.
            server : str, optional
                The name of the server to fetch the technology type from. If not provided, the default server name will be used.

            Returns
            -------
            list[dict] | str
                A list of dictionaries containing the detailed information for the specified technology type.
                If the technology type is not found, returns the string "no type found".
            Raises
            ------
            InvalidParameterException: If the API response indicates an error (non-200 status code),
                                       this exception is raised with details from the response content.
            PropertyServerException: If the API response indicates a server side error.
            UserNotAuthorizedException:

            Notes
            -----
            More information can be found at: https://egeria-project.org/concepts/deployed-implementation-type
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_technology_type_detail(type_name, server)
        )
        return response

    async def _async_find_technology_types(self, search_string: str = "*", server: str = None, start_from: int = 0,
                                           page_size: int = max_paging_size, starts_with: bool = False,
                                           ends_with: bool = False, ignore_case: bool = True) -> list | str:
        """ Retrieve the list of technology types that contain the search string. Async version.

            Parameters:
            ----------
            type_name: str
                The technology type we are looking for.
            server: str, optional
                The name of the server. If None, will use the default server specified in the instance will be used.

            starts_with : bool, optional
               Whether to search engine actions that start with the given search string. Default is False.

            ends_with : bool, optional
               Whether to search engine actions that end with the given search string. Default is False.

            ignore_case : bool, optional
               Whether to ignore case while searching engine actions. Default is True.

            start_from : int, optional
               The index from which to start fetching the engine actions. Default is 0.

            page_size : int, optional
               The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.
            Returns:
            -------
                [dict] | str: List of elements describing the technology - or "no tech found" if not found.

            Raises:
            ------
            InvalidParameterException: If the API response indicates an error (non-200 status code),
                                       this exception is raised with details from the response content.
            PropertyServerException: If the API response indicates a server side error.
            UserNotAuthorizedException:

            Notes
            -----
            For more information see: https://egeria-project.org/concepts/deployed-implementation-type
        """
        server = self.server_name if server is None else server

        starts_with_s = str(starts_with).lower()
        ends_with_s = str(ends_with).lower()
        ignore_case_s = str(ignore_case).lower()
        validate_name(search_string)
        if search_string == "*":
            search_string = ""

        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/automated-curation/technology-types/"
               f"by-search-string?startFrom={start_from}&pageSize={page_size}&startsWith={starts_with_s}&"
               f"endsWith={ends_with_s}&ignoreCase={ignore_case_s}")
        body = {"string": search_string}

        response = await self._async_make_request("POST", url, body)
        return response.json().get("elements", "no tech found")

    def find_technology_types(self, type_name: str = "*", server: str = None, start_from: int = 0,
                              page_size: int = max_paging_size, starts_with: bool = False,
                              ends_with: bool = False, ignore_case: bool = True) -> list | str:
        """ Retrieve the list of technology types that contain the search string. Async version.

            Parameters:
            ----------
            type_name: str
                The technology type we are looking for.
            server: str, optional
                The name of the server. If None, will use the default server specified in the instance will be used.
            Returns:
            -------
                [dict] | str: List of elements describing the technology - or "no tech found" if not found.

            Raises:
            ------
            InvalidParameterException: If the API response indicates an error (non-200 status code),
                                       this exception is raised with details from the response content.
            PropertyServerException: If the API response indicates a server side error.
            UserNotAuthorizedException:

            Notes
            -----
            For more information see: https://egeria-project.org/concepts/deployed-implementation-type
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_technology_types(type_name, server, start_from,
                                              page_size, starts_with, ends_with, ignore_case)
        )
        return response

    async def _async_get_all_technology_types(self, server: str = None, start_from: int = 0,
                                              page_size: int = max_paging_size) -> list | str:
        return await self._async_find_technology_types("*", server, start_from, page_size)

    def get_all_technology_types(self, server: str = None, start_from: int = 0,
                                 page_size: int = max_paging_size) -> list | str:
        return self.find_technology_types("*", server, start_from, page_size)


if __name__ == "__main__":
    p = AutomatedCuration("meow", "https://127.0.0.1:9443", "garygeeke", verify_flag=False)
    response = p.get_active_engine_actions()
    out = response.json()
    print(out)
