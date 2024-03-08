"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

 OMAG Server operations.  These functions provide operations on a running OMAG server.

"""

from requests import Response

from pyegeria.exceptions import (
    InvalidParameterException,
)
from pyegeria import Platform
import asyncio

class ServerOps(Platform):
    """
    Client to issue operations on a running OMAG server.

    Attributes:

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
        __init__(self,
                 platform_url: str,
                 end_user_id: str,
                 )
         Initializes the connection - throwing an exception if there is a problem

    """


    def __init__(
            self,
            server_name: str,
            platform_url: str,
            user_id: str,
            user_pwd: str = None,
            verify_flag: bool = False,
    ):
        Platform.__init__(self, server_name, platform_url, user_id, user_pwd, verify_flag)
        self.ops_command_root = (self.platform_url +
                                   "/open-metadata/server-operations/users/" +
                                   user_id)


    async def _async_get_active_configuration(self, server: str = None) -> dict | str:
        """
        Return the configuration of the server if it is running. Return invalidParameter Exception if not running.

        Parameters
        ----------
        server: str - name of the server to get the configuration for.

        Returns
        -------
        Returns configuration if server is active; InvalidParameter exception thrown otherwise

        """
        if server is None:
            server = self.server_name

        is_known = await self._async_is_server_known(server)
        if is_known is False:
            return "No active configuration found"

        url = self.ops_command_root + "/servers/" + server + "/instance/configuration"

        response = await self._async_make_request("GET", url)
        return response.json().get("omagserverConfig", "No active configuration found")

    def get_active_configuration(self, server: str = None) -> dict | str:
        """
        Return the configuration of the server if it is running. Return invalidParameter Exception if not running.

        Parameters
        ----------
        server: str - name of the server to get the configuration for.

        Returns
        -------
        Returns configuration if server is active; InvalidParameter exception thrown otherwise

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_active_configuration(server))
        return response




    async def _async_add_archive_file(self, archive_file: str, server: str = None) -> None:
        """
        Load the server with the contents of the indicated archive file.

        Parameters
        ----------
        archive_file: the name of the archive file to load
                - note that the path is relative to the working directory of the platform.
        server : Use the server if specified. If None, use the default server associated with the Platform object.

        Returns
        -------
        Response object.  Also throws exceptions if no viable server or endpoint errors

        """
        if server is None:
            server = self.server_name

        url = (
                self.ops_command_root
                + "/servers/" + server
                + "/instance/open-metadata-archives/file"
        )

        await self._async_make_request("POST-DATA", url, archive_file)

    def add_archive_file(self, archive_file: str, server: str = None) -> None:
        """
        Load the server with the contents of the indicated archive file.

        Parameters
        ----------
        archive_file: the name of the archive file to load
                - note that the path is relative to the working directory of the platform.
        server : Use the server if specified. If None, use the default server associated with the Platform object.

        Returns
        -------
        Response object.  Also throws exceptions if no viable server or endpoint errors

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_add_archive_file(archive_file, server))

    async def _async_add_archive(self, archive_connection: str, server: str = None) -> None:
        """ Load the server with the contents of the indicated archive file.

        /open-metadata/server-operations/users/{userId}/server-platform/servers/{serverName}/instance/open-metadata-archives/connection

        Parameters
        ----------
        archive_connection: str
            the name of the archive connection to load from
        server: str
            Use the server if specified. If None, use the default server associated with the Platform object.

        Returns
        -------
        Response object.  Also throws exceptions if no viable server or endpoint errors

        Todo: Need to find a good example of an archive connection to test with
        """
        if server is None:
            server = self.server_name

        url = (
                self.ops_command_root
                + "/servers/" + server
                + "/instance/open-metadata-archives/connection"
        )
        await self._async_make_request("POST-DATA", url, archive_connection)


    def add_archive(self, archive_connection: str, server: str = None) -> None:
        """
        Load the server with the contents of the indicated archive file.

        /open-metadata/server-operations/users/{userId}/server-platform/servers/{serverName}/instance/open-metadata-archives/connection

        Parameters
        ----------
        archive_connection: str
            the name of the archive connection to load from
        server: str
            Use the server if specified. If None, use the default server associated with the Platform object.

        Returns
        -------
        Response object.  Also throws exceptions if no viable server or endpoint errors

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_add_archive_file(archive_connection,server))

    async def _async_get_active_server_status(self, server:str = None) -> dict:
        """  Get the status for the specified server.

        Parameters
        ----------
        server : Use the server if specified. If None, use the default server associated with the Platform object.

        Returns
        -------
        dict: a json object containing the status of the specified server

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
        """
        if server is None:
            server = self.server_name

        url = self.admin_command_root + "/servers/" + server + "/instance/status"

        response = await self._async_make_request("GET", url)
        return response

    def get_active_server_status(self, server: str = None) -> dict:
        """
        Get the status for the specified server.
        /open-metadata/platform-services/users/{userId}/server-platform/servers/{server}/instance/status

        Parameters
        ----------
        server : Use the server if specified. If None, use the default server associated with the Platform object.

        Returns
        -------
        dict: a json object containing the status of the specified server

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_active_server_status(server))
        return response.json()

    async def _async_get_active_service_list_for_server(self, server: str = None) -> Response:
        """
        List all known active servers on the associated platform.

        /open-metadata/server-operations/users/{userId}/server-platform/servers/{server}/services

        Parameters
        ----------
        server : Use the server if specified. If None, use the default server associated with the Platform object.

        Returns
        -------
        Response object. Also throws exceptions if no viable endpoint or errors

        """
        if server is None:
            server = self.server_name

        url = self.ops_command_root + "/servers/" + server + "/services"
        response = await self._async_make_request("GET", url)
        return response.json().get("serverServicesList")

    def get_active_service_list_for_server(self, server: str = None) -> Response:
        """
        List all known active servers on the associated platform.

        /open-metadata/server-operations/users/{userId}/server-platform/servers/{server}/services

        Parameters
        ----------
        server : Use the server if specified. If None, use the default server associated with the Platform object.

        Returns
        -------
        Response object. Also throws exceptions if no viable endpoint or errors

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_active_service_list_for_server(server))
        return response

    async def _async_get_governance_engine_summaries(self, server: str = None) -> dict:
        """ Get Governance Engine Summaries. Async version.
        Parameters
        ----------
        server : str, optional
            The name of the server to get governance engine summaries from. If not provided, the default server name will be used.

        Returns
        -------
        Response
            The response object containing the governance engine summaries.

        """
        if server is None:
            server = self.server_name

        url = (f"{self.platform_url}/servers/{server}/open-metadata/engine-host/users/{self.user_id}"
               f"/governance-engines/summary")
        response = await self._async_make_request("GET", url)
        return response.json().get("governanceEngineSummaries")

    def get_governance_engine_summaries(self, server: str = None) -> dict:
        """Get Governance Engine Summaries.
        Parameters
        ----------
        server : str, optional
            The name of the server to get governance engine summaries from. If not provided, the default server name will be used.

        Returns
        -------
        Response
            The response object containing the governance engine summaries.

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_governance_engine_summaries(server))
        return response
#
# Integration Daemon
#
    async def _async_get_integration_daemon_status(self, server: str = None) -> dict | str:
        """ Get the current status of the integration daemon. Async version.

        """
        if server is None:
            server = self.server_name

        url = f"{self.platform_url}/servers/{server}/open-metadata/integration-daemon/users/{self.user_id}/status"
        response = await self._async_make_request("GET", url)
        return response.json().get("integrationDaemonStatus", "No Integration Groups")
        # return response.json()

    def get_integration_daemon_status(self, server: str = None) -> dict | str:
        """ Get the current status of the integration daemon. Async version.

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_integration_daemon_status(server))
        return response

    def get_integration_connector_status(self, server: str = None)-> list:
        response = self.get_integration_daemon_status(server)
        pass


if __name__ == "__main__":
    p = ServerOps("meow", "https://127.0.0.1:9443", "garygeeke", verify_flag=False)
    response = p.get_active_service_list_for_server()
    out = response.json()["result"]
    print(out)
