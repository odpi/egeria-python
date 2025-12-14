"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module is for testing the core Project Manager class and methods
The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests.

"""

import json
import time
from pydantic import ValidationError
from pyegeria.external_links import ExternalReferences
from pyegeria._exceptions import PyegeriaException, print_basic_exception, print_exception_table, \
    print_validation_error, PyegeriaAPIException

from pyegeria._exceptions import (
    PyegeriaInvalidParameterException,
    PyegeriaAPIException,
    PyegeriaUnauthorizedException,
    print_basic_exception as print_exception_response,
)

# from pyegeria.admin_services import FullServerConfig

disable_ssl_warnings = True


class TestExternalReferences:
    good_platform1_url = "https://127.0.0.1:9443"
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
    good_server_1 = "qs-metadata-store"
    good_server_2 = "laz_kv"
    good_server_3 = "active-metadata-store"
    good_server_4 = "integration-daemon"
    good_server_5 = "fluffy_kv"
    good_server_6 = "cocoVIew1"
    good_engine_host_1 = "governDL01"
    good_view_server_1 = "view-server"
    good_view_server_2 = "qs-view-server"
    bad_server_1 = "coco"
    bad_server_2 = ""



    def test_get_classified_external_references(self):
        try:
            p_client = ExternalReferences(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )
            token = p_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            # parent_guid = "0fa16a37-5c61-44c1-85a0-e415c3cecb82"
            # classification = "RootCollection"
            classification = "GovernanceProject"
            response = p_client.get_classified_external_references(classification)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            print(f"response type is: {type(response)}")
            if type(response) is tuple:
                t = response[0]
                count = len(t)
                print(f"Found {count} projects {type(t)}\n\n")
                print(json.dumps(response, indent=4))
            elif type(response) is list:
                count = len(response)
                print(f"Found {count} projects\n\n")
                print(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\n" + response)
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            p_client.close_session()

    def test_find_external_references(self):
        try:
            p_client = ExternalReferences(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )
            token = p_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            search_string = "*"

            response = p_client.find_external_references(
                search_string, metadata_element_subtypes=["ExternalReference"],output_format="JSON", report_spec="Regerenceable"
            )
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                print(f"Found {len(response)} External References {type(response)}\n\n")
                print("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (
            PyegeriaException
        ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
        finally:
            p_client.close_session()

    def test_get_external_references_by_name(self):
        try:
            p_client = ExternalReferences(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )
            token = p_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            # project_name = "Teddy Bear Drop Foot Clinical Trial IT Setup"
            ref_name = "ExtRef::Data-Prep-Kit"
            response = p_client.get_external_references_by_name(ref_name)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                print("\n\n" + json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}")
                print("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nResponse is: " + response)
            assert True

        except (
            PyegeriaException
        ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
        finally:
            p_client.close_session()

    def test_get_classified_external_references(self):
        try:
            p_client = ExternalReferences(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )
            token = p_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            project_classification = "Campaign"

            response = p_client.get_classified_external_references(project_classification)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                print(f"Type was list - found {len(response)} elements\n")
                print(json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}")
                print("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (
            PyegeriaException
        ) as e:
            print_basic_exception( e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
        finally:
            p_client.close_session()

    def test_get_external_reference_by_guid(self):
        try:
            p_client = ExternalReferences(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )
            token = p_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            ref_guid = '4aa07538-57de-4d86-ab5c-566bbc3531c8'

            response = p_client.get_external_reference_by_guid(ref_guid, element_type="CitedDocument", output_format="DICT", report_spec="External-Reference-DrE")
            duration = time.perf_counter() - start_time
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            print(f"Type of response is {type(response)}")

            if isinstance(response, list| dict):
                print("dict:\n\n")
                print(json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}\n\n")
                print(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (
            PyegeriaException, PyegeriaAPIException,
        ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            p_client.close_session()

    def test_link_external_reference(self):
        try:
            p_client = ExternalReferences(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )
            token = p_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            ref_guid = '75821ed5-eec9-41cf-867c-349eb8c797f6'
            element = '60f00f73-76c6-4227-9859-313253a5fdbe'
            pages = '1'

            response = p_client.link_external_reference(element, ref_guid)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            print(f"Type of response is {type(response)}")

            if isinstance(response, list | dict):
                print("dict:\n\n")
                print(json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}\n\n")
                print(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (
                PyegeriaException, PyegeriaAPIException,
        ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            p_client.close_session()

    def test_unlink_external_reference(self):
        try:
            p_client = ExternalReferences(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )
            token = p_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            ref_guid = '75821ed5-eec9-41cf-867c-349eb8c797f6'
            element = '60f00f73-76c6-4227-9859-313253a5fdbe'
            pages = '1'

            response = p_client.detach_external_reference(element, ref_guid)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            print(f"Type of response is {type(response)}")

            if isinstance(response, list | dict):
                print("dict:\n\n")
                print(json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}\n\n")
                print(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (
                PyegeriaException, PyegeriaAPIException,
        ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            p_client.close_session()


    def test_link_cited_document(self):
        try:
            p_client = ExternalReferences(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )
            token = p_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            ref_guid = '43419d38-6b33-4509-b48f-b588b55a9136'
            element = '8e5aa063-468a-4504-a93f-5960f8bcee71'
            pages = '1'
            description = 'This is a test description'
            body = {
                "class": "CitedDOcumentLinkProperties",
                "referenceId" : ref_guid,
                "description" : description,
                "pages" : pages
            }
            response = p_client.link_cited_document(element, ref_guid)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            print(f"Type of response is {type(response)}")

            if isinstance(response, list | dict):
                print("dict:\n\n")
                print(json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(f"Type is {type(response)}\n\n")
                print(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (
                PyegeriaException, PyegeriaAPIException,
        ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            p_client.close_session()

    def test_update_project(self):
        try:
            p_client = ExternalReferences(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )

            token = p_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            project_guid = "7ab4f441-83e2-4e3f-8b63-2ed3946a5dd7"
            qualified_name = (
                "PersonalProject-First Child Project-Mon Apr 22 07:53:13 2024"
            )
            response = p_client.update_project(project_guid, project_status="Active")
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            if type(response) is dict:
                print(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            p_client.close_session()

    # def test_update_status(self):
    #     try:
    #         p_client = ExternalReferences(
    #             self.good_view_server_2,
    #             self.good_platform1_url,
    #             user_id=self.good_user_2,
    #         )
    #
    #         token = p_client.create_egeria_bearer_token(self.good_user_2, "secret")
    #         start_time = time.perf_counter()
    #         guid = "8269a34d-fc7b-44c5-b111-b156f2e48bc2"
    #         new_status = "DRAFT"
    #         p_client.update_element_status(guid, status=new_status)
    #         duration = time.perf_counter() - start_time
    #         print(f"\n\tDuration was {duration} seconds\n")
    #         assert True
    #
    #     except (
    #         PyegeriaException
    #     ) as e:
    #         print_basic_exception(e)
    #         assert False, "Invalid request"
    #     finally:
    #         p_client.close_session()

    def test_delete_ext_ref(self):
        try:
            p_client = ExternalReferences(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )

            token = p_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            ext_ref_guid = '4aa07538-57de-4d86-ab5c-566bbc3531c8'

            response = p_client.delete_external_reference(ext_ref_guid)
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            print(f"Project GUID: {ext_ref_guid} was deleted")
            assert True

        except (
            PyegeriaException
        ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"
        finally:
            p_client.close_session()

    def test_get_project_team(self):
        try:
            p_client = ExternalReferences(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )

            token = p_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            project_guid = "456cacde-a891-4e5a-bd3f-9fa0eeaa792c"

            response = p_client.get_project_team(project_guid)
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            print(f"Result type is: {type(response)}")
            if type(response) is list:
                print(json.dumps(response, indent=4))
            elif type(response) is tuple:
                print(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nGUID is: " + response)
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            p_client.close_session()

    def test_add_to_project_team(self):
        try:
            p_client = ExternalReferences(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )

            token = p_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            project_guid = "456cacde-a891-4e5a-bd3f-9fa0eeaa792c"
            actor_guid = "a588fb08-ae09-4415-bd5d-991882ceacba"

            p_client.add_to_project_team(project_guid, actor_guid)
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            print("Added project member ")
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            p_client.close_session()

    def test_remove_from_project_team(self):
        try:
            p_client = ExternalReferences(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )

            token = p_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            project_guid = "b9580bfb-c3dd-4c74-ae3d-3c4c4bf0b3ab"
            actor_guid = "a588fb08-ae09-4415-bd5d-991882ceacba"

            response = p_client.remove_from_project_team(project_guid, actor_guid)
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            print(f"Removed project member {actor_guid}")
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            p_client.close_session()

    def test_setup_proj_mgmt_role(self):
        try:
            p_client = ExternalReferences(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )

            token = p_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            project_guid = "be04abf9-9bd9-411a-b4a4-bbad682c5c35"
            prj_guid = "522f1b0a-9d44-43f5-a0ab-fc2e7487cfb7"

            response = p_client.setup_project_management_role(project_guid, prj_guid)
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            print(f"Project manager role is  {prj_guid}")
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            p_client.close_session()

    def test_clear_proj_mgmt_role(self):
        try:
            p_client = ExternalReferences(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )

            token = p_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            project_guid = "b9580bfb-c3dd-4c74-ae3d-3c4c4bf0b3ab"
            prj_guid = "522f1b0a-9d44-43f5-a0ab-fc2e7487cfb7"

            response = p_client.clear_project_management_role(project_guid, prj_guid)
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds\n")
            print(f"Project manager role  {prj_guid} was cleared.")
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            p_client.close_session()



