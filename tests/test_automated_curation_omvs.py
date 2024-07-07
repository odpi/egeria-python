"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module is for testing the Automated Curation View Service module.
The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests.

"""
import json
import time
import httpx
from rich import print, print_json
from rich.console import Console
from rich.pretty import pprint

from pyegeria import AutomatedCuration
from pyegeria._exceptions import (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,
                                  print_exception_response, )

# from pyegeria.admin_services import FullServerConfig

disable_ssl_warnings = True
console = Console()


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
    good_view_server_2 = "fluffy_view"
    bad_server_1 = "coco"
    bad_server_2 = ""

    def test_create_element_from_template(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
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
                    "serverName": "Survey Engine Host"
                }
            }
            start_time = time.perf_counter()
            response = a_client.create_element_from_template(body)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print("Guid of created element is:" + str(response))
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_create_folder_asset(self ) -> str:
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
            token = a_client.create_egeria_bearer_token()
            path_name = "/Users/dwolfson/localGit/databricks"
            folder_name = "databricks"
            file_system = "laz"
            description = "Folder for databricks work"
            version = "0.1"
            start_time = time.perf_counter()
            response = a_client.create_folder_element_from_template(path_name, folder_name, "laz.local",
                                                                    description, version)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                out = ("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                pprint(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                pprint("created folder with GUID: " + response)
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()


    def test_create_kafka_server_element_from_template(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = a_client.create_kafka_server_element_from_template("pdr-kafka5", "egeria.pdr-associates.com",
                                                                          "9093")
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                out = ("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                pprint(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                pprint("created Kafka Server with GUID: " + response)
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_create_postgres_server_element_from_template(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = a_client.create_postgres_server_element_from_template("laz-postgres", "localhost", "5432",
                                                                             db_user="postgres", db_pwd="secret")
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                out = ("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                pprint(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                pprint("Database Server GUID create is " + response)
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_get_engine_actions(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = a_client.get_engine_actions()
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"The type of response is: {type(response)}")
            if type(response) is list:
                out = ("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_get_engine_action(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
            token = a_client.create_egeria_bearer_token()
            engine_action_guid = "2374f070-de61-4ba5-959c-2d5621da2a1c"
            start_time = time.perf_counter()
            response = a_client.get_engine_action(engine_action_guid)
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_cancel_engine_action(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
            token = a_client.create_egeria_bearer_token()
            engine_action_guid = "2374f070-de61-4ba5-959c-2d5621da2a1c"
            start_time = time.perf_counter()
            a_client.cancel_engine_action(engine_action_guid)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            pprint(f"Canceled engine action: {engine_action_guid}")
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_get_active_engine_actions(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = a_client.get_active_engine_actions()
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                out = ("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                print(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                print("\n\n" + response)
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_get_engine_actions_by_name(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = a_client.get_engine_actions_by_name("JDBCDatabaseCataloguer")
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_find_engine_actions(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = a_client.find_engine_actions("Downloads")
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    #
    #   Governance Processes
    #
    def test_get_governance_action_process_by_guid(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
            token = a_client.create_egeria_bearer_token()
            action_guid = "dde1e255-6d0c-4589-b4a6-17e7d01db5ab"
            start_time = time.perf_counter()
            response = a_client.get_governance_action_process_by_guid(action_guid)
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_get_gov_action_process_graph(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
            token = a_client.create_egeria_bearer_token()
            action_guid = "dde1e255-6d0c-4589-b4a6-17e7d01db5ab"
            start_time = time.perf_counter()
            response = a_client.get_gov_action_process_graph(action_guid)
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_summarize_graph(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
            token = a_client.create_egeria_bearer_token()
            action_guid = "dde1e255-6d0c-4589-b4a6-17e7d01db5ab"
            start_time = time.perf_counter()
            response = a_client.get_gov_action_process_graph(action_guid)
            duration = time.perf_counter() - start_time

            if type(response) is dict:
                process_steps: [dict]
                step_links: [dict] = []
                gov_process_qn = response["governanceActionProcess"]["processProperties"]["qualifiedName"]
                gov_process_dn = response["governanceActionProcess"]["processProperties"]["displayName"]
                domain_id = response["governanceActionProcess"]["processProperties"]["domainIdentifier"]
                # print(f"\n\n Qualified Name: {gov_process_qn} \t\t Display Name: {gov_process_dn}")
                md = f"\n---\ntitle: {gov_process_dn}\n---\nflowchart LR\n"
                element = response["firstProcessStep"]["element"]
                qname = element["processStepProperties"]["qualifiedName"]
                dname = element["processStepProperties"]["displayName"]
                domain_id = element["processStepProperties"]["domainIdentifier"]
                guid = element["elementHeader"]["guid"]
                wait = element["processStepProperties"]["waitTime"]
                ignore_mult_trig = element["processStepProperties"]["ignoreMultipleTriggers"]
                link = response["firstProcessStep"]["linkGUID"]

                # print(f"\n\n First Step: {qname}\tDisplay Name: {dname}\t Wait: {wait}\t Link: {link}")
                md = f"{md}\nStep1([\"'**{dname}**\n* guid: {guid}\nwait_time: {wait}\ndomain: {domain_id}\nmult_trig: {ignore_mult_trig}`\"])"
                process_steps = {qname: {"step": "Step1", "displayName": dname, "guid": guid, "domain": domain_id,
                    "ignoreMultTrig": ignore_mult_trig, "waitTime": wait, "link_guid": link}}
                next_steps = response.get("nextProcessSteps", None)
                if next_steps is not None:
                    i = 1
                    for step in next_steps:
                        i += 1
                        qname = step["processStepProperties"]["qualifiedName"]
                        dname = step["processStepProperties"]["displayName"]
                        wait = step["processStepProperties"]["waitTime"]
                        step = f"Step{i}"
                        md = f"{md}\n{step}(\"`**{dname}**\nguid: {guid}\nwait_time: {wait}\ndomain: {domain_id}\nmult_trig: {ignore_mult_trig}`\")"
                        process_steps.update({
                            qname: {"step": step, "displayName": dname, "guid": guid, "domain": domain_id,
                                "ignoreMultTrig": ignore_mult_trig,
                                "waitTime": wait}})  # process_steps.append({qname: {"step": step,"displayName": dname, "waitTime": wait}})
                # print(md)
                # Now process the links
                process_step_links = response.get("processStepLinks", None)
                if process_step_links is not None:
                    for slink in process_step_links:
                        prev_step_name = slink["previousProcessStep"]["uniqueName"]
                        next_step_name = slink["nextProcessStep"]["uniqueName"]
                        next_step_link_guid = slink["nextProcessStepLinkGUID"]
                        guard = slink["guard"]
                        mandatory_guard = slink["mandatoryGuard"]
                        # print(f"\n\n Links: prev_step: {prev_step_name}\t next_step: {next_step_name}\t next_step_link: {next_step_link_guid}\t Guard: {guard}\t mandatory_guard: {mandatory_guard}")
                        step_links.append({
                            next_step_link_guid: {"prev_step_name": prev_step_name, "next_step_name": next_step_name,
                                "guard": guard, "mandatory_guard": mandatory_guard}})
                        step_p = process_steps[prev_step_name]["step"]
                        step_n = process_steps[next_step_name]["step"]
                        if mandatory_guard:
                            link = f"Mandatory:{guard}"
                        else:
                            link = guard
                        md = f"{md}\n{step_p}-->|{link}|{step_n}"
                    i = 1

                print(md)


            elif type(response) is str:
                console.log("\n\n" + response)
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_get_gov_action_process_by_name(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
            token = a_client.create_egeria_bearer_token()
            name = "Survey"
            start_time = time.perf_counter()
            response = a_client.get_gov_action_processes_by_name(name)
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_find_gov_action_processes(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
            token = a_client.create_egeria_bearer_token()
            name = "Daily"
            start_time = time.perf_counter()
            response = a_client.find_gov_action_processes(name, starts_with=True, ignore_case=True)
            duration = time.perf_counter() - start_time
            print(f"n\tDuration was {duration} seconds")
            print(f"\n Type of response is {type(response)}")
            if type(response) is list:
                out = ("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                console.log(f"Found {count} elements")
                print_json(out)
            elif type(response) is str:
                console.log("\n\n" + response)
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_initiate_gov_action_process(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
            token = a_client.create_egeria_bearer_token()
            action_type_qualified_name = ""
            start_time = time.perf_counter()
            request_source_guids = None
            action_targets = None
            request_parameters = None
            orig_service_name = None
            orig_engine_name = None

            response = a_client.initiate_gov_action_process(action_type_qualified_name, request_source_guids,
                                                            action_targets, start_time, request_parameters,
                                                            orig_service_name, orig_engine_name)

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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_get_gov_action_types_by_guid(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_get_gov_action_types_by_name(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_find_gov_action_types(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    #   Get Technology types
    #

    def test_get_all_technology_types(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_find_technology_types(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = a_client.find_technology_types("PostgreSQL", starts_with=True, ignore_case=True)
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_get_technology_types_for_open_metadata_type(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = a_client.get_tech_types_for_open_metadata_type("SoftwareServer", "PostgreSQL")
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_get_technology_type_detail(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    #
    #   Governance Actions
    #
    def test_initiate_gov_action_type(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_get_catalog_target(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
            token = a_client.create_egeria_bearer_token()
            postgres_server_connector_guid = "36f69fd0-54ba-4f59-8a44-11ccf2687a34"
            element_guid = "731eb432-e9e9-482a-86fc-0a7407ea78e6"
            rel_guid = "2ec7af3f-1d1e-4d5d-85a4-15c62480b898"
            start_time = time.perf_counter()
            # gov_action_type_qn = "Egeria:GovernanceActionType:2adeb8f1-0f59-4970-b6f2-6cc25d4d2402survey-folder"

            response = a_client.get_catalog_target(rel_guid)
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_get_catalog_targets(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
            token = a_client.create_egeria_bearer_token()
            postgres_server_connector_guid = "36f69fd0-54ba-4f59-8a44-11ccf2687a34"
            folder_connector_guid = "cd6479e1-2fe7-4426-b358-8a0cf70be117"
            element_guid = "061a4fb3-7d41-4e52-9080-65e9c61084d2"
            relationship_guid = "6be6e470-7aa2-4f50-8142-246866037523"
            t = folder_connector_guid
            start_time = time.perf_counter()
            response = a_client.get_catalog_targets(t)
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_add_catalog_target(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
            token = a_client.create_egeria_bearer_token()
            element_guid = "061a4fb3-7d41-4e52-9080-65e9c61084d2"
            catalog_target_name = "deltalake experiments"
            file_folder_integ_con = "cd6479e1-2fe7-4426-b358-8a0cf70be117"
            start_time = time.perf_counter()
            guid = a_client.add_catalog_target(file_folder_integ_con, element_guid, catalog_target_name)
            duration = time.perf_counter() - start_time
            print(f"guid returned is: {guid}")
            print(f"\n\tDuration was {duration} seconds")
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_update_catalog_targets(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
            token = a_client.create_egeria_bearer_token()
            element_guid = "001927b1-b960-48c6-a99e-73b6957c259d"
            catalog_target_name = "deltalake experiments on laz"
            file_folder_integ_con = "cd6479e1-2fe7-4426-b358-8a0cf70be117"
            relationship_guid = "2ec7af3f-1d1e-4d5d-85a4-15c62480b898"
            start_time = time.perf_counter()
            guid = a_client.update_catalog_target(relationship_guid, catalog_target_name)
            duration = time.perf_counter() - start_time
            print(f"guid returned is: {guid}")
            print(f"\n\tDuration was {duration} seconds")
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_catalog_folder_files(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
            token = a_client.create_egeria_bearer_token()
            # jdbc_database_connector_guid = "70dcd0b7-9f06-48ad-ad44-ae4d7a7762aa"
            # postgres_connector_guid = "36f69fd0-54ba-4f59-8a44-11ccf2687a34"
            folder_guid = "aaffdb1b-269f-4a1e-9325-7a324ee0ddf4"
            catalog_target_name = "Brain-API-Quickstart"
            file_connector_guid = "d13ba229-d406-43f7-b395-9462b7d98900"
            # element_guid = "64296369-323f-4d74-aab3-c2ebae923d25"
            # catalog_target_name = "coco_ods_catalog_target"
            start_time = time.perf_counter()
            a_client.add_catalog_target(file_connector_guid, folder_guid, catalog_target_name)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_remove_catalog_target(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
            token = a_client.create_egeria_bearer_token()

            relationship_guid = "0fa9bc0d-4a1b-4d8a-8928-020fb2465eac"

            start_time = time.perf_counter()

            a_client.remove_catalog_target(relationship_guid)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_initiate_postgres_server_survey(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
            token = a_client.create_egeria_bearer_token()
            a_postgres_server_guid = "8dc2cbdd-c1f3-4a45-be30-1835a8ac0453"
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_initiate_postgres_database_survey(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_initiate_file_folder_survey(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            # file_folder_guid = "58ef1911-1e85-43cc-a6cb-a8990112e591"
            file_folder_guid = "902d806f-a908-4cef-97ee-8147659c4e9d"
            response = a_client.initiate_file_folder_survey(file_folder_guid,
                                                            'Egeria:GovernanceActionType:AssetSurvey:survey-all-folders')
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_initiate_file_survey(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()

    def test_get_technology_type_elements(self):
        try:
            a_client = AutomatedCuration(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
            token = a_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            filter = "CSV Data File"
            # filter = "Apache Kafka Server"
            response = a_client.get_technology_type_elements(filter, get_templates=False)
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

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            a_client.close_session()
