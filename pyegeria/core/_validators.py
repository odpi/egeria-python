"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.
"""

import inspect
import json
import re
from json import JSONDecodeError

import validators

from pyegeria.core._exceptions import PyegeriaInvalidParameterException

"""
This package contains internally used validators.

"""

# user_id and server_name are both interpolated directly into URL path segments
# in several places (e.g. pyegeria/omvs/server_operations.py's
# ".../users/{self.user_id}/status") without URL-encoding, so a value containing
# a control character or a URL-path-structural character (/, ?, #, backslash,
# whitespace) would otherwise only surface as an opaque httpx.InvalidURL /
# generic PyegeriaUnknownException deep inside a later request. Reject those
# characters at construction time instead, where the error is immediately
# traceable to the bad input.
_URL_UNSAFE_CHARS_RE = re.compile(r'[\x00-\x1f\x7f/?#\\\s]')


def _validate_url_path_safe(value: str, param_name: str) -> None:
    match = _URL_UNSAFE_CHARS_RE.search(value)
    if match:
        context: dict = {}
        context['calling_frame'] = inspect.currentframe().f_back.f_back
        context['caller_method'] = inspect.currentframe().f_back.f_back.f_code.co_name
        additional_info = {
            "reason": f"Invalid {param_name} - contains a character unsafe for use in a URL path "
                      f"({match.group()!r})",
            param_name: value,
        }
        raise PyegeriaInvalidParameterException(None, context, additional_info)


def validate_user_id(user_id: str) -> bool:
    """
    Validate that the provided user id is neither null nor empty, and contains no
    characters that are unsafe once interpolated into a URL path.

    Parameters
    ----------
    user_id : str  The user id string to validate

    Returns
    -------
    bool: True if valid, If invalid input, a PyegeriaInvalidParameterException is raised.

    Raises
    ------
    PyegeriaInvalidParameterException
        If the provided user id is null, empty, or contains URL-unsafe characters
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
    _validate_url_path_safe(user_id, "user_id")
    return True


def validate_server_name(server_name: str) -> bool:
    """
    Validate that the provided server name is neither null nor empty, and contains
    no characters that are unsafe once interpolated into a URL path.

    Parameters
    ----------
    server_name : str  The user id string to validate

    Returns
    -------
    bool - True if valid, If invalid an PyegeriaInvalidParameterException is raised.

    Raises
    ------
    PyegeriaInvalidParameterException
        If the provided server name is null, empty, or contains URL-unsafe characters

    """

    if (server_name is None) or (len(server_name) == 0):
        context: dict = {}
        context['calling_frame'] = inspect.currentframe().f_back
        context['caller_method'] = inspect.currentframe().f_back.f_code.co_name
        additional_info = {
            "reason": "Invalid server name - its empty", "input_parameters": f"server_name={server_name}",
            }
        raise PyegeriaInvalidParameterException(None, context, additional_info)
    _validate_url_path_safe(server_name, "server_name")
    return True


def validate_guid(guid: str) -> bool:
    """
    Validate that the provided guid is neither null nor empty.

    Parameters
    ----------
    guid : str  The user id string to validate

    Returns
    -------
    bool - True if valid, If invalid an PyegeriaInvalidParameterException is raised.

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
    bool - True if valid, If invalid an PyegeriaInvalidParameterException is raised.

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
    bool - True if valid, If invalid an PyegeriaInvalidParameterException is raised.

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
    bool - True if valid, If invalid an PyegeriaInvalidParameterException is raised.

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
    bool - True if valid, If invalid an PyegeriaInvalidParameterException is raised.

    """
    context: dict = {}
    context['calling_frame'] = inspect.currentframe().f_back
    context['caller_method'] = inspect.currentframe().f_back.f_code.co_name

    if (url is None) or (len(url) == 0):

        additional_info = {"reason": "The provided URL is invalid - it is empty",
                           "input_parameters": f"URL: {url}"}
        raise PyegeriaInvalidParameterException(None,context, additional_info)

    # The following hack allows localhost and other simple hostnames to be used as a hostname 
    # - which is disallowed by the validations package
    if ("localhost" in url) and ("localhost." not in url):
        url = url.replace("localhost", "127.0.0.1")
    
    # If the URL looks valid but lacks a dot in the hostname (common in Docker), 
    # we skip the strict validators.url check or we could try to make it pass.
    # For now, let's just use a simpler check if validators.url fails.
    
    result = validators.url(url)
    if result is not True:
        # Fallback for Docker hostnames (no dots in hostname)
        from urllib.parse import urlparse
        try:
            parsed = urlparse(url)
            if parsed.scheme in ('http', 'https') and parsed.netloc:
                # If it has a scheme and a netloc, it's good enough for us
                # especially if it's a simple hostname like 'egeria-main'
                return True
        except Exception:
            pass

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
