"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

 OMAG Platform functions.  These functions are used to configure and operate the Egeria OMAG Server PLatform.

"""

import asyncio
import inspect
import json

import httpx

from pyegeria import Client
from pyegeria._validators import validate_user_id
from pyegeria._exceptions import (
    OMAGCommonErrorCode,
    InvalidParameterException,
    UserNotAuthorizedException,
    PropertyServerException, print_exception_response,
)


# import requests


class Platform(Client):
    """
    Client to operate Egeria Platforms - inherits from Server Ops

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
        validate_user_id(user_id)  # add this check since we aren't using bearer tokens in this class

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

        global response
        calling_frame = inspect.currentframe().f_back
        caller_method = inspect.getframeinfo(calling_frame).function
        class_name = __class__.__name__

        url = self.admin_command_root + "/origin"

        local_session = httpx.Client(verify=self.ssl_verify)
        response = " "
        try:
            response = local_session.get(url)
            if response.status_code != 200:
                msg = OMAGCommonErrorCode.CLIENT_SIDE_REST_API_ERROR.value[
                    "message_template"
                ].format(
                    response.status_code,
                    caller_method,
                    class_name,
                    url,
                    OMAGCommonErrorCode.CLIENT_SIDE_REST_API_ERROR.value["message_id"],
                ) + "==>System reports:'" + response.reason_phrase + "'"
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
        except InvalidParameterException:
            raise

        except (
                httpx.NetworkError,
                httpx.ProtocolError,
                httpx.HTTPStatusError,
                httpx.TimeoutException,
        ) as e:
            msg = OMAGCommonErrorCode.CLIENT_SIDE_REST_API_ERROR.value[
                "message_template"
            ].format(
                e.args[0],
                caller_method,
                class_name,
                url,
                OMAGCommonErrorCode.CLIENT_SIDE_REST_API_ERROR.value["message_id"],
            ) + "==>System reports:'" + response.reason_phrase + "'"
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

    async def _async_activate_server_stored_config(self, server: str = None, timeout: int = 60) -> None:
        """ Activate a server on the associated platform with the stored configuration. Async version.

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

        await self._async_make_request("POST", url, time_out=timeout)

    def activate_server_stored_config(self, server: str = None, timeout: int = 90) -> None:
        """ Activate a server on the associated platform with the stored configuration.

        Parameters
        ----------
        server : Use the server if specified. If None, use the default server associated with the Platform object.
        timeout: number of seconds to wait for a response before raising an exception

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
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_activate_server_stored_config(server, timeout))
        return response

    async def _async_activate_server_supplied_config(self, config_body: dict, server: str = None, timeout: int = 60)\
            -> None:
        """ Activate a server on the associated platform with the stored configuration. Async version.

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
        await self._async_make_request("POST", url, config_body, time_out=timeout)

    def activate_server_supplied_config(self, config_body: dict, server: str = None, timeout: int = 60) -> None:
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
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_activate_server_supplied_config(config_body, server, timeout))

    async def _async_get_active_server_instance_status(self, server: str = None) -> dict | str:
        """ Get the current status of all services running in the specified active server. Async version.

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
        response = await self._async_make_request("GET", url)
        return response.json().get("serverStatus", "No status found")

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
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_active_server_instance_status(server))
        return response

    async def _async_get_known_servers(self) -> list[str] | str:
        """ List all known servers on the associated platform. Async version.

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
        response = await self._async_make_request("GET", url)
        return response.json().get("serverList", "No servers found")

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
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_known_servers())
        return response

    async def _async_is_server_known(self, server: str = None) -> bool:
        """ Is the server known? Async version.

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
        response = await self._async_make_request("GET", url)
        return response.json().get("flag")

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
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_is_server_known(server))
        return response

    async def _async_is_server_configured(self, server: str = None) -> bool:
        """ is a server known and configured? Async version.
        Parameters
        ----------
        server : str, optional
            The name of the server to check if configured. If not specified, the server name stored in
            `self.server_name` will be used.

        Returns
        -------
        bool
            Returns `True` if the server is configured, otherwise `False`.
        """
        if server is None:
            server = self.server_name
        url = f"{self.platform_url}/open-metadata/admin-services/users/{self.user_id}/servers/{server}/configuration"

        response = await self._async_make_request("GET", url)
        config = response.json().get("omagserverConfig", "No configuration found")
        if 'auditTrail' in config:
            return True
        else:
            return False

    def is_server_configured(self, server: str = None) -> bool:
        """ is a server known and configured?
        Parameters
        ----------
        server : str, optional
            The name of the server to check if configured. If not specified,
            the server name stored in `self.server_name` will be used.

        Returns
        -------
        bool
            Returns `True` if the server is configured, otherwise `False`.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_is_server_configured(server))
        return response

    async def _async_get_active_configuration(self, server: str = None) -> dict | str:
        """  Return the configuration of the server if it is running. Return invalidParameter Exception if not running.
             Async version.

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

        url = self.admin_command_root + "/servers/" + server + "/instance/configuration"

        response = await self._async_make_request("GET", url)
        return response.json().get("omagserverConfig", "No active configuration found")

    def get_active_configuration(self, server: str = None) -> dict | str:
        """ Return the configuration of the server if it is running. Return invalidParameter Exception if not running.

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

    async def _async_check_server_active(self, server: str = None):
        """ Get status of the server specified. Async version.

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
        response = await self._async_make_request("GET", url)

        return response.json().get("active")

    def check_server_active(self, server: str = None):
        """ Get status of the server specified.

        Parameters
        ----------
        server : Use the server if specified. If None, use the default server associated with the Platform object.

        Returns
        -------
        bool: True if the server has been activated, otherwise False.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_check_server_active(server))
        return response

    async def _async_get_active_server_list(self) -> list:
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

        response = await self._async_make_request("GET", url)
        return response.json().get('serverList', "No servers active")

    def get_active_server_list(self) -> list:
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
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_active_server_list())
        return response

    async def _async_shutdown_platform(self) -> None:
        """ Shutdown the platform. Async version.

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

        await self._async_make_request("DELETE", url)

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
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_shutdown_platform())

    async def _async_shutdown_server(self, server: str = None) -> None:
        """ Shutdown a server on the associated platform. Async version.

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
        await self._async_make_request("DELETE", url)

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
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_shutdown_server(server))

    async def _async_shutdown_unregister_servers(self) -> None:
        """
        Shutdown and unregister all servers from their cohorts on the associated platform. Async version.

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

        await self._async_make_request("DELETE", url)

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
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_shutdown_unregister_servers())

    async def _async_shutdown_all_servers(self) -> None:
        """
        Shutdown all servers on the associated platform. Async version.

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
        await self._async_make_request("DELETE", url)

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
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_shutdown_all_servers())

    async def _async_activate_server_if_down(self, server: str, verbose: bool = True, timeout: int = 60) -> bool:
        """ Activate server if it is down. Async version.

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
        # c_client = CoreServerConfig(server, self.platform_url, self.user_id)

        if server is None:
            server = self.server_name
        try:
            if verbose:
                print(f"\n\tChecking OMAG Server {server}")
            is_configured = await self._async_is_server_configured()
            if is_configured:
                if verbose:
                    print(f"        OMAG Server {server} is configured")
                active_servers = await self._async_get_active_server_list()
                if server in active_servers:
                    if verbose:
                        print(f"        OMAG Server {server} is active")
                    return True
                else:  # configured but not active, so activate
                    if verbose:
                        print(f"        OMAG Server {server} is being activated")
                    await self._async_activate_server_stored_config(timeout=timeout)
                    return True
            else:
                if verbose:
                    print(f"      OMAG Server {server} needs to be configured")
                return False

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            if verbose:
                print_exception_response(e)
            raise e

    def activate_server_if_down(self, server: str, verbose: bool = True, timeout: int = 60) -> bool:
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
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_activate_server_if_down(server, verbose, timeout))
        return response

    async def _async_activate_servers_on_platform(self, server_list: [str], verbose=False, timeout: int = 60) -> bool:
        """ Activate the servers from the list provided. Async version.
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
        # c_client = CoreServerConfig(server_list[0], self.platform_url, self.user_id)
        num_servers = len(server_list)
        if num_servers > 0:
            for x in server_list:
                if await self._async_is_server_configured(x) is True:
                    if verbose:
                        print(f"\t\tServer {x} is configured and ready to be activated")
                    await self._async_activate_server_stored_config(x, timeout=timeout)
                    if verbose:
                        print(f"\t\t\tServer {x} was activated")
                else:
                    if verbose:
                        print(f"\t\t\tServer {x} is not configured - bypassing")
            return True
        else:
            if verbose:
                print(f"\t\tServer list empty")
            return False

    def activate_servers_on_platform(self, server_list: [str], verbose=False, timeout: int = 60) -> bool:
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
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_activate_servers_on_platform(server_list,
                                                                                    verbose, timeout=timeout))
        return response

    async def _async_activate_platform(self, platform_name: str, hosted_server_names: [str], timeout: int = 60) -> None:
        """ Activate an OMAG Server Platform and start the servers requested. Async version.

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
        This method attempts to activate a platform by checking its status. If the platform is already active and
        running, it prints a message indicating so and activates any hosted servers
        that are down. If the platform is not active, it prints a message indicating so. If there is any exception
        while activating the platform or starting the servers, it prints an error message and the exception response.
        """
        try:
            status = self.get_platform_origin()
            if status:
                print(f"\n\n\t Platform {platform_name} is active and running: \n\t\t{status}")
                print(f"\tWill start the following servers if configured: {hosted_server_names}")
                for server in hosted_server_names:
                    activated = await self._async_activate_server_if_down(server, timeout=timeout)
                    if activated:
                        print(f"\t Started server: {server}")
                return
            else:
                print(f"   {platform_name}, is down - start it before proceeding")
        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print(f"   {platform_name}, is down - start it before proceeding")
            print_exception_response(e)

    def activate_platform(self, platform_name: str, hosted_server_names: [str], timeout: int = 60) -> None:
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
        This method attempts to activate a platform by checking its status. If the platform is already active and
        running, it prints a message indicating so and activates any hosted servers
        that are down. If the platform is not active, it prints a message indicating so. If there is any exception
        while activating the platform or starting the servers, it prints an error message and the exception response.
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_activate_platform(platform_name, hosted_server_names, timeout))


if __name__ == "__main__":
    p = Platform("meow", "https://127.0.0.1:9443", "garygeeke", verify_flag=False)
    response = p.get_known_servers()

    print(response)
