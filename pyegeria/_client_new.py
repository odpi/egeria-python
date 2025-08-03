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
import re
from datetime import datetime

import httpcore
import httpx
# from venv import logger
from loguru import logger

from httpx import AsyncClient, Response, HTTPStatusError

from pyegeria.utils import body_slimmer
from pyegeria._exceptions_new import (
    PyegeriaException, PyegeriaAPIException, PyegeriaConnectionException, PyegeriaInvalidParameterException,
    PyegeriaNotFoundException, PyegeriaUnknownException, PyegeriaErrorCode,
    PyegeriaUnauthorizedException, PyegeriaClientException
    )
from pyegeria._globals import enable_ssl_check, max_paging_size, NO_ELEMENTS_FOUND
from pyegeria._validators import (
    is_json,
    validate_name,
    validate_server_name,
    validate_url,
    validate_user_id,
)

...


class Client2:
    """
    An abstract class used to establish connectivity for an Egeria Client
    for a particular server, platform and user.

    Attributes
    ----------
        server_name : str (required)
            Name of the OMAG server to use
        platform_url : str (required)
            URL of the server platform to connect to
        user_id : str
            The identity of the user calling the method - this sets a default optionally used by the methods
            when the user doesn't pass the user_id on a method call.
        user_pwd : str
            The password used to authenticate the server identity

    Methods
    -------
        create_egeria_bearer_token(user_Id: str, password: str = None) -> str
           Create a bearer token using the simple Egeria token service - store the bearer token in the object instance.

        refresh_egeria_bearer_token()-> None
            Refresh the bearer token using the attributes of the object instance.

        set_bearer_token(token: str) -> None
            Set the bearer token attribute in the object instance - used when the token is generated
            by an external service.

        get_token() -> str
            Retrieve the bearer token.

        make_request(request_type: str, endpoint: str, payload: str | dict = None,
                    time_out: int = 30) -> Response
            Make an HTTP Restful request and handle potential errors and exceptions.

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
        self, user_id: str = None, password: str = None
    ) -> str:
        """Create and set an Egeria Bearer Token for the user. Async version
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
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
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
            validate_user_id(self.user_id)
            user_id = self.user_id
        if password is None:
            validate_name(self.user_pwd)
            password = self.user_pwd

        url = f"{self.platform_url}/api/token"
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
        """Create and set an Egeria Bearer Token for the user
        Parameters
        ----------
        user_id : str
            The user id to authenticate with.
        password : str
            The password for the user.

        Returns
        -------
        token
            The bearer token for the specified user.

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
        `create_egeria_bearer_token` method to create a new bearer token. Otherwise,
        it raises an `InvalidParameterException`.

        Parameters:

        Returns:
            None

        Raises:
            InvalidParameterException: If the token source is invalid.
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


    def refresh_egeria_bearer_token(self) -> None:
        """
        Refreshes the Egeria bearer token.

        This method is used to refresh the bearer token used for authentication with Egeria. It checks if the token
        source is 'Egeria', and if the user ID and password are valid. If all conditions are met, it calls the
        `create_egeria_bearer_token` method to create a new bearer token. Otherwise,
        it raises an `InvalidParameterException`.

        Parameters:

        Returns:
            None

        Raises:
            InvalidParameterException: If the token source is invalid.
            PropertyServerException
                Raised by the server when an issue arises in processing a valid request
            NotAuthorizedException
                The principle specified by the user_id does not have authorization for the requested action
        """
        loop = asyncio.get_event_loop()
        token = loop.run_until_complete(self._async_refresh_egeria_bearer_token())
        return token

    def set_bearer_token(self, token: str) -> None:
        """Retrieve and set a Bearer Token
        Parameters
        ----------
        token: str
        A bearer token supplied to the method.

        Returns
        -------
        None
            This method does not return anything.

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
        This routine sets the bearer token for the current object. The user is responsible for providing the token.

        """
        validate_name(token)
        self.headers["Authorization"] = f"Bearer {token}"
        self.text_headers["Authorization"] = f"Bearer {token}"

    def get_token(self) -> str:
        """Retrieve and return the bearer token"""
        return self.text_headers["Authorization"]

    def get_platform_origin(self):
        """Validate platform connectivity"""
        origin_url = f"{self.platform_url}/open-metadata/platform-services/users/{self.user_id}/server-platform/origin"
        response = self.make_request("GET", origin_url, is_json=False)
        if response.status_code == 200:
            logger.success(f"Got response from {origin_url}\n Response: {response.text}")
            if response.text.split()[0] == "Egeria":
                return True
            else:
                return False
        else:
            logger.info(f"Got response from {origin_url}\n status_code: {response.status_code}")


    # @logger.catch
    def make_request(
        self,
        request_type: str,
        endpoint: str,
        payload: str | dict = None,
        time_out: int = 30,
        is_json: bool = True,
        ) -> Response | str:
        """Make a request to the Egeria API."""
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                coro = self._async_make_request(request_type, endpoint, payload, time_out, is_json)
                return asyncio.run_coroutine_threadsafe(coro, loop).result()
            else:
                return loop.run_until_complete(self._async_make_request(request_type, endpoint, payload, time_out, is_json))
        except RuntimeError:
            # No running loop exists; run the coroutine
            return asyncio.run(self._async_make_request(request_type, endpoint, payload, time_out, is_json))

    async def _async_make_request(
        self,
        request_type: str,
        endpoint: str,
        payload: str | dict = None,
        time_out: int = 30,
        is_json: bool = True,
    ) -> Response | str:
        """Make a request to the Egeria API - Async Version
        Function to make an API call via the self.session Library. Raise an exception if the HTTP response code
        is not 200/201. IF there is a REST communication exception, raise InvalidParameterException.

        :param request_type: Type of Request.
               Supported Values - GET, POST, (not PUT, PATCH, DELETE).
               Type - String
        :param endpoint: API Endpoint. Type - String
        :param payload: API Request Parameters or Query String.
               Type - String or Dict
        :param time_out: Timeout in seconds. Type - Integer
        :param is_json: Whether the payload is JSON or not. Type - Boolean
        :return: Response. Type - JSON Formatted String

        """
        context: dict = {}
        context['class name'] = __class__.__name__
        context['caller method'] = inspect.currentframe().f_back.f_code.co_name
        response: Response

        try:
            if request_type == "GET":
                response = await self.session.get(
                    endpoint, params=payload, headers=self.headers, timeout=time_out
                )

            elif request_type == "POST":
                if payload is None:
                    response = await self.session.post(
                        endpoint, headers=self.headers, timeout=time_out
                    )
                elif type(payload) is str:
                    response = await self.session.post(
                        endpoint,
                        headers=self.text_headers,
                        data=payload,
                        timeout=time_out,
                    )
                else:
                    response = await self.session.post(
                        endpoint, headers=self.headers, json=payload, timeout=time_out
                    )

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

        except (httpx.TimeoutException, httpcore.ConnectError, httpx.ConnectError) as e:
            additional_info = {"endpoint": endpoint, "error_kind": "connection"}
            raise PyegeriaConnectionException(context, additional_info, e)

        except (HTTPStatusError, httpx.HTTPStatusError, httpx.RequestError) as e:
            # context["caught_exception"] = e
            # context['HTTPStatusCode'] = e.response.status_code
            additional_info = {"userid": self.user_id}
            raise PyegeriaClientException(response, context, additional_info, e)
        #
        # except json.JSONDecodeError as e:
        #     # context["caught_exception"] = e
        #     # context['HTTPStatusCode'] = e.response.status_code
        #     additional_info = {"userid": self.user_id}
        #     raise PyegeriaClientException(response, context, additional_info )
        #
        # except PyegeriaAPIException as e:
        #     raise PyegeriaAPIException(response, context, additional_info=None)

        except Exception as e:
            additional_info = {"userid": self.user_id}
            if 'response' in locals() and response is not None:
                logger.error(f"Response error with code {response.status_code}")
            else:
                logger.error("Response object not available due to error")
            raise PyegeriaUnknownException(None, context, additional_info, e)

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
                    response, context,e = e
                    )



    def build_global_guid_lists(self) -> None:
        global template_guids, integration_guids

        self.create_egeria_bearer_token(self.user_id, self.user_pwd)
        # get all technology types
        url = (
            f"{self.platform_url}/servers/{self.server_name}/api/open-metadata/automated-curation/technology-types/"
            f"by-search-string?startFrom=0&pageSize=0&startsWith=false&"
            f"endsWith=false&ignoreCase=true"
        )
        body = {"filter": ""}

        response = self.make_request("POST", url, body)
        tech_types = response.json().get("elements", "no tech found")
        if type(tech_types) is list:
            for tech_type in tech_types:
                # get tech type details
                display_name = tech_type["name"]

                url = f"{self.platform_url}/servers/{self.server_name}/api/open-metadata/automated-curation/technology-types/by-name"
                body = {"filter": display_name}
                response = self.make_request("POST", url, body)
                details = response.json().get("element", "no type found")
                if type(details) is str:
                    continue
                # get templates and update the template_guids global
                templates = details.get("catalogTemplates", "Not Found")
                if type(templates) is str:
                    template_guids[display_name] = None
                else:
                    for template in templates:
                        template_name = template.get("name", None)
                        template_guid = template["relatedElement"]["guid"]
                        template_guids[template_name] = template_guid
                        # print(f"Added {template_name} template with GUID {template_guids[template_name]}")

                # Now find the integration connector guids
                resource_list = details.get("resourceList", " ")
                if type(resource_list) is str:
                    integration_guids[display_name] = None
                else:
                    for resource in resource_list:
                        resource_guid = resource["relatedElement"]["guid"]
                        resource_type = resource["relatedElement"]["type"]["typeName"]
                        if resource_type == "IntegrationConnector":
                            integration_guids[display_name] = resource_guid
                            # print(f"Added {display_name} integration connector with GUID {integration_guids[display_name]}")

    async def __async_get_guid__(
        self,
        guid: str = None,
        display_name: str = None,
        property_name: str = "qualifiedName",
        qualified_name: str = None,
        tech_type: str = None,
    ) -> str:
        """Helper function to return a server_guid - one of server_guid, qualified_name or display_name should
        contain information. If all are None, an exception will be thrown. If all contain
        values, server_guid will be used first, followed by qualified_name.  If the tech_type is supplied and the
        property_name is qualifiedName then the display_name will be pre-pended with the tech_type name to form a
        qualifiedName.

        An InvalidParameter Exception is thrown if multiple matches
        are found for the given property name. If this occurs, use a qualified name for the property name.
        Async version.
        """

        if guid:
            return guid

        if qualified_name:
            body = {
                "class": "NameRequestBody",
                "name": qualified_name,
                "namePropertyName": "qualifiedName",
                "forLineage": False,
                "forDuplicateProcessing": False,
                "effectiveTime": None,
            }
            url = (
                f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/classification-manager/"
                f"elements/guid-by-unique-name?forLineage=false&forDuplicateProcessing=false"
            )

            result = await self._async_make_request("POST", url, body_slimmer(body))
            return result.json().get("guid", NO_ELEMENTS_FOUND)

        try:
            view_server = self.view_server
        except AttributeError:
            view_server = os.environ.get("EGERIA_VIEW_SERVER", "view-server")

        if (not qualified_name) and display_name:
            if (tech_type) and (property_name == "qualifiedName"):
                name = f"{tech_type}::{display_name}"
                body = {
                    "class": "NameRequestBody",
                    "name": name,
                    "namePropertyName": property_name,
                    "forLineage": False,
                    "forDuplicateProcessing": False,
                    "effectiveTime": None,
                }
                url = (
                    f"{self.platform_url}/servers/{view_server}/api/open-metadata/classification-manager/"
                    f"elements/guid-by-unique-name?forLineage=false&forDuplicateProcessing=false"
                )

                result = await self._async_make_request("POST", url, body_slimmer(body))
                return result.json().get("guid", NO_ELEMENTS_FOUND)
            else:
                body = {
                    "class": "NameRequestBody",
                    "name": display_name,
                    "namePropertyName": property_name,
                    "forLineage": False,
                    "forDuplicateProcessing": False,
                    "effectiveTime": None,
                }
                url = (
                    f"{self.platform_url}/servers/{view_server}/api/open-metadata/classification-manager/"
                    f"elements/guid-by-unique-name?forLineage=false&forDuplicateProcessing=false"
                )

                result = await self._async_make_request("POST", url, body_slimmer(body))
                return result.json().get("guid", NO_ELEMENTS_FOUND)
        else:
            additional_info = {"reason": "Neither server_guid nor server_name were provided - please provide.",
                                "parameters": (f"GUID={guid}, display_name={display_name}, property_name={property_name},"
                                              f"qualified_name={qualified_name}, tech_type={tech_type}")
                              }
            raise PyegeriaInvalidParameterException(None, None, additional_info)

    def __get_guid__(
        self,
        guid: str = None,
        display_name: str = None,
        property_name: str = "qualifiedName",
        qualified_name: str = None,
        tech_type: str = None,
    ) -> str:
        """Helper function to return a server_guid - one of server_guid, qualified_name or display_name should
        contain information. If all are None, an exception will be thrown. If all contain
        values, server_guid will be used first, followed by qualified_name.  If the tech_type is supplied and the
        property_name is qualifiedName then the display_name will be pre-pended with the tech_type name to form a
        qualifiedName.

        An InvalidParameter Exception is thrown if multiple matches
        are found for the given property name. If this occurs, use a qualified name for the property name.
        Async version.
        """
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            self.__async_get_guid__(
                guid, display_name, property_name, qualified_name, tech_type
            )
        )
        return result

    def __create_qualified_name__(self, type: str, display_name: str, local_qualifier: str = None,
                                  version_identifier: str = None) -> str:
        """Helper function to create a qualified name for a given type and display name.
           If present, the local qualifier will be prepended to the qualified name."""
        EGERIA_LOCAL_QUALIFIER = os.environ.get("EGERIA_LOCAL_QUALIFIER", local_qualifier)
        # display_name = re.sub(r'\s','-',display_name.strip()) # This changes spaces between words to -; removing
        if display_name is None:
            additional_info = {"reason": "Display name is missing - please provide.",}
            raise PyegeriaInvalidParameterException(additional_info=additional_info)
        q_name = f"{type}::{display_name.strip()}"
        if EGERIA_LOCAL_QUALIFIER:
            q_name = f"{EGERIA_LOCAL_QUALIFIER}::{q_name}"
        if version_identifier:
            q_name = f"{q_name}::{version_identifier}"
        return q_name


    async def _async_get_element_by_guid_(self, element_guid: str) -> dict | str:
        """
        Simplified, internal version of get_element_by_guid found in Classification Manager.
        Retrieve an element by its guid.  Async version.

        Parameters
        ----------
        element_guid: str
            - unique identifier for the element

        Returns
        -------
        dict | str
            Returns a string if no element found; otherwise a dict of the element.

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """

        body = {
            "class": "EffectiveTimeQueryRequestBody",
            "effectiveTime": None,
        }

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/classification-manager/elements/"
               f"{element_guid}?forLineage=false&forDuplicateProcessing=false")

        response: Response = await self._async_make_request("POST", url, body_slimmer(body))

        elements = response.json().get("element", NO_ELEMENTS_FOUND)

        return elements


if __name__ == "__main__":
    print("Main-__client")