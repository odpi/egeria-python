"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Definitions, utilities and exceptions in support of the Egeria Python Client package.

"""



from enum import Enum
import json
from json import JSONDecodeError
import requests
import validators
import sys
import inspect


comment_types = (
    "ANSWER",
    "OTHER",
    "QUESTION",
    "STANDARD_COMMENT",
    "SUGGESTION",
    "USAGE_EXPERIENCE",
)
star_ratings = (
    "FIVE_STARS",
    "FOUR_STARS",
    "NO_RECOMMENDATION",
    "ONE_STAR",
    "THREE_STARS",
    "TWO_STARS",
)

"""

The following definitions are used in creating Exception messages. 
They miror similar definitions in the Egeria core. 
Note that not all of the definitions are currently used - they merely serve as placeholders for future extensions.

"""


class EgeriaErrorCode(Enum):
    def __str__(self):
        return (
            "http_error_code="
            + self.value["http_error_code"]
            + "messageId="
            + self.value["message_id"]
            + ", message="
            + self.value["message_template"]
            + ", systemAction="
            + self.value["system_action"]
            + ", userAction="
            + self.value["user_action"]
        )


class OMAGServerInstanceErrorCode(EgeriaErrorCode):
    """
    OMAG-MULTI-TENANT-400-001 - The OMAG server {0} has been configured with a bad connection to its security connector.
    rror message is {1}. Connection is {2}
    """

    BAD_SERVER_SECURITY_CONNECTION = dict(
        https_error_code="400",
        message_id="OMAG-MULTI-TENANT-400-001",
        message_template="The OMAG server {0} has been configured with a bad connection to its security connector."
        + " Error message is {1}. Connection is {2}",
        system_action="The system is unable to validate the users issuing requests to this server.",
        user_action="Review the error message to determine the cause of the problem.",
    )

    """
        OMAG-MULTI-TENANT-400-002 - The OMAG server {0} has been requested to shut down but the following services are
        still running: {1}
    """
    SERVICES_NOT_SHUTDOWN = dict(
        https_error_code="400",
        message_id="OMAG-MULTI-TENANT-400-002",
        message_template="The OMAG server {0} has been requested to shutdown but the following services are still running: {1}",
        system_action="The system is unable to shutdown the server correctly.",
        user_action="Review other error messages to determine the cause of the problem."
        + " This is likely to be a logic error in the services listed in the message",
    )

    """
        OMAG-MULTI-TENANT-400-003 - Method {0} called on behalf of the {1} service is unable to create a client-side
        open metadata topic connection because the topic name is not configured in the configuration for this service.
    """
    NO_TOPIC_INFORMATION = dict(
        https_error_code="400",
        message_id="OMAG-MULTI-TENANT-400-003",
        message_template="Method {0} called on behalf of the {1} service is unable to create a client-side open "
        + "metadata topic connection because the topic name is not configured in the configuration for this service.",
        system_action="This is a configuration error and an exception is sent to the requester.",
        user_action="Correct the configuration of the access service to include the name of the topic.",
    )

    """
        OMAG-MULTI-TENANT-400-004 - The connector provider class name {0} does not create a connector of class {1} 
        which is required for the {2}
    """
    NOT_CORRECT_CONNECTOR_PROVIDER = dict(
        https_error_code="400",
        message_id="OMAG-MULTI-TENANT-400-004",
        message_template="The connector provider class name {0} does not create a connector of class {1} which is"
        + " required for the {2}",
        system_action="An invalid parameter exception is returned to the caller.",
        user_action="Either change the connector or the hosting environment because the current"
        + " combination is not compatible.",
    )

    """
        OMAG-MULTI-TENANT-404-001 - The OMAG Server {0} is not available to service a request from user {1}
    """
    SERVER_NOT_AVAILABLE = dict(
        https_error_code="404",
        message_id="OMAG-MULTI-TENANT-404-001",
        message_template="The OMAG Server {0} is not available to service a request from user {1}",
        system_action="The system is unable to process the request because the server"
        + " is not running on the called platform.",
        user_action="Verify that the correct server is being called on the correct platform and that this server is running. "
        + "Retry the request when the server is available.",
    )

    """
        OMAG-MULTI-TENANT-404-002 - The {0} service is not available on OMAG Server {1} to handle a request from user {2}
    """
    SERVICE_NOT_AVAILABLE = dict(
        https_error_code="404",
        message_id="OMAG-MULTI-TENANT-404-002",
        message_template="The {0} service is not available on OMAG Server {1} to handle a request from user {2}",
        system_action="The system is unable to process the request because the service is not available.",
        user_action="Verify that the correct server is being called on the correct platform and that the requested service is configured to run there.  "
        + "Once the correct environment is in place, retry the request.",
    )

    """
        OMAG-MULTI-TENANT-404-003 - The server name is not available for the {0} operation
    """
    SERVER_NAME_NOT_AVAILABLE = dict(
        https_error_code="404",
        message_id="OMAG-MULTI-TENANT-404-003",
        message_template="The server name is not available for the {0} operation",
        system_action="The system is unable to return the server name because it is not available.",
        user_action="Check that the server where the access service is running initialized correctly.  "
        + "Correct any errors discovered and retry the request when the open metadata services are available.",
    )

    """
        OMAG-MULTI-TENANT-404-004 - The open metadata repository services are not initialized for the {0} operation
    """
    OMRS_NOT_INITIALIZED = dict(
        https_error_code="404",
        message_id="OMAG-MULTI-TENANT-404-004",
        message_template="The open metadata repository services are not initialized for the {0} operation",
        system_action="The system is unable to connect to the open metadata repository services because"
        + " they are not running in this server.",
        user_action="Check that the server where the called service is running initialized correctly.  "
        + "Correct any errors discovered and retry the request when the open metadata services are available.",
    )

    """
        OMAG-MULTI-TENANT-404-005 - The open metadata repository services are not available for the {0} operation
    """
    OMRS_NOT_AVAILABLE = (
        dict(
            https_error_code="404",
            message_id="OMAG-MULTI-TENANT-404-005",
            message_template="The open metadata repository services are not available for the {0} operation",
            system_action="The system is unable to connect to the open metadata repository services because"
            " they are not in the correct state to be called.",
            user_action="Check that the server where the called service is running initialized correctly and is not"
            + " in the process of shutting down. Correct any errors discovered and retry the"
            + " request when the open metadata repository services are available.",
        ),
    )

    """
        OMAG-MULTI-TENANT-500-003 - Method {0} called on behalf of the {1} service detected a {2} exception when
        creating an open metadata topic connection because the connector provider is incorrect.  
        The error message was {3}
    """
    BAD_TOPIC_CONNECTOR_PROVIDER = dict(
        http_error_code="500",
        message_id="OMAG-MULTI-TENANT-500-003",
        message_template="Method {0} called on behalf of the {1} service detected a {2} exception when creating an open "
        + "metadata topic connection because the connector provider is incorrect.  The error message was {3}",
        system_action="This is an internal error.  The access service is not using a valid connector provider.",
        user_action="Raise an issue on Egeria's GitHub and work with the Egeria community to resolve.",
    )


class OMAGCommonErrorCode(EgeriaErrorCode):

    CLIENT_SIDE_REST_API_ERROR = dict(
        http_error_code="503",
        message_id="CLIENT-SIDE-REST-API-CONNECTOR-503-002",
        message_template="A client-side error {0} was received by method {1} from API call {2} during the call {3}."
        + " The error message was {4}",
        system_action="The client has issued a call to the open metadata access service REST API in a remote server"
        + "and has received an exception from the local client libraries.",
        user_action="Review the error message to determine the cause of the error. Check that the server is running"
        + " and the URL is correct. Look for errors in the local server's console to understand and"
        + " correct the cause of the error. Then rerun the request",
    )

    EXCEPTION_RESPONSE_FROM_API = dict(
        http_error_code="503",
        message_id="SERVER-SIDE-REST-API-ERROR-503-003 ",
        message_template="A {0} exception was received from REST API call {1} to server {2}: error message was: {3}",
        system_action="The system has issued a call to an open metadata access service REST API in a remote server"
        + " and has received an exception response.",
        user_action="The error message should indicate the cause of the error. "
        + "Otherwise look for errors in the remote server's audit log and console to understand and "
        + "correct the source of the error.",
    )

    SERVER_URL_NOT_SPECIFIED = dict(
        http_error_code="400",
        message_id="OMAG-COMMON-400-001",
        message_template="The OMAG Server Platform URL is null",
        system_action="The system is unable to identify the OMAG Server Platform.",
        user_action="Create a new client and pass the URL for the server on the constructor.",
    )

    SERVER_URL_MALFORMED = dict(
        http_error_code="400",
        message_id="OMAG-COMMON-400-002",
        message_template="The OMAS Server URL: {0} is not in a recognized format",
        system_action="The system is unable to connect to the OMAG Server Platform to fulfill any requests.",
        user_action="Create a new client and pass the correct URL for the server on the constructor.",
    )

    SERVER_NAME_NOT_SPECIFIED = dict(
        http_error_code="400",
        message_id="OMAG-COMMON-400-003",
        message_template="The OMAG Server name is null",
        system_action="The system is unable to locate to the OMAG Server to fulfill any request.",
        user_action="Create a new client and pass the correct name for the server on the constructor.",
    )

    NULL_USER_ID = dict(
        http_error_code="400",
        message_id="OMAG-COMMON-400-004",
        message_template="The user identifier {0} passed on the operation is null",
        system_action="The system is unable to process the request without a user id..",
        user_action="Correct the code in the caller to provide the user id.",
    )

    NULL_GUID = dict(
        http_error_code="400",
        message_id="OMAG-COMMON-400-005",
        message_template="The unique identifier (guid) passed is null or not a string",
        system_action="The system is unable to process the request without a guid.",
        user_action="Correct the code in the caller to provide the guid.",
    )

    NULL_NAME = dict(
        http_error_code="400",
        message_id="OMAG-COMMON-400-006",
        message_template="The name passed on the parameter of the operation is null",
        system_action="The system is unable to process the request without a name.",
        user_action="Correct the code in the caller to provide the name on the parameter.",
    )

    NULL_ARRAY_PARAMETER = dict(
        http_error_code="400",
        message_id="OMAG-COMMON-400-007",
        message_template="The array value passed on the {0} parameter of the {1} operation is null or empty",
        system_action="The system is unable to process the request without this value.",
        user_action="Correct the code in the caller to provide the array.",
    )

    NEGATIVE_START_FROM = dict(
        http_error_code="400",
        message_id="OMAG-COMMON-400-008",
        message_template="The starting point for the results {0}, passed on the {1} parameter of the {2}"
        + " operation, is negative",
        system_action="The system is unable to process the request with this invalid value."
        + "It should be zero for the start of the values, or a number greater than 0 to start partway down the list.",
        user_action="Correct the code in the caller to provide a non-negative value for the starting point.",
    )

    NEGATIVE_PAGE_SIZE = dict(
        http_error_code="400",
        message_id="OMAG-COMMON-400-009",
        message_template="The page size for the results {0}, passed on the {1} parameter of the {2} operation, is negative",
        system_action="The system is unable to process the request with this invalid value. "
        + "It should be zero to return all the result, or greater than zero to set a maximum.",
        user_action="Correct the code in the caller to provide a non-negative value for the page size.",
    )

    MAX_PAGE_SIZE = dict(
        http_error_code="400",
        message_id="OMAG-COMMON-400-010",
        message_template=(
            "The number of records to return, {0}, passed on the {1} parameter of the {2} operation, "
            + "is greater than the allowable maximum of {3}"
        ),
        system_action="The system is unable to process the request with this page size value.",
        user_action="Correct the code in the caller to provide a smaller page size.",
    )

    NULL_ENUM = dict(
        http_error_code="400",
        message_id="OMAG-COMMON-400-012",
        message_template="The enumeration value passed on the {0} parameter of the {1} operation is null",
        system_action="The system is unable to process the request without a enumeration value.",
        user_action="Correct the code in the caller to provide the enumeration value.",
    )

    NULL_TEXT = dict(
        http_error_code="400",
        message_id="OMAG-COMMON-400-013",
        message_template="The text field passed on the {0} parameter of the {1} operation is null",
        system_action="The system is unable to process the request without this text value.",
        user_action="Correct the code in the caller to provide a value in the text field.",
    )

    NULL_OBJECT = dict(
        http_error_code="400",
        message_id="OMAG-COMMON-400-015",
        message_template="The object passed on the {0} parameter of the {1} operation is null",
        system_action="The system is unable to process the request without this object.",
        user_action="Correct the code in the caller to provide the object.",
    )

    NULL_SEARCH_STRING = dict(
        http_error_code="400",
        message_id="OMAG-COMMON-400-022",
        message_template="The search string passed on the {0} parameter of the {1} operation is null",
        system_action="The system is unable to process the request without a search string.",
        user_action="Correct the code in the caller to provide the search string.",
    )


class EgeriaException(Exception):
    """
    Define the Egeria exceptions raised during error handling. Modeled on the Egeria Exceptions defined in the
    Egeria core.

    """

    def __init__(self, response_body) -> object:
        response_dict = json.loads(response_body)
        self.response_class = response_dict["class"]
        self.related_http_code = response_dict["relatedHTTPCode"]
        self.exception_class_name = response_dict["exceptionClassName"]
        self.action_description = response_dict["actionDescription"]
        self.exception_error_message = response_dict["exceptionErrorMessage"]
        self.exception_error_message_id = response_dict["exceptionErrorMessageId"]

        # self.exception_error_message_id = response_dict["exceptionErrorMessageId"]
        self.exception_error_message_parameters = response_dict[
            "exceptionErrorMessageParameters"
        ]
        self.exception_system_action = response_dict["exceptionSystemAction"]
        self.exception_user_action = response_dict["exceptionUserAction"]

    def __str__(self):
        return self.exception_error_message


class InvalidParameterException(EgeriaException):
    """Exception due to invalid parameters such as one of the parameters is null or invalid"""

    def __init__(self, response_body):

        EgeriaException.__init__(self, response_body)


class PropertyServerException(EgeriaException):
    """Exception due to a problem retrieving information from the property server"""

    def __init__(self, response_body):

        EgeriaException.__init__(self, response_body)


class UserNotAuthorizedException(EgeriaException):
    """Exception as the requesting user is not authorized to issue this request"""

    def __init__(self, response_body):

        EgeriaException.__init__(self, response_body)


# class RESTConnectionException(EgeriaException):
#     """Exception that wraps exceptions coming from the Request package
#
#     Note that I am trying a different approach where I'm not hiding the REST error
#     """
#
#     # Todo - evaluate if this is still needed.. perhaps remove this exception
#     def __init__(
#         self,
#         error_msg: str,
#         error_code: OMAGCommonErrorCode,
#         class_name: str,
#         method_name: str,
#         params: [str],
#     ):
#         EgeriaException.__init__(
#             self,
#             error_msg,
#             error_code,
#             class_name,
#             method_name,
#             params,
#         )
#

