"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This is a simple class to create and manage a connection to an Egeria backend. It is the Superclass for the
different client capabilities. It also provides the common methods used to make restful self.session to Egeria.

"""

import asyncio
import inspect
import json
import os

import httpcore
import httpx
from httpx import AsyncClient, Response, HTTPStatusError
from loguru import logger

from pyegeria.core._exceptions import (
    PyegeriaAPIException, PyegeriaConnectionException, PyegeriaInvalidParameterException,
    PyegeriaUnknownException, PyegeriaClientException, PyegeriaTimeoutException
)
from pyegeria.core._globals import enable_ssl_check, max_paging_size
from pyegeria.core._validators import (
    validate_name,
    validate_server_name,
    validate_url,
    validate_user_id,
)

...


class BaseServerClient:
    """
    An abstract class used to establish connectivity for an Egeria Client
    for a particular server, platform and user. This is a base client that more functional clients inherit from.

    Attributes
    ----------
    server_name : str
        Name of the OMAG server to use
    platform_url : str
        URL of the server platform to connect to
    user_id : str
        The identity of the user calling the method - this sets a default optionally used by the methods
        when the user doesn't pass the user_id on a method call.
    user_pwd : str
        The password used to authenticate the server identity
    page_size : int
        The default page size for paged requests.
    token : str
        An optional bearer token for authentication.
    token_src : str
        The source of the bearer token (e.g., 'Egeria').
    api_key : str
        An optional API key for authentication.

    """

    json_header = {"Content-Type": "application/json"}

    def __init__(
            self,
            server_name: str,
            platform_url: str,
            user_id: str = None,
            user_pwd: str = None,
            token: str = None,
            token_src: str = None,
            api_key: str = None,
            page_size: int = max_paging_size,
    ):
        self.server_name = validate_server_name(server_name)
        self.platform_url = validate_url(platform_url)
        self.user_id = user_id
        self.user_pwd = user_pwd
        self.page_size = page_size
        self.token_src = token_src
        self.token = token
        self.exc_type = None
        self.exc_value = None
        self.exc_tb = None

        #
        #           I'm commenting this out since you should only have to use tokens if you want - just have to
        #           create or set the token with the appropriate methods as desired.
        # if token is None:
        #     token = os.environ.get("Egeria_Bearer_Token", None)
        #     if token is None: # No token found - so make one
        #         self.create_egeria_bearer_token(self.user_id, self.user_pwd)
        #     else:
        #         self.token = token

        if api_key is None:
            api_key = os.environ.get("API_KEY", None)
        self.api_key = api_key

        self.headers = {
            "Content-Type": "application/json",
        }
        self.text_headers = {
            "Content-Type": "text/plain",
        }
        if self.api_key is not None:
            self.headers["X-Api-Key"] = self.api_key
            self.text_headers["X-Api-Key"] = self.api_key

        if token is not None:
            self.headers["Authorization"] = f"Bearer {token}"
            self.text_headers["Authorization"] = f"Bearer {token}"

        v_url = validate_url(platform_url)

        if v_url:
            self.platform_url = platform_url
            if validate_server_name(server_name):
                self.server_name = server_name
            self.session = AsyncClient(verify=enable_ssl_check)
        self.command_root: str = f"{self.platform_url}/servers/{self.server_name}/api/open-metadata/"

        try:
            result = self.check_connection()
            logger.debug(f"client initialized, platform origin is: {result}")
        except PyegeriaConnectionException as e:
            raise

    async def _async_check_connection(self) -> str:
        """Check if the connection is working. Async version.

        Returns
        -------
        str
            The platform origin string if reachable, otherwise an empty string.

        Raises
        ------
        PyegeriaConnectionException
            If the connection to the platform fails.
        """
        try:
            response = await self.async_get_platform_origin()
            return response

        except PyegeriaConnectionException as e:
            raise
    def check_connection(self) -> str:
        """Check if the connection is working.

        Returns
        -------
        str
            The platform origin string if reachable, otherwise an empty string.

        Raises
        ------
        PyegeriaConnectionException
            If the connection to the platform fails.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_check_connection())
        return response

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.aclose()
        if exc_type is not None:
            self.exc_type = exc_type
            self.exc_val = exc_val
            self.exc_tb = exc_tb

        return False  # allows exceptions to propagate

    def __str__(self):
        return (f"EgeriaClient(server_name={self.server_name}, platform_url={self.platform_url}, "
                f"user_id={self.user_id}, page_size={self.page_size})")

    async def _async_close_session(self) -> None:
        """Close the session"""
        await self.session.aclose()

    def close_session(self) -> None:
        """Close the session"""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_close_session())
        return

    async def _async_create_egeria_bearer_token(
            self, user_id: str , password: str
    ) -> str:
        """Create and set an Egeria Server Bearer Token for the user. Async version
        Parameters
        ----------
        user_id : str, opt
            The user id to authenticate with. If None, then user_id from class instance used.
        password : str, opt
            The password for the user. If None, then user_pwd from class instance is used.

        Returns
        -------
        token
            The bearer token for the specified user.

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
        Notes
        -----
        This routine creates a new bearer token for the user and updates the object with it.
        It uses Egeria's mechanisms to create a token. This is useful if an Egeria token expires.
        A bearer token from another source can be set with the set_bearer_token() method.

        """
        if user_id is None:
            user_id = self.user_id
        if password is None:
            password = self.user_pwd

        url = f"{self.platform_url}/servers/{self.server_name}/api/token"
        data = {"userId": user_id, "password": password}
        async with AsyncClient(verify=enable_ssl_check) as client:
            try:
                response = await client.post(url, json=data, headers=self.headers)
                token = response.text
            except httpx.HTTPError as e:
                print(e)
                return "FAILED"

        if token:
            self.token_src = "Egeria"
            self.headers["Authorization"] = f"Bearer {token}"
            self.text_headers["Authorization"] = f"Bearer {token}"
            return token
        else:
            additional_info = {"reason": "No token returned - request issue?"}
            raise PyegeriaInvalidParameterException(None, None, additional_info)

    def create_egeria_bearer_token(
            self, user_id: str = None, password: str = None
    ) -> str:
        """Create and set an Egeria Server Bearer Token for the user
        Parameters
        ----------
        user_id : str, optional
            The user id to authenticate with. If None, then user_id from class instance used.
        password : str, optional
            The password for the user. If None, then user_pwd from class instance is used.

        Returns
        -------
        token
            The server bearer token for the specified user.

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
        Notes
        -----
        This routine creates a new bearer token for the user and updates the object with it.
        It uses Egeria's mechanisms to create a token. This is useful if an Egeria token expires.
        A bearer token from another source can be set with the set_bearer_token() method.

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_egeria_bearer_token(user_id, password)
        )
        return response

    async def _async_refresh_egeria_bearer_token(self) -> str:
        """
        Refreshes the Egeria bearer token. Async version.

        This method is used to refresh the bearer token used for authentication with Egeria. It checks if the token
        source is 'Egeria', and if the user ID and password are valid. If all conditions are met, it calls the
        `create_egeria_bearer_token` method to create a new bearer token.

        Returns
        -------
        str
            The new platform bearer token.

        Raises
        ------
        PyegeriaInvalidParameterException
            If the token source is invalid or user credentials are missing.
        """
        if (
                (self.token_src == "Egeria")
                and validate_user_id(self.user_id)
                and validate_name(self.user_pwd)
        ):
            token = await self._async_create_egeria_bearer_token(
                self.user_id, self.user_pwd
            )
            return token
        else:
            additional_info = {"reason": "Invalid token source"}
            raise PyegeriaInvalidParameterException(None, None, additional_info)

    def refresh_egeria_bearer_token(self) -> str:
        """
        Refreshes the Egeria bearer token.

        This method is used to refresh the bearer token used for authentication with Egeria. It checks if the token
        source is 'Egeria', and if the user ID and password are valid. If all conditions are met, it calls the
        `create_egeria_bearer_token` method to create a new bearer token.

        Returns
        -------
        str
            The new platform bearer token.

        Raises
        ------
        PyegeriaInvalidParameterException
            If the token source is invalid or user credentials are missing.
        PyegeriaAPIException
            Raised by the server when an issue arises in processing a valid request
        PyegeriaNotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action
        """
        loop = asyncio.get_event_loop()
        token = loop.run_until_complete(self._async_refresh_egeria_bearer_token())
        return token

    def set_bearer_token(self, token: str) -> None:
        """Set the Bearer Token for the client.

        Parameters
        ----------
        token : str
            A bearer token supplied to the method.

        Raises
        ------
        PyegeriaInvalidParameterException
            If the token is invalid.
        """
        validate_name(token)
        self.headers["Authorization"] = f"Bearer {token}"
        self.text_headers["Authorization"] = f"Bearer {token}"

    def get_token(self) -> str:
        """Retrieve and return the current bearer token.

        Returns
        -------
        str
            The current bearer token.
        """
        return self.text_headers["Authorization"]

    async def async_get_platform_origin(self) -> str:
        """Return the platform origin string if reachable. Async version.

        Returns
        -------
        str
            The platform origin string if reachable, otherwise an empty string.
        """
        origin_url = f"{self.platform_url}/api/about"
        response = await self._async_make_request("GET", origin_url, is_json=False)
        if response.status_code == 200:
            text = response.text.strip()
            logger.debug(f"Got response from {origin_url}\n Response: {text}")
            return text
        else:
            logger.debug(f"Got response from {origin_url}\n status_code: {response.status_code}")
            return ""


    def get_platform_origin(self) -> str:
        """Return the platform origin string if reachable.

        Returns
        -------
        str
            The platform origin string if reachable, otherwise an empty string.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self.async_get_platform_origin())
        return response

    # @logger.catch
    def make_request(
            self,
            request_type: str,
            endpoint: str,
            payload: str | dict = None,
            time_out: int = 30,
            is_json: bool = True,
            params: dict | None = None
    ) -> Response | str:
        """Make a synchronous request to the Egeria API.

        Parameters
        ----------
        request_type : str
            The type of HTTP request (e.g., 'GET', 'POST').
        endpoint : str
            The API endpoint URL.
        payload : str | dict, optional
            The request payload.
        time_out : int, optional
            The timeout for the request in seconds (default is 30).
        is_json : bool, optional
            Whether the payload is in JSON format (default is True).
        params : dict, optional
            Query parameters for the request.

        Returns
        -------
        Response | str
            The response from the API.

        Raises
        ------
        PyegeriaException
            If the request fails.
        """
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                coro = self._async_make_request(request_type, endpoint, payload, time_out, is_json, params)
                return asyncio.run_coroutine_threadsafe(coro, loop).result()
            else:
                return loop.run_until_complete(
                    self._async_make_request(request_type, endpoint, payload, time_out, is_json, params))
        except RuntimeError:
            # No running loop exists; run the coroutine
            return asyncio.run(self._async_make_request(request_type, endpoint, payload, time_out, is_json, params))


    async def _async_make_request(
            self,
            request_type: str,
            endpoint: str,
            payload: str | dict = None,
            time_out: int = 30,
            is_json: bool = True,
            params: dict | None = None
    ) -> Response | str:
        """Make an asynchronous request to the Egeria API.

        Parameters
        ----------
        request_type : str
            The type of HTTP request (e.g., 'GET', 'POST').
        endpoint : str
            The API endpoint URL.
        payload : str | dict, optional
            The request payload.
        time_out : int, optional
            The timeout for the request in seconds (default is 30).
        is_json : bool, optional
            Whether the payload is in JSON format (default is True).
        params : dict, optional
            Query parameters for the request.

        Returns
        -------
        Response | str
            The response from the API.

        Raises
        ------
        PyegeriaAPIException
            If the server returns an error.
        PyegeriaConnectionException
            If there is a connection issue.
        PyegeriaInvalidParameterException
            If the request parameters are invalid.
        """
        context: dict = {}
        context['class name'] = __class__.__name__
        context['caller method'] = inspect.currentframe().f_back.f_code.co_name
        response: Response = None  # Initialize to None to avoid UnboundLocalError

        try:
            if request_type == "GET":
                response = await self.session.get(
                    endpoint, params=params, headers=self.headers, timeout=time_out,
                )

            elif request_type == "POST":
                if payload is None:
                    response = await self.session.post(
                        endpoint, headers=self.headers, timeout=time_out, params = params
                    )
                elif type(payload) is dict:
                    response = await self.session.post(
                        endpoint, json=payload, headers=self.headers, timeout=time_out
                    )
                elif type(payload) is str:
                    response = await self.session.post(
                        endpoint,
                        headers=self.headers,
                        content=payload,
                        timeout=time_out,
                        params=params
                    )
                else:
                    raise TypeError(f"Invalid payload type {type(payload)}")


            elif request_type == "POST-DATA":
                if True:
                    response = await self.session.post(
                        endpoint, headers=self.headers, data=payload, timeout=time_out
                    )
            elif request_type == "DELETE":
                if True:
                    response = await self.session.delete(
                        endpoint, headers=self.headers, timeout=time_out
                    )
            response.raise_for_status()

            status_code = response.status_code

        except httpx.TimeoutException as e:
            additional_info = {
                "endpoint": endpoint,
                "error_kind": "timeout",
                "timeout_seconds": time_out,
            }
            raise PyegeriaTimeoutException(context, additional_info, e)

        except (httpcore.ConnectError, httpx.ConnectError) as e:
            additional_info = {"endpoint": endpoint, "error_kind": "connection"}
            raise PyegeriaConnectionException(context, additional_info, e)

        except (HTTPStatusError, httpx.HTTPStatusError, httpx.RequestError) as e:
            additional_info = {"userid": self.user_id}
            if response is not None:
                additional_info["reason"] = response.text

            raise PyegeriaClientException(response, context, additional_info, e)

        except Exception as e:
            additional_info = {"userid": self.user_id}
            if response is not None:
                logger.error(f"Response error with code {response.status_code}")
            else:
                logger.error("Response object not available due to error")
            raise PyegeriaUnknownException(response, context, additional_info, e)

        if status_code in (200, 201):
            try:
                if is_json:
                    json_response = response.json()
                    related_http_code = json_response.get("relatedHTTPCode", 0)
                    if related_http_code == 200:
                        return response
                    else:
                        raise PyegeriaAPIException(response, context, additional_info=None)

                else:  # Not JSON - Text?
                    return response


            except json.JSONDecodeError as e:
                logger.error("Failed to decode JSON response from %s: %s", endpoint, response.text,
                             exc_info=True)
                context['caught_exception'] = e
                raise PyegeriaInvalidParameterException(
                    response, context, e=e
                )
