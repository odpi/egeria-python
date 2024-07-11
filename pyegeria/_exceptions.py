"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Definitions, utilities and exceptions in support of the Egeria Python Client package.

"""

import json
from enum import Enum

"""

The following definitions are used in creating Exception messages. 
They mirror similar definitions in the Egeria core. 
Note that not all of the definitions are currently used - they merely serve as placeholders for future extensions.

"""


class EgeriaErrorCode(Enum):
    """ Egeria error codes """

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
    """ OMAGServer instance error codes """

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
        message_template="The OMAG server {0} has been requested to shutdown but the following services " +
                         "are still running: {1}",
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
                         + "metadata topic connection because the topic name is not configured in the configuration "
                         + "for this service.",
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
        user_action="Verify that the correct server is being called on the correct platform and that this server "
                    + "is running. Retry the request when the server is available.",
    )

    """
        OMAG-MULTI-TENANT-404-002- The {0} service is not available on OMAG Server {1} to handle a request from user {2}
    """
    SERVICE_NOT_AVAILABLE = dict(
        https_error_code="404",
        message_id="OMAG-MULTI-TENANT-404-002",
        message_template="The {0} service is not available on OMAG Server {1} to handle a request from user {2}",
        system_action="The system is unable to process the request because the service is not available.",
        user_action="Verify that the correct server is being called on the correct platform and that the "
                    + "requested service is configured to run there.  "
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
        message_template="Method {0} called on behalf of the {1} service detected a {2} exception when creating an "
        + "open metadata topic connection because the connector provider is incorrect.  The error message was {3}",
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
                      + " and has received an exception from the local client libraries.",
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
        + "It should be zero for the start of the values, or a number greater than 0"
        + "to start partway down the list.",
        user_action="Correct the code in the caller to provide a non-negative value for the starting point.",
    )

    NEGATIVE_PAGE_SIZE = dict(
        http_error_code="400",
        message_id="OMAG-COMMON-400-009",
        message_template="The page size for the results {0}, passed on the {1} parameter of the {2} operation, " +
                         "is negative",
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
    Define the Egeria exceptions raised during error handling. Modeled on the exceptions defined in the Egeria core.

    """
    raw_error_message = ""

    def __init__(self, response_body) -> None:
        response_dict = json.loads(response_body)
        self.response_class = response_dict["class"]
        self.related_http_code = response_dict["relatedHTTPCode"]
        self.exception_class_name = response_dict["exceptionClassName"]
        self.action_description = response_dict["actionDescription"]
        self.exception_error_message = response_dict["exceptionErrorMessage"]
        self.exception_error_message_id = response_dict.get("exceptionErrorMessageId", "UNKNOWN-ERROR-CODE")

        # self.exception_error_message_id = response_dict["exceptionErrorMessageId"]
        self.exception_error_message_parameters = response_dict.get("exceptionErrorMessageParameters", "{}")
        self.exception_system_action = response_dict.get("exceptionSystemAction", "UNKNOWN-SYSTEM-ACTION")
        self.exception_user_action = response_dict.get("exceptionUserAction", "UNKNOWN-USER-ACTION")

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


def print_exception_response(e: EgeriaException):
    """ Prints the exception response """

    if isinstance(e, EgeriaException):
        print(f"\n\nException: {e.response_class}")
        print(f"\t\t   Error Message: {e.exception_error_message}")
        print(
            f"\t\t   Error Code: {e.exception_error_message_id} with http code {str(e.related_http_code)}"
        )
        # print(f"\t\t   Raw Error Text is {e.raw_error_message}")
        print(f"\t\t   Class: {e.exception_class_name}")
        print(f"\t\t   Caller: {e.action_description}")
        print(f"\t\t   System Action: {e.exception_system_action}")
        print(f"\t\t   User Action: {e.exception_user_action}")
    else:
        print(f"\n\n\t  Not an Egeria exception {e}")
