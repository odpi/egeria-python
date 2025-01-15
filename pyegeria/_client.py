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
from pyegeria import body_slimmer
import httpx
from httpx import AsyncClient, Response

from pyegeria._exceptions import (
    OMAGCommonErrorCode,
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
)
from pyegeria._globals import (
    max_paging_size,
    enable_ssl_check,
)
from pyegeria._validators import (
    validate_name,
    validate_server_name,
    validate_url,
    validate_user_id,
    is_json,
)

...


class Client:
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
        user_id : str (required)
            The identity used to connect to the server
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
        self.server_name = None
        self.platform_url = None
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
            raise InvalidParameterException("No token returned - request issue")

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
            raise InvalidParameterException("Invalid token source")

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

    def make_request(
        self,
        request_type: str,
        endpoint: str,
        payload: str | dict = None,
        time_out: int = 30,
    ) -> Response | str:
        """Make a request to the Egeria API"""
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_make_request(request_type, endpoint, payload, time_out)
        )
        return response

    async def _async_make_request(
        self,
        request_type: str,
        endpoint: str,
        payload: str | dict = None,
        time_out: int = 30,
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
        :return: Response. Type - JSON Formatted String

        """
        class_name = __class__.__name__
        calling_frame = inspect.currentframe().f_back
        caller_method = inspect.getframeinfo(calling_frame).function

        try:
            response = ""
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

            status_code = response.status_code

            if status_code in (200, 201):
                # Success
                if is_json(response.text):
                    # now look at the response itself and throw an exception if an issue
                    related_code = response.json().get("relatedHTTPCode")
                    if related_code == 200:
                        return response
                    else:
                        exc_message = response.text
                        raise InvalidParameterException(exc_message)
                else:
                    msg = OMAGCommonErrorCode.CLIENT_SIDE_REST_API_ERROR.value[
                        "message_template"
                    ].format(
                        "**invalid JSON response - check parameters**",
                        caller_method,
                        class_name,
                        endpoint,
                        OMAGCommonErrorCode.CLIENT_SIDE_REST_API_ERROR.value[
                            "message_id"
                        ],
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
                                endpoint,
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
                                "endpoint": endpoint,
                                "server": self.server_name,
                                "user_id": self.user_id,
                            },
                        }
                    )
                    raise InvalidParameterException(exc_msg)

            if response.status_code in (400, 401, 403, 404, 405, 415):
                # 4xx are client side errors - 400 bad request, 401 unauthorized
                msg = OMAGCommonErrorCode.CLIENT_SIDE_REST_API_ERROR.value[
                    "message_template"
                ].format(
                    str(response.status_code),
                    caller_method,
                    class_name,
                    endpoint,
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
                            endpoint,
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
                            "endpoint": endpoint,
                            "server": self.server_name,
                            "user_id": self.user_id,
                        },
                    }
                )
                if response.status_code in (401, 403, 405):
                    raise UserNotAuthorizedException(exc_msg)
                else:
                    raise InvalidParameterException(exc_msg)

            elif response.status_code in (500, 501, 502, 503, 504):
                # server errors
                msg = (
                    OMAGCommonErrorCode.EXCEPTION_RESPONSE_FROM_API.value[
                        "message_template"
                    ].format(
                        str(response.status_code),
                        caller_method,
                        endpoint,
                        OMAGCommonErrorCode.EXCEPTION_RESPONSE_FROM_API.value[
                            "message_id"
                        ],
                    )
                    + "==>System reports:'"
                    + response.reason_phrase
                    + "'"
                )
                exc_msg = json.dumps(
                    {
                        "class": "VoidResponse",
                        "relatedHTTPCode": response.status_code,
                        "exceptionClassName": "PropertyServerException",
                        "actionDescription": caller_method,
                        "exceptionErrorMessage": msg,
                        "exceptionErrorMessageId": OMAGCommonErrorCode.CLIENT_SIDE_REST_API_ERROR.value[
                            "message_id"
                        ],
                        "exceptionErrorMessageParameters": [
                            endpoint,
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
                            "endpoint": endpoint,
                            "server": self.server_name,
                            "user_id": self.user_id,
                        },
                    }
                )
                raise PropertyServerException(exc_msg)

        except InvalidParameterException:
            raise
        except UserNotAuthorizedException:
            raise
        except (
            httpx.NetworkError,
            httpx.ProtocolError,
            httpx.HTTPStatusError,
            httpx.TimeoutException,
        ) as e:
            if type(response) is str:
                reason = response
            else:
                reason = response.reason_phrase

            msg = (
                OMAGCommonErrorCode.CLIENT_SIDE_REST_API_ERROR.value[
                    "message_template"
                ].format(
                    e.args[0],
                    caller_method,
                    class_name,
                    endpoint,
                    OMAGCommonErrorCode.CLIENT_SIDE_REST_API_ERROR.value["message_id"],
                )
                + "==>System reports:'"
                + reason
                + "'"
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
                    "exceptionErrorMessageParameters": endpoint,
                    "exceptionSystemAction": OMAGCommonErrorCode.CLIENT_SIDE_REST_API_ERROR.value[
                        "system_action"
                    ],
                    "exceptionUserAction": OMAGCommonErrorCode.CLIENT_SIDE_REST_API_ERROR.value[
                        "user_action"
                    ],
                    "exceptionProperties": {"endpoint": endpoint},
                }
            )
            raise InvalidParameterException(exc_msg)

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
            return result.json().get("guid", "No elements found")

        try:
            view_server = self.view_server
        except AttributeError:
            view_server = os.environ.get("EGERIA_VIEW_SERVER", "view-server")

        if (not qualified_name) and display_name:
            if (tech_type) and (property_name == "qualifiedName"):
                name = f"{tech_type}:{display_name}"
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
                return result.json().get("guid", "No elements found")
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
                return result.json().get("guid", "No elements found")
        else:
            raise InvalidParameterException(
                "Neither server_guid nor server_name were provided - please provide."
            )

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


if __name__ == "__main__":
    print("Main-__client")
