"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Runtime manager is a view service that supports user interaction with the running platforms.

"""
import asyncio
from requests import Response

from pyegeria._exceptions import (
    InvalidParameterException,
)
from pyegeria import Client, AutomatedCuration, max_paging_size, body_slimmer



class RuntimeManager(Client):
    """
    Client to issue Runtime status requests.

    Attributes:

        server_name: str
                Name of the server to use.
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

    Methods:

    """

    def __init__(
            self,
            server_name: str,
            platform_url: str,
            user_id: str,
            user_pwd: str = None,
            verify_flag: bool = False,
        ):
        Client.__init__(self, server_name, platform_url, user_id,
                          user_pwd, verify_flag)
        self.cur_command_root = f"{platform_url}/servers/"
        self.platform_guid = "44bf319f-1e41-4da1-b771-2753b92b631a" # this is platform @ 9443 from the core content archive
        self.default_platform_name = "Default Local OMAG Server Platform" # this from the core content archive

    async def _async_get_platforms_by_name(self, filter: str = None, server:str = None, effective_time: str = None,
                                           start_from: int = 0, page_size: int = max_paging_size )-> str | list:
        """ Returns the list of platforms with a particular name. The name is specified in the filter.  Async version.
            Parameters
            ----------
           filter : str, opt
                Filter specifies the display name or qualified name of the platforms to return information for. If the
                value is None, we will default to the default_platform_name that comes from the core content pack.

            server : str, optional
               The name of the server to get governance engine summaries from. If not provided, the default server name
               will be used.

            start_from : int, optional
               The index from which to start fetching the engine actions. Default is 0.

            page_size : int, optional
               The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

            Returns
            -------
            Response
               A lit of json dict with the platform reports.

            Raises
            ------
            InvalidParameterException
            PropertyServerException
            UserNotAuthorizedException

        """
        if server is None:
           server = self.server_name

        if filter is None:
            filter = self.default_platform_name


        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/runtime-manager/platforms/by-name?"
               f"startFrom={start_from}&pageSize={page_size}")
        if effective_time is not None:
            body = {
                "filter" : filter,
                "effectiveTime" : effective_time
            }
        else:
            body = {
                "filter": filter
            }

        response = await self._async_make_request("POST", url, body)

        return response.json().get('elementList','No platforms found')


    def get_platforms_by_name(self, filter: str = None, server: str = None, effective_time: str = None,
                              start_from: int = 0, page_size: int = max_paging_size) -> str | list:
        """ Returns the list of platforms with a particular name. The name is specified in the filter.

            Parameters
            ----------
            filter : str, opt
                Filter specifies the display name or qualified name of the platforms to return information for. If the
                value is None, we will default to the default_platform_name that comes from the core content pack.

            server : str, optional
               The name of the server to get governance engine summaries from. If not provided, the default server name
               will be used.

            start_from : int, optional
               The index from which to start fetching the engine actions. Default is 0.


            page_size : int, optional
               The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

            Returns
            -------
            Response
               A lit of json dict with the platform reports.

            Raises
            ------
            InvalidParameterException
            PropertyServerException
            UserNotAuthorizedException
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_platforms_by_name(filter, server,
                                                                             effective_time,
                                                                            start_from, page_size))
        return response

    async def _async_get_platforms_by_type(self, filter: str = None, server:str = None, effective_time: str = None,
                                           start_from: int = 0, page_size: int = max_paging_size )-> str | list:
        """ Returns the list of platforms with a particular deployed implementation type.  The value is specified in
            the filter. If it is null, or no request body is supplied, all platforms are returned.  Async version.

            Parameters
            ----------
            filter : str, opt
                Filter specifies the kind of deployed implementation type of the platforms to return information for.
                If the value is None, we will default to the "OMAG Server Platform".

            server : str, optional
                   The name of the server to get governance engine summaries from. If not provided, the default server name
                   will be used.

            start_from : int, optional
                   The index from which to start fetching the engine actions. Default is 0.

            page_size : int, optional
               The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

            Returns
            -------
            Response
               A lit of json dict with the platform reports.

            Raises
            ------
            InvalidParameterException
            PropertyServerException
            UserNotAuthorizedException

        """
        if server is None:
           server = self.server_name

        if filter is None:
            filter = "OMAG Server Platform"

        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/runtime-manager/platforms/"
               f"by-deployed-implementation-type?startFrom={start_from}&pageSize={page_size}")

        if effective_time is not None:
            body = {
                "filter": filter,
                "effectiveTime": effective_time
            }
        else:
            body = {
                "filter": filter
            }

        response = await self._async_make_request("POST", url, body)
        return response.json().get('elementList','No platforms found')

    def get_platforms_by_type(self, filter: str = None, server:str = None, effective_time: str = None,
                              start_from: int = 0, page_size: int = max_paging_size ) -> str | list:
        """ Returns the list of platforms with a particular deployed implementation type.  The value is specified in
            the filter. If it is null, or no request body is supplied, all platforms are returned.

            Parameters
            ----------
            filter : str, opt
                Filter specifies the kind of deployed implementation type of the platforms to return information for.
                If the value is None, we will default to the "OMAG Server Platform".

            server : str, optional
               The name of the server to get governance engine summaries from. If not provided, the default server name
               will be used.

            start_from : int, optional
               The index from which to start fetching the engine actions. Default is 0.


            page_size : int, optional
               The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

            Returns
            -------
            Response
               A lit of json dict with the platform reports.

            Raises
            ------
            InvalidParameterException
            PropertyServerException
            UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_platforms_by_type(filter, server, effective_time,
                                                                             start_from, page_size))
        return response

    async def _async_get_platform_templates_by_type(self, filter: str = None, server:str = None, effective_time: str = None,
                                           start_from: int = 0, page_size: int = max_paging_size )-> str | list:
        """ Returns the list of platform templates for a particular deployed implementation type.  The value is
            specified in the filter. If it is null, or no request body is supplied, all platforms are returned.
            Async version.

            Parameters
            ----------
            filter : str, opt
                Filter specifies the kind of deployed implementation type of the platforms to return information for.
                If the value is None, we will default to the "OMAG Server Platform".

            server : str, optional
                   The name of the server to get governance engine summaries from. If not provided, the default server name
                   will be used.

            start_from : int, optional
                   The index from which to start fetching the engine actions. Default is 0.

            page_size : int, optional
               The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

            Returns
            -------
            Response
               A lit of json dict with the platform reports.

            Raises
            ------
            InvalidParameterException
            PropertyServerException
            UserNotAuthorizedException

        """
        if server is None:
           server = self.server_name

        if filter is None:
            filter = "OMAG Server Platform"

        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/runtime-manager/platforms/"
               f"by-deployed-implementation-type?startFrom={start_from}&pageSize={page_size}&getTemplates=true")

        if effective_time is not None:
            body = {
                "filter": filter,
                "effectiveTime": effective_time
            }
        else:
            body = {
                "filter": filter
            }

        response = await self._async_make_request("POST", url, body)
        return response.json().get('elementList','No platforms found')


    def get_platform_templates_by_type(self, filter: str = None, server:str = None, effective_time: str = None,
                              start_from: int = 0, page_size: int = max_paging_size ) -> str | list:
        """ Returns the list of platform templates with a particular deployed implementation type.  The value is
            specified in the filter. If it is null, or no request body is supplied, all platforms are returned.

            Parameters
            ----------
            filter : str, opt
                Filter specifies the kind of deployed implementation type of the platforms to return information for.
                If the value is None, we will default to the "OMAG Server Platform".

            server : str, optional
               The name of the server to get governance engine summaries from. If not provided, the default server name
               will be used.

            start_from : int, optional
               The index from which to start fetching the engine actions. Default is 0.


            page_size : int, optional
               The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

            Returns
            -------
            Response
               A lit of json dict with the platform reports.

            Raises
            ------
            InvalidParameterException
            PropertyServerException
            UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_platforms_by_type(filter, server, effective_time,
                                                                             start_from, page_size))
        return response

    async def _async_get_platform_report(self, platform_guid: str = None, server:str = None) -> str | list:
        """ Returns details about the running platform. Async version.

            Parameters
            ----------
            platform_guid : str
                The unique identifier for the platform.

            server : str, optional
               The name of the server to get governance engine summaries from. If not provided, the default server name
               will be used.

            Returns
            -------
            Response
               A json dict with the platform report.

            Raises
            ------
            InvalidParameterException
            PropertyServerException
            UserNotAuthorizedException

        """
        if server is None:
           server = self.server_name

        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/runtime-manager/platforms/{platform_guid}/report")

        response = await self._async_make_request("GET", url)

        return response.json().get('element','No platforms found')

    def get_platform_report(self, platform_guid: str = None, server: str = None) -> str | list:
        """ Returns details about the running platform.

            Parameters
            ----------
            platform_guid : str
                The unique identifier for the platform.

            server : str, optional
               The name of the server to get governance engine summaries from. If not provided, the default server name
               will be used.


            Returns
            -------
            Response
               A json dict with the platform report.

            Raises
            ------
            InvalidParameterException
            PropertyServerException
            UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_platform_report(platform_guid, server))
        return response

    async def _async_get_platform_by_guid(self, platform_guid: str = None, server:str = None,
                                           effective_time: str = None) -> str | list:
        """ Returns details about the platform's catalog entry (asset). Async version.

            Parameters
            ----------
            filter : str, opt
                Filter specifies the kind of deployed implementation type of the platforms to return information for.
                If the value is None, we will default to the "OMAG Server Platform".

            server : str, optional
               The name of the server to get governance engine summaries from. If not provided, the default server name
               will be used.

            start_from : int, optional
               The index from which to start fetching the engine actions. Default is 0.


            page_size : int, optional
               The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

            Returns
            -------
            Response
               A lit of json dict with the platform reports.

        """
        if server is None:
           server = self.server_name

        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/runtime-manager/platforms/{platform_guid}")

        if effective_time is not None:
            body = {
                "effectiveTime": effective_time
            }
            response = await self._async_make_request("POST", url, body)

        else:
            response = await self._async_make_request("POST", url)

        return response.json().get('elementList','No platforms found')

    def get_platform_by_guid(self, platform_guid: str = None, server: str = None,
                                effective_time: str = None) -> str | list:
        """ Returns details about the platform's catalog entry (asset).

            Parameters
            ----------
            filter : str, opt
                Filter specifies the kind of deployed implementation type of the platforms to return information for.
                If the value is None, we will default to the "OMAG Server Platform".

            server : str, optional
               The name of the server to get governance engine summaries from. If not provided, the default server name
               will be used.

            start_from : int, optional
               The index from which to start fetching the engine actions. Default is 0.


            page_size : int, optional
               The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

            Returns
            -------
            Response
               A lit of json dict with the platform reports.

            Raises
            ------
            InvalidParameterException
            PropertyServerException
            UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_platforms_by_guid(platform_guid, server,
                                                                             effective_time))
        return response

    async def _async_get_server_by_guid(self, server_guid: str, server:str = None,
                                           effective_time: str = None) -> str | dict:
        """ Returns details about the server's catalog entry (asset). Async version.

            Parameters
            ----------
            server_guid : str
                The unique identifier for the platform.

            server : str, optional
               The name of the server to get governance engine summaries from. If not provided, the default server name
               will be used.

            Returns
            -------
            Response
               A lit of json dict with the platform reports.

            Raises
            ------
            InvalidParameterException
            PropertyServerException
            UserNotAuthorizedException

        """
        if server is None:
           server = self.server_name

        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/runtime-manager/servers/{server_guid}")

        if effective_time is not None:
            body = {
                "effectiveTime": effective_time
            }
            response = await self._async_make_request("POST", url, body)

        else:
            response = await self._async_make_request("POST", url)

        return response.json().get('elementList','No server found')

    def get_server_by_guid(self, server_guid: str, server: str = None,
                                effective_time: str = None) -> str | dict:
        """ Returns details about the platform's catalog entry (asset).

            Parameters
            ----------
            server_guid : str
                The unique identifier for the platform.

            server : str, optional
               The name of the server to get governance engine summaries from. If not provided, the default server name
               will be used.

            Returns
            -------
            Response
               A lit of json dict with the platform reports.

            Raises
            ------
            InvalidParameterException
            PropertyServerException
            UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_server_by_guid(server_guid, server, effective_time))
        return response


    async def _async_get_servers_by_name(self, filter: str, server:str = None, effective_time: str = None,
                                        start_from: int = 0, page_size: int = max_paging_size ) -> str | list:
        """ Returns the list of servers with a particular name.  The name is specified in the filter. Async version.

            Parameters
            ----------
            filter : str, opt
                Filter specifies the kind of deployed implementation type of the platforms to return information for.
                If the value is None, we will default to the "OMAG Server Platform".

            server : str, optional
               The name of the server to get governance engine summaries from. If not provided, the default server name
               will be used.

            start_from : int, optional
               The index from which to start fetching the engine actions. Default is 0.


            page_size : int, optional
               The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

            Returns
            -------
            Response
               A lit of json dict with the platform reports.

            Raises
            ------
            InvalidParameterException
            PropertyServerException
            UserNotAuthorizedException

        """
        if server is None:
           server = self.server_name

        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/runtime-manager/servers/by-name?"
               f"startFrom={start_from}&pageSize={page_size}")

        if effective_time is None:
            body = {
                "filter": filter
            }
        else:
            body = {
                "filter": filter,
                "effective_time": effective_time
            }
        response = await self._async_make_request("POST", url, body)

        return response.json().get('elementList','No platforms found')

    def get_servers_by_name(self, filter: str, server: str = None) -> str | list:
        """ Returns the list of servers with a particular name.  The name is specified in the filter.

            Parameters
            ----------
            filter : str, opt
                Filter specifies the kind of deployed implementation type of the platforms to return information for.
                If the value is None, we will default to the "OMAG Server Platform".

            server : str, optional
               The name of the server to get governance engine summaries from. If not provided, the default server name
               will be used.

            start_from : int, optional
               The index from which to start fetching the engine actions. Default is 0.


            page_size : int, optional
               The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

            Returns
            -------
            Response
               A lit of json dict with the platform reports.

            Raises
            ------
            InvalidParameterException
            PropertyServerException
            UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_servers_by_name(filter, server))
        return response

    async def _async_get_servers_by_dep_impl_type(self, filter: str = "*", server:str = None, effective_time: str = None,
                                        start_from: int = 0, page_size: int = max_paging_size ) -> str | list:
        """ Returns the list of servers with a particular deployed implementation type. The value is specified
            in the filter. If it is null, or no request body is supplied, all servers are returned.
            Async version.

            Parameters
            ----------
            filter : str, opt
                Filter specifies the kind of deployed implementation type of the platforms to return information for.
                If the value is None, we will default to the "OMAG Server Platform".

            server : str, optional
               The name of the server to get governance engine summaries from. If not provided, the default server name
               will be used.

            start_from : int, optional
               The index from which to start fetching the engine actions. Default is 0.


            page_size : int, optional
               The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

            Returns
            -------
            Response
               A lit of json dict with the platform reports.

            Raises
            ------
            InvalidParameterException
            PropertyServerException
            UserNotAuthorizedException

        """
        if server is None:
           server = self.server_name

        if filter == '*':
            filter = None

        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/runtime-manager/servers/"
               f"by-deployed-implementation-type?startFrom={start_from}&pageSize={page_size}")

        body = body_slimmer({ "filter": filter, "effective_time": effective_time})

        response = await self._async_make_request("POST", url, body)

        return response.json().get('elementList','No platforms found')

    def get_servers_by_dep_impl_type(self, filter: str = "*", server:str = None, effective_time: str = None,
                                     start_from: int = 0, page_size: int = max_paging_size ) -> str | list:
        """ Returns the list of servers with a particular deployed implementation type.
            The value is specified in the filter. If it is null, or no request body is supplied,
            all servers are returned.

            Parameters
            ----------
            filter : str, opt
                Filter specifies the kind of deployed implementation type of the platforms to return information for.
                If the value is None, we will default to the "OMAG Server Platform".

            server : str, optional
               The name of the server to get governance engine summaries from. If not provided, the default server name
               will be used.

            start_from : int, optional
               The index from which to start fetching the engine actions. Default is 0.


            page_size : int, optional
               The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

            Returns
            -------
            Response
               A lit of json dict with the platform reports.

            Raises
            ------
            InvalidParameterException
            PropertyServerException
            UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_servers_by_dep_impl_type(filter, server, effective_time,
                                                                                    start_from, page_size))
        return response

    async def _async_get_server_templates_by_dep_impl_type(self, filter: str = "*", server:str = None, effective_time: str = None,
                                        start_from: int = 0, page_size: int = max_paging_size ) -> str | list:
        """ Returns the list of server templates with a particular deployed implementation type.   The value is
            specified in the filter. If it is null, or no request body is supplied, all servers are returned.
            Async version.

            Parameters
            ----------
            filter : str, opt
                Filter specifies the kind of deployed implementation type of the platforms to return information for.
                If the value is None, we will default to the "OMAG Server Platform".

            server : str, optional
               The name of the server to get governance engine summaries from. If not provided, the default server name
               will be used.

            start_from : int, optional
               The index from which to start fetching the engine actions. Default is 0.


            page_size : int, optional
               The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

            Returns
            -------
            Response
               A lit of json dict with the platform reports.

            Raises
            ------
            InvalidParameterException
            PropertyServerException
            UserNotAuthorizedException

        """
        if server is None:
           server = self.server_name

        if filter == '*':
            filter = None

        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/runtime-manager/servers/"
               f"by-deployed-implementation-type?startFrom={start_from}&pageSize={page_size}&getTemplates=true")

        body = body_slimmer({ "filter": filter, "effective_time": effective_time})

        response = await self._async_make_request("POST", url, body)

        return response.json().get('elementList','No platforms found')

    def get_server_templates_by_dep_impl_type(self, filter: str = "*", server:str = None, effective_time: str = None,
                                     start_from: int = 0, page_size: int = max_paging_size ) -> str | list:
        """ Returns the list of server templates with a particular deployed implementation type.
            The value is specified in the filter. If it is null, or no request body is supplied,
            all servers are returned.

            Parameters
            ----------
            filter : str, opt
                Filter specifies the kind of deployed implementation type of the platforms to return information for.
                If the value is None, we will default to the "OMAG Server Platform".

            server : str, optional
               The name of the server to get governance engine summaries from. If not provided, the default server name
               will be used.

            start_from : int, optional
               The index from which to start fetching the engine actions. Default is 0.


            page_size : int, optional
               The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

            Returns
            -------
            Response
               A lit of json dict with the platform reports.

            Raises
            ------
            InvalidParameterException
            PropertyServerException
            UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_server_templates_by_dep_impl_type(filter, server, effective_time,
                                                                                    start_from, page_size))
        return response


    async def _async_get_server_by_guid(self, server_guid: str = None, server:str = None,
                                           effective_time: str = None) -> str | list:
        """ Returns details about the server's catalog entry (asset). Async version.

            Parameters
            ----------
            filter : str, opt
                Filter specifies the kind of deployed implementation type of the platforms to return information for.
                If the value is None, we will default to the "OMAG Server Platform".

            server : str, optional
               The name of the server to get governance engine summaries from. If not provided, the default server name
               will be used.

            start_from : int, optional
               The index from which to start fetching the engine actions. Default is 0.


            page_size : int, optional
               The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

            Returns
            -------
            Response
               A lit of json dict with the platform reports.

            Raises
            ------
            InvalidParameterException
            PropertyServerException
            UserNotAuthorizedException

        """
        if server is None:
           server = self.server_name

        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/runtime-manager/servers/{server_guid}")

        if effective_time is not None:
            body = {
                "effectiveTime": effective_time
            }
            response = await self._async_make_request("POST", url, body)

        else:
            response = await self._async_make_request("POST", url)

        return response.json().get('element','No servers found')

    def get_server_by_guid(self, server_guid: str = None, server: str = None,
                                effective_time: str = None) -> str | list:
        """ Returns details about the server's catalog entry (asset). Async version.

            Parameters
            ----------
            filter : str, opt
                Filter specifies the kind of deployed implementation type of the platforms to return information for.
                If the value is None, we will default to the "OMAG Server Platform".

            server : str, optional
               The name of the server to get governance engine summaries from. If not provided, the default server name
               will be used.

            start_from : int, optional
               The index from which to start fetching the engine actions. Default is 0.


            page_size : int, optional
               The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

            Returns
            -------
            Response
               A lit of json dict with the platform reports.

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_server_by_guid(server_guid, server,
                                                                             effective_time))
        return response


    async def _async_get_server_report(self, server_guid: str = None, server: str = None) -> str | list:
        """ Returns details about the running server. Async version.

            Parameters
            ----------
            filter : str, opt
                Filter specifies the kind of deployed implementation type of the platforms to return information for.
                If the value is None, we will default to the "OMAG Server Platform".

            server : str, optional
               The name of the server to get governance engine summaries from. If not provided, the default server name
               will be used.


            Returns
            -------
            Response
               A lit of json dict with the platform reports.

            Raises
            ------
            InvalidParameterException
            PropertyServerException
            UserNotAuthorizedException

        """
        if server is None:
            server = self.server_name

        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/runtime-manager/servers/{server_guid}/report")

        response = await self._async_make_request("GET", url)

        return response.json().get('elementList', 'No server found')


    def get_server_report(self, server_guid: str = None, server: str = None) -> str | list:
        """ Returns details about the running server.

            Parameters
            ----------
            filter : str, opt
                Filter specifies the kind of deployed implementation type of the platforms to return information for.
                If the value is None, we will default to the "OMAG Server Platform".

            server : str, optional
               The name of the server to get governance engine summaries from. If not provided, the default server name
               will be used.

            Returns
            -------
            Response
               A lit of json dict with the platform reports.

            Raises
            ------
            InvalidParameterException
            PropertyServerException
            UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_server_report(server_guid, server))
        return response

