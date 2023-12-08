"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

 OMAG Server configuration functions.  These functions add definitions to an OMAG server's configuration document

"""

import json
import inspect

from .client import Client
import requests
from requests import Response
from .server_operations import ServerOps

from .util_exp import (
    OMAGCommonErrorCode,
    EgeriaException,
    InvalidParameterException,
    OMAGServerInstanceErrorCode,
    PropertyServerException,
    is_json,
)


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
        ServerOps.__init__(self, server_name, platform_url, user_id, user_pwd, verify_flag)
        self.admin_command_root = (self.platform_url +
                                   "/open-metadata/platform-services/users/" +
                                   user_id +
                                   "/server-platform")

    def shutdown_platform(self) -> bool:
        """
        Shutdown the platform.

        /open-metadata/platform-services/users/{userId}/server-platform/instance

        Parameters
        ----------

        Returns
        -------
        Returns true if successful, false otherwise.  Also throws exceptions if there is a URL issue or
        if the specified server isn't active.

        """

        url = self.admin_command_root + "/instance"

        response = self.make_request("DELETE", url)
        if response.status_code != 200:
            return False  # should never get here?

    def get_platform_origin(self) -> str:
        """
         Get the version and origin of the platform software

         /open-metadata/platform-services/users/{userId}/server-platform/origin
         Response from this call is a string not JSON..

         Parameters
         ----------

         Returns
         -------
        String with the platform origin information.  Also throws exceptions if no viable server or endpoint errors

        """
        # class_name = sys._getframe(2).f_code.co_name
        # caller_method = sys._getframe(1).f_code.co_name
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

    def activate_server_stored_config(self, server: str = None) -> str:
        """
        Activate a server on the associated platform with the stored configuration.

        /open-metadata/platform-services/users/{userId}/server-platform/servers/{serverName}/instance

        Parameters
        ----------
        server : Use the server if specified. If None, use the default server associated with the Platform object.

        Returns
        -------
        JSON string containing a SuccessMessageResponse.  Also throws exceptions if no viable server or endpoint errors

        """
        if server is None:
            server = self.server_name

        url = self.admin_command_root + "/servers/" + server + "/instance"

        response = self.make_request("POST", url)
        if response.status_code != 200:
            return response.json()  # should never get here?

        related_code = response.json().get("relatedHTTPCode")
        if related_code == 200:
            return response.json()
        else:
            raise InvalidParameterException(response.content)

    def shutdown_server(self, server: str = None) -> bool:
        """
        Shutdown a server on the associated platform.

        /open-metadata/platform-services/users/{userId}/server-platform/servers/{serverName}/instance

        Parameters
        ----------
        server : Use the server if specified. If None, use the default server associated with the Platform object.

        Returns
        -------
        Return true if successful. Also throws exceptions if no viable server or endpoint errors

        """
        if server is None:
            server = self.server_name

        url = self.admin_command_root + "/servers/" + server + "/instance"
        active = self.check_server_active(server)
        if not active:
            return True # already shutdown/inactive

        response = self.make_request("DELETE", url)

        if response.json().get("relatedHTTPCode") == 200:
            return True
        else:
            raise InvalidParameterException(response.content)

    def list_servers(self) -> list[str]:
        """
        List all known servers on the associated platform.

        /open-metadata/platform-services/users/{userId}/server-platform/servers

        Parameters
        ----------

        Returns
        -------
        List of servers. Also throws exceptions if no viable endpoint or errors

        """

        url = self.admin_command_root + "/servers"

        response = self.make_request("GET", url)

        if response.status_code != 200:
            return response.json()  # should never get here?

        related_code = response.json().get("relatedHTTPCode")
        if related_code == 200:
            return response.json().get("serverList")
        else:
            raise InvalidParameterException(response.content)

    def shutdown_unregister_servers(self) -> Response:
        """
        Shutdown and unregister all servers on the associated platform.

        /open-metadata/platform-services/users/{userId}/server-platform/servers

        Parameters
        ----------

        Returns
        -------
        Response object. Also throws exceptions if no viable endpoint or errors

        """

        url = self.admin_command_root + "/servers"
        try:
            response = self.make_request("DELETE", url)
            return response
        except Exception as e:
            raise (e)

    # def get_active_configuration(self, server: str = None) -> str:
    #     """
    #     Return the configuration of the server if it is running. Return invalidParameter Exception if not running.
    #
    #        /open-metadata/platform-services/users/{userId}/server-platform/servers/{serverName}/instance/configuration
    #
    #     Parameters
    #     ----------
    #     server: str - name of the server to get the configuration for.
    #
    #     Returns
    #     -------
    #     Returns configuration if server is active; InvalidParameter exception thrown otherwise
    #
    #     """
    #     if server is None:
    #         server = self.server_name
    #
    #     url = self.admin_command_root + "/servers/" + server + "/instance/configuration"
    #
    #     response = self.make_request("GET", url)
    #     if response.status_code != 200:
    #         return response.json()  # should never get here?
    #
    #     related_code = response.json().get("relatedHTTPCode")
    #     if related_code == 200:
    #         return response.json()
    #     else:
    #         raise InvalidParameterException(response.content)

    def activate_server_supplied_config(
        self, config_body: str, server: str = None
    ) -> Response:
        """
        Activate a server on the associated platform with the stored configuration.

        /open-metadata/platform-services/users/{userId}/server-platform/servers/{serverName}/instance

        Parameters
        ----------
        server : Use the server if specified. If None, use the default server associated with the Platform object.

        Returns
        -------
        Response object.  Also throws exceptions if no viable server or endpoint errors

        """
        if server is None:
            server = self.server_name

        url = self.admin_command_root + "/servers/" + server + "/instance/configuration"
        response = self.make_request("POST", url, config_body)
        if response.status_code != 200:
            return response.json()  # should never get here?

        related_code = response.json().get("relatedHTTPCode")
        if related_code == 200:
            return response.json()
        else:
            raise InvalidParameterException(response.content)

    # def load_archive_file(self, archive_file: str, server: str = None) -> Response:
    #     """
    #     Load the server with the contents of the indicated archvie file.
    #
    #     /open-metadata/platform-services/users/{userId}/server-platform/servers/{serverName}/instance/open-metadata-archives/file
    #
    #     Parameters
    #     ----------
    #     archive_file: the name of the archive file to load
    #             - note that the path is relative to the working directory of the platform.
    #     server : Use the server if specified. If None, use the default server associated with the Platform object.
    #
    #     Returns
    #     -------
    #     Response object.  Also throws exceptions if no viable server or endpoint errors
    #
    #     """
    #     if server is None:
    #         server = self.server_name
    #
    #     url = (
    #         self.admin_command_root
    #         + "/servers/"
    #         + server
    #         + "/instance/open-metadata-archives/file"
    #     )
    #
    #     response = self.make_request("POST-DATA", url, archive_file)
    #     if response.status_code != 200:
    #         return response.json()  # should never get here?
    #
    #     related_code = response.json().get("relatedHTTPCode")
    #     if related_code == 200:
    #         return response.json()
    #     else:
    #         raise InvalidParameterException(response.content)
    #
    # def get_active_server_status(self, server: str = None) -> Response:
    #     """
    #     Get the status for the specified server.
    #     /open-metadata/platform-services/users/{userId}/server-platform/servers/{server}/instance/status
    #
    #     Parameters
    #     ----------
    #     server : Use the server if specified. If None, use the default server associated with the Platform object.
    #
    #     Returns
    #     -------
    #     Response object. Also throws exceptions if no viable endpoint or errors
    #
    #     """
    #     if server is None:
    #         server = self.server_name
    #
    #     url = self.admin_command_root + "/servers/" + server + "/instance/status"
    #
    #     response = self.make_request("GET", url)
    #     if response.status_code != 200:
    #         return response.json()  # should never get here?
    #
    #     related_code = response.json().get("relatedHTTPCode")
    #     if related_code == 200:
    #         return response.json()
    #     else:
    #         raise InvalidParameterException(response.content)

    def is_server_known(self, server: str = None) -> Response:
        """
        Is the server known?
        /open-metadata/platform-services/users/{userId}/server-platform/servers/{server}/is-known

        Parameters
        ----------
        server : Use the server if specified. If None, use the default server associated with the Platform object.

        Returns
        -------
        Response object. Also throws exceptions if no viable endpoint or errors

        """
        if server is None:
            server = self.server_name

        url = self.admin_command_root + "/servers/" + server + "/is-known"
        response = self.make_request("GET", url)
        if response.status_code != 200:
            return response.json()  # should never get here?

        related_code = response.json().get("relatedHTTPCode")
        if related_code == 200:
            return response.json().get("flag")
        else:
            raise InvalidParameterException(response.content)

    def get_active_service_list_for_server(self, server: str = None) -> Response:
        """
        List all known active servers on the associated platform.

        /open-metadata/platform-services/users/{userId}/server-platform/servers/{server}/services

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
        if response.status_code != 200:
            return response.json()  # should never get here?

        related_code = response.json().get("relatedHTTPCode")
        if related_code == 200:
            service_list = response.json().get("serverServicesList")
            return service_list
        else:
            raise InvalidParameterException(response.content)

    # def get_server_status(self, server: str = None) -> Response:
    #     """
    #     Get status of the server specified.
    #
    #     /open-metadata/platform-services/users/{userId}/server-platform/servers/{server}/status
    #
    #     Parameters
    #     ----------
    #     server : Use the server if specified. If None, use the default server associated with the Platform object.
    #
    #     Returns
    #     -------
    #     Response object. Also throws exceptions if no viable endpoint or errors
    #
    #     """
    #     if server is None:
    #         server = self.server_name
    #
    #     url = self.admin_command_root + "/servers/" + server + "/status"
    #     response = self.make_request("GET", url)
    #     if response.status_code != 200:
    #         return response.json()  # should never get here?
    #
    #     related_code = response.json().get("relatedHTTPCode")
    #     if related_code == 200:
    #         return response.json()
    #     else:
    #         raise InvalidParameterException(response.content)

    def get_active_server_list(self) -> Response:
        """
        List all active servers on the associated platform.

        /open-metadata/platform-services/users/{userId}/server-platform/servers/active

        Parameters
        ----------
        server : Use the server if specified. If None, use the default server associated with the Platform object.

        Returns
        -------
        Response object. Also throws exceptions if no viable endpoint or errors

        """

        url = self.admin_command_root + "/servers/active"

        response = self.make_request("GET", url)
        if response.status_code != 200:
            return response.json()  # should never get here?

        related_code = response.json().get("relatedHTTPCode")
        if related_code == 200:
            return response.json().get("serverList")
        else:
            raise InvalidParameterException(response.content)

    def shutdown_all_servers(self) -> bool:
        """
        Shutdown all servers on the associated platform.

        /open-metadata/platform-services/users/{userId}/server-platform/servers/instance

        Parameters
        ----------

        Returns
        -------
        Response object. Also throws exceptions if no viable endpoint or errors

        """

        url = self.admin_command_root + "/servers/instance"
        response = self.make_request("DELETE", url)
        if response.status_code != 200:
            return False  # should never get here?

        related_code = response.json().get("relatedHTTPCode")
        if related_code == 200:
            return True  ## todo review this
        else:
            raise InvalidParameterException(response.content)

    def activate_server_if_down(self, server: str):
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
                    return True # server was already active
            else:
                return False
        except (InvalidParameterException, PropertyServerException) as e:
            raise (e)

    def activate_servers_on_platform(self, server_list: str) -> bool:
        num_servers = len(server_list)
        if num_servers > 0:
            for x in range(num_servers):
                self.activate_server_stored_config(server_list[x])
            return True
        return False

    def check_server_configured(self, server: str = None) -> bool:
        if server is None:
            server = self.server_name
        response = self.get_active_configuration(server)

        server_config = response["omagserverConfig"]
        audit_trail = server_config["auditTrail"]
        if audit_trail is not None:
            return True
        else:
            return False

    def check_server_active(self, server: str = None):

        """
        Get status of the server specified.
        /open-metadata/platform-services/users/{userId}/server-platform/servers/{server}/status

        Parameters
        ----------
        server : Use the server if specified. If None, use the default server associated with the Platform object.

        Returns
        -------
        Response object. Also throws exceptions if no viable endpoint or errors

        """

        if server is None:
            server = self.server_name

        url = self.admin_command_root + "/servers/" + server + "/status"
        response = self.make_request("GET", url)
        if response.status_code != 200:
            return response.json()  # should never get here?

        related_code = response.json().get("relatedHTTPCode")
        if related_code == 200:
            return response.json().get("active")
        else:
            raise InvalidParameterException(response.content)


if __name__ == "__main__":
    p = Platform("meow", "https://127.0.0.1:9443", "garygeeke", verify_flag=False)
    response = p.list_servers()
    l = response.json()["result"]
    print(l)
# activatePlatform(corePlatformName, corePlatformURL, [cocoMDS2Name, cocoMDS3Name, cocoMDS5Name, cocoMDS6Name])