"""

Validators and error handlers for common parameters

"""


def validate_user_id(user_id: str) -> bool:
    """
    Validate that the provided user id is neither null nor empty.

    Parameters
    ----------
    user_id : str  The user id string to validate

    Returns
    -------
    bool - True if valid, If invalid an InvalidParameterException is raised.

    """
    if (user_id is None) or len(user_id) == 0:
        msg = str(OMAGCommonErrorCode.NULL_USER_ID.value["message_template"]).format(
            "user_id"
        )
        calling_frame = inspect.currentframe().f_back
        caller_method = inspect.getframeinfo(calling_frame).function

        exc_msg = json.dumps(
            {
                "class": "VoidResponse",
                "relatedHTTPCode": 400,
                "exceptionClassName": "InvalidParameterException",
                "actionDescription": caller_method,
                "exceptionErrorMessage": msg,
                "exceptionErrorMessageId": OMAGCommonErrorCode.NULL_USER_ID.value[
                    "message_id"
                ],
                "exceptionErrorMessageParameters": user_id,
                "exceptionSystemAction": OMAGCommonErrorCode.NULL_USER_ID.value[
                    "system_action"
                ],
                "exceptionUserAction": OMAGCommonErrorCode.NULL_USER_ID.value[
                    "user_action"
                ],
                "exceptionProperties": {"user_id": user_id},
            }
        )
        raise InvalidParameterException(exc_msg)
    else:
        return True


