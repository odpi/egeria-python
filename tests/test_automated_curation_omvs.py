"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module is for testing the Automated Curation View Service module. We assume that the Core Content Pack
has been loaded.

The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests.

"""

import json
import time
from datetime import datetime

from pydantic import ValidationError
from rich import print, print_json
from rich.console import Console
from rich.pretty import pprint

from pyegeria import AutomatedCuration, PyegeriaException, print_basic_exception, \
    print_validation_error, PyegeriaAPIException, EgeriaTech
from pyegeria._exceptions import (
    PyegeriaInvalidParameterException,
    PyegeriaAPIException,
    PyegeriaUnauthorizedException,
    print_basic_exception as print_exception_response,
)

# from pyegeria.admin_services import FullServerConfig

disable_ssl_warnings = True
console = Console(width=200)


class TestAutomatedCuration:
    good_platform1_url = "https://localhost:9443"

    good_user_1 = "garygeeke"
    good_user_2 = "erinoverview"
    good_user_3 = "peterprofile"
    bad_user_1 = "eviledna"
    bad_user_2 = ""

    good_server_1 = "simple-metadata-store"
    good_server_2 = "laz_kv"
    good_server_3 = "active-metadata-store"
    good_server_4 = "integration-daemon"

    good_engine_host_1 = "governDL01"
    good_view_server_1 = "view-server"
    good_view_server_2 = "qs-view-server"
    bad_server_1 = "coco"
    bad_server_2 = ""

    def test_create_element_from_template(self):
        try:
            a_client = AutomatedCuration(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token()
            # body = {"templateGUID": "379e6c05-9cfa-4d31-a837-0ed4eee6482a", "isOwnAnchor": "true",
            #     "placeholderPropertyValues": {"pathName": "/Users/dwolfson/localGit/datahub",
            #         "deployedImplementationType": "File Folder", "folderName": "Sample Data"}}
            # body for a omag server
            body = {
                "templateGUID": "1764a891-4234-45f1-8cc3-536af40c790d",
                "isOwnAnchor": True,
                "placeholderPropertyValues": {
                    "userId": "garygeeke",
                    "hostURL": "https://localhost",
                    "portNumber": "9446",
                    "serverName": "Survey Engine Host",
                },
            }
            start_time = time.perf_counter()
            response = a_client.create_elem_from_template(body)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print("Guid of created element is:" + str(response))
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_create_folder_asset(self) -> str:
        try:
            a_client = AutomatedCuration(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token()
            path_name = "/deployments/loading-bay"
            folder_name = "loading-bay"
            file_system = None
            description = "Loading bay folder"
            version = "0.1"
            start_time = time.perf_counter()
            response = a_client.create_folder_element_from_template(
                path_name, folder_name, "laz.local", description, version
            )
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                out = "\n\n" + json.dumps(response, indent=4)
                count = len(response)
                pprint(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                pprint("created folder with GUID: " + response)
            assert True

        except (
            PyegeriaException, PyegeriaAPIException,
        ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_create_kafka_server_element_from_template(self):
        try:
            a_client = AutomatedCuration(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = a_client.create_kafka_server_element_from_template(
                "pdr-kafka5", "egeria.pdr-associates.com", "9093"
            )
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                out = "\n\n" + json.dumps(response, indent=4)
                count = len(response)
                pprint(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                pprint("created Kafka Server with GUID: " + response)
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()


    def test_create_kafka_element_from_template(self):
        try:
            a_client = AutomatedCuration(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = a_client.create_kafka_server_element_from_template(
                "pdr-kafka5", "egeria.pdr-associates.com", "9093"
            )
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                out = "\n\n" + json.dumps(response, indent=4)
                count = len(response)
                pprint(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                pprint("created Kafka Server with GUID: " + response)
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_create_csv_data_file_element_from_template(self):
        try:
            a_client = AutomatedCuration(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()

            # response = a_client.create_csv_data_file_element_from_template(
            #     "raw emission factor data.csv",
            #     "CSV",
            #     "/deployments/loading-bay/Sustainability Files/raw emission factor data.csv",
            #     "2022-6-digit",
            #     "UTF-8",
            #     "csv",
            #     "",
            #     "NAICS was originally developed to provide a consistent framework for the collection, analysis, and dissemination of industrial statistics used by government policy analysts, by academics and researchers, by the business community, and by the public. Revisions for 2022 were made to account for our rapidly changing economies"
            # )
            #
            response = a_client.create_csv_data_file_element_from_template(
                "raw emission factor data.csv",
                "CSV",
                "/loading-bay/Sustainability Files/raw emission factor data.csv",
                None,
                "UTF-8",
                "csv",
                None,
                "Raw emissions factor data for deriving standard emissions from different fuels and sources"
            )
            # response = a_client.create_csv_data_file_element_from_template(
            #     "NAICS-6-digit_2022_Codes.csv",
            #     "CSV",
            #     "/loading-bay/Sustainability Files/NAICS-6-digit_2022_Codes.csv",
            #     "2022",
            #     "UTF-8",
            #     "csv",
            #     "",
            #     "NAICS was originally developed to provide a consistent framework for the collection, analysis, and dissemination of industrial statistics used by government policy analysts, by academics and researchers, by the business community, and by the public. Revisions for 2022 were made to account for our rapidly changing economies"
            # )

            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                out = "\n\n" + json.dumps(response, indent=4)
                count = len(response)
                pprint(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                pprint("Database Server GUID create is " + response)
            assert True

        except (
            PyegeriaException, PyegeriaAPIException
        ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
        finally:
            a_client.close_session()

    def test_create_postgres_database_element_from_template(self):
        try:
            a_client = AutomatedCuration(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = a_client.create_postgres_database_element_from_template(
                "egeria",
                "LocalPostgreSQL",
                "host.docker.internal",
                "5442",
                db_user="egeria_user",
                db_pwd="user4egeria",
                description="Egeria Repository"
            )
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                out = "\n\n" + json.dumps(response, indent=4)
                count = len(response)
                pprint(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                pprint("Database Server GUID create is " + response)
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_create_uc_server_element_from_template(self):
        try:
            a_client = AutomatedCuration(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = a_client.create_uc_server_element_from_template(
                "laz3", "http://host.docker.internal", "8080", "my test uc", "0.1"
            )
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                out = "\n\n" + json.dumps(response, indent=4)
                count = len(response)
                pprint(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                pprint("UC Server GUID create is " + response)
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_get_engine_actions(self):
        try:
            a_client = AutomatedCuration(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token()


            start_time = time.perf_counter()
            response = a_client.get_active_engine_actions()
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"The type of response is: {type(response)}")
            if type(response) is list:
                out = "\n\n" + json.dumps(response, indent=4)
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)
            assert True

        except (
            PyegeriaException
        ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_get_engine_action(self):
        try:
            a_client = AutomatedCuration(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token()
            engine_action_guid = "3034d5f3-2cf1-420a-8b64-103079570659"
            start_time = time.perf_counter()
            response = a_client.get_engine_action(engine_action_guid)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict:
                out = "\n\n" + json.dumps(response, indent=4)
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_cancel_engine_action(self):
        try:
            a_client = AutomatedCuration(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token()
            engine_action_guid = ""
            start_time = time.perf_counter()
            a_client.cancel_engine_action(engine_action_guid)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            pprint(f"Canceled engine action: {engine_action_guid}")
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_get_active_engine_actions(self):
        try:
            a_client = AutomatedCuration(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token("peterprofile","secret")

            start_time = time.perf_counter()
            response = a_client.get_active_engine_actions()
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                out = "\n\n" + json.dumps(response, indent=4)
                count = len(response)
                print(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                print("\n\n" + response)
            assert True

        except (
            PyegeriaException
        ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_get_engine_actions_by_name(self):
        try:
            a_client = AutomatedCuration(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = a_client.get_engine_actions_by_name("JDBCDatabaseCataloguer")
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n Type of response is {type(response)}")
            if type(response) is list:
                out = "\n\n" + json.dumps(response, indent=4)
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_find_engine_actions(self):
        try:
            a_client = AutomatedCuration(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = a_client.find_engine_actions("*", output_format = "DICT", report_spec = "Referenceable")
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                out = "\n\n" + json.dumps(response, indent=4)
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                out = "\n\n" + json.dumps(response, indent=4)
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)
            assert True

        except (
            PyegeriaException
        ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    #
    #   Governance Processes
    #


    def test_initiate_gov_action_process(self):
        try:
            a_client = AutomatedCuration(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token()
            action_type_qualified_name = "Egeria:DailyGovernanceActionProcess"
            start_time = time.perf_counter()
            # start_time_now: datetime = datetime.now()
            start_time_now = None
            request_source_guids = None
            action_targets = None
            request_parameters = None
            orig_service_name = None
            orig_engine_name = None

            response = a_client.initiate_gov_action_process(
                action_type_qualified_name,
                request_source_guids,
                action_targets,
                start_time_now,
                request_parameters,
                orig_service_name,
                orig_engine_name,
            )

            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n Type of response is {type(response)}")
            if type(response) is dict:
                out = "\n\n" + json.dumps(response, indent=4)
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_get_gov_action_types_by_guid(self):
        try:
            a_client = AutomatedCuration(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token()
            gov_action_guid = ""
            start_time = time.perf_counter()
            response = a_client.get_gov_action_types_by_guid(gov_action_guid)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n Type of response is {type(response)}")
            if type(response) is dict:
                out = "\n\n" + json.dumps(response, indent=4)
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_get_gov_action_types_by_name(self):
        try:
            a_client = AutomatedCuration(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token()
            name = "AssetSurvey:survey-kafka-server"
            start_time = time.perf_counter()
            response = a_client.get_gov_action_types_by_name(name)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n Type of response is {type(response)}")
            if type(response) is list:
                out = "\n\n" + json.dumps(response, indent=4)
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()



    #   Get Technology types
    #

    def test_get_all_technology_types(self):
        try:
            a_client = AutomatedCuration(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = a_client.get_all_technology_types(output_format = "JSON", report_spec = "Referenceable")
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                out = "\n\n" + json.dumps(response, indent=4)
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)
            assert True

        except (
            PyegeriaException
        ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_find_technology_types(self):
        try:
            a_client = AutomatedCuration(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = a_client.find_technology_types(
                "PostgreSQL", starts_with=True, ignore_case=True, output_format = "JSON", report_spec = "Tech-Types"
            )
            duration = time.perf_counter() - start_time
            print(f"\n\t# Elements was {len(response)} with {duration:.2f} seconds")
            print(f"Type of response was {type(response)}")
            if type(response) is list:
                out = "\n\n" + json.dumps(response, indent=4)
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)
            assert True

        except (
            PyegeriaException
        ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)

        finally:
            a_client.close_session()

    def test_get_technology_types_for_open_metadata_type(self):
        try:
            a_client = AutomatedCuration(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id="peterprofile",
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = a_client.get_tech_types_for_open_metadata_type(
                "SoftwareServer", "Database", output_format = "JSON", report_spec = "Referenceable"
            )
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                out = "\n\n" + json.dumps(response, indent=4)
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)
            assert True

        except (
            PyegeriaException
        ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_get_tech_type_detail(self):
        try:
            a_client = AutomatedCuration(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            # response = a_client.get_tech_type_detail("CSV Data File", True)
            response = a_client.get_tech_type_detail("PostgreSQL Relational Database", output_format="TABLE",
                                                     report_spec="Tech-Type-Processes")
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                out = "\n\n" + json.dumps(response, indent=4)
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)

            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict:
                out = "\n\n" + json.dumps(response, indent=4)
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_get_tech_type_hierarchy(self):
        try:
            a_client = AutomatedCuration(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token()
            # tech_type = "PostgreSQL Server"
            tech_type = "*"
            start_time = time.perf_counter()
            response = a_client.get_tech_type_hierarchy(tech_type, output_format="JSON",
                                                     report_spec="Tech-Type-Details")
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if isinstance(response, list | dict):
                out = "\n\n" + json.dumps(response, indent=4)
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)

            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict:
                out = "\n\n" + json.dumps(response, indent=4)
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_get_template_guid_for_technology_type(self):
        try:
            a_client = AutomatedCuration(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = a_client.get_template_guid_for_technology_type("File System",)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict:
                out = "\n\n" + json.dumps(response, indent=4)
                count = len(response)
                print(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                print("\nTemplate GUID is: " + response)
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
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
            a_client = AutomatedCuration(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            gov_action_type_qn = "Egeria:GovernanceActionType:2adeb8f1-0f59-4970-b6f2-6cc25d4d2402survey-folder"

            response = a_client.initiate_gov_action_type("PostgreSQL Server")
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict:
                out = "\n\n" + json.dumps(response, indent=4)
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_get_catalog_target(self):
        try:
            a_client = AutomatedCuration(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token()

            unity_sync_guid = "06d068d9-9e08-4e67-8c59-073bbf1013af"
            u2 = "ec069de6-5755-45cd-8b78-9c76452a060f"
            element_guid = "731eb432-e9e9-482a-86fc-0a7407ea78e6"
            rel_guid = "19a5fc39-f928-4a78-8637-ade37e0c5598"
            start_time = time.perf_counter()
            target_relationship = "8f730d8e-96a4-44ca-ad6f-2888c181ec3b"
            response = a_client.get_catalog_target(target_relationship)
            duration = time.perf_counter() - start_time
            duration = time.perf_counter() - start_time
            print(f"Type of response was {type(response)}")
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict:
                out = "\n\n" + json.dumps(response, indent=4)
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)
            assert True

        except (
            PyegeriaException, PyegeriaAPIException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()



    def test_get_catalog_targets(self):
        try:
            a_client = AutomatedCuration(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token()
            postgres_server_connector_guid = a_client.get_connector_guid('PostgreSQLServerCataloguer')

            element_guid = "061a4fb3-7d41-4e52-9080-65e9c61084d2"
            relationship_guid = "6be6e470-7aa2-4f50-8142-246866037523"
            # t = INTEGRATION_GUIDS['SampleDataFilesMonitor']
            t = a_client.get_connector_guid('UnityCatalogServerSynchronizer')
            # t = INTEGRATION_GUIDS["UnityCatalogServerSynchronizer"]
            start_time = time.perf_counter()

            response = a_client.get_catalog_targets(postgres_server_connector_guid)
            duration = time.perf_counter() - start_time
            print(f"Type of response was {type(response)}")
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                out = "\n\n" + json.dumps(response, indent=4)
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                print(f"\n\nfor {t} got response {response} ")
            assert True

        except (
            PyegeriaException
        ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_add_catalog_target(self):
        try:
            a_client = AutomatedCuration(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token()
            element_guid = "ff0aec48-b3c8-4732-a0da-5ab4596c2a60"
            catalog_target_name = "exchange-folder"
            postgres_con_guid = ""
            start_time = time.perf_counter()
            connector_guid = a_client.get_connector_guid('PostgreSQLServer')
            guid = a_client.add_catalog_target(
                connector_guid, element_guid, catalog_target_name
            )
            duration = time.perf_counter() - start_time
            print(f"guid returned is: {guid}")
            print(f"\n\tDuration was {duration} seconds")
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_update_catalog_targets(self):
        try:
            a_client = AutomatedCuration(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token()
            element_guid = "001927b1-b960-48c6-a99e-73b6957c259d"
            catalog_target_name = "deltalake experiments on laz"
            file_folder_integ_con = "cd6479e1-2fe7-4426-b358-8a0cf70be117"
            relationship_guid = "2ec7af3f-1d1e-4d5d-85a4-15c62480b898"
            start_time = time.perf_counter()
            guid = a_client.update_catalog_target(
                relationship_guid, catalog_target_name
            )
            duration = time.perf_counter() - start_time
            print(f"guid returned is: {guid}")
            print(f"\n\tDuration was {duration} seconds")
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_catalog_folder_files(self):
        try:
            a_client = AutomatedCuration(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token()
            # jdbc_database_connector_guid = "70dcd0b7-9f06-48ad-ad44-ae4d7a7762aa"
            # postgres_connector_guid = "36f69fd0-54ba-4f59-8a44-11ccf2687a34"
            folder_guid = a_client.get_connector_guid("FileFolder")
            catalog_target_name = "Brain-API-Quickstart"
            file_connector_guid = a_client.get_connector_guid("FileFolder")
            # element_guid = "64296369-323f-4d74-aab3-c2ebae923d25"
            # catalog_target_name = "coco_ods_catalog_target"
            start_time = time.perf_counter()
            a_client.add_catalog_target(
                file_connector_guid, folder_guid, catalog_target_name
            )
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_remove_catalog_target(self):
        try:
            a_client = AutomatedCuration(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token()

            relationship_guid = "7d7fe5db-55bb-4f69-9e2c-e43b82692751"

            start_time = time.perf_counter()

            a_client.remove_catalog_target(relationship_guid)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_initiate_postgres_server_survey(self):
        try:
            a_client = EgeriaTech(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token()
            a_postgres_server_guid = "c8638b61-09b9-48d3-9dea-5dddfb9f01f1"
            start_time = time.perf_counter()
            g1 = a_client.get_element_guid_by_unique_name("PostgreSQLServer:CreateAndSurveyGovernanceActionProcess")
            response = a_client.initiate_postgres_server_survey(a_postgres_server_guid)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict:
                out = "\n\n" + json.dumps(response, indent=4)
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)
            assert True

        except (
            PyegeriaException
        ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"
        except Exception as e:
            print_basic_exception(e)
            assert False, "Invalid request"
        finally:
            a_client.close_session()

    def test_initiate_postgres_database_survey(self):
        try:
            a_client = AutomatedCuration(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token()
            a_postgres_database_guid = "da160627-8d5d-4778-89fe-6d1df7843e30"

            start_time = time.perf_counter()

            response = a_client.initiate_postgres_database_survey(
                a_postgres_database_guid
            )
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict:
                out = "\n\n" + json.dumps(response, indent=4)
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_initiate_file_folder_survey(self):
        try:
            a_client = AutomatedCuration(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            # file_folder_guid = "58ef1911-1e85-43cc-a6cb-a8990112e591"
            file_folder_guid = "7c28d5cb-c745-4663-bdaa-19c0bf962ecf"
            response = a_client.initiate_file_folder_survey(
                file_folder_guid, "FileSurvey:survey-all-folders-and-files"
            )
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict:
                out = "\n\n" + json.dumps(response, indent=4)
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_initiate_file_survey(self):
        try:
            a_client = AutomatedCuration(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            file_guid = "9dbb47d9-4ca9-404e-b02d-2e049e6e6c6e"
            response = a_client.initiate_file_survey(file_guid)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict:
                out = "\n\n" + json.dumps(response, indent=4)
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_initiate_uc_server_survey(self):
        try:
            a_client = AutomatedCuration(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            uc_server_guid = "527b7499-fcd0-43e9-8302-b20e8378e63d"
            response = a_client.initiate_uc_server_survey(uc_server_guid)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict:
                out = "\n\n" + json.dumps(response, indent=4)
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_get_technology_type_elements(self):
        try:
            a_client = AutomatedCuration(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            # filter = "CSV Data File"
            filter = "File System Directory"
            response = a_client.get_technology_type_elements(filter, get_templates=True, output_format="JSON",
                                                             report_spec="Tech-Type-Elements")
                                                             # report_spec="Common-Mermaid")
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                out = "\n\n" + json.dumps(response, indent=4)
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)
            assert True

        except (PyegeriaException) as e:
            print_basic_exception(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Invalid request"
        finally:
            a_client.close_session()
