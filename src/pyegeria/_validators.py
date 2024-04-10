"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.
"""
import inspect
import json
import validators
from json import JSONDecodeError
from pyegeria._exceptions import (
    OMAGCommonErrorCode,
    InvalidParameterException,
)

"""
This package contains internally used validators.

"""


def validate_user_id(user_id: str) -> bool:
    """
    Validate that the provided user id is neither null nor empty.

    Parameters
    ----------
    user_id : str  The user id string to validate

    Returns
    -------
    bool: True if valid, If invalid an InvalidParameterException is raised.

    Raises
    ------
    InvalidParameterException
        If the provided user id is null or empty
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

    if (guid is None) or (len(guid) == 0) or (type(guid) is not str):
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
        msg = str(OMAGCommonErrorCode.NULL_SEARCH_STRING.value["message_template"].
                  format('search_string', caller_method))
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
                "exceptionErrorMessageParameters": [search_string, caller_method],
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
                "exceptionErrorMessageId": OMAGCommonErrorCode.SERVER_URL_MALFORMED.value[
                    "message_id"
                ],
                "exceptionErrorMessageParameters": url,
                "exceptionSystemAction": OMAGCommonErrorCode.SERVER_URL_MALFORMED.value[
                    "system_action"
                ],
                "exceptionUserAction": OMAGCommonErrorCode.SERVER_URL_MALFORMED.value[
                    "user_action"
                ],
                "exceptionProperties": {"url": url},
            }
        )
        raise InvalidParameterException(exc_msg)

    # The following hack allows localhost to be used as a hostname - which is disallowed by the
    # validations package
    if ('localhost' in url) and ('localhost.' not in url):
        url = url.replace('localhost', '127.0.0.1')

    result = validators.url(url)
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
                "exceptionErrorMessageId": OMAGCommonErrorCode.SERVER_URL_MALFORMED.value[
                    "message_id"
                ],
                "exceptionErrorMessageParameters": url,
                "exceptionSystemAction": OMAGCommonErrorCode.SERVER_URL_MALFORMED.value[
                    "system_action"
                ],
                "exceptionUserAction": OMAGCommonErrorCode.SERVER_URL_MALFORMED.value[
                    "user_action"
                ],
                "exceptionProperties": {"url": url},
            }
        )
        raise InvalidParameterException(exc_msg)
    else:
        return True


def is_json(txt: str) -> bool:
    """
    Parameters
    ----------
    txt : str
        The string to check if it is a valid JSON.

    Returns
    -------
    bool
        True if the string is a valid JSON, False otherwise.
    """
    try:
        json.loads(txt)
        return True
    except (ValueError, JSONDecodeError) as e:
        print(e)
        return False