def validate_server_name(server_name: str) -> bool:
    """
    Validate that the provided server name is neither null nor empty.

    Parameters
    ----------
    server_name : str  The user id string to validate

    Returns
    -------
    bool - True if valid, If invalid an InvalidParameterException is raised.

    """
    calling_frame = inspect.currentframe().f_back
    caller_method = inspect.getframeinfo(calling_frame).function

    if (server_name is None) or (len(server_name) == 0):
        msg = str(
            OMAGCommonErrorCode.SERVER_NAME_NOT_SPECIFIED.value["message_template"]
        )
        exc_msg = json.dumps(
            {
                "class": "VoidResponse",
                "relatedHTTPCode": 400,
                "exceptionClassName": "InvalidParameterException",
                "actionDescription": caller_method,
                "exceptionErrorMessage": msg,
                "exceptionErrorMessageId": OMAGCommonErrorCode.NULL_USER_ID.value[
                    "message_id"
                ],
                "exceptionErrorMessageParameters": server_name,
                "exceptionSystemAction": OMAGCommonErrorCode.NULL_USER_ID.value[
                    "system_action"
                ],
                "exceptionUserAction": OMAGCommonErrorCode.NULL_USER_ID.value[
                    "user_action"
                ],
                "exceptionProperties": {"server_name": server_name},
            }
        )
        raise InvalidParameterException(exc_msg)
    else:
        return True


