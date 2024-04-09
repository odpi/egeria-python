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
    good_platform1_url = "https://cray.local:9443"


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

    def test_create_kafka_element_from_template(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()

            response = a_client.create_kafka_server_element_from_template(kafka_server="pdr-kafka-server",
                                                                          host_name='egeria.pdr-associates.com',
                                                                          port='9092')
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict:
                out = ("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\nGUID is: " + response)
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

            response = a_client.create_postgres_server_element_from_template(postgres_server="egeriadashboard",
                                                                             host_name='egeria.pdr-associates.com',
                                                                             port="5432",
                                                                             db_user="surveyor",
                                                                             db_pwd='secret')
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict:
                out = ("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\nGUID is: " + response)
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
    # Engine Functions
    #
    def test_get_engine_actions(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()

            response = a_client.get_engine_actions()
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                out = ("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\nGUID is: " + response)
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

    def test_initiate_file_folder_survey(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            folder_guid = "9f547ca9-3b23-45cb-a6dd-1f7e317e4336"

            response = a_client.initiate_file_folder_survey(folder_guid)
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

    def test_initiate_postgres_server_survey(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            postgres_server_guid = "a095cb16-c108-40cf-b7bb-bfda003ea60b"

            response = a_client.initiate_postgres_server_survey(postgres_server_guid)
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

    def test_initiate_kafka_server_survey(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            kafka_server_guid = " d744474c-54ee-47b8-bc46-3cac9662f489"

            response = a_client.initiate_kafka_server_survey(kafka_server_guid)
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

    if __name__ == "__main__":
        try:
            a_client = AutomatedCuration(good_view_server_1, good_platform1_url,
                                         user_id=good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = a_client.create_postgres_server_element_from_template("cray-server",
                                                                             "egeria.pdr-associates.com",
                                                                             "5432", db_user="surveyor",
                                                                             db_pwd="secret")
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")

            pprint("Database Server GUID is " + response)

            a_client.initiate_gov_action_type("PostgreSQL Server")
        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()