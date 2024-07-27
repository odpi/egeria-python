"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

General utility functions in support of the Egeria Python Client package.

"""
import json
from rich import print, print_json
from datetime import datetime
from rich.console import Console

console = Console(width=200)

# def wrap_text(df: pd.DataFrame, wrap_len: int = 30) -> pd.DataFrame:
#     """ Wrap the text in a dataframe
#     Parameters
#     ----------
#     df : pandas.DataFrame
#         The DataFrame to wrap the text in.
#     wrap_len : int, optional
#         The maximum length of each cell's contents to wrap. Defaults to 30.
#
#     Returns
#     -------
#     pandas.DataFrame
#         A new DataFrame with the wrapped text.
#
#     """
#
#     # Helper function to wrap text in a particular cell
#     def wrap_cell_contents(cell_contents: str, wrap: int = 30) -> str:
#         """ Wrap the text in a cell
#         Parameters
#         ----------
#         cell_contents : str or any
#             The contents of a cell in a dataframe.
#         wrap : int, optional
#             The maximum width at which to wrap the cell contents. Default is 30.
#
#         Returns
#         -------
#         str or any
#             If the cell_contents is a string and its length is greater than wrap_len,
#             the contents are wrapped at wrap_len width using textwrap.
#             Otherwise, the original cell_contents are returned as is.
#         """
#         if isinstance(cell_contents, str) and len(cell_contents) > wrap:
#             return textwrap.fill(cell_contents, width=wrap)
#         else:
#             return cell_contents
#
#     # Apply the helper function to each element in the DataFrame
#     return df.map(lambda x: wrap_cell_contents(x, wrap_len))
#
#
# def print_nice_table(df, wrap_len: int = 20, tablefmt: str = "grid") -> None:
#     """ Print a nice table from the data frame"""
#     print(tabulate(wrap_text(df, wrap_len), headers="keys", tablefmt=tablefmt))
#
#
# def get_json_as_table(input_json, wrap_len: int = 30, tablefmt: str = "grid") -> str:
#     """ return the input json as a table"""
#     data = json.loads(json.dumps(input_json))
#     df = pd.json_normalize(data)
#     return tabulate(wrap_text(df, wrap_len), headers="keys", tablefmt=tablefmt)
#
#
# def print_json_list_as_table(input_json, wrap_len: int = 30, tablefmt: str = "grid") -> None:
#     """ print a json list as a table"""
#     data = json.loads(json.dumps(input_json))
#     df = pd.json_normalize(data)
#     print(tabulate(wrap_text(df, wrap_len), headers="keys", tablefmt=tablefmt))


def print_rest_request_body(body):
    """

    Args:
        body:
    """
    pretty_body = json.dumps(body, indent=4)
    print_json(pretty_body, indent=4, sort_keys=True)


def print_rest_response(response):
    """

    Args:
        response:
    """
    print("Returns:")
    pretty_body = json.dumps(response, indent=4)
    print_json(pretty_body, indent=4, sort_keys=True)


def print_guid_list(guids):
    """Print a list of guids"""
    if guids is None:
        print("No assets created")
    else:
        pretty_guids = json.dumps(guids, indent=4)
        print_json(pretty_guids, indent=4, sort_keys=True)


#
# OCF Common services
# Working with assets - this set of functions displays assets returned from the open metadata repositories.
#


def print_response(response):
    """

    Args:
        response:

    Returns:
        : str
    """
    pretty_response = json.dumps(response.json(), indent=4)
    print(" ")
    print("Response: ")
    print(pretty_response)
    print(" ")


def print_unexpected_response(
        server_name, platform_name, platform_url, response
):
    """

    Args:
        server_name:
        platform_name:
        platform_url:
        response:
    """
    if response.status_code == 200:
        related_http_code = response.json().get("related_http_code")
        if related_http_code == 200:
            print("Unexpected response from server " + server_name)
            print_response(response)
        else:
            exceptionErrorMessage = response.json().get("exceptionErrorMessage")
            exceptionSystemAction = response.json().get("exceptionSystemAction")
            exceptionUserAction = response.json().get("exceptionUserAction")
            if exceptionErrorMessage is not None:
                print(exceptionErrorMessage)
                print(" * " + exceptionSystemAction)
                print(" * " + exceptionUserAction)
            else:
                print("Unexpected response from server " + server_name)
                print_response(response)
    else:
        print(
            "Unexpected response from server platform "
            + platform_name
            + " at "
            + platform_url
        )
        print_response(response)


def get_last_guid(guids):
    """

    Args:
        guids:

    Returns:

    """
    if guids is None:
        return None
    else:
        return guids[-1]


def body_slimmer(body: dict) -> dict:
    """ body_slimmer is a little function to remove unused keys from a dict

    Parameters
    ----------
    body : the dictionary that you want to slim

    Returns
    -------
    dict:
        a slimmed body
    """
    slimmed = {key: value for key, value in body.items() if value}
    return slimmed