def validate_guid(guid: str) -> bool:
    """
    Validate that the provided guid is neither null nor empty.

    Parameters
    ----------
    guid : str  The user id string to validate

    Returns
    -------
    bool - True if valid, If invalid an InvalidParameterException is raised.

    """
    calling_frame = inspect.currentframe().f_back
    caller_method = inspect.getframeinfo(calling_frame).function

    if (guid is None) or (len(guid) == 0) or (type(guid) != str):
        msg = str(OMAGCommonErrorCode.NULL_GUID.value["message_template"])
        exc_msg = json.dumps(
            {
                "class": "VoidResponse",
                "relatedHTTPCode": 400,
                "exceptionClassName": "InvalidParameterException",
                "actionDescription": caller_method,
                "exceptionErrorMessage": msg,
                "exceptionErrorMessageId": OMAGCommonErrorCode.NULL_USER_ID.value[
                    "message_id"
                ],
                "exceptionErrorMessageParameters": guid,
                "exceptionSystemAction": OMAGCommonErrorCode.NULL_USER_ID.value[
                    "system_action"
                ],
                "exceptionUserAction": OMAGCommonErrorCode.NULL_USER_ID.value[
                    "user_action"
                ],
                "exceptionProperties": {"guid": guid},
            }
        )
        raise InvalidParameterException(exc_msg)
    else:
        return True


