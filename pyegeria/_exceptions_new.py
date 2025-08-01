"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Definitions, utilities and exceptions in support of the Egeria Python Client package.

"""
import os
import json
from enum import Enum

from httpx import Response
from loguru import logger
from rich.markdown import Markdown
from rich.table import Table
from rich.text import Text
from rich import print, box
from rich.console import Console


EGERIA_WIDTH = os.getenv("PYEGERIA_CONSOLE_WIDTH", 200)
console = Console(width=EGERIA_WIDTH)

"""

The following definitions are used in creating Exception messages. 
They mirror similar definitions in the Egeria core. 
Note that not all of the definitions are currently used - they merely serve as placeholders for future extensions.

"""
class PyegeriaErrorCode(Enum):
    """Egeria error codes"""
    CLIENT_ERROR = {
        "http_code": 400,
        "egeria_code": "From Egeria",
        "message_id": "CLIENT_ERROR_400",
        "message_template": "Client error occurred accessing `{0}` with status code `{1}`.",
        "system_action": "The client is unable to connect to the Egeria platform.",
        "user_action": "Check the URL to ensure the valid platform url, server, user id are correct.",
    }
    VALIDATION_ERROR = {
        "http_code": 0,
        "egeria_code": "From Egeria",
        "message_id": "VALIDATION_ERROR_1",
        "message_template": "Invalid parameters were provided -> `{0}`.",
        "system_action": "The parameters provided were invalid.",
        "user_action": "Check that your parameters are correct - please see documentation, if unsure.",
        }
    AUTHORIZATION_ERROR = {
        "http_code": 401,
        "pyegeria_code": "From Egeria",
        "message_id": "AUTHORIZATION_ERROR_401",
        "message_template": "User not authorized received for user - `{0}`.",
        "system_action": "The user credentials provided were not authorized.",
        "user_action": "Check that your user credentials are correct - please see documentation, if unsure.",
        }
    AUTHENTICATION_ERROR = {
        "http_code": 403,
        "egeria_code": "From Egeria",
        "message_id": "AUTHENTICATION_ERROR_403",
        "message_template": "User not authenticated received for user - `{0}`.",
        "system_action": "The user credentials provided were not authenticated.",
        "user_action": "Check that your user credentials and token are valid - please see documentation, if unsure.",
        }
    CONNECTION_ERROR = {
        "http_code": 404,
        "egeria_code": "Connection error",
        "message_id": "CONNECTION_ERROR_1",
        "message_template": "Client failed to connect to the Egeria platform using URL `{0}`.",
        "system_action": "The client is unable to connect to the Egeria platform.",
        "user_action": "Check the URL to ensure the valid platform url, server, user id are correct.",
        }
    EGERIA_ERROR = {
        "http_code": 500,
        "egeria_code": "From Egeria",
        "message_id": "SERVER_ERROR_500",
        "message_template": "Egeria detected error: `{0}`.",
        "system_action": "Server-side issue requires attention.",
        "user_action": "Contact server support."
        }

    def __str__(self):
        return (
            "\nhttp_code= "
            + str(self.value["http_code"])
            + "\n\t* messageId= "
            + self.value["message_id"]
            + ",\n\t message= "
            + self.value["message_template"]
            + ",\n\t systemAction= "
            + self.value["system_action"]
            + ",\n\t userAction= "
            + self.value["user_action"]
        )
colors = ["blue", "red", "green"]

def print_bullet_list_colored(items, colors)->Text:
    for i, item in enumerate(items):
        bullet_text = Text(f"\t• ", style="bold yellow")
        wrapped_text = Text(item, style=colors[i % len(colors)])  # Rotate colors
        bullet_text.append(wrapped_text)
    return bullet_text

def print_bullet_list(items)->Text:
    for key, value in items:
        bullet_text = Text(f"\t• {key}", style="bold yellow")
        wrapped_text = Text(value, style= "blue")
        bullet_text.append(wrapped_text)
        console.print(bullet_text)
    return bullet_text


def flatten_dict_to_string(d: dict) -> str:
    """Flatten a dictionary into a string and replace quotes with backticks."""
    try:
        flat_string = "\n\t".join(
            # Change replace(\"'\", '`') to replace("'", '`')
            f"\t* {key}=`{str(value).replace('\"', '`').replace("'", '`')}`"
            for key, value in d.items()
        )
        return flat_string
    except Exception as e:
        # Corrected syntax for exception chaining
        raise Exception("Error flattening dictionary") from e

def format_dict_to_string(d: dict) -> str:
    """
    Converts a dictionary into a printable string of name-value pairs.
    Replaces quotes with backticks and removes braces.

    Args:
        d (dict): The input dictionary.

    Returns:
        str: A formatted printable string.
    """
    if isinstance(d, dict):
        name_value_set = {
            f"`{str(value).replace('\"', '`').replace("'", '`')}`"
            for key, value in d.items()
            }
        # Join the set elements into a single printable string
        return ", ".join(name_value_set)
    else:
        return str(d)


class PyegeriaException(Exception):
    """Base exception for My REST Library errors."""

    def __init__(self, response:Response, error_code: PyegeriaErrorCode,
                 context: dict = None, additional_info:dict = None, e:Exception = None) -> None:
        self.response = response
        self.error_code = error_code
        self.error_details = error_code.value
        self.pyegeria_code = self.error_details.get("message_id", "UNKNOWN_ERROR")
        self.response_url = getattr(response, "url", "unknown URL") if response else additional_info.get("endpoint","")
        self.response_code = getattr(response, "status_code", "unknown status code") if response else ""
        self.message = self.error_details["message_template"].format(self.response_url, self.response_code)
        self.system_action = self.error_details.get("system_action", "")
        self.user_action = self.error_details.get("user_action", "")
        # self.original_exception = context.get("exception", {}) if context else None
        self.context = context
        self.additional_info = additional_info or {}
        self.e = e


    def __str__(self):
        msg = "\n"
        # ctx_str = flatten_dict_to_string(self.context)
        ctx_str = flatten_dict_to_string(self.context)

        msg += f"\n=> \t{self.pyegeria_code}"
        msg += f"\n=>\t{self.message}"
        msg += f"\n\t* Context: \n\t{ctx_str}\n"

        related_http_code = self.additional_info.get('relatedHTTPCode', None)
        if related_http_code:
            if related_http_code != 200:
                msg += f"\t* Egeria error information: \n"
                for key, value in self.additional_info.items():
                    msg += f"\t* {key}= `{str(value).replace('\"', '`').replace("'", '`')}`\n"

        else:
            msg += f"\t* System Action: {self.system_action}\n"
            msg += f"\t* User Action: {self.user_action}\n"
            if self.response:
                msg += f"\t* HTTP Code: {self.response_code}\n"
        return msg


class PyegeriaConnectionException(PyegeriaException):
    """Raised when there's an issue connecting to an Egeria Platform."""
    def __init__(self, context: dict = None, additional_info:dict = None, e: Exception = None) -> None:
        super().__init__(None, PyegeriaErrorCode.CONNECTION_ERROR,
                 context, additional_info, e)
        self.message = self.error_details["message_template"].format(self.response_url)
        logger.error(self.__str__())

