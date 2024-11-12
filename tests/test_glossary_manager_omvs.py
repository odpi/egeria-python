"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module is for testing the glossary manager class and methods
The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests.

"""
import time

import pytest
import asyncio
import json

from contextlib import nullcontext as does_not_raise

from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)

from pyegeria.core_omag_server_config import CoreServerConfig

from pyegeria import GlossaryManager
from tests.test_feedback_manager_omvs import password

# from pyegeria.admin_services import FullServerConfig

disable_ssl_warnings = True


class TestGlossaryManager:
    good_platform1_url = "https://127.0.0.1:9443"
    good_platform2_url = "https://oak.local:9443"
    bad_platform1_url = "https://localhost:9443"

    good_user_1 = "garygeeke"
    good_user_2 = "erinoverview"
    good_user_3 = "peterprofile"
    bad_user_1 = "eviledna"
    bad_user_2 = ""
    good_user_2_pwd = "secret"
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

    def test_create_glossary(self):
        try:
            g_client = GlossaryManager(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )

            token = g_client.create_egeria_bearer_token(
                self.good_user_2, self.good_user_2_pwd
            )
            start_time = time.perf_counter()
            display_name = "test"
            description = "A glossary used for test"
            language = "English"
            usage = "for testing purposes only"
            response = g_client.create_glossary(
                display_name, description, language, usage
            )
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nNew glossary {display_name} created with GUID of {response}")
            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            g_client.close_session()

    def test_update_glossary(self):
        try:
            g_client = GlossaryManager(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )

            token = g_client.create_egeria_bearer_token(
                self.good_user_2, self.good_user_2_pwd
            )
            glossary_guid = "70ae4d54-05bb-4411-96e6-697d0640a10e"
            start_time = time.perf_counter()
            body = {
                "class": "ReferenceableRequestBody",
                "elementProperties": {
                    "class": "GlossaryProperties",
                    "displayName": "puddys-universe",
                    "qualified_name": "Glossary:puddys-universe",
                },
            }

            g_client.update_glossary(glossary_guid, body, True)
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nUpdated glossary {glossary_guid}")
            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            g_client.close_session()

    def test_delete_glossary(self):
        try:
            g_client = GlossaryManager(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )

            token = g_client.create_egeria_bearer_token(
                self.good_user_2, self.good_user_2_pwd
            )
            start_time = time.perf_counter()
            glossary_guid = "2a7b7423-335b-4b0f-9dfe-af73621b465d"
            g_client.delete_glossary(glossary_guid)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nDeleted glossary {glossary_guid}")
            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            g_client.close_session()

    def test_find_glossaries(self):
        try:
            g_client = GlossaryManager(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()
            response = g_client.find_glossaries(
                # "*",
                "Sustainability Glossary",
                starts_with=False,
                ends_with=False,
                ignore_case=True,
                page_size=0,
                effective_time=None,
            )
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                # print("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                print(f"Found {count} glossaries")
                for i in range(count):
                    print(
                        f"Found glossary: {response[i]['glossaryProperties']['qualifiedName']} with id of {response[i]['elementHeader']['guid']}"
                    )
                print(json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\n" + response)
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            g_client.close_session()

    def test_get_glossary_by_guid(self, server: str = good_view_server_1):
        try:
            server_name = server
            g_client = GlossaryManager(
                server_name, self.good_platform1_url, user_id=self.good_user_2
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            # glossary_guid = "f9b78b26-6025-43fa-9299-a905cc6d1575"  # This is the sustainability glossary
            glossary_guid = (
                "c13e22d5-756a-4b54-b784-14037ee3dfc4"  # This is pdr glossary
            )
            response = g_client.get_glossary_by_guid(glossary_guid, server_name)
            print(f"type is {type(response)}")
            if type(response) is dict:
                print("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                print(f"Found {count} terms")
            elif type(response) is str:
                print("\n\n" + response)
            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            g_client.close_session()

    def test_get_glossaries_by_name(self, server: str = good_view_server_1):
        try:
            server_name = server
            g_client = GlossaryManager(
                server_name, self.good_platform1_url, user_id=self.good_user_2
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            glossary_name = "puddys-universe"

            response = g_client.get_glossaries_by_name(glossary_name)
            print(f"type is {type(response)}")
            if type(response) is list:
                print("\n\n" + json.dumps(response, indent=4))

            elif type(response) is str:
                print("\n\n" + response)
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            g_client.close_session()

    #
    #       Catagories
    #
    def test_create_category(self):
        try:
            g_client = GlossaryManager(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )

            token = g_client.create_egeria_bearer_token(
                self.good_user_2, self.good_user_2_pwd
            )
            start_time = time.perf_counter()
            glossary_guid = "31dd2534-55c7-4c23-a157-2196e21a908e"
            display_name = "Test category"
            description = "A category used for testing"
            language = "English"
            usage = "for testing purposes only"
            response = g_client.create_category(
                glossary_guid, display_name, description
            )
            duration = time.perf_counter() - start_time
            # resp_str = json.loads(response)
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nNew category {display_name} created with GUID of {response}")
            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            g_client.close_session()

    def test_get_terms_for_glossary(self, server: str = good_view_server_1):
        server_name = server
        try:
            g_client = GlossaryManager(
                server_name, self.good_platform1_url, user_id="erinoverview"
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            # glossary_guid = "f9b78b26-6025-43fa-9299-a905cc6d1575"  # This is the sustainability glossary
            # glossary_guid = "706ba88d-d0bb-42da-82d9-385b13516b34" # Teddy Bear Drop Foot
            # glossary_guid = (
            #     "c13e22d5-756a-4b54-b784-14037ee3dfc4"  # larger sustainability glossary
            # )
            glossary_guid = "70ae4d54-05bb-4411-96e6-697d0640a10e"

            start_time = time.perf_counter()
            response = g_client.get_terms_for_glossary(
                glossary_guid, page_size=500, effective_time=None
            )
            print(f"Duration is {time.perf_counter()-start_time} seconds")
            print(f"type is {type(response)}")
            if type(response) is list:
                print("\n\n" + json.dumps(response, indent=4))
                count = len(response)
                print(f"Found {count} terms")
            elif type(response) is str:
                print("\n\n" + response)
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            g_client.close_session()

    def test_export_glossary_to_csv(self):
        try:
            g_client = GlossaryManager(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )

            token = g_client.create_egeria_bearer_token(
                self.good_user_2, self.good_user_2_pwd
            )
            start_time = time.perf_counter()
            glossary_guid = "70ae4d54-05bb-4411-96e6-697d0640a10e"
            file_name = f"/Users/dwolfson/localGit/test_export-{glossary_guid}.csv"
            response = g_client.export_glossary_to_csv(glossary_guid, file_name)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nExported {response} rows to {file_name}")
            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            g_client.close_session()

    def test_get_glossary_for_term(self, server: str = good_view_server_1):
        server_name = server

        try:
            g_client = GlossaryManager(
                server_name, self.good_platform1_url, user_id="erinoverview"
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            term_guid = "5467f5d4-d821-4fc2-ad71-8af7181826ff"
            response = g_client.get_glossary_for_term(term_guid)

            print(f"type is {type(response)}")
            if type(response) is dict:
                print("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\n" + response)
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            g_client.close_session()

    def test_get_terms_by_name(self, server: str = good_view_server_1):
        server_name = server

        try:
            g_client = GlossaryManager(
                server_name, self.good_platform1_url, user_id="erinoverview"
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            term_name = "GlossaryTerm: puddie - 2024-10-18T13:51:52.356216"
            glossary_guid = "70ae4d54-05bb-4411-96e6-697d0640a10e"
            response = g_client.get_terms_by_name(term_name, glossary_guid, ["DRAFT"])

            print(f"type is {type(response)}")
            if type(response) is list:
                print("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\n" + response)
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            g_client.close_session()

    def test_get_terms_by_guid(self, server: str = good_view_server_1):
        server_name = server

        try:
            g_client = GlossaryManager(
                server_name, self.good_platform1_url, user_id="erinoverview"
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            term_guid = "50c7668a-9cef-4c1e-bd9d-dde99c03a310"
            response = g_client.get_terms_by_guid(term_guid)

            print(f"type is {type(response)}")
            if type(response) is dict:
                print("\n\n" + json.dumps(response, indent=4))
                print(
                    f"Term name is: {response['glossaryTermProperties']['displayName']}"
                )
            elif type(response) is str:
                print("\n\n" + response)
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            g_client.close_session()

    def test_find_glossary_terms(self):
        try:
            g_client = GlossaryManager(
                self.good_view_server_1, self.good_platform1_url, self.good_user_2
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            # glossary_guid = "017dee20-b8ce-4d74-854b-f2a888a082cd" # small-email glossary
            # glossary_guid = (
            #     "f9b78b26-6025-43fa-9299-a905cc6d1575"  # sustainability glossary
            # )
            glossary_guid = None
            start_time = time.perf_counter()
            response = g_client.find_glossary_terms(
                "*",
                glossary_guid=glossary_guid,
                starts_with=True,
                ends_with=False,
                for_lineage=False,
                ignore_case=True,
                for_duplicate_processing=True,
                status_filter=[],
                page_size=10,
                effective_time=None,
            )
            print(f"Duration is {time.perf_counter() - start_time} seconds")
            print(f"Number of terms is: {len(response)}")
            if type(response) is list:
                print("\n\n" + json.dumps(response, indent=4))
                # print_json_list_as_table(response)
                count = len(response)
                print(f"Found {count} terms")
            elif type(response) is str:
                print("\n\n" + response)
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            g_client.close_session()

    def test_update_term(self):
        try:
            g_client = GlossaryManager(
                self.good_view_server_1, self.good_platform1_url, self.good_user_2
            )

            token = g_client.create_egeria_bearer_token(self.good_user_2, "secret")
            term_guid = "f9ed697c-04be-4744-aa7c-d302b6d91321"
            body = {
                "class": "ReferenceableUpdateRequestBody",
                "elementProperties": {
                    "class": "GlossaryTermProperties",
                    "description": "This is the long description of the term. And this is some more text.",
                },
            }

            start_time = time.perf_counter()
            g_client.update_term(term_guid, body, True)
            print(f"Duration is {time.perf_counter() - start_time} seconds")

            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            g_client.close_session()

    def test_load_terms_from_csv(self):
        try:
            g_client = GlossaryManager(
                self.good_view_server_1, self.good_platform1_url, self.good_user_3
            )
            token = g_client.create_egeria_bearer_token(self.good_user_3, "secret")
            glossary = "example"
            file_name = "/Users/dwolfson/localGit/egeria-v5-1/egeria-workspaces/exchange/loading-bay/glossary/upsert-example.om-terms"
            response = g_client.load_terms_from_file(glossary, file_name, True)
            print(f"type is {type(response)}")
            if type(response) is list:
                print("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\n" + response)
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        except Exception as e:
            print(e)

        finally:
            g_client.close_session()

    def test_delete_term(self):
        try:
            g_client = GlossaryManager(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd=self.good_user_2_pwd,
            )

            token = g_client.create_egeria_bearer_token(
                self.good_user_2, self.good_user_2_pwd
            )
            start_time = time.perf_counter()
            term_guid = "50c7668a-9cef-4c1e-bd9d-dde99c03a310"
            g_client.delete_term(term_guid)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nDeleted term {term_guid}")
            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
        finally:
            g_client.close_session()
