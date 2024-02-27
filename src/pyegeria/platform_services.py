"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

 OMAG Platform functions.  These functions are used to configure and operate the Egeria OMAG Server PLatform.

"""

import inspect
import json

import requests

from pyegeria import CoreServerConfig, Client
from pyegeria.exceptions import (
    OMAGCommonErrorCode,
    InvalidParameterException,
    UserNotAuthorizedException,
    PropertyServerException, print_exception_response,
)


class Platform(Client):
    """
    Client to operate Egeria Platforms - inherits from Server Ops

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
        __init__(self, platform_url: str, end_user_id: str)
         Initializes the connection - throwing an exception if there is a problem



        get_platform_origin() -> str

        activate_server_stored_config(server: str = None, timeout: int = 30) -> None

        activate_server_supplied_config(config_body: str, server: str = None, timeout: int = 30) -> None

        get_active_server_instance_status(server: str = None)-> dict | str

        get_known_servers() -> list[str] | str

        is_server_known(server: str = None) -> bool

        is_server_configured(server: str = None) -> bool

        check_server_active(server: str = None)

        get_active_server_list() -> dict | str

        shutdown_platform() -> None:

        shutdown_server(server: str = None) -> None:

        shutdown_unregister_servers() -> None

        shutdown_all_servers() -> None

        activate_server_if_down(server: str) -> bool

        activate_servers_on_platform(server_list: str) -> bool

       activate_platform(self, platform_name: str, hosted_server_names: [str], timeout:int = 60) -> None

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
                                   "/open-metadata/platform-services/users/" +
                                   user_id +
                                   "/server-platform")

    def get_platform_origin(self) -> str:
        """ Get the version and origin of the platform software

         /open-metadata/platform-services/users/{userId}/server-platform/origin
         Response from this call is a string not JSON..

         Parameters
         ----------

         Returns
         -------
        String with the platform origin information.  Also throws exceptions if no viable server or endpoint errors

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
        """

        calling_frame = inspect.currentframe().f_back
        caller_method = inspect.getframeinfo(calling_frame).function
        class_name = __class__.__name__

        url = self.admin_command_root + "/origin"
        try:
            response = requests.get(
                url, timeout=30, params=None, verify=self.ssl_verify
            )
            if response.status_code != 200:
                msg = OMAGCommonErrorCode.CLIENT_SIDE_REST_API_ERROR.value[
                    "message_template"
                ].format(
                    response.status_code,
                    caller_method,
                    class_name,
                    url,
                    OMAGCommonErrorCode.CLIENT_SIDE_REST_API_ERROR.value["message_id"],
                )
                exc_msg = json.dumps(
                    {
                        "class": "VoidResponse",
                        "relatedHTTPCode": response.status_code,
                        "exceptionClassName": "InvalidParameterException",
                        "actionDescription": caller_method,
                        "exceptionErrorMessage": msg,
                        "exceptionErrorMessageId": OMAGCommonErrorCode.CLIENT_SIDE_REST_API_ERROR.value[
                            "message_id"
                        ],
                        "exceptionErrorMessageParameters": [
                            url,
                            self.server_name,
                            self.user_id,
                        ],
                        "exceptionSystemAction": OMAGCommonErrorCode.CLIENT_SIDE_REST_API_ERROR.value[
                            "system_action"
                        ],
                        "exceptionUserAction": OMAGCommonErrorCode.CLIENT_SIDE_REST_API_ERROR.value[
                            "user_action"
                        ],
                        "exceptionProperties": {
                            "endpoint": url,
                            "server": self.server_name,
                            "user_id": self.user_id,
                        },
                    }
                )
                raise InvalidParameterException(exc_msg)
            else:
                return response.text
        except (InvalidParameterException):
            raise

        except (
                requests.ConnectionError,
                requests.ConnectTimeout,
                requests.HTTPError,
                requests.RequestException,
                requests.Timeout,
        ) as e:
            msg = OMAGCommonErrorCode.CLIENT_SIDE_REST_API_ERROR.value[
                "message_template"
            ].format(
                e.args[0],
                caller_method,
                class_name,
                url,
                OMAGCommonErrorCode.CLIENT_SIDE_REST_API_ERROR.value["message_id"],
            )
            exc_msg = json.dumps(
                {
                    "class": "VoidResponse",
                    "relatedHTTPCode": 400,
                    "exceptionClassName": "InvalidParameterException",
                    "actionDescription": caller_method,
                    "exceptionErrorMessage": msg,
                    "exceptionErrorMessageId": OMAGCommonErrorCode.CLIENT_SIDE_REST_API_ERROR.value[
                        "message_id"
                    ],
                    "exceptionErrorMessageParameters": [
                        url,
                        self.server_name,
                        self.user_id,
                    ],
                    "exceptionSystemAction": OMAGCommonErrorCode.CLIENT_SIDE_REST_API_ERROR.value[
                        "system_action"
                    ],
                    "exceptionUserAction": OMAGCommonErrorCode.CLIENT_SIDE_REST_API_ERROR.value[
                        "user_action"
                    ],
                    "exceptionProperties": {
                        "endpoint": url,
                        "server": self.server_name,
                        "user_id": self.user_id,
                    },
                }
            )
            raise InvalidParameterException(exc_msg)

    def activate_server_stored_config(self, server: str = None, timeout: int = 60) -> None:
        """ Activate a server on the associated platform with the stored configuration.

        Parameters
        ----------
        server : Use the server if specified. If None, use the default server associated with the Platform object.

        Returns
        -------
        None

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

        url = self.admin_command_root + "/servers/" + server + "/instance"

        self.make_request("POST", url, time_out=timeout)

    def activate_server_supplied_config(self, config_body: str, server: str = None, timeout: int = 60) -> None:
        """ Activate a server on the associated platform with the stored configuration.

        Parameters
        ----------
        config_body: str
            Server configuration to use for activation.
        server : str, optional
            Use the server if specified. If None, use the default server associated with the Platform object.
        timeout: int, optional
            A request timeout in seconds

        Returns
        -------
        None

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

        url = self.admin_command_root + "/servers/" + server + "/instance/configuration"
        self.make_request("POST", url, config_body, time_out=timeout)

    def get_active_server_instance_status(self, server: str = None) -> dict | str:
        """ Get the current status of all services running in the specified active server.

                Parameters
                ----------
                server : str, optional
                    The current active server we want to get status from.
                    If None, use the default server associated with the Platform object.
                Returns
                -------
                List of server status.

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

        url = f"{self.admin_command_root}/servers/{server}/instance/status"
        response = self.make_request("GET", url)
        return response.json().get("serverStatus", "No status found")

    def get_known_servers(self) -> list[str] | str:
        """ List all known servers on the associated platform.

        Parameters
        ----------

        Returns
        -------
        List of servers. Also throws exceptions if no viable endpoint or errors

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
        """
        url = self.admin_command_root + "/servers"
        response = self.make_request("GET", url)
        return response.json().get("serverList", "No servers found")

    def is_server_known(self, server: str = None) -> bool:
        """ Is the server known?

        Parameters
        ----------
        server : Use the server if specified. If None, use the default server associated with the Platform object.

        Returns
        -------
        bool: Returns True if the server is known, False otherwise.

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

        url = self.admin_command_root + "/servers/" + server + "/is-known"
        response = self.make_request("GET", url)
        return response.json().get("flag")

    def is_server_configured(self, server: str = None) -> bool:
        """ is a server known and configured?
        Parameters
        ----------
        server : str, optional
            The name of the server to check if configured. If not specified, the server name stored in `self.server_name` will be used.

        Returns
        -------
        bool
            Returns `True` if the server is configured, otherwise `False`.
        """
        if server is None:
            server = self.server_name
        config_response = self.get_active_configuration(server)
        if type(config_response) is dict:
            return True
        else:
            return False

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
        if server is None:
            server = self.server_name

        is_known = self.is_server_known(server)
        if is_known is False:
            return "No active configuration found"

        url = self.admin_command_root + "/servers/" + server + "/instance/configuration"
        response = self.make_request("GET", url)
        return response.json().get("omagserverConfig", "No active configuration found")

    def check_server_active(self, server: str = None):
        """ Get status of the server specified.

        Parameters
        ----------
        server : Use the server if specified. If None, use the default server associated with the Platform object.

        Returns
        -------
        bool: True if the server has been activated, otherwise False.
        """

        if server is None:
            server = self.server_name

        url = self.admin_command_root + "/servers/" + server + "/status"
        response = self.make_request("GET", url)

        return response.json().get("active")

    def get_active_server_list(self) -> dict | str:
        """
        List all active servers on the associated platform.

        Parameters
        ----------

        Returns
        -------
        List of servers. If no servers found then returns a string indicating none found.

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
        """

        url = self.admin_command_root + "/servers/active"

        response = self.make_request("GET", url)
        return response.json().get("serverList", "No servers found")

    def shutdown_platform(self) -> None:
        """ Shutdown the platform.

        An exception is thrown if a problem occurs during the request.

        Parameters
        ----------

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
        """

        url = self.admin_command_root + "/instance"

        self.make_request("DELETE", url)

    def shutdown_server(self, server: str = None) -> None:
        """ Shutdown a server on the associated platform.

        Parameters
        ----------
        server : Use the server if specified. If None, use the default server associated with the Platform object.

        Returns
        -------
        None

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

        url = self.admin_command_root + "/servers/" + server + "/instance"
        self.make_request("DELETE", url)

    def shutdown_unregister_servers(self) -> None:
        """
        Shutdown and unregister all servers from their cohorts on the associated platform.

        /open-metadata/platform-services/users/{userId}/server-platform/servers

        Parameters
        ----------

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
        """

        url = self.admin_command_root + "/servers"

        self.make_request("DELETE", url)

    def shutdown_all_servers(self) -> None:
        """
        Shutdown all servers on the associated platform.

        Parameters
        ----------

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
        """

        url = self.admin_command_root + "/servers/instance"
        self.make_request("DELETE", url)

    def activate_server_if_down(self, server: str, verbose:bool = True, timeout:int = 60) -> bool:
        """ Activate server if it is down.

        Parameters
        ----------
        server : str
            The name of the server to activate. If None, the method uses the server name stored in the object.
        verbose: bool, optional
            If 'verbose' is False, then print statements are ignored. Defaults to True.
        timeout: int, optional
            A time in seconds to wait for the request to complete
        Returns
        -------
        bool
            Return False if server is not known

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
        """
        c_client = CoreServerConfig(server,self.platform_url, self.user_id)

        if server is None:
            server = self.server_name
        try:
            if verbose:
                print(f"\n\tChecking OMAG Server {server}")
            is_configured = c_client.is_server_configured()
            if is_configured:
                if verbose:
                    print(f"        OMAG Server {server} is configured")
                active_servers = self.get_active_server_list()
                if server in active_servers:
                    if verbose:
                        print(f"        OMAG Server {server} is active")
                    return True
                else: # configured but not active, so activate
                    if verbose:
                        print(f"        OMAG Server {server} is being activated")
                    self.activate_server_stored_config(timeout=timeout)
                    return True
            else:
                if verbose:
                    print(f"      OMAG Server {server} needs to be configured")
                return False

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            if verbose:
                print_exception_response(e)
            raise (e)

    def activate_servers_on_platform(self, server_list: [str], verbose = False, timeout:int = 60) -> bool:
        """ Activate the servers from the list provided.
        Parameters
        ----------
        server_list : str
            A string representing the list of servers to be activated.
        verbose: bool, optional
            If verbose is true, print out diagnostic messages.
        timeout: int, optional
            A time in seconds to wait for the request to complete

        Returns
        -------
        bool
            Returns True if at least one server is successfully activated.
            Returns False if the server list is empty.

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        This method activates servers on a platform by iterating through the given server list and calling the
        `activate_server_stored_config` method for each server. The method returns True if at least one server
        is successfully activated, otherwise it returns False.
        """
        c_client = CoreServerConfig(server_list[0], self.platform_url, self.user_id)
        num_servers = len(server_list)
        if num_servers > 0:
            for x in server_list:
                if c_client.is_server_configured(x) is True:
                    if verbose:
                        print(f"\t\tServer {x} is configured and ready to be activated")
                    self.activate_server_stored_config(x, timeout=timeout)
                    if verbose:
                        print(f"\t\tServer {x} was activated")
                else:
                    if verbose:
                        print(f"\t\tServer {x} is not configured - returning")
                    return False # a server was not configured
            return True
        else:
            if verbose:
                print(f"\t\tServer list empty")
            return False

    def activate_platform(self, platform_name: str, hosted_server_names: [str], timeout:int = 60) -> None:
        """ Activate an OMAG Server Platform and start the servers requested

        Parameters
        ----------
        platform_name : str
            The display friendly name of the platform to activate.

        hosted_server_names : list of str
            List of names of the OMAG servers to activate.

        timeout: int, optional
            A time in seconds to wait for the request to complete
        Returns
        -------
        None

        Raises
        ------
        Exception
            If there is an error while activating the platform or starting the servers.

        Notes
        -----
        This method attempts to activate a platform by checking its status. If the platform is already active and running, it prints a message indicating so and activates any hosted servers
        * that are down. If the platform is not active, it prints a message indicating so. If there is any exception while activating the platform or starting the servers, it prints an error
        * message and the exception response.
        """
        try:
            status = self.get_platform_origin()
            if status:
                print(f"\n\n\t Platform {platform_name} is active and running: \n\t\t{status}")
                print(f"\tWill start the following servers if configured: {hosted_server_names}")
                for server in hosted_server_names:
                    activated = self.activate_server_if_down(server, timeout=timeout)
                    if activated:
                        print(f"\t Started server: {server}")
                return
            else:
                print(f"   {platform_name}, is down - start it before proceeding")
        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        )as e:
            print(f"   {platform_name}, is down - start it before proceeding")
            print_exception_response(e)


if __name__ == "__main__":
    p = Platform("meow", "https://127.0.0.1:9443", "garygeeke", verify_flag=False)
    response = p.get_known_servers()

    print(response)
