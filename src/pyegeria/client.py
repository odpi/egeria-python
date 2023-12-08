"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This is a simple class to create and manage a connection to an Egeria backend

"""
import os
import sys
import json
import inspect

import requests
from enum import Enum
from requests import Timeout, ConnectTimeout, ConnectionError, Response

from .util_exp import (
    OMAGCommonErrorCode,
    validate_url,
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    is_json, validate_server_name, validate_user_id,
)


class RequestType(Enum):
    """
    Enum class for RequestType containing 4 values - GET, POST, PUT, PATCH, DELETE
    """

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


...

max_paging_size = 100


class Client:
    """
    An abstract class used to establish connectivity for an Egeria Client
    for a particular server, platform and user.

    Attributes:
        server_name : str (required)
            Name of the OMAG server to use
        platform_url : str (required)
            URL of the server platform to connect to
        end_user_id : str
            The identity of the user calling the method - this sets a default optionally used by the methods
            when the user doesn't pass the user_id on a method call.
        user_id : str (required)
            The identity used to connect to the server
        user_pwd : str
            The password used to authenticate the server identity

    Methods:
        __init__(self, server_name: str,
                 platform_url: str,
                 end_user_id: str,
                 user_id: str = None,
                 user_pwd: str = None
                 )
         Initializes the connection - throwing an exception if there is a problem



    """

    json_header = {"Content-Type": "application/json"}

    def __init__(
        self,
        server_name: str,
        platform_url: str,
        user_id: str = None,
        user_pwd: str = None,
        verify_flag: bool = False,
        page_size: int = max_paging_size,
    ):
        self.server_name = None
        self.platform_url = None
        self.user_id = user_id
        self.user_pwd = user_pwd
        self.ssl_verify = verify_flag
        self.page_size = page_size
        api_key = os.environ.get("API_KEY")
        self.headers = {"Content-Type": "application/json", "x-api-key": api_key}

        # class_name = sys._getframe(2).f_code
        # caller_method = sys._getframe(1).f_code.co_name
        calling_frame = inspect.currentframe().f_back
        caller_method = inspect.getframeinfo(calling_frame).function


        v_url = validate_url(platform_url)
        # Todo: Document and cleanup
        # So currently requiring valid server and user names
        if v_url:
            self.platform_url = platform_url
            if validate_server_name(server_name):
                self.server_name = server_name
            if validate_user_id(user_id):
                self.user_id = user_id
            self.session = requests.Session()
        else:
            if platform_url:
                msg = OMAGCommonErrorCode.SERVER_URL_MALFORMED.value[
                    "message_template"
                ].format(platform_url)
                ex_t = OMAGCommonErrorCode.SERVER_URL_MALFORMED
            else:
                msg = OMAGCommonErrorCode.SERVER_URL_NOT_SPECIFIED.value[
                    "message_template"
                ]
            ex_t = OMAGCommonErrorCode.SERVER_URL_MALFORMED
            exc_msg = json.dumps(
                {
                    "class": "VoidResponse",
                    "relatedHTTPCode": 400,
                    "exceptionClassName": "InvalidParameterException",
                    "actionDescription": caller_method,
                    "exceptionErrorMessage": msg,
                    "exceptionErrorMessageId": ex_t.value["message_id"],
                    "exceptionErrorMessageParameters": platform_url,
                    "exceptionSystemAction": ex_t.value["system_action"],
                    "exceptionUserAction": ex_t.value["user_action"],
                    "exceptionProperties": {"endpoint": platform_url},
                }
            )
            raise InvalidParameterException(exc_msg)

    def make_request(
        self, request_type: str, endpoint: str, payload: str = None
    ) -> Response:
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
        # class_name = sys._getframe(2).f_code.co_name
        # caller_method = sys._getframe(1).f_code.co_name
        class_name = __class__.__name__
        calling_frame = inspect.currentframe().f_back
        caller_method = inspect.getframeinfo(calling_frame).function
        try:
            response = ""
            if request_type == "GET":
                response = requests.get(
                    endpoint, timeout=30, params=payload, verify=self.ssl_verify
                )
            elif request_type == "POST":
                response = requests.post(
                    endpoint,
                    headers=self.headers,
                    timeout=30,
                    json=payload,
                    verify=self.ssl_verify,
                )
            elif request_type == "POST-DATA":
                response = requests.post(
                    endpoint,
                    headers=self.headers,
                    timeout=30,
                    data=payload,
                    verify=self.ssl_verify,
                )
            elif request_type == "DELETE":
                response = requests.delete(endpoint, timeout=30, verify=self.ssl_verify)

            if response.status_code in (200, 201):
                if is_json(response.text):
                    return response
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
                raise InvalidParameterException(exc_msg)

            elif response.status_code in (500, 501, 502, 503, 504):
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
                raise PropertyServerException(exc_msg)
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