def validate_name(name: str) -> bool:
    """
    Validate that the provided name is neither null nor empty.

    Parameters
    ----------
    name: str  The user id string to validate

    Returns
    -------
    bool - True if valid, If invalid an InvalidParameterException is raised.

    """
    calling_frame = inspect.currentframe().f_back
    caller_method = inspect.getframeinfo(calling_frame).function

    if (name is None) or (len(name) == 0):
        msg = str(OMAGCommonErrorCode.NULL_NAME.value["message_template"])
        exc_msg = json.dumps(
            {
                "class": "VoidResponse",
                "relatedHTTPCode": 400,
                "exceptionClassName": "InvalidParameterException",
                "actionDescription": caller_method,
                "exceptionErrorMessage": msg,
                "exceptionErrorMessageId": OMAGCommonErrorCode.NULL_USER_ID.value[
                    "message_id"
                ],
                "exceptionErrorMessageParameters": name,
                "exceptionSystemAction": OMAGCommonErrorCode.NULL_USER_ID.value[
                    "system_action"
                ],
                "exceptionUserAction": OMAGCommonErrorCode.NULL_USER_ID.value[
                    "user_action"
                ],
                "exceptionProperties": {"name": name},
            }
        )
        raise InvalidParameterException(exc_msg)
    else:
        return True


def validate_search_string(search_string: str) -> bool:
    """
    Validate that the provided search string is neither null nor empty.

    Parameters
    ----------
    search_string : str  The user id string to validate

    Returns
    -------
    bool - True if valid, If invalid an InvalidParameterException is raised.

    """
    calling_frame = inspect.currentframe().f_back
    caller_method = inspect.getframeinfo(calling_frame).function

    if (search_string is None) or (len(search_string) == 0):
        msg = str(OMAGCommonErrorCode.NULL_SEARCH_STRING.value["message_template"])
        exc_msg = json.dumps(
            {
                "class": "VoidResponse",
                "relatedHTTPCode": 400,
                "exceptionClassName": "InvalidParameterException",
                "actionDescription": caller_method,
                "exceptionErrorMessage": msg,
                "exceptionErrorMessageId": OMAGCommonErrorCode.NULL_USER_ID.value[
                    "message_id"
                ],
                "exceptionErrorMessageParameters": search_string,
                "exceptionSystemAction": OMAGCommonErrorCode.NULL_USER_ID.value[
                    "system_action"
                ],
                "exceptionUserAction": OMAGCommonErrorCode.NULL_USER_ID.value[
                    "user_action"
                ],
                "exceptionProperties": {"search_string": search_string},
            }
        )
        raise InvalidParameterException(exc_msg)
    else:
        return True


