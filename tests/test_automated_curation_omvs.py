"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module is for testing the Automated Curation View Service module.
The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests.

"""
import time

import pytest
import asyncio
import json
from rich import print, print_json
from rich.pretty import pprint

from rich.console import Console
from contextlib import nullcontext as does_not_raise

from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)

from pyegeria import AutomatedCuration, GlossaryBrowser
from pyegeria.utils import print_json_list_as_table

# from pyegeria.admin_services import FullServerConfig

disable_ssl_warnings = True
console = Console()

class TestAutomatedCuration:
    good_platform1_url = "https://localhost:9443"
    good_platform2_url = "https://oak.local:9443"
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


    def test_create_element_from_template(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()
            body = {
                "templateGUID": "5e1ff810-5418-43f7-b7c4-e6e062f9aff7",
                "isOwnAnchor": "true",
                "placeholderPropertyValues": {
                    "serverName": "localKafka5",
                    "hostIdentifier": "localhost",
                    "portNumber": "9092"
                }
            }
            start_time = time.perf_counter()
            response = a_client.create_element_from_template(body)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print("Guid of created element is:" + response)
            assert True

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_create_postgres_element_from_template(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = a_client.create_postgres_server_element_from_template("observations_base",
                                                                             "egeria.pdr-associates.com",
                                                                             "5432", db_user="surveyor",
                                                                             db_pwd="secret")
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list :
                out = ("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                pprint(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                pprint("Database GUID create is " + response)
            assert True

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_get_engine_actions(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = a_client.get_engine_actions()
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list :
                out = ("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)
            assert True

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_get_engine_action(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()
            engine_action_guid = "2374f070-de61-4ba5-959c-2d5621da2a1c"
            start_time = time.perf_counter()
            response = a_client.get_engine_action(engine_action_guid)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict :
                out = ("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)
            assert True

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_cancel_engine_action(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()
            engine_action_guid = "2374f070-de61-4ba5-959c-2d5621da2a1c"
            start_time = time.perf_counter()
            a_client.cancel_engine_action(engine_action_guid)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            pprint(f"Canceled engine action: {engine_action_guid}")
            assert True

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_get_active_engine_actions(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = a_client.get_active_engine_actions()
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list :
                out = ("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                print(f"Found {count} elements")
                print_json(out)
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
            a_client.close_session()

    def test_get_engine_actions_by_name(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = a_client.get_engine_actions_by_name("survey-folder:AssetSurvey")
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict :
                out = ("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)
            assert True

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_find_engine_actions(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = a_client.find_engine_actions()
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list :
                out = ("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)
            assert True

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

#
#   Governance Processes
#
    def test_get_governance_action_process_by_guid(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()
            action_guid = "2374f070-de61-4ba5-959c-2d5621da2a1c"
            start_time = time.perf_counter()
            response = a_client.get_governance_action_process_by_guid(action_guid)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict :
                out = ("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)
            assert True

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

#
#   Get Technology types
#
    def test_get_all_technology_types(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = a_client.get_all_technology_types()
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                out = ("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_find_technology_types(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = a_client.find_technology_types("postgres", ignore_case=True)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                out = ("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_get_technology_types_for_open_metadata_type(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = a_client.get_tech_types_for_open_metadata_type("SoftwareServer","PostgreSQL")
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                out = ("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_get_technology_type_detail(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = a_client.get_technology_type_details("PostgreSQL Server")
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict:
                out = ("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)
            assert True

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

#
#   Governance Actions
#
    def test_initiate_gov_action_type(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            gov_action_type_qn = "Egeria:GovernanceActionType:2adeb8f1-0f59-4970-b6f2-6cc25d4d2402survey-folder"

            response = a_client.initiate_gov_action_type("PostgreSQL Server")
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict:
                out = ("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)
            assert True

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()