class PyegeriaInvalidParameterException(PyegeriaException):
    """Raised for invalid parameters - parameters that might be missing or incorrect."""
    def __init__(self, response: Response,
                 context: dict = None, additional_info: dict = None, e: Exception = None) -> None:
        super().__init__(response, PyegeriaErrorCode.VALIDATION_ERROR,
                         context, additional_info, e)
        self.message = self.error_details["message_template"].format(self.additional_info.get('reason', ''))
        logger.error(self.__str__(), ip=self.response_url, http_code=self.response_code, pyegeria_code=self.pyegeria_code)

class PyegeriaClientException(PyegeriaException):
    """Raised for invalid parameters - parameters that might be missing or incorrect."""
    def __init__(self, response: Response,
                 context: dict = None, additional_info: dict = None, e: Exception = None) -> None:
        # base_exception = context.get('caught_exception', None)
        super().__init__(response, PyegeriaErrorCode.CLIENT_ERROR,
                         context, additional_info, e)
        logger.error(self.__str__(), ip=self.response_url, http_code=self.response_code, pyegeria_code=self.pyegeria_code)


class PyegeriaAPIException(PyegeriaException):
    """Raised for errors reported by Egeria"""
    def __init__(self, response: Response,
                 context: dict = None, additional_info: dict = None, e: Exception = None) -> None:
        super().__init__(response, PyegeriaErrorCode.EGERIA_ERROR,
                         context, additional_info, e)
        related_response = response.json()
        self.related_http_code = related_response.get("relatedHTTPCode", None)
        msg = self.__str__()
        if self.related_http_code:
            exception_msg_id = related_response.get("exceptionErrorMessageId", "UNKNOWN_ERROR")
            msg += f"\n\t{self.error_details['message_template'].format(exception_msg_id)}\n"

            for key, value in related_response.items():
                msg += f"\t\t* {key} = {format_dict_to_string(value)}\n"

        logger.error(msg, ip=self.response_url, http_code=self.response_code, pyegeria_code=self.pyegeria_code)