def validate_public(is_public: bool) -> bool:
    """
    Validate that the provided flag is boolean.

    Parameters
    ----------
    is_public : bool  The flag must be boolean

    Returns
    -------
    bool - True if valid, If invalid an InvalidParameterException is raised.

    """
    calling_frame = inspect.currentframe().f_back
    caller_method = inspect.getframeinfo(calling_frame).function

    if is_public is None:
        msg = str(OMAGCommonErrorCode.NULL_OBJECT.value["message_template"])
        exc_msg = json.dumps(
            {
                "class": "VoidResponse",
                "relatedHTTPCode": 400,
                "exceptionClassName": "InvalidParameterException",
                "actionDescription": caller_method,
                "exceptionErrorMessage": msg,
                "exceptionErrorMessageId": OMAGCommonErrorCode.NULL_USER_ID.value[
                    "message_id"
                ],
                "exceptionErrorMessageParameters": is_public,
                "exceptionSystemAction": OMAGCommonErrorCode.NULL_USER_ID.value[
                    "system_action"
                ],
                "exceptionUserAction": OMAGCommonErrorCode.NULL_USER_ID.value[
                    "user_action"
                ],
                "exceptionProperties": {"is_public": is_public},
            }
        )
        raise InvalidParameterException(exc_msg)
    else:
        return True


def validate_url(url: str) -> bool:
    """
    Validate that the provided url is neither null nor empty. The syntax of the url
    string is also checked to see that it conforms to standards.

    Note: The validation package used does not view http://localhost:9443 as valid - expects a domain suffix.

    Parameters
    ----------
    url : str  The url string to validate.

    Returns
    -------
    bool - True if valid, If invalid an InvalidParameterException is raised.

    """
    calling_frame = inspect.currentframe().f_back
    caller_method = inspect.getframeinfo(calling_frame).function

    if (url is None) or (len(url) == 0):
        msg = str(
            OMAGCommonErrorCode.SERVER_URL_NOT_SPECIFIED.value["message_template"]
        )
        exc_msg = json.dumps(
            {
                "class": "VoidResponse",
                "relatedHTTPCode": 400,
                "exceptionClassName": "InvalidParameterException",
                "actionDescription": caller_method,
                "exceptionErrorMessage": msg,
                "exceptionErrorMessageId": OMAGCommonErrorCode.NULL_USER_ID.value[
                    "message_id"
                ],
                "exceptionErrorMessageParameters": url,
                "exceptionSystemAction": OMAGCommonErrorCode.NULL_USER_ID.value[
                    "system_action"
                ],
                "exceptionUserAction": OMAGCommonErrorCode.NULL_USER_ID.value[
                    "user_action"
                ],
                "exceptionProperties": {"url": url},
            }
        )
        raise InvalidParameterException(exc_msg)

    result = validators.url(url)
    # print(f"validation result is {result}")
    if result is not True:
        msg = OMAGCommonErrorCode.SERVER_URL_MALFORMED.value["message_template"].format(
            url
        )
        exc_msg = json.dumps(
            {
                "class": "VoidResponse",
                "relatedHTTPCode": 400,
                "exceptionClassName": "InvalidParameterException",
                "actionDescription": caller_method,
                "exceptionErrorMessage": msg,
                "exceptionErrorMessageId": OMAGCommonErrorCode.NULL_USER_ID.value[
                    "message_id"
                ],
                "exceptionErrorMessageParameters": url,
                "exceptionSystemAction": OMAGCommonErrorCode.NULL_USER_ID.value[
                    "system_action"
                ],
                "exceptionUserAction": OMAGCommonErrorCode.NULL_USER_ID.value[
                    "user_action"
                ],
                "exceptionProperties": {"url": url},
            }
        )
        raise InvalidParameterException(exc_msg)
    else:
        return True


