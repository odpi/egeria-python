"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This is a simple class to create and manage a connection to an Egeria backend. It is the Superclass for the
different client capabilities. It also provides the common methods used to make restful requests to Egeria.

"""
import inspect
import json
import os
import requests
from requests import Response
from enum import Enum
from pyegeria._globals import max_paging_size

from pyegeria._exceptions import (
    OMAGCommonErrorCode,
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
)
from pyegeria._validators import (
    validate_name,
    validate_server_name,
    validate_url,
    validate_user_id,
    is_json
)


# class RequestType(Enum):
#     """
#     Enum class for RequestType containing 4 values - GET, POST, PUT, PATCH, DELETE
#     """
#
#     GET = "GET"
#     POST = "POST"
#     PUT = "PUT"
#     PATCH = "PATCH"
#     DELETE = "DELETE"


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
        verify_flag: bool = False,
        api_key: str = None,
        page_size: int = max_paging_size,
        token: str = None,
        token_src: str = None,
    ):
        self.server_name = None
        self.platform_url = None
        self.user_id = user_id
        self.user_pwd = user_pwd
        self.ssl_verify = verify_flag
        self.page_size = page_size
        self.token_src = token_src
        self.token = token

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
            api_key = os.environ.get("API_KEY",None)
        self.api_key = api_key

        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            }
        self.text_headers = {
            "Content-Type": "text/plain",
            "x-api-key": api_key,
            }
        if token is None:
            validate_user_id(user_id)
            self.user_id = user_id
        else:
            self.headers["Authorization"] = f"Bearer {token}"
            self.text_headers["Authorization"] = f"Bearer {token}"

        calling_frame = inspect.currentframe().f_back
        caller_method = inspect.getframeinfo(calling_frame).function

        v_url = validate_url(platform_url)

        if v_url:
            self.platform_url = platform_url
            if validate_server_name(server_name):
                self.server_name = server_name
            self.session = requests.Session()

    def create_egeria_bearer_token(self, user_Id: str, password: str = None) -> str:
        """ Create and set an Egeria Bearer Token for the user
        Parameters
        ----------
        user_Id : str
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
        validate_name(user_Id)
        validate_name(password)

        url = f"{self.platform_url}/api/token"
        data = {
            "userId": user_Id,
            "password": password
        }
        response = self.session.post(url, json=data, headers=self.headers, verify=self.ssl_verify, timeout=30)
        # response = self.make_request("POST", url, data)
        token = response.text
        if token:
            self.token_src = 'Egeria'
            self.headers["Authorization"] = f"Bearer {token}"
            self.text_headers["Authorization"] = f"Bearer {token}"
            return token
        else:
            raise InvalidParameterException("No token returned - request issue")

    def refresh_egeria_bearer_token(self)-> None:
        if (self.token_src == 'Egeria') and validate_user_id(self.user_id) and validate_name(self.user_pwd):
            self.create_egeria_bearer_token(self.user_id, self.user_pwd)
        else:
            raise InvalidParameterException("Invalid token source")
        # todo - should I turn the above into a regular exception?

    def set_bearer_token(self, token: str) -> None:
        """ Retrieve and set a Bearer Token
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
        return self.text_headers["Authorization"]

    def make_request(
        self, request_type: str, endpoint: str, payload: str | dict = None, time_out: int = 30) -> Response:
        """
        Function to make an API call via the Requests Library. Raise an exception if the HTTP response code
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
                response = requests.get(
                    endpoint, params=payload, verify=self.ssl_verify, headers=self.headers
                )
            elif request_type == "POST":
                if type(payload) is str:
                    response = requests.post(
                        endpoint,
                        headers=self.text_headers,
                        timeout=time_out,
                        data=payload,
                        verify=self.ssl_verify,
                )
                else:
                    response = requests.post(
                        endpoint,
                        headers=self.headers,
                        timeout=time_out,
                        json=payload,
                        verify=self.ssl_verify,
                    )
            elif request_type == "POST-DATA":
                response = requests.post(
                    endpoint,
                    headers=self.headers,
                    timeout=time_out,
                    data=payload,
                    verify=self.ssl_verify,
                )
            elif request_type == "DELETE":
                response = requests.delete(endpoint, timeout=30, verify=self.ssl_verify, headers=self.headers)
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

            if response.status_code in (400, 401, 403, 404, 405):
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
                if response.status_code in (401,403,405):
                    raise UserNotAuthorizedException(exc_msg)
                else:
                    raise InvalidParameterException(exc_msg)

            elif response.status_code in (500, 501, 502, 503, 504):
                # server errors
                msg = OMAGCommonErrorCode.EXCEPTION_RESPONSE_FROM_API.value[
                    "message_template"
                ].format(
                    str(response.status_code),
                    caller_method,
                    endpoint,
                    OMAGCommonErrorCode.EXCEPTION_RESPONSE_FROM_API.value["message_id"],
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
            requests.ConnectionError,
            requests.ConnectTimeout,
            requests.HTTPError,
            requests.RequestException,
            requests.Timeout,
            # InvalidParameterException
            # HTTPSConnectionPool,
        ) as e:
            msg = OMAGCommonErrorCode.CLIENT_SIDE_REST_API_ERROR.value[
                "message_template"
            ].format(
                e.args[0],
                caller_method,
                class_name,
                endpoint,
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



if __name__ == "__main__":
    try:
        connection = Client(
            "active-metadata-store", "https://127.0.0.1:9443", "garygeeke", "foo"
        )
    except Exception as e:
        print(e)