# class PyegeriaAuthenticationException(PyegeriaException):
#     """Raised for 401 authentication errors."""
#     def __init__(self, response: Response,
#                  context: dict = None, additional_info: dict = None) -> None:
#         super().__init__(response,  PyegeriaErrorCode.AUTHENTICATION_ERROR,
#                          context, additional_info)
#         self.message = self.error_details["message_template"].format(additional_info.get("userid",""))
#         logger.error(self.__str__(), ip=self.response_url, http_code=self.response_code, pyegeria_code=self.pyegeria_code)

class PyegeriaUnauthorizedException(PyegeriaException):
    """Raised for 403 authorization errors."""
    def __init__(self, response: Response,
                 context: dict = None, additional_info: dict = None, e: Exception = None) -> None:
        super().__init__(response, PyegeriaErrorCode.AUTHORIZATION_ERROR,
                         context, additional_info, e)
        self.message = self.error_details["message_template"].format(additional_info.get("userid", ""))
        logger.error(self.__str__(), ip=self.response_url, http_code=self.response_code, pyegeria_code=self.pyegeria_code)



class PyegeriaNotFoundException(PyegeriaException):
    """Raised for 404 Not Found errors."""
    def __init__(self, response: Response,
                 context: dict = None, additional_info: dict = None, e: Exception = None) -> None:
        super().__init__(response, PyegeriaErrorCode.CLIENT_ERROR,
                         context, additional_info, e)
        logger.error(self.__str__(), ip=self.response_url, http_code=self.response_code, pyegeria_code=self.pyegeria_code)


# class PyegeriaInvalidResponseException(PyegeriaException):
#     """Raised when the API returns an unparseable or unexpected response."""
#     def __init__(self, response: Response,
#                  context: dict = None, additional_info: dict = None) -> None:
#         super().__init__(response, PyegeriaErrorCode.CLIENT_ERROR,
#                          context, additional_info)
#         logger.error(self.__str__(), ip=self.response_url, http_code=self.response_code, pyegeria_code=self.pyegeria_code)
#
#
# class PyegeriaValidationException(PyegeriaException):
#     """Raised when data sent to the API fails validation, or received data fails Pydantic validation."""
#
#     def __init__(self, response: Response = None,
#                  context: dict = None, additional_info: dict = None) -> None:
#         super().__init__(response, PyegeriaErrorCode.VALIDATION_ERROR,
#                          context, additional_info)
#         reason = additional_info.get("reason","")
#         input_parameters = additional_info.get("input_parameters","")
#         self.message = self.error_details["message_template"].format(reason, input_parameters)
#         logger.error(self.__str__(), ip=self.response_url, http_code=self.response_code, pyegeria_code=self.pyegeria_code)
#
# class PyegeriaRequestException(PyegeriaException):
#     """Raised when data sent to the API fails validation, or received data fails Pydantic validation."""
#     def __init__(self, response: Response,
#                  context: dict = None, additional_info: dict = None) -> None:
#         super().__init__(response, PyegeriaErrorCode.CLIENT_ERROR,
#                          context, additional_info)
#         logger.error(self.__str__(), ip=self.response_url, http_code=self.response_code, pyegeria_code=self.pyegeria_code)