def print_rest_request(url):
    """

    Args:
        url:
    """
    print(" ")
    print(url)


def print_rest_request_body(body):
    """

    Args:
        body:
    """
    prettyBody = json.dumps(body, indent=4)
    print(prettyBody)
    print(" ")


def print_rest_response(response):
    """

    Args:
        response:
    """
    print("Returns:")
    prettyResponse = json.dumps(response, indent=4)
    print(prettyResponse)
    print(" ")


def print_exception_response(e: EgeriaException):
    """

    Args:
        serverName:
        serverPlatformName:
        serverPlatformURL:
        response:

    Returns:

    """
    if isinstance(e, EgeriaException):
        print(f"\n\nException: {e.response_class}")
        print(f"\t\t   Error Message: {e.exception_error_message}")
        print(
            f"\t\t   Error Code: {e.exception_error_message_id} with http code {e.related_http_code}"
        )
        print(f"\t\t   Class: {e.exception_class_name}")
        print(f"\t\t   Caller: {e.action_description}")
        print(f"\t\t   System Action: {e.exception_system_action}")
        print(f"\t\t   User Action: {e.exception_user_action}")
    else:
        print(f"\n\n\t  Not an Egeria exception {e}")


def print_guid_list(guids):
    if guids == None:
        print("No assets created")
    else:
        prettyGUIDs = json.dumps(guids, indent=4)
        print(prettyGUIDs)


def is_json(txt: str) -> bool:
    try:
        json_object = json.loads(txt)
        return True
    except (ValueError, JSONDecodeError) as e:
        print(e)
        return False


#
# OCF Common services
# Working with assets - this set of functions displays assets returned from the open metadata repositories.
#
class comment:
    def __init__(
        self,
        comment_guid: str,
        comment_type: str,
        comment_text: str,
        comment_owner: str,
        is_public: bool,
    ):
        self.comment_guid: str = comment_guid
        self.comment_type: str = comment_type
        self.comment_text: str = comment_text
        self.comment_owner: str = comment_owner
        self.is_public: bool = is_public

        if self.comment_type not in comment_types:
            raise ValueError(comment_type + " is an Invalid comment type")


def getAssetUniverse(
    serverName,
    serverPlatformName,
    serverPlatformURL,
    serviceURLMarker,
    userId,
    assetGUID,
):
    connectedAssetURL = (
        serverPlatformURL
        + "/servers/"
        + serverName
        + "/open-metadata/common-services/"
        + serviceURLMarker
        + "/connected-asset/users/"
        + userId
    )
    getAsset = connectedAssetURL + "/assets/" + assetGUID
    response = issueGet(getAsset)
    asset = response.json().get("asset")
    if asset:
        return response.json()
    else:
        print("No Asset returned")
        process_error_response(serverName, "fixme", serverPlatformURL, response)


def get_related_assets(
    serverName,
    serverPlatformName,
    serverPlatformURL,
    serviceURLMarker,
    userId,
    assetGUID,
):
    connectedAssetURL = (
        serverPlatformURL
        + "/servers/"
        + serverName
        + "/open-metadata/common-services/"
        + serviceURLMarker
        + "/connected-asset/users/"
        + userId
    )
    getRelatedAsset = (
        connectedAssetURL
        + "/assets/"
        + assetGUID
        + "/related-assets?elementStart=0&maxElements=50"
    )
    response = issueGet(getRelatedAsset)
    if response.status_code == 200:
        relatedHTTPCode = response.json().get("relatedHTTPCode")
        if relatedHTTPCode == 200:
            return response.json().get("list")
        else:
            printUnexpectedResponse(
                serverName, serverPlatformName, serverPlatformURL, response
            )
    else:
        printUnexpectedResponse(
            serverName, serverPlatformName, serverPlatformURL, response
        )


def getComments(
    serverName,
    serverPlatformName,
    serverPlatformURL,
    serviceURLMarker,
    userId,
    assetGUID,
):
    connectedAssetURL = (
        serverPlatformURL
        + "/servers/"
        + serverName
        + "/open-metadata/common-services/"
        + serviceURLMarker
        + "/connected-asset/users/"
        + userId
    )
    commentQuery = (
        connectedAssetURL
        + "/assets/"
        + assetGUID
        + "/comments?elementStart=0&maxElements=50"
    )
    response = issueGet(commentQuery)
    responseObjects = response.json().get("list")
    if responseObjects:
        return responseObjects
    else:
        print("No comments returned")
        process_error_response(serverName, "fixme", serverPlatformURL, response)


