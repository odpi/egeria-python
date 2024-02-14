"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

 OMAG Server operations.  These functions provide operations on a running OMAG server.

"""

from requests import Response

from pyegeria._exceptions import (
    InvalidParameterException,
)
from pyegeria._client import Client


class ServerOps(Client):

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

    admin_command_root: str

    def __init__(
        self,
        server_name: str,
        platform_url: str,
        user_id: str,
        user_pwd: str = None,
        verify_flag: bool = False,
    ):
        Client.__init__(self, server_name, platform_url, user_id, user_pwd, verify_flag)
        self.admin_command_root = (self.platform_url +
                                   "/open-metadata/server-operations/users/" +
                                   user_id)

    def get_active_configuration(self, server: str = None) -> str:
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

        url = self.admin_command_root + "/servers/" + server + "/instance/configuration"
        response = self.make_request("GET", url)
        if type(response) is dict:
            return response.json().get("omagserverConfig", "No configuration found")
        else:
            return ("No configuration found")

    def add_archive_file(self, archive_file: str, server: str = None) -> Response:
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
            self.admin_command_root
            + "/servers/" + server
            + "/instance/open-metadata-archives/file"
        )

        response = self.make_request("POST-DATA", url, archive_file)
        if response.status_code != 200:
            return response.json()  # should never get here?

        related_code = response.json().get("relatedHTTPCode")
        if related_code == 200:
            return response.json()
        else:
            raise InvalidParameterException(response.content)

    def add_archive(self, archive_connection: str, server: str = None) -> Response:
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

        Todo: Need to find a good example of an archive connection to test with
        """
        if server is None:
            server = self.server_name

        url = (
            self.admin_command_root
            + "/servers/" + server
            + "/instance/open-metadata-archives/connection"
        )

        response = self.make_request("POST-DATA", url, archive_connection)
        if response.status_code != 200:
            return response.json()  # should never get here?

        related_code = response.json().get("relatedHTTPCode")
        if related_code == 200:
            return response.json()
        else:
            raise InvalidParameterException(response.content)

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
        if server is None:
            server = self.server_name

        url = self.admin_command_root + "/servers/" + server + "/instance/status"

        response = self.make_request("GET", url)

        return response.json()

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
        if server is None:
            server = self.server_name

        url = self.admin_command_root + "/servers/" + server + "/services"
        response = self.make_request("GET", url)
        return response.json().get("serverServicesList")

    def get_server_status(self, server: str = None) -> dict:
        """
        Get status of the server specified.

        Parameters
        ----------
        server : Use the server if specified. If None, use the default server associated with the Platform object.

        Returns
        -------
        Json dict containing the active server status.
        """
        if server is None:
            server = self.server_name

        url = self.admin_command_root + "/servers/" + server + "/instance/status"
        response = self.make_request("GET", url)
        return response.json()

if __name__ == "__main__":
    p = ServerOps("meow", "https://127.0.0.1:9443", "garygeeke", verify_flag=False)
    response = p.get_active_service_list_for_server()
    out = response.json()["result"]
    print(out)