class PyegeriaUnknownException(PyegeriaException):
    """Raised when data sent to the API fails validation, or received data fails Pydantic validation."""
    def __init__(self, response: Response,
                 context: dict = None, additional_info: dict = None, e: Exception = None) -> None:
        super().__init__(response, PyegeriaErrorCode.CLIENT_ERROR,
                         context, additional_info, e)
        logger.error(self.__str__(), ip=self.response_url, http_code=self.response_code, pyegeria_code=self.pyegeria_code)



def print_exception_response(e: PyegeriaException):
    """Prints the exception response"""
    if isinstance(e, PyegeriaException):
        console.print(Markdown(f"\n---\n# Exception: {e.__class__.__name__}"))
        msg: Text = Text(e.__str__(), overflow="fold")
        if hasattr(e, 'related_http_code') and e.related_http_code:
            related_response = e.response.json()
            exception_msg_id = related_response.get("exceptionErrorMessageId", None)
            if exception_msg_id:
                msg.append( f"\n\t{e.error_details['message_template'].format(exception_msg_id)}\n")

            # for key, value in related_response.items():
            #     msg += f"\t\t* {key} = {print(value)}\n"
            for key, value in related_response.items():
                msg.append( Text(f"\t* {key} =", style = "bold yellow"))
                msg.append(Text( f"\n\t\t{format_dict_to_string(value)}\n", overflow="fold", style = "green"))
        console.print(msg)
    else:
        print(f"\n\n\t  Not an Pyegeria exception {e}")

def print_exception_table(e: PyegeriaException):
    """Prints the exception response"""
    related_code = e.related_http_code if hasattr(e, "related_http_code") else ""
    related_response = e.response.json()
    table = Table(title=f"Exception: {e.__class__.__name__}", show_lines=True, header_style="bold", box=box.HEAVY_HEAD)
    table.caption = e.pyegeria_code
    table.add_column("Facet", justify="center")
    table.add_column("Item", justify="center")

    if isinstance(e, PyegeriaException):
        table.add_row("HTTP Code", str(e.response_code))
        table.add_row("Egeria Code", str(related_code))
        table.add_row("Caller Method", e.context.get("caller method", "---"))
        table.add_row("Request URL", str(e.response_url))
        if e.related_http_code:
            item_table = Table(show_lines = True, header_style="bold")
            item_table.add_column("Item", justify="center")
            item_table.add_column("Detail", justify="left")
            for key, value in related_response.items():
                item_table.add_row(key, format_dict_to_string(value))
            table.add_row("Egeria Details", item_table)




        exception_msg_id = related_response.get("exceptionErrorMessageId", None)
        table.add_row("Pyegeria Exception", exception_msg_id)
        table.add_row("Pyegeria Message",
                      f"\n\t{e.error_details['message_template'].format(exception_msg_id)}\n")


        console.print(table)
    else:
        print(f"\n\n\t  Not an Pyegeria exception {e}")

def print_basic_exception(e: PyegeriaException):
    """Prints the exception response"""
    related_code = e.related_http_code if hasattr(e, "related_http_code") else ""
    related_response = e.response.json()
    table = Table(title=f"Exception: {e.__class__.__name__}", show_lines=True, header_style="bold", box=box.HEAVY_HEAD)
    table.caption = e.pyegeria_code
    table.add_column("Facet", justify="center")
    table.add_column("Item", justify="left", width=80)

    if isinstance(e, PyegeriaException):
        table.add_row("HTTP Code", str(e.response_code))
        table.add_row("Egeria Code", str(related_code))
        table.add_row("Caller Method", e.context.get("caller method", "---"))
        table.add_row("Request URL", str(e.response_url))
        table.add_row("Egeria Message",
                      format_dict_to_string(related_response.get('exceptionErrorMessage',"")))
        table.add_row("Egeria User Action",
                      format_dict_to_string(related_response.get('exceptionUserAction',"")))

        exception_msg_id = related_response.get("exceptionErrorMessageId", None)
        table.add_row("Pyegeria Exception", exception_msg_id)
        table.add_row("Pyegeria Message",
                      f"\n\t{e.error_details['message_template'].format(exception_msg_id)}\n")


        console.print(table)
    else:
        print(f"\n\n\t  Not an Pyegeria exception {e}")