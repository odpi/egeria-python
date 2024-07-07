"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module is for testing the core OMAG config class and methods
The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests.

"""
import time

import pytest
import asyncio
import json
import rich
from rich import console, print_json
from rich.console import Console
from contextlib import nullcontext as does_not_raise
from pyegeria.my_profile_omvs import MyProfile
from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)

from pyegeria.core_omag_server_config import CoreServerConfig

from pyegeria.glossary_browser_omvs import GlossaryBrowser
from pyegeria.utils import print_json_list_as_table

# from pyegeria.admin_services import FullServerConfig

disable_ssl_warnings = True


class TestMyProfile:
    good_platform1_url = "https://127.0.0.1:9443"
    good_platform2_url = "https://cray.local:9443"
    bad_platform1_url = "https://localhost:9443"

    # good_platform1_url = "https://127.0.0.1:30080"
    # good_platform2_url = "https://127.0.0.1:30081"
    # bad_platform1_url = "https://localhost:9443"

    good_user_1 = "garygeeke"
    good_user_2 = "erinoverview"
    good_user_3 = "peterprofile"
    bad_user_1 = "eviledna"
    bad_user_2 = ""
    good_integ_1 = "fluffy_integration"
    good_server_1 = "simple-metadata-store"
    good_server_2 = "laz_kv"
    good_server_3 = "active-metadata-store"
    good_server_4 = "integration-daemon"
    good_server_5 = "fluffy_kv"
    good_server_6 = "cocoVIew1"
    good_engine_host_1 = "governDL01"
    good_view_server_1 = "view-server"
    good_view_server_2 = "fluffy_view"
    bad_server_1 = "coco"
    bad_server_2 = ""

    def test_get_my_profile(self):
        try:
            m_client = MyProfile(self.good_view_server_1, self.good_platform1_url,
                                       user_id=self.good_user_2)

            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")

            response = m_client.get_my_profile()

            # resp_str = json.loads(response)
            id_list = []
            if type(response) is dict:
                print_json(data = response)
            elif type(response) is str:
                print("\n\n" + response)
            assert True

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            m_client.close_session()

    def test_get_assigned_actions(self, server_name:str= good_view_server_1):
        console = Console()
        try:
            m_client = MyProfile(server_name, self.good_platform1_url,
                                 user_id=self.good_user_2)

            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")
            actor = "a588fb08-ae09-4415-bd5d-991882ceacba"

            response = m_client.get_assigned_actions(actor)

            if type(response) is list:
                print(f"Number of assigned actions: {len(response)}")
                print_json(data=response)
            elif type(response) is str:
                console.print("\n\n\t Response is " + response)
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            console.print_exception(show_locals= True)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_get_actions_for_sponsor(self, server_name:str= good_view_server_1):
        console = Console()
        try:
            m_client = MyProfile(server_name, self.good_platform1_url,
                                 user_id=self.good_user_2)

            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")
            element_guid = "a588fb08-ae09-4415-bd5d-991882ceacba"

            response = m_client.get_actions_for_sponsor(element_guid)

            if type(response) is list:
                print_json(data=response)
            elif type(response) is str:
                console.print("\n\n\t Response is" + response)
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            console.print_exception(show_locals= True)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_create_to_do(self, server_name:str = good_view_server_1):
        try:
            m_client = MyProfile(server_name, self.good_platform1_url,
                                 user_id=self.good_user_2)

            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")
            erins_guid = "a588fb08-ae09-4415-bd5d-991882ceacba"
            to_do = "Mandy will delegate the Latte to Peter"
            to_do_desc = "Latte to go"
            to_do_type = "drink"
            body = {
                        "properties": {
                            "class" : "ToDoProperties",
                            "qualifiedName": f"Test-To-Do-{time.asctime()}",
                            "name": to_do,
                            "description": to_do_desc,
                            "toDoType": to_do_type,
                            "priority": 0,
                            "dueTime": "2024-03-11T15:42:11.307Z",
                            "status": "OPEN"
                        },
                    "assignToActorGUID": erins_guid
            }
            # print(json.dumps(body,indent=4))
            response = m_client.create_to_do(body)

            print(f"\n\n\t To-Do {to_do} created successfully with response:")
            if type(response) is dict:
                print_json(data=response, indent=4)
            else: print(response)
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_get_to_do(self, server_name: str = good_view_server_1):
        console = Console()
        try:
            m_client = MyProfile(server_name, self.good_platform1_url,
                                 user_id=self.good_user_2)

            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")
            todo_guid = "97d1977e-c0d5-49a9-996b-4b73ce0517be"
            # 10a5e593-cc8a-45d0-a191-d060656363e9
            response = m_client.get_to_do(todo_guid, server_name)

            if type(response) is dict:
                print_json(data=response)
            elif type(response) is str:
                console.print("\n\n\t Response is" + response)
            assert True

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            console.print_exception(show_locals=True)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_find_to_do(self, server_name: str = good_view_server_1):
        console = Console()
        try:
            m_client = MyProfile(server_name, self.good_platform1_url,
                                 user_id=self.good_user_2)

            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")

            response = m_client.find_to_do(" ")

            if type(response) is list:
                print(f"Found {len(response)} todos that matched the criteria")

                print_json(data=response)
            elif type(response) is str:
                console.print("\n\n\t Response is " + response)
            assert True

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            console.print_exception(show_locals=True)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_get_to_dos_by_type(self, server_name: str = good_view_server_1):
        console = Console()
        try:
            m_client = MyProfile(server_name, self.good_platform1_url,
                                 user_id=self.good_user_2)

            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")

            response = m_client.get_to_dos_by_type("drink", server_name, status=None)

            if type(response) is list:
                print_json(data=response)
            elif type(response) is str:
                console.print("\n\n\t Response is \n" + response)
            assert True

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            console.print_exception(show_locals=True)
            assert False, "Invalid request"

        finally:
            m_client.close_session()