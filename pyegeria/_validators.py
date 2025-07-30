"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.
"""

import inspect
import json
from json import JSONDecodeError

import validators

from pyegeria._exceptions import InvalidParameterException, OMAGCommonErrorCode
from pyegeria._exceptions_new import PyegeriaInvalidParameterException

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
    bool: True if valid, If invalid input, a PyegeriaAuthenticationException is raised.

    Raises
    ------
    PyegeriaAuthenticationException
        If the provided user id is null or empty
    """
    if (user_id is None) or len(user_id) == 0:
        context: dict = {}
        context['calling_frame'] = inspect.currentframe().f_back
        context['caller_method'] = inspect.currentframe().f_back.f_code.co_name
        additional_info = {
            "reason": "Invalid user name - its empty",
            "userid": user_id,
            }
        raise PyegeriaInvalidParameterException(None,context, additional_info)
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

    Raises
    ------
    PyegeriaInvalidParameterException
        If the provided server name is null or empty

    """

    if (server_name is None) or (len(server_name) == 0):
        context: dict = {}
        context['calling_frame'] = inspect.currentframe().f_back
        context['caller_method'] = inspect.currentframe().f_back.f_code.co_name
        additional_info = {
            "reason": "Invalid server name - its empty", "input_parameters": f"server_name={server_name}",
            }
        raise PyegeriaInvalidParameterException(None, context, additional_info)
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

    Raises
    ------
    PyegeriaInvalidParameterException
        If the provided guid is null or empty
    """
    if (guid is None) or (len(guid) == 0) or (type(guid) is not str):
        context: dict = {}
        context['calling_frame'] = inspect.currentframe().f_back
        context['caller_method'] = inspect.currentframe().f_back.f_code.co_name
        additional_info = {
            "reason": "Invalid GUID", "input_parameters": f"guid = {guid}"
            }
        raise PyegeriaInvalidParameterException(None,context, additional_info)
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

    Raises
    ------
    PyegeriaInvalidParameterException
        If the provided name is null or empty
    """

    if (name is None) or (len(name) == 0):
        context: dict = {}
        context['calling_frame'] = inspect.currentframe().f_back
        context['caller_method'] = inspect.currentframe().f_back.f_code.co_name
        additional_info = {
            "reason": "Invalid `name`", "input_parameters": f"name = {name}"
            }
        raise PyegeriaInvalidParameterException(None,context, additional_info)
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

    Raises
    ------
    PyegeriaInvalidParameterException
        If the provided search string is null or empty
    """

    if (search_string is None) or (len(search_string) == 0):
        context: dict = {}
        context['calling_frame'] = inspect.currentframe().f_back
        context['caller_method'] = inspect.currentframe().f_back.f_code.co_name
        additional_info = {
            "reason": "Invalid `name`", "input_parameters": f"search_string={search_string}"
            }
        raise PyegeriaInvalidParameterException(None,context, additional_info)
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

    Raises
    ------
    PyegeriaInvalidParameterException
        If the provided public flag is null or empty
    """

    if is_public is None:
        context: dict = {}
        context['calling_frame'] = inspect.currentframe().f_back
        context['caller_method'] = inspect.currentframe().f_back.f_code.co_name
        additional_info = {
            "reason": "Invalid `name`", "input_parameters": f"is_public={is_public}"
            }
        raise PyegeriaInvalidParameterException(None,context, additional_info)
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
    context: dict = {}
    context['calling_frame'] = inspect.currentframe().f_back
    context['caller_method'] = inspect.currentframe().f_back.f_code.co_name

    if (url is None) or (len(url) == 0):

        additional_info = {"reason": "The provided URL is invalid - it is empty",
                           "input_parameters": f"URL: {url}"}
        raise PyegeriaInvalidParameterException(None,context, additional_info)

    # The following hack allows localhost to be used as a hostname - which is disallowed by the
    # validations package
    if ("localhost" in url) and ("localhost." not in url):
        url = url.replace("localhost", "127.0.0.1")

    result = validators.url(url)
    if result is not True:
        additional_info = {
            "reason": "The provided URL is invalid",
            "input_parameters": f"URL: {url}"
            }
        raise PyegeriaInvalidParameterException(None,context, additional_info)
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