def getCommentReplies(
    serverName,
    serverPlatformName,
    serverPlatformURL,
    serviceURLMarker,
    userId,
    assetGUID,
    commentGUID,
):
    connectedAssetURL = (
        serverPlatformURL
        + "/servers/"
        + serverName
        + "/open-metadata/common-services/"
        + serviceURLMarker
        + "/connected-asset/users/"
        + userId
    )
    commentReplyQuery = (
        connectedAssetURL
        + "/assets/"
        + assetGUID
        + "/comments/"
        + commentGUID
        + "/replies?elementStart=0&maxElements=50"
    )
    response = issueGet(commentReplyQuery)
    responseObjects = response.json().get("list")
    if responseObjects:
        return responseObjects
    else:
        print("No comments returned")
        process_error_response(serverName, "fixme", serverPlatformURL, response)


def getAPIOperations(
    serverName,
    serverPlatformName,
    serverPlatformURL,
    serviceURLMarker,
    userId,
    apiSchemaTypeGUID,
):
    connectedAssetURL = (
        serverPlatformURL
        + "/servers/"
        + serverName
        + "/open-metadata/common-services/"
        + serviceURLMarker
        + "/connected-asset/users/"
        + userId
    )
    requestURL = (
        connectedAssetURL
        + "/assets/schemas/apis/"
        + apiSchemaTypeGUID
        + "/api-operations?elementStart=0&maxElements=50"
    )
    response = issueGet(requestURL)
    responseObjects = response.json().get("list")
    if response.status_code == 200:
        relatedHTTPCode = response.json().get("relatedHTTPCode")
        if relatedHTTPCode == 200:
            return response.json().get("list")
        else:
            printUnexpectedResponse(
                serverName, serverPlatformName, serverPlatformURL, response
            )
    else:
        printUnexpectedResponse(
            serverName, serverPlatformName, serverPlatformURL, response
        )


def getSchemaAttributesFromSchemaType(
    serverName,
    serverPlatformName,
    serverPlatformURL,
    serviceURLMarker,
    userId,
    schemaTypeGUID,
):
    ocfURL = (
        serverPlatformURL
        + "/servers/"
        + serverName
        + "/open-metadata/common-services/"
        + serviceURLMarker
        + "/connected-asset/users/"
        + userId
    )
    getSchemaAttributesURL = (
        ocfURL
        + "/assets/schemas/"
        + schemaTypeGUID
        + "/schema-attributes?elementStart=0&maxElements=100"
    )
    response = issueGet(getSchemaAttributesURL)
    schemaAttributes = response.json().get("list")
    if schemaAttributes:
        return schemaAttributes
    else:
        print("No Schema attributes retrieved")
        process_error_response(serverName, "fixme", serverPlatformURL, response)


def print_response(response):
    """

    Args:
        response:

    Returns:
        : str
    """
    prettyResponse = json.dumps(response.json(), indent=4)
    print(" ")
    print("Response: ")
    print(prettyResponse)
    print(" ")


def print_unexpected_response(
    serverName, serverPlatformName, serverPlatformURL, response
):
    """

    Args:
        serverName:
        serverPlatformName:
        serverPlatformURL:
        response:
    """
    if response.status_code == 200:
        relatedHTTPCode = response.json().get("relatedHTTPCode")
        if relatedHTTPCode == 200:
            print("Unexpected response from server " + serverName)
            print_response(response)
        else:
            exceptionErrorMessage = response.json().get("exceptionErrorMessage")
            exceptionSystemAction = response.json().get("exceptionSystemAction")
            exceptionUserAction = response.json().get("exceptionUserAction")
            if exceptionErrorMessage != None:
                print(exceptionErrorMessage)
                print(" * " + exceptionSystemAction)
                print(" * " + exceptionUserAction)
            else:
                print("Unexpected response from server " + serverName)
                print_response(response)
    else:
        print(
            "Unexpected response from server platform "
            + serverPlatformName
            + " at "
            + serverPlatformURL
        )
        print_response(response)


def get_last_guid(guids):
    """

    Args:
        guids:

    Returns:

    """
    if guids == None:
        return "<unknown>"
    else:
        return guids[-1]
