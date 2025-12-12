#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

A simple display for collections
"""
import argparse
import json
import os
import time

from jsonschema import ValidationError
from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
from loguru import logger
from pyegeria import (
    CollectionManager, settings,
    NO_ELEMENTS_FOUND, config_logging, load_app_config, get_app_config, init_logging, config_logging, PyegeriaException,
    print_basic_exception,PyegeriaException, )
from commands.cat.run_report import list_generic
from pyegeria._exceptions import print_validation_error
app_config = settings.Environment

EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
app_settings = get_app_config(app_config.pyegeria_root+"/.env")

config_logging()

console = Console(width=app_config.console_width, force_terminal=(not app_config.egeria_jupyter))

def display_collections(
    search_string: str = "*",
    view_server: str = app_config.egeria_view_server,
    view_url: str = app_config.egeria_view_server_url,
    user: str = app_settings.User_Profile.user_name,
    user_pass: str = app_settings.User_Profile.user_pwd,
    jupyter: bool = app_config.egeria_jupyter,
    width: int = app_config.console_width,
    output_format: str = "TABLE"
):
    """Display either a specified glossary or all collections if the search_string is '*'.
    Parameters
    ----------
    search_string : str, default is '*'
        The string used to search for collections.
    view_server : str
        The view server name or address where the Egeria services are hosted.
    view_url : str
        The URL of the platform the view server is on.
    user : str
        The user ID for authentication with the Egeria server.
    user_pass : str
        The password for authentication with the Egeria server.
    jupyter : bool, optional
        A boolean indicating whether the output is intended for a Jupyter notebook (default is EGERIA_JUPYTER).
    width : int, optional
        The width of the console output (default is EGERIA_WIDTH).
    output_format : str, optional
        Format of the output. Default is TABLE.
    """

    try:
        table_caption = "Basic Collection List"
        list_generic(report_spec="BasicCollections", output_format=output_format, view_server=view_server,
                     view_url=view_url, user=user, user_pass=user_pass, params={"search_string": search_string},
                     render_table=True, write_file=True, table_caption=table_caption, use_pager=True,
                     width=width, jupyter=jupyter, prompt_missing=True)


    except (PyegeriaException) as e:
        print_basic_exception(e)
    except ValidationError as e:
        print_validation_error(e)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")

    args = parser.parse_args()

    server = args.server if args.server is not None else app_config.egeria_view_server
    url = args.url if args.url is not None else app_config.egeria_view_server_url
    userid = args.userid if args.userid is not None else app_settings.User_Profile.user_name
    user_pass = args.password if args.password is not None else app_settings.User_Profile.user_pwd

    try:
        search_string = Prompt.ask(
            "Enter the collection you are looking for or '*' for all:", default="*"
        ).strip()
        output_format = Prompt.ask("Which output format do you want?", choices=["DICT", "TABLE", "FORM", "REPORT", "HTML", "LIST"], default="TABLE")

        display_collections(search_string, server, url, userid, user_pass, output_format = output_format)

    except KeyboardInterrupt:
        pass

    except PyegeriaException as e:
        print_basic_exception(e)
    except ValidationError as e:
        print_validation_error(e)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    # EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
    # EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
    # PYEGERIA_ROOT_PATH = os.environ.get("PYEGERIA_ROOT_PATH", "/Users/dwolfson/localGit/egeria-v5-3/egeria-python")
    main()
