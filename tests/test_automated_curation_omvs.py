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
                    "serverName": "localKafka6",
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

    def test_create_kafka_server_element_from_template(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = a_client.create_kafka_server_element_from_template("pdr-kafka",
                                                                             "egeria.pdr-associates.com",
                                                                             "9092")
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list :
                out = ("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                pprint(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                pprint("Kafka Server GUID create is " + response)
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

    def test_create_postgres_server_element_from_template(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = a_client.create_postgres_server_element_from_template("egeria-pdr",
                                                                             "egeria.com",
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
                pprint("Database Server GUID create is " + response)
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
            print(f"The type of response is: {type(response)}")
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
            response = a_client.get_engine_actions_by_name("JDBCDatabaseCataloguer")
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n Type of response is {type(response)}")
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

    def test_find_engine_actions(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = a_client.find_engine_actions("Downloads")
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

    def test_get_gov_action_process_graph(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()
            action_guid = "2374f070-de61-4ba5-959c-2d5621da2a1c"
            start_time = time.perf_counter()
            response = a_client.get_gov_action_process_graph(action_guid)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n Type of response is {type(response)}")
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

    def test_get_gov_action_process_by_name(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()
            name = "Survey"
            start_time = time.perf_counter()
            response = a_client.get_gov_action_processes_by_name(name)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n Type of response is {type(response)}")
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

    def test_find_gov_action_processes(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()
            name = "Survey"
            start_time = time.perf_counter()
            response = a_client.find_gov_action_processes(name)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n Type of response is {type(response)}")
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

    def test_initiate_gov_action_process(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()
            action_type_qualified_name = ""
            start_time = time.perf_counter()
            request_source_guids = None
            action_targets = None
            request_parameters = None
            orig_service_name = None
            orig_engine_name = None

            response = a_client.initiate_gov_action_process(action_type_qualified_name,request_source_guids,
                                                            action_targets, start_time, request_parameters,
                                                            orig_service_name, orig_engine_name)

            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n Type of response is {type(response)}")
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

    def test_get_gov_action_types_by_guid(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()
            gov_action_guid = ""
            start_time = time.perf_counter()
            response = a_client.get_gov_action_types_by_guid(gov_action_guid)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n Type of response is {type(response)}")
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

    def test_get_gov_action_types_by_name(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()
            name = "Egeria:GovernanceActionType:2adeb8f1-0f59-4970-b6f2-6cc25d4d2402survey-folder"
            start_time = time.perf_counter()
            response = a_client.get_gov_action_types_by_name(name)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n Type of response is {type(response)}")
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

    def test_find_gov_action_types(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()
            search_string = "AssetSurvey"
            start_time = time.perf_counter()
            response = a_client.find_gov_action_types(search_string)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n Type of response is {type(response)}")
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
            response = a_client.find_technology_types("*", starts_with=True,ignore_case=True)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"Type of response was {type(response)}")
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
            response = a_client.get_technology_type_detail("FileFolder")
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

    def test_get_catalog_target(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()
            postgres_server_connector_guid = "36f69fd0-54ba-4f59-8a44-11ccf2687a34"
            element_guid = "852b2e56-b68d-40a1-b5ac-ef0d1c62cc7a"
            start_time = time.perf_counter()
            # gov_action_type_qn = "Egeria:GovernanceActionType:2adeb8f1-0f59-4970-b6f2-6cc25d4d2402survey-folder"

            response = a_client.get_catalog_target(postgres_server_connector_guid,element_guid)
            duration = time.perf_counter() - start_time
            print(f"Type of response was {type(response)}")
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

    def test_get_catalog_targets(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()
            postgres_server_connector_guid = "36f69fd0-54ba-4f59-8a44-11ccf2687a34"
            folder_connector_guid = "d13ba229-d406-43f7-b395-9462b7d98900"
            element_guid = "852b2e56-b68d-40a1-b5ac-ef0d1c62cc7a"
            start_time = time.perf_counter()
            response = a_client.get_catalog_targets(folder_connector_guid)
            duration = time.perf_counter() - start_time
            print(f"Type of response was {type(response)}")
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

    def test_add_catalog_targets(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()
            jdbc_database_connector_guid = "70dcd0b7-9f06-48ad-ad44-ae4d7a7762aa"
            postgres_connector_guid = "36f69fd0-54ba-4f59-8a44-11ccf2687a34"
            element_guid = "64296369-323f-4d74-aab3-c2ebae923d25"
            catalog_target_name = "coco_ods_catalog_target"
            start_time = time.perf_counter()
            a_client.add_catalog_target(postgres_connector_guid,
                                                   element_guid, catalog_target_name)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
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

    def test_catalog_folder_files(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()
            # jdbc_database_connector_guid = "70dcd0b7-9f06-48ad-ad44-ae4d7a7762aa"
            # postgres_connector_guid = "36f69fd0-54ba-4f59-8a44-11ccf2687a34"
            folder_guid = "289172e5-d5f5-4673-854c-847192f2eaef"
            catalog_target_name = "Dan's Downloads Folder"
            file_connector_guid = "d13ba229-d406-43f7-b395-9462b7d98900"
            # element_guid = "64296369-323f-4d74-aab3-c2ebae923d25"
            # catalog_target_name = "coco_ods_catalog_target"
            start_time = time.perf_counter()
            a_client.add_catalog_target(file_connector_guid,
                                                   folder_guid, catalog_target_name)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
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


    def test_remove_catalog_target(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()
            postgres_server_connector_guid = "36f69fd0-54ba-4f59-8a44-11ccf2687a34"
            folder_connector_guid = "d13ba229-d406-43f7-b395-9462b7d98900"
            element_guid = "20f6827f-9e0c-4c42-9b9f-acb5894a2970"
            catalog_target_name = "Egeria Postgres Server"

            start_time = time.perf_counter()

            a_client.remove_catalog_target(folder_connector_guid,
                                                   element_guid)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
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
            a_postgres_server_guid = "64296369-323f-4d74-aab3-c2ebae923d25"
            start_time = time.perf_counter()

            response = a_client.initiate_postgres_server_survey(a_postgres_server_guid)
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

    def test_initiate_postgres_database_survey(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()
            a_postgres_database_guid = "78cf662f-c91d-44f9-aefe-61015d045c37"

            start_time = time.perf_counter()

            response = a_client.initiate_postgres_database_survey(a_postgres_database_guid)
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
            file_folder_guid = "289172e5-d5f5-4673-854c-847192f2eaef"
            response = a_client.initiate_file_folder_survey(file_folder_guid)
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

    def test_initiate_file_survey(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            file_guid = "9dbb47d9-4ca9-404e-b02d-2e049e6e6c6e"
            response = a_client.initiate_file_survey(file_guid)
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
