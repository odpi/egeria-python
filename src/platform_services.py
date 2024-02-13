"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

 OMAG Platform functions.  These functions are used to configure and operate the Egeria OMAG Server PLatform.

"""

import inspect
import json

import requests

from pyegeria._exceptions import (
    OMAGCommonErrorCode,
    InvalidParameterException,
    UserNotAuthorizedException,
    PropertyServerException,
)
from pyegeria.server_operations import ServerOps


class Platform(ServerOps):
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



        get_platform_origin(self) -> str

        activate_server_stored_config(self, server: str = None, timeout: int = 30) -> None

        activate_server_supplied_config(self, config_body: str, server: str = None, timeout: int = 30) -> None

        get_known_servers(self) -> list[str] | str

        is_server_known(self, server: str = None) -> bool

        check_server_active(self, server: str = None)

        get_active_server_list(self) -> dict | str

        shutdown_platform(self) -> None:

        shutdown_server(self, server: str = None) -> None:

        shutdown_unregister_servers(self) -> None

        shutdown_all_servers(self) -> None

        activate_server_if_down(self, server: str) -> bool

        activate_servers_on_platform(self, server_list: str) -> bool

        list_servers(self) -> list[str] | str

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
        ServerOps.__init__(self, server_name, platform_url, user_id, user_pwd, verify_flag)
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

    def activate_server_stored_config(self, server: str = None, timeout: int = 30) -> None:
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

    def activate_server_supplied_config(self, config_body: str, server: str = None, timeout: int = 30) -> None:
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

    def activate_server_if_down(self, server: str) -> bool:
        """ Activate server if it is down.

        Parameters
        ----------
        server : str
            The name of the server to activate. If None, the method uses the server name stored in the object.

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
        if server is None:
            server = self.server_name
        try:
            is_known = self.is_server_known(server)
            if is_known:
                actives = self.get_active_server_list()
                if actives is None:
                    self.activate_server_stored_config(server)
                    return True
                if server not in actives:
                    self.activate_server_stored_config(server)
                    return True
                else:
                    return True  # server was already active
            else:
                return False
        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            raise (e)

    def activate_servers_on_platform(self, server_list: str) -> bool:
        """ Activate the servers from the list provided.
        Parameters
        ----------
        server_list : str
            A string representing the list of servers to be activated.

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
        num_servers = len(server_list)
        if num_servers > 0:
            for x in range(num_servers):
                self.activate_server_stored_config(server_list[x])
            return True
        return False


if __name__ == "__main__":
    p = Platform("meow", "https://127.0.0.1:9443", "garygeeke", verify_flag=False)
    response = p.get_known_servers()

    print(response)